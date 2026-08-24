# Clone Details Injected Parameters & Environment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enhance the "Clone Details" (`CloneDetailWindow`) dialog in ATBClone to display rich, structured runtime information regarding injected launch parameters (`--data-dir`, `--lang=...`, `-AppleLanguages`, etc.), injected environment variables (`HOME`, `LANG`, `LC_ALL`, `HTTP_PROXY`, etc.), and the full launcher `exec` command with a quick copy action.

**Architecture:** Implement a hybrid `CloneInspector` core service that parses actual on-disk bash wrapper scripts (with fallback to Recipe reconstruction), extend `i18n.py` with 9-language translation keys, and update `CloneDetailWindow` with a structured, scrollable two-card layout including a native clipboard copy helper.

**Tech Stack:** Python 3.12+, Toga (macOS Cocoa), pytest.

## Global Constraints
- Target macOS native patterns, PySide6/Toga, Python 3.12+, with `conda run -n ATBClone` for Python env.
- Test command: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/`
- Zero external third-party runtime dependencies beyond project requirements.
- Maintain full 9-language i18n coverage (`en`, `zh`, `zh_TW`, `ja`, `ko`, `de`, `fr`, `ru`, `es`).

---

### Task 1: Core `CloneInspector` & Unit Tests

**Files:**
- Create: `src/atbclone/core/clone_inspector.py`
- Test: `tests/test_clone_inspector.py`

**Interfaces:**
- Produces:
  ```python
  @dataclass
  class InjectedDetails:
      launch_args: list[str]
      env_vars: dict[str, str]
      exec_command: str
      source_type: str  # "wrapper_script" | "recipe_fallback"

  class CloneInspector:
      @classmethod
      def inspect(cls, record: CloneRecord) -> InjectedDetails: ...
      @classmethod
      def parse_wrapper_script(cls, script_content: str) -> InjectedDetails: ...
  ```

- [ ] **Step 1: Write the failing tests for `CloneInspector`**

```python
# tests/test_clone_inspector.py
import pytest
from pathlib import Path
from atbclone.core.state import CloneRecord
from atbclone.core.clone_inspector import CloneInspector, InjectedDetails

def test_parse_wrapper_script_basic():
    script = """#!/bin/bash
REAL_USER_HOME="$HOME"
export LANG="zh_CN.UTF-8"
export LC_ALL="zh_CN.UTF-8"
export HTTP_PROXY="http://127.0.0.1:7890"
exec "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --user-data-dir="/Users/test/Data" --lang=zh-CN "$@"
"""
    details = CloneInspector.parse_wrapper_script(script)
    assert details.env_vars.get("LANG") == "zh_CN.UTF-8"
    assert details.env_vars.get("LC_ALL") == "zh_CN.UTF-8"
    assert details.env_vars.get("HTTP_PROXY") == "http://127.0.0.1:7890"
    assert '--user-data-dir="/Users/test/Data"' in details.launch_args or '--user-data-dir=/Users/test/Data' in details.launch_args
    assert '--lang=zh-CN' in details.launch_args
    assert 'Google Chrome' in details.exec_command
    assert details.source_type == "wrapper_script"

def test_inspect_fallback_when_file_not_found(tmp_path):
    record = CloneRecord(
        clone_name="TestApp_Clone",
        source_app="TestApp",
        source_path="/Applications/TestApp.app",
        bundle_id="com.google.Chrome",
        strategy="soft_clone",
        dest_path=str(tmp_path / "NonExistent.app"),
        data_dir=str(tmp_path / "Data"),
        created_at="2026-08-24T00:00:00Z",
        language="zh-Hans",
        proxy_enabled=True,
        proxy_summary="http://127.0.0.1:8080",
    )
    details = CloneInspector.inspect(record)
    assert details.source_type == "recipe_fallback"
    assert any("user-data-dir" in arg for arg in details.launch_args) or any("lang" in arg for arg in details.launch_args)
    assert details.env_vars.get("HTTP_PROXY") == "http://127.0.0.1:8080"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_clone_inspector.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'atbclone.core.clone_inspector'`

- [ ] **Step 3: Write implementation in `src/atbclone/core/clone_inspector.py`**

```python
"""Clone inspector for resolving injected launch parameters and environment variables."""

from dataclasses import dataclass, field
from pathlib import Path
import re
import shlex

from atbclone.core.locale import build_language_wrapper_snippet
from atbclone.core.logger import get_logger
from atbclone.core.state import CloneRecord
from atbclone.recipes.loader import RecipeLoader

logger = get_logger("core.clone_inspector")


@dataclass
class InjectedDetails:
    launch_args: list[str] = field(default_factory=list)
    env_vars: dict[str, str] = field(default_factory=dict)
    exec_command: str = ""
    source_type: str = "recipe_fallback"  # "wrapper_script" | "recipe_fallback"


class CloneInspector:
    """Extracts and resolves runtime injected launch arguments, environment variables, and exec commands."""

    @classmethod
    def inspect(cls, record: CloneRecord) -> InjectedDetails:
        """Inspect a clone record, trying on-disk wrapper script first and falling back to recipe reconstruction."""
        dest_path = Path(record.dest_path)
        macos_dir = dest_path / "Contents" / "MacOS"

        if macos_dir.exists() and macos_dir.is_dir():
            for child in macos_dir.iterdir():
                if child.is_file() and not child.name.endswith(".bin"):
                    try:
                        content = child.read_text(encoding="utf-8", errors="ignore")
                        if content.startswith("#!/bin/bash") or "exec " in content:
                            details = cls.parse_wrapper_script(content)
                            if details.exec_command or details.env_vars or details.launch_args:
                                return details
                    except Exception as e:
                        logger.debug(f"Failed to read wrapper script {child}: {e}")

        return cls.reconstruct_from_recipe(record)

    @classmethod
    def parse_wrapper_script(cls, script_content: str) -> InjectedDetails:
        """Parse bash wrapper script content to extract exports and exec command."""
        env_vars: dict[str, str] = {}
        launch_args: list[str] = []
        exec_command = ""

        for line in script_content.splitlines():
            line_str = line.strip()
            if line_str.startswith("export "):
                # Match export KEY="VALUE" or export KEY=VALUE
                export_match = re.match(r'^export\s+([A-Za-z_][A-Za-z0-9_]*)=(.*)$', line_str)
                if export_match:
                    k, v = export_match.group(1), export_match.group(2)
                    if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                        v = v[1:-1]
                    env_vars[k] = v

            elif line_str.startswith("exec "):
                exec_command = line_str[5:].strip()
                try:
                    # Remove trailing "$@" if present
                    cleaned_cmd = re.sub(r'\s+"\$@"\s*$', '', exec_command).strip()
                    tokens = shlex.split(cleaned_cmd)
                    if tokens:
                        # tokens[0] is executable path/name, remainder are injected launch args
                        launch_args = tokens[1:]
                except Exception as e:
                    logger.debug(f"Failed to split exec command tokens: {e}")

        return InjectedDetails(
            launch_args=launch_args,
            env_vars=env_vars,
            exec_command=exec_command,
            source_type="wrapper_script",
        )

    @classmethod
    def reconstruct_from_recipe(cls, record: CloneRecord) -> InjectedDetails:
        """Fallback reconstruction using Recipe and CloneRecord properties."""
        recipe = RecipeLoader.match(record.bundle_id)
        env_vars: dict[str, str] = {}
        launch_args: list[str] = []

        # 1. Environment injection from recipe
        for k, v in recipe.environment_injection.items():
            env_vars[k] = v.replace("{{ATB_DATA_DIR}}", record.data_dir)

        # 2. Language settings
        app_type = recipe.app_type or "cocoa"
        _, lang_args = build_language_wrapper_snippet(record.language, app_type=app_type)
        if record.language != "system":
            env_vars["LANG"] = f"{record.language}.UTF-8"
            env_vars["LC_ALL"] = f"{record.language}.UTF-8"

        # 3. Proxy
        if record.proxy_enabled and record.proxy_summary:
            env_vars["HTTP_PROXY"] = record.proxy_summary
            env_vars["HTTPS_PROXY"] = record.proxy_summary

        # 4. Launch args from recipe + lang args
        for arg in recipe.launch_args:
            launch_args.append(arg.replace("{{ATB_DATA_DIR}}", record.data_dir))
        launch_args.extend(lang_args)

        # 5. Exec command estimate
        src_bin = f"{record.source_path}/Contents/MacOS/{record.source_app}"
        args_str = f" {' '.join(shlex.quote(a) for a in launch_args)}" if launch_args else ""
        exec_command = f'exec "{src_bin}"{args_str} "$@"'

        return InjectedDetails(
            launch_args=launch_args,
            env_vars=env_vars,
            exec_command=exec_command,
            source_type="recipe_fallback",
        )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_clone_inspector.py`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add src/atbclone/core/clone_inspector.py tests/test_clone_inspector.py
git commit -m "feat(core): implement CloneInspector for extracting injected launch parameters"
```

---

### Task 2: Localization Keys in `i18n.py`

**Files:**
- Modify: `src/atbclone/core/i18n.py:3236-3350`
- Test: `tests/test_i18n.py`

**Interfaces:**
- Produces:
  - `win_detail_section_basic`
  - `win_detail_section_injected`
  - `win_detail_launch_args`
  - `win_detail_env_vars`
  - `win_detail_exec_cmd`
  - `win_detail_btn_copy_cmd`
  - `win_detail_cmd_copied`
  - `win_detail_none`

- [ ] **Step 1: Write failing test for new i18n keys**

```python
# tests/test_i18n_detail_keys.py
from atbclone.core.i18n import t

def test_detail_injected_i18n_keys():
    for key in [
        "win_detail_section_basic",
        "win_detail_section_injected",
        "win_detail_launch_args",
        "win_detail_env_vars",
        "win_detail_exec_cmd",
        "win_detail_btn_copy_cmd",
        "win_detail_cmd_copied",
        "win_detail_none",
    ]:
        val_en = t(key, lang="en")
        val_zh = t(key, lang="zh")
        assert val_en != key
        assert val_zh != key
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_i18n_detail_keys.py`
Expected: FAIL

- [ ] **Step 3: Add localized translations to `src/atbclone/core/i18n.py`**

Add all 8 keys in `TRANSLATIONS` across 9 languages (`en`, `zh`, `zh_TW`, `ja`, `ko`, `de`, `fr`, `ru`, `es`).

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_i18n_detail_keys.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/atbclone/core/i18n.py tests/test_i18n_detail_keys.py
git commit -m "feat(i18n): add translations for clone detail injected parameters"
```

---

### Task 3: GUI `CloneDetailWindow` Enhancements & Clipboard Helper

**Files:**
- Modify: `src/atbclone/gui/windows/clone_detail.py`
- Test: `tests/test_clone_detail_gui.py`

**Interfaces:**
- Consumes:
  - `CloneInspector.inspect(record) -> InjectedDetails`
  - `i18n.t(...)`

- [ ] **Step 1: Write the failing tests for `CloneDetailWindow` structure**

```python
# tests/test_clone_detail_gui.py
from atbclone.core.state import CloneRecord
from atbclone.gui.windows.clone_detail import CloneDetailWindow

def test_clone_detail_window_creates(tmp_path):
    record = CloneRecord(
        clone_name="TestApp_Clone",
        source_app="TestApp",
        source_path="/Applications/TestApp.app",
        bundle_id="com.google.Chrome",
        strategy="soft_clone",
        dest_path=str(tmp_path / "Clone.app"),
        data_dir=str(tmp_path / "Data"),
        created_at="2026-08-24T00:00:00Z",
        language="zh-Hans",
        proxy_enabled=True,
        proxy_summary="http://127.0.0.1:7890",
    )
    win = CloneDetailWindow(record)
    assert win.title.startswith("分身详情") or "Clone Details" in win.title
    assert hasattr(win, "details")
    assert win.details is not None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_clone_detail_gui.py`
Expected: FAIL

- [ ] **Step 3: Implement enhanced `CloneDetailWindow` in `src/atbclone/gui/windows/clone_detail.py`**

Update `CloneDetailWindow` with:
- Window size `(560, 580)`.
- Inspect record with `CloneInspector.inspect(record)`.
- Add clipboard helper function `copy_to_clipboard(text: str)`.
- Build Section 1 "基本信息" card.
- Build Section 2 "注入与启动参数" card:
  - List launch arguments.
  - List environment variables.
  - Exec command view with "复制命令" button.
- Wrap content in `toga.ScrollContainer`.

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_clone_detail_gui.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/atbclone/gui/windows/clone_detail.py tests/test_clone_detail_gui.py
git commit -m "feat(gui): enhance CloneDetailWindow with injected parameters card and copy button"
```

---

### Task 4: Full Test Suite Verification

**Files:**
- Test: All tests in `tests/`

- [ ] **Step 1: Run complete test suite**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/`
Expected: ALL PASS with zero failures

- [ ] **Step 2: Clean up temporary test files if any**

Run: `git status` to ensure clean working tree.
