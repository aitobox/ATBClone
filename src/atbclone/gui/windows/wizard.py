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
from atbclone.core.i18n import t
from atbclone.core.logger import get_logger
from atbclone.core.models import AppInfo
from atbclone.gui.services.clone_service import CloneService
from atbclone.gui.services.probe_service import ProbeService
from atbclone.recipes.loader import RecipeLoader
from atbclone.recipes.models import Recipe, ProxyConfig, supports_data_dir
from atbclone.gui.patch_cocoa import patch_cocoa_widgets, configure_cocoa_window

logger = get_logger("gui.wizard")


class WizardWindow(toga.Window):
    TOTAL_STEPS = 7

    def __init__(
        self,
        clone_service: CloneService | None = None,
        probe_service: ProbeService | None = None,
        on_complete: Callable[[], Coroutine[Any, Any, None]] | None = None,
    ):
        patch_cocoa_widgets()
        super().__init__(title=t("win_wizard_title"), size=(560, 520))
        configure_cocoa_window(self, floating=True)

        self.clone_service = clone_service or CloneService()
        self.probe_service = probe_service or ProbeService()
        self.on_complete_callback = on_complete

        self.current_step = 1
        self.app_info: AppInfo | None = None
        self.recipe: Recipe | None = None

        # Step indicator label
        self.label_step_header = toga.Label(
            t("win_wizard_step1_header"),
            style=Pack(font_size=15, font_weight="bold", margin_bottom=10),
        )

        # Dynamic container for step forms
        self.step_container = toga.Box(style=Pack(direction=COLUMN, flex=1, margin=10))

        # Bottom navigation buttons
        self.btn_prev = toga.Button(t("win_wizard_btn_back"), on_press=lambda w: asyncio.create_task(self.go_prev()), enabled=False, style=Pack(margin=5))
        self.btn_next = toga.Button(t("win_wizard_btn_next"), on_press=lambda w: asyncio.create_task(self.go_next()), style=Pack(margin=5))
        self.btn_cancel = toga.Button(t("btn_cancel"), on_press=lambda w: self.close(), style=Pack(margin=5))

        # Initialize UI elements for all 7 steps
        self._init_step_widgets()

        # Build window layout
        self.content = self._build_layout()
        self._render_current_step()

    def show(self):
        super().show()
        configure_cocoa_window(self, floating=True)


    def _init_step_widgets(self):
        # Step 1: Select App
        self.input_app_path = toga.TextInput(placeholder="/Applications/Example.app", style=Pack(flex=1))
        self.btn_browse_app = toga.Button(t("btn_browse_app"), on_press=self._on_browse_app, style=Pack(margin_left=5))

        # Step 2: Recipe Info
        self.label_recipe_app = toga.Label(f"{t('probe_row_app_name')}: —", style=Pack(margin=4))
        self.label_recipe_bundle = toga.Label(f"{t('probe_row_bundle_id')}: —", style=Pack(margin=4))
        self.label_recipe_strat = toga.Label(f"{t('probe_row_strategy')}: —", style=Pack(margin=4))
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
        self.btn_browse_dest = toga.Button(t("btn_browse_dir"), on_press=self._on_browse_dest, style=Pack(margin_left=5))

        # Step 5: Data Directory
        self.label_data_dir_support = toga.Label(t("win_wizard_step5_supported"), style=Pack(margin=4))
        self.input_data_dir = toga.TextInput(style=Pack(flex=1))
        self.btn_browse_data = toga.Button(t("btn_browse_dir"), on_press=self._on_browse_data, style=Pack(margin_left=5))

        # Step 6: Proxy Settings
        self.switch_proxy = toga.Switch(t("win_wizard_step6_switch"), value=False, style=Pack(margin=5))
        self.select_proxy_type = toga.Selection(items=["http", "socks5"], style=Pack(width=100))
        self.input_proxy_host = toga.TextInput(value="127.0.0.1", style=Pack(flex=1))
        self.input_proxy_port = toga.TextInput(value="7890", style=Pack(width=80))

        # Step 7: Confirmation & Execution
        self.label_summary = toga.Label("", style=Pack(margin=5))
        self.label_status = toga.Label(t("win_wizard_status_ready"), style=Pack(margin=5, font_weight="bold"))
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
        self.btn_next.text = t("win_wizard_btn_clone_now") if self.current_step == self.TOTAL_STEPS else t("win_wizard_btn_next")

        if self.current_step == 1:
            self.label_step_header.text = t("win_wizard_step1_header")
            box = toga.Box(style=Pack(direction=COLUMN, margin=5))
            box.add(toga.Label(t("win_wizard_step1_desc"), style=Pack(margin_bottom=8)))
            row = toga.Box(style=Pack(direction=ROW))
            row.add(self.input_app_path)
            row.add(self.btn_browse_app)
            box.add(row)
            self.step_container.add(box)

        elif self.current_step == 2:
            self.label_step_header.text = t("win_wizard_step2_header")
            box = toga.Box(style=Pack(direction=COLUMN, margin=5))
            box.add(self.label_recipe_app)
            box.add(self.label_recipe_bundle)
            box.add(self.label_recipe_strat)
            box.add(self.label_recipe_origin)
            row_strat = toga.Box(style=Pack(direction=ROW, margin_top=5))
            row_strat.add(toga.Label(t("win_wizard_step2_select_strat"), style=Pack(width=130)))
            row_strat.add(self.select_recipe_strat)
            box.add(row_strat)
            self.step_container.add(box)

        elif self.current_step == 3:
            self.label_step_header.text = t("win_wizard_step3_header")
            box = toga.Box(style=Pack(direction=COLUMN, margin=5))
            row_name = toga.Box(style=Pack(direction=ROW, margin=5))
            row_name.add(toga.Label(t("win_wizard_step3_clone_name"), style=Pack(width=130)))
            row_name.add(self.input_clone_name)
            box.add(row_name)

            row_disp = toga.Box(style=Pack(direction=ROW, margin=5))
            row_disp.add(toga.Label(t("win_wizard_step3_display_name"), style=Pack(width=130)))
            row_disp.add(self.input_display_name)
            box.add(row_disp)
            self.step_container.add(box)

        elif self.current_step == 4:
            self.label_step_header.text = t("win_wizard_step4_header")
            box = toga.Box(style=Pack(direction=COLUMN, margin=5))
            box.add(toga.Label(t("win_wizard_step4_desc"), style=Pack(margin_bottom=8)))
            row = toga.Box(style=Pack(direction=ROW))
            row.add(self.input_dest_dir)
            row.add(self.btn_browse_dest)
            box.add(row)
            self.step_container.add(box)

        elif self.current_step == 5:
            self.label_step_header.text = t("win_wizard_step5_header")
            box = toga.Box(style=Pack(direction=COLUMN, margin=5))
            box.add(self.label_data_dir_support)
            row = toga.Box(style=Pack(direction=ROW, margin_top=8))
            row.add(toga.Label(t("win_wizard_step5_label"), style=Pack(width=130)))
            row.add(self.input_data_dir)
            if not self.input_data_dir.readonly:
                row.add(self.btn_browse_data)
            box.add(row)
            self.step_container.add(box)

        elif self.current_step == 6:
            self.label_step_header.text = t("win_wizard_step6_header")
            box = toga.Box(style=Pack(direction=COLUMN, margin=5))
            box.add(self.switch_proxy)
            row = toga.Box(style=Pack(direction=ROW, margin=5))
            row.add(toga.Label(t("win_wizard_step6_type_host_port"), style=Pack(width=130)))
            row.add(self.select_proxy_type)
            row.add(self.input_proxy_host)
            row.add(self.input_proxy_port)
            box.add(row)
            self.step_container.add(box)

        elif self.current_step == 7:
            self.label_step_header.text = t("win_wizard_step7_header")
            box = toga.Box(style=Pack(direction=COLUMN, margin=5))
            box.add(self.label_summary)
            box.add(self.label_status)
            box.add(self.progress_bar)
            self.step_container.add(box)

        # Keep wizard window in front and focused during step transitions
        configure_cocoa_window(self, floating=True)

    async def _on_browse_app(self, widget: toga.Button):
        """Browse for macOS application bundle (.app) in /Applications."""
        try:
            selected = await self.open_file_dialog(
                title=t("dialog_select_app_title"),
                file_types=["app"],
                initial_directory=Path("/Applications"),
            )
            if selected:
                self.input_app_path.value = str(selected)
        except Exception:
            pass
        finally:
            configure_cocoa_window(self, floating=True)

    async def _on_browse_dest(self, widget: toga.Button):
        """Browse for destination directory (step 4)."""
        try:
            selected = await self.select_folder_dialog(
                title=t("dialog_select_dest_dir_title"),
            )
            if selected:
                self.input_dest_dir.value = str(selected)
        except Exception:
            pass
        finally:
            configure_cocoa_window(self, floating=True)

    async def _on_browse_data(self, widget: toga.Button):
        """Browse for data directory (step 5)."""
        try:
            selected = await self.select_folder_dialog(
                title=t("dialog_select_data_dir_title"),
            )
            if selected:
                self.input_data_dir.value = str(selected)
        except Exception:
            pass
        finally:
            configure_cocoa_window(self, floating=True)

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
                await self.error_dialog(t("dialog_input_required_title"), t("dialog_input_required_app_path"))
                return
            try:
                self.app_info = AppInspector.inspect(path_str)
            except Exception as e:
                # Fallback probe or show error
                await self.error_dialog(t("dialog_error_title"), f"Failed to inspect app: {e}")
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

            self.label_recipe_app.text = f"{t('probe_row_app_name')}: {self.app_info.app_name}"
            self.label_recipe_bundle.text = f"{t('probe_row_bundle_id')}: {self.app_info.bundle_id}"
            self.label_recipe_strat.text = f"{t('probe_row_strategy')}: {self.recipe.strategy}"
            self.select_recipe_strat.value = self.recipe.strategy
            if self._recipe_from_probe:
                self.label_recipe_origin.text = t("win_wizard_step2_origin_probe")
            else:
                self.label_recipe_origin.text = t("win_wizard_step2_origin_builtin")

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
                await self.error_dialog(t("dialog_input_required_title"), t("dialog_input_required_clone_name"))
                return

        elif self.current_step == 4:
            dest_dir = self.input_dest_dir.value.strip()
            if not dest_dir:
                await self.error_dialog(t("dialog_input_required_title"), t("dialog_input_required_dest_dir"))
                return
            clone_name = self.input_clone_name.value.strip()
            self.input_data_dir.value = str(DEFAULT_DATA_DIR / clone_name)
            if not supports_data_dir(self.recipe):
                self.label_data_dir_support.text = t("win_wizard_step5_unsupported")
                self.input_data_dir.readonly = True
            else:
                self.label_data_dir_support.text = t("win_wizard_step5_supported")
                self.input_data_dir.readonly = False

        elif self.current_step == 6:
            # Prepare summary for step 7
            clone_name = self.input_clone_name.value.strip()
            proxy_str = t("list_proxy_enabled") if self.switch_proxy.value else t("list_proxy_disabled")
            data_label = t("win_wizard_step5_label").rstrip(":")
            summary_text = (
                f"{t('card_label_source', source_app=self.app_info.app_name)} ({self.app_info.bundle_id})\n"
                f"{t('list_col_name')}: {clone_name}\n"
                f"{t('list_col_strategy')}: {self.recipe.strategy}\n"
                f"{t('list_col_destination')}: {self.input_dest_dir.value}/{clone_name}.app\n"
                f"{data_label}: {self.input_data_dir.value}\n"
                f"{t('list_col_proxy')}: {proxy_str}"
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
        self.label_status.text = t("win_wizard_status_cloning")
        self.progress_bar.start()  # start indeterminate spinner

        clone_name = self.input_clone_name.value.strip()
        dest_dir = Path(self.input_dest_dir.value.strip()).expanduser().resolve()
        dest_path = dest_dir / f"{clone_name}.app"
        data_dir = Path(self.input_data_dir.value.strip()).expanduser().resolve()
        new_bundle_id = AppInspector.generate_bundle_id(self.app_info.bundle_id, 1)
        display_name = self.input_display_name.value.strip() or None

        logger.info(f"Wizard executing clone: name='{clone_name}', source='{self.app_info.path}', dest='{dest_path}', data_dir='{data_dir}'")

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
            self.label_status.text = t("win_wizard_status_success", path=str(dest_path))
            logger.info(f"Wizard finished successfully for clone '{clone_name}'")
            if self.on_complete_callback:
                await self.on_complete_callback()
            await self.info_dialog(
                t("dialog_clone_success_title"),
                t("dialog_clone_success_msg", path=str(dest_path)),
            )
            self.close()
        except Exception as e:
            self.progress_bar.stop()
            self.label_status.text = t("win_wizard_status_failed", error=str(e))
            logger.error(f"Wizard failed to create clone '{clone_name}': {e}")
            await self.error_dialog(t("dialog_clone_error_title"), str(e))
            self.btn_next.enabled = True
            self.btn_prev.enabled = True

