# Future
from __future__ import division, print_function, unicode_literals

# Third Party
from future.utils import python_2_unicode_compatible

# Local
from .base import APISet, BaseAPIClient, BaseAPIObject
from .constants import BULK_LIMIT, PER_PAGE_MAX
from .documents import Document
from .exceptions import DoesNotExistError, MultipleObjectsReturnedError
from .toolbox import get_id, grouper


@python_2_unicode_compatible
class Project(BaseAPIObject):
    """A documentcloud project"""

    api_path = "projects"
    writable_fields = ["description", "private", "title"]

    def __init__(self, *args, **kwargs):
        per_page = kwargs.pop("per_page", PER_PAGE_MAX)
        super(Project, self).__init__(*args, **kwargs)
        self._document_list = None
        self._per_page = per_page

    def __str__(self):
        return self.title

    def save(self):
        """Add the documents to the project as well"""
        # XXX this is broken due to multiple calls to PUT
        # conflicting with each other
        super(Project, self).save()
        if self._document_list:
            data = [{"document": d} for d in self.document_ids]
            for data_group in grouper(data, BULK_LIMIT):
                # Grouper will put None's on the end of the last group
                data_group = [d for d in data_group if d is not None]
                self._client.put(
                    "{}/{}/documents/".format(self.api_path, self.id), json=data_group
                )

    @property
    def document_list(self):
        if self._document_list is None:
            response = self._client.get(
                "{}/{}/documents/".format(self.api_path, get_id(self.id)),
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
            "{}/{}/documents/{}".format(self.api_path, get_id(self.id), doc_id),
            params={"expand": ["document"]},
        )
        return Document(self._client, response.json()["document"])


class ProjectClient(BaseAPIClient):
    """Client for interacting with projects"""

    api_path = "projects"
    resource = Project

    # all is overriden to filter by the current user for backward compatibility
    def all(self, **params):
        return self.list(user=self.client.user_id, **params)

    def get(self, id=None, title=None):
        # pylint:disable=redefined-builtin, arguments-differ
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
        return super(ProjectClient, self).get(id_)

    def get_by_title(self, title):
        response = self.client.get(
            self.api_path + "/", params={"title": title, "user": self.client.user_id}
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
                "{}/{}/documents/".format(self.api_path, project.id), json=data
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
