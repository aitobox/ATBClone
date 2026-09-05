"""Recipe Editor Window."""

from typing import Callable, Coroutine, Any
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER

from atbclone.core.i18n import t
from atbclone.core.locale import SUPPORTED_LANGUAGES
from atbclone.recipes.models import AppType, ProxyConfig, Recipe
from atbclone.gui.patch_cocoa import configure_cocoa_window
from atbclone.gui.theme import Theme


def format_env_injection(env: dict[str, str]) -> str:
    """Serialize dictionary of env vars to multi-line KEY=VALUE format."""
    return "\n".join(f"{k}={v}" for k, v in env.items())


def parse_env_injection(text: str) -> tuple[dict[str, str], str | None]:
    """
    Parse multi-line KEY=VALUE text into a dict.
    Ignores empty lines and comments (starting with #).
    Returns (env_dict, error_message). If invalid syntax is found, error_message is not None.
    """
    env_dict: dict[str, str] = {}
    lines = text.strip().splitlines()
    for idx, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            return {}, t("dialog_recipe_invalid_env_line", line_num=idx, line=line)
        key, val = line.split("=", 1)
        key = key.strip()
        val = val.strip()
        if not key:
            return {}, t("dialog_recipe_invalid_env_line", line_num=idx, line=line)
        env_dict[key] = val
    return env_dict, None


def format_list_lines(items: list[str]) -> str:
    """Serialize list of strings into multi-line text."""
    return "\n".join(items)


def parse_list_lines(text: str) -> list[str]:
    """Parse multi-line text into a list of strings, stripping blanks and comments."""
    result: list[str] = []
    for raw_line in text.strip().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        result.append(line)
    return result


class RecipeEditWindow(toga.Window):
    def __init__(
        self,
        title: str = "Edit Recipe",
        recipe: Recipe | None = None,
        on_save: Callable[[Recipe], Coroutine[Any, Any, None]] | None = None,
    ):
        super().__init__(title=title, size=(540, 580))
        configure_cocoa_window(self, floating=True)
        self.original_recipe = recipe
        self.on_save_callback = on_save

        # Basic inputs
        self.input_bundle_id = toga.TextInput(
            value=recipe.bundle_id if recipe else "",
            readonly=bool(recipe and recipe.bundle_id),
            style=Pack(flex=1, font_size=13.5),
        )
        self.input_app_name = toga.TextInput(
            value=recipe.app_name if recipe else "",
            style=Pack(flex=1, font_size=13.5),
        )
        self.select_strategy = toga.Selection(
            items=["hard_clone", "soft_clone"],
            value=recipe.strategy if recipe else "hard_clone",
            style=Pack(flex=1, font_size=12.0),
        )
        self.select_injection_strategy = toga.Selection(
            items=["auto", "dylib", "launcher"],
            value=recipe.injection_strategy if recipe and recipe.injection_strategy else "auto",
            style=Pack(flex=1, font_size=12.0),
        )
        self.switch_strip_sandbox = toga.Switch(
            text=t("win_recipe_strip_sandbox"),
            value=recipe.strip_sandbox if recipe else False,
            style=Pack(margin_bottom=4, font_size=13.5),
        )

        # Proxy Configuration
        proxy = recipe.proxy if recipe and recipe.proxy else ProxyConfig()
        self.switch_proxy = toga.Switch(
            text=t("win_recipe_enable_proxy"),
            value=proxy.enabled,
            style=Pack(margin_bottom=4, font_size=13.5),
        )
        self.select_proxy_type = toga.Selection(
            items=["http", "https", "socks5"],
            value=proxy.type,
            style=Pack(width=105, margin_right=8, font_size=12.0),
        )
        self.input_proxy_host = toga.TextInput(
            value=proxy.host,
            style=Pack(flex=1, margin_right=8, font_size=13.5),
        )
        self.input_proxy_port = toga.TextInput(
            value=str(proxy.port),
            style=Pack(width=90, font_size=13.5),
        )

        # Advanced inputs
        self._app_type_keys: list[AppType | None] = [None, "cocoa", "electron", "chromium", "firefox", "generic"]
        self._app_type_items: list[str] = [
            t("win_recipe_app_type_auto"),
            "Cocoa",
            "Electron",
            "Chromium",
            "Firefox",
            "Generic",
        ]
        curr_app_type = recipe.app_type if recipe else None
        curr_app_type_idx = (
            self._app_type_keys.index(curr_app_type)
            if curr_app_type in self._app_type_keys
            else 0
        )
        self.select_app_type = toga.Selection(
            items=self._app_type_items,
            value=self._app_type_items[curr_app_type_idx],
            style=Pack(flex=1, font_size=12.0),
        )

        self._lang_keys = list(SUPPORTED_LANGUAGES.keys())
        self._lang_display_items = [
            t(SUPPORTED_LANGUAGES[k]["label_key"]) for k in self._lang_keys
        ]
        curr_lang = recipe.language if recipe and recipe.language in self._lang_keys else "system"
        curr_lang_idx = self._lang_keys.index(curr_lang)
        self.select_language = toga.Selection(
            items=self._lang_display_items,
            value=self._lang_display_items[curr_lang_idx],
            style=Pack(flex=1, font_size=12.0),
        )

        self.input_env_injection = toga.MultilineTextInput(
            value=format_env_injection(recipe.environment_injection if recipe else {}),
            style=Pack(flex=1, height=85, font_size=12.0),
        )
        self.input_launch_args = toga.MultilineTextInput(
            value=format_list_lines(recipe.launch_args if recipe else []),
            style=Pack(flex=1, height=75, font_size=12.0),
        )
        self.input_symlink_whitelist = toga.MultilineTextInput(
            value=format_list_lines(recipe.symlink_whitelist if recipe else []),
            style=Pack(flex=1, height=65, font_size=12.0),
        )

        # Advanced Toggle & Box
        self.advanced_expanded: bool = False
        self.btn_toggle_advanced = toga.Button(
            t("win_recipe_btn_advanced_expand"),
            on_press=self.on_toggle_advanced,
            style=Pack(margin_top=14, margin_bottom=4, height=28, font_size=12.5, font_weight="bold"),
        )
        self.label_advanced_warning = toga.Label(
            t("win_recipe_advanced_warning"),
            style=Pack(margin_bottom=8, font_size=11.5, color=Theme.TEXT_MUTED),
        )
        self.advanced_box = self._build_advanced_box()

        # Action buttons
        self.btn_save = toga.Button(
            t("btn_save_recipe"),
            on_press=self.on_save_press,
            style=Pack(flex=1, margin_left=8, height=30, font_weight="bold", font_size=13),
        )
        self.btn_cancel = toga.Button(
            t("btn_cancel"),
            on_press=lambda widget: self.close(),
            style=Pack(flex=1, height=30, font_size=13),
        )
        self.btn_box = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin_top=20))
        self.btn_box.add(self.btn_cancel)
        self.btn_box.add(self.btn_save)

        self.form_box = self._build_form_box()
        self.scroll_container = toga.ScrollContainer(
            content=self.form_box,
            horizontal=False,
            style=Pack(flex=1),
        )
        self.content = self.scroll_container

    def _build_advanced_box(self) -> toga.Box:
        adv_box = toga.Box(style=Pack(direction=COLUMN, margin_top=4, margin_bottom=10))
        adv_box.add(self.label_advanced_warning)

        # App Type
        row_app_type = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin_bottom=8))
        row_app_type.add(toga.Label(t("win_recipe_app_type"), style=Pack(width=120, font_size=13, color=Theme.TEXT_PRIMARY)))
        row_app_type.add(self.select_app_type)
        adv_box.add(row_app_type)

        # Language
        row_lang = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin_bottom=10))
        row_lang.add(toga.Label(t("win_recipe_language"), style=Pack(width=120, font_size=13, color=Theme.TEXT_PRIMARY)))
        row_lang.add(self.select_language)
        adv_box.add(row_lang)

        # Environment Injection
        lbl_env = toga.Label(t("win_recipe_env_injection"), style=Pack(font_size=13, font_weight="bold", margin_bottom=2, color=Theme.TEXT_PRIMARY))
        lbl_env_hint = toga.Label(t("win_recipe_env_hint"), style=Pack(font_size=11, color=Theme.TEXT_MUTED, margin_bottom=4))
        adv_box.add(lbl_env)
        adv_box.add(lbl_env_hint)
        adv_box.add(self.input_env_injection)

        # Launch Args
        lbl_args = toga.Label(t("win_recipe_launch_args"), style=Pack(font_size=13, font_weight="bold", margin_top=10, margin_bottom=2, color=Theme.TEXT_PRIMARY))
        lbl_args_hint = toga.Label(t("win_recipe_launch_args_hint"), style=Pack(font_size=11, color=Theme.TEXT_MUTED, margin_bottom=4))
        adv_box.add(lbl_args)
        adv_box.add(lbl_args_hint)
        adv_box.add(self.input_launch_args)

        # Symlink Whitelist
        lbl_sym = toga.Label(t("win_recipe_symlink_whitelist"), style=Pack(font_size=13, font_weight="bold", margin_top=10, margin_bottom=2, color=Theme.TEXT_PRIMARY))
        lbl_sym_hint = toga.Label(t("win_recipe_symlink_hint"), style=Pack(font_size=11, color=Theme.TEXT_MUTED, margin_bottom=4))
        adv_box.add(lbl_sym)
        adv_box.add(lbl_sym_hint)
        adv_box.add(self.input_symlink_whitelist)

        return adv_box

    def _build_form_box(self) -> toga.Box:
        form_box = toga.Box(style=Pack(direction=COLUMN, margin=(18, 20, 18, 20)))

        # Bundle ID
        row1 = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin_bottom=8))
        row1.add(toga.Label(t("win_recipe_bundle_id"), style=Pack(width=120, font_size=13, color=Theme.TEXT_PRIMARY)))
        row1.add(self.input_bundle_id)
        form_box.add(row1)

        # App Name
        row2 = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin_bottom=8))
        row2.add(toga.Label(t("win_recipe_app_name"), style=Pack(width=120, font_size=13, color=Theme.TEXT_PRIMARY)))
        row2.add(self.input_app_name)
        form_box.add(row2)

        # Strategy
        row3 = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin_bottom=8))
        row3.add(toga.Label(t("win_recipe_strategy"), style=Pack(width=120, font_size=13, color=Theme.TEXT_PRIMARY)))
        row3.add(self.select_strategy)
        form_box.add(row3)

        # Injection Strategy
        row_inj = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin_bottom=8))
        row_inj.add(toga.Label(t("win_recipe_injection_strategy"), style=Pack(width=120, font_size=13, color=Theme.TEXT_PRIMARY)))
        row_inj.add(self.select_injection_strategy)
        form_box.add(row_inj)

        # Strip Sandbox
        row4 = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin_bottom=8))
        row4.add(toga.Label(t("win_recipe_sandbox"), style=Pack(width=120, font_size=13, color=Theme.TEXT_PRIMARY)))
        row4.add(self.switch_strip_sandbox)
        form_box.add(row4)

        # Proxy section
        proxy_heading = toga.Label(t("win_recipe_proxy_heading"), style=Pack(margin_top=12, margin_bottom=8, font_size=15, font_weight="bold", color=Theme.TEXT_PRIMARY))
        form_box.add(proxy_heading)

        row_proxy_switch = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin_bottom=6))
        row_proxy_switch.add(self.switch_proxy)
        form_box.add(row_proxy_switch)

        row_proxy_detail = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin_bottom=8))
        row_proxy_detail.add(toga.Label(t("win_edit_type_host_port"), style=Pack(width=120, font_size=13, color=Theme.TEXT_PRIMARY)))
        row_proxy_detail.add(self.select_proxy_type)
        row_proxy_detail.add(self.input_proxy_host)
        row_proxy_detail.add(self.input_proxy_port)
        form_box.add(row_proxy_detail)

        # Advanced toggle button
        form_box.add(self.btn_toggle_advanced)

        # Action Buttons
        form_box.add(self.btn_box)

        return form_box

    def on_toggle_advanced(self, widget: toga.Button) -> None:
        """Toggle collapsible advanced parameters container."""
        self.advanced_expanded = not self.advanced_expanded
        if self.advanced_expanded:
            self.btn_toggle_advanced.text = t("win_recipe_btn_advanced_collapse")
            # Insert before btn_box
            idx = self.form_box.children.index(self.btn_box)
            self.form_box.insert(idx, self.advanced_box)
        else:
            self.btn_toggle_advanced.text = t("win_recipe_btn_advanced_expand")
            if self.advanced_box in self.form_box.children:
                self.form_box.remove(self.advanced_box)

    def _get_selected_app_type(self) -> AppType | None:
        if self.select_app_type.value:
            try:
                idx = self._app_type_items.index(str(self.select_app_type.value))
                return self._app_type_keys[idx]
            except ValueError:
                pass
        return None

    def _get_selected_language(self) -> str:
        if self.select_language.value:
            try:
                idx = self._lang_display_items.index(str(self.select_language.value))
                return self._lang_keys[idx]
            except ValueError:
                pass
        return "system"

    def get_recipe_from_form(self) -> Recipe:
        port = 1080
        try:
            port = int(self.input_proxy_port.value)
        except ValueError:
            pass

        proxy = ProxyConfig(
            enabled=self.switch_proxy.value,
            type=str(self.select_proxy_type.value),
            host=self.input_proxy_host.value.strip() or "127.0.0.1",
            port=port,
        )

        env_dict, env_err = parse_env_injection(self.input_env_injection.value or "")
        if env_err:
            raise ValueError(env_err)

        launch_args = parse_list_lines(self.input_launch_args.value or "")
        symlink_whitelist = parse_list_lines(self.input_symlink_whitelist.value or "")
        app_type = self._get_selected_app_type()
        language = self._get_selected_language()

        injection_strategy = (
            str(self.select_injection_strategy.value)
            if self.select_injection_strategy.value
            else "auto"
        )

        return Recipe(
            bundle_id=self.input_bundle_id.value.strip(),
            app_name=self.input_app_name.value.strip(),
            strategy=str(self.select_strategy.value),
            strip_sandbox=self.switch_strip_sandbox.value,
            proxy=proxy,
            environment_injection=env_dict,
            symlink_whitelist=symlink_whitelist,
            launch_args=launch_args,
            language=language,
            app_type=app_type,
            injection_strategy=injection_strategy,
        )

    async def on_save_press(self, widget: toga.Button):
        try:
            recipe = self.get_recipe_from_form()
        except ValueError as err:
            await self.error_dialog(
                t("dialog_validation_error_title"),
                str(err),
            )
            return

        if not recipe.bundle_id or not recipe.app_name:
            await self.error_dialog(t("dialog_validation_error_title"), t("dialog_validation_error_msg"))
            return

        if self.on_save_callback:
            await self.on_save_callback(recipe)
        self.close()

