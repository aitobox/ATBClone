# GUI Multilingual ReleaseNotes Viewer & Settings Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an internationalized "Release Notes" button to "About ATBClone" in `SettingsView` and implement a dedicated `ReleaseNotesWindow` to view localized release notes with language selection.

**Architecture:** Extend `atbclone.core.i18n` with UI translation strings for 9 languages, implement resource resolution helpers in `atbclone.core.resources` to locate `docs/release/ReleaseNote*.md`, build `ReleaseNotesWindow` with Toga controls (Selection, MultilineTextInput, Buttons), and integrate the trigger button into `SettingsView`.

**Tech Stack:** Python 3.12+, BeeWare Toga, pytest.

## Global Constraints
- Strictly adhere to existing 9 languages: `en`, `zh`, `zh_TW`, `ja`, `ko`, `de`, `fr`, `ru`, `es`.
- Use `conda run -n ATBClone` / `PYTHONPATH=src` for testing.
- Target zero external runtime dependencies beyond Toga and standard library.

---

### Task 1: Core i18n Translation Keys & Resource Path Resolution

**Files:**
- Modify: `src/atbclone/core/i18n.py`
- Modify: `src/atbclone/core/resources.py`
- Test: `tests/test_release_notes_core.py`

**Interfaces:**
- Produces in `src/atbclone/core/i18n.py`:
  - New message keys: `settings_btn_release_notes`, `release_notes_window_title`, `release_notes_lang_label`, `release_notes_btn_open_external`, `release_notes_btn_close`, `release_notes_err_not_found`
- Produces in `src/atbclone/core/resources.py`:
  - `LANGUAGE_RELEASE_NOTE_FILES: dict[str, str]`
  - `get_release_notes_dir() -> Path`
  - `get_release_notes_path(lang: str | None = None) -> Path | None`

- [ ] **Step 1: Write failing unit test for core i18n keys and resource resolution**

```python
# tests/test_release_notes_core.py
from pathlib import Path
import pytest

from atbclone.core.i18n import SUPPORTED_LANGUAGES, t, set_language
from atbclone.core.resources import (
    LANGUAGE_RELEASE_NOTE_FILES,
    get_release_notes_dir,
    get_release_notes_path,
)

def test_release_notes_i18n_keys():
    keys = [
        "settings_btn_release_notes",
        "release_notes_window_title",
        "release_notes_lang_label",
        "release_notes_btn_open_external",
        "release_notes_btn_close",
        "release_notes_err_not_found",
    ]
    for lang in SUPPORTED_LANGUAGES:
        set_language(lang)
        for key in keys:
            val = t(key, path="test.md")
            assert val != key, f"Missing translation for {key} in language {lang}"
            assert len(val.strip()) > 0
    set_language(None)

def test_release_notes_path_resolution_all_languages():
    release_dir = get_release_notes_dir()
    assert release_dir.is_dir(), f"Release notes directory not found: {release_dir}"
    
    for lang, filename in LANGUAGE_RELEASE_NOTE_FILES.items():
        path = get_release_notes_path(lang)
        assert path is not None, f"Path was None for lang {lang}"
        assert path.exists(), f"Release note file does not exist: {path}"
        assert path.name == filename
        # Verify non-empty file
        content = path.read_text(encoding="utf-8")
        assert len(content) > 50

def test_release_notes_path_fallback():
    # Invalid lang should fallback to English or default
    path = get_release_notes_path("invalid_lang_code")
    assert path is not None
    assert path.exists()
    assert path.name == "ReleaseNote.md"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_release_notes_core.py -v`
Expected: FAIL (ImportError / missing functions / missing keys)

- [ ] **Step 3: Implement translation keys in `src/atbclone/core/i18n.py` and path resolution in `src/atbclone/core/resources.py`**

In `src/atbclone/core/i18n.py`, add to `MESSAGES`:
```python
    # --- GUI Settings & Release Notes ---
    "settings_btn_release_notes": {
        "en": "📄 Release Notes",
        "zh": "📄 更新日志 (Release Notes)",
        "zh_TW": "📄 更新日誌 (Release Notes)",
        "ja": "📄 リリースノート (Release Notes)",
        "ko": "📄 릴리즈 노트 (Release Notes)",
        "de": "📄 Versionshinweise (Release Notes)",
        "fr": "📄 Notes de version (Release Notes)",
        "ru": "📄 История версий (Release Notes)",
        "es": "📄 Notas de la versión (Release Notes)",
    },
    "release_notes_window_title": {
        "en": "ATBClone Release Notes",
        "zh": "ATBClone 更新日志",
        "zh_TW": "ATBClone 更新日誌",
        "ja": "ATBClone リリースノート",
        "ko": "ATBClone 릴리즈 노트",
        "de": "ATBClone Versionshinweise",
        "fr": "ATBClone Notes de version",
        "ru": "ATBClone История версий",
        "es": "ATBClone Notas de la versión",
    },
    "release_notes_lang_label": {
        "en": "Language:",
        "zh": "语言版本:",
        "zh_TW": "語言版本:",
        "ja": "言語:",
        "ko": "언어:",
        "de": "Sprache:",
        "fr": "Langue :",
        "ru": "Язык:",
        "es": "Idioma:",
    },
    "release_notes_btn_open_external": {
        "en": "📂 Open in Editor",
        "zh": "📂 在外部打开",
        "zh_TW": "📂 在外部開啟",
        "ja": "📂 外部で開く",
        "ko": "📂 외부에서 열기",
        "de": "📂 Im Editor öffnen",
        "fr": "📂 Ouvrir dans l'éditeur",
        "ru": "📂 Открыть в редакторе",
        "es": "📂 Abrir en editor",
    },
    "release_notes_btn_close": {
        "en": "Close",
        "zh": "关闭",
        "zh_TW": "關閉",
        "ja": "閉じる",
        "ko": "닫기",
        "de": "Schließen",
        "fr": "Fermer",
        "ru": "Закрыть",
        "es": "Cerrar",
    },
    "release_notes_err_not_found": {
        "en": "Release notes file not found: {path}",
        "zh": "未找到更新日志文件: {path}",
        "zh_TW": "未找到更新日誌檔案: {path}",
        "ja": "リリースノートファイルが見つかりません: {path}",
        "ko": "릴리즈 노트 파일을 찾을 수 없습니다: {path}",
        "de": "Versionshinweis-Datei nicht gefunden: {path}",
        "fr": "Fichier de notes de version introuvable : {path}",
        "ru": "Файл заметок о выпуске не найден: {path}",
        "es": "Archivo de notas de la versión no encontrado: {path}",
    },
```

In `src/atbclone/core/resources.py`, add:
```python
LANGUAGE_RELEASE_NOTE_FILES: dict[str, str] = {
    "en": "ReleaseNote.md",
    "zh": "ReleaseNote_zh.md",
    "zh_TW": "ReleaseNote_zh_TW.md",
    "ja": "ReleaseNote_ja.md",
    "ko": "ReleaseNote_ko.md",
    "de": "ReleaseNote_de.md",
    "fr": "ReleaseNote_fr.md",
    "ru": "ReleaseNote_ru.md",
    "es": "ReleaseNote_es.md",
}

def get_release_notes_dir() -> Path:
    """Resolve directory containing multilingual release notes documents."""
    module_dir = Path(__file__).resolve().parent  # src/atbclone/core
    src_dir = module_dir.parent.parent  # src
    repo_root = src_dir.parent  # project root
    
    # 1. Direct development workspace docs/release
    candidate_repo = repo_root / "docs" / "release"
    if candidate_repo.is_dir():
        return candidate_repo

    # 2. macOS App Bundle Contents/Resources/docs/release or Contents/Resources/release
    if hasattr(sys, "executable") and sys.executable:
        exe_path = Path(sys.executable).resolve()
        app_contents = exe_path.parent.parent
        bundle_docs = app_contents / "Resources" / "docs" / "release"
        if bundle_docs.is_dir():
            return bundle_docs
        bundle_rel = app_contents / "Resources" / "release"
        if bundle_rel.is_dir():
            return bundle_rel

    # 3. Frozen bundle directory (sys._MEIPASS)
    if hasattr(sys, "_MEIPASS"):
        meipass_docs = Path(sys._MEIPASS) / "docs" / "release"
        if meipass_docs.is_dir():
            return meipass_docs
        meipass_rel = Path(sys._MEIPASS) / "release"
        if meipass_rel.is_dir():
            return meipass_rel

    # 4. Fallback resource/docs/release
    resource_docs = get_resource_dir() / "docs" / "release"
    if resource_docs.is_dir():
        return resource_docs

    return candidate_repo

def get_release_notes_path(lang: str | None = None) -> Path | None:
    """Resolve path to localized release note markdown file for given language."""
    from atbclone.core.i18n import normalize_lang_code, get_language
    
    target_lang = normalize_lang_code(lang) if lang else get_language()
    filename = LANGUAGE_RELEASE_NOTE_FILES.get(target_lang, "ReleaseNote.md")
    
    release_dir = get_release_notes_dir()
    target_file = release_dir / filename
    if target_file.exists():
        return target_file
    
    # Fallback to English default
    fallback = release_dir / "ReleaseNote.md"
    if fallback.exists():
        return fallback
    return None
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_release_notes_core.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/atbclone/core/i18n.py src/atbclone/core/resources.py tests/test_release_notes_core.py
git commit -m "feat(core): add multilingual release notes i18n keys and resource path resolution"
```

---

### Task 2: ReleaseNotesWindow Implementation

**Files:**
- Create: `src/atbclone/gui/windows/release_notes.py`
- Modify: `src/atbclone/gui/windows/__init__.py`
- Test: `tests/test_release_notes_window.py`

**Interfaces:**
- Consumes: `atbclone.core.i18n.t`, `atbclone.core.i18n.get_language`, `atbclone.core.resources.get_release_notes_path`
- Produces: `ReleaseNotesWindow(toga.Window)`

- [ ] **Step 1: Write failing unit test for ReleaseNotesWindow**

```python
# tests/test_release_notes_window.py
import pytest
import toga

from atbclone.core.i18n import set_language
from atbclone.gui.windows.release_notes import ReleaseNotesWindow, LANGUAGE_DISPLAY_NAMES

def test_release_notes_window_init():
    set_language("zh")
    window = ReleaseNotesWindow()
    assert "ATBClone" in window.title
    assert window.size == (780, 580)
    assert window.selection_lang is not None
    assert window.text_content is not None
    # Verify content loaded
    assert len(window.text_content.value) > 50
    assert "ATBClone" in window.text_content.value
    set_language(None)

def test_release_notes_window_lang_switch():
    window = ReleaseNotesWindow(initial_lang="en")
    assert window.current_lang == "en"
    assert "Release Notes" in window.text_content.value
    
    # Switch to ja
    window.switch_language("ja")
    assert window.current_lang == "ja"
    assert len(window.text_content.value) > 50
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_release_notes_window.py -v`
Expected: FAIL (ModuleNotFoundError: No module named 'atbclone.gui.windows.release_notes')

- [ ] **Step 3: Implement `ReleaseNotesWindow` in `src/atbclone/gui/windows/release_notes.py`**

```python
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

class ReleaseNotesWindow(toga.Window):
    """Dedicated window for browsing multilingual ATBClone Release Notes."""

    def __init__(self, initial_lang: Optional[str] = None):
        super().__init__(
            title=t("release_notes_window_title"),
            size=(780, 580),
        )
        
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
```

Update `src/atbclone/gui/windows/__init__.py`:
```python
from atbclone.gui.windows.clone_detail import CloneDetailWindow
from atbclone.gui.windows.clone_edit import CloneEditWindow
from atbclone.gui.windows.recipe_edit import RecipeEditWindow
from atbclone.gui.windows.wizard import WizardWindow
from atbclone.gui.windows.release_notes import ReleaseNotesWindow

__all__ = [
    "CloneDetailWindow",
    "CloneEditWindow",
    "RecipeEditWindow",
    "WizardWindow",
    "ReleaseNotesWindow",
]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_release_notes_window.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/atbclone/gui/windows/release_notes.py src/atbclone/gui/windows/__init__.py tests/test_release_notes_window.py
git commit -m "feat(gui): implement ReleaseNotesWindow with dynamic language selector"
```

---

### Task 3: SettingsView Integration & Full Test Verification

**Files:**
- Modify: `src/atbclone/gui/views/settings_view.py`
- Test: `tests/test_settings_release_notes.py`

**Interfaces:**
- Consumes: `ReleaseNotesWindow`, `t("settings_btn_release_notes")`
- Produces: `SettingsView.btn_release_notes` and `SettingsView.on_open_release_notes`

- [ ] **Step 1: Write failing unit test for SettingsView ReleaseNotes button**

```python
# tests/test_settings_release_notes.py
import pytest
import toga

from atbclone.core.i18n import set_language, t
from atbclone.gui.views.settings_view import SettingsView
from atbclone.gui.windows.release_notes import ReleaseNotesWindow

def test_settings_view_release_notes_button_exists():
    set_language("zh")
    view = SettingsView()
    assert hasattr(view, "btn_release_notes")
    assert view.btn_release_notes.text == t("settings_btn_release_notes")
    assert "更新日志" in view.btn_release_notes.text
    set_language(None)

def test_settings_view_open_release_notes_action(monkeypatch):
    view = SettingsView()
    shown = []
    
    def mock_show(self):
        shown.append(self)
    
    monkeypatch.setattr(ReleaseNotesWindow, "show", mock_show)
    
    # Call handler
    view.on_open_release_notes(view.btn_release_notes)
    assert len(shown) == 1
    assert isinstance(shown[0], ReleaseNotesWindow)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_settings_release_notes.py -v`
Expected: FAIL (AttributeError: 'SettingsView' object has no attribute 'btn_release_notes')

- [ ] **Step 3: Modify `src/atbclone/gui/views/settings_view.py` to add ReleaseNotes button**

In `src/atbclone/gui/views/settings_view.py`:
1. Import `t` and `ReleaseNotesWindow`:
```python
from atbclone.core.i18n import t
from atbclone.gui.windows.release_notes import ReleaseNotesWindow
```
2. In `__init__`, in Card 4 (`card_info`):
```python
        # ── Card 4: System Info ────────────────────────────────────────────── #
        card_info = toga.Box(style=Pack(direction=COLUMN, margin=10, background_color=Theme.BG_CARD))
        card_info.add(toga.Label("ℹ️ 关于 ATBClone", style=Pack(font_weight="bold", font_size=14, margin_bottom=6, color=Theme.TEXT_PRIMARY)))
        card_info.add(toga.Label(f"ATBClone 版本: v{__version__}", style=Pack(font_size=12, color=Theme.TEXT_MUTED, margin_bottom=2)))
        card_info.add(toga.Label(f"Python 核心: {platform.python_version()} ({platform.machine()})", style=Pack(font_size=12, color=Theme.TEXT_MUTED, margin_bottom=2)))
        card_info.add(toga.Label(f"macOS 系统架构: {platform.mac_ver()[0] or 'macOS'}", style=Pack(font_size=12, color=Theme.TEXT_MUTED, margin_bottom=8)))
        
        self.btn_release_notes = toga.Button(
            t("settings_btn_release_notes"),
            on_press=self.on_open_release_notes,
            style=Pack(height=32, margin_top=4),
        )
        card_info.add(self.btn_release_notes)
        content_box.add(card_info)
        
        self.release_notes_window: Optional[ReleaseNotesWindow] = None
```
3. Add method `on_open_release_notes`:
```python
    def on_open_release_notes(self, widget: toga.Button):
        """Open or focus the ReleaseNotesWindow."""
        self.release_notes_window = ReleaseNotesWindow()
        self.release_notes_window.show()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_settings_release_notes.py -v`
Expected: PASS

- [ ] **Step 5: Run full project test suite**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/ -q`
Expected: 100% PASS (all tests pass)

- [ ] **Step 6: Commit**

```bash
git add src/atbclone/gui/views/settings_view.py tests/test_settings_release_notes.py
git commit -m "feat(gui): integrate ReleaseNotes button into SettingsView"
```
