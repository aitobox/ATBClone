# ATBClone BeeWare (Toga) GUI Native Application Design

## 1. Overview & Goals

This design specification details the native macOS GUI application for **ATBClone**, built with **BeeWare (Toga + Briefcase)**.
The GUI provides a first-class visual interface running on macOS that reuses the existing `atbclone.core` and `atbclone.recipes` business logic while providing complete feature parity with the existing CLI operations.

### Key Objectives:
1. **Interactive Cloning Wizard**: Step-by-step visual guidance for cloning apps.
2. **Clone Lifecycle Management**: List, inspect, update, and remove existing clones.
3. **Clone Parameter Editing**: Visual editing for clone parameters (e.g. proxy, display name).
4. **Recipe Explorer & Editor**: Manage built-in and custom recipes with full CRUD capabilities.
5. **App Prober Integration**: Probe unconfigured apps and save results directly to the recipe list.
6. **Environment Doctor**: Visual system environment and prerequisite dependency diagnostics.
7. **Maximum Code Reuse**: Direct Python import of `atbclone.core` and `atbclone.recipes`, zero dependency on CLI/Click layers.

---

## 2. Architecture & Layering

The application adopts a clean, decoupled architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                    ATBClone GUI App                         │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                   gui/ Layer (Toga)                 │    │
│  │  app.py │ views/ │ windows/ │ services/             │    │
│  └──────────────────────┬──────────────────────────────┘    │
│                         │ Direct Python import               │
│  ┌──────────────────────▼──────────────────────────────┐    │
│  │         core/ + recipes/ Shared Layers (Unmodified) │    │
│  │  StateManager │ CloneEngine │ AppProber │ Recipe    │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

- **`src/atbclone/gui/`**: Contains Toga widgets, windows, views, and routing logic.
- **`src/atbclone/gui/services/`**: Bridges asynchronous UI actions with blocking core logic using `asyncio.get_event_loop().run_in_executor()`.
- **`src/atbclone/core/`**: Shared core domain models and execution engines (unmodified).
- **`src/atbclone/recipes/`**: Shared recipe models and loaders (unmodified).
- **`src/atbclone/cli/`**: Existing CLI layer (unmodified, completely independent).

---

## 3. UI Layout & Navigation

### 3.1 Main Window Layout
The main window uses a standard macOS Split View (`toga.SplitContainer`):
- **Left Sidebar**: Navigation categories
  - 📱 **Clones (`CloneListView`)**: List of active cloned apps.
  - 🍳 **Recipes (`RecipeListView`)**: Built-in & user custom recipes.
  - 🔧 **Tools**:
    - **Probe (`ProbeView`)**: Deep application analysis and recipe extraction.
    - **Doctor (`DoctorView`)**: Dependency and environment health check.
- **Right Content Area**: Dynamic view container swapping views based on sidebar selection.
- **Top Toolbar**:
  - `[➕ New Clone]` (Opens Wizard Window)
  - `[🔄 Refresh]`
  - `[🔍 Probe App]`
  - `[💊 Doctor]`

### 3.2 Modal & Auxiliary Windows (`toga.Window`)
- **`WizardWindow`**: 7-step modal wizard for creating a clone.
- **`CloneDetailWindow`**: Read-only inspector displaying all metadata from `CloneRecord`.
- **`CloneEditWindow`**: Editor for mutable clone properties (display name, proxy configuration).
- **`RecipeEditWindow`**: Visual form editor for editing or creating recipe YAML configurations.

---

## 4. Feature Specifications

### 4.1 Feature 1: Multi-Step Cloning Wizard (`WizardWindow`)
A 7-step wizard with step indicator, Back/Next navigation, and asynchronous execution:
1. **Step 1 - Select Source App**: File picker or drag-and-drop `.app` bundle. Calls `AppInspector.inspect()`.
2. **Step 2 - Recipe Matching**: Automatically match recipe via `RecipeLoader`. If unmatched, offers auto-probe.
3. **Step 3 - Identity & Naming**: Clone name input (auto-incremented suggestion) and Display Name input.
4. **Step 4 - Destination Directory**: Select target directory (`~/Applications` default or `/Applications`).
5. **Step 5 - Data Directory**: If supported (`supports_data_dir()`), allow custom data storage path.
6. **Step 6 - Proxy Configuration**: Toggle proxy with type (HTTP/SOCKS5), host, port, credentials.
7. **Step 7 - Summary & Execution**: Final review. Running clone asynchronously in background with real-time log output widget.

### 4.2 Feature 2: Cloned Apps Management (`CloneListView`)
- Displays `toga.Table` with columns: Name, Source App, Strategy, Proxy, Created At.
- Actions on selection:
  - **Update (`[🔄 Update]`)**: Re-runs engine sync to preserve user data while updating binary.
  - **Remove (`[🗑️ Delete]`)**: Prompts user confirmation dialog asking whether to purge data directory (`--with-data` vs `--keep-data`).
  - **Detail (`[📋 Detail]`)**: Opens `CloneDetailWindow`.
  - **Edit (`[✏️ Edit]`)**: Opens `CloneEditWindow`.

### 4.3 Feature 3: Clone Parameter Editing (`CloneEditWindow`)
- Editable parameters: Display name (`display_name`) and `ProxyConfig` fields.
- Read-only parameters: Source path, Bundle ID, Engine strategy, Destination path, Data directory.
- Updates persisted via `StateManager.add()`, and re-signs/updates launcher if proxy changed.

### 4.4 Feature 4: Recipe Management (`RecipeListView` & `RecipeEditWindow`)
- Displays both built-in recipes (read-only flag) and user recipes in `~/.atbclone/recipes/`.
- Actions:
  - **Add (`[➕ New]`)**: Opens `RecipeEditWindow` to create custom recipe.
  - **Edit (`[✏️ Edit]`)**: Edits user recipes.
  - **Duplicate as Custom (`[📋 Copy]`)**: Clones a built-in recipe into `~/.atbclone/recipes/` for customization.
  - **Delete (`[🗑️ Delete]`)**: Deletes custom recipe files.

### 4.5 Feature 5: App Prober (`ProbeView`)
- User selects any `.app` bundle to inspect.
- Calls `AppProber.probe()` asynchronously.
- Renders results: Detected Engine (Chromium/Electron/Gecko/Native), Sandbox status, recommended strategy.
- Offers `[💾 Save to Recipes]` (writes to `~/.atbclone/recipes/<bundle_id>.yaml`) and `[📋 Copy YAML]`.

### 4.6 Feature 6: Environment Doctor (`DoctorView`)
- Evaluates system prerequisites (Xcode Command Line Tools, `codesign`, `PlistBuddy`, Python runtime).
- Renders clear checklist with status indicators (✅ / ⚠️ / ❌) and remediation steps.
- Includes `[🔄 Re-check]` button.

---

## 5. Directory Structure & Files

```
src/atbclone/
├── gui/
│   ├── __init__.py          # Briefcase entry: app = build_app()
│   ├── app.py               # toga.App main class, window setup, toolbar
│   ├── views/
│   │   ├── __init__.py
│   │   ├── clone_list.py    # CloneListView
│   │   ├── recipe_list.py   # RecipeListView
│   │   ├── probe_view.py    # ProbeView
│   │   └── doctor_view.py   # DoctorView
│   ├── windows/
│   │   ├── __init__.py
│   │   ├── wizard.py        # WizardWindow (7 steps)
│   │   ├── clone_detail.py  # CloneDetailWindow
│   │   ├── clone_edit.py    # CloneEditWindow
│   │   └── recipe_edit.py   # RecipeEditWindow
│   └── services/
│       ├── __init__.py
│       ├── clone_service.py  # Async wrappers for clone/update/remove
│       ├── probe_service.py  # Async wrapper for probing
│       ├── recipe_service.py # Recipe CRUD & custom file persistence
│       └── doctor_service.py # System checks logic
```

---

## 6. Build & Packaging Configuration

Briefcase configuration will be added to `pyproject.toml`:
```toml
[tool.briefcase]
project_name = "ATBClone"
bundle = "com.atbclone"
version = "0.6.0"

[tool.briefcase.app.atbclone-gui]
formal_name = "ATBClone"
description = "macOS App Cloning Engine"
sources = ["src/atbclone"]
requires = [
    "toga>=0.4",
    "pydantic>=2.0",
    "pyyaml>=6.0",
]

[tool.briefcase.app.atbclone-gui.macOS]
requires = [
    "std-nslog",
]
```
