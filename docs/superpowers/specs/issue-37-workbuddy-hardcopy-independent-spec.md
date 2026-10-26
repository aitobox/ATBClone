# Specification: Issue #37 - WorkBuddy 物理克隆分身独立运行及单例冲突修复

## 1. Background & Problem Statement
When cloning WorkBuddy (`com.tencent.workbuddy.mac` / `com.workbuddy.workbuddy-ai`) using physical hard clone (`hard_clone`), ATBClone's prober previously grouped Electron apps with Chromium browsers and assigned `--user-data-dir={{ATB_DATA_DIR}}` with empty environment injection (`env_injection = {}`).

However:
1. Electron desktop applications on macOS do not parse `--user-data-dir` for `userData` or `ProcessSingleton` locks.
2. WorkBuddy natively relies on environment variables `WORKBUDDY_USER_DATA_DIR`, `WORKBUDDY_CONFIG_DIR`, and `HOME`.
3. Because `--user-data-dir` was passed and `HOME`/`TMPDIR` were missing from the environment, both instances pointed to the default `~/.workbuddy/app/` directory and shared the `ProcessSingleton` lock socket (`SingletonSocket`).
4. On startup, the cloned app detected the held lock, emitted a `second-instance` IPC event to the existing WorkBuddy instance (causing it to restore and focus its window), and immediately exited.

## 2. Architecture & Design

### 2.1 Built-in Recipes
Add built-in recipe files:
- `src/atbclone/recipes/builtin/com.tencent.workbuddy.mac.yaml`
- `src/atbclone/recipes/builtin/com.workbuddy.workbuddy-ai.yaml`

Specifications:
- `strategy: hard_clone`
- `app_type: electron`
- `strip_sandbox: true`
- `strip_url_schemes: true`
- `launch_args: []`
- `environment_injection`:
  - `HOME: '{{ATB_DATA_DIR}}/Home'`
  - `TMPDIR: '{{ATB_DATA_DIR}}/Tmp'`
  - `WORKBUDDY_CONFIG_DIR: '{{ATB_DATA_DIR}}/Config'`
  - `WORKBUDDY_USER_DATA_DIR: '{{ATB_DATA_DIR}}/UserData'`
- `symlink_whitelist`:
  - `Library/Keychains`

### 2.2 Prober Improvements (`src/atbclone/core/app_prober.py`)
- Refactor `AppProber.analyze()`: Separate `app_type == "electron"` from `app_type == "chromium"`.
  - `chromium`: Web browsers (Chrome, Edge, Brave) remain `strategy = "soft_clone"` with `launch_args = ["--user-data-dir={{ATB_DATA_DIR}}"]`.
  - `electron`: Generic Electron apps default to `strategy = "hard_clone"` with `strip_sandbox = has_sandbox`, `launch_args = []`, and `env_injection = {"HOME": "{{ATB_DATA_DIR}}/Home", "TMPDIR": "{{ATB_DATA_DIR}}/Tmp"}`.
  - WorkBuddy detection: If bundle ID or app name matches WorkBuddy, inject `WORKBUDDY_CONFIG_DIR` and `WORKBUDDY_USER_DATA_DIR` automatically.

### 2.3 Engine Improvements (`src/atbclone/core/engines.py`)
- In `HardCloneEngine`:
  - Detect `is_workbuddy` (via `com.tencent.workbuddy.mac`, `com.workbuddy.workbuddy-ai`, or `patch_workbuddy_isolation`).
  - Force `use_dylib = False` (use native C launcher with environment injection).
  - Inject `WORKBUDDY_CONFIG_DIR` and `WORKBUDDY_USER_DATA_DIR` into `effective_env` if not already present.
  - Build `_build_workbuddy_isolation_cmd`: Compiles `libatbclone_workbuddy_hook.dylib` and injects via `DYLD_INSERT_LIBRARIES` to interpose Cocoa and POSIX home/app-support directory calls.
  - Ensure URL schemes are stripped for WorkBuddy (`strip_url_schemes: true`).
  - Guarantee that for any `electron` app, `HOME` and `TMPDIR` are always present in `effective_env`.

## 3. Implementation Task List

- [ ] Task 1: Create WorkBuddy builtin recipes (`com.tencent.workbuddy.mac.yaml` & `com.workbuddy.workbuddy-ai.yaml`)
- [ ] Task 2: Enhance `AppProber` in `src/atbclone/core/app_prober.py` to differentiate Electron from Chromium and probe WorkBuddy with proper environment variables
- [ ] Task 3: Enhance `HardCloneEngine` in `src/atbclone/core/engines.py` with WorkBuddy isolation hook and Electron environment guarantees
- [ ] Task 4: Add comprehensive unit tests in `tests/test_workbuddy_isolation.py`
- [ ] Task 5: Run full test suite (`pytest tests/`) to ensure 100% pass with zero regressions
- [ ] Task 6: Audit deliverables via `grill-me` before code review handoff
