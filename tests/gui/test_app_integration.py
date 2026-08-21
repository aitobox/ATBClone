from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
import toga

from atbclone.gui.app import ATBCloneApp, set_macos_dock_icon, set_macos_dock_visible


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


def test_set_macos_dock_visible_mac_and_fallback():
    with patch("atbclone.gui.app.sys.platform", "linux"):
        assert set_macos_dock_visible(True) is False
        assert set_macos_dock_visible(False) is False

    with patch("atbclone.gui.app.sys.platform", "darwin"), \
         patch("toga_cocoa.libs.appkit.NSApplication") as mock_app, \
         patch("atbclone.gui.app.set_macos_dock_icon") as mock_set_icon:
        mock_nsapp = MagicMock()
        mock_app.sharedApplication = mock_nsapp

        # Test hide dock icon (Accessory = 1)
        res_hide = set_macos_dock_visible(False)
        assert res_hide is True
        mock_nsapp.setActivationPolicy_.assert_called_with(1)

        # Test show dock icon (Regular = 0)
        res_show = set_macos_dock_visible(True)
        assert res_show is True
        mock_nsapp.setActivationPolicy_.assert_called_with(0)
        mock_set_icon.assert_called_once()


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

    with patch("atbclone.gui.app.set_macos_dock_visible") as mock_dock_vis:
        # show_main_window should restore dock icon
        app.show_main_window()
        assert app.main_window.visible
        mock_dock_vis.assert_called_with(True)

    with patch.object(app.tray_service, "disable") as mock_disable, \
         patch("atbclone.gui.app.set_macos_dock_visible") as mock_dock_vis, \
         patch.object(app, "exit") as mock_exit:
        app.exit_application()
        mock_disable.assert_called_once()
        mock_dock_vis.assert_called_with(True)
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

    # When tray is enabled, close handler should return False and hide dock icon
    with patch.object(app.tray_service, "_is_enabled", True), \
         patch("atbclone.gui.app.set_macos_dock_visible") as mock_dock_vis:
        res = app._on_window_close(app.main_window)
        assert res is False
        mock_dock_vis.assert_called_once_with(False)

    # When tray is disabled, close handler returns True and does not hide dock icon
    with patch.object(app.tray_service, "_is_enabled", False), \
         patch("atbclone.gui.app.set_macos_dock_visible") as mock_dock_vis:
        res = app._on_window_close(app.main_window)
        assert res is True
        mock_dock_vis.assert_not_called()


def test_app_window_hide_dock_visibility(tmp_path, monkeypatch):
    from atbclone.core import config
    from atbclone.core.config import set_config_value

    test_cfg_file = tmp_path / "config.yaml"
    monkeypatch.setattr(config, "DEFAULT_CONFIG_FILE", test_cfg_file)
    monkeypatch.setattr(config, "DEFAULT_ATB_DIR", tmp_path)
    set_config_value("minimize_to_tray", True)

    app = ATBCloneApp("ATBClone", "com.atbclone.app")
    app.startup()

    # When tray is enabled, hide handler hides dock icon
    with patch.object(app.tray_service, "_is_enabled", True), \
         patch("atbclone.gui.app.set_macos_dock_visible") as mock_dock_vis:
        app._on_window_hide(app.main_window)
        mock_dock_vis.assert_called_once_with(False)

    # When tray is disabled, hide handler does not alter dock icon
    with patch.object(app.tray_service, "_is_enabled", False), \
         patch("atbclone.gui.app.set_macos_dock_visible") as mock_dock_vis:
        app._on_window_hide(app.main_window)
        mock_dock_vis.assert_not_called()


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


def test_app_on_exit_hook():
    app = ATBCloneApp("ATBClone", "com.atbclone.app")
    app.startup()
    assert app.on_exit == app._on_app_exit

    with patch.object(app.tray_service, "disable") as mock_disable, \
         patch("atbclone.gui.app.set_macos_dock_visible") as mock_dock_vis:
        ret = app._on_app_exit(app)
        assert ret is True
        mock_disable.assert_called_once()
        mock_dock_vis.assert_called_with(True)


def test_main_entry_clean_exit():
    from atbclone.gui import main
    mock_app = MagicMock()
    with patch("atbclone.gui.build_app", return_value=mock_app), \
         patch("os._exit") as mock_os_exit:
        main()
        mock_app.main_loop.assert_called_once()
        mock_os_exit.assert_called_once_with(0)





