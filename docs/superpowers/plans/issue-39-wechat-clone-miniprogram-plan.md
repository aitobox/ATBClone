# Implementation Plan: Issue #39 - WeChat Clone Mini Programs Runtime Fix

## Objective
Fix WeChat physical cloning (`hard_clone`) so that mini programs (`WeChatAppEx.app` / WMPF / CEF runtime) work properly in cloned instances, preserving nested helper bundles and removing sandbox inheritance restrictions during codesigning.

---

### Task 1: Enhance `_build_process_name_cmd` in `src/atbclone/core/engines.py`
**File to modify**:
- `src/atbclone/core/engines.py`

**Changes**:
1. Expand `is_chromium` detection in `_build_process_name_cmd`:
   - Add checks for `WeChatAppEx.app`, `WeChatAppEx*.framework`, `WMPF*.framework`, and recursive `Contents/**/*Helper*.app`.
   - Propagate to both the outer Python check and the embedded bash script.
2. In the `os.walk` directory walker:
   - Identify nested `.app` bundles under `Contents/` (e.g. `any(p.endswith(".app") for p in dir_path.relative_to(app).parts[:-1])` or relative traversal checks) and skip them to ensure no nested sub-application's binaries or plists are modified.
   - For `is_chromium` apps, strictly enforce that only the root `main` binary and `entry` launcher are renamed.

**Verification**:
```bash
PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_process_names.py
```

---

### Task 2: Enhance Codesigning in `HardCloneEngine.execute`
**File to modify**:
- `src/atbclone/core/engines.py`

**Changes**:
1. When `task.recipe.strip_sandbox` is `True`:
   - Delete `com.apple.security.inherit` from `$ent_plist` using PlistBuddy.
   - Include `'com.apple.security.inherit'` in the Python entitlements cleaner's `restricted` tuple.
2. Sign nested `.app` and `.framework` sub-bundles inside-out (deepest first, sorted by path depth/length descending) so that embedded framework helpers (`Versions/C/Helpers/*.app`) are signed before their enclosing framework and parent application.

**Verification**:
```bash
PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_engines.py
```

---

### Task 3: Add Regression Unit Tests
**File to modify**:
- `tests/test_process_names.py`
- `tests/test_engines.py`

**Test Cases**:
1. `test_wechat_nested_appex_and_helpers_preserved`:
   - Simulates a Cocoa app with `Contents/MacOS/WeChatAppEx.app` and `Contents/MacOS/WeChatAppEx.app/Contents/Frameworks/WeChatAppEx Framework.framework/Versions/C/Helpers/WeChatAppEx Helper.app`.
   - Asserts root binary is renamed to clone name.
   - Asserts `WeChatAppEx` executable and `WeChatAppEx Helper` executables remain untampered with original names and unmodified `Info.plist`.
2. `test_hard_clone_engine_strips_sandbox_and_inherit`:
   - Verifies that generated codesigning script removes both `com.apple.security.app-sandbox` and `com.apple.security.inherit`.

**Verification**:
```bash
PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_process_names.py tests/test_engines.py
```

---

### Task 4: Run Full Project Test Suite
**Command**:
```bash
PYTHONPATH=src conda run -n ATBClone python -m pytest tests/
```

---

### Task 5: Audit & Handoff via `grill-me`
**Actions**:
1. Run `grill-me` verification against all deliverables, test outputs, and acceptance criteria.
2. Advance state to `reviewing` in `.github-agent-state.yml`.
3. Hand off to `atb-github-code-reviewer`.
