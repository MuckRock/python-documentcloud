# Local
from .base import BaseAPIClient, BaseAPIObject


class User(BaseAPIObject):
    """A documentcloud user"""

    api_path = "users"
    writable_fields = ["organization"]

    def __str__(self):
        return self.username


class UserClient(BaseAPIClient):
    """Client for interacting with users"""

    api_path = "users"
    resource = User
