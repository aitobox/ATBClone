"""ATBClone Main Application (BeeWare Toga) with Modern GUI Architecture."""

import asyncio
from typing import Any, Optional
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

from atbclone.gui.services.clone_service import CloneService
from atbclone.gui.services.doctor_service import DoctorService
from atbclone.gui.services.probe_service import ProbeService
from atbclone.gui.services.recipe_service import RecipeService
from atbclone.gui.components.sidebar import SidebarNav
from atbclone.gui.views.clone_list import CloneListView
from atbclone.gui.views.recipe_list import RecipeListView
from atbclone.gui.views.probe_view import ProbeView
from atbclone.gui.views.doctor_view import DoctorView
from atbclone.gui.views.logs_view import LogsView
from atbclone.gui.views.settings_view import SettingsView
from atbclone.gui.windows.wizard import WizardWindow
from atbclone.gui.theme import Theme


class ATBCloneApp(toga.App):
    """Main BeeWare Toga application entry point and view coordinator."""

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
        self.main_window.show()

        # Initial refresh
        self.safe_create_task(self.clone_view.refresh_clones())

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
