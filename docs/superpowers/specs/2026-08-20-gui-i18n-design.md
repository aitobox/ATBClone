# ATBClone GUI Internationalization (i18n) & Dynamic Language Switching Design

## Background & Objectives
ATBClone's CLI currently has comprehensive internationalization support covering 9 languages (`en`, `zh`, `zh_TW`, `ja`, `ko`, `de`, `fr`, `ru`, `es`), utilizing the centralized `atbclone.core.i18n` engine.
However, the GUI application layer (`src/atbclone/gui/`) was previously hardcoded with mixed Chinese and English text across its sidebar navigation, top header bar, views, cards, detail/edit/wizard windows, and system dialogs.

This document specifies the end-to-end design for bringing 100% i18n coverage across all GUI dialogs, buttons, labels, and windows, along with dynamic language switching in `SettingsView`.

---

## Architectural Design

### 1. Core i18n Dictionary & Persistence (`src/atbclone/core/i18n.py`)
1. **Language Map**:
   ```python
   SUPPORTED_LANGUAGES_MAP: dict[str, str] = {
       "auto": "自动 / System Default",
       "zh": "简体中文",
       "zh_TW": "繁體中文",
       "en": "English",
       "ja": "日本語",
       "ko": "한국어",
       "de": "Deutsch",
       "fr": "Français",
       "ru": "Русский",
       "es": "Español",
   }
   ```
2. **Language Resolution Hierarchy**:
   - Runtime override via `set_language(...)` / GUI selection.
   - User persistent config file `~/.atbclone/config.json` (`language` key).
   - Environment variable `ATBCLONE_LANG`.
   - macOS system settings (`AppleLanguages` -> `AppleLocale` -> `LC_ALL` / `LANG`).
   - Default fallback (`en`).
3. **Comprehensive Key Categorization**:
   - `nav_*`: Sidebar navigation keys (`nav_clones`, `nav_recipes`, `nav_probe`, `nav_doctor`, `nav_logs`, `nav_settings`).
   - `topbar_*`: Top header bar titles, search placeholders, mode toggles (`topbar_view_grid`, `topbar_view_list`), and refresh button.
   - `card_*`: CloneCard and RecipeCard fields, strategy badges, and action tooltips.
   - `view_clones_*`: Clone list filter items, sort options, empty hints, table headers, and batch actions.
   - `view_recipes_*`: Recipe list filter items, sort options, origin badges, table headers, and creation actions.
   - `view_probe_*`: Prober app target selection, results cards, strategy reasons, and save buttons.
   - `view_doctor_*`: Environment checklist table headers, status badges, and summary text.
   - `view_logs_*`: Logs search placeholder, clear button, and dynamic line count titles.
   - `view_settings_*`: Settings cards (storage, paths, proxy, language preference, system info), browse buttons, and save feedback.
   - `win_wizard_*`: 7-step wizard headers, descriptions, step inputs, strategy options, data dir hints, and background progress status.
   - `win_detail_*`, `win_edit_*`, `win_recipe_edit_*`: Window titles, form labels, switch text, and action buttons.
   - `dialog_*`: System dialogs (`info_dialog`, `error_dialog`, `confirm_dialog`, `open_file_dialog`, `select_folder_dialog`) titles and bodies.

---

### 2. GUI Component & View Modernization

1. **`SidebarNav` (`src/atbclone/gui/components/sidebar.py`)**:
   - Update navigation items dynamically using `t("nav_*")`.
   - Support `retranslate()` to refresh button text upon language change.
2. **`TopHeaderBar` (`src/atbclone/gui/components/top_bar.py`)**:
   - Translate default search placeholders, view selection items, and refresh button.
   - Language-agnostic view mode detection (supporting both localized labels and internal mode identifiers).
3. **`CloneCard` & `CloneListView` (`src/atbclone/gui/views/clone_list.py`)**:
   - Localize all filter dropdown items, sort options, table column headers, and action buttons (`▶️ Launch`, `🔄 Update`, `✏️ Edit`, `ℹ️ Detail`, `🗑️ Delete`).
   - Localize empty state hints and error/confirmation dialogs.
4. **`RecipeListView` (`src/atbclone/gui/views/recipe_list.py`)**:
   - Localize built-in / custom filter labels, table columns, copy / edit / delete buttons, and duplicate dialogs.
5. **`ProbeView` & `DoctorView`**:
   - Localize all analysis output rows, summary headers, table columns, and save confirmation badges.
6. **`LogsView` & `SettingsView`**:
   - Localize log filters and counts.
   - Add a Language Selection Card in `SettingsView` allowing users to select "Auto" or any of the 9 supported languages, immediately triggering live UI refresh.

---

### 3. Popups, Windows, and Interactive Dialogs

1. **`WizardWindow` (`src/atbclone/gui/windows/wizard.py`)**:
   - 7 step headers, helper text, and button labels (`◀ Back`, `Next ▶`, `Cancel`, `🚀 Clone Now`).
   - Probe vs. built-in origin badges and real-time execution status labels.
   - File/directory chooser dialog titles and confirmation dialogs.
2. **`CloneDetailWindow`, `CloneEditWindow`, `RecipeEditWindow`**:
   - Window titles, property labels, switches, and validation alert dialogs.

---

### 4. Dynamic Coordinator Workflow (`ATBCloneApp`)

- `ATBCloneApp` provides `retranslate_ui()`:
  - Invokes `SidebarNav.retranslate()` or re-instantiates navigation.
  - Re-initializes all 6 views with updated translation strings while preserving active view state and user data.
  - Re-renders `content_container` and updates window title.

---

## Verification & Testing Plan

1. **Unit Tests (`tests/test_i18n.py`)**:
   - Verify all GUI translation keys exist for all 9 languages without missing strings or syntax formatting errors.
   - Verify `set_language(...)` and `get_language()` behavior with config persistence and fallback logic.
2. **GUI Integration Tests (`tests/gui/`)**:
   - Update existing GUI test fixtures to ensure language independence.
   - Add new test suite `tests/gui/test_gui_i18n.py` validating that language changes dynamically update sidebar, top bar, views, and dialog titles.
   - Test wizard window and edit windows under multiple language settings (`en`, `zh`, `ja`, etc.).
3. **Full Test Suite Execution**:
   - Execute `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/` and ensure 100% pass rate.
