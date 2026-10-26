# Implementation Plan: Issue #37 - WorkBuddy 物理克隆分身独立运行及单例冲突修复

## Objective
Fix WorkBuddy physical cloning (`hard_clone`) so that cloned WorkBuddy instances run independently without conflicting with or activating existing instances.

---

### Task 1: Create WorkBuddy Builtin Recipes
**Files to create**:
- `src/atbclone/recipes/builtin/com.tencent.workbuddy.mac.yaml`
- `src/atbclone/recipes/builtin/com.workbuddy.workbuddy-ai.yaml`

**Content**:
```yaml
bundle_id: com.tencent.workbuddy.mac (or com.workbuddy.workbuddy-ai)
app_name: WorkBuddy (or WorkBuddy AI)
strategy: hard_clone
app_type: electron
strip_sandbox: true
strip_url_schemes: true
launch_args: []
environment_injection:
  HOME: '{{ATB_DATA_DIR}}/Home'
  TMPDIR: '{{ATB_DATA_DIR}}/Tmp'
  WORKBUDDY_CONFIG_DIR: '{{ATB_DATA_DIR}}/Config'
  WORKBUDDY_USER_DATA_DIR: '{{ATB_DATA_DIR}}/UserData'
symlink_whitelist:
- Library/Keychains
```

**Verification**:
```bash
PYTHONPATH=src conda run -n ATBClone python -c "from atbclone.recipes.loader import RecipeLoader; r = RecipeLoader.get('com.tencent.workbuddy.mac'); assert r and r.strategy == 'hard_clone' and 'WORKBUDDY_USER_DATA_DIR' in r.environment_injection; r2 = RecipeLoader.get('com.workbuddy.workbuddy-ai'); assert r2 and r2.strategy == 'hard_clone'"
```

---

### Task 2: Enhance `AppProber` in `src/atbclone/core/app_prober.py`
**File to modify**:
- `src/atbclone/core/app_prober.py`

**Changes**:
- In `analyze()`:
  - Separate `chromium` and `electron`.
  - For `chromium`: `strategy = "soft_clone"`, `launch_args = ["--user-data-dir={{ATB_DATA_DIR}}"]`.
  - For `electron`: `strategy = "hard_clone"`, `strip_sandbox = has_sandbox`, `launch_args = []`, `env_injection = {"HOME": "{{ATB_DATA_DIR}}/Home", "TMPDIR": "{{ATB_DATA_DIR}}/Tmp"}`.
  - Check if bundle ID or app name matches WorkBuddy (`com.tencent.workbuddy.mac`, `com.workbuddy.workbuddy-ai`, or `workbuddy` in bundle_id/app_name): also add `WORKBUDDY_CONFIG_DIR: "{{ATB_DATA_DIR}}/Config"` and `WORKBUDDY_USER_DATA_DIR: "{{ATB_DATA_DIR}}/UserData"`.

**Verification**:
```bash
PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_app_prober.py
```

---

### Task 3: Enhance `HardCloneEngine` in `src/atbclone/core/engines.py`
**File to modify**:
- `src/atbclone/core/engines.py`

**Changes**:
- Define `_build_workbuddy_isolation_cmd(cls, task: CloneTask) -> str`:
  - Compiles `libatbclone_workbuddy_hook.dylib` in `Contents/Frameworks/`.
  - Strips URL schemes from `Info.plist` if `strip_url_schemes` is enabled.
- Detect `is_workbuddy` in `execute()`:
  - Matches `patch_workbuddy_isolation`, `com.tencent.workbuddy.mac`, `com.workbuddy.workbuddy-ai`.
  - If `is_workbuddy`:
    - `use_dylib = False` (forces C launcher).
    - `hook_dylib_rel_path = "../Frameworks/libatbclone_workbuddy_hook.dylib"`.
    - Ensure `WORKBUDDY_CONFIG_DIR` and `WORKBUDDY_USER_DATA_DIR` are populated in `effective_env`.
- Ensure all `app_type == "electron"` apps guarantee `HOME` and `TMPDIR` in `effective_env`.

**Verification**:
```bash
PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_engines.py
```

---

### Task 4: Add Unit Tests in `tests/test_workbuddy_isolation.py`
**File to create**:
- `tests/test_workbuddy_isolation.py`

**Test Cases**:
1. `test_workbuddy_builtin_recipes`: verifies both recipes load properly with required fields.
2. `test_app_prober_electron_vs_chromium`: verifies `AppProber` assigns `hard_clone` + HOME/TMPDIR to Electron apps and `soft_clone` to Chromium.
3. `test_app_prober_workbuddy_detection`: verifies WorkBuddy probing sets `WORKBUDDY_CONFIG_DIR` and `WORKBUDDY_USER_DATA_DIR`.
4. `test_hard_clone_engine_workbuddy_script`: verifies generated script contains WorkBuddy hook compilation, env variables, and URL scheme stripping.

**Verification**:
```bash
PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_workbuddy_isolation.py
```

---

### Task 5: Full Test Suite Verification
**Command**:
```bash
PYTHONPATH=src conda run -n ATBClone python -m pytest tests/
```
All existing and new tests must pass with 0 errors.

---

### Task 6: Audit via `grill-me`
Verify stress-test scenarios, edge cases, and scope adherence before transitioning state to `reviewing`.
