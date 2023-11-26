# Third Party
from listcrunch.listcrunch import uncrunch

# Local
from .base import BaseAPIObject, ChildAPIClient
from .toolbox import merge_dicts


class Annotation(BaseAPIObject):
    """A note on a document"""

    writable_fields = [
        "access",
        "content",
        "page_number",
        "title",
        "x1",
        "x2",
        "y1",
        "y2",
    ]

    def __str__(self):
        return self.title

    @property
    def api_path(self):
        return f"documents/{self.document.id}/notes"

    @property
    def location(self):
        page_spec = uncrunch(self.document.page_spec)
        width, height = page_spec[self.page_number].split("x")
        width, height = float(width), float(height)
        # normalize to a width of 700
        height = (700 / width) * height
        width = 700
        return Location(
            int(self.y1 * height),
            int(self.x2 * width),
            int(self.y2 * height),
            int(self.x1 * width),
        )

    @property
    def page(self):
        return self.page_number

    @property
    def description(self):
        return self.content


class Location(object):
    def __init__(self, top, right, bottom, left):
        self.top = top
        self.right = right
        self.bottom = bottom
        self.left = left


class AnnotationClient(ChildAPIClient):
    """Client for interacting with Sections"""

    resource = Annotation

    @property
    def api_path(self):
        return f"documents/{self.parent.id}/notes"

    def create(
        self,
        title,
        page_number,
        content="",
        access="private",
        x1=None,
        y1=None,
        x2=None,
        y2=None,
    ):
        coords = [x1, y2, x2, y2]
        if not (all(c is None for c in coords) or all(c is not None for c in coords)):
            raise ValueError(
                "x1, y2, x2, y2 must either all be None or all be not None"
            )
        if coords[0] is not None and not all(0 <= c <= 1.0 for c in coords):
            raise ValueError("x1, y2, x2, y2 must all be between 0.0 and 1.0")

        data = {
            "title": title,
            "page_number": page_number,
            "content": content,
            "access": access,
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2,
        }
        response = self.client.post(f"{self.api_path}/", json=data)
        return Annotation(
            self.client, merge_dicts(response.json(), {"document": self.parent})
        )
