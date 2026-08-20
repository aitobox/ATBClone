"""Recipe Editor Window."""

from typing import Callable, Coroutine, Any
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

from atbclone.core.i18n import t
from atbclone.recipes.models import ProxyConfig, Recipe


class RecipeEditWindow(toga.Window):
    def __init__(
        self,
        title: str = "Edit Recipe",
        recipe: Recipe | None = None,
        on_save: Callable[[Recipe], Coroutine[Any, Any, None]] | None = None,
    ):
        super().__init__(title=title, size=(500, 520))
        self.original_recipe = recipe
        self.on_save_callback = on_save

        self.input_bundle_id = toga.TextInput(
            value=recipe.bundle_id if recipe else "",
            style=Pack(flex=1),
        )
        self.input_app_name = toga.TextInput(
            value=recipe.app_name if recipe else "",
            style=Pack(flex=1),
        )
        self.select_strategy = toga.Selection(
            items=["hard_clone", "soft_clone"],
            value=recipe.strategy if recipe else "hard_clone",
            style=Pack(flex=1),
        )
        self.switch_strip_sandbox = toga.Switch(
            text=t("win_recipe_strip_sandbox"),
            value=recipe.strip_sandbox if recipe else False,
            style=Pack(margin_top=5),
        )

        # Proxy Configuration
        proxy = recipe.proxy if recipe and recipe.proxy else ProxyConfig()
        self.switch_proxy = toga.Switch(
            text=t("win_recipe_enable_proxy"),
            value=proxy.enabled,
            style=Pack(margin_top=5),
        )
        self.select_proxy_type = toga.Selection(
            items=["http", "socks5"],
            value=proxy.type,
            style=Pack(width=100),
        )
        self.input_proxy_host = toga.TextInput(
            value=proxy.host,
            style=Pack(flex=1),
        )
        self.input_proxy_port = toga.TextInput(
            value=str(proxy.port),
            style=Pack(width=80),
        )

        # Action buttons
        self.btn_save = toga.Button(
            t("btn_save_recipe"),
            on_press=self.on_save_press,
            style=Pack(flex=1, margin=5),
        )
        self.btn_cancel = toga.Button(
            t("btn_cancel"),
            on_press=lambda widget: self.close(),
            style=Pack(flex=1, margin=5),
        )

        self.content = self._build_content()

    def _build_content(self) -> toga.Box:
        form_box = toga.Box(style=Pack(direction=COLUMN, margin=15))

        # Bundle ID
        row1 = toga.Box(style=Pack(direction=ROW, margin=5))
        row1.add(toga.Label(t("win_recipe_bundle_id"), style=Pack(width=120)))
        row1.add(self.input_bundle_id)
        form_box.add(row1)

        # App Name
        row2 = toga.Box(style=Pack(direction=ROW, margin=5))
        row2.add(toga.Label(t("win_recipe_app_name"), style=Pack(width=120)))
        row2.add(self.input_app_name)
        form_box.add(row2)

        # Strategy
        row3 = toga.Box(style=Pack(direction=ROW, margin=5))
        row3.add(toga.Label(t("win_recipe_strategy"), style=Pack(width=120)))
        row3.add(self.select_strategy)
        form_box.add(row3)

        # Strip Sandbox
        row4 = toga.Box(style=Pack(direction=ROW, margin=5))
        row4.add(toga.Label(t("win_recipe_sandbox"), style=Pack(width=120)))
        row4.add(self.switch_strip_sandbox)
        form_box.add(row4)

        # Proxy section
        proxy_heading = toga.Label(t("win_recipe_proxy_heading"), style=Pack(margin_top=15, font_weight="bold"))
        form_box.add(proxy_heading)

        row_proxy_switch = toga.Box(style=Pack(direction=ROW, margin=5))
        row_proxy_switch.add(self.switch_proxy)
        form_box.add(row_proxy_switch)

        row_proxy_detail = toga.Box(style=Pack(direction=ROW, margin=5))
        row_proxy_detail.add(toga.Label(t("win_edit_type_host_port"), style=Pack(width=120)))
        row_proxy_detail.add(self.select_proxy_type)
        row_proxy_detail.add(self.input_proxy_host)
        row_proxy_detail.add(self.input_proxy_port)
        form_box.add(row_proxy_detail)

        # Button row
        btn_box = toga.Box(style=Pack(direction=ROW, margin_top=20))
        btn_box.add(self.btn_cancel)
        btn_box.add(self.btn_save)
        form_box.add(btn_box)

        return form_box

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

        return Recipe(
            bundle_id=self.input_bundle_id.value.strip(),
            app_name=self.input_app_name.value.strip(),
            strategy=str(self.select_strategy.value),
            strip_sandbox=self.switch_strip_sandbox.value,
            proxy=proxy,
        )

    async def on_save_press(self, widget: toga.Button):
        recipe = self.get_recipe_from_form()
        if not recipe.bundle_id or not recipe.app_name:
            await self.error_dialog(t("dialog_validation_error_title"), t("dialog_validation_error_msg"))
            return

        if self.on_save_callback:
            await self.on_save_callback(recipe)
        self.close()

