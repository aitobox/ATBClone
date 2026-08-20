"""7-Step Interactive Cloning Wizard Window."""

import asyncio
from pathlib import Path
from typing import Callable, Coroutine, Any
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

from atbclone.core.app_inspector import AppInspector
from atbclone.core.clone_task import CloneTask
from atbclone.core.config import DEFAULT_APPS_DIR, DEFAULT_DATA_DIR
from atbclone.core.models import AppInfo
from atbclone.gui.services.clone_service import CloneService
from atbclone.gui.services.probe_service import ProbeService
from atbclone.recipes.loader import RecipeLoader
from atbclone.recipes.models import Recipe, ProxyConfig, supports_data_dir


class WizardWindow(toga.Window):
    TOTAL_STEPS = 7

    def __init__(
        self,
        clone_service: CloneService | None = None,
        probe_service: ProbeService | None = None,
        on_complete: Callable[[], Coroutine[Any, Any, None]] | None = None,
    ):
        super().__init__(title="Clone App Wizard", size=(560, 520))
        self.clone_service = clone_service or CloneService()
        self.probe_service = probe_service or ProbeService()
        self.on_complete_callback = on_complete

        self.current_step = 1
        self.app_info: AppInfo | None = None
        self.recipe: Recipe | None = None

        # Step indicator label
        self.label_step_header = toga.Label(
            "Step 1 of 7: Select Source Application",
            style=Pack(font_size=15, font_weight="bold", margin_bottom=10),
        )

        # Dynamic container for step forms
        self.step_container = toga.Box(style=Pack(direction=COLUMN, flex=1, margin=10))

        # Bottom navigation buttons
        self.btn_prev = toga.Button("◀ Back", on_press=lambda w: asyncio.create_task(self.go_prev()), enabled=False, style=Pack(margin=5))
        self.btn_next = toga.Button("Next ▶", on_press=lambda w: asyncio.create_task(self.go_next()), style=Pack(margin=5))
        self.btn_cancel = toga.Button("Cancel", on_press=lambda w: self.close(), style=Pack(margin=5))

        # Initialize UI elements for all 7 steps
        self._init_step_widgets()

        # Build window layout
        self.content = self._build_layout()
        self._render_current_step()

    def _init_step_widgets(self):
        # Step 1: Select App
        self.input_app_path = toga.TextInput(placeholder="/Applications/Example.app", style=Pack(flex=1))
        self.btn_browse_app = toga.Button("📂 Browse...", on_press=self._on_browse_app, style=Pack(margin_left=5))

        # Step 2: Recipe Info
        self.label_recipe_app = toga.Label("App: —", style=Pack(margin=4))
        self.label_recipe_bundle = toga.Label("Bundle ID: —", style=Pack(margin=4))
        self.label_recipe_strat = toga.Label("Strategy: —", style=Pack(margin=4))
        self.select_recipe_strat = toga.Selection(items=["hard_clone", "soft_clone"], style=Pack(margin=4, width=150))
        # Shows whether recipe came from built-in library or Probe analysis
        self.label_recipe_origin = toga.Label("", style=Pack(margin=4, font_style="italic"))

        # Step 3: Naming
        self._display_name_customized = False
        self._syncing_name = False
        self.input_clone_name = toga.TextInput(
            placeholder="e.g. WeChat2",
            on_change=self._on_clone_name_change,
            style=Pack(flex=1),
        )
        self.input_display_name = toga.TextInput(
            placeholder="Display name in Dock/Finder",
            on_change=self._on_display_name_change,
            style=Pack(flex=1),
        )

        # Step 4: Destination Directory
        self.input_dest_dir = toga.TextInput(value=str(DEFAULT_APPS_DIR), style=Pack(flex=1))
        self.btn_browse_dest = toga.Button("📂 Browse...", on_press=self._on_browse_dest, style=Pack(margin_left=5))

        # Step 5: Data Directory
        self.label_data_dir_support = toga.Label("Data Directory Isolation Supported", style=Pack(margin=4))
        self.input_data_dir = toga.TextInput(style=Pack(flex=1))
        self.btn_browse_data = toga.Button("📂 Browse...", on_press=self._on_browse_data, style=Pack(margin_left=5))

        # Step 6: Proxy Settings
        self.switch_proxy = toga.Switch("Enable Dedicated Proxy", value=False, style=Pack(margin=5))
        self.select_proxy_type = toga.Selection(items=["http", "socks5"], style=Pack(width=100))
        self.input_proxy_host = toga.TextInput(value="127.0.0.1", style=Pack(flex=1))
        self.input_proxy_port = toga.TextInput(value="7890", style=Pack(width=80))

        # Step 7: Confirmation & Execution
        self.label_summary = toga.Label("", style=Pack(margin=5))
        self.label_status = toga.Label("Ready to clone.", style=Pack(margin=5, font_weight="bold"))
        self.progress_bar = toga.ProgressBar(max=None, style=Pack(flex=1, margin=5))  # indeterminate

    def _build_layout(self) -> toga.Box:
        root = toga.Box(style=Pack(direction=COLUMN, margin=15, flex=1))
        root.add(self.label_step_header)
        root.add(self.step_container)

        nav_box = toga.Box(style=Pack(direction=ROW, margin_top=10))
        nav_box.add(self.btn_cancel)
        nav_box.add(toga.Box(style=Pack(flex=1)))
        nav_box.add(self.btn_prev)
        nav_box.add(self.btn_next)
        root.add(nav_box)
        return root

    def _render_current_step(self):
        # Clear step container
        while len(self.step_container.children) > 0:
            self.step_container.remove(self.step_container.children[0])

        self.btn_prev.enabled = (self.current_step > 1)
        self.btn_next.text = "🚀 Clone Now" if self.current_step == self.TOTAL_STEPS else "Next ▶"

        if self.current_step == 1:
            self.label_step_header.text = "Step 1 of 7: Select Source Application"
            box = toga.Box(style=Pack(direction=COLUMN, margin=5))
            box.add(toga.Label("Choose the .app bundle you want to clone:", style=Pack(margin_bottom=8)))
            row = toga.Box(style=Pack(direction=ROW))
            row.add(self.input_app_path)
            row.add(self.btn_browse_app)
            box.add(row)
            self.step_container.add(box)

        elif self.current_step == 2:
            self.label_step_header.text = "Step 2 of 7: Confirm Recipe & Strategy"
            box = toga.Box(style=Pack(direction=COLUMN, margin=5))
            box.add(self.label_recipe_app)
            box.add(self.label_recipe_bundle)
            box.add(self.label_recipe_strat)
            box.add(self.label_recipe_origin)
            row_strat = toga.Box(style=Pack(direction=ROW, margin_top=5))
            row_strat.add(toga.Label("Cloning Strategy:", style=Pack(width=130)))
            row_strat.add(self.select_recipe_strat)
            box.add(row_strat)
            self.step_container.add(box)

        elif self.current_step == 3:
            self.label_step_header.text = "Step 3 of 7: Clone Name & Display Name"
            box = toga.Box(style=Pack(direction=COLUMN, margin=5))
            row_name = toga.Box(style=Pack(direction=ROW, margin=5))
            row_name.add(toga.Label("Clone Name:", style=Pack(width=130)))
            row_name.add(self.input_clone_name)
            box.add(row_name)

            row_disp = toga.Box(style=Pack(direction=ROW, margin=5))
            row_disp.add(toga.Label("Display Name:", style=Pack(width=130)))
            row_disp.add(self.input_display_name)
            box.add(row_disp)
            self.step_container.add(box)

        elif self.current_step == 4:
            self.label_step_header.text = "Step 4 of 7: Destination Directory"
            box = toga.Box(style=Pack(direction=COLUMN, margin=5))
            box.add(toga.Label("Target directory where the cloned .app will be saved:", style=Pack(margin_bottom=8)))
            row = toga.Box(style=Pack(direction=ROW))
            row.add(self.input_dest_dir)
            row.add(self.btn_browse_dest)
            box.add(row)
            self.step_container.add(box)

        elif self.current_step == 5:
            self.label_step_header.text = "Step 5 of 7: Data Directory Isolation"
            box = toga.Box(style=Pack(direction=COLUMN, margin=5))
            box.add(self.label_data_dir_support)
            row = toga.Box(style=Pack(direction=ROW, margin_top=8))
            row.add(toga.Label("Data Directory:", style=Pack(width=130)))
            row.add(self.input_data_dir)
            if not self.input_data_dir.readonly:
                row.add(self.btn_browse_data)
            box.add(row)
            self.step_container.add(box)

        elif self.current_step == 6:
            self.label_step_header.text = "Step 6 of 7: Network Proxy Configuration"
            box = toga.Box(style=Pack(direction=COLUMN, margin=5))
            box.add(self.switch_proxy)
            row = toga.Box(style=Pack(direction=ROW, margin=5))
            row.add(toga.Label("Type/Host/Port:", style=Pack(width=130)))
            row.add(self.select_proxy_type)
            row.add(self.input_proxy_host)
            row.add(self.input_proxy_port)
            box.add(row)
            self.step_container.add(box)

        elif self.current_step == 7:
            self.label_step_header.text = "Step 7 of 7: Confirmation & Execution"
            box = toga.Box(style=Pack(direction=COLUMN, margin=5))
            box.add(self.label_summary)
            box.add(self.label_status)
            box.add(self.progress_bar)
            self.step_container.add(box)

    async def _on_browse_app(self, widget: toga.Button):
        """Browse for macOS application bundle (.app) in /Applications."""
        if hasattr(self, "app") and self.app and hasattr(self.app, "main_window"):
            try:
                selected = await self.app.main_window.open_file_dialog(
                    title="Select macOS Application",
                    file_types=["app"],
                    initial_directory=Path("/Applications"),
                )
                if selected:
                    self.input_app_path.value = str(selected)
            except Exception:
                pass

    async def _on_browse_dest(self, widget: toga.Button):
        """Browse for destination directory (step 4)."""
        if hasattr(self, "app") and self.app and hasattr(self.app, "main_window"):
            try:
                selected = await self.app.main_window.select_folder_dialog(
                    title="Select Destination Directory",
                )
                if selected:
                    self.input_dest_dir.value = str(selected)
            except Exception:
                pass

    async def _on_browse_data(self, widget: toga.Button):
        """Browse for data directory (step 5)."""
        if hasattr(self, "app") and self.app and hasattr(self.app, "main_window"):
            try:
                selected = await self.app.main_window.select_folder_dialog(
                    title="Select Data Directory",
                )
                if selected:
                    self.input_data_dir.value = str(selected)
            except Exception:
                pass

    def _on_clone_name_change(self, widget: toga.TextInput):
        """Automatically mirror Clone Name into Display Name if user hasn't customized it."""
        if not getattr(self, "_display_name_customized", False):
            self._syncing_name = True
            try:
                self.input_display_name.value = widget.value
            finally:
                self._syncing_name = False

    def _on_display_name_change(self, widget: toga.TextInput):
        """Track if the user manually typed a custom display name."""
        if getattr(self, "_syncing_name", False):
            return
        if widget.value != self.input_clone_name.value:
            self._display_name_customized = True
        else:
            # If user restored it back to match clone name, re-enable auto-sync
            self._display_name_customized = False

    async def go_prev(self):
        if self.current_step > 1:
            self.current_step -= 1
            self._render_current_step()

    async def go_next(self):
        # Validation before advancing
        if self.current_step == 1:
            path_str = self.input_app_path.value.strip()
            if not path_str:
                await self.error_dialog("Input Required", "Please select or enter an application path.")
                return
            try:
                self.app_info = AppInspector.inspect(path_str)
            except Exception as e:
                # Fallback probe or show error
                await self.error_dialog("Error", f"Failed to inspect app: {e}")
                return

            # Recipe matching: try built-in library first (consistent with CLI cmd_clone logic),
            # fall back to Probe auto-analysis only when no built-in recipe exists.
            self._recipe_from_probe = False
            try:
                self.recipe = RecipeLoader.match(self.app_info.bundle_id)
                self._recipe_from_probe = False
            except Exception:
                # No built-in recipe found — run Probe to auto-generate one
                probe_res = await self.probe_service.probe_app(self.app_info.path)
                self.recipe = probe_res.recipe
                self._recipe_from_probe = True

            self.label_recipe_app.text = f"App Name: {self.app_info.app_name}"
            self.label_recipe_bundle.text = f"Bundle ID: {self.app_info.bundle_id}"
            self.label_recipe_strat.text = f"Matched Strategy: {self.recipe.strategy}"
            self.select_recipe_strat.value = self.recipe.strategy
            if self._recipe_from_probe:
                self.label_recipe_origin.text = "ℹ️ No built-in Recipe found — strategy auto-detected via Probe analysis."
            else:
                self.label_recipe_origin.text = "✅ Matched built-in Recipe from library."

        elif self.current_step == 2:
            self.recipe.strategy = str(self.select_recipe_strat.value)
            out_dir = Path(self.input_dest_dir.value.strip() or str(DEFAULT_APPS_DIR))
            suggested_name, num = AppInspector.next_available_name(self.app_info.app_name, out_dir)
            self._display_name_customized = False
            self.input_clone_name.value = suggested_name
            self.input_display_name.value = suggested_name

        elif self.current_step == 3:
            clone_name = self.input_clone_name.value.strip()
            if not clone_name:
                await self.error_dialog("Input Required", "Clone name cannot be empty.")
                return

        elif self.current_step == 4:
            dest_dir = self.input_dest_dir.value.strip()
            if not dest_dir:
                await self.error_dialog("Input Required", "Destination directory cannot be empty.")
                return
            clone_name = self.input_clone_name.value.strip()
            self.input_data_dir.value = str(DEFAULT_DATA_DIR / clone_name)
            if not supports_data_dir(self.recipe):
                self.label_data_dir_support.text = "⚠️ Custom Data Directory is not supported by this Recipe strategy."
                self.input_data_dir.readonly = True
            else:
                self.label_data_dir_support.text = "✅ Data Directory isolation supported."
                self.input_data_dir.readonly = False

        elif self.current_step == 6:
            # Prepare summary for step 7
            clone_name = self.input_clone_name.value.strip()
            summary_text = (
                f"Source: {self.app_info.app_name} ({self.app_info.bundle_id})\n"
                f"Clone Name: {clone_name}\n"
                f"Strategy: {self.recipe.strategy}\n"
                f"Destination: {self.input_dest_dir.value}/{clone_name}.app\n"
                f"Data Directory: {self.input_data_dir.value}\n"
                f"Proxy: {'Enabled' if self.switch_proxy.value else 'Disabled'}"
            )
            self.label_summary.text = summary_text

        elif self.current_step == 7:
            # Execute cloning!
            await self._execute_clone()
            return

        self.current_step += 1
        self._render_current_step()

    async def _execute_clone(self):
        self.btn_next.enabled = False
        self.btn_prev.enabled = False
        self.label_status.text = "⏳ Cloning application in background..."
        self.progress_bar.start()  # start indeterminate spinner

        clone_name = self.input_clone_name.value.strip()
        dest_dir = Path(self.input_dest_dir.value.strip()).expanduser().resolve()
        dest_path = dest_dir / f"{clone_name}.app"
        data_dir = Path(self.input_data_dir.value.strip()).expanduser().resolve()
        new_bundle_id = AppInspector.generate_bundle_id(self.app_info.bundle_id, 1)
        display_name = self.input_display_name.value.strip() or None

        # Build recipe copy with proxy
        port = 1080
        try:
            port = int(self.input_proxy_port.value)
        except ValueError:
            pass

        recipe = self.recipe.model_copy(deep=True)
        if self.switch_proxy.value:
            recipe.proxy.enabled = True
            recipe.proxy.type = str(self.select_proxy_type.value)
            recipe.proxy.host = self.input_proxy_host.value.strip() or "127.0.0.1"
            recipe.proxy.port = port

        task = CloneTask(
            source=self.app_info,
            dest_path=dest_path,
            data_dir=data_dir,
            recipe=recipe,
            clone_name=clone_name,
            new_bundle_id=new_bundle_id,
            display_name=display_name,
        )

        try:
            await self.clone_service.create_clone(task)
            self.progress_bar.stop()
            self.label_status.text = f"🎉 Successfully created clone at {dest_path}!"
            if self.on_complete_callback:
                await self.on_complete_callback()
            await self.info_dialog("Success", f"Clone created successfully!\n{dest_path}")
            self.close()
        except Exception as e:
            self.progress_bar.stop()
            self.label_status.text = f"❌ Clone failed: {e}"
            await self.error_dialog("Clone Error", str(e))
            self.btn_next.enabled = True
            self.btn_prev.enabled = True
