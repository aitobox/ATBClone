"""Comprehensive GUI i18n & dynamic translation tests."""

import toga
from unittest.mock import MagicMock, patch
from atbclone.core.i18n import set_language, get_language, t
from atbclone.gui.app import ATBCloneApp
from atbclone.gui.components.sidebar import SidebarNav
from atbclone.gui.components.top_bar import TopHeaderBar
from atbclone.gui.views.clone_list import CloneListView
from atbclone.gui.views.recipe_list import RecipeListView
from atbclone.gui.views.probe_view import ProbeView
from atbclone.gui.views.doctor_view import DoctorView
from atbclone.gui.views.logs_view import LogsView
from atbclone.gui.views.settings_view import SettingsView


def test_sidebar_nav_i18n_multi_language():
    for lang, expected_clones in [
        ("en", "Clones"),
        ("zh", "我的分身"),
        ("ja", "マイ クローン"),
        ("ko", "내 클론"),
        ("de", "Meine Klone"),
        ("fr", "Mes Clones"),
        ("ru", "Мои клоны"),
        ("es", "Mis Clones"),
    ]:
        set_language(lang)
        sidebar = SidebarNav(on_select=lambda k: None)
        assert expected_clones in sidebar.buttons["clones"].text
        assert len(sidebar.buttons["settings"].text) > 0


def test_top_header_bar_i18n():
    set_language("en")
    top_bar_en = TopHeaderBar(on_action=lambda w: None, on_refresh=lambda w: None)
    assert top_bar_en.btn_action.text == "+ New Clone"
    assert top_bar_en.btn_refresh.text == "🔄 Refresh"

    set_language("zh")
    top_bar_zh = TopHeaderBar(on_action=lambda w: None, on_refresh=lambda w: None)
    assert top_bar_zh.btn_action.text == "+ 新建分身"
    assert top_bar_zh.btn_refresh.text == "🔄 刷新"


def test_views_i18n_multi_language():
    for lang in ("en", "zh", "zh_TW", "ja", "ko", "de", "fr", "ru", "es"):
        set_language(lang)
        clone_v = CloneListView()
        assert clone_v.top_bar is not None
        assert clone_v.table is not None

        recipe_v = RecipeListView()
        assert recipe_v.top_bar is not None
        assert recipe_v.table is not None

        probe_v = ProbeView()
        assert probe_v.label_app_name is not None

        doctor_v = DoctorView()
        assert doctor_v.label_summary is not None

        logs_v = LogsView()
        assert logs_v.top_bar is not None

        settings_v = SettingsView()
        assert settings_v.select_language is not None
        assert settings_v.btn_release_notes is not None
        assert len(settings_v.btn_release_notes.text) > 0


def test_app_retranslate_ui(tmp_path, monkeypatch):
    from atbclone.core import config
    monkeypatch.setattr(config, "DEFAULT_CONFIG_FILE", tmp_path / "config.json")
    monkeypatch.setattr(config, "DEFAULT_ATB_DIR", tmp_path)

    app = ATBCloneApp(formal_name="ATBCloneTest", app_id="com.test.atbclone")
    # Mock window show and cocoa calls
    with patch("atbclone.gui.app.set_macos_dock_icon"), \
         patch("toga.MainWindow.show"):
        app.startup()

        # Default Chinese or system
        set_language("zh")
        app.retranslate_ui()
        assert "我的分身" in app.sidebar.buttons["clones"].text
        assert "更新日志" in app.settings_view.btn_release_notes.text

        # Switch to Japanese
        set_language("ja")
        app.retranslate_ui()
        assert "マイ クローン" in app.sidebar.buttons["clones"].text
        assert "リリースノート" in app.settings_view.btn_release_notes.text

        # Switch to English
        set_language("en")
        app.retranslate_ui()
        assert "Clones" in app.sidebar.buttons["clones"].text
        assert "Release Notes" in app.settings_view.btn_release_notes.text

