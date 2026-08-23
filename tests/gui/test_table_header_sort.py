"""Tests for Cocoa Table header sorting patch."""

import pytest
import toga
from unittest.mock import MagicMock
from atbclone.gui.patch_cocoa import patch_cocoa_widgets, configure_cocoa_table


def test_table_header_sort_generic():
    """Verify generic Table sorts data on header click."""
    patch_cocoa_widgets()
    table = toga.Table(columns=["Name", "Age"])
    table.data = [
        ("Charlie", 30),
        ("Alice", 25),
        ("Bob", 20),
    ]

    impl = table._impl
    native_table = impl.native_table
    assert hasattr(native_table, "tableView_didClickTableColumn_")

    col_name = native_table.tableColumns[0]
    # First click: sort ascending by Name
    native_table.tableView_didClickTableColumn_(native_table, col_name)
    assert [r.name for r in table.data] == ["Alice", "Bob", "Charlie"]

    # Second click: sort descending by Name
    native_table.tableView_didClickTableColumn_(native_table, col_name)
    assert [r.name for r in table.data] == ["Charlie", "Bob", "Alice"]

    # Click age column: sort ascending by Age
    col_age = native_table.tableColumns[1]
    native_table.tableView_didClickTableColumn_(native_table, col_age)
    assert [r.age for r in table.data] == [20, 25, 30]

    # Click age column again: sort descending by Age
    native_table.tableView_didClickTableColumn_(native_table, col_age)
    assert [r.age for r in table.data] == [30, 25, 20]


def test_table_custom_header_sort_callback():
    """Verify custom on_header_sort callback is called if defined on table."""
    patch_cocoa_widgets()
    table = toga.Table(columns=["Title", "Count"])
    table.data = [("A", 1), ("B", 2)]

    mock_cb = MagicMock()
    table.on_header_sort = mock_cb

    native_table = table._impl.native_table
    col = native_table.tableColumns[0]
    native_table.tableView_didClickTableColumn_(native_table, col)

    mock_cb.assert_called_once()
    args, kwargs = mock_cb.call_args
    assert args[0] == 0  # col index
    assert args[2] is True  # ascending

    # Click again: ascending should be False
    mock_cb.reset_mock()
    native_table.tableView_didClickTableColumn_(native_table, col)
    mock_cb.assert_called_once()
    args, kwargs = mock_cb.call_args
    assert args[0] == 0
    assert args[2] is False


def test_table_header_sort_mixed_types_and_none():
    """Verify generic sorting handles None values and mixed strings safely."""
    patch_cocoa_widgets()
    table = toga.Table(columns=["Val"])
    table.data = [
        ("beta",),
        (None,),
        ("Alpha",),
        ("gamma",),
    ]

    native_table = table._impl.native_table
    col = native_table.tableColumns[0]
    native_table.tableView_didClickTableColumn_(native_table, col)

    # Ascending sort: strings case-insensitive, None handled gracefully
    vals = [r.val for r in table.data]
    assert vals == ["Alpha", "beta", "gamma", None] or vals == [None, "Alpha", "beta", "gamma"]
