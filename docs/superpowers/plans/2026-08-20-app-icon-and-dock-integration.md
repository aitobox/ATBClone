# ATBClone App Icon & macOS Dock Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Integrate the application logo (`logo.png` and `logo.icns`) across ATBClone GUI, macOS Dock, window icons, sidebar branding, and packaging build pipelines (Briefcase & Nuitka).

**Architecture:** Create a unified resource locator `atbclone.core.resources` for robust path resolution across development and packaged bundles; add a native Cocoa AppKit bridge to immediately bind the macOS Dock icon during GUI startup; embed the logo image into `SidebarNav`; and configure `pyproject.toml`, `scripts/build_gui.sh`, and `scripts/build_cli.sh` to package the icons.

**Tech Stack:** Python 3.12, BeeWare Toga (toga-cocoa, Rubicon ObjC, AppKit), Pytest, Briefcase, Nuitka.

## Global Constraints

- Python 3.12+ in conda environment `ATBClone`.
- Zero third-party runtime dependencies outside existing stack (`toga`, `pydantic`, `pyyaml`, `click`, `rich`).
- Safe fallback / degradation for Cocoa AppKit calls in non-macOS or headless test environments.
- All existing tests in `tests/` must remain 100% passing (`PYTHONPATH=src conda run -n ATBClone python -m pytest tests/`).

---

### Task 1: Centralized Resource Locator Module

**Files:**
- Create: `src/atbclone/core/resources.py`
- Test: `tests/test_resources.py`

**Interfaces:**
- Produces:
  - `get_resource_dir() -> Path`: Returns the base path to the resource directory.
  - `get_resource_path(relative_path: str) -> Path`: Resolves full path for a relative asset path.
  - `get_app_icon_path(prefer_format: str = "png") -> Path | None`: Returns path to `logo.png` or `logo.icns`.

- [ ] **Step 1: Write failing test for resource locator**

```python
# tests/test_resources.py
from pathlib import Path
import pytest
from atbclone.core.resources import get_resource_dir, get_resource_path, get_app_icon_path


def test_get_resource_dir_exists():
    res_dir = get_resource_dir()
    assert res_dir.exists()
    assert res_dir.is_dir()


def test_get_resource_path_resolves_logo():
    png_path = get_resource_path("images/logo.png")
    assert png_path.exists()
    assert png_path.name == "logo.png"


def test_get_app_icon_path_png():
    icon_path = get_app_icon_path("png")
    assert icon_path is not None
    assert icon_path.exists()
    assert icon_path.suffix == ".png"


def test_get_app_icon_path_icns():
    icon_path = get_app_icon_path("icns")
    assert icon_path is not None
    assert icon_path.exists()
    assert icon_path.suffix == ".icns"


def test_get_app_icon_path_invalid_format():
    icon_path = get_app_icon_path("invalid_format")
    # Falls back to png or icns if exists
    assert icon_path is not None
    assert icon_path.exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_resources.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'atbclone.core.resources'`

- [ ] **Step 3: Implement `src/atbclone/core/resources.py`**

```python
"""Resource management and asset path resolution for ATBClone."""

from pathlib import Path
import sys
from typing import Optional


def get_resource_dir() -> Path:
    """Resolve the root directory containing static assets and resources.

    Resolution order:
    1. Repository root / 'resource' (during local development / source runs)
    2. macOS App Bundle Contents/Resources/resource or Contents/Resources
    3. Frozen bundle directory (sys._MEIPASS or package directory)
    """
    # 1. Check direct development workspace root
    module_dir = Path(__file__).resolve().parent  # src/atbclone/core
    src_dir = module_dir.parent.parent  # src
    repo_root = src_dir.parent  # project root
    candidate_repo = repo_root / "resource"
    if candidate_repo.is_dir():
        return candidate_repo

    # 2. Check macOS app bundle Contents/Resources
    if hasattr(sys, "executable") and sys.executable:
        exe_path = Path(sys.executable).resolve()
        # Typical structure: ATBClone.app/Contents/MacOS/ATBClone -> Resources
        app_contents = exe_path.parent.parent
        bundle_res = app_contents / "Resources" / "resource"
        if bundle_res.is_dir():
            return bundle_res
        bundle_res_direct = app_contents / "Resources"
        if bundle_res_direct.is_dir():
            return bundle_res_direct

    # 3. Check PyInstaller / Nuitka frozen directory
    if hasattr(sys, "_MEIPASS"):
        meipass_res = Path(sys._MEIPASS) / "resource"
        if meipass_res.is_dir():
            return meipass_res

    # 4. Fallback to package-relative directory
    pkg_res = module_dir.parent / "resource"
    if pkg_res.is_dir():
        return pkg_res

    # Default fallback
    return candidate_repo


def get_resource_path(relative_path: str) -> Path:
    """Resolve the absolute path to a specific resource file."""
    base_dir = get_resource_dir()
    resolved = (base_dir / relative_path).resolve()
    if not resolved.exists():
        # Also try direct relative to repo root if base_dir was altered
        module_dir = Path(__file__).resolve().parent
        fallback = (module_dir.parent.parent.parent / "resource" / relative_path).resolve()
        if fallback.exists():
            return fallback
    return resolved


def get_app_icon_path(prefer_format: str = "png") -> Optional[Path]:
    """Retrieve absolute path to application logo icon (.png or .icns)."""
    fmt = prefer_format.lower().lstrip(".")
    if fmt == "icns":
        candidate = get_resource_path("images/logo.icns")
        if candidate.exists():
            return candidate
        fallback_png = get_resource_path("images/logo.png")
        return fallback_png if fallback_png.exists() else None

    # Default prefer png
    candidate = get_resource_path("images/logo.png")
    if candidate.exists():
        return candidate
    fallback_icns = get_resource_path("images/logo.icns")
    return fallback_icns if fallback_icns.exists() else None
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_resources.py -v`
Expected: PASS (5 passed)

---

### Task 2: Native Cocoa Dock Bridge & App / Window Icon Integration

**Files:**
- Modify: `src/atbclone/gui/__init__.py:1-14`
- Modify: `src/atbclone/gui/app.py:1-75`
- Modify: `src/atbclone/gui/windows/wizard.py:25-45`
- Test: `tests/gui/test_app_integration.py`
- Test: `tests/gui/test_wizard_window.py`

**Interfaces:**
- Consumes:
  - `atbclone.core.resources.get_app_icon_path`
- Produces:
  - `atbclone.gui.app.set_macos_dock_icon(icon_path: Path | None = None) -> bool`
  - `atbclone.gui.build_app() -> ATBCloneApp` (with `icon=icon_path`)

- [ ] **Step 1: Write tests for Cocoa Dock bridge & app icon setup**

```python
# In tests/gui/test_app_integration.py
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
from atbclone.gui import build_app
from atbclone.gui.app import set_macos_dock_icon


def test_set_macos_dock_icon_safe():
    # Calling with valid path or None should return boolean and not raise exceptions
    res = set_macos_dock_icon(None)
    assert isinstance(res, bool)


def test_set_macos_dock_icon_with_mock():
    with patch("toga_cocoa.libs.appkit.NSApplication") as mock_app, \
         patch("toga_cocoa.libs.appkit.NSImage") as mock_img:
        mock_ns_img = MagicMock()
        mock_img.alloc.return_value.initWithContentsOfFile_.return_value = mock_ns_img
        
        test_path = Path("resource/images/logo.png")
        success = set_macos_dock_icon(test_path)
        assert success is True
        mock_app.sharedApplication.setApplicationIconImage_.assert_called_once_with(mock_ns_img)


def test_build_app_has_icon():
    app = build_app()
    assert app.icon is not None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/gui/test_app_integration.py -k "test_set_macos_dock_icon or test_build_app_has_icon" -v`
Expected: FAIL (functions not yet added / app not passing icon)

- [ ] **Step 3: Update `src/atbclone/gui/__init__.py`**

```python
"""ATBClone GUI Package (BeeWare Toga)."""

from atbclone.core.resources import get_app_icon_path


def build_app():
    from .app import ATBCloneApp
    icon_path = get_app_icon_path("png")
    return ATBCloneApp("ATBClone", "com.atbclone.app", icon=icon_path)


def main():
    app = build_app()
    return app.main_loop()


__all__ = ["build_app", "main"]
```

- [ ] **Step 4: Update `src/atbclone/gui/app.py`**

Add `set_macos_dock_icon` helper and call it during `ATBCloneApp.startup()`, plus ensure `MainWindow` receives `icon`:

```python
def set_macos_dock_icon(icon_path: Optional[Path] = None) -> bool:
    """Explicitly set application icon on macOS Dock via Cocoa AppKit."""
    if icon_path is None:
        icon_path = get_app_icon_path("png")
    if not icon_path or not icon_path.exists():
        return False
    try:
        from toga_cocoa.libs.appkit import NSApplication, NSImage
        ns_img = NSImage.alloc().initWithContentsOfFile_(str(icon_path))
        if ns_img:
            NSApplication.sharedApplication.setApplicationIconImage_(ns_img)
            return True
    except Exception:
        # Graceful fallback for non-macOS or headless test environments
        pass
    return False
```
Inside `startup()`:
```python
        # Ensure Dock icon is bound
        icon_path = get_app_icon_path("png")
        set_macos_dock_icon(icon_path)

        # Main window setup
        self.main_window = toga.MainWindow(
            title=self.formal_name,
            size=(1020, 680),
            icon=self.icon or icon_path,
        )
```

- [ ] **Step 5: Update `src/atbclone/gui/windows/wizard.py`**

In `WizardWindow.__init__`:
```python
        icon_path = get_app_icon_path("png")
        super().__init__(title="Clone App Wizard", size=(560, 520), icon=icon_path)
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/gui/test_app_integration.py tests/gui/test_wizard_window.py -v`
Expected: PASS

---

### Task 3: Sidebar Navigation Branding

**Files:**
- Modify: `src/atbclone/gui/components/sidebar.py:30-40`
- Modify: `tests/gui/test_sidebar.py`

**Interfaces:**
- Consumes:
  - `atbclone.core.resources.get_app_icon_path`
- Produces:
  - `SidebarNav` brand header featuring `toga.ImageView(toga.Image(...))` + App Title + Version label.

- [ ] **Step 1: Write test for Sidebar branding header**

```python
# In tests/gui/test_sidebar.py
import toga
from atbclone.gui.components.sidebar import SidebarNav


def test_sidebar_brand_header():
    sidebar = SidebarNav(on_select=lambda k: None)
    header_box = sidebar.children[0]
    assert len(header_box.children) >= 1
    # Check that header contains both logo image (if available) and labels
    labels = [c for c in header_box.children if isinstance(c, toga.Label)]
    assert any("ATBClone" in l.text for l in labels) or any(
        isinstance(sub, toga.Box) and any("ATBClone" in l.text for l in sub.children if isinstance(l, toga.Label))
        for sub in header_box.children
    )
```

- [ ] **Step 2: Run test to verify status**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/gui/test_sidebar.py -v`

- [ ] **Step 3: Update `src/atbclone/gui/components/sidebar.py`**

```python
        # Brand header with logo icon
        header_box = toga.Box(style=Pack(direction=ROW, alignment=CENTER, margin=(16, 12, 12, 12)))
        
        logo_path = get_app_icon_path("png")
        if logo_path and logo_path.exists():
            try:
                logo_img = toga.Image(logo_path)
                logo_view = toga.ImageView(logo_img, style=Pack(width=28, height=28, margin_right=8))
                header_box.add(logo_view)
            except Exception:
                pass

        title_box = toga.Box(style=Pack(direction=COLUMN))
        title_label = toga.Label("ATBClone", style=Pack(font_weight="bold", font_size=16, color=Theme.TEXT_PRIMARY))
        ver_label = toga.Label(f"v{__version__} App Cloner", style=Pack(font_size=10, color=Theme.TEXT_MUTED, margin_top=2))
        title_box.add(title_label)
        title_box.add(ver_label)
        header_box.add(title_box)
        self.add(header_box)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/gui/test_sidebar.py tests/gui/test_theme_and_components.py -v`
Expected: PASS

---

### Task 4: Packaging & Build Scripts Integration

**Files:**
- Modify: `pyproject.toml:39-53`
- Modify: `scripts/build_gui.sh:170-220`
- Modify: `scripts/build_cli.sh:150-170`
- Test: `tests/test_build_script.py`

**Interfaces:**
- Produces:
  - Briefcase `pyproject.toml` config declaring `icon = "resource/images/logo"` and `resources = ["resource/images"]`.
  - Nuitka flags in `scripts/build_cli.sh` with `--macos-app-icon=resource/images/logo.icns` and `--include-data-dir=resource=resource`.
  - Icon bundle verification in `scripts/build_gui.sh`.

- [ ] **Step 1: Write test for packaging icon configurations**

```python
# In tests/test_build_script.py
from pathlib import Path


def test_pyproject_contains_briefcase_icon():
    content = Path("pyproject.toml").read_text(encoding="utf-8")
    assert 'icon = "resource/images/logo"' in content


def test_build_cli_contains_macos_icon_flag():
    content = Path("scripts/build_cli.sh").read_text(encoding="utf-8")
    assert "--macos-app-icon=" in content


def test_build_gui_references_icon():
    content = Path("scripts/build_gui.sh").read_text(encoding="utf-8")
    assert "logo.icns" in content or "ATBClone.icns" in content or "icon" in content
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_build_script.py -k "icon" -v`
Expected: FAIL

- [ ] **Step 3: Update `pyproject.toml`**

Add `icon = "resource/images/logo"` and `resources` under `[tool.briefcase.app.atbclone]` and `[tool.briefcase.app.atbclone.macOS]`.

- [ ] **Step 4: Update `scripts/build_cli.sh`**

Add `--macos-app-icon=resource/images/logo.icns` and `--include-data-dir=resource=resource` to Nuitka invocation.

- [ ] **Step 5: Update `scripts/build_gui.sh`**

Add icon verification step in build script checking `.app/Contents/Resources`.

- [ ] **Step 6: Run tests to verify they pass**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_build_script.py -v`
Expected: PASS

---

### Task 5: Full Regression Testing & Verification

**Files:**
- Test: all `tests/`

- [ ] **Step 1: Run full test suite**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/ -v`
Expected: All tests PASS

- [ ] **Step 2: Validate Briefcase build configuration syntax**

Run: `PYTHONPATH=src conda run -n ATBClone python -c "import atbclone.core.resources as r; print('PNG:', r.get_app_icon_path('png')); print('ICNS:', r.get_app_icon_path('icns'))"`
Expected: Prints valid paths to `resource/images/logo.png` and `resource/images/logo.icns`
