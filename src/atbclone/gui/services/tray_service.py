"""macOS Cocoa native menu bar status item (tray) service for ATBClone."""

import sys
from pathlib import Path
from typing import Any, Optional

from atbclone.core.i18n import t
from atbclone.core.logger import get_logger
from atbclone.core.resources import get_app_icon_path

logger = get_logger("gui.tray")

try:
    from toga_cocoa.libs.appkit import (
        NSApplication,
        NSStatusBar,
        NSMenu,
        NSMenuItem,
        NSImage,
    )
    from rubicon.objc import NSObject, objc_method, NSSize, SEL
except Exception:
    NSApplication = None
    NSStatusBar = None
    NSMenu = None
    NSMenuItem = None
    NSImage = None
    NSObject = object
    objc_method = lambda fn: fn
    NSSize = None
    SEL = lambda name: name


class TrayCallbackTarget(NSObject):
    """Objective-C target object to receive Cocoa NSStatusBarButton click events."""

    @objc_method
    def onTrayClicked_(self, sender) -> None:
        if hasattr(self, "_tray_service") and self._tray_service:
            self._tray_service._handle_click(sender)

    @objc_method
    def onMenuShow_(self, sender) -> None:
        if hasattr(self, "_tray_service") and self._tray_service:
            self._tray_service.on_menu_show()

    @objc_method
    def onMenuQuit_(self, sender) -> None:
        if hasattr(self, "_tray_service") and self._tray_service:
            self._tray_service.on_menu_quit()


class TrayService:
    """Manages the lifecycle, appearance, and event dispatch of the macOS status tray icon."""

    def __init__(self, app: Any):
        self.app = app
        self._status_item: Any = None
        self._target: Any = None
        self._is_enabled: bool = False

    @property
    def is_enabled(self) -> bool:
        return self._is_enabled

    def enable(self) -> bool:
        if self._is_enabled or sys.platform != "darwin" or NSStatusBar is None:
            return False
        try:
            # -2 represents NSSquareStatusItemLength; -1 represents NSVariableStatusItemLength
            self._status_item = NSStatusBar.systemStatusBar.statusItemWithLength_(-2)
            button = getattr(self._status_item, "button", None)
            if button is not None:
                icon_path = get_app_icon_path("png")
                if icon_path and Path(icon_path).exists() and NSImage is not None:
                    try:
                        img = NSImage.alloc().initWithContentsOfFile_(str(icon_path))
                        if img:
                            if NSSize is not None:
                                img.setSize_(NSSize(18, 18))
                            if hasattr(button, "setImage_"):
                                button.setImage_(img)
                    except Exception as e:
                        logger.debug(f"Could not set tray icon image: {e}")

                if hasattr(button, "setToolTip_"):
                    button.setToolTip_("ATBClone")

                if NSObject is not object and hasattr(TrayCallbackTarget, "alloc"):
                    self._target = TrayCallbackTarget.alloc().init()
                    self._target._tray_service = self

                    if hasattr(button, "setTarget_"):
                        button.setTarget_(self._target)
                    if hasattr(button, "setAction_"):
                        button.setAction_(SEL("onTrayClicked:"))
                    # NSEventMaskLeftMouseUp = 1 << 2, NSEventMaskRightMouseDown = 1 << 3, NSEventMaskRightMouseUp = 1 << 4
                    if hasattr(button, "sendActionOn_"):
                        button.sendActionOn_((1 << 2) | (1 << 3) | (1 << 4))

            self._is_enabled = True
            logger.info("System tray icon enabled successfully.")
            return True
        except Exception as e:
            logger.warning(f"Failed to enable system tray icon: {e}")
            self._status_item = None
            self._is_enabled = False
            return False

    def disable(self) -> None:
        if not self._is_enabled or self._status_item is None:
            self._is_enabled = False
            return
        try:
            if NSStatusBar is not None and hasattr(NSStatusBar, "systemStatusBar"):
                NSStatusBar.systemStatusBar.removeStatusItem_(self._status_item)
        except Exception as e:
            logger.warning(f"Error removing status item: {e}")
        self._status_item = None
        self._target = None
        self._is_enabled = False
        logger.info("System tray icon disabled.")

    def _handle_click(self, sender: Any) -> None:
        """Handle left vs right mouse button click events."""
        try:
            current_event = getattr(NSApplication.sharedApplication, "currentEvent", None) if NSApplication else None
            event_type = getattr(current_event, "type", None)
            # NSEventTypeRightMouseDown = 3, NSEventTypeRightMouseUp = 4
            if event_type in (3, 4):
                self.show_context_menu()
            else:
                self.on_menu_show()
        except Exception as e:
            logger.debug(f"Error determining click event type: {e}")
            self.on_menu_show()

    def show_context_menu(self) -> None:
        """Build and popup the context NSMenu for right-click."""
        if not self._status_item or NSMenu is None or NSMenuItem is None:
            return
        try:
            menu = NSMenu.alloc().init()
            if hasattr(menu, "setAutoenablesItems_"):
                menu.setAutoenablesItems_(True)

            item_show = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                t("tray_menu_show"),
                SEL("onMenuShow:"),
                "",
            )
            if self._target and hasattr(item_show, "setTarget_"):
                item_show.setTarget_(self._target)
            menu.addItem_(item_show)

            if hasattr(NSMenuItem, "separatorItem"):
                sep = NSMenuItem.separatorItem()
                menu.addItem_(sep)

            item_quit = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                t("tray_menu_quit"),
                SEL("onMenuQuit:"),
                "",
            )
            if self._target and hasattr(item_quit, "setTarget_"):
                item_quit.setTarget_(self._target)
            menu.addItem_(item_quit)

            if hasattr(self._status_item, "popUpStatusItemMenu_"):
                self._status_item.popUpStatusItemMenu_(menu)
        except Exception as e:
            logger.warning(f"Failed to popup context menu: {e}")

    def on_menu_show(self) -> None:
        if self.app and hasattr(self.app, "show_main_window"):
            self.app.show_main_window()

    def on_menu_quit(self) -> None:
        if self.app and hasattr(self.app, "exit_application"):
            self.app.exit_application()

    def retranslate(self) -> None:
        """Context menu is dynamically generated with localized strings on popup."""
        pass
