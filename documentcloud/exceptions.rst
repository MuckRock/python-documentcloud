Exceptions
===========

The DocumentCloud Python library and the API have several potential errors. 

Importing Exceptions
--------------------

>>> from documentcloud.exceptions import APIError, DuplicateObjectError, CredentialsFailedError, DoesNotExistError, MultipleObjectsReturnedError

DocumentCloudError
-------------------

.. class:: documentcloud.exceptions.DocumentCloudError(Exception)
    Base class for errors for python-documentcloud

DuplicateObjectError
---------------------

.. class:: documentcloud.exceptions.DuplicateObjectError(DocumentCloudError)
    Raised when an object is added to a unique list more than once.

CredentialsFailedError
----------------------

.. class:: documentcloud.exceptions.CredentialsFailedError(DocumentCloudError)
    Raised if unable to obtain an access token due to bad login credentials.

APIError
--------

.. class:: documentcloud.exceptions.APIError(DocumentCloudError)
    Any other error calling the API. 

DoesNotExistError
-----------------

.. class:: documentcloud.exceptions.DoesNotExistError(APIError)
    Raised when the user asks the API for something it cannot find.

MultipleObjectsReturnedError
----------------------------

.. class:: documentcloud.exceptions.MultipleObjectsReturnedError(APIError)
    Raised when the API returns multiple objects when it expected one. 
