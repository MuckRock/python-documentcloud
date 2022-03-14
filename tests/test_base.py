# Future
from __future__ import division, print_function, unicode_literals

# Standard Library
from builtins import str

# Third Party
import pytest

# DocumentCloud
from documentcloud.documents import Document
from documentcloud.exceptions import DuplicateObjectError


class TestAPIResults:
    def test_str(self, client):
        results = client.documents.list()
        assert str(results)

    def test_getitem(self, client):
        results = client.documents.list()
        assert isinstance(results[0], Document)

    def test_getitem_paginate(self, client):
        results = client.documents.list(per_page=2)
        assert isinstance(results[3], Document)

    def test_getitem_index_error(self, client):
        # pylint: disable=pointless-statement
        results = client.documents.list()
        index = len(list(results)) + 1
        with pytest.raises(IndexError):
            results[index]

    def test_len(self, client):
        results = client.documents.list()
        assert len(results.results) > 0

    def test_iter(self, client):
        results = client.documents.list()
        for doc in results:
            assert isinstance(doc, Document)

    def test_next(self, client):
        results = client.documents.list(user=client.user_id, per_page=1)
        assert len(results.results) > 0
        while results.next is not None:
            results = results.next

    def test_previous(self, client):
        results = client.documents.list(user=client.user_id, per_page=1).next
        assert results.previous
        assert results.previous.previous is None


class TestAPISet:
    def test_init(self, project_factory, document):
        project = project_factory()
        document_list = project.document_list
        project.document_list = [document]
        project.document_list = document_list

    def test_init_bad_types(self, project):
        with pytest.raises(TypeError):
            project.document_list = [1, 2, 3]

    def test_init_dupes(self, project, document):
        with pytest.raises(DuplicateObjectError):
            project.document_list = [document, document]

    def test_append(self, project, document_factory):
        document = document_factory()
        project.document_list.append(document)
        assert project.document_list[-1] == document
        project.document_list.remove(document)

    def test_append_bad_type(self, project):
        with pytest.raises(TypeError):
            project.document_list.append(1)

    def test_append_dupes(self, project, document):
        with pytest.raises(DuplicateObjectError):
            project.document_list.append(document)

    def test_add(self, project, document_factory):
        document = document_factory()
        project.document_list.add(document)
        assert document in project.document_list
        project.document_list.remove(document)

    def test_add_bad_type(self, project):
        with pytest.raises(TypeError):
            project.document_list.add(1)

    def test_add_dupe(self, project, document):
        assert document in project.document_list
        length = len(project.document_list)
        project.document_list.add(document)
        assert document in project.document_list
        assert len(project.document_list) == length

    def test_extend(self, project, document_factory):
        document = document_factory()
        project.document_list.extend([document])
        assert document == project.document_list[-1]
        project.document_list.remove(document)

    def test_extend_bad_type(self, project):
        with pytest.raises(TypeError):
            project.document_list.extend([1])

    def test_extend_dupe(self, project, document):
        with pytest.raises(DuplicateObjectError):
            project.document_list.extend([document])
