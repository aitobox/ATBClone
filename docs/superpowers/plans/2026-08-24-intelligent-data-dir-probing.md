# Intelligent Data Directory Probing & Launch Argument Filtering Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement static Mach-O binary argument probing for unknown macOS applications to detect custom data-dir flags (e.g. `--data-dir`, `--profile`), and validate/prune unsupported launch arguments before generating clone wrapper scripts.

**Architecture:** A new `argument_prober.py` module containing `BinaryArgumentProber` (extracts printable Mach-O strings and matches priority candidate patterns) and `LaunchArgumentValidator` (filters `launch_args` against framework whitelists and binary string pools). `AppProber` and `CloneEngines` integrate these components to safely isolate data directories and avoid passing unrecognized flags to applications.

**Tech Stack:** Python 3.12, PySide6/Toga (macOS), pytest, Mach-O binary analysis, regular expressions.

## Global Constraints

- Native macOS Python 3.12+ in Conda env `ATBClone`
- Zero third-party runtime package dependencies beyond existing pyproject.toml
- TDD approach: write failing tests first, then implementation, verify passing, and commit

---

### Task 1: Binary Argument Prober (`BinaryArgumentProber`)

**Files:**
- Create: `src/atbclone/core/argument_prober.py`
- Test: `tests/test_argument_prober.py`

**Interfaces:**
- Produces:
  ```python
  class ArgumentProbeResult:
      flag: str | None  # e.g. "--data-dir"
      template: str | None  # e.g. "--data-dir={{ATB_DATA_DIR}}"
      syntax: str  # "equals" or "space"
      reason: str

  class BinaryArgumentProber:
      @staticmethod
      def extract_binary_strings(binary_path: Path | str, min_len: int = 3, max_bytes: int = 10_000_000) -> set[str]: ...
      @classmethod
      def probe_data_dir_argument(cls, binary_path: Path | str) -> ArgumentProbeResult: ...
  ```

- [ ] **Step 1: Write the failing test**

```python
# tests/test_argument_prober.py
from pathlib import Path
import pytest
from atbclone.core.argument_prober import BinaryArgumentProber, ArgumentProbeResult


def test_extract_binary_strings(tmp_path: Path):
    dummy_bin = tmp_path / "dummy_bin"
    dummy_bin.write_bytes(b"\x00\x01\x02--user-data-dir\x00some_other_string\x00\xff")
    strings = BinaryArgumentProber.extract_binary_strings(dummy_bin)
    assert "--user-data-dir" in strings
    assert "some_other_string" in strings


def test_probe_data_dir_argument_user_data_dir(tmp_path: Path):
    dummy_bin = tmp_path / "app_chromium"
    dummy_bin.write_bytes(b"MachO_HEADER\x00--user-data-dir\x00--lang\x00")
    res = BinaryArgumentProber.probe_data_dir_argument(dummy_bin)
    assert res.flag == "--user-data-dir"
    assert res.template == "--user-data-dir={{ATB_DATA_DIR}}"


def test_probe_data_dir_argument_data_dir(tmp_path: Path):
    dummy_bin = tmp_path / "app_custom"
    dummy_bin.write_bytes(b"MachO_HEADER\x00--data-dir=\x00--other\x00")
    res = BinaryArgumentProber.probe_data_dir_argument(dummy_bin)
    assert res.flag == "--data-dir"
    assert res.template == "--data-dir={{ATB_DATA_DIR}}"


def test_probe_data_dir_argument_profile_space(tmp_path: Path):
    dummy_bin = tmp_path / "app_gecko"
    dummy_bin.write_bytes(b"MachO_HEADER\x00-profile <path>\x00")
    res = BinaryArgumentProber.probe_data_dir_argument(dummy_bin)
    assert res.flag == "-profile"
    assert res.template == "-profile {{ATB_DATA_DIR}}"


def test_probe_data_dir_argument_none(tmp_path: Path):
    dummy_bin = tmp_path / "app_native"
    dummy_bin.write_bytes(b"MachO_HEADER\x00CocoaApp\x00NSWindow\x00")
    res = BinaryArgumentProber.probe_data_dir_argument(dummy_bin)
    assert res.flag is None
    assert res.template is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_argument_prober.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'atbclone.core.argument_prober'`

- [ ] **Step 3: Implement `BinaryArgumentProber`**

Implement `src/atbclone/core/argument_prober.py` with fast byte streaming string extraction and candidate pattern priority matching.

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_argument_prober.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/atbclone/core/argument_prober.py tests/test_argument_prober.py
git commit -m "feat(core): implement BinaryArgumentProber for Mach-O CLI argument detection"
```

---

### Task 2: Launch Argument Validator & Filter (`LaunchArgumentValidator`)

**Files:**
- Modify: `src/atbclone/core/argument_prober.py`
- Test: `tests/test_argument_validator.py`

**Interfaces:**
- Produces:
  ```python
  class LaunchArgumentValidator:
      FRAMEWORK_WHITELISTS: dict[str, set[str]]
      @classmethod
      def validate_and_filter(
          cls,
          binary_path: Path | str,
          launch_args: list[str],
          app_type: str | None = None,
      ) -> tuple[list[str], list[str]]:
          """Returns (validated_args, pruned_args)."""
  ```

- [ ] **Step 1: Write the failing test**

```python
# tests/test_argument_validator.py
from pathlib import Path
import pytest
from atbclone.core.argument_prober import LaunchArgumentValidator


def test_validator_framework_whitelist_chromium(tmp_path: Path):
    dummy_bin = tmp_path / "chrome_bin"
    dummy_bin.write_bytes(b"empty")
    args = ["--user-data-dir=/tmp/data", "--lang=zh-CN", "--no-sandbox"]
    valid, pruned = LaunchArgumentValidator.validate_and_filter(dummy_bin, args, app_type="chromium")
    assert valid == args
    assert pruned == []


def test_validator_prune_unsupported_args(tmp_path: Path):
    dummy_bin = tmp_path / "native_bin"
    dummy_bin.write_bytes(b"MachO_HEADER\x00--supported-flag\x00")
    args = ["--supported-flag=123", "--unsupported-flag=456", "--user-data-dir=/tmp/data"]
    valid, pruned = LaunchArgumentValidator.validate_and_filter(dummy_bin, args, app_type="cocoa")
    assert "--supported-flag=123" in valid
    assert "--unsupported-flag=456" in pruned
    assert "--user-data-dir=/tmp/data" in pruned


def test_validator_cocoa_apple_args(tmp_path: Path):
    dummy_bin = tmp_path / "cocoa_bin"
    dummy_bin.write_bytes(b"empty")
    args = ["-AppleLanguages", '("zh-Hans")', "-AppleLocale", "zh_CN"]
    valid, pruned = LaunchArgumentValidator.validate_and_filter(dummy_bin, args, app_type="cocoa")
    assert valid == args
    assert pruned == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_argument_validator.py`
Expected: FAIL

- [ ] **Step 3: Implement `LaunchArgumentValidator`**

In `src/atbclone/core/argument_prober.py`, add `LaunchArgumentValidator` with framework whitelists, flag token extraction, and binary string checking.

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_argument_validator.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/atbclone/core/argument_prober.py tests/test_argument_validator.py
git commit -m "feat(core): implement LaunchArgumentValidator for filtering unsupported CLI flags"
```

---

### Task 3: Integrate `ArgumentProber` into `AppProber`

**Files:**
- Modify: `src/atbclone/core/app_prober.py`
- Test: `tests/test_app_prober.py`

**Interfaces:**
- Consumes: `BinaryArgumentProber.probe_data_dir_argument()`
- Produces: `AppProber.analyze()` dynamically assigning custom data-dir launch_args and strategy for generic/unknown apps when CLI flags are detected.

- [ ] **Step 1: Write the failing test**

```python
# In tests/test_app_prober.py
def test_probe_unknown_app_with_data_dir_flag(tmp_path: Path):
    app_dir = tmp_path / "CustomTool.app"
    macos_dir = app_dir / "Contents" / "MacOS"
    macos_dir.mkdir(parents=True)
    exe = macos_dir / "CustomTool"
    exe.write_bytes(b"MachO_DATA\x00--data-dir=\x00--verbose\x00")
    plist = app_dir / "Contents" / "Info.plist"
    plist.write_bytes(b"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleIdentifier</key><string>com.custom.tool</string>
    <key>CFBundleExecutable</key><string>CustomTool</string>
    <key>CFBundleName</key><string>CustomTool</string>
</dict>
</plist>""")

    res = AppProber.analyze(app_dir)
    assert "--data-dir={{ATB_DATA_DIR}}" in res.recipe.launch_args
    assert res.recipe.strategy == "soft_clone"
    assert "CLI data directory parameter '--data-dir'" in res.reason
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_app_prober.py -k test_probe_unknown_app_with_data_dir_flag`
Expected: FAIL

- [ ] **Step 3: Update `AppProber.analyze()`**

In `src/atbclone/core/app_prober.py`, when `app_type` is `"generic"` or `"cocoa"`, probe the executable binary using `BinaryArgumentProber.probe_data_dir_argument(app_info.executable)`. If a data-dir argument is detected, assign `launch_args=[res.template]`, `strategy="soft_clone"` (or retain hard_clone if sandboxed). If not detected, assign `launch_args=[]`, `strategy="hard_clone"`, and inject `HOME`/`TMPDIR`.

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_app_prober.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/atbclone/core/app_prober.py tests/test_app_prober.py
git commit -m "feat(core): integrate BinaryArgumentProber into AppProber for unknown apps"
```

---

### Task 4: Integrate `LaunchArgumentValidator` into `CloneEngines`

**Files:**
- Modify: `src/atbclone/core/engines.py`
- Test: `tests/test_engines.py`

**Interfaces:**
- Consumes: `LaunchArgumentValidator.validate_and_filter()`
- Produces: Sanitized wrapper scripts that exclude unsupported flags and automatically maintain `HOME`/`TMPDIR` isolation when all flags are pruned.

- [ ] **Step 1: Write the failing test**

```python
# In tests/test_engines.py
def test_soft_clone_engine_prunes_unsupported_args(tmp_path: Path, monkeypatch):
    # Setup mock task with unsupported args in recipe
    ...
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_engines.py -k test_soft_clone_engine_prunes_unsupported_args`
Expected: FAIL

- [ ] **Step 3: Update `SoftCloneEngine` and `HardCloneEngine` in `src/atbclone/core/engines.py`**

Filter `task.recipe.launch_args` through `LaunchArgumentValidator.validate_and_filter()`. If pruned, log a warning and only include validated args in `args_list`. Under `HardCloneEngine`, if all `launch_args` containing `{{ATB_DATA_DIR}}` were pruned and no `environment_injection` was present, inject default `HOME` and `TMPDIR`.

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_engines.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/atbclone/core/engines.py tests/test_engines.py
git commit -m "feat(engines): validate and prune unsupported launch arguments during clone creation"
```

---

### Task 5: End-to-End CLI / GUI Verification and Full Test Suite

**Files:**
- Test: `tests/test_cmd_probe.py`, `tests/test_cmd_clone.py`, and full test suite

- [ ] **Step 1: Add CLI integration tests for argument probing and pruning**
- [ ] **Step 2: Run CLI tests to verify behavior**
- [ ] **Step 3: Run full pytest test suite across entire project**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/`
Expected: 100% tests passing

- [ ] **Step 4: Commit**

```bash
git add tests/
git commit -m "test: add end-to-end integration tests for argument probing and filtering"
```
