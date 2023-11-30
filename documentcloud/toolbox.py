"""
A few toys the API will use.
"""

# Standard Library
from itertools import zip_longest
from urllib.parse import urlparse

# Third Party
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def requests_retry_session(
    retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504), session=None
):
    """Automatic retries for HTTP requests
    See: https://www.peterbe.com/plog/best-practice-with-retries-with-requests
    """
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def get_id(id_):
    """Allow specifying old or new style IDs and convert old style to new style IDs

    Old style: 123-the-slug
    New style: 123 or the-slug-123
    """

    if isinstance(id_, int):
        return id_
    elif "-" in id_:
        front = id_.split("-", 1)[0]
        if front.isdigit():
            return front
        back = id_.rsplit("-", 1)[-1]
        if back.isdigit():
            return back

    return id_


def is_url(url):
    """Is `url` a valid url?"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except (ValueError, AttributeError):
        return False


def grouper(iterable, num, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * num
    return zip_longest(*args, fillvalue=fillvalue)


def merge_dicts(*dicts):
    merged = {}
    for dict_ in dicts:
        merged.update(dict_)
    return merged
