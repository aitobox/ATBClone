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
        content_box = toga.Box(style=Pack(direction=COLUMN, margin=(0, 24, 20, 24)))
        scroll.content = content_box
        self.add(scroll)

        # ── Card 1: Language Preference ────────────────────────────────────── #
        card_lang = toga.Box(style=Pack(direction=COLUMN, margin_bottom=14, background_color=Theme.BG_CARD))
        inner_lang = toga.Box(style=Pack(direction=COLUMN, margin=(14, 18, 14, 18)))
        inner_lang.add(toga.Label(t("settings_card_language"), style=Pack(font_weight="bold", font_size=15, margin_bottom=12, color=Theme.TEXT_PRIMARY)))

        row_lang = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin_bottom=6))
        row_lang.add(toga.Label(t("settings_label_language"), style=Pack(width=120, font_size=13, color=Theme.TEXT_PRIMARY)))

        lang_items = list(SUPPORTED_LANGUAGES_MAP.values())
        current_cfg = get_configured_language()
        current_item = SUPPORTED_LANGUAGES_MAP.get(current_cfg, lang_items[0])

        self.select_language = toga.Selection(
            items=lang_items,
            value=current_item,
            on_change=self._on_language_changed,
            style=Pack(flex=1, font_size=12.0),
        )
        row_lang.add(self.select_language)
        inner_lang.add(row_lang)
        inner_lang.add(toga.Label(t("settings_hint_language"), style=Pack(font_size=11.5, color=Theme.TEXT_MUTED, margin_top=4)))
        card_lang.add(inner_lang)
        content_box.add(card_lang)

        # ── Card 2: Data & Storage Management ──────────────────────────────── #
        card_dir = toga.Box(style=Pack(direction=COLUMN, margin_bottom=14, background_color=Theme.BG_CARD))
        inner_dir = toga.Box(style=Pack(direction=COLUMN, margin=(14, 18, 14, 18)))
        inner_dir.add(toga.Label(t("settings_card_storage"), style=Pack(font_weight="bold", font_size=15, margin_bottom=12, color=Theme.TEXT_PRIMARY)))

        # Root Workspace Directory input row
        row_base = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin_bottom=6))
        row_base.add(toga.Label(t("settings_label_root"), style=Pack(width=120, font_size=13, color=Theme.TEXT_PRIMARY)))
        self.input_base_dir = toga.TextInput(value=str(DEFAULT_ATB_DIR), on_change=self._on_base_dir_changed, style=Pack(flex=1, margin_right=8, font_size=13.5))
        self.btn_browse_base = toga.Button(t("btn_browse_dir"), on_press=self._on_browse_base, style=Pack(height=30, font_size=13))
        row_base.add(self.input_base_dir)
        row_base.add(self.btn_browse_base)
        inner_dir.add(row_base)

        inner_dir.add(toga.Label(t("settings_hint_paths"), style=Pack(font_size=11.5, color=Theme.TEXT_MUTED, margin_top=4, margin_bottom=10)))

        # Dynamic subdirectories labels synchronized with root directory
        self.label_apps_dir = toga.Label(t("settings_label_apps_dir", path=str(DEFAULT_APPS_DIR)), style=Pack(font_size=12.5, color=Theme.TEXT_MUTED, margin_bottom=4))
        self.label_data_dir = toga.Label(t("settings_label_data_dir", path=str(DEFAULT_DATA_DIR)), style=Pack(font_size=12.5, color=Theme.TEXT_MUTED, margin_bottom=10))
        inner_dir.add(self.label_apps_dir)
        inner_dir.add(self.label_data_dir)

        self.btn_open_finder = toga.Button(
            t("settings_btn_open_finder"),
            on_press=self.on_open_data_dir_in_finder,
            style=Pack(font_weight="bold", font_size=13, height=30),
        )
        inner_dir.add(self.btn_open_finder)
        card_dir.add(inner_dir)
        content_box.add(card_dir)

        # ── Card 3: Default Proxy ──────────────────────────────────────────── #
        card_proxy = toga.Box(style=Pack(direction=COLUMN, margin_bottom=14, background_color=Theme.BG_CARD))
        inner_proxy = toga.Box(style=Pack(direction=COLUMN, margin=(14, 18, 14, 18)))
        inner_proxy.add(toga.Label(t("settings_card_proxy"), style=Pack(font_weight="bold", font_size=15, margin_bottom=12, color=Theme.TEXT_PRIMARY)))

        self.switch_proxy = toga.Switch(t("settings_switch_proxy_default"), value=False, style=Pack(margin_bottom=8, font_size=13.5))
        inner_proxy.add(self.switch_proxy)

        row_proxy = toga.Box(style=Pack(direction=ROW, align_items=CENTER))
        self.select_proxy_type = toga.Selection(items=["http", "https", "socks5"], style=Pack(width=105, margin_right=8, font_size=12.0))
        self.input_proxy_host = toga.TextInput(value="127.0.0.1", style=Pack(flex=1, margin_right=8, font_size=13.5))
        self.input_proxy_port = toga.TextInput(value="7890", style=Pack(width=90, font_size=13.5))
        row_proxy.add(self.select_proxy_type)
        row_proxy.add(self.input_proxy_host)
        row_proxy.add(self.input_proxy_port)
        inner_proxy.add(row_proxy)
        card_proxy.add(inner_proxy)
        content_box.add(card_proxy)

        # ── Card 4: Window & Tray Preferences ──────────────────────────────── #
        card_tray = toga.Box(style=Pack(direction=COLUMN, margin_bottom=14, background_color=Theme.BG_CARD))
        inner_tray = toga.Box(style=Pack(direction=COLUMN, margin=(14, 18, 14, 18)))
        inner_tray.add(toga.Label(t("settings_card_tray"), style=Pack(font_weight="bold", font_size=15, margin_bottom=12, color=Theme.TEXT_PRIMARY)))

        current_tray_cfg = bool(get_config_value("minimize_to_tray", False))
        self.switch_minimize_to_tray = toga.Switch(
            t("settings_switch_minimize_to_tray"),
            value=current_tray_cfg,
            on_change=self._on_minimize_to_tray_changed,
            style=Pack(margin_bottom=6, font_size=13.5),
        )
        inner_tray.add(self.switch_minimize_to_tray)
        inner_tray.add(toga.Label(t("settings_hint_minimize_to_tray"), style=Pack(font_size=11.5, color=Theme.TEXT_MUTED)))
        card_tray.add(inner_tray)
        content_box.add(card_tray)

        # ── Card 5: System Info ────────────────────────────────────────────── #
        card_info = toga.Box(style=Pack(direction=COLUMN, margin_bottom=14, background_color=Theme.BG_CARD))
        inner_info = toga.Box(style=Pack(direction=COLUMN, margin=(14, 18, 14, 18)))
        inner_info.add(toga.Label(t("settings_card_about"), style=Pack(font_weight="bold", font_size=15, margin_bottom=10, color=Theme.TEXT_PRIMARY)))
        inner_info.add(toga.Label(t("settings_label_version", ver=__version__), style=Pack(font_size=12.5, color=Theme.TEXT_MUTED, margin_bottom=4)))
        inner_info.add(toga.Label(t("settings_label_python", ver=platform.python_version(), arch=platform.machine()), style=Pack(font_size=12.5, color=Theme.TEXT_MUTED, margin_bottom=4)))
        inner_info.add(toga.Label(t("settings_label_os", ver=platform.mac_ver()[0] or 'macOS'), style=Pack(font_size=12.5, color=Theme.TEXT_MUTED, margin_bottom=12)))

        self.btn_release_notes = toga.Button(
            t("settings_btn_release_notes"),
            on_press=self.on_open_release_notes,
            style=Pack(height=30, font_size=13),
        )
        inner_info.add(self.btn_release_notes)
        card_info.add(inner_info)
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
                from atbclone.gui.app import set_macos_dock_visible
                set_macos_dock_visible(True)

    def _on_base_dir_changed(self, widget: toga.TextInput) -> None:
        self._sync_storage_labels()

    def _sync_storage_labels(self) -> None:
        raw = self.input_base_dir.value.strip() if hasattr(self, "input_base_dir") and self.input_base_dir.value else ""
        base_path = Path(raw) if raw else DEFAULT_ATB_DIR
        if hasattr(self, "label_apps_dir"):
            self.label_apps_dir.text = t("settings_label_apps_dir", path=str(base_path / "Apps"))
        if hasattr(self, "label_data_dir"):
            self.label_data_dir.text = t("settings_label_data_dir", path=str(base_path / "Data"))

    def on_open_data_dir_in_finder(self, widget: toga.Button):
        """Open default base directory in macOS Finder."""
        base_dir = Path(self.input_base_dir.value.strip() or str(DEFAULT_ATB_DIR))
        logger.info(f"Opening data directory in Finder: '{base_dir}'")
        try:
            base_dir.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError):
            pass
        try:
            subprocess.Popen(["open", str(base_dir)])
        except Exception as e:
            logger.warning(f"Failed to open directory in Finder: {e}")

    async def _on_browse_base(self, widget: toga.Button):
        if self.app_instance and hasattr(self.app_instance, "main_window"):
            try:
                selected = await self.app_instance.main_window.select_folder_dialog(
                    title=t("dialog_select_root_dir_title"),
                    initial_directory=Path(self.input_base_dir.value.strip() or str(DEFAULT_ATB_DIR)),
                )
                if selected:
                    self.input_base_dir.value = str(selected)
                    self._sync_storage_labels()
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


