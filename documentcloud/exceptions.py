"""
Custom exceptions for python-documentcloud
"""

# Third Party
# pylint: disable=unused-import
# Import exceptions from python-squarelet
from squarelet.exceptions import (
    APIError,
    CredentialsFailedError,
    DoesNotExistError,
    DuplicateObjectError,
    MultipleObjectsReturnedError,
    SquareletError as DocumentCloudError,
)
