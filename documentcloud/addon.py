"""
This is a base class for DocumentCloud Add-Ons to inherit from.
It provides some common Add-On functionality.
"""

# Standard Library
import argparse
import json
import os
import sys

# Third Party
import fastjsonschema
import requests
import yaml

# Local
from .client import DocumentCloud


class BaseAddOn:
    """Functionality shared between all Add-On types"""

    def __init__(self):
        args = self._parse_arguments()
        client = self._create_client(args)

        # a unique identifier for this run
        self.id = args.pop("id", None)
        # a unique identifier for the event that triggered this run
        self.event_id = args.pop("event_id", None)
        # Documents is a list of document IDs which were selected to run with this
        # addon activation
        self.documents = args.pop("documents", None)
        # Query is the search query selected to run with this addon activation
        self.query = args.pop("query", None)
        # user and org IDs
        self.user_id = args.pop("user", None)
        self.org_id = args.pop("organization", None)
        # add on specific data
        self.data = args.pop("data", None)

    def _create_client(self, args):
        client_kwargs = {
            k: v
            for k, v in args.items()
            if k in ["base_uri", "auth_uri"] and v is not None
        }
        username = (
            args["username"] if args["username"] else os.environ.get("DC_USERNAME")
        )
        password = (
            args["password"] if args["password"] else os.environ.get("DC_PASSWORD")
        )
        if username and password:
            client_kwargs["username"] = username
            client_kwargs["password"] = password
        self.client = DocumentCloud(**client_kwargs)
        if args["refresh_token"] is not None:
            self.client.refresh_token = args["refresh_token"]
        if args["token"] is not None:
            self.client.session.headers.update(
                {"Authorization": "Bearer {}".format(args["token"])}
            )

        # custom user agent for AddOns
        self.client.session.headers["User-Agent"] += " (DC AddOn)"

    def _parse_arguments(self):
        """Parse command line arguments"""
        parser = argparse.ArgumentParser(
            description="Run a DocumentCloud add on.\n\n"
            "Command line arguments are provided for testing locally.\n"
            "A JSON blob may also be passed in, as is done when running on "
            "GitHub actions."
        )
        parser.add_argument(
            "--username",
            help="DocumentCloud username - "
            "can also be passed in environment variable DC_USERNAME",
        )
        parser.add_argument(
            "--password",
            help="DocumentCloud password - "
            "can also be passed in environment variable DC_PASSWORD",
        )
        parser.add_argument("--token", help="DocumentCloud access token")
        parser.add_argument("--refresh_token", help="DocumentCloud refresh token")
        parser.add_argument("--documents", type=int, nargs="+", help="Document IDs")
        parser.add_argument("--query", help="Search query")
        parser.add_argument("--data", help="Parameter JSON")
        parser.add_argument("--base_uri", help="Set an alternate base URI")
        parser.add_argument("--auth_uri", help="Set an alternate auth URI")
        parser.add_argument(
            "json", nargs="?", default="{}", help="JSON blob for passing in arguments"
        )
        args = parser.parse_args()
        # convert args to a dictionary
        args = vars(args)
        if args["data"] is None:
            args["data"] = {}
        else:
            args["data"] = json.loads(args["data"])

        blob = args.pop("json")
        if blob:
            blob = json.loads(blob)
            if blob:
                # merge json blob into the arguments
                args.update(blob)

        # validate parameter data
        try:
            with open("config.yaml") as config:
                schema = yaml.safe_load(config)
                args["data"] = fastjsonschema.validate(schema, args["data"])
        except FileNotFoundError:
            pass
        except fastjsonschema.JsonSchemaException as exc:
            print(exc.message)
            sys.exit(1)
        return args

    def send_mail(self, subject, content):
        """Send yourself an email"""
        return self.client.post(
            "messages/", json={"subject": subject, "content": content}
        )


class AddOn(BaseAddOn):
    """Base functionality for DocumentCloud Add-Ons."""

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
        # we want data to be in binary mode
        if "b" in file.mode:
            # already binary
            data = file
        else:
            # text file's buffer is in binary mode
            data = file.buffer
        response = requests.put(presigned_url, data=data)
        response.raise_for_status()
        return self.client.patch(
            f"addon_runs/{self.id}/", json={"file_name": file_name}
        )

    def load_event_data(self):
        """Load persistent data for this event"""
        if not self.event_id:
            return None

        response = self.client.get(f"addon_events/{self.event_id}/")
        response.raise_for_status()
        return response.json()["scratch"]

    def store_event_data(self, scratch):
        """Store persistent data for this event"""
        if not self.event_id:
            return

        return self.client.patch(
            f"addon_events/{self.event_id}/", json={"scratch": scratch}
        )

    def get_document_count(self):
        """Get document count from either selected or queried documents"""
        if self.documents:
            return len(self.documents)
        elif self.query:
            documents = self.client.documents.search(self.query)
            return documents.count

    def get_documents(self):
        """Get documents from either selected or queried documents"""
        if self.documents:
            for document in self.client.documents.list(id__in=self.documents):
                yield document
        elif self.query:
            documents = self.client.documents.search(self.query)
            for document in documents:
                yield document


class CronAddOn(BaseAddOn):
    """DEPREACTED"""
