# Local
from .base import APISet, BaseAPIClient, BaseAPIObject
from .constants import BULK_LIMIT, PER_PAGE_MAX
from .documents import Document
from .exceptions import DoesNotExistError, MultipleObjectsReturnedError
from .toolbox import get_id, grouper


class Project(BaseAPIObject):
    """A documentcloud project"""

    api_path = "projects"
    writable_fields = ["description", "private", "title"]

    def __init__(self, *args, **kwargs):
        per_page = kwargs.pop("per_page", PER_PAGE_MAX)
        super().__init__(*args, **kwargs)
        self._document_list = None
        self._per_page = per_page

    def __str__(self):
        return self.title

    def save(self):
        """Add the documents to the project as well"""
        super().save()
        if self._document_list:
            self.clear_documents()
            self.add_documents(self._document_list)

    @property
    def document_list(self):
        if self._document_list is None:
            response = self._client.get(
                f"{self.api_path}/{get_id(self.id)}/documents/",
                params={"per_page": self._per_page, "expand": ["document"]},
            )
            json = response.json()
            next_url = json["next"]
            results = json["results"]
            while next_url:
                response = self._client.get(next_url, full_url=True)
                json = response.json()
                next_url = json["next"]
                results.extend(json["results"])
            self._document_list = APISet(
                (Document(self._client, r["document"]) for r in results), Document
            )
        return self._document_list

    @document_list.setter
    def document_list(self, value):
        if value is None:
            self._document_list = APISet([], Document)
        elif isinstance(value, list):
            self._document_list = APISet(value, Document)
        else:
            raise TypeError("document_list must be set to a list or None")

    @property
    def documents(self):
        return self.document_list

    @documents.setter
    def documents(self, value):
        self.document_list = value

    @property
    def document_ids(self):
        return [d.id for d in self.document_list]

    def get_document(self, doc_id):
        response = self._client.get(
            f"{self.api_path}/{get_id(self.id)}/documents/{doc_id}",
            params={"expand": ["document"]},
        )
        return Document(self._client, response.json()["document"])

    def clear_documents(self):
        """Remove all documents from this project"""
        self._client.put(f"{self.api_path}/{self.id}/documents/", json=[])

    def add_documents(self, documents):
        """Efficient way to bulk add documents to a project"""
        data = [{"document": d.id} for d in documents]
        for data_group in grouper(data, BULK_LIMIT):
            # Grouper will put None's on the end of the last group
            data_group = [d for d in data_group if d is not None]
            self._client.patch(f"{self.api_path}/{self.id}/documents/", json=data_group)


class ProjectClient(BaseAPIClient):
    """Client for interacting with projects"""

    api_path = "projects"
    resource = Project

    # all is overridden to filter by the current user for backward compatibility
    def all(self, **params):
        return self.list(user=self.client.user_id, **params)

    def get(self, id=None, title=None):
        # pylint:disable=redefined-builtin, arguments-renamed
        # pylint disables are necessary for backward compatibility
        if id is not None and title is not None:
            raise ValueError(
                "You can only retrieve a Project by id or title, not by both"
            )
        elif id is None and title is None:
            raise ValueError("You must provide an id or a title to make a request.")

        if id is not None:
            return self.get_by_id(id)
        else:
            return self.get_by_title(title)

    def get_by_id(self, id_):
        return super().get(id_)

    def get_by_title(self, title):
        response = self.client.get(
            f"{self.api_path}/", params={"title": title, "user": self.client.user_id}
        )
        json = response.json()
        count = len(json["results"])
        if count == 0:
            raise DoesNotExistError(response=response)
        elif count > 1:
            raise MultipleObjectsReturnedError(response=response)

        return self.resource(self.client, json["results"][0])

    def create(self, title, description="", private=True, document_ids=None):
        data = {"title": title, "description": description, "private": private}
        response = self.client.post(self.api_path + "/", json=data)
        project = Project(self.client, response.json())
        if document_ids:
            data = [{"document": d} for d in document_ids]
            response = self.client.put(
                f"{self.api_path}/{project.id}/documents/", json=data
            )
        return project

    def get_or_create_by_title(self, title):
        try:
            project = self.get(title=title)
            created = False
        except DoesNotExistError:
            project = self.create(title=title)
            created = True
        return project, created
