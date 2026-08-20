"""Application Prober View with modern card-based analysis."""

import asyncio
from pathlib import Path
from typing import Optional
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER

from atbclone.core.app_prober import ProbeResult
from atbclone.gui.services.probe_service import ProbeService
from atbclone.gui.services.recipe_service import RecipeService
from atbclone.gui.components.top_bar import TopHeaderBar
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
            title="应用探测",
            action_label="🔍 开始探测",
            on_action=lambda w: asyncio.create_task(self.do_probe()),
        )
        self.add(self.top_bar)

        content_box = toga.Box(style=Pack(direction=COLUMN, margin=(0, 20, 20, 20), flex=1))
        self.add(content_box)

        # ── Card 1: Target App Selection ───────────────────────────────────── #
        card_target = toga.Box(style=Pack(direction=COLUMN, margin_bottom=15, margin=10, background_color=Theme.BG_CARD))
        card_target.add(toga.Label("🎯 选择目标应用", style=Pack(font_weight="bold", font_size=14, margin_bottom=8, color=Theme.TEXT_PRIMARY)))

        row_input = toga.Box(style=Pack(direction=ROW, align_items=CENTER))
        self.input_path = toga.TextInput(
            placeholder="选择或输入应用路径，如 /Applications/Google Chrome.app",
            style=Pack(flex=1, margin_right=6),
        )
        self.btn_browse = toga.Button("📂 浏览应用...", on_press=self.on_browse_press, style=Pack(width=110))
        row_input.add(self.input_path)
        row_input.add(self.btn_browse)
        card_target.add(row_input)
        content_box.add(card_target)

        # ── Card 2: Analysis Results Panel ─────────────────────────────────── #
        self.card_results = toga.Box(style=Pack(direction=COLUMN, margin=10, background_color=Theme.BG_CARD))
        self.card_results.add(toga.Label("📊 探测分析结果", style=Pack(font_weight="bold", font_size=14, margin_bottom=10, color=Theme.TEXT_PRIMARY)))

        self.label_app_name = toga.Label("应用名称: —", style=Pack(font_size=12, margin_bottom=4))
        self.label_bundle_id = toga.Label("Bundle ID: —", style=Pack(font_size=12, margin_bottom=4))
        self.label_sandbox = toga.Label("Sandbox 沙盒隔离: —", style=Pack(font_size=12, margin_bottom=4))
        self.label_frameworks = toga.Label("底层技术框架: —", style=Pack(font_size=12, margin_bottom=4))
        self.label_reason = toga.Label("策略推导原因: —", style=Pack(font_size=12, margin_bottom=6))
        self.label_strategy = toga.Label("推荐克隆策略: —", style=Pack(font_weight="bold", font_size=13, color=Theme.ACCENT_BLUE, margin_bottom=12))

        self.card_results.add(self.label_app_name)
        self.card_results.add(self.label_bundle_id)
        self.card_results.add(self.label_sandbox)
        self.card_results.add(self.label_frameworks)
        self.card_results.add(self.label_reason)
        self.card_results.add(self.label_strategy)

        # Action: Save as custom recipe
        self.btn_save_recipe = toga.Button(
            "💾 保存至自定义配方库",
            on_press=lambda w: asyncio.create_task(self.save_probed_recipe()),
            enabled=False,
            style=Pack(font_weight="bold", height=32),
        )
        self.card_results.add(self.btn_save_recipe)
        content_box.add(self.card_results)

    async def on_browse_press(self, widget: toga.Button):
        if self.app_instance and hasattr(self.app_instance, "main_window"):
            try:
                selected_file = await self.app_instance.main_window.open_file_dialog(
                    title="选择要探测的 macOS 应用程序",
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
                await self.app_instance.main_window.error_dialog("提示", "请先选择或输入应用程序路径。")
            return

        try:
            res = await self.probe_service.probe_app(Path(path_str))
            self.current_result = res

            self.label_app_name.text = f"应用名称: {res.app_info.app_name}"
            self.label_bundle_id.text = f"Bundle ID: {res.app_info.bundle_id}"
            self.label_sandbox.text = f"Sandbox 沙盒隔离: {'是 (已启用)' if res.has_sandbox else '否 (无沙盒)'}"
            self.label_frameworks.text = f"底层技术框架: {', '.join(res.frameworks) if res.frameworks else 'Native AppKit'}"
            self.label_reason.text = f"策略推导原因: {res.reason}"
            strat_label = "物理完整克隆 (Hard Clone)" if res.strategy == "hard_clone" else "软包装克隆 (Soft Clone)"
            self.label_strategy.text = f"推荐克隆策略: {strat_label}"

            self.btn_save_recipe.enabled = True
            self.btn_save_recipe.text = "💾 保存至自定义配方库"
        except Exception as e:
            if self.app_instance and hasattr(self.app_instance, "main_window"):
                await self.app_instance.main_window.error_dialog("探测失败", str(e))

    async def save_probed_recipe(self):
        if not self.current_result:
            return
        await self.recipe_service.save_custom_recipe(self.current_result.recipe)
        self.btn_save_recipe.text = "✅ 已成功保存至配方库！"
        self.btn_save_recipe.enabled = False
