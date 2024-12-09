"""
Custom exceptions for python-documentcloud
"""

# pylint: disable=unused-import
# Import exceptions from python-squarelet
from squarelet.exceptions import SquareletError as DocumentCloudError
from squarelet.exceptions import DuplicateObjectError
from squarelet.exceptions import CredentialsFailedError
from squarelet.exceptions import APIError
from squarelet.exceptions import DoesNotExistError
from squarelet.exceptions import MultipleObjectsReturnedError
