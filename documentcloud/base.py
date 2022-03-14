# Future
from __future__ import division, print_function, unicode_literals

# Standard Library
from builtins import str
from copy import copy

# Third Party
from dateutil.parser import parse as dateparser
from future.utils import python_2_unicode_compatible

# Local
from .exceptions import DuplicateObjectError
from .toolbox import get_id, merge_dicts


@python_2_unicode_compatible
class APIResults(object):
    """Class for encapsulating paginated list results from the API"""

    def __init__(
        self, resource, client, response, extra=None, next_=None, previous=None
    ):
        if extra is None:
            extra = {}

        self.resource = resource
        self.client = client
        json = response.json()

        self.count = json.get("count")
        self.next_url = json["next"]
        self.previous_url = json["previous"]
        self._next = next_
        self._previous = previous
        self.results = [
            resource(client, merge_dicts(r, extra)) for r in json["results"]
        ]

    def __repr__(self):
        return "<APIResults: {!r}".format(self.results)  # pragma: no cover

    def __str__(self):
        return "[{}]".format(", ".join(str(r) for r in self.results))

    def __getitem__(self, key):
        # pylint: disable=unsubscriptable-object
        length = len(self.results)
        if key < length:
            return self.results[key]
        elif self.next_url:
            return self.next[key - length]
        raise IndexError

    def __iter__(self):
        for result in self.results:
            yield result
        if self.next_url:
            # pylint: disable=not-an-iterable
            for result in self.next:
                yield result
        else:
            return

    def _fetch(self, url, next_=None, previous=None):
        if url:
            response = self.client.get(url, full_url=True)
            return APIResults(
                self.resource, self.client, response, next_=next_, previous=previous
            )
        else:
            return None

    @property
    def next(self):
        if self._next is None:
            self._next = self._fetch(self.next_url, previous=self)
        return self._next

    @property
    def previous(self):
        if self._previous is None:
            self._previous = self._fetch(self.previous_url, next_=self)
        return self._previous


class BaseAPIClient(object):
    """Base client for all API resources"""

    # subclasses should set these
    api_path = None
    resource = None

    def __init__(self, client):
        self.client = client

    def get(self, id_, expand=None):
        """Get a resource by its ID"""
        if expand is not None:
            params = {"expand": ",".join(expand)}
        else:
            params = {}
        response = self.client.get(
            "{}/{}/".format(self.api_path, get_id(id_)), params=params
        )
        # pylint: disable=not-callable
        return self.resource(self.client, response.json())

    def delete(self, id_):
        """Deletes a resource"""
        self.client.delete("{}/{}/".format(self.api_path, get_id(id_)))

    def all(self, **params):
        return self.list(**params)

    def list(self, **params):
        response = self.client.get(self.api_path + "/", params=params)
        return APIResults(self.resource, self.client, response)


class ChildAPIClient(BaseAPIClient):
    """Base client for sub resources"""

    def __init__(self, client, parent):
        super(ChildAPIClient, self).__init__(client)
        self.parent = parent

    def list(self, **params):
        response = self.client.get(self.api_path + "/", params=params)
        parent_name = self.parent.__class__.__name__.lower()
        return APIResults(
            self.resource, self.client, response, {parent_name: self.parent}
        )

    # try to emulate old behavior by making it act as the list of returned resources
    def __iter__(self):
        return iter(self.list())

    def __getitem__(self, key):
        return self.list()[key]


class BaseAPIObject(object):
    """Base object for all API resources"""

    date_fields = []

    def __init__(self, client, dict_):
        self.__dict__ = dict_
        self._client = client
        for field in self.date_fields:
            setattr(self, field, dateparser(getattr(self, field)))

    def __repr__(self):
        return "<{}: {} - {}>".format(
            self.__class__.__name__, self.id, self
        )  # pragma: no cover

    def __eq__(self, obj):
        return isinstance(obj, type(self)) and self.id == obj.id

    def put(self):
        """Alias for save"""
        return self.save()

    def save(self):
        data = {f: getattr(self, f) for f in self.writable_fields if hasattr(self, f)}
        self._client.put("{}/{}/".format(self.api_path, self.id), json=data)

    def delete(self):
        self._client.delete("{}/{}/".format(self.api_path, self.id))


@python_2_unicode_compatible
class APISet(list):
    def __init__(self, iterable, resource):
        super(APISet, self).__init__(iterable)
        self.resource = resource
        if not all(isinstance(obj, self.resource) for obj in self):
            raise TypeError(
                "Only {} can be added to this list".format(
                    self.resource.__class__.__name__
                )
            )
        ids = [obj.id for obj in self]
        for id_ in ids:
            if ids.count(id_) > 1:
                raise DuplicateObjectError(
                    "Object with ID {} appears in the list more than once".format(id_)
                )

    def append(self, obj):
        if not isinstance(obj, self.resource):
            raise TypeError(
                "Only {} can be added to this list".format(
                    self.resource.__class__.__name__
                )
            )
        if obj.id in [i.id for i in self]:
            raise DuplicateObjectError(
                "Object with ID {} appears in the list more than once".format(obj.id)
            )
        super(APISet, self).append(copy(obj))

    def add(self, obj):
        if not isinstance(obj, self.resource):
            raise TypeError(
                "Only {} can be added to this list".format(
                    self.resource.__class__.__name__
                )
            )
        # skip duplicates silently
        if obj.id not in [i.id for i in self]:
            super(APISet, self).append(copy(obj))

    def extend(self, list_):
        if not all(isinstance(obj, self.resource) for obj in list_):
            raise TypeError(
                "Only {} can be added to this list".format(
                    self.resource.__class__.__name__
                )
            )
        ids = [obj.id for obj in self + list_]
        for id_ in ids:
            if ids.count(id_) > 1:
                raise DuplicateObjectError(
                    "Object with ID {} appears in the list more than once".format(id)
                )
        super(APISet, self).extend(copy(obj) for obj in list_)
