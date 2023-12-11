# Future
from __future__ import division, print_function, unicode_literals

# Standard Library
from builtins import str
from datetime import datetime

# Third Party
import pytest

# DocumentCloud
from documentcloud.documents import Mention
from documentcloud.exceptions import APIError, DoesNotExistError
from documentcloud.organizations import Organization
from documentcloud.users import User

# pylint: disable=protected-access


class TestDocument:
    def test_str(self, document):
        assert str(document) == document.title

    def test_dates(self, document):
        for date_field in document.date_fields:
            assert isinstance(getattr(document, date_field), datetime)

    @pytest.mark.parametrize(
        "attr",
        [
            "full_text_url",
            "full_text",
            "thumbnail_image_url",
            "small_image",
            "normal_image_url_list",
            "large_image_url",
            "page_text",
            "json_text_url",
            "pdf",
        ],
    )
    def test_getattr(self, document, attr):
        assert getattr(document, attr)

    @pytest.mark.parametrize(
        "attr",
        [
            "get_full_text_url",
            "get_full_text",
            "get_thumbnail_image_url",
            "get_small_image",
            "get_normal_image_url_list",
            "get_large_image_url",
            "get_page_text",
            "get_json_text_url",
            "get_pdf",
        ],
    )
    def test_getattr_method(self, document, attr):
        assert getattr(document, attr)()

    @pytest.mark.parametrize(
        "attr",
        [
            "full_text_url",
            "get_full_text",
            "thumbnail_image_url",
            "get_small_image",
            "normal_image_url_list",
            "get_large_image_url",
        ],
    )
    def test_dir(self, document, attr):
        assert attr in dir(document)

    def test_mentions(self, client, document):
        document = client.documents.search(
            f"document:{document.id} text", mentions="true"
        )[0]
        assert document.mentions
        mention = document.mentions[0]
        assert mention.page
        assert "<em>text</em>" in mention.text

    def test_mentions_nosearch(self, document):
        assert not document.mentions

    def test_user(self, document):
        assert document._user is None
        assert isinstance(document.user, User)
        assert document.user == document._user

    def test_user_expanded(self, client, document):
        document = client.documents.get(document.id, expand=["user"])
        assert document._user is not None
        assert document._user == document.user

    def test_organization(self, document):
        assert document._organization is None
        assert isinstance(document.organization, Organization)
        assert document.organization == document._organization

    @pytest.mark.parametrize(
        "attr",
        [
            "id",
            "access",
            "asset_url",
            "canonical_url",
            "created_at",
            "data",
            "description",
            "edit_access",
            "language",
            "organization_id",
            "page_count",
            "page_spec",
            "projects",
            "related_article",
            "published_url",
            "slug",
            "source",
            "status",
            "title",
            "updated_at",
            "user_id",
            "pages",
            "contributor",
            "contributor_organization",
            "contributor_organization_slug",
        ],
    )
    def test_attrs(self, document, attr):
        assert getattr(document, attr)

    def test_save(self, client, document):
        assert document.source == "DocumentCloud"
        document.source = "MuckRock"
        document.save()
        document = client.documents.get(document.id)
        assert document.source == "MuckRock"

    def test_delete(self, client, document_factory):
        document = document_factory()
        document.delete()

        with pytest.raises(DoesNotExistError):
            client.documents.get(document.id)

    def test_section(self, document_factory):
        document = document_factory()
        assert len(document.sections.list().results) == 0
        section = document.sections.create("Test Section", 0)
        assert str(section) == "Test Section - p0"
        assert section.page == 0
        assert section == document.sections.list()[0]


class TestDocumentClient:
    def test_search(self, client, document):
        documents = client.documents.search(
            f"document:{document.id} simple"
        )
        assert documents

    def test_list(self, client):
        # list and all are aliases
        all_documents = client.documents.all()
        my_documents = client.documents.list(user=client.user_id)
        assert len(list(all_documents)) > len(list(my_documents.results))

    def test_upload_url(self, document_factory):
        document = document_factory()
        assert document.status == "success"

    def test_public_upload(self, public_client):
        with pytest.raises(APIError, match=r"403"):
            public_client.documents.upload("tests/test.pdf")

    def test_upload_file(self, document_factory):
        with open("tests/test.pdf", "rb") as pdf:
            document = document_factory(pdf)
        assert document.status == "success"


    def test_upload_file_path(self, document_factory):
        document = document_factory("tests/test.pdf")
        assert document.status == "success"

    def test_upload_big_file(self, client, mocker):
        mocker.patch("os.path.getsize", return_value=502 * 1024 * 1024)
        with pytest.raises(ValueError):
            client.documents.upload("tests/test.pdf")

    def test_upload_dir(self, client):
        documents = client.documents.upload_directory("tests/pdfs/")
        assert len(documents) == 2

    def test_format_upload_parameters(self, client):
        with pytest.warns(UserWarning):
            params = client.documents._format_upload_parameters(
                "tests/test.pdf", access="private", secure=True, project=2, foo="bar"
            )
        assert params == {"title": "test", "access": "private", "projects": [2]}

    def test_delete(self, document_factory, client):
        document = document_factory()
        client.documents.delete(document.id)

        with pytest.raises(DoesNotExistError):
            client.documents.get(document.id)


class TestMention:
    def test_mention(self):
        mention = Mention("page_no_42", "text")
        assert str(mention) == '42 - "text"'


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
