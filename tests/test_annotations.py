# Future
from __future__ import division, print_function, unicode_literals

# Standard Library
from builtins import str

# Third Party
import pytest

# DocumentCloud
from documentcloud.annotations import Annotation


class TestAnnotation:
    def test_create_delete(self, document):
        assert len(document.notes.list().results) == 1
        note = document.notes.create(
            "Test Note", 0, "<p>Note content!</p>", x1=0.1, y1=0.1, x2=0.2, y2=0.2
        )
        assert len(document.notes.list().results) == 2
        for note in document.notes:
            assert isinstance(note, Annotation)
        note.delete()
        assert len(document.notes.list().results) == 1

    def test_create_page_note(self, document):
        note = document.notes.create("Test Note", 0, "<p>Page note!</p>")
        assert note
        note.delete()

    def test_create_partial_coords(self, document):
        with pytest.raises(ValueError):
            document.notes.create("Test Note", 0, "<p>Page note!</p>", x1=0.5)

    def test_create_invalid_coords(self, document):
        with pytest.raises(ValueError):
            document.notes.create(
                "Test Note", 0, "<p>Page note!</p>", x1=0.5, y1=1.5, x2=2, y2=3
            )

    def test_str(self, document):
        assert str(document.notes[0])

    def test_alias(self, document):
        assert document.notes is document.annotations

    def test_location(self, document):
        note = document.notes[0]
        assert note.location.top < note.location.bottom
        assert note.location.left < note.location.right
