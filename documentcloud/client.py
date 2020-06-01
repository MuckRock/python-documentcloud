"""
The public interface for the DocumentCloud API
"""

from functools import partial

import requests

from .documents import DocumentClient
from .toolbox import CredentialsFailedError, requests_retry_session

BASE_URI = "https://api.beta.documentcloud.org/api/"
AUTH_URI = "https://accounts.muckrock.com/api/"
TIMEOUT = 10


class DocumentCloud:
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
        debug=False,
    ):
        self.base_uri = base_uri
        self.auth_uri = auth_uri
        self.username = username
        self.password = password
        self.timeout = timeout
        # XXX use proper logging
        self.debug = debug
        self.refresh_token = None
        self.session = requests.Session()
        self._set_tokens()

        self.documents = DocumentClient(self)

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
            self.session.headers.update({"Authorization": f"Bearer {access_token}"})

    def _get_tokens(self, username, password):
        """Get an access and refresh token in exchange for the username and password"""
        response = requests_retry_session().post(
            f"{self.auth_uri}token/",
            json={"username": username, "password": password},
            timeout=self.timeout,
        )

        if response.status_code == requests.codes.UNAUTHORIZED:
            raise CredentialsFailedError("The username and password is incorrect")

        # XXX catch and convert to internal error type?
        response.raise_for_status()

        json = response.json()
        return (json["access"], json["refresh"])

    def _refresh_tokens(self, refresh_token):
        """Refresh the access and refresh tokens"""
        response = requests_retry_session().post(
            f"{self.auth_uri}refresh/",
            json={"refresh": refresh_token},
            timeout=self.timeout,
        )

        if response.status_code == requests.codes.UNAUTHORIZED:
            # refresh token is expired
            return self._get_tokens(self.username, self.password)

        # XXX catch and convert to internal error type?
        response.raise_for_status()

        json = response.json()
        return (json["access"], json["refresh"])

    def _request(self, method, url, **kwargs):
        """Generic method to make API requests"""
        # XXX proper logging
        if self.debug:
            print(f"{method}: {url} - {kwargs}")
        set_tokens = kwargs.pop("set_tokens", True)
        response = requests_retry_session(session=self.session).request(
            method, f"{self.base_uri}{url}", timeout=self.timeout, **kwargs
        )
        if self.debug:
            print(f"Response: {response.status_code} - {response.content}")
        if response.status_code == requests.codes.FORBIDDEN and set_tokens:
            self._set_tokens()
            # track set_tokens to not enter an infinite loop
            kwargs["set_tokens"] = False
            return self._request(method, url, **kwargs)

        return response

    def __getattr__(self, attr):
        """Generate methods for each HTTP request type"""
        methods = ["get", "options", "head", "post", "put", "patch", "delete"]
        if attr in methods:
            return partial(self._request, attr)
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{attr}'"
        )
