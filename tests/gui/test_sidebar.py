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
    assert sidebar.promo_subtitle_label.text == "Dual-panel File Manager"
    assert "Visit Website" in sidebar.promo_btn.text

    set_language("zh")
    sidebar.retranslate()
    assert "我的分身" in sidebar.buttons["clones"].text
    assert sidebar.promo_subtitle_label.text == "双面板文件管理工具"
    assert "访问官网" in sidebar.promo_btn.text


def test_sidebar_promo_card_structure():
    sidebar = SidebarNav(on_select=lambda k: None)
    assert hasattr(sidebar, "promo_card")
    assert sidebar.promo_title_label.text == "ATBCmder"
    assert sidebar.promo_ad_badge.text == "[AD]"
    assert sidebar.promo_subtitle_label is not None
    assert sidebar.promo_btn is not None
    assert sidebar.promo_card in sidebar.children


def test_sidebar_promo_click_opens_url(monkeypatch):
    sidebar = SidebarNav(on_select=lambda k: None)
    mock_open = MagicMock()
    monkeypatch.setattr("webbrowser.open", mock_open)

    sidebar._on_open_cmder_url(sidebar.promo_btn)
    mock_open.assert_called_once_with("https://cmder.aitobox.com")


