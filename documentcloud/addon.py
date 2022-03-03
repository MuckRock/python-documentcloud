"""
This is a base class for DocumentCloud Add-Ons to inherit from.
It provides some common Add-On functionality.
"""

# Standard Library
import json
import os
import sys

# Third Party
import requests

# Local
from .client import DocumentCloud


class BaseAddOn:
    """Functionality shared between normal Add-On's and Cron Add-On's"""

    def send_mail(self, subject, content):
        """Send yourself an email"""
        return self.client.post(
            "messages/", json={"subject": subject, "content": content}
        )


class AddOn(BaseAddOn):
    """Base functionality for DocumentCloud Add-Ons."""

    def __init__(self):
        token, base_uri = self._load_params()
        # set up the client
        kwargs = {"base_uri": base_uri} if base_uri is not None else {}
        self.client = DocumentCloud(**kwargs)
        # if no token is passed in, the Add-On will only have anonymous access
        # to the API
        if token is not None:
            self.client.session.headers.update(
                {"Authorization": "Bearer {}".format(token)}
            )
        self.client.session.headers["User-Agent"] += " (DC AddOn)"

    def _load_params(self):
        """Load the parameters passed in to the GitHub Action."""
        params = json.loads(sys.argv[1])
        # token is a JWT to use to authenticate against the DocumentCloud API
        token = params.pop("token", None)
        # base_uri is the URI to make API calls to - allows the addon to function
        # in non-production environments
        base_uri = params.pop("base_uri", None)

        # a unique identifier for this run
        self.id = params.pop("id", None)
        # Documents is a list of document IDs which were selected to run with this
        # addon activation
        self.documents = params.pop("documents", None)
        # Query is the search query selected to run with this addon activation
        self.query = params.pop("query", None)
        # user and org IDs
        self.user_id = params.pop("user", None)
        self.org_id = params.pop("organization", None)
        # add on specific data
        self.data = params.pop("data", None)

        return token, base_uri

    def set_progress(self, progress):
        """Set the progress as a percentage between 0 and 100."""
        if not self.id:
            return None
        assert 0 <= progress <= 100
        return self.client.patch(f"addon_runs/{self.id}/", json={"progress": progress})

    def set_message(self, message):
        """Set the progress message."""
        if not self.id:
            return None
        return self.client.patch(f"addon_runs/{self.id}/", json={"message": message})

    def upload_file(self, file):
        """Uploads a file to the addon run."""
        if not self.id:
            return None
        # go to the beginning of the file
        file.seek(0)
        file_name = os.path.basename(file.name)
        resp = self.client.get(
            f"addon_runs/{self.id}/", params={"upload_file": file_name}
        )
        presigned_url = resp.json()["presigned_url"]
        # use buffer as it should always be binary, which requests wants
        response = requests.put(presigned_url, data=file.buffer)
        response.raise_for_status()
        return self.client.patch(
            f"addon_runs/{self.id}/", json={"file_name": file_name}
        )



class CronAddOn(BaseAddOn):
    """Base functionality for a Cron Add-On"""

    def __init__(self):
        self.client = DocumentCloud(
            username=os.environ["DC_USERNAME"], password=os.environ["DC_PASSWORD"]
        )
