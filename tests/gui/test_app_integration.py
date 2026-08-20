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

