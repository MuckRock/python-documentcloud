# Standard Library
from unittest.mock import MagicMock

# Third Party
import pytest

# DocumentCloud
from documentcloud.addon import AddOn

# pylint: disable=redefined-outer-name


@pytest.fixture
def addon():
    """An AddOn instance built without invoking argparse or constructing a real client.

    Tests can override `.id`, `.event_id`, `.client`, etc. as needed.
    """
    instance = AddOn.__new__(AddOn)
    instance.id = "run-123"
    instance.addon_id = "addon-1"
    instance.event_id = None
    instance.documents = None
    instance.query = None
    instance.user_id = None
    instance.org_id = None
    instance.data = {}
    instance.title = "Test AddOn"
    instance.client = MagicMock()
    return instance


class TestLoadRunData:
    def test_returns_data_when_run_id_set(self, addon):
        addon.client.get.return_value.json.return_value = {"data": {"foo": "bar"}}

        result = addon.load_run_data()

        addon.client.get.assert_called_once_with("addon_runs/run-123/")
        assert result == {"foo": "bar"}

    def test_returns_empty_dict_when_no_run_id(self, addon):
        addon.id = None

        assert addon.load_run_data() == {}
        addon.client.get.assert_not_called()

    def test_returns_empty_dict_when_data_missing_from_response(self, addon):
        addon.client.get.return_value.json.return_value = {}

        assert addon.load_run_data() == {}


class TestStoreRunData:
    def test_patches_run_with_data(self, addon):
        addon.store_run_data({"foo": "bar"})

        addon.client.patch.assert_called_once_with(
            "addon_runs/run-123/", json={"foo": "bar"}
        )

    def test_no_op_when_no_run_id(self, addon, capsys):
        addon.id = None

        result = addon.store_run_data({"foo": "bar"})

        assert result is None
        addon.client.patch.assert_not_called()
        assert "Run ID not set" in capsys.readouterr().out

    def test_rejects_non_dict_data(self, addon):
        with pytest.raises(TypeError):
            addon.store_run_data("not a dict")

        addon.client.patch.assert_not_called()


class TestLoadEventData:
    def test_returns_scratch_when_event_id_set(self, addon):
        addon.event_id = "evt-9"
        addon.client.get.return_value.json.return_value = {"scratch": {"x": 1}}

        result = addon.load_event_data()

        addon.client.get.assert_called_once_with("addon_events/evt-9/")
        assert result == {"x": 1}

    def test_returns_none_when_no_event_id(self, addon):
        assert addon.load_event_data() is None
        addon.client.get.assert_not_called()


class TestStoreEventData:
    def test_patches_event_with_scratch(self, addon):
        addon.event_id = "evt-9"

        addon.store_event_data({"x": 1})

        addon.client.patch.assert_called_once_with(
            "addon_events/evt-9/", json={"scratch": {"x": 1}}
        )

    def test_no_op_when_no_event_id(self, addon):
        assert addon.store_event_data({"x": 1}) is None
        addon.client.patch.assert_not_called()
