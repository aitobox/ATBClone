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


def test_sidebar_brand_header():
    import toga
    sidebar = SidebarNav(on_select=lambda k: None)
    header_box = sidebar.children[0]
    assert len(header_box.children) >= 1
    # Check that header contains both logo image (if available) and labels
    labels = [c for c in header_box.children if isinstance(c, toga.Label)]
    assert any("ATBClone" in l.text for l in labels) or any(
        isinstance(sub, toga.Box) and any("ATBClone" in l.text for l in sub.children if isinstance(l, toga.Label))
        for sub in header_box.children
    )


def test_sidebar_nav_retranslate():
    from atbclone.core.i18n import set_language
    set_language("en")
    sidebar = SidebarNav(on_select=lambda k: None)
    assert "Clones" in sidebar.buttons["clones"].text
    set_language("zh")
    sidebar.retranslate()
    assert "我的分身" in sidebar.buttons["clones"].text

