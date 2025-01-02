# Future
from __future__ import division, print_function, unicode_literals

# Standard Library
from builtins import str

# Third Party
import pytest

# DocumentCloud
from documentcloud.documents import Document
from documentcloud.exceptions import DoesNotExistError, MultipleObjectsReturnedError


class TestProject:
    def test_str(self, project):
        assert str(project) == project.title

    def test_save(self, client, project, document_factory):
        document = document_factory()
        assert document not in project.documents
        project.documents.append(document)
        # put is an alias for save
        project.put()
        project = client.projects.get(project.id)
        assert document in project.documents

    def test_document_list(self, project):
        assert len(project.document_list) > 0
        assert all(isinstance(d, Document) for d in project.document_list)

    def test_document_list_paginate(self, project):
        # pylint: disable=protected-access
        length = len(project.document_list)
        assert length > 1
        # clear cache
        project._document_list = None
        # set per page to 1 to force pagination
        project._per_page = 1
        assert len(project.document_list) == length

    def test_document_list_setter(self, project, document):
        assert document in project.document_list
        # setting to none clears it and sets to an empty list
        project.document_list = None
        assert document not in project.document_list
        # documents is an alias for document_list
        project.documents = [document]
        assert document in project.document_list
        with pytest.raises(TypeError):
            project.document_list = document

    def test_document_ids(self, project, document):
        assert document.id in project.document_ids

    def test_get_document(self, project, document):
        assert project.get_document(document.id)

    def test_get_document_missing(self, project, document_factory):
        document = document_factory()
        with pytest.raises(DoesNotExistError):
            project.get_document(document.id)


class TestProjectClient:
    def test_list(self, client):
        all_projects = client.projects.list()
        my_projects = client.projects.all()
        assert len(all_projects.results) > len(my_projects.results)
        assert len(client.projects.list(user=client.user_id).results) == len(
            my_projects.results
        )

    def test_get_id(self, client, project):
        assert client.projects.get(id=project.id)

    def test_get_title(self, client, project):
        assert client.projects.get(title=project.title)

    def test_get_nothing(self, client):
        with pytest.raises(ValueError):
            client.projects.get()

    def test_get_both(self, client, project):
        with pytest.raises(ValueError):
            client.projects.get(id=project.id, title=project.title)

    def test_get_by_id(self, client, project):
        assert client.projects.get_by_id(project.id)

    def test_get_by_title(self, client, project):
        assert client.projects.get_by_title(project.title)

    def test_get_by_title_multiple(self, client, project_factory):
        for _ in range(2):
            project_factory(title="Dupe")
        with pytest.raises(MultipleObjectsReturnedError):
            client.projects.get_by_title("Dupe")

    def test_get_or_create_by_title_get(self, client, project):
        title = project.title
        project, created = client.projects.get_or_create_by_title(title)
        assert project.title == title
        assert not created

    def test_get_or_create_by_title_create(self, client):
        title = "Created Title"
        project, created = client.projects.get_or_create_by_title(title)
        assert project.title == title
        project.delete()
        assert created
