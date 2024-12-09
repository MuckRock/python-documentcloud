# Import SquareletClient from python-squarelet
# Standard Library
import logging

# Third Party
from squarelet import SquareletClient

# Local
# Local Imports
from .documents import DocumentClient
from .organizations import OrganizationClient
from .projects import ProjectClient
from .users import UserClient

logger = logging.getLogger("documentcloud")

class DocumentCloud:
    """
    The public interface for the DocumentCloud API, now integrated with SquareletClient
    """
    # pylint:disable=too-many-positional-arguments
    def __init__(
        self,
        username=None,
        password=None,
        base_uri="https://api.www.documentcloud.org/api/",
        auth_uri="https://accounts.muckrock.com/api/",
        timeout=20,
        loglevel=None,
        rate_limit=True,
        rate_limit_sleep=True,
    ):
        # Initialize SquareletClient for authentication and request handling
        self.squarelet_client = SquareletClient(
            base_uri=base_uri,
            username=username,
            password=password,
            auth_uri=auth_uri,
            timeout=timeout,
            rate_limit=rate_limit,
            rate_limit_sleep=rate_limit_sleep
        )

        # Set up logging
        if loglevel:
            logging.basicConfig(
                level=loglevel,
                format="%(asctime)s %(levelname)-8s %(name)-25s %(message)s",
            )
        else:
            logger.addHandler(logging.NullHandler())

        # Initialize the sub-clients using SquareletClient
        self.documents = DocumentClient(self.squarelet_client)
        self.projects = ProjectClient(self.squarelet_client)
        self.users = UserClient(self.squarelet_client)
        self.organizations = OrganizationClient(self.squarelet_client)

    def _request(self, method, url, raise_error=True, **kwargs):
        """Delegates request to the SquareletClient's _request method"""
        return self.squarelet_client.request(method, url, raise_error, **kwargs)

    @property
    def user_id(self):
        """Get the user ID of the authenticated user"""
        user = self.users.get("me")
        return user.id
