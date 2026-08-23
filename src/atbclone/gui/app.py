"""ATBClone Main Application (BeeWare Toga) with Modern GUI Architecture."""

import asyncio
import sys
from pathlib import Path
from typing import Any, Optional
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

from atbclone import __version__
from atbclone.core.config import get_config_value
from atbclone.core.logger import get_logger
from atbclone.core.resources import get_app_icon_path
from toga.constants import WindowState

logger = get_logger("gui.app")
from atbclone.gui.services.clone_service import CloneService
from atbclone.gui.services.doctor_service import DoctorService
from atbclone.gui.services.probe_service import ProbeService
from atbclone.gui.services.recipe_service import RecipeService
from atbclone.gui.services.tray_service import TrayService
from atbclone.gui.components.sidebar import SidebarNav
from atbclone.gui.views.clone_list import CloneListView
from atbclone.gui.views.recipe_list import RecipeListView
from atbclone.gui.views.probe_view import ProbeView
from atbclone.gui.views.doctor_view import DoctorView
from atbclone.gui.views.logs_view import LogsView
from atbclone.gui.views.settings_view import SettingsView
from atbclone.gui.windows.wizard import WizardWindow
from atbclone.gui.theme import Theme
from atbclone.gui.patch_cocoa import patch_cocoa_widgets


def set_macos_dock_icon(icon_path: Optional[Path] = None) -> bool:
    """Explicitly set application icon on macOS Dock via Cocoa AppKit."""
    if icon_path is None:
        icon_path = get_app_icon_path("png")
    if not icon_path or not icon_path.exists():
        return False
    try:
        from toga_cocoa.libs.appkit import NSApplication, NSImage
        ns_img = NSImage.alloc().initWithContentsOfFile_(str(icon_path))
        if ns_img:
            NSApplication.sharedApplication.setApplicationIconImage_(ns_img)
            return True
    except Exception:
        # Graceful fallback for non-macOS or headless test environments
        pass
    return False


def set_macos_dock_visible(visible: bool) -> bool:
    """Show or hide the application icon on macOS Dock via Cocoa AppKit activation policy.

    - visible=True: Sets NSApplicationActivationPolicyRegular (0) to show Dock icon and standard UI.
    - visible=False: Sets NSApplicationActivationPolicyAccessory (1) to hide Dock icon.
    """
    if sys.platform != "darwin":
        return False
    try:
        from toga_cocoa.libs.appkit import (
            NSApplication,
            NSApplicationActivationPolicyRegular,
            NSApplicationActivationPolicyAccessory,
        )
        if NSApplication is not None and hasattr(NSApplication, "sharedApplication"):
            ns_app = NSApplication.sharedApplication
            if hasattr(ns_app, "setActivationPolicy_"):
                policy = NSApplicationActivationPolicyRegular if visible else NSApplicationActivationPolicyAccessory
                ns_app.setActivationPolicy_(policy)
                if visible:
                    set_macos_dock_icon()
                return True
    except Exception as e:
        logger.debug(f"Failed setting macOS dock visibility to {visible}: {e}")
    return False


class ATBCloneApp(toga.App):
    """Main BeeWare Toga application entry point and view coordinator."""

    def __init__(
        self,
        formal_name: str = "ATBClone",
        app_id: str = "com.atbclone.app",
        app_name: str = "atbclone",
        version: Optional[str] = None,
        author: str = "Brain Zhang",
        description: str = "macOS App Cloning Engine",
        home_page: str = "https://github.com/aitobox/ATBClone",
        **kwargs,
    ):
        patch_cocoa_widgets()
        if "icon" not in kwargs or kwargs["icon"] is None:
            icon_path = get_app_icon_path("png")
            if icon_path:
                kwargs["icon"] = icon_path
        if version is None:
            version = __version__
        super().__init__(
            formal_name=formal_name,
            app_id=app_id,
            app_name=app_name,
            version=version,
            author=author,
            description=description,
            home_page=home_page,
            **kwargs,
        )


    def safe_create_task(self, coro):
        """Safely schedule a coroutine if an event loop is running."""
        try:
            loop = asyncio.get_running_loop()
            return loop.create_task(coro)
        except RuntimeError:
            if hasattr(self, "loop") and self.loop and self.loop.is_running():
                return self.loop.create_task(coro)
            coro.close()
            return None

    def startup(self):
        # Set macOS Dock icon immediately on app launch
        set_macos_dock_icon(get_app_icon_path("png"))

        # Initialize services
        self.clone_service = CloneService()
        self.recipe_service = RecipeService()
        self.probe_service = ProbeService()
        self.doctor_service = DoctorService()

        # Initialize all 6 views
        self.clone_view = CloneListView(clone_service=self.clone_service, app=self)
        self.recipe_view = RecipeListView(recipe_service=self.recipe_service, app=self)
        self.probe_view = ProbeView(probe_service=self.probe_service, recipe_service=self.recipe_service, app=self)
        self.doctor_view = DoctorView(doctor_service=self.doctor_service, app=self)
        self.logs_view = LogsView(app=self)
        self.settings_view = SettingsView(app=self)

        self.current_view_name = "clones"

        # Main window setup
        self.main_window = toga.MainWindow(
            title=self.formal_name,
            size=(1020, 680),
        )

        # Left Sidebar Navigation
        self.sidebar = SidebarNav(on_select=self.switch_view, active_key="clones")

        # Right-side dynamic view container
        self.content_container = toga.Box(style=Pack(direction=COLUMN, flex=1, background_color=Theme.BG_WINDOW))
        self.content_container.add(self.clone_view)

        # Root layout box
        self.root_box = toga.Box(style=Pack(direction=ROW, flex=1))
        self.root_box.add(self.sidebar)
        self.root_box.add(self.content_container)

        self.main_window.content = self.root_box
        self.main_window.on_hide = self._on_window_hide
        self.main_window.on_close = self._on_window_close
        self.on_exit = self._on_app_exit
        self.main_window.show()

        # Initialize native system tray service
        self.tray_service = TrayService(app=self)
        if bool(get_config_value("minimize_to_tray", False)):
            self.tray_service.enable()

        # Initial refresh
        self.safe_create_task(self.clone_view.refresh_clones())

    def _on_window_hide(self, window: Any) -> None:
        """Handle window minimize/hide event when tray mode is active."""
        if hasattr(self, "tray_service") and self.tray_service and self.tray_service.is_enabled:
            try:
                native_win = getattr(getattr(window, "_impl", None), "native", None)
                if native_win and hasattr(native_win, "orderOut_"):
                    native_win.orderOut_(None)
                set_macos_dock_visible(False)
            except Exception as e:
                logger.debug(f"Error hiding window to tray: {e}")

    def _on_window_close(self, window: Any) -> bool:
        """Handle window close event: hide to tray if minimize_to_tray is enabled, else allow exit."""
        if hasattr(self, "tray_service") and self.tray_service and self.tray_service.is_enabled:
            try:
                native_win = getattr(getattr(window, "_impl", None), "native", None)
                if native_win and hasattr(native_win, "orderOut_"):
                    native_win.orderOut_(None)
                set_macos_dock_visible(False)
                return False
            except Exception as e:
                logger.debug(f"Error intercepting window close for tray: {e}")
        return True

    def _on_app_exit(self, app: Any) -> bool:
        """Handle application exit event: teardown tray icon, restore dock, and allow shutdown."""
        logger.info("Application shutdown initiated via on_exit hook.")
        try:
            if hasattr(self, "tray_service") and self.tray_service:
                self.tray_service.disable()
            set_macos_dock_visible(True)
        except Exception as e:
            logger.warning(f"Error during on_app_exit cleanup: {e}")
        return True

    def show_main_window(self) -> None:
        """Bring main window to front and activate application from tray or background."""
        try:
            if not hasattr(self, "main_window") or not self.main_window:
                return

            # 0. Ensure Dock icon is visible when restoring main window
            set_macos_dock_visible(True)

            # 1. Cocoa native unhide and activate application
            if sys.platform == "darwin":
                try:
                    from toga_cocoa.libs.appkit import NSApplication
                    if NSApplication is not None and hasattr(NSApplication, "sharedApplication"):
                        ns_app = NSApplication.sharedApplication
                        if hasattr(ns_app, "unhide_"):
                            ns_app.unhide_(None)
                        if hasattr(ns_app, "activateIgnoringOtherApps_"):
                            ns_app.activateIgnoringOtherApps_(True)
                        elif hasattr(ns_app, "activate"):
                            ns_app.activate()
                except Exception as e:
                    logger.debug(f"Failed activating NSApplication: {e}")

            # 2. Reset any pending state transition in Toga
            impl = getattr(self.main_window, "_impl", None)
            if impl and hasattr(impl, "_pending_state_transition"):
                impl._pending_state_transition = None

            # 3. Cocoa native deminiaturize & bring window to front
            if sys.platform == "darwin" and impl:
                native_win = getattr(impl, "native", None)
                if native_win is not None:
                    try:
                        if getattr(native_win, "isMiniaturized", False):
                            if hasattr(native_win, "deminiaturize_"):
                                native_win.deminiaturize_(None)
                        if hasattr(native_win, "setIsVisible_"):
                            native_win.setIsVisible_(True)
                        if hasattr(native_win, "makeKeyAndOrderFront_"):
                            native_win.makeKeyAndOrderFront_(None)
                        if hasattr(native_win, "orderFrontRegardless"):
                            native_win.orderFrontRegardless()
                        if hasattr(native_win, "makeMainWindow"):
                            native_win.makeMainWindow()
                        if hasattr(native_win, "makeKeyWindow"):
                            native_win.makeKeyWindow()
                    except Exception as e:
                        logger.debug(f"Failed native window restore: {e}")

            # 4. Toga window state synchronization
            try:
                if self.main_window.state != WindowState.NORMAL:
                    if impl and hasattr(impl, "_apply_state"):
                        impl._apply_state(WindowState.NORMAL)
            except Exception:
                pass

            # 5. Toga show fallback if still not visible
            try:
                if not self.main_window.visible:
                    self.main_window.show()
            except Exception:
                pass

            # 6. Re-activate app again to ensure key window focus
            if sys.platform == "darwin":
                try:
                    from toga_cocoa.libs.appkit import NSApplication
                    if NSApplication is not None and hasattr(NSApplication, "sharedApplication"):
                        ns_app = NSApplication.sharedApplication
                        if hasattr(ns_app, "activateIgnoringOtherApps_"):
                            ns_app.activateIgnoringOtherApps_(True)
                except Exception:
                    pass

        except Exception as e:
            logger.warning(f"Error restoring main window: {e}")

    def exit_application(self) -> None:
        """Cleanly terminate the application and remove status tray icon."""
        if hasattr(self, "tray_service") and self.tray_service:
            self.tray_service.disable()
        set_macos_dock_visible(True)
        self.exit()

    def switch_view(self, view_name: str):
        """Switch right content area between feature views."""
        self.current_view_name = view_name

        # Clear content container
        while len(self.content_container.children) > 0:
            self.content_container.remove(self.content_container.children[0])

        if view_name == "clones":
            self.content_container.add(self.clone_view)
            self.safe_create_task(self.clone_view.refresh_clones())
        elif view_name == "recipes":
            self.content_container.add(self.recipe_view)
            self.safe_create_task(self.recipe_view.refresh_recipes())
        elif view_name == "probe":
            self.content_container.add(self.probe_view)
        elif view_name == "doctor":
            self.content_container.add(self.doctor_view)
            self.safe_create_task(self.doctor_view.run_checks())
        elif view_name == "logs":
            self.content_container.add(self.logs_view)
            self.logs_view.reload_from_disk()
        elif view_name == "settings":
            self.content_container.add(self.settings_view)

    def action_new_clone(self, widget: Any):
        async def _on_complete():
            await self.clone_view.refresh_clones()
            self.logs_view.log_info(f"Cloning wizard finished successfully.")

        wizard = WizardWindow(
            clone_service=self.clone_service,
            probe_service=self.probe_service,
            on_complete=_on_complete,
        )
        wizard.show()

    def action_refresh_current(self, widget: Any):
        if self.current_view_name == "clones":
            self.safe_create_task(self.clone_view.refresh_clones())
        elif self.current_view_name == "recipes":
            self.safe_create_task(self.recipe_view.refresh_recipes())
        elif self.current_view_name == "doctor":
            self.safe_create_task(self.doctor_view.run_checks())

    def retranslate_ui(self):
        """Dynamically refresh all UI components and views after language change."""
        if hasattr(self, "sidebar") and self.sidebar:
            self.sidebar.retranslate()

        if hasattr(self, "tray_service") and self.tray_service:
            self.tray_service.retranslate()

        # Re-initialize views with updated localized strings
        self.clone_view = CloneListView(clone_service=self.clone_service, app=self)
        self.recipe_view = RecipeListView(recipe_service=self.recipe_service, app=self)
        self.probe_view = ProbeView(probe_service=self.probe_service, recipe_service=self.recipe_service, app=self)
        self.doctor_view = DoctorView(doctor_service=self.doctor_service, app=self)
        self.logs_view = LogsView(app=self)
        self.settings_view = SettingsView(app=self)

        # Re-mount currently active view
        self.switch_view(self.current_view_name)

