"""
This is a base class for DocumentCloud Add-Ons to inherit from.
It provides some common Add-On functionality.
"""

# Standard Library
import argparse
import json
import os
import sys
import time

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
        self._create_client(args)

        # a unique identifier for this run
        self.id = args.pop("id", None)
        # the id of the add-on
        self.addon_id = args.pop("addon_id", None)
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
        # title of the addon
        self.title = args.pop("title", None)

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
                {"Authorization": f"Bearer {args['token']}"}
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
            if "payload" in blob:
                # merge v2 json blob into the arguments
                args.update(blob["payload"])
            elif blob:
                # merge v1 json blob into the arguments
                args.update(blob)

        # validate parameter data
        try:
            with open("config.yaml", encoding="utf-8") as config:
                schema = yaml.safe_load(config)
                args["data"] = fastjsonschema.validate(schema, args["data"])
                # add title in case the add-on wants to reference its own title
                args["title"] = schema.get("title")
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
            print(f"Progress: {progress}%")
            return None
        assert 0 <= progress <= 100
        return self.client.patch(f"addon_runs/{self.id}/", json={"progress": progress})

    def set_message(self, message):
        """Set the progress message."""
        if not self.id:
            print(message)
            return None
        return self.client.patch(f"addon_runs/{self.id}/", json={"message": message})

    def upload_file(self, file):
        """Uploads a file to the addon run."""
        if not self.id:
            print(f"Uploading: {file.name}")
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
        # pylint: disable=W3101
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
            return None

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

        return 0

    def get_documents(self):
        """Get documents from either selected or queried documents"""
        if self.documents:
            documents = self.client.documents.list(id__in=self.documents)
        elif self.query:
            documents = self.client.documents.search(self.query)
        else:
            documents = []

        yield from documents

    def charge_credits(self, amount):
        """Charge the organization a certain amount of premium credits"""

        if not self.id:
            print(f"Charge credits: {amount}")
            return None
        elif not self.org_id:
            self.set_message("No organization to charge.")
            raise ValueError

        resp = self.client.post(
            f"organizations/{self.org_id}/ai_credits/",
            json={
                "ai_credits": amount,
                "addonrun_id": self.id,
                "note": f"AddOn run: {self.title} - {self.id}",
            },
        )
        if resp.status_code != 200:
            self.set_message("Error charging AI credits.")
            raise ValueError
        return resp


class CronAddOn(BaseAddOn):
    """DEPREACTED"""


class SoftTimeOutAddOn(AddOn):
    """
    An add-on which can automatically rerun itself on soft-timeout with the
    remaining documents
    """

    # default to a 5 minute soft timeout
    soft_time_limit = 300

    def __init__(self):
        super().__init__()
        # record starting time to track when the soft timeout is reached
        self._start = time.time()

        self._documents_iter = None
        self._current_document = None

    def rerun_addon(self, include_current=False):
        """Re-run the add on with the same parameters"""
        options = {}
        if self.documents:
            # If documents were passed in by ID, pass in the remaining documents by ID
            options["documents"] = [d.id for d in self._documents_iter]
            if include_current:
                options["documents"].insert(0, self._current_document.id)
        elif self.query:
            # If documents were passed in by query, get the id from the next
            # document, and add that in to the data under a reserved name, so
            # that the next run can filter out documents before that id
            if include_current:
                next_document = self._current_document
            else:
                next_document = next(self._documents_iter)
            self.data["_id_start"] = next_document.id
            options["query"] = self.query

        self.data["_restore_key"] = self.id
        self.client.post(
            "addon_runs/",
            json={
                "addon": self.addon_id,
                "parameters": self.data,
                **options,
            },
        )
        # dismiss the current add-on run from the dashboard
        self.client.patch(
            f"addon_runs/{self.id}/",
            json={"dismissed": True},
        )

    def get_documents(self):
        """Get documents from either selected or queried documents"""

        if self.documents:
            documents = self.client.documents.list(id__in=self.documents)
        elif self.query and "_id_start" in self.data:
            documents = self.client.documents.search(
                self.query, sort="id", id=f"[{self.data['_id_start']} TO *]"
            )
        elif self.query:
            documents = self.client.documents.search(self.query, sort="id")
        else:
            documents = []

        # turn documents into an iterator, so that documents that get yielded are
        # consumed and not re-used when we rerun
        self._documents_iter = iter(documents)
        for i, self._current_document in enumerate(self._documents_iter):
            yield self._current_document
            if self.soft_timeout():
                self.cleanup()
                self.rerun_addon()
                self.set_message(
                    f"Soft time out, processed {i+1} documents, "
                    "continuing rest of documents in a new run"
                )
                break

    def soft_timeout(self):
        """Check if enough time has elapsed for a soft timeout"""
        return time.time() - self._start > self.soft_time_limit

    def cleanup(self):
        """Hook to run code before automatic re-run"""
