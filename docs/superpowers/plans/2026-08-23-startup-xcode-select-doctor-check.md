# Startup Defensive Xcode-Select Check Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement startup defensive checking of `xcode-select -p`, automatic redirection to Doctor self-inspection view on failure, and guided one-click invocation of macOS native 2GB Xcode Command Line Tools installer.

**Architecture:** 
- `DoctorService` encapsulates asynchronous execution of `xcode-select -p` and `xcode-select --install` via subprocess runners.
- `ATBCloneApp.startup()` schedules non-blocking startup check and triggers view navigation to "doctor" when prerequisites are missing.
- `DoctorView` dynamically renders an install action button and handles interactive installation feedback with Toga dialogs.
- `i18n.py` provides complete multi-language dictionary entries across 9 locales.

**Tech Stack:** Python 3.12, BeeWare Toga, macOS Cocoa AppKit, Pytest.

## Global Constraints
- Target macOS native patterns, PySide6/Toga, Python 3.12+ with conda env `ATBClone`.
- Run tests via `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/`.
- Maintain strict multi-language support across all 9 locales: `zh`, `en`, `zh_TW`, `ja`, `ko`, `de`, `fr`, `ru`, `es`.
- Never block the UI event loop; execute system subprocesses via asyncio executor.

---

### Task 1: Add i18n Localization Entries for Doctor Actions & Dialogs

**Files:**
- Modify: `src/atbclone/core/i18n.py`
- Test: `tests/test_i18n.py`

**Interfaces:**
- Produces translation keys:
  - `doctor_btn_install_xcode`
  - `doctor_hint_xcode_select`
  - `doctor_dialog_install_title`
  - `doctor_dialog_install_msg`
  - `doctor_dialog_install_already_msg`
  - `doctor_dialog_install_error_msg`

- [ ] **Step 1: Write test for new i18n keys**

Add test in `tests/test_i18n.py`:
```python
def test_doctor_install_i18n_keys():
    from atbclone.core.i18n import t, set_locale
    for lang in ["en", "zh", "zh_TW", "ja", "ko", "de", "fr", "ru", "es"]:
        set_locale(lang)
        assert t("doctor_btn_install_xcode") != "doctor_btn_install_xcode"
        assert t("doctor_hint_xcode_select") != "doctor_hint_xcode_select"
        assert t("doctor_dialog_install_title") != "doctor_dialog_install_title"
        assert t("doctor_dialog_install_msg") != "doctor_dialog_install_msg"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_i18n.py -k test_doctor_install_i18n_keys`
Expected: FAIL due to missing keys in `_TRANSLATIONS`.

- [ ] **Step 3: Implement new i18n keys in `src/atbclone/core/i18n.py`**

Add translation dictionary definitions for all 9 languages for `doctor_btn_install_xcode`, `doctor_hint_xcode_select`, `doctor_dialog_install_title`, `doctor_dialog_install_msg`, `doctor_dialog_install_already_msg`, `doctor_dialog_install_error_msg`.

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_i18n.py`
Expected: PASS

---

### Task 2: Implement `DoctorService` Xcode Check and Installer Methods

**Files:**
- Modify: `src/atbclone/gui/services/doctor_service.py`
- Test: `tests/gui/test_services.py`

**Interfaces:**
- Consumes: Subprocess execution & asyncio loop executor
- Produces:
  - `DoctorService.check_xcode_select_installed() -> bool`
  - `DoctorService.trigger_xcode_install() -> tuple[bool, str]`

- [ ] **Step 1: Write failing tests in `tests/gui/test_services.py`**

```python
import pytest
from unittest.mock import patch, MagicMock
from atbclone.gui.services.doctor_service import DoctorService

@pytest.mark.anyio
async def test_check_xcode_select_installed_success():
    service = DoctorService()
    with patch("subprocess.check_output", return_value="/Applications/Xcode.app/Contents/Developer\n"):
        assert await service.check_xcode_select_installed() is True

@pytest.mark.anyio
async def test_check_xcode_select_installed_failure():
    service = DoctorService()
    with patch("subprocess.check_output", side_effect=Exception("not found")):
        assert await service.check_xcode_select_installed() is False

@pytest.mark.anyio
async def test_trigger_xcode_install_success():
    service = DoctorService()
    mock_res = MagicMock(returncode=0, stderr="", stdout="install requested")
    with patch("subprocess.run", return_value=mock_res):
        success, code = await service.trigger_xcode_install()
        assert success is True
        assert code == "launched"

@pytest.mark.anyio
async def test_trigger_xcode_install_already_installed():
    service = DoctorService()
    mock_res = MagicMock(returncode=1, stderr="command line tools are already installed", stdout="")
    with patch("subprocess.run", return_value=mock_res):
        success, code = await service.trigger_xcode_install()
        assert success is True
        assert code == "already_installed"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/gui/test_services.py -k "test_check_xcode or test_trigger_xcode"`
Expected: FAIL with AttributeError (`check_xcode_select_installed` not defined).

- [ ] **Step 3: Implement methods in `src/atbclone/gui/services/doctor_service.py`**

Implement:
```python
async def check_xcode_select_installed(self) -> bool:
    loop = asyncio.get_running_loop()
    def _check():
        try:
            out = subprocess.check_output("xcode-select -p", shell=True, stderr=subprocess.STDOUT, text=True).strip()
            return bool(out and Path(out).exists())
        except Exception:
            return False
    return await loop.run_in_executor(None, _check)

async def trigger_xcode_install(self) -> tuple[bool, str]:
    loop = asyncio.get_running_loop()
    def _install():
        try:
            res = subprocess.run(["xcode-select", "--install"], capture_output=True, text=True)
            err = (res.stderr or "").lower()
            out = (res.stdout or "").lower()
            if res.returncode == 0 or "install requested" in out or "install requested" in err:
                return True, "launched"
            if "already installed" in err or "already installed" in out:
                return True, "already_installed"
            return False, res.stderr.strip() or "Unknown error"
        except Exception as e:
            return False, str(e)
    return await loop.run_in_executor(None, _install)
```
Update `check_environment()` to use `t("doctor_hint_xcode_select")`.

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/gui/test_services.py`
Expected: PASS

---

### Task 3: Enhance `DoctorView` with Install Action Button & Dialogs

**Files:**
- Modify: `src/atbclone/gui/views/doctor_view.py`
- Test: `tests/gui/test_probe_and_doctor_ui.py`

**Interfaces:**
- Consumes: `DoctorService.trigger_xcode_install()`, `i18n.t`
- Produces: `DoctorView.btn_install_xcode`, `DoctorView.action_install_xcode()`

- [ ] **Step 1: Write failing tests in `tests/gui/test_probe_and_doctor_ui.py`**

Test that:
- `DoctorView` creates `btn_install_xcode` in summary card.
- `run_checks()` sets `btn_install_xcode.style.visibility = "visible"` when `xcode-select` fails, and `"hidden"` when it passes.
- Calling `action_install_xcode` triggers `trigger_xcode_install()` and opens the info dialog.

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/gui/test_probe_and_doctor_ui.py`
Expected: FAIL (`btn_install_xcode` attribute missing).

- [ ] **Step 3: Implement UI updates in `src/atbclone/gui/views/doctor_view.py`**

- Add `self.btn_install_xcode` in `inner_summary` with `Theme.COLOR_PRIMARY` styling and `visibility="hidden"`.
- In `run_checks()`, toggle visibility based on `xcode-select` check result.
- Implement `action_install_xcode(widget)`:
  - Disables button.
  - Calls `await self.doctor_service.trigger_xcode_install()`.
  - Shows `self.app_instance.main_window.info_dialog(...)`.
  - Re-enables button.

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/gui/test_probe_and_doctor_ui.py`
Expected: PASS

---

### Task 4: Add Startup Defensive Check & Auto-Redirection in `ATBCloneApp`

**Files:**
- Modify: `src/atbclone/gui/app.py`
- Test: `tests/gui/test_app_integration.py`

**Interfaces:**
- Consumes: `DoctorService.check_xcode_select_installed()`, `SidebarNav.select_item()`, `switch_view()`
- Produces: `ATBCloneApp._startup_environment_check()`

- [ ] **Step 1: Write failing tests in `tests/gui/test_app_integration.py`**

```python
@pytest.mark.anyio
async def test_startup_environment_check_redirects_on_missing():
    app = ATBCloneApp()
    app.doctor_service.check_xcode_select_installed = AsyncMock(return_value=False)
    app.sidebar.select_item = MagicMock()
    
    await app._startup_environment_check()
    app.sidebar.select_item.assert_called_with("doctor")

@pytest.mark.anyio
async def test_startup_environment_check_stays_on_normal():
    app = ATBCloneApp()
    app.doctor_service.check_xcode_select_installed = AsyncMock(return_value=True)
    app.sidebar.select_item = MagicMock()
    
    await app._startup_environment_check()
    app.sidebar.select_item.assert_not_called()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/gui/test_app_integration.py -k "test_startup_environment_check"`
Expected: FAIL (`_startup_environment_check` not defined).

- [ ] **Step 3: Implement `_startup_environment_check()` in `src/atbclone/gui/app.py`**

- In `startup()`, add:
  ```python
  self.safe_create_task(self._startup_environment_check())
  ```
- Implement `_startup_environment_check()`:
  ```python
  async def _startup_environment_check(self):
      logger.info("Executing defensive startup environment check for xcode-select...")
      is_installed = await self.doctor_service.check_xcode_select_installed()
      if not is_installed:
          logger.warning("xcode-select toolchain missing! Redirecting to doctor view.")
          self.sidebar.select_item("doctor")
  ```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/gui/test_app_integration.py`
Expected: PASS

---

### Task 5: Full Regression Testing & Verification

**Files:**
- Entire test suite `tests/`

- [ ] **Step 1: Run complete automated test suite**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/`
Expected: All 354+ tests pass cleanly with 0 errors and 0 warnings.

- [ ] **Step 2: Verify code formatting and linting**

Verify that all touched files conform to project conventions.
