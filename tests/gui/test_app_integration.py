from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
import toga

from atbclone.gui.app import ATBCloneApp, set_macos_dock_icon


def test_app_creation_and_routing():
    app = ATBCloneApp("ATBClone", "com.atbclone.app")
    app.startup()

    assert app.main_window is not None
    assert app.clone_view is not None
    assert app.recipe_view is not None
    assert app.probe_view is not None
    assert app.doctor_view is not None

    # Test route switching
    app.switch_view("recipes")
    assert app.current_view_name == "recipes"

    app.switch_view("probe")
    assert app.current_view_name == "probe"

    app.switch_view("doctor")
    assert app.current_view_name == "doctor"

    app.switch_view("logs")
    assert app.current_view_name == "logs"

    app.switch_view("settings")
    assert app.current_view_name == "settings"

    app.switch_view("clones")
    assert app.current_view_name == "clones"


def test_set_macos_dock_icon_safe():
    res = set_macos_dock_icon(None)
    assert isinstance(res, bool)


def test_set_macos_dock_icon_with_mock():
    with patch("toga_cocoa.libs.appkit.NSApplication") as mock_app, \
         patch("toga_cocoa.libs.appkit.NSImage") as mock_img:
        mock_ns_img = MagicMock()
        mock_img.alloc.return_value.initWithContentsOfFile_.return_value = mock_ns_img

        test_path = Path("resource/images/logo.png").resolve()
        success = set_macos_dock_icon(test_path)
        assert success is True
        mock_app.sharedApplication.setApplicationIconImage_.assert_called_once_with(mock_ns_img)


def test_build_app_has_icon():
    from atbclone.gui import build_app
    app = build_app()
    assert app.icon is not None


def test_app_tray_service_initialized_and_enabled(tmp_path, monkeypatch):
    from atbclone.core import config
    from atbclone.core.config import set_config_value

    test_cfg_file = tmp_path / "config.yaml"
    monkeypatch.setattr(config, "DEFAULT_CONFIG_FILE", test_cfg_file)
    monkeypatch.setattr(config, "DEFAULT_ATB_DIR", tmp_path)

    set_config_value("minimize_to_tray", True)
    with patch("atbclone.gui.services.tray_service.TrayService.enable") as mock_enable:
        app = ATBCloneApp("ATBClone", "com.atbclone.app")
        app.startup()
        assert hasattr(app, "tray_service")
        assert app.tray_service is not None
        mock_enable.assert_called_once()


def test_app_show_main_window_and_exit():
    app = ATBCloneApp("ATBClone", "com.atbclone.app")
    app.startup()

    # show_main_window should not raise
    app.show_main_window()
    assert app.main_window.visible

    with patch.object(app.tray_service, "disable") as mock_disable, \
         patch.object(app, "exit") as mock_exit:
        app.exit_application()
        mock_disable.assert_called_once()
        mock_exit.assert_called_once()


def test_app_window_close_and_hide_with_tray(tmp_path, monkeypatch):
    from atbclone.core import config
    from atbclone.core.config import set_config_value

    test_cfg_file = tmp_path / "config.yaml"
    monkeypatch.setattr(config, "DEFAULT_CONFIG_FILE", test_cfg_file)
    monkeypatch.setattr(config, "DEFAULT_ATB_DIR", tmp_path)
    set_config_value("minimize_to_tray", True)

    app = ATBCloneApp("ATBClone", "com.atbclone.app")
    app.startup()

    # When tray is enabled, close handler should return False to keep app alive
    with patch.object(app.tray_service, "_is_enabled", True):
        res = app._on_window_close(app.main_window)
        assert res is False

    # When tray is disabled, close handler returns True
    with patch.object(app.tray_service, "_is_enabled", False):
        res = app._on_window_close(app.main_window)
        assert res is True


def test_app_show_main_window_restores_from_hidden_or_minimized():
    from toga.constants import WindowState
    app = ATBCloneApp("ATBClone", "com.atbclone.app")
    app.startup()

    # Simulate hidden window
    native = getattr(getattr(app.main_window, "_impl", None), "native", None)
    if native and hasattr(native, "orderOut_"):
        native.orderOut_(None)

    app.show_main_window()
    assert app.main_window.visible


def test_app_retranslate_ui_updates_tray():
    app = ATBCloneApp("ATBClone", "com.atbclone.app")
    app.startup()
    with patch.object(app.tray_service, "retranslate") as mock_retrans:
        app.retranslate_ui()
        mock_retrans.assert_called_once()



