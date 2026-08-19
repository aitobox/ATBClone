# Standardize Bundle Identifier Naming Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Standardize cloned app Bundle Identifier naming across ATBClone to `<original_bundle_id>.atbclone.<instance_number>` and centralize generation into `AppInspector.generate_bundle_id`.

**Architecture:** Add a centralized `AppInspector.generate_bundle_id(bundle_id: str, num: int = 1) -> str` helper in core, and update `cmd_clone.py`, `cmd_wizard.py`, and `cmd_update.py` to use it instead of ad-hoc string formatting.

**Tech Stack:** Python 3.12, PySide6/Click CLI, pytest.

## Global Constraints

- Suffix format must be `.atbclone.<num>` (e.g. `com.google.Chrome.atbclone.2`).
- Default / fallback instance index is `1` (e.g. `com.google.Chrome.atbclone.1`).
- All existing unit and integration tests must pass with `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/`.

---

### Task 1: Add `AppInspector.generate_bundle_id` with Unit Tests

**Files:**
- Modify: `src/atbclone/core/app_inspector.py`
- Modify: `tests/test_inspector.py`

**Interfaces:**
- Produces: `AppInspector.generate_bundle_id(bundle_id: str, num: int = 1) -> str`

- [ ] **Step 1: Write failing unit tests for `AppInspector.generate_bundle_id`**

Add tests to `tests/test_inspector.py`:
```python
def test_generate_bundle_id_default_num():
    bundle_id = AppInspector.generate_bundle_id("com.google.Chrome")
    assert bundle_id == "com.google.Chrome.atbclone.1"


def test_generate_bundle_id_custom_num():
    bundle_id = AppInspector.generate_bundle_id("com.tencent.xinWeChat", 2)
    assert bundle_id == "com.tencent.xinWeChat.atbclone.2"


def test_generate_bundle_id_large_num():
    bundle_id = AppInspector.generate_bundle_id("org.mozilla.firefox", 10)
    assert bundle_id == "org.mozilla.firefox.atbclone.10"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_inspector.py -k "test_generate_bundle_id" -v`
Expected: FAIL with `AttributeError: type object 'AppInspector' has no attribute 'generate_bundle_id'`

- [ ] **Step 3: Implement `AppInspector.generate_bundle_id`**

Add static method to `src/atbclone/core/app_inspector.py`:
```python
    @staticmethod
    def generate_bundle_id(bundle_id: str, num: int = 1) -> str:
        """Generate standardized bundle identifier for a cloned application instance."""
        return f"{bundle_id}.atbclone.{num}"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_inspector.py -k "test_generate_bundle_id" -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add src/atbclone/core/app_inspector.py tests/test_inspector.py
git commit -m "feat(core): add AppInspector.generate_bundle_id helper"
```

---

### Task 2: Update CLI `clone` and `wizard` Commands and Tests

**Files:**
- Modify: `src/atbclone/cli/cmd_clone.py:69-71`
- Modify: `src/atbclone/cli/cmd_wizard.py:102-104`
- Modify: `tests/test_cmd_clone.py`
- Modify: `tests/test_cmd_wizard.py`

**Interfaces:**
- Consumes: `AppInspector.generate_bundle_id(bundle_id: str, num: int = 1) -> str`

- [ ] **Step 1: Update assertions in `tests/test_cmd_clone.py` and `tests/test_cmd_wizard.py`**

In `tests/test_cmd_clone.py`:
- Replace all occurrences of `"com.tencent.xinWeChat.atb2"` with `"com.tencent.xinWeChat.atbclone.2"`.

In `tests/test_cmd_wizard.py`:
- Replace all occurrences of `"com.tencent.xinWeChat.atb2"` with `"com.tencent.xinWeChat.atbclone.2"`.

- [ ] **Step 2: Run tests to verify failures**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_cmd_clone.py tests/test_cmd_wizard.py -v`
Expected: FAIL due to mismatch (`com.tencent.xinWeChat.atb2` vs `com.tencent.xinWeChat.atbclone.2`)

- [ ] **Step 3: Update `cmd_clone.py` and `cmd_wizard.py` implementation**

In `src/atbclone/cli/cmd_clone.py`:
Replace:
```python
    clone_name, num = AppInspector.next_available_name(name or info.app_name, out_path)
    new_bundle_id = f"{info.bundle_id}.atb{num}"
```
With:
```python
    clone_name, num = AppInspector.next_available_name(name or info.app_name, out_path)
    new_bundle_id = AppInspector.generate_bundle_id(info.bundle_id, num)
```

In `src/atbclone/cli/cmd_wizard.py`:
Replace:
```python
    clone_name, num = AppInspector.next_available_name(name or info.app_name, out_path)
    new_bundle_id = f"{info.bundle_id}.atb{num}"
```
With:
```python
    clone_name, num = AppInspector.next_available_name(name or info.app_name, out_path)
    new_bundle_id = AppInspector.generate_bundle_id(info.bundle_id, num)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_cmd_clone.py tests/test_cmd_wizard.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/atbclone/cli/cmd_clone.py src/atbclone/cli/cmd_wizard.py tests/test_cmd_clone.py tests/test_cmd_wizard.py
git commit -m "feat(cli): standardize bundle id generation in clone and wizard commands"
```

---

### Task 3: Update CLI `update` Command and Tests

**Files:**
- Modify: `src/atbclone/cli/cmd_update.py:57-59`
- Modify: `tests/test_cmd_update.py`

**Interfaces:**
- Consumes: `AppInspector.generate_bundle_id(bundle_id: str, num: int = 1) -> str`

- [ ] **Step 1: Update fixtures and fallback assertions in `tests/test_cmd_update.py`**

In `tests/test_cmd_update.py`:
- Update `mock_record_user_dir`, `mock_record_admin_dir`, `mock_record_soft_clone` to use `new_bundle_id="com.tencent.xinWeChat.atbclone.2"` / `new_bundle_id="com.google.Chrome.atbclone.2"`.
- Update any test testing empty `record.new_bundle_id` fallback to expect `AppInspector.generate_bundle_id(record.bundle_id, 1)` -> `"com.tencent.xinWeChat.atbclone.1"`.

- [ ] **Step 2: Update `cmd_update.py` implementation**

In `src/atbclone/cli/cmd_update.py`:
Replace:
```python
        new_bundle_id = record.new_bundle_id or f"{record.bundle_id}.atb1"
```
With:
```python
        new_bundle_id = record.new_bundle_id or AppInspector.generate_bundle_id(record.bundle_id, 1)
```

- [ ] **Step 3: Run tests to verify they pass**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_cmd_update.py -v`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add src/atbclone/cli/cmd_update.py tests/test_cmd_update.py
git commit -m "feat(cli): standardize fallback bundle id generation in update command"
```

---

### Task 4: Full Test Suite Verification

**Files:**
- None (verification only)

- [ ] **Step 1: Run complete test suite**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/`
Expected: PASS (all tests pass)

- [ ] **Step 2: Commit plan document**

```bash
git add docs/superpowers/plans/2026-08-19-bundle-id-naming-standard.md
git commit -m "docs: add bundle id naming standard implementation plan"
```
