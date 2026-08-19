# Design Spec: Standardized Bundle Identifier Naming

**Date:** 2026-08-19  
**Status:** Approved  
**Topic:** Standardize cloned app Bundle Identifier naming to `.atbclone.<num>`

## 1. Overview & Motivation

When ATBClone generates a cloned macOS application instance, it modifies `CFBundleIdentifier` to ensure macOS LaunchServices, sandbox container routing, and user defaults distinguish the clone from the original application.

Previously, clone bundle IDs used an unstandardized format `f"{info.bundle_id}.atb{num}"` (e.g., `com.google.Chrome.atb2`), which lacked proper dot-notation hierarchy, brand consistency, and was duplicated across multiple CLI modules.

This design standardizes the clone bundle ID format to:
```
<original_bundle_id>.atbclone.<instance_number>
```
Example: `com.google.Chrome.atbclone.2`.

## 2. Goals & Non-Goals

### Goals
- **Clear Brand Identity**: Explicitly associate clone instances with `atbclone`.
- **Apple Reverse-DNS Compliance**: Use dot-separated hierarchical notation (`.atbclone.<num>`).
- **DRY Architecture**: Centralize bundle ID generation into a reusable helper method in `AppInspector`.
- **Test Integrity**: Update unit and integration tests to verify the new naming standard.

### Non-Goals
- Modifying previously created instances already recorded in existing state files (preserves backward compatibility with existing user state).

## 3. Detailed Design

### 3.1 Naming Specification
- **Format**: `<original_bundle_id>.atbclone.<num>`
- **Examples**:
  - Original: `com.google.Chrome` (Clone #2) -> `com.google.Chrome.atbclone.2`
  - Original: `com.tencent.xinWeChat` (Clone #2) -> `com.tencent.xinWeChat.atbclone.2`
  - Fallback / Default instance: `<bundle_id>.atbclone.1`

### 3.2 Centralized Helper Method
Add a static method to `AppInspector`:
```python
class AppInspector:
    # ...
    @staticmethod
    def generate_bundle_id(bundle_id: str, num: int = 1) -> str:
        """Generate standardized bundle identifier for a cloned application instance."""
        return f"{bundle_id}.atbclone.{num}"
```

### 3.3 Affected Components

1. **`src/atbclone/core/app_inspector.py`**:
   - Add `AppInspector.generate_bundle_id(bundle_id: str, num: int) -> str`.
2. **`src/atbclone/cli/cmd_clone.py`**:
   - Replace `new_bundle_id = f"{info.bundle_id}.atb{num}"` with `AppInspector.generate_bundle_id(info.bundle_id, num)`.
3. **`src/atbclone/cli/cmd_wizard.py`**:
   - Replace `new_bundle_id = f"{info.bundle_id}.atb{num}"` with `AppInspector.generate_bundle_id(info.bundle_id, num)`.
4. **`src/atbclone/cli/cmd_update.py`**:
   - Replace `f"{record.bundle_id}.atb1"` with `AppInspector.generate_bundle_id(record.bundle_id, 1)`.

## 4. Testing & Verification

1. **Unit Tests for Helper (`tests/test_app_inspector.py`)**:
   - Test `AppInspector.generate_bundle_id` with various bundle IDs and instance numbers.
2. **CLI Tests**:
   - Update assertions in `tests/test_cmd_clone.py` from `com.tencent.xinWeChat.atb2` to `com.tencent.xinWeChat.atbclone.2`.
   - Update assertions in `tests/test_cmd_wizard.py` and `tests/test_cmd_update.py`.
3. **Regression Test Suite**:
   - Execute full test suite via `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/`.
