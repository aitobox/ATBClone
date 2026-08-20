from unittest.mock import MagicMock
from atbclone.gui.components.sidebar import SidebarNav


def test_sidebar_nav_initialization_and_selection():
    on_select = MagicMock()
    sidebar = SidebarNav(on_select=on_select, active_key="clones")
    assert sidebar.active_key == "clones"

    # Select recipes
    sidebar.select_item("recipes")
    assert sidebar.active_key == "recipes"
    on_select.assert_called_with("recipes")

    # Select settings
    sidebar.select_item("settings")
    assert sidebar.active_key == "settings"
    on_select.assert_called_with("settings")
