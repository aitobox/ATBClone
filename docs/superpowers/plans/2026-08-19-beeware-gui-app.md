# ATBClone BeeWare (Toga) GUI Native Application Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a native macOS GUI application for ATBClone using BeeWare (Toga + Briefcase) that provides an interactive wizard, clone lifecycle management, parameter editing, recipe explorer/editor, app prober, and doctor checks while directly reusing existing core logic.

**Architecture:** A decoupled Model-View-Service architecture where Toga UI views trigger async tasks in `services/`, which execute synchronous `core/` and `recipes/` methods inside an `asyncio` executor. The existing CLI and core code remain intact.

**Tech Stack:** Python 3.10+, BeeWare Toga (`toga>=0.4.0`), Briefcase, Pydantic v2, PyYAML, pytest, pytest-mock.

## Global Constraints
- Target platform: macOS (Cocoa / AppKit via Toga)
- Direct code reuse: Import from `atbclone.core` and `atbclone.recipes` without modifying existing core logic or introducing CLI dependencies
- Threading model: Non-blocking UI; long-running operations executed asynchronously via `asyncio.get_event_loop().run_in_executor()`
- Storage compliance: State stored in `~/.atbclone/clones.yaml`, custom recipes in `~/.atbclone/recipes/`

---

### Task 1: Briefcase Packaging Configuration & GUI Module Scaffolding

**Files:**
- Modify: `pyproject.toml`
- Create: `src/atbclone/gui/__init__.py`
- Test: `tests/gui/test_scaffolding.py`

**Interfaces:**
- Consumes: Package metadata
- Produces: `atbclone.gui.main` entry point and package layout

- [ ] **Step 1: Write test for GUI module import and Briefcase entry point**
```python
def test_gui_module_exports_main():
    import atbclone.gui
    assert hasattr(atbclone.gui, "main") or hasattr(atbclone.gui, "build_app")
```

- [ ] **Step 2: Run test to verify it fails**
Run: `PYTHONPATH=src pytest tests/gui/test_scaffolding.py -v`
Expected: FAIL (ModuleNotFoundError or AttributeError)

- [ ] **Step 3: Update `pyproject.toml` and scaffold `src/atbclone/gui/__init__.py`**
Add Briefcase configuration:
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
    "toga>=0.4.0",
    "pydantic>=2.0",
    "pyyaml>=6.0",
]

[tool.briefcase.app.atbclone-gui.macOS]
requires = [
    "std-nslog",
]
```
Create `src/atbclone/gui/__init__.py` with `main` and `build_app`.

- [ ] **Step 4: Run test to verify it passes**
Run: `PYTHONPATH=src pytest tests/gui/test_scaffolding.py -v`
Expected: PASS

---

### Task 2: Service Layer for Core Asynchronous Execution

**Files:**
- Create: `src/atbclone/gui/services/__init__.py`
- Create: `src/atbclone/gui/services/clone_service.py`
- Create: `src/atbclone/gui/services/recipe_service.py`
- Create: `src/atbclone/gui/services/probe_service.py`
- Create: `src/atbclone/gui/services/doctor_service.py`
- Test: `tests/gui/test_services.py`

**Interfaces:**
- Consumes: `atbclone.core.StateManager`, `atbclone.core.CloneEngine`, `atbclone.core.AppProber`, `atbclone.recipes.loader.RecipeLoader`
- Produces:
  - `CloneService`: `async list_clones() -> list[CloneRecord]`, `async update_clone(name) -> None`, `async remove_clone(name, with_data: bool) -> None`, `async create_clone(task: CloneTask) -> None`
  - `RecipeService`: `async list_all_recipes() -> list[dict]`, `async save_custom_recipe(recipe: Recipe) -> None`, `async delete_custom_recipe(bundle_id: str) -> bool`
  - `ProbeService`: `async probe_app(app_path: Path) -> tuple[AppInfo, Recipe]`
  - `DoctorService`: `async check_environment() -> list[DoctorItem]`

- [ ] **Step 1: Write failing tests for all services**
Test listing clones, saving recipes, running probes, and running doctor checks asynchronously with mocked dependencies.

- [ ] **Step 2: Run test to verify it fails**
Run: `PYTHONPATH=src pytest tests/gui/test_services.py -v`
Expected: FAIL

- [ ] **Step 3: Implement Services**
Implement `CloneService`, `RecipeService`, `ProbeService`, and `DoctorService` utilizing `asyncio.get_event_loop().run_in_executor()`.

- [ ] **Step 4: Run test to verify it passes**
Run: `PYTHONPATH=src pytest tests/gui/test_services.py -v`
Expected: PASS

---

### Task 3: Recipe Explorer View & Recipe Editor Window

**Files:**
- Create: `src/atbclone/gui/views/recipe_list.py`
- Create: `src/atbclone/gui/windows/recipe_edit.py`
- Test: `tests/gui/test_recipe_ui.py`

**Interfaces:**
- Consumes: `RecipeService`, `atbclone.recipes.models.Recipe`
- Produces: `RecipeListView(toga.Box)`, `RecipeEditWindow(toga.Window)`

- [ ] **Step 1: Write unit tests for RecipeListView and RecipeEditWindow logic**
Verify form population, validation, and calling `RecipeService.save_custom_recipe()`.

- [ ] **Step 2: Run test to verify it fails**
Run: `PYTHONPATH=src pytest tests/gui/test_recipe_ui.py -v`
Expected: FAIL

- [ ] **Step 3: Implement RecipeListView and RecipeEditWindow**
Build list view showing built-in (read-only) vs user recipes, with Add/Edit/Copy/Delete actions and modal form window for YAML field editing.

- [ ] **Step 4: Run test to verify it passes**
Run: `PYTHONPATH=src pytest tests/gui/test_recipe_ui.py -v`
Expected: PASS

---

### Task 4: App Prober View & Doctor Diagnostic View

**Files:**
- Create: `src/atbclone/gui/views/probe_view.py`
- Create: `src/atbclone/gui/views/doctor_view.py`
- Test: `tests/gui/test_probe_and_doctor_ui.py`

**Interfaces:**
- Consumes: `ProbeService`, `DoctorService`
- Produces: `ProbeView(toga.Box)`, `DoctorView(toga.Box)`

- [ ] **Step 1: Write tests for ProbeView and DoctorView**
Verify asynchronous probe execution, UI status rendering, and doctor check display.

- [ ] **Step 2: Run test to verify it fails**
Run: `PYTHONPATH=src pytest tests/gui/test_probe_and_doctor_ui.py -v`
Expected: FAIL

- [ ] **Step 3: Implement ProbeView and DoctorView**
- `ProbeView`: File selector, probe trigger, architecture & sandbox breakdown, and "Save to Recipes" button.
- `DoctorView`: Status table of prerequisites (Xcode tools, codesign, PlistBuddy, Python), diagnostic icons (✅/⚠️/❌), and remediation guidelines.

- [ ] **Step 4: Run test to verify it passes**
Run: `PYTHONPATH=src pytest tests/gui/test_probe_and_doctor_ui.py -v`
Expected: PASS

---

### Task 5: Clone List View, Detail Window & Parameter Edit Window

**Files:**
- Create: `src/atbclone/gui/views/clone_list.py`
- Create: `src/atbclone/gui/windows/clone_detail.py`
- Create: `src/atbclone/gui/windows/clone_edit.py`
- Test: `tests/gui/test_clone_views.py`

**Interfaces:**
- Consumes: `CloneService`, `atbclone.core.state.CloneRecord`
- Produces: `CloneListView(toga.Box)`, `CloneDetailWindow(toga.Window)`, `CloneEditWindow(toga.Window)`

- [ ] **Step 1: Write tests for CloneListView, CloneDetailWindow, and CloneEditWindow**
Verify clone listing, selection triggering detail window, edit window saving updated proxy/display_name to StateManager.

- [ ] **Step 2: Run test to verify it fails**
Run: `PYTHONPATH=src pytest tests/gui/test_clone_views.py -v`
Expected: FAIL

- [ ] **Step 3: Implement CloneListView, CloneDetailWindow, and CloneEditWindow**
- `CloneListView`: Table listing clones, action toolbar (Update, Edit, Detail, Delete).
- `CloneDetailWindow`: Inspector view displaying bundle info, paths, strategy, proxy summary.
- `CloneEditWindow`: Modal allowing editing of display name and proxy parameters.

- [ ] **Step 4: Run test to verify it passes**
Run: `PYTHONPATH=src pytest tests/gui/test_clone_views.py -v`
Expected: PASS

---

### Task 6: 7-Step Interactive Cloning Wizard Window

**Files:**
- Create: `src/atbclone/gui/windows/wizard.py`
- Test: `tests/gui/test_wizard_window.py`

**Interfaces:**
- Consumes: `CloneService`, `ProbeService`, `RecipeService`, `atbclone.core.AppInspector`
- Produces: `WizardWindow(toga.Window)`

- [ ] **Step 1: Write tests for wizard navigation and parameter compilation**
Test step progression (Step 1 -> Step 7), validation, name suggestion, custom data directory gating, and `CloneTask` creation.

- [ ] **Step 2: Run test to verify it fails**
Run: `PYTHONPATH=src pytest tests/gui/test_wizard_window.py -v`
Expected: FAIL

- [ ] **Step 3: Implement WizardWindow**
Build 7-step wizard with step indicator, Previous/Next navigation, auto-probing fallback, data-dir support check, proxy config, and asynchronous execution with progress log output.

- [ ] **Step 4: Run test to verify it passes**
Run: `PYTHONPATH=src pytest tests/gui/test_wizard_window.py -v`
Expected: PASS

---

### Task 7: Main Application Assembly, Navigation Router & End-to-End Verification

**Files:**
- Create: `src/atbclone/gui/app.py`
- Modify: `src/atbclone/gui/__init__.py`
- Test: `tests/gui/test_app_integration.py`

**Interfaces:**
- Consumes: `CloneListView`, `RecipeListView`, `ProbeView`, `DoctorView`, `WizardWindow`
- Produces: `ATBCloneApp(toga.App)`

- [ ] **Step 1: Write integration tests for main app lifecycle and view routing**
Verify main window creation, sidebar switching between Clone / Recipe / Probe / Doctor views, and toolbar action triggers.

- [ ] **Step 2: Run test to verify it fails**
Run: `PYTHONPATH=src pytest tests/gui/test_app_integration.py -v`
Expected: FAIL

- [ ] **Step 3: Implement ATBCloneApp and main entry points**
Assemble `ATBCloneApp` in `src/atbclone/gui/app.py` with `toga.SplitContainer`, dynamic content switching, menu items, and toolbar shortcuts.

- [ ] **Step 4: Run all test suites and verify**
Run: `PYTHONPATH=src pytest tests/ -v`
Expected: All unit and integration tests pass.
