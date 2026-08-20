# ATBClone GUI Multilingual ReleaseNotes Viewer & Settings Integration Design

## Background & Objectives
ATBClone maintains a standardized suite of release notes across 9 supported languages (`en`, `zh`, `zh_TW`, `ja`, `ko`, `de`, `fr`, `ru`, `es`) under `docs/release/`.
In the GUI settings panel (`SettingsView` under "About ATBClone"), users currently see version, Python runtime, and macOS system architecture information, but there is no direct way to inspect the release notes and changelog within the application.

This specification details the design for adding an internationalized "Release Notes" button to the "About ATBClone" card in `SettingsView`, and providing a dedicated, native `ReleaseNotesWindow` modal that automatically presents the changelog in the user's active language with dynamic multilingual switching and external editor options.

---

## Architectural Design

### 1. Multilingual Translation Keys (`src/atbclone/core/i18n.py`)
In `MESSAGES`, add localization strings for all 9 supported languages (`en`, `zh`, `zh_TW`, `ja`, `ko`, `de`, `fr`, `ru`, `es`):
- `settings_btn_release_notes`:
  - `en`: "📄 Release Notes"
  - `zh`: "📄 更新日志 (Release Notes)"
  - `zh_TW`: "📄 更新日誌 (Release Notes)"
  - `ja`: "📄 リリースノート (Release Notes)"
  - `ko`: "📄 릴리즈 노트 (Release Notes)"
  - `de`: "📄 Versionshinweise (Release Notes)"
  - `fr`: "📄 Notes de version (Release Notes)"
  - `ru`: "📄 История версий (Release Notes)"
  - `es`: "📄 Notas de la versión (Release Notes)"
- `release_notes_window_title`:
  - `en`: "ATBClone Release Notes"
  - `zh`: "ATBClone 更新日志"
  - `zh_TW`: "ATBClone 更新日誌"
  - `ja`: "ATBClone リリースノート"
  - `ko`: "ATBClone 릴리즈 노트"
  - `de`: "ATBClone Versionshinweise"
  - `fr`: "ATBClone Notes de version"
  - `ru`: "ATBClone История версий"
  - `es`: "ATBClone Notas de la versión"
- `release_notes_lang_label`:
  - `en`: "Language:"
  - `zh`: "语言版本:"
  - `zh_TW`: "語言版本:"
  - `ja`: "言語:"
  - `ko`: "언어:"
  - `de`: "Sprache:"
  - `fr`: "Langue :"
  - `ru`: "Язык:"
  - `es`: "Idioma:"
- `release_notes_btn_open_external`:
  - `en`: "📂 Open in Editor"
  - `zh`: "📂 在外部打开"
  - `zh_TW`: "📂 在外部開啟"
  - `ja`: "📂 外部で開く"
  - `ko`: "📂 외부에서 열기"
  - `de`: "📂 Im Editor öffnen"
  - `fr`: "📂 Ouvrir dans l'éditeur"
  - `ru`: "📂 Открыть в редакторе"
  - `es`: "📂 Abrir en editor"
- `release_notes_btn_close`:
  - `en`: "Close"
  - `zh`: "关闭"
  - `zh_TW`: "關閉"
  - `ja`: "閉じる"
  - `ko`: "닫기"
  - `de`: "Schließen"
  - `fr`: "Fermer"
  - `ru`: "Закрыть"
  - `es`: "Cerrar"

---

### 2. Release Notes Path Resolution (`src/atbclone/core/resources.py`)
Add resource resolution helpers for release note documents:
1. `LANGUAGE_RELEASE_NOTE_FILES`:
   - `en` ➔ `ReleaseNote.md`
   - `zh` ➔ `ReleaseNote_zh.md`
   - `zh_TW` ➔ `ReleaseNote_zh_TW.md`
   - `ja` ➔ `ReleaseNote_ja.md`
   - `ko` ➔ `ReleaseNote_ko.md`
   - `de` ➔ `ReleaseNote_de.md`
   - `fr` ➔ `ReleaseNote_fr.md`
   - `ru` ➔ `ReleaseNote_ru.md`
   - `es` ➔ `ReleaseNote_es.md`
2. `get_release_notes_dir() -> Path`:
   - Checks repository root `docs/release/`
   - Checks macOS bundle `Contents/Resources/docs/release` or `Contents/Resources/release`
   - Checks frozen directory `sys._MEIPASS / docs / release` or `sys._MEIPASS / release`
   - Fallback to package relative path
3. `get_release_notes_path(lang: str | None = None) -> Path | None`:
   - Resolves the normalized language code to the target markdown file path.
   - Falls back to `ReleaseNote.md` (English) or `ReleaseNote_zh.md` if the specific language file is missing.

---

### 3. Release Notes Window Component (`src/atbclone/gui/windows/release_notes.py`)
Implement `ReleaseNotesWindow(toga.Window)`:
- **Properties & Sizing**:
  - Window title: localized `release_notes_window_title`
  - Size: `(780, 580)`
- **Header Bar / Control Area**:
  - `toga.Label`: localized `release_notes_lang_label`
  - `toga.Selection`: Items mapping display names to language codes (`"简体中文"`, `"English"`, `"繁體中文"`, `"日本語"`, `"한국어"`, `"Deutsch"`, `"Français"`, `"Русский"`, `"Español"`). Defaults to current active language (`get_language()`).
  - `toga.Button`: localized `release_notes_btn_open_external` (triggers `open <filepath>` via `subprocess.Popen`).
  - `toga.Button`: localized `release_notes_btn_close` (invokes `self.close()`).
- **Content Area**:
  - `toga.MultilineTextInput(readonly=True, style=Pack(flex=1, font_family="monospace", font_size=12, margin=10))`
  - Automatically loads and displays the markdown text content of the selected language version.
- **Event Handling**:
  - Changing selection dynamically reads and displays the corresponding `.md` file content.

---

### 4. Settings View Integration (`src/atbclone/gui/views/settings_view.py`)
In `SettingsView`:
- Under Card 4 (`card_info` - "About ATBClone"):
  - Instantiate `self.btn_release_notes = toga.Button(t("settings_btn_release_notes"), on_press=self.on_open_release_notes, style=Pack(margin_top=8, height=32))`
  - Add `self.btn_release_notes` to `card_info`.
- Handler `on_open_release_notes`:
  - Opens `ReleaseNotesWindow()`. If an existing instance is already open, brings it to front.

---

## Verification & Testing Plan

### 1. Automated Unit & Integration Tests
- **`tests/test_release_notes.py`**:
  - Validate that `get_release_notes_dir()` and `get_release_notes_path(lang)` correctly resolve files for all 9 supported languages.
  - Verify fallback behavior when given an invalid or unknown language code.
  - Validate that all 9 i18n keys for ReleaseNotes are present and non-empty across all 9 languages in `MESSAGES`.
- **`tests/gui/test_release_notes_gui.py`**:
  - Test instantiation of `ReleaseNotesWindow`.
  - Test language dropdown selection switching and markdown content loading.
  - Test `SettingsView` button presence and `on_open_release_notes` callback.

### 2. Manual Verification
- Run GUI application (`conda run -n ATBClone python -m atbclone.gui`).
- Navigate to "全局设置 (Settings)".
- Verify "📄 更新日志 (Release Notes)" button is present in the "关于 ATBClone" card.
- Click the button, confirm `ReleaseNotesWindow` opens with correct active language content, test language switcher dropdown across multiple languages, and test "在外部打开" button.
- Run full pytest test suite: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/`.
