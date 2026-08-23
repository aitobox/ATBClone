"""Application Prober View with modern card-based analysis."""

import asyncio
from pathlib import Path
from typing import Optional
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER

from atbclone.core.app_prober import ProbeResult
from atbclone.core.i18n import t
from atbclone.gui.services.probe_service import ProbeService
from atbclone.gui.services.recipe_service import RecipeService
from atbclone.gui.components.top_bar import TopHeaderBar
from atbclone.gui.components.wrapping_label import WrappingLabel
from atbclone.gui.theme import Theme


class ProbeView(toga.Box):
    """View providing deep binary, sandbox, and framework analysis for macOS applications."""

    def __init__(
        self,
        probe_service: Optional[ProbeService] = None,
        recipe_service: Optional[RecipeService] = None,
        app: Optional[toga.App] = None,
    ):
        super().__init__(style=Pack(direction=COLUMN, flex=1, background_color=Theme.BG_WINDOW))
        self.probe_service = probe_service or ProbeService()
        self.recipe_service = recipe_service or RecipeService()
        self.app_instance = app
        self.current_result: Optional[ProbeResult] = None

        # Top Header Bar
        self.top_bar = TopHeaderBar(
            title=t("nav_probe"),
            action_label=t("probe_btn_start"),
            on_action=lambda w: asyncio.create_task(self.do_probe()),
        )
        self.add(self.top_bar)

        content_box = toga.Box(style=Pack(direction=COLUMN, margin=(0, 24, 24, 24), flex=1))
        self.add(content_box)

        # ── Card 1: Target App Selection ───────────────────────────────────── #
        card_target = toga.Box(style=Pack(direction=COLUMN, margin_bottom=14, background_color=Theme.BG_CARD))
        inner_target = toga.Box(style=Pack(direction=COLUMN, margin=(14, 18, 14, 18)))
        inner_target.add(toga.Label(t("probe_card_target"), style=Pack(font_weight="bold", font_size=15, margin_bottom=12, color=Theme.TEXT_PRIMARY)))

        row_input = toga.Box(style=Pack(direction=ROW, align_items=CENTER))
        self.input_path = toga.TextInput(
            placeholder=t("probe_input_placeholder"),
            style=Pack(flex=1, margin_right=8, font_size=13.5),
        )
        self.btn_browse = toga.Button(t("btn_browse_app"), on_press=self.on_browse_press, style=Pack(width=100, height=30, font_size=13))
        row_input.add(self.input_path)
        row_input.add(self.btn_browse)
        inner_target.add(row_input)
        card_target.add(inner_target)
        content_box.add(card_target)

        # ── Card 2: Analysis Results Panel ─────────────────────────────────── #
        self.card_results = toga.Box(style=Pack(direction=COLUMN, margin_bottom=14, background_color=Theme.BG_CARD))
        inner_results = toga.Box(style=Pack(direction=COLUMN, margin=(14, 18, 14, 18)))
        inner_results.add(toga.Label(t("probe_card_results"), style=Pack(font_weight="bold", font_size=15, margin_bottom=12, color=Theme.TEXT_PRIMARY)))

        self.label_app_name = WrappingLabel(f"{t('probe_row_app_name')}: —", style=Pack(font_size=13, color=Theme.TEXT_MUTED, margin_bottom=5))
        self.label_bundle_id = WrappingLabel(f"{t('probe_row_bundle_id')}: —", style=Pack(font_size=13, color=Theme.TEXT_MUTED, margin_bottom=5))
        self.label_sandbox = WrappingLabel(f"{t('probe_row_sandbox')}: —", style=Pack(font_size=13, color=Theme.TEXT_MUTED, margin_bottom=5))
        self.label_frameworks = WrappingLabel(f"{t('probe_row_frameworks')}: —", style=Pack(font_size=13, color=Theme.TEXT_MUTED, margin_bottom=5))
        self.label_reason = WrappingLabel(f"{t('probe_row_reason')}: —", style=Pack(font_size=13, color=Theme.TEXT_MUTED, margin_bottom=5))
        self.label_strategy = WrappingLabel(f"{t('probe_row_strategy')}: —", style=Pack(font_weight="bold", font_size=13.5, color=Theme.ACCENT_BLUE, margin_bottom=12))

        inner_results.add(self.label_app_name)
        inner_results.add(self.label_bundle_id)
        inner_results.add(self.label_sandbox)
        inner_results.add(self.label_frameworks)
        inner_results.add(self.label_reason)
        inner_results.add(self.label_strategy)

        # Action: Save as custom recipe
        self.btn_save_recipe = toga.Button(
            t("probe_btn_save_recipe"),
            on_press=lambda w: asyncio.create_task(self.save_probed_recipe()),
            enabled=False,
            style=Pack(font_weight="bold", font_size=13, height=30),
        )
        inner_results.add(self.btn_save_recipe)
        self.card_results.add(inner_results)
        content_box.add(self.card_results)

    async def on_browse_press(self, widget: toga.Button):
        if self.app_instance and hasattr(self.app_instance, "main_window"):
            try:
                selected_file = await self.app_instance.main_window.open_file_dialog(
                    title=t("dialog_select_app_title"),
                    file_types=["app"],
                    initial_directory=Path("/Applications"),
                )
                if selected_file:
                    self.input_path.value = str(selected_file)
            except Exception:
                pass

    async def do_probe(self):
        path_str = self.input_path.value.strip()
        if not path_str:
            if self.app_instance and hasattr(self.app_instance, "main_window"):
                await self.app_instance.main_window.error_dialog(t("dialog_info_title"), t("dialog_probe_input_required"))
            return

        try:
            res = await self.probe_service.probe_app(Path(path_str))
            self.current_result = res

            self.label_app_name.text = f"{t('probe_row_app_name')}: {res.app_info.app_name}"
            self.label_bundle_id.text = f"{t('probe_row_bundle_id')}: {res.app_info.bundle_id}"
            sandbox_str = t("probe_sandbox_yes") if res.has_sandbox else t("probe_sandbox_no")
            self.label_sandbox.text = f"{t('probe_row_sandbox')}: {sandbox_str}"
            fw_str = ", ".join(res.frameworks) if res.frameworks else "Native AppKit"
            self.label_frameworks.text = f"{t('probe_row_frameworks')}: {fw_str}"
            self.label_reason.text = f"{t('probe_row_reason')}: {res.reason}"
            strat_label = t("card_strategy_hard") if res.strategy == "hard_clone" else t("card_strategy_soft")
            self.label_strategy.text = f"{t('probe_row_strategy')}: {strat_label}"

            self.btn_save_recipe.enabled = True
            self.btn_save_recipe.text = t("probe_btn_save_recipe")
        except Exception as e:
            if self.app_instance and hasattr(self.app_instance, "main_window"):
                await self.app_instance.main_window.error_dialog(t("dialog_probe_failed_title"), str(e))

    async def save_probed_recipe(self):
        if not self.current_result:
            return
        await self.recipe_service.save_custom_recipe(self.current_result.recipe)
        self.btn_save_recipe.text = t("probe_saved_success")
        self.btn_save_recipe.enabled = False

