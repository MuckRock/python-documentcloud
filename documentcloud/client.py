"""
The public interface for the DocumentCloud API
"""

# Future
from __future__ import division, print_function, unicode_literals

# Standard Library
import logging
from functools import partial
from urllib.parse import parse_qs, urlparse

# Third Party
import ratelimit
import requests

# Local
from .constants import AUTH_URI, BASE_URI, RATE_LIMIT, RATE_PERIOD, TIMEOUT
from .documents import DocumentClient
from .exceptions import APIError, CredentialsFailedError, DoesNotExistError
from .organizations import OrganizationClient
from .projects import ProjectClient
from .toolbox import requests_retry_session
from .users import UserClient

logger = logging.getLogger("documentcloud")


class DocumentCloud(object):
    """
    The public interface for the DocumentCloud API
    """

    def __init__(
        self,
        username=None,
        password=None,
        base_uri=BASE_URI,
        auth_uri=AUTH_URI,
        timeout=TIMEOUT,
        loglevel=None,
        rate_limit=True,
        rate_limit_sleep=True,
    ):
        self.base_uri = base_uri
        self.auth_uri = auth_uri
        self.username = username
        self.password = password
        self._user_id = None
        self.timeout = timeout
        self.refresh_token = None
        self.session = requests.Session()
        self._set_tokens()

        if loglevel:  # pragma: no cover
            logging.basicConfig(
                level=loglevel,
                format="%(asctime)s %(levelname)-8s %(name)-25s %(message)s",
            )
        else:
            logger.addHandler(logging.NullHandler())

        self.documents = DocumentClient(self)
        self.projects = ProjectClient(self)
        self.users = UserClient(self)
        self.organizations = OrganizationClient(self)

        if rate_limit:
            self._request = ratelimit.limits(calls=RATE_LIMIT, period=RATE_PERIOD)(
                self._request
            )
            if rate_limit_sleep:
                self._request = ratelimit.sleep_and_retry(self._request)

    def _set_tokens(self):
        """Set the refresh and access tokens"""
        if self.refresh_token:
            access_token, self.refresh_token = self._refresh_tokens(self.refresh_token)
        elif self.username and self.password:
            access_token, self.refresh_token = self._get_tokens(
                self.username, self.password
            )
        else:
            access_token = None

        if access_token:
            self.session.headers.update(
                {"Authorization": "Bearer {}".format(access_token)}
            )

    def _get_tokens(self, username, password):
        """Get an access and refresh token in exchange for the username and password"""
        response = requests_retry_session().post(
            "{}token/".format(self.auth_uri),
            json={"username": username, "password": password},
            timeout=self.timeout,
        )

        if response.status_code == requests.codes.UNAUTHORIZED:
            raise CredentialsFailedError("The username and password is incorrect")

        self.raise_for_status(response)

        json = response.json()
        return (json["access"], json["refresh"])

    def _refresh_tokens(self, refresh_token):
        """Refresh the access and refresh tokens"""
        response = requests_retry_session().post(
            "{}refresh/".format(self.auth_uri),
            json={"refresh": refresh_token},
            timeout=self.timeout,
        )

        if response.status_code == requests.codes.UNAUTHORIZED:
            # refresh token is expired
            return self._get_tokens(self.username, self.password)

        self.raise_for_status(response)

        json = response.json()
        return (json["access"], json["refresh"])

    @property
    def user_id(self):
        if self._user_id is None:
            user = self.users.get("me")
            self._user_id = user.id
        return self._user_id

    def _request(self, method, url, raise_error=True, **kwargs):
        """Generic method to make API requests"""
        # pylint: disable=method-hidden
        logger.info("request: %s - %s - %s", method, url, kwargs)
        set_tokens = kwargs.pop("set_tokens", True)
        full_url = kwargs.pop("full_url", False)

        if not full_url:
            url = "{}{}".format(self.base_uri, url)

        # set the API to version 2.0
        parsed_url = urlparse(url)
        if "version" not in parse_qs(parsed_url.query):
            # check to avoid double setting version
            kwargs.setdefault("params", {}).update({"version": "2.0"})

        response = requests_retry_session(session=self.session).request(
            method, url, timeout=self.timeout, **kwargs
        )
        logger.debug("response: %s - %s", response.status_code, response.content)
        if response.status_code == requests.codes.FORBIDDEN and set_tokens:
            self._set_tokens()
            # track set_tokens to not enter an infinite loop
            kwargs["set_tokens"] = False
            return self._request(method, url, full_url=True, **kwargs)

        if raise_error:
            self.raise_for_status(response)

        return response

    def __getattr__(self, attr):
        """Generate methods for each HTTP request type"""
        methods = ["get", "options", "head", "post", "put", "patch", "delete"]
        if attr in methods:
            return partial(self._request, attr)
        raise AttributeError(
            "'{}' object has no attribute '{}'".format(self.__class__.__name__, attr)
        )

    def raise_for_status(self, response):
        """Raise for status with a custom error class"""
        try:
            response.raise_for_status()
        except requests.exceptions.RequestException as exc:
            if exc.response.status_code == 404:
                raise DoesNotExistError(response=exc.response)
            else:
                raise APIError(response=exc.response)
