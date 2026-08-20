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
from atbclone.core.config import (
    DEFAULT_ATB_DIR,
    DEFAULT_APPS_DIR,
    DEFAULT_DATA_DIR,
    get_config_value,
    set_config_value,
)
from atbclone.core.i18n import (
    t,
    SUPPORTED_LANGUAGES_MAP,
    get_configured_language,
    save_configured_language,
    set_language,
    detect_system_language,
)
from atbclone.core.logger import get_logger
from atbclone.gui.components.top_bar import TopHeaderBar
from atbclone.gui.theme import Theme
from atbclone.gui.windows.release_notes import ReleaseNotesWindow

logger = get_logger("gui.settings")


class SettingsView(toga.Box):
    """Global preferences panel including Finder directory reveal, language preferences, and default configs."""

    def __init__(self, app: Optional[toga.App] = None):
        super().__init__(style=Pack(direction=COLUMN, flex=1, background_color=Theme.BG_WINDOW))
        self.app_instance = app

        # Top Header Bar
        self.top_bar = TopHeaderBar(
            title=t("nav_settings"),
            action_label=t("settings_btn_save"),
            on_action=self.on_save_settings,
        )
        self.add(self.top_bar)

        # Scrollable container for settings cards
        scroll = toga.ScrollContainer(style=Pack(flex=1), horizontal=False)
        content_box = toga.Box(style=Pack(direction=COLUMN, margin=(0, 20, 20, 20)))
        scroll.content = content_box
        self.add(scroll)

        # ── Card 1: Language Preference ────────────────────────────────────── #
        card_lang = toga.Box(style=Pack(direction=COLUMN, margin_bottom=15, background_color=Theme.BG_CARD))
        card_lang.add(toga.Label(t("settings_card_language"), style=Pack(font_weight="bold", font_size=14, margin_bottom=8, color=Theme.TEXT_PRIMARY)))

        row_lang = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin_bottom=6))
        row_lang.add(toga.Label(t("settings_label_language"), style=Pack(width=100, font_size=12)))

        lang_items = list(SUPPORTED_LANGUAGES_MAP.values())
        current_cfg = get_configured_language()
        current_item = SUPPORTED_LANGUAGES_MAP.get(current_cfg, lang_items[0])

        self.select_language = toga.Selection(
            items=lang_items,
            value=current_item,
            on_change=self._on_language_changed,
            style=Pack(flex=1),
        )
        row_lang.add(self.select_language)
        card_lang.add(row_lang)
        card_lang.add(toga.Label(t("settings_hint_language"), style=Pack(font_size=11, color=Theme.TEXT_MUTED, margin_top=2)))
        content_box.add(card_lang)

        # ── Card 2: Data Directory Management ──────────────────────────────── #
        card_dir = toga.Box(style=Pack(direction=COLUMN, margin_bottom=15, background_color=Theme.BG_CARD))
        card_dir.add(toga.Label(t("settings_card_storage"), style=Pack(font_weight="bold", font_size=14, margin_bottom=8, color=Theme.TEXT_PRIMARY)))
        card_dir.add(toga.Label(t("settings_label_root_dir", path=str(DEFAULT_ATB_DIR)), style=Pack(font_size=12, color=Theme.TEXT_MUTED, margin_bottom=4)))
        card_dir.add(toga.Label(t("settings_label_apps_dir", path=str(DEFAULT_APPS_DIR)), style=Pack(font_size=12, color=Theme.TEXT_MUTED, margin_bottom=4)))
        card_dir.add(toga.Label(t("settings_label_data_dir", path=str(DEFAULT_DATA_DIR)), style=Pack(font_size=12, color=Theme.TEXT_MUTED, margin_bottom=10)))

        self.btn_open_finder = toga.Button(
            t("settings_btn_open_finder"),
            on_press=self.on_open_data_dir_in_finder,
            style=Pack(font_weight="bold", height=34),
        )
        card_dir.add(self.btn_open_finder)
        content_box.add(card_dir)

        # ── Card 3: Default Working Directory ───────────────────────────────── #
        card_paths = toga.Box(style=Pack(direction=COLUMN, margin_bottom=15, margin=10, background_color=Theme.BG_CARD))
        card_paths.add(toga.Label(t("settings_card_paths"), style=Pack(font_weight="bold", font_size=14, margin_bottom=8, color=Theme.TEXT_PRIMARY)))

        row_base = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin_bottom=6))
        row_base.add(toga.Label(t("settings_label_root"), style=Pack(width=100, font_size=12)))
        self.input_base_dir = toga.TextInput(value=str(DEFAULT_ATB_DIR), style=Pack(flex=1, margin_right=6))
        self.btn_browse_base = toga.Button(t("btn_browse_dir"), on_press=self._on_browse_base, style=Pack(width=90))
        row_base.add(self.input_base_dir)
        row_base.add(self.btn_browse_base)
        card_paths.add(row_base)

        card_paths.add(toga.Label(t("settings_hint_paths"), style=Pack(font_size=11, color=Theme.TEXT_MUTED, margin_top=4)))
        content_box.add(card_paths)

        # ── Card 4: Default Proxy ──────────────────────────────────────────── #
        card_proxy = toga.Box(style=Pack(direction=COLUMN, margin_bottom=15, margin=10, background_color=Theme.BG_CARD))
        card_proxy.add(toga.Label(t("settings_card_proxy"), style=Pack(font_weight="bold", font_size=14, margin_bottom=8, color=Theme.TEXT_PRIMARY)))

        self.switch_proxy = toga.Switch(t("settings_switch_proxy_default"), value=False, style=Pack(margin_bottom=8))
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

        # ── Card 5: Window & Tray Preferences ──────────────────────────────── #
        card_tray = toga.Box(style=Pack(direction=COLUMN, margin_bottom=15, margin=10, background_color=Theme.BG_CARD))
        card_tray.add(toga.Label(t("settings_card_tray"), style=Pack(font_weight="bold", font_size=14, margin_bottom=8, color=Theme.TEXT_PRIMARY)))

        current_tray_cfg = bool(get_config_value("minimize_to_tray", False))
        self.switch_minimize_to_tray = toga.Switch(
            t("settings_switch_minimize_to_tray"),
            value=current_tray_cfg,
            on_change=self._on_minimize_to_tray_changed,
            style=Pack(margin_bottom=4),
        )
        card_tray.add(self.switch_minimize_to_tray)
        card_tray.add(toga.Label(t("settings_hint_minimize_to_tray"), style=Pack(font_size=11, color=Theme.TEXT_MUTED)))
        content_box.add(card_tray)

        # ── Card 6: System Info ────────────────────────────────────────────── #
        card_info = toga.Box(style=Pack(direction=COLUMN, margin=10, background_color=Theme.BG_CARD))
        card_info.add(toga.Label(t("settings_card_about"), style=Pack(font_weight="bold", font_size=14, margin_bottom=6, color=Theme.TEXT_PRIMARY)))
        card_info.add(toga.Label(t("settings_label_version", version=__version__), style=Pack(font_size=12, color=Theme.TEXT_MUTED, margin_bottom=2)))
        card_info.add(toga.Label(t("settings_label_python", version=platform.python_version(), arch=platform.machine()), style=Pack(font_size=12, color=Theme.TEXT_MUTED, margin_bottom=2)))
        card_info.add(toga.Label(t("settings_label_os", os_ver=platform.mac_ver()[0] or 'macOS'), style=Pack(font_size=12, color=Theme.TEXT_MUTED, margin_bottom=8)))

        self.btn_release_notes = toga.Button(
            t("settings_btn_release_notes"),
            on_press=self.on_open_release_notes,
            style=Pack(height=32, margin_top=4),
        )
        card_info.add(self.btn_release_notes)
        content_box.add(card_info)

        self.release_notes_window: Optional[ReleaseNotesWindow] = None

    def on_open_release_notes(self, widget: toga.Button):
        """Open or focus the ReleaseNotesWindow."""
        self.release_notes_window = ReleaseNotesWindow()
        self.release_notes_window.show()

    def _on_language_changed(self, widget: toga.Selection):
        if widget.value is None:
            return
        selected_label = str(widget.value)
        selected_code = "auto"
        for code, label in SUPPORTED_LANGUAGES_MAP.items():
            if label == selected_label or selected_label.startswith(code + " ") or (code == "auto" and "auto" in selected_label.lower()):
                selected_code = code
                break

        save_configured_language(selected_code)
        if selected_code == "auto":
            detected = detect_system_language()
            set_language(detected)
        else:
            set_language(selected_code)

        if self.app_instance and hasattr(self.app_instance, "retranslate_ui"):
            self.app_instance.retranslate_ui()

    def _on_minimize_to_tray_changed(self, widget: toga.Switch) -> None:
        val = bool(widget.value)
        set_config_value("minimize_to_tray", val)
        logger.info(f"Minimize to tray preference changed to {val}")
        if self.app_instance and hasattr(self.app_instance, "tray_service") and self.app_instance.tray_service:
            if val:
                self.app_instance.tray_service.enable()
            else:
                self.app_instance.tray_service.disable()

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
                    title=t("dialog_select_root_dir_title"),
                    initial_directory=Path(self.input_base_dir.value.strip() or str(DEFAULT_ATB_DIR)),
                )
                if selected:
                    self.input_base_dir.value = str(selected)
            except Exception:
                pass

    async def on_save_settings(self, widget: toga.Button):
        base_dir = self.input_base_dir.value.strip()
        proxy_enabled = self.switch_proxy.value
        minimize_to_tray = self.switch_minimize_to_tray.value
        set_config_value("minimize_to_tray", bool(minimize_to_tray))
        logger.info(f"Settings saved: base_dir='{base_dir}', proxy_enabled={proxy_enabled}, minimize_to_tray={minimize_to_tray}")
        if self.app_instance and hasattr(self.app_instance, "main_window"):
            await self.app_instance.main_window.info_dialog(
                t("dialog_settings_saved_title"),
                t("dialog_settings_saved_msg"),
            )


