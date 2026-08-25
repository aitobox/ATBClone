"""Modern macOS-style compact Sidebar Navigation component."""

from typing import Callable, Dict
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER
from atbclone import __version__
from atbclone.core.i18n import t
from atbclone.core.resources import get_app_icon_path
from atbclone.gui.theme import Theme
from atbclone.gui.patch_cocoa import configure_cocoa_sidebar_active


class SidebarNav(toga.Box):
    """Sidebar navigation bar with branding, main sections, and bottom auxiliary items."""

    MAIN_NAV_KEYS = ["clones", "recipes", "probe", "doctor"]
    BOTTOM_NAV_KEYS = ["logs", "settings"]

    def __init__(self, on_select: Callable[[str], None], active_key: str = "clones"):
        super().__init__(style=Pack(direction=COLUMN, width=200, margin=0, background_color=Theme.BG_SIDEBAR))
        self.on_select = on_select
        self.active_key = active_key
        self.buttons: Dict[str, toga.Button] = {}

        # Brand header with logo icon
        header_box = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin=(20, 14, 16, 14)))

        logo_path = get_app_icon_path("png")
        if logo_path and logo_path.exists():
            try:
                logo_img = toga.Image(logo_path)
                logo_view = toga.ImageView(logo_img, style=Pack(width=28, height=28, margin_right=10))
                header_box.add(logo_view)
            except Exception:
                pass

        title_box = toga.Box(style=Pack(direction=COLUMN))
        title_label = toga.Label("ATBClone", style=Pack(font_weight="bold", font_size=15.5, color=Theme.TEXT_PRIMARY))
        ver_label = toga.Label(f"v{__version__} App Cloner", style=Pack(font_size=11, color=Theme.TEXT_TERTIARY, margin_top=2))
        title_box.add(title_label)
        title_box.add(ver_label)
        header_box.add(title_box)
        self.add(header_box)

        # Main Navigation Section
        self.main_box = toga.Box(style=Pack(direction=COLUMN, margin=(4, 10, 4, 10)))
        for key in self.MAIN_NAV_KEYS:
            btn = toga.Button(
                t(f"nav_{key}"),
                on_press=self._create_select_handler(key),
                style=Pack(margin_bottom=5, height=30, font_size=13),
            )
            self.buttons[key] = btn
            self.main_box.add(btn)
        self.add(self.main_box)

        # Flexible spacer to push bottom items down
        self.add(toga.Box(style=Pack(flex=1)))

        # Bottom Fixed Navigation Section
        self.bottom_box = toga.Box(style=Pack(direction=COLUMN, margin=(4, 10, 16, 10)))
        for key in self.BOTTOM_NAV_KEYS:
            btn = toga.Button(
                t(f"nav_{key}"),
                on_press=self._create_select_handler(key),
                style=Pack(margin_bottom=4, height=28, font_size=13),
            )
            self.buttons[key] = btn
            self.bottom_box.add(btn)
        self.add(self.bottom_box)

        self._update_button_styles()

    def retranslate(self):
        """Update button texts dynamically after language change."""
        for key in self.MAIN_NAV_KEYS + self.BOTTOM_NAV_KEYS:
            if key in self.buttons:
                self.buttons[key].text = t(f"nav_{key}")

    def _create_select_handler(self, key: str):
        return lambda widget: self.select_item(key)

    def select_item(self, key: str):
        self.active_key = key
        self._update_button_styles()
        if self.on_select:
            self.on_select(key)

    def _update_button_styles(self):
        for key, btn in self.buttons.items():
            is_active = (key == self.active_key)
            btn.style.font_weight = "bold" if is_active else "normal"
            try:
                native_btn = getattr(getattr(btn, "_impl", None), "native", None)
                configure_cocoa_sidebar_active(native_btn, is_active)
            except Exception:
                pass

