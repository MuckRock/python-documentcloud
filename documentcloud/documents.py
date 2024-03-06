"""
Documents
"""

# Standard Library
import datetime
import logging
import os
import re
import warnings
from functools import partial

# Third Party
from requests.exceptions import RequestException

# Local
from .annotations import AnnotationClient
from .base import APIResults, BaseAPIClient, BaseAPIObject
from .constants import BULK_LIMIT, SUPPORTED_EXTENSIONS
from .exceptions import APIError
from .organizations import Organization
from .sections import SectionClient
from .toolbox import grouper, is_url, merge_dicts, requests_retry_session
from .users import User

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

logger = logging.getLogger("documentcloud")

IMAGE_SIZES = ["thumbnail", "small", "normal", "large", "xlarge"]


class Document(BaseAPIObject):
    """A single DocumentCloud document"""

    api_path = "documents"
    writable_fields = [
        "access",
        "data",
        "description",
        "language",
        "publish_at",
        "published_url",
        "related_article",
        "source",
        "title",
    ]
    date_fields = ["created_at", "updated_at"]

    def __init__(self, client, dict_):
        # deal with potentially nested objects
        objs = [("user", User), ("organization", Organization)]
        for name, resource in objs:
            value = dict_.get(name)
            if isinstance(value, dict):
                dict_[f"_{name}"] = resource(client, value)
                dict_[f"{name}_id"] = value.get("id")
            elif isinstance(value, int):
                dict_[f"_{name}"] = None
                dict_[f"{name}_id"] = value

        super().__init__(client, dict_)

        self.sections = SectionClient(client, self)
        self.annotations = AnnotationClient(client, self)
        self.notes = self.annotations

    def __str__(self):
        return self.title

    def __getattr__(self, attr):
        """Generate methods for fetching resources"""
        p_image = re.compile(
            r"^get_(?P<size>thumbnail|small|normal|large)_image_url(?P<list>_list)?$"
        )
        get = attr.startswith("get_")
        url = attr.endswith("_url")
        text = attr.endswith("_text")
        json = attr.endswith(("_json", "_json_text"))
        fmt = "json" if json else "text" if text else None
        # this allows dropping `get_` to act like a property, ie
        # .full_text_url
        if not get and hasattr(self, f"get_{attr}"):
            return getattr(self, f"get_{attr}")()
        # this allows dropping `_url` to fetch the url, ie
        # .get_full_text()
        if not url and hasattr(self, f"{attr}_url"):
            return lambda *a, **k: self._get_url(
                getattr(self, f"{attr}_url")(*a, **k), fmt
            )
        # this genericizes the image sizes
        m_image = p_image.match(attr)
        if m_image and m_image.group("list"):
            return partial(self.get_image_url_list, size=m_image.group("size"))
        if m_image and not m_image.group("list"):
            return partial(self.get_image_url, size=m_image.group("size"))
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{attr}'"
        )

    def __dir__(self):
        attrs = dir(type(self)) + list(self.__dict__.keys())
        getters = [a for a in attrs if a.startswith("get_")]
        attrs += [a[len("get_") :] for a in getters]
        attrs += [a[: -len("_url")] for a in getters if a.endswith("url")]
        attrs += [a[len("get_") : -len("_url")] for a in getters if a.endswith("url")]
        for size in IMAGE_SIZES:
            attrs += [
                f"get_{size}_image_url",
                f"{size}_image_url",
                f"get_{size}_image",
                f"{size}_image",
                f"get_{size}_image_url_list",
                f"{size}_image_url_list",
            ]
        return sorted(attrs)

    @property
    def pages(self):
        return self.page_count

    @property
    def mentions(self):
        if hasattr(self, "highlights") and self.highlights is not None:
            return [
                Mention(page, text)
                for page, texts in self.highlights.items()
                for text in texts
            ]
        else:
            return []

    @property
    def user(self):
        # pylint:disable=access-member-before-definition
        if self._user is None:
            self._user = self._client.users.get(self.user_id)
        return self._user

    @property
    def organization(self):
        # pylint:disable=access-member-before-definition
        if self._organization is None:
            self._organization = self._client.organizations.get(self.organization_id)
        return self._organization

    @property
    def contributor(self):
        return self.user.name

    @property
    def contributor_organization(self):
        return self.organization.name

    @property
    def contributor_organization_slug(self):
        return self.organization.slug

    def _get_url(self, url, fmt=None):
        base_netloc = urlparse(self._client.base_uri).netloc
        url_netloc = urlparse(url).netloc

        if base_netloc == url_netloc:
            # if the url host is the same as the base api host,
            # sent the request with the client in order to include
            # authentication credentials
            response = self._client.get(url, full_url=True)
        else:
            response = requests_retry_session().get(
                url, headers={"User-Agent": "python-documentcloud2"}
            )
        if fmt == "text":
            return response.content.decode("utf8")
        elif fmt == "json":
            return response.json()
        else:
            return response.content

    # Resource URLs
    def get_full_text_url(self):
        return f"{self.asset_url}documents/{self.id}/{self.slug}.txt"

    def get_page_text_url(self, page=1):
        return f"{self.asset_url}documents/{self.id}/pages/{self.slug}-p{page}.txt"

    def get_page_position_json_url(self, page=1):
        return (
            f"{self.asset_url}documents/{self.id}/pages/"
            f"{self.slug}-p{page}.position.json"
        )

    def get_json_text_url(self):
        return f"{self.asset_url}documents/{self.id}/{self.slug}.txt.json"

    def get_pdf_url(self):
        return f"{self.asset_url}documents/{self.id}/{self.slug}.pdf"

    def get_image_url(self, page=1, size="normal"):
        return (
            f"{self.asset_url}documents/{self.id}/pages/{self.slug}-p{page}-{size}.gif"
        )

    def get_image_url_list(self, size="normal"):
        return [
            self.get_image_url(page=i, size=size) for i in range(1, self.page_count + 1)
        ]

    def get_errors(self):
        """Retrieve errors for the document"""
        endpoint = f"documents/{self.id}/errors/"
        all_results = []

        while endpoint:
            response = self._client.get(endpoint)
            data = response.json()

            results = data.get("results", [])
            for entry in results:
                created_at_str = entry.get("created_at")
                if created_at_str:
                    entry["created_at"] = datetime.datetime.strptime(
                        created_at_str, "%Y-%m-%dT%H:%M:%S.%fZ"
                    )

            all_results.extend(results)
            endpoint = data.get("next")

        return all_results

    def process(self):
        """Reprocess the document"""
        self._client.post(f"{self.api_path}/{self.id}/process/")


class DocumentClient(BaseAPIClient):
    """Client for interacting with Documents"""

    api_path = "documents"
    resource = Document

    def search(self, query, **params):
        """Return documents matching a search query"""

        # legacy parameter mentions renamed to hl
        mentions = params.pop("mentions", None)
        params["hl"] = mentions
        data = params.pop("data", None)
        if data is not None:  # pragma: no cover
            warnings.warn(
                "The `data` argument to `search` is deprecated, "
                "it will always include data now",
                DeprecationWarning,
            )

        if query:
            params["q"] = query
        response = self.client.get("documents/search/", params=params)
        return APIResults(self.resource, self.client, response)

    def list(self, **params):
        """Convert id__in from list to string if needed"""
        if "id__in" in params and isinstance(params["id__in"], list):
            params["id__in"] = ",".join(str(i) for i in params["id__in"])
        return super().list(**params)

    def upload(self, pdf, **kwargs):
        """Upload a document"""

        def check_size(size):
            # DocumentCloud's size limit is set to 501MB to give people a little leeway
            # for OS rounding
            if size >= 501 * 1024 * 1024:
                raise ValueError(
                    "The pdf you have submitted is over the DocumentCloud API's 500MB "
                    "file size limit. Split it into smaller pieces and try again."
                )

        # if they pass in a URL, use the URL upload flow
        if is_url(pdf):
            return self._upload_url(pdf, **kwargs)
        # otherwise use the direct file upload flow - determine if they passed
        # in a file or a path
        elif hasattr(pdf, "read"):
            try:
                size = os.fstat(pdf.fileno()).st_size
            except (AttributeError, OSError):  # pragma: no cover
                size = 0
            check_size(size)
            return self._upload_file(pdf, **kwargs)
        else:
            size = os.path.getsize(pdf)
            check_size(size)
            with open(pdf, "rb") as pdf_file:
                return self._upload_file(pdf_file, **kwargs)

    def _format_upload_parameters(self, name, **kwargs):
        """Prepare upload parameters from kwargs"""
        allowed_parameters = [
            "access",
            "description",
            "language",
            "original_extension",
            "related_article",
            "publish_at",
            "published_url",
            "source",
            "title",
            "data",
            "force_ocr",
            "projects",
            "delayed_index",
            "revision_control",
        ]
        # these parameters currently do not work, investigate...
        ignored_parameters = ["secure"]

        # title is required, so set a default
        params = {"title": self._get_title(name)}

        if "project" in kwargs:
            params["projects"] = [kwargs["project"]]

        for param in allowed_parameters:
            if param in kwargs:
                params[param] = kwargs[param]

        for param in ignored_parameters:
            if param in kwargs:
                warnings.warn(f"The parameter `{param}` is not currently supported")

        return params

    def _get_title(self, name):
        """Get the default title for a document from its path"""
        return name.split(os.sep)[-1].rsplit(".", 1)[0]

    def _upload_url(self, file_url, **kwargs):
        """Upload a document from a publicly accessible URL"""
        params = self._format_upload_parameters(file_url, **kwargs)
        params["file_url"] = file_url
        response = self.client.post("documents/", json=params)
        return Document(self.client, response.json())

    def _upload_file(self, file_, **kwargs):
        """Upload a document directly"""
        # create the document
        force_ocr = kwargs.pop("force_ocr", False)
        params = self._format_upload_parameters(file_.name, **kwargs)
        response = self.client.post("documents/", json=params)

        # upload the file directly to storage
        create_json = response.json()
        presigned_url = create_json["presigned_url"]
        response = requests_retry_session().put(presigned_url, data=file_.read())

        # begin processing the document
        doc_id = create_json["id"]
        response = self.client.post(
            f"documents/{doc_id}/process/", json={"force_ocr": force_ocr}
        )

        return Document(self.client, create_json)

    def _collect_files(self, path, extensions):
        """Find the paths to files with specified extensions under a directory"""
        path_list = []
        for dirpath, _, filenames in os.walk(path):
            path_list.extend(
                [
                    os.path.join(dirpath, filename)
                    for filename in filenames
                    if os.path.splitext(filename)[1].lower() in extensions
                ]
            )
        return path_list

    def upload_directory(self, path, handle_errors=False, extensions=".pdf", **kwargs):
        """Upload files with specified extensions in a directory"""
        # pylint: disable=too-many-locals, too-many-branches

        # Do not set the same title for all documents
        kwargs.pop("title", None)

        # If extensions are specified as None, it will check for all supported
        # filetypes.
        if extensions is None:
            extensions = SUPPORTED_EXTENSIONS

        # Convert single extension to a list if provided
        if extensions and not isinstance(extensions, list):
            extensions = [extensions]

        # Checks to see if the extensions are supported, raises an error if not.
        invalid_extensions = set(extensions) - set(SUPPORTED_EXTENSIONS)
        if invalid_extensions:
            raise ValueError(
                f"Invalid extensions provided: {', '.join(invalid_extensions)}"
            )

        # Loop through the path and get all the files with matching extensions
        path_list = self._collect_files(path, extensions)

        logger.info(
            "Upload directory on %s: Found %d files to upload",
            path,
            len(path_list)
        )

        # Upload all the files using the bulk API to reduce the number
        # of API calls and improve performance
        obj_list = []
        params = self._format_upload_parameters("", **kwargs)
        for i, file_paths in enumerate(grouper(path_list, BULK_LIMIT)):
            # Grouper will put None's on the end of the last group
            file_paths = [p for p in file_paths if p is not None]

            logger.info("Uploading group %d:\n%s", i + 1, "\n".join(file_paths))

            # Create the documents
            logger.info("Creating the documents...")
            try:
                response = self.client.post(
                    "documents/",
                    json=[
                        merge_dicts(
                            params,
                            {
                                "title": self._get_title(p),
                                "original_extension": os.path.splitext(
                                    os.path.basename(p)
                                )[1]
                                .lower()
                                .lstrip("."),
                            },
                        )
                        for p in file_paths
                    ],
                )
            except (APIError, RequestException) as exc:
                if handle_errors:
                    logger.info(
                        "Error creating the following documents: %s\n%s",
                        exc,
                        "\n".join(file_paths)
                    )
                    continue
                else:
                    raise

            # Upload the files directly to storage
            create_json = response.json()
            obj_list.extend(create_json)
            presigned_urls = [j["presigned_url"] for j in create_json]
            for url, file_path in zip(presigned_urls, file_paths):
                logger.info("Uploading %s to S3...", file_path)
                try:
                    with open(file_path, "rb") as file:
                        response = requests_retry_session().put(url, data=file.read())
                    self.client.raise_for_status(response)
                except (APIError, RequestException) as exc:
                    if handle_errors:
                        logger.info(
                            "Error uploading the following document: %s %s",
                            exc,
                            file_path
                        )
                        continue
                    else:
                        raise

            # Begin processing the documents
            logger.info("Processing the documents...")
            doc_ids = [j["id"] for j in create_json]
            try:
                response = self.client.post("documents/process/", json={"ids": doc_ids})
            except (APIError, RequestException) as exc:
                if handle_errors:
                    logger.info(
                        "Error creating the following documents: %s\n%s",
                        exc,
                        "\n".join(file_paths)
                    )
                    continue
                else:
                    raise

        logger.info("Upload directory complete")

        # Pass back the list of documents
        return [Document(self.client, d) for d in obj_list]

    def upload_urls(self, url_list, handle_errors=False, **kwargs):
        """Upload documents from a list of URLs"""

        # Do not set the same title for all documents
        kwargs.pop("title", None)

        obj_list = []
        params = self._format_upload_parameters("", **kwargs)
        for i, url_group in enumerate(grouper(url_list, BULK_LIMIT)):
            # Grouper will put None's on the end of the last group
            url_group = [url for url in url_group if url is not None]

            logger.info(
                "Uploading group %d: %s",
                i + 1,
                "\n".join(url_group)
            )

            # Create the documents
            logger.info("Creating the documents...")
            try:
                response = self.client.post(
                    "documents/",
                    json=[
                        merge_dicts(
                            params,
                            {
                                "title": self._get_title(url),
                                "file_url": url,
                            },
                        )
                        for url in url_group
                    ],
                )
            except (APIError, RequestException) as exc:
                if handle_errors:
                    logger.info(
                        "Error creating the following documents: %s\n%s",
                        str(exc),
                        "\n".join(url_group)
                    )
                    continue
                else:
                    raise

            create_json = response.json()
            obj_list.extend(create_json)

        logger.info("Upload URLs complete")

        # Pass back the list of documents
        return [Document(self.client, d) for d in obj_list]


class Mention:
    """A snippet from a document search"""

    def __init__(self, page, text):
        if page.startswith("page_no_"):
            page = page[len("page_no_") :]
        self.page = page
        self.text = text

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self}>"  # pragma: no cover

    def __str__(self):
        return f'{self.page} - "{self.text}"'
