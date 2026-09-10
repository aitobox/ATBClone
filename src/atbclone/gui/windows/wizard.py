"""7-Step Interactive Cloning Wizard Window."""

import asyncio
from pathlib import Path
from typing import Callable, Coroutine, Any
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER

from atbclone.core.app_inspector import AppInspector
from atbclone.core.clone_task import CloneTask
from atbclone.core.config import DEFAULT_APPS_DIR, DEFAULT_DATA_DIR, get_config_value
from atbclone.core.i18n import t
from atbclone.core.logger import get_logger
from atbclone.core.models import AppInfo
from atbclone.gui.services.clone_service import CloneService
from atbclone.gui.services.probe_service import ProbeService
from atbclone.recipes.loader import RecipeLoader
from atbclone.recipes.models import Recipe, ProxyConfig, supports_data_dir
from atbclone.gui.components.wrapping_label import WrappingLabel
from atbclone.gui.patch_cocoa import patch_cocoa_widgets, configure_cocoa_window
from atbclone.gui.theme import Theme
from atbclone.validation import validate_host, validate_proxy_port, validate_proxy_credential

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
        super().__init__(title=t("win_wizard_title"), size=(580, 530))
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
            style=Pack(font_size=15, font_weight="bold", margin_bottom=12, color=Theme.TEXT_PRIMARY),
        )

        # Dynamic container for step forms
        self.step_container = toga.Box(style=Pack(direction=COLUMN, flex=1, margin=6))

        # Bottom navigation buttons
        self.btn_prev = toga.Button(t("win_wizard_btn_back"), on_press=lambda w: asyncio.create_task(self.go_prev()), enabled=False, style=Pack(margin=4, height=30, font_size=13))
        self.btn_next = toga.Button(t("win_wizard_btn_next"), on_press=lambda w: asyncio.create_task(self.go_next()), style=Pack(margin=4, height=30, font_size=13, font_weight="bold"))
        self.btn_cancel = toga.Button(t("btn_cancel"), on_press=lambda w: self.close(), style=Pack(margin=4, height=30, font_size=13))

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
        self.input_app_path = toga.TextInput(placeholder="/Applications/Example.app", style=Pack(flex=1, margin_right=8, font_size=13.5))
        self.btn_browse_app = toga.Button(t("btn_browse_app"), on_press=self._on_browse_app, style=Pack(height=30, font_size=13))

        # Step 2: Recipe Info
        self.label_recipe_app = WrappingLabel(f"{t('probe_row_app_name')}: —", style=Pack(font_size=13, color=Theme.TEXT_MUTED, margin_bottom=4))
        self.label_recipe_bundle = WrappingLabel(f"{t('probe_row_bundle_id')}: —", style=Pack(font_size=13, color=Theme.TEXT_MUTED, margin_bottom=4))
        self.label_recipe_strat = WrappingLabel(f"{t('probe_row_strategy')}: —", style=Pack(font_size=13, color=Theme.TEXT_MUTED, margin_bottom=4))
        self.select_recipe_strat = toga.Selection(items=["hard_clone", "soft_clone"], style=Pack(width=160, font_size=12.0))
        self.select_injection_strat = toga.Selection(items=["auto", "dylib", "launcher"], style=Pack(width=160, font_size=12.0))
        # Shows whether recipe came from built-in library or Probe analysis
        self.label_recipe_origin = WrappingLabel("", style=Pack(font_size=11.5, font_style="italic", margin_bottom=6))

        # Step 3: Naming & Language
        self._display_name_customized = False
        self._syncing_name = False
        self.input_clone_name = toga.TextInput(
            placeholder="e.g. WeChat2",
            on_change=self._on_clone_name_change,
            style=Pack(flex=1, font_size=13.5),
        )
        self.input_display_name = toga.TextInput(
            placeholder="Display name in Dock/Finder",
            on_change=self._on_display_name_change,
            style=Pack(flex=1, font_size=13.5),
        )

        from atbclone.core.locale import SUPPORTED_LANGUAGES
        self._lang_keys = list(SUPPORTED_LANGUAGES.keys())
        self._lang_display_items = [
            t(SUPPORTED_LANGUAGES[k]["label_key"]) for k in self._lang_keys
        ]
        self.select_language = toga.Selection(
            items=self._lang_display_items,
            style=Pack(flex=1, font_size=12.0),
        )

        # Step 4: Destination Directory
        self.input_dest_dir = toga.TextInput(value=str(DEFAULT_APPS_DIR), style=Pack(flex=1, margin_right=8, font_size=13.5))
        self.btn_browse_dest = toga.Button(t("btn_browse_dir"), on_press=self._on_browse_dest, style=Pack(height=30, font_size=13))

        # Step 5: Data Directory
        self.label_data_dir_support = WrappingLabel(t("win_wizard_step5_supported"), style=Pack(font_size=13, color=Theme.TEXT_MUTED, margin_bottom=6))
        self.input_data_dir = toga.TextInput(style=Pack(flex=1, margin_right=8, font_size=13.5))
        self.btn_browse_data = toga.Button(t("btn_browse_dir"), on_press=self._on_browse_data, style=Pack(height=30, font_size=13))

        # Step 6: Proxy Settings
        cfg_proxy = get_config_value("default_proxy", {})
        default_proxy_enabled = bool(cfg_proxy.get("enabled", False))
        default_proxy_type = cfg_proxy.get("type", "http")
        default_proxy_host = cfg_proxy.get("host", "127.0.0.1")
        default_proxy_port = str(cfg_proxy.get("port", 7890))
        default_proxy_user = cfg_proxy.get("username", "")
        default_proxy_has_auth = bool(default_proxy_user)
        default_proxy_pass = ""
        if default_proxy_has_auth:
            try:
                from atbclone.core.keychain import get_default_proxy_password
                p = get_default_proxy_password()
                if p:
                    default_proxy_pass = p
            except Exception:
                pass

        self.switch_proxy = toga.Switch(
            t("win_wizard_step6_switch"),
            value=default_proxy_enabled,
            on_change=self._on_proxy_toggle,
            style=Pack(margin_bottom=8, font_size=13.5),
        )
        self.select_proxy_type = toga.Selection(
            items=["http", "https", "socks5"],
            value=default_proxy_type if default_proxy_type in ["http", "https", "socks5"] else "http",
            style=Pack(width=105, margin_right=8, font_size=12.0),
        )
        self.input_proxy_host = toga.TextInput(value=default_proxy_host, style=Pack(flex=1, margin_right=8, font_size=13.5))
        self.input_proxy_port = toga.TextInput(value=default_proxy_port, style=Pack(width=90, font_size=13.5))

        self.switch_proxy_auth = toga.Switch(
            t("proxy_auth_enable"),
            value=default_proxy_has_auth,
            on_change=self._on_auth_toggle,
            style=Pack(margin_top=8, margin_bottom=6, font_size=13),
        )
        self.input_proxy_user = toga.TextInput(
            value=default_proxy_user,
            placeholder=t("proxy_auth_username"),
            style=Pack(flex=1, margin_right=8, font_size=13),
        )
        self.input_proxy_pass = toga.PasswordInput(
            value=default_proxy_pass,
            placeholder=t("proxy_auth_password"),
            style=Pack(flex=1, font_size=13),
        )

        # Step 7: Confirmation & Execution
        self.label_summary = WrappingLabel("", style=Pack(font_size=12.5, color=Theme.TEXT_MUTED, margin_bottom=10))
        self.label_status = toga.Label(t("win_wizard_status_ready"), style=Pack(font_size=13.5, font_weight="bold", margin_bottom=8, color=Theme.TEXT_PRIMARY))
        self.progress_bar = toga.ProgressBar(max=None, style=Pack(flex=1, margin_top=4))  # indeterminate
        self._on_proxy_toggle(self.switch_proxy)

    def _on_proxy_toggle(self, widget: toga.Switch) -> None:
        enabled = bool(widget.value)
        self.select_proxy_type.enabled = enabled
        self.input_proxy_host.enabled = enabled
        self.input_proxy_port.enabled = enabled
        self.switch_proxy_auth.enabled = enabled
        auth_enabled = enabled and bool(self.switch_proxy_auth.value)
        self.input_proxy_user.enabled = auth_enabled
        self.input_proxy_pass.enabled = auth_enabled

    def _on_auth_toggle(self, widget: toga.Switch) -> None:
        auth_enabled = bool(self.switch_proxy.value) and bool(widget.value)
        self.input_proxy_user.enabled = auth_enabled
        self.input_proxy_pass.enabled = auth_enabled

    def _build_layout(self) -> toga.Box:
        root = toga.Box(style=Pack(direction=COLUMN, margin=(18, 20, 18, 20), flex=1))
        root.add(self.label_step_header)
        root.add(self.step_container)

        nav_box = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin_top=14))
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
            box = toga.Box(style=Pack(direction=COLUMN, margin=4))
            box.add(toga.Label(t("win_wizard_step1_desc"), style=Pack(font_size=13.5, color=Theme.TEXT_MUTED, margin_bottom=10)))
            row = toga.Box(style=Pack(direction=ROW, align_items=CENTER))
            row.add(self.input_app_path)
            row.add(self.btn_browse_app)
            box.add(row)
            self.step_container.add(box)

        elif self.current_step == 2:
            self.label_step_header.text = t("win_wizard_step2_header")
            box = toga.Box(style=Pack(direction=COLUMN, margin=4))
            box.add(self.label_recipe_app)
            box.add(self.label_recipe_bundle)
            box.add(self.label_recipe_strat)
            box.add(self.label_recipe_origin)
            row_strat = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin_top=8))
            row_strat.add(toga.Label(t("win_wizard_step2_select_strat"), style=Pack(width=130, font_size=14, color=Theme.TEXT_PRIMARY)))
            row_strat.add(self.select_recipe_strat)
            box.add(row_strat)
            row_inj = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin_top=8))
            row_inj.add(toga.Label(t("win_wizard_step2_select_injection"), style=Pack(width=130, font_size=14, color=Theme.TEXT_PRIMARY)))
            row_inj.add(self.select_injection_strat)
            box.add(row_inj)
            self.step_container.add(box)

        elif self.current_step == 3:
            self.label_step_header.text = t("win_wizard_step3_header")
            box = toga.Box(style=Pack(direction=COLUMN, margin=4))
            row_name = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin_bottom=8))
            row_name.add(toga.Label(t("win_wizard_step3_clone_name"), style=Pack(width=130, font_size=14, color=Theme.TEXT_PRIMARY)))
            row_name.add(self.input_clone_name)
            box.add(row_name)

            row_disp = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin_bottom=8))
            row_disp.add(toga.Label(t("win_wizard_step3_display_name"), style=Pack(width=130, font_size=14, color=Theme.TEXT_PRIMARY)))
            row_disp.add(self.input_display_name)
            box.add(row_disp)

            row_lang = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin_bottom=8))
            row_lang.add(toga.Label(t("win_wizard_step3_language"), style=Pack(width=130, font_size=14, color=Theme.TEXT_PRIMARY)))
            row_lang.add(self.select_language)
            box.add(row_lang)
            self.step_container.add(box)

        elif self.current_step == 4:
            self.label_step_header.text = t("win_wizard_step4_header")
            box = toga.Box(style=Pack(direction=COLUMN, margin=4))
            box.add(toga.Label(t("win_wizard_step4_desc"), style=Pack(font_size=13.5, color=Theme.TEXT_MUTED, margin_bottom=10)))
            row = toga.Box(style=Pack(direction=ROW, align_items=CENTER))
            row.add(self.input_dest_dir)
            row.add(self.btn_browse_dest)
            box.add(row)
            self.step_container.add(box)

        elif self.current_step == 5:
            self.label_step_header.text = t("win_wizard_step5_header")
            box = toga.Box(style=Pack(direction=COLUMN, margin=4))
            box.add(self.label_data_dir_support)
            row = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin_top=8))
            row.add(toga.Label(t("win_wizard_step5_label"), style=Pack(width=130, font_size=14, color=Theme.TEXT_PRIMARY)))
            row.add(self.input_data_dir)
            if not self.input_data_dir.readonly:
                row.add(self.btn_browse_data)
            box.add(row)
            self.step_container.add(box)

        elif self.current_step == 6:
            self.label_step_header.text = t("win_wizard_step6_header")
            box = toga.Box(style=Pack(direction=COLUMN, margin=4))
            box.add(self.switch_proxy)
            row = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin_top=6))
            row.add(toga.Label(t("win_wizard_step6_type_host_port"), style=Pack(width=130, font_size=14, color=Theme.TEXT_PRIMARY)))
            row.add(self.select_proxy_type)
            row.add(self.input_proxy_host)
            row.add(self.input_proxy_port)
            box.add(row)

            # Proxy Auth Section
            box_auth = toga.Box(style=Pack(direction=COLUMN, margin_top=8, margin_left=12))
            box_auth.add(self.switch_proxy_auth)

            row_auth = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin_top=4))
            row_auth.add(toga.Label(t("proxy_auth_username"), style=Pack(width=80, font_size=12.5, color=Theme.TEXT_PRIMARY)))
            row_auth.add(self.input_proxy_user)
            row_auth.add(toga.Label(t("proxy_auth_password"), style=Pack(margin_left=8, margin_right=6, font_size=12.5, color=Theme.TEXT_PRIMARY)))
            row_auth.add(self.input_proxy_pass)
            box_auth.add(row_auth)

            box_auth.add(toga.Label(t("proxy_auth_password_hint"), style=Pack(font_size=11, color=Theme.TEXT_MUTED, margin_top=4, margin_left=80)))
            box.add(box_auth)

            self.step_container.add(box)

        elif self.current_step == 7:
            self.label_step_header.text = t("win_wizard_step7_header")
            box = toga.Box(style=Pack(direction=COLUMN, margin=4))
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

            if getattr(self.app_info, "is_ios_app", False):
                await self.error_dialog(t("dialog_clone_error_title"), t("clone_err_ios_wrapper_unsupported"))
                return

            # Recipe matching: try built-in library first (consistent with CLI cmd_clone logic),
            # fall back to Probe auto-analysis only when no built-in recipe exists.
            if RecipeLoader.has_recipe(self.app_info.bundle_id):
                self.recipe = RecipeLoader.match(self.app_info.bundle_id, app_path=self.app_info.path)
                self._recipe_from_probe = False
            else:
                # No built-in recipe found — run Probe to auto-generate one
                probe_res = await self.probe_service.probe_app(self.app_info.path)
                self.recipe = probe_res.recipe
                self._recipe_from_probe = True

            self.label_recipe_app.text = f"{t('probe_row_app_name')}: {self.app_info.app_name}"
            self.label_recipe_bundle.text = f"{t('probe_row_bundle_id')}: {self.app_info.bundle_id}"
            self.label_recipe_strat.text = f"{t('probe_row_strategy')}: {self.recipe.strategy}"
            self.select_recipe_strat.value = self.recipe.strategy
            self.select_injection_strat.value = getattr(self.recipe, "injection_strategy", "auto")
            if self._recipe_from_probe:
                self.label_recipe_origin.text = t("win_wizard_step2_origin_probe")
            else:
                self.label_recipe_origin.text = t("win_wizard_step2_origin_builtin")

        elif self.current_step == 2:
            self.recipe.strategy = str(self.select_recipe_strat.value)
            self.recipe.injection_strategy = str(self.select_injection_strat.value)
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
            # Validate proxy settings before advancing
            if self.switch_proxy.value:
                host = self.input_proxy_host.value.strip() or "127.0.0.1"
                port_str = self.input_proxy_port.value.strip()
                try:
                    validate_host(host)
                    try:
                        port = int(port_str)
                    except ValueError:
                        raise ValueError(f"Invalid proxy port: {port_str!r}. Expected an integer 1-65535.")
                    validate_proxy_port(port)

                    if self.switch_proxy_auth.value:
                        user = self.input_proxy_user.value.strip()
                        pwd = self.input_proxy_pass.value or ""
                        validate_proxy_credential(user, field="username")
                        validate_proxy_credential(pwd, field="password")
                except ValueError as e:
                    await self.error_dialog(t("dialog_validation_error_title"), str(e))
                    return

            # Prepare summary for step 7
            clone_name = self.input_clone_name.value.strip()
            if self.switch_proxy.value:
                if self.switch_proxy_auth.value and self.input_proxy_user.value.strip():
                    user_str = f"{self.input_proxy_user.value.strip()}:***@"
                else:
                    user_str = ""
                proxy_str = f"{self.select_proxy_type.value}://{user_str}{self.input_proxy_host.value.strip()}:{self.input_proxy_port.value.strip()}"
            else:
                proxy_str = t("list_proxy_disabled")
            data_label = t("win_wizard_step5_label").rstrip(":")
            summary_text = (
                f"{t('card_label_source', source_app=self.app_info.app_name)} ({self.app_info.bundle_id})\n"
                f"{t('list_col_name')}: {clone_name}\n"
                f"{t('list_col_strategy')}: {self.recipe.strategy}\n"
                f"{t('detail_label_injection')}: {self.select_injection_strat.value}\n"
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

    def _get_selected_language(self) -> str:
        if self.select_language.value:
            try:
                idx = self._lang_display_items.index(str(self.select_language.value))
                return self._lang_keys[idx]
            except ValueError:
                pass
        return "system"

    async def _execute_clone(self):
        if getattr(self.app_info, "is_ios_app", False):
            err_msg = t("clone_err_ios_wrapper_unsupported")
            self.label_status.text = t("win_wizard_status_failed", error=err_msg)
            logger.error(f"Wizard cannot clone iOS wrapper app '{self.app_info.app_name}': {err_msg}")
            await self.error_dialog(t("dialog_clone_error_title"), err_msg)
            self.btn_next.enabled = True
            self.btn_prev.enabled = True
            return

        self.btn_next.enabled = False
        self.btn_prev.enabled = False
        self.label_status.text = t("win_wizard_status_cloning")
        self.progress_bar.start()  # start indeterminate spinner

        clone_name = self.input_clone_name.value.strip()
        dest_dir = Path(self.input_dest_dir.value.strip()).expanduser().resolve()
        dest_path = dest_dir / f"{clone_name}.app"
        data_dir = Path(self.input_data_dir.value.strip()).expanduser().resolve()
        existing_records = self.clone_service.state_manager.load()
        existing_bundle_ids = {r.new_bundle_id for r in existing_records if r.new_bundle_id}
        new_bundle_id = AppInspector.resolve_bundle_id(
            self.app_info.bundle_id,
            clone_name=clone_name,
            existing_bundle_ids=existing_bundle_ids,
        )
        display_name = self.input_display_name.value.strip() or None
        lang = self._get_selected_language()

        logger.info(f"Wizard executing clone: name='{clone_name}', source='{self.app_info.path}', dest='{dest_path}', data_dir='{data_dir}', language='{lang}'")

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
            if self.switch_proxy_auth.value:
                recipe.proxy.username = self.input_proxy_user.value.strip()
                recipe.proxy.password = self.input_proxy_pass.value or ""

        try:
            task = CloneTask(
                source=self.app_info,
                dest_path=dest_path,
                data_dir=data_dir,
                recipe=recipe,
                clone_name=clone_name,
                new_bundle_id=new_bundle_id,
                display_name=display_name,
                language=lang,
                injection_strategy=str(self.select_injection_strat.value),
            )
        except ValueError as e:
            self.progress_bar.stop()
            self.label_status.text = t("win_wizard_status_failed", error=str(e))
            logger.error(f"Wizard rejected clone inputs for '{clone_name}': {e}")
            await self.error_dialog(t("dialog_clone_error_title"), str(e))
            self.btn_next.enabled = True
            self.btn_prev.enabled = True
            return

        try:
            await self.clone_service.create_clone(task)
            self.progress_bar.stop()
            self.label_status.text = t("win_wizard_status_success", dest=str(dest_path))
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

