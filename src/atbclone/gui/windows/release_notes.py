"""Release Notes Viewer Window with dynamic language switching."""

import asyncio
import subprocess
from pathlib import Path
from typing import Optional
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER

from atbclone.core.i18n import t, get_language, normalize_lang_code
from atbclone.core.resources import get_release_notes_path
from atbclone.gui.theme import Theme

LANGUAGE_DISPLAY_NAMES: list[tuple[str, str]] = [
    ("zh", "简体中文 (Simplified Chinese)"),
    ("zh_TW", "繁體中文 (Traditional Chinese)"),
    ("en", "English"),
    ("ja", "日本語 (Japanese)"),
    ("ko", "한국어 (Korean)"),
    ("de", "Deutsch (German)"),
    ("fr", "Français (French)"),
    ("ru", "Русский (Russian)"),
    ("es", "Español (Spanish)"),
]


from atbclone.gui.patch_cocoa import configure_cocoa_window


class ReleaseNotesWindow(toga.Window):
    """Dedicated window for browsing multilingual ATBClone Release Notes."""

    def __init__(self, initial_lang: Optional[str] = None):
        super().__init__(
            title=t("release_notes_window_title"),
            size=(780, 580),
        )
        configure_cocoa_window(self, floating=True)

        self.current_lang = normalize_lang_code(initial_lang or get_language())

        self.current_path: Optional[Path] = None

        # Build UI Components
        self._build_ui()
        self.load_release_notes(self.current_lang)

    def _build_ui(self):
        root_box = toga.Box(style=Pack(direction=COLUMN, flex=1, background_color=Theme.BG_WINDOW))

        # Top Control Bar
        top_bar = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin=(12, 16, 8, 16)))

        label_lang = toga.Label(
            t("release_notes_lang_label"),
            style=Pack(font_weight="bold", font_size=12, margin_right=8, color=Theme.TEXT_PRIMARY),
        )
        top_bar.add(label_lang)

        # Build dropdown selection items
        display_items = [name for _, name in LANGUAGE_DISPLAY_NAMES]
        self.selection_lang = toga.Selection(
            items=display_items,
            on_change=self._on_lang_changed,
            style=Pack(width=260, margin_right=12),
        )

        # Set default selection index
        lang_codes = [code for code, _ in LANGUAGE_DISPLAY_NAMES]
        if self.current_lang in lang_codes:
            idx = lang_codes.index(self.current_lang)
            self.selection_lang.value = display_items[idx]
        top_bar.add(self.selection_lang)

        # Spacer
        spacer = toga.Box(style=Pack(flex=1))
        top_bar.add(spacer)

        # Open in external editor button
        self.btn_open_external = toga.Button(
            t("release_notes_btn_open_external"),
            on_press=self.on_open_in_external_editor,
            style=Pack(margin_right=8, height=30),
        )
        top_bar.add(self.btn_open_external)

        # Close button
        self.btn_close = toga.Button(
            t("release_notes_btn_close"),
            on_press=lambda w: self.close(),
            style=Pack(width=70, height=30),
        )
        top_bar.add(self.btn_close)

        root_box.add(top_bar)

        # Main Text Display Box
        content_box = toga.Box(style=Pack(direction=COLUMN, flex=1, margin=(0, 16, 16, 16)))

        self.text_content = toga.MultilineTextInput(
            readonly=True,
            style=Pack(
                flex=1,
                font_family="monospace",
                font_size=12,
                background_color=Theme.BG_CARD,
            ),
        )
        content_box.add(self.text_content)
        root_box.add(content_box)

        self.content = root_box

    def _on_lang_changed(self, widget: toga.Selection):
        display_val = widget.value
        for code, name in LANGUAGE_DISPLAY_NAMES:
            if name == display_val:
                self.switch_language(code)
                break

    def switch_language(self, lang_code: str):
        """Switch active displayed language and reload notes."""
        self.current_lang = normalize_lang_code(lang_code)
        self.load_release_notes(self.current_lang)

    def load_release_notes(self, lang_code: str):
        """Load markdown content into text viewer."""
        path = get_release_notes_path(lang_code)
        self.current_path = path
        if path and path.exists():
            try:
                content = path.read_text(encoding="utf-8")
                self.text_content.value = content
            except Exception as e:
                self.text_content.value = f"Error loading release notes: {e}"
        else:
            self.text_content.value = t("release_notes_err_not_found", path=str(path or ""))

    def on_open_in_external_editor(self, widget: toga.Button):
        """Open current markdown release notes file in macOS default app."""
        if self.current_path and self.current_path.exists():
            try:
                subprocess.Popen(["open", str(self.current_path)])
            except Exception:
                pass
