"""Modern macOS-style compact Sidebar Navigation component."""

from typing import Callable, Dict
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER
from atbclone import __version__
from atbclone.gui.theme import Theme


class SidebarNav(toga.Box):
    """Sidebar navigation bar with branding, main sections, and bottom auxiliary items."""

    MAIN_NAV_ITEMS = [
        ("clones", "📱 我的分身"),
        ("recipes", "📖 预设配方"),
        ("probe", "🔍 应用探测"),
        ("doctor", "🩺 环境自检"),
    ]

    BOTTOM_NAV_ITEMS = [
        ("logs", "📋 运行日志"),
        ("settings", "⚙️ 全局设置"),
    ]

    def __init__(self, on_select: Callable[[str], None], active_key: str = "clones"):
        super().__init__(style=Pack(direction=COLUMN, width=180, margin=0, background_color=Theme.BG_SIDEBAR))
        self.on_select = on_select
        self.active_key = active_key
        self.buttons: Dict[str, toga.Button] = {}

        # Brand header
        header_box = toga.Box(style=Pack(direction=COLUMN, margin=(16, 12, 12, 12)))
        title_label = toga.Label("🚀 ATBClone", style=Pack(font_weight="bold", font_size=16, color=Theme.TEXT_PRIMARY))
        ver_label = toga.Label(f"v{__version__} App Cloner", style=Pack(font_size=10, color=Theme.TEXT_MUTED, margin_top=2))
        header_box.add(title_label)
        header_box.add(ver_label)
        self.add(header_box)

        # Main Navigation Section
        self.main_box = toga.Box(style=Pack(direction=COLUMN, margin=(4, 8, 4, 8)))
        for key, title in self.MAIN_NAV_ITEMS:
            btn = toga.Button(
                title,
                on_press=self._create_select_handler(key),
                style=Pack(margin_bottom=4, height=32),
            )
            self.buttons[key] = btn
            self.main_box.add(btn)
        self.add(self.main_box)

        # Flexible spacer to push bottom items down
        self.add(toga.Box(style=Pack(flex=1)))

        # Bottom Fixed Navigation Section
        self.bottom_box = toga.Box(style=Pack(direction=COLUMN, margin=(4, 8, 12, 8)))
        for key, title in self.BOTTOM_NAV_ITEMS:
            btn = toga.Button(
                title,
                on_press=self._create_select_handler(key),
                style=Pack(margin_bottom=4, height=30),
            )
            self.buttons[key] = btn
            self.bottom_box.add(btn)
        self.add(self.bottom_box)

        self._update_button_styles()

    def _create_select_handler(self, key: str):
        return lambda widget: self.select_item(key)

    def select_item(self, key: str):
        self.active_key = key
        self._update_button_styles()
        if self.on_select:
            self.on_select(key)

    def _update_button_styles(self):
        for key, btn in self.buttons.items():
            if key == self.active_key:
                btn.style.font_weight = "bold"
            else:
                btn.style.font_weight = "normal"
