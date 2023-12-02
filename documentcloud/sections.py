# Local
from .base import BaseAPIObject, ChildAPIClient
from .toolbox import merge_dicts


class Section(BaseAPIObject):
    """A section of a document"""

    writable_fields = ["page_number", "title"]

    def __str__(self):
        return f"{self.title} - p{self.page}"

    @property
    def api_path(self):
        return f"documents/{self.document.id}/sections"

    @property
    def page(self):
        return self.page_number


class SectionClient(ChildAPIClient):
    """Client for interacting with Sections"""

    resource = Section

    @property
    def api_path(self):
        return f"documents/{self.parent.id}/sections"

    def create(self, title, page_number):
        data = {"title": title, "page_number": page_number}
        response = self.client.post(f"{self.api_path}/", json=data)
        return Section(
            self.client, merge_dicts(response.json(), {"document": self.parent})
        )
