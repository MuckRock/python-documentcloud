# Standard Library
import logging
import time

# Third Party
import token_bucket
from squarelet import SquareletClient

# Local
from .documents import DocumentClient
from .organizations import OrganizationClient
from .projects import ProjectClient
from .users import UserClient

logger = logging.getLogger("documentcloud")

# Per-endpoint rate limits applied on top of the global squarelet limit.
# Format: (method, url_pattern, rate_per_second, capacity)
#
# Endpoint              Rate        Burst   Notes
# --------              ----        -----   -----
# GET  documents/search  15/min      50
# POST documents/        12/min      100     25 docs/bulk call = up to 300 docs/min
# PUT  documents/        12/min      100     25 docs/bulk call = up to 300 docs/min
# GET  files/            15/min      100     PDFs, full text, and other private assets
ENDPOINT_RATE_LIMITS = [
    ("GET", "documents/search", 15 / 60, 50),
    ("POST", "documents/", 12 / 60, 100),
    ("PUT", "documents/", 12 / 60, 100),
    ("GET", "files/", 15 / 60, 100),
]


class DocumentCloud(SquareletClient):
    """
    The public interface for the DocumentCloud API, now integrated with SquareletClient
    """

    def __init__(
        self,
        username=None,
        password=None,
        base_uri="https://api.www.documentcloud.org/api/",
        auth_uri="https://accounts.muckrock.com/api/",
        timeout=20,
        loglevel=None,
        rate_limit=True,
        rate_limit_sleep=True,
    ):
        # Initialize SquareletClient for authentication and request handling
        super().__init__(
            base_uri=base_uri,
            username=username,
            password=password,
            auth_uri=auth_uri,
            timeout=timeout,
            rate_limit=rate_limit,
            rate_limit_sleep=rate_limit_sleep,
        )

        # Set up logging
        if loglevel:
            logging.basicConfig(
                level=loglevel,
                format="%(asctime)s %(levelname)-8s %(name)-25s %(message)s",
            )
        else:
            logger.addHandler(logging.NullHandler())

        # Build per-endpoint token bucket rate limiters
        storage = token_bucket.MemoryStorage()
        self._endpoint_limiters = [
            (
                pattern_method,
                pattern,
                token_bucket.Limiter(rate=rate, capacity=capacity, storage=storage),
                f"{pattern_method}:{pattern}",
            )
            for pattern_method, pattern, rate, capacity in ENDPOINT_RATE_LIMITS
        ]

        # Initialize the sub-clients using SquareletClient
        self.documents = DocumentClient(self)
        self.projects = ProjectClient(self)
        self.users = UserClient(self)
        self.organizations = OrganizationClient(self)

    def request(self, method, url, raise_error=True, **kwargs):
        for pattern_method, pattern, limiter, bucket_key in self._endpoint_limiters:
            if pattern_method.upper() == method.upper() and pattern in url:
                if not limiter.consume(bucket_key):
                    logger.warning(
                        "Rate limit reached for %s %s, throttling...",
                        method.upper(),
                        pattern,
                    )
                    while not limiter.consume(bucket_key):
                        time.sleep(0.1)
                return super().request(method, url, raise_error=raise_error, **kwargs)
        return super().request(method, url, raise_error=raise_error, **kwargs)
