"""
Custom exceptions for python-documentcloud
"""


class DocumentCloudError(Exception):
    """Base class for errors for python-documentcloud"""

    def __init__(self, *args, **kwargs):
        self.response = kwargs.pop("response", None)
        if self.response is not None:
            self.error = self.response.text
            self.status_code = self.response.status_code
            if not args:
                args = [f"{self.status_code} - {self.error}"]
        else:
            self.error = None
            self.status_code = None
        super().__init__(*args, **kwargs)


class DoesNotExistError(DocumentCloudError):
    """Raised when the user asks the API for something it cannot find"""


class MultipleObjectsReturnedError(DocumentCloudError):
    """Raised when the API returns multiple objects when it expected one"""


class DuplicateObjectError(DocumentCloudError):
    """Raised when an object is added to a unique list more than once"""


class CredentialsFailedError(DocumentCloudError):
    """Raised if unable to obtain an access token due to bad login credentials"""


class CredentialsMissingError(DocumentCloudError):
    """Raised if you attempt to perform an action which requires authentication
    without supplying credentials
    """


class APIError(DocumentCloudError):
    """Any other error calling the API"""
