# Future
from __future__ import division, print_function, unicode_literals

# Standard Library
import time

# Third Party
import pytest
import ratelimit

# DocumentCloud
from documentcloud import DocumentCloud
from documentcloud.constants import RATE_LIMIT
from documentcloud.exceptions import APIError, CredentialsFailedError

# pylint: disable=protected-access


def test_set_tokens_credentials(client):
    """Test setting the tokens using credentials"""
    client.refresh_token = None
    del client.session.headers["Authorization"]
    client._set_tokens()
    assert client.refresh_token
    assert "Authorization" in client.session.headers


def test_set_tokens_refresh(client):
    """Test setting the tokens using refresh token"""
    # first set tokens sets, refresh token, second one uses it
    client.refresh_token = None
    del client.session.headers["Authorization"]
    client._set_tokens()
    client._set_tokens()
    assert client.refresh_token
    assert "Authorization" in client.session.headers


def test_set_tokens_none(public_client):
    """Test setting the tokens with no credentials"""
    public_client._set_tokens()
    assert public_client.refresh_token is None
    assert "Authorization" not in public_client.session.headers


def test_get_tokens(client):
    """Test getting access and refresh tokens using valid credentials"""
    access, refresh = client._get_tokens(client.username, client.password)
    assert access
    assert refresh


def test_get_tokens_bad_credentials(client):
    """Test getting access and refresh tokens using invalid credentials"""
    with pytest.raises(CredentialsFailedError):
        client._get_tokens(client.username, "foo")


def test_refresh_tokens(client):
    """Test refreshing the tokens"""
    access, refresh = client._refresh_tokens(client.refresh_token)
    assert access
    assert refresh


def test_user_id(client):
    assert client.user_id


def test_user_id_public(public_client):
    # pylint: disable=pointless-statement
    with pytest.raises(APIError, match=r"404"):
        public_client.user_id


def test_bad_attr(client):
    with pytest.raises(AttributeError):
        assert client.foo


def test_rate_limit(rate_client):
    with pytest.raises(ratelimit.RateLimitException):
        for _ in range(RATE_LIMIT * 2):
            rate_client.users.get("me")


@pytest.mark.short
@pytest.mark.vcr(cassette_library_dir="tests/cassettes/short_fixtures")
def test_expired_access_token(short_client, record_mode):
    # get fresh tokens
    short_client._set_tokens()
    old_refresh_token = short_client.refresh_token
    # wait for the access token to expire
    if record_mode == "all":
        time.sleep(3)
    # make a request
    assert short_client.users.get("me")
    # check the refresh token was updated
    assert old_refresh_token != short_client.refresh_token


@pytest.mark.short
@pytest.mark.vcr(cassette_library_dir="tests/cassettes/short_fixtures")
def test_expired_refresh_token(short_client, record_mode):
    # get fresh tokens
    short_client._set_tokens()
    old_refresh_token = short_client.refresh_token
    # wait for the access and refresh tokens to expire
    if record_mode == "all":
        time.sleep(6)
    # make a request
    assert short_client.users.get("me")
    # check the refresh token was updated
    assert old_refresh_token != short_client.refresh_token


def test_endpoint_rate_limit_burst_exhaustion():
    """Token bucket should block after burst capacity is exhausted"""
    client = DocumentCloud()
    # Exhaust the search burst (capacity=50)
    _pattern_method, _pattern, limiter, bucket_key = client._endpoint_limiters[0]
    for _ in range(50):
        limiter.consume(bucket_key)
    assert not limiter.consume(bucket_key)


def test_endpoint_rate_limit_method_specificity():
    """GET and POST to documents/ should use different limiters"""
    client = DocumentCloud()
    limiters = {(pm, p): lim for pm, p, lim, _ in client._endpoint_limiters}
    assert limiters[("GET", "files/")] is not limiters[("POST", "documents/")]


def test_endpoint_rate_limit_pattern_ordering():
    """documents/search should match before documents/"""
    client = DocumentCloud()
    url = "documents/search/"
    matched = next(
        p for pm, p, _, _ in client._endpoint_limiters if pm == "GET" and p in url
    )
    assert matched == "documents/search"


def test_asset_rate_limit_burst_exhaustion():
    """Asset token bucket should block after burst capacity is exhausted"""
    client = DocumentCloud()
    limiter = client.documents._asset_limiter
    for _ in range(100):
        limiter.consume("asset")
    assert not limiter.consume("asset")


def test_asset_rate_limit_refills():
    """Asset token bucket should refill over time"""
    client = DocumentCloud()
    limiter = client.documents._asset_limiter
    for _ in range(100):
        limiter.consume("asset")
    assert not limiter.consume("asset")
    time.sleep(5)
    assert limiter.consume("asset")


def test_endpoint_rate_limit_buckets_are_independent():
    """Exhausting one endpoint's bucket should not affect another"""
    client = DocumentCloud()
    limiters = {(pm, p): (lim, bk) for pm, p, lim, bk in client._endpoint_limiters}
    search_limiter, search_key = limiters[("GET", "documents/search")]
    files_limiter, files_key = limiters[("GET", "files/")]

    # Exhaust search bucket
    for _ in range(50):
        search_limiter.consume(search_key)
    assert not search_limiter.consume(search_key)

    # Files bucket should still have tokens
    assert files_limiter.consume(files_key)


def test_endpoint_rate_limit_no_match_for_unrecognized_url():
    """Unrecognized URLs should not match any endpoint limiter"""
    client = DocumentCloud()
    url = "users/me/"
    matched = next(
        (p for pm, p, _, _ in client._endpoint_limiters if p in url),
        None,
    )
    assert matched is None
