"""Modern macOS-style compact Sidebar Navigation component."""

import webbrowser
from typing import Callable, Dict
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER
from atbclone import __version__
from atbclone.core.i18n import t
from atbclone.core.resources import get_app_icon_path, get_cmder_icon_path
from atbclone.gui.theme import Theme
from atbclone.gui.patch_cocoa import configure_cocoa_sidebar_active, configure_cocoa_card


class SidebarNav(toga.Box):
    """Sidebar navigation bar with branding, main sections, and bottom auxiliary items."""

    MAIN_NAV_KEYS = ["clones", "recipes", "probe", "doctor"]
    BOTTOM_NAV_KEYS = ["logs", "settings"]
    CMDER_WEBSITE_URL = "https://cmder.aitobox.com"

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

        # Flexible spacer to push promo card towards center
        self.add(toga.Box(style=Pack(flex=1)))

        # Promo Card: ATBCmder promotion
        self.promo_card = self._create_promo_card()
        self.add(self.promo_card)

        # Flexible spacer between promo card and bottom navigation
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

    def _create_promo_card(self) -> toga.Box:
        card = toga.Box(
            style=Pack(
                direction=COLUMN,
                margin=(0, 10, 0, 10),
                background_color=Theme.BG_CARD,
            )
        )
        inner_box = toga.Box(style=Pack(direction=COLUMN, margin=(10, 10, 10, 10)))

        # Top row: App icon + Titles
        top_row = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin_bottom=6))

        cmder_icon_path = get_cmder_icon_path("png")
        if cmder_icon_path and cmder_icon_path.exists():
            try:
                icon_img = toga.Image(cmder_icon_path)
                icon_view = toga.ImageView(icon_img, style=Pack(width=28, height=28, margin_right=8))
                top_row.add(icon_view)
            except Exception:
                pass

        name_box = toga.Box(style=Pack(direction=COLUMN))
        title_row = toga.Box(style=Pack(direction=ROW, align_items=CENTER))
        self.promo_title_label = toga.Label(
            t("promo_cmder_title"),
            style=Pack(font_weight="bold", font_size=12.5, color=Theme.TEXT_PRIMARY),
        )
        self.promo_ad_badge = toga.Label(
            "[AD]",
            style=Pack(font_size=9.5, font_weight="bold", color=Theme.TEXT_TERTIARY, margin_left=4),
        )
        title_row.add(self.promo_title_label)
        title_row.add(self.promo_ad_badge)

        self.promo_subtitle_label = toga.Label(
            t("promo_cmder_subtitle"),
            style=Pack(font_size=10.5, color=Theme.TEXT_SECONDARY, margin_top=2),
        )
        name_box.add(title_row)
        name_box.add(self.promo_subtitle_label)
        top_row.add(name_box)
        inner_box.add(top_row)

        # Action Button: Visit Website
        self.promo_btn = toga.Button(
            t("promo_cmder_btn"),
            on_press=self._on_open_cmder_url,
            style=Pack(height=26, font_size=11.5, margin_top=4),
        )
        inner_box.add(self.promo_btn)
        card.add(inner_box)

        try:
            native_card = getattr(getattr(card, "_impl", None), "native", None)
            configure_cocoa_card(native_card, corner_radius=8.0, border_width=0.5)
        except Exception:
            pass

        return card

    def _on_open_cmder_url(self, widget: toga.Button):
        """Open official ATBCmder website in system default browser."""
        webbrowser.open(self.CMDER_WEBSITE_URL)

    def retranslate(self):
        """Update button texts dynamically after language change."""
        for key in self.MAIN_NAV_KEYS + self.BOTTOM_NAV_KEYS:
            if key in self.buttons:
                self.buttons[key].text = t(f"nav_{key}")
        if hasattr(self, "promo_title_label") and self.promo_title_label:
            self.promo_title_label.text = t("promo_cmder_title")
        if hasattr(self, "promo_subtitle_label") and self.promo_subtitle_label:
            self.promo_subtitle_label.text = t("promo_cmder_subtitle")
        if hasattr(self, "promo_btn") and self.promo_btn:
            self.promo_btn.text = t("promo_cmder_btn")

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

