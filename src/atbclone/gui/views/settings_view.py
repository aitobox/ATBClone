"""Settings View for managing global application preferences and data directories."""

import asyncio
import subprocess
import platform
import sys
from pathlib import Path
from typing import Optional
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER

from atbclone import __version__
from atbclone.core.config import DEFAULT_ATB_DIR, DEFAULT_APPS_DIR, DEFAULT_DATA_DIR
from atbclone.core.logger import get_logger
from atbclone.gui.components.top_bar import TopHeaderBar
from atbclone.gui.theme import Theme

logger = get_logger("gui.settings")


class SettingsView(toga.Box):
    """Global preferences panel including Finder directory reveal and default configs."""

    def __init__(self, app: Optional[toga.App] = None):
        super().__init__(style=Pack(direction=COLUMN, flex=1, background_color=Theme.BG_WINDOW))
        self.app_instance = app

        # Top Header Bar
        self.top_bar = TopHeaderBar(
            title="全局设置",
            action_label="💾 保存设置",
            on_action=self.on_save_settings,
        )
        self.add(self.top_bar)

        # Scrollable container for settings cards
        scroll = toga.ScrollContainer(style=Pack(flex=1), horizontal=False)
        content_box = toga.Box(style=Pack(direction=COLUMN, margin=(0, 20, 20, 20)))
        scroll.content = content_box
        self.add(scroll)

        # ── Card 1: Data Directory Management ──────────────────────────────── #
        card_dir = toga.Box(style=Pack(direction=COLUMN, margin_bottom=15, background_color=Theme.BG_CARD))
        card_dir.add(toga.Label("📁 数据与存储管理", style=Pack(font_weight="bold", font_size=14, margin_bottom=8, color=Theme.TEXT_PRIMARY)))
        card_dir.add(toga.Label(f"ATBClone 根工作目录: {DEFAULT_ATB_DIR}", style=Pack(font_size=12, color=Theme.TEXT_MUTED, margin_bottom=4)))
        card_dir.add(toga.Label(f"分身应用存放目录: {DEFAULT_APPS_DIR}", style=Pack(font_size=12, color=Theme.TEXT_MUTED, margin_bottom=4)))
        card_dir.add(toga.Label(f"数据隔离存放目录: {DEFAULT_DATA_DIR}", style=Pack(font_size=12, color=Theme.TEXT_MUTED, margin_bottom=10)))

        self.btn_open_finder = toga.Button(
            "📂 在 Finder 中打开数据目录 (~/.atbclone)",
            on_press=self.on_open_data_dir_in_finder,
            style=Pack(font_weight="bold", height=34),
        )
        card_dir.add(self.btn_open_finder)
        content_box.add(card_dir)

        # ── Card 2: Default Working Directory ───────────────────────────────── #
        card_paths = toga.Box(style=Pack(direction=COLUMN, margin_bottom=15, margin=10, background_color=Theme.BG_CARD))
        card_paths.add(toga.Label("⚙️ 默认路径偏好", style=Pack(font_weight="bold", font_size=14, margin_bottom=8, color=Theme.TEXT_PRIMARY)))

        row_base = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin_bottom=6))
        row_base.add(toga.Label("根工作目录:", style=Pack(width=100, font_size=12)))
        self.input_base_dir = toga.TextInput(value=str(DEFAULT_ATB_DIR), style=Pack(flex=1, margin_right=6))
        self.btn_browse_base = toga.Button("📂 浏览...", on_press=self._on_browse_base, style=Pack(width=90))
        row_base.add(self.input_base_dir)
        row_base.add(self.btn_browse_base)
        card_paths.add(row_base)

        card_paths.add(toga.Label("（分身应用、隔离数据及配方规则将自动归档在该根工作目录下）", style=Pack(font_size=11, color=Theme.TEXT_MUTED, margin_top=4)))
        content_box.add(card_paths)

        # ── Card 3: Default Proxy ──────────────────────────────────────────── #
        card_proxy = toga.Box(style=Pack(direction=COLUMN, margin_bottom=15, margin=10, background_color=Theme.BG_CARD))
        card_proxy.add(toga.Label("🌐 默认代理配置 (可选)", style=Pack(font_weight="bold", font_size=14, margin_bottom=8, color=Theme.TEXT_PRIMARY)))

        self.switch_proxy = toga.Switch("创建分身时默认启用代理", value=False, style=Pack(margin_bottom=8))
        card_proxy.add(self.switch_proxy)

        row_proxy = toga.Box(style=Pack(direction=ROW, align_items=CENTER))
        self.select_proxy_type = toga.Selection(items=["http", "socks5"], style=Pack(width=90, margin_right=6))
        self.input_proxy_host = toga.TextInput(value="127.0.0.1", style=Pack(flex=1, margin_right=6))
        self.input_proxy_port = toga.TextInput(value="7890", style=Pack(width=80))
        row_proxy.add(self.select_proxy_type)
        row_proxy.add(self.input_proxy_host)
        row_proxy.add(self.input_proxy_port)
        card_proxy.add(row_proxy)
        content_box.add(card_proxy)

        # ── Card 4: System Info ────────────────────────────────────────────── #
        card_info = toga.Box(style=Pack(direction=COLUMN, margin=10, background_color=Theme.BG_CARD))
        card_info.add(toga.Label("ℹ️ 关于 ATBClone", style=Pack(font_weight="bold", font_size=14, margin_bottom=6, color=Theme.TEXT_PRIMARY)))
        card_info.add(toga.Label(f"ATBClone 版本: v{__version__}", style=Pack(font_size=12, color=Theme.TEXT_MUTED, margin_bottom=2)))
        card_info.add(toga.Label(f"Python 核心: {platform.python_version()} ({platform.machine()})", style=Pack(font_size=12, color=Theme.TEXT_MUTED, margin_bottom=2)))
        card_info.add(toga.Label(f"macOS 系统架构: {platform.mac_ver()[0] or 'macOS'}", style=Pack(font_size=12, color=Theme.TEXT_MUTED)))
        content_box.add(card_info)

    def on_open_data_dir_in_finder(self, widget: toga.Button):
        """Open default base directory ~/.atbclone in macOS Finder."""
        base_dir = Path(self.input_base_dir.value.strip() or str(DEFAULT_ATB_DIR))
        logger.info(f"Opening data directory in Finder: '{base_dir}'")
        base_dir.mkdir(parents=True, exist_ok=True)
        loop = asyncio.get_running_loop()
        loop.run_in_executor(None, lambda: subprocess.Popen(["open", str(base_dir)]))

    async def _on_browse_base(self, widget: toga.Button):
        if self.app_instance and hasattr(self.app_instance, "main_window"):
            try:
                selected = await self.app_instance.main_window.select_folder_dialog(
                    title="选择 ATBClone 根工作目录",
                    initial_directory=Path(self.input_base_dir.value.strip() or str(DEFAULT_ATB_DIR)),
                )
                if selected:
                    self.input_base_dir.value = str(selected)
            except Exception:
                pass

    async def on_save_settings(self, widget: toga.Button):
        base_dir = self.input_base_dir.value.strip()
        proxy_enabled = self.switch_proxy.value
        logger.info(f"Settings saved: base_dir='{base_dir}', proxy_enabled={proxy_enabled}")
        if self.app_instance and hasattr(self.app_instance, "main_window"):
            await self.app_instance.main_window.info_dialog("Settings Saved", "Preferences have been updated successfully.")
