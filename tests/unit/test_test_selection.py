"""Offline API tests must not be skipped merely by their directory name."""

from unittest.mock import Mock
from tests.conftest import pytest_collection_modifyitems


def test_default_selection_only_skips_explicit_live_marker():
    offline = Mock(keywords={"integration": True})
    offline.get_closest_marker.return_value = None
    live = Mock(keywords={"integration": True})
    live.get_closest_marker.return_value = object()
    config = Mock()
    config.option.markexpr = ""
    pytest_collection_modifyitems(config, [offline, live])
    offline.add_marker.assert_not_called()
    live.add_marker.assert_called_once()
