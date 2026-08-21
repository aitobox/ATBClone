"""Unit tests for native macOS TrayService and event handling."""

import sys
from unittest.mock import MagicMock, patch
import pytest

from atbclone.gui.services.tray_service import TrayService


class DummyApp:
    def __init__(self):
        self.shown = False
        self.exited = False

    def show_main_window(self):
        self.shown = True

    def exit_application(self):
        self.exited = True


def test_tray_service_init_disabled():
    app = DummyApp()
    service = TrayService(app=app)
    assert not service.is_enabled
    assert service.app is app


def test_tray_service_enable_and_disable():
    app = DummyApp()
    service = TrayService(app=app)
    with patch("atbclone.gui.services.tray_service.NSStatusBar") as mock_sb:
        mock_item = MagicMock()
        mock_button = MagicMock()
        mock_item.button = mock_button
        mock_sb.systemStatusBar.statusItemWithLength_.return_value = mock_item
        with patch("atbclone.gui.services.tray_service.sys.platform", "darwin"):
            success = service.enable()
            assert success is True
            assert service.is_enabled is True
            mock_button.setToolTip_.assert_called_with("ATBClone")

            # Disabling should clean up
            service.disable()
            assert service.is_enabled is False
            mock_button.setTarget_.assert_called_with(None)
            mock_button.setAction_.assert_called_with(None)
            mock_sb.systemStatusBar.removeStatusItem_.assert_called_once_with(mock_item)


def test_tray_service_fallback_on_non_macos():
    app = DummyApp()
    service = TrayService(app=app)
    with patch("atbclone.gui.services.tray_service.sys.platform", "linux"):
        success = service.enable()
        assert success is False
        assert service.is_enabled is False


def test_tray_service_left_click_shows_window():
    app = DummyApp()
    service = TrayService(app=app)
    with patch("atbclone.gui.services.tray_service.NSApplication") as mock_nsapp:
        mock_event = MagicMock()
        mock_event.type = 2  # LeftMouseUp
        mock_event.modifierFlags = 0
        mock_nsapp.sharedApplication.currentEvent.return_value = mock_event

        service._handle_click(None)
        assert app.shown is True


def test_tray_service_ctrl_left_click_shows_menu():
    app = DummyApp()
    service = TrayService(app=app)
    service._status_item = MagicMock()
    with patch("atbclone.gui.services.tray_service.NSApplication") as mock_nsapp, \
         patch("atbclone.gui.services.tray_service.NSMenu") as mock_menu_cls, \
         patch("atbclone.gui.services.tray_service.NSMenuItem") as mock_menu_item_cls:
        
        mock_event = MagicMock()
        mock_event.type = 1  # LeftMouseDown with Ctrl modifier
        mock_event.modifierFlags = 0x40000  # NSEventModifierFlagControl
        mock_nsapp.sharedApplication.currentEvent.return_value = mock_event

        mock_menu = MagicMock()
        mock_menu_cls.alloc.return_value.init.return_value = mock_menu

        service._handle_click(None)
        service._status_item.popUpStatusItemMenu_.assert_called_once_with(mock_menu)


def test_tray_service_right_click_shows_menu():
    app = DummyApp()
    service = TrayService(app=app)
    service._status_item = MagicMock()
    with patch("atbclone.gui.services.tray_service.NSApplication") as mock_nsapp, \
         patch("atbclone.gui.services.tray_service.NSMenu") as mock_menu_cls, \
         patch("atbclone.gui.services.tray_service.NSMenuItem") as mock_menu_item_cls:
        
        mock_event = MagicMock()
        mock_event.type = 3  # NSEventTypeRightMouseDown
        mock_event.modifierFlags = 0
        mock_nsapp.sharedApplication.currentEvent.return_value = mock_event

        mock_menu = MagicMock()
        mock_menu_cls.alloc.return_value.init.return_value = mock_menu

        service._handle_click(None)
        service._status_item.popUpStatusItemMenu_.assert_called_once_with(mock_menu)


def test_tray_service_menu_callbacks():
    app = DummyApp()
    service = TrayService(app=app)
    service.on_menu_show()
    assert app.shown is True

    service.on_menu_quit()
    assert app.exited is True


def test_tray_callback_target():
    from atbclone.gui.services.tray_service import TrayCallbackTarget
    app = DummyApp()
    service = TrayService(app=app)
    target = TrayCallbackTarget.alloc().init() if hasattr(TrayCallbackTarget, "alloc") else TrayCallbackTarget()
    target._tray_service = service

    with patch.object(service, "_handle_click") as mock_handle:
        target.onTrayClicked_(None)
        mock_handle.assert_called_once()

    target.onMenuShow_(None)
    assert app.shown is True

    target.onMenuQuit_(None)
    assert app.exited is True


def test_tray_service_retranslate():
    app = DummyApp()
    service = TrayService(app=app)
    # Shouldn't raise any exceptions
    service.retranslate()

