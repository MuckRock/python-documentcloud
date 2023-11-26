# Local
from .base import BaseAPIClient, BaseAPIObject


class Organization(BaseAPIObject):
    """A documentcloud organization"""

    api_path = "organizations"
    writable_fields = []

    def __str__(self):
        return self.name


class OrganizationClient(BaseAPIClient):
    """Client for interacting with organizations"""

    api_path = "organizations"
    resource = Organization
