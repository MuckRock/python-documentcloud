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


class DuplicateObjectError(DocumentCloudError):
    """Raised when an object is added to a unique list more than once"""


class CredentialsFailedError(DocumentCloudError):
    """Raised if unable to obtain an access token due to bad login credentials"""


class APIError(DocumentCloudError):
    """Any other error calling the API"""


class DoesNotExistError(APIError):
    """Raised when the user asks the API for something it cannot find"""


class MultipleObjectsReturnedError(APIError):
    """Raised when the API returns multiple objects when it expected one"""
