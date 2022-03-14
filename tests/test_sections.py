# Future
from __future__ import division, print_function, unicode_literals

# Standard Library
from builtins import str

# Third Party
import pytest

# DocumentCloud
from documentcloud.exceptions import APIError


class TestSection:
    def test_create_delete(self, document_factory):
        document = document_factory()
        assert len(document.sections.list().results) == 0
        section = document.sections.create("Test Section", 0)
        assert len(document.sections.list().results) == 1

        # may not have two sections on the same page
        with pytest.raises(APIError):
            document.sections.create("Test Section 2", 0)

        section.delete()
        assert len(document.sections.list().results) == 0

    def test_str(self, document):
        assert str(document.sections[0])

    def test_page(self, document):
        assert document.sections[0].page == 0
