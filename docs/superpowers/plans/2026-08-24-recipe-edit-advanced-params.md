# Recipe Edit Advanced Parameters Customization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enable editing of advanced recipe parameters (`environment_injection`, `launch_args`, `symlink_whitelist`, `app_type`, `language`) inside `RecipeEditWindow` under a collapsible "高级参数 (专家设置)" section with full validation and i18n support.

**Architecture:** Extend `RecipeEditWindow` with reusable text parsing helpers for dicts (`KEY=VALUE`) and lists (line-by-line), add a collapsible disclosure box inside a `toga.ScrollContainer`, populate form fields on initialization, validate syntax during save, and supply comprehensive i18n translations.

**Tech Stack:** Python 3.12+, Toga (AppKit backend), PySide6 / pytest, Pydantic `Recipe` model.

## Global Constraints
- Target macOS native patterns, PySide6 / Toga GUI, Python 3.12+, with `conda run -n ATBClone` for Python env.
- Test command: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/`
- Zero external third-party dependencies outside the established project dependencies.
- Full bilingual i18n support in `src/atbclone/core/i18n.py`.

---

### Task 1: Add i18n Localization Strings for Advanced Recipe Parameters

**Files:**
- Modify: `src/atbclone/core/i18n.py`
- Test: `tests/test_recipe_edit_window.py`

**Interfaces:**
- Produces translation keys:
  - `win_recipe_btn_advanced_expand`
  - `win_recipe_btn_advanced_collapse`
  - `win_recipe_advanced_warning`
  - `win_recipe_app_type`
  - `win_recipe_app_type_auto`
  - `win_recipe_language`
  - `win_recipe_env_injection`
  - `win_recipe_env_placeholder`
  - `win_recipe_launch_args`
  - `win_recipe_launch_args_placeholder`
  - `win_recipe_symlink_whitelist`
  - `win_recipe_symlink_placeholder`
  - `dialog_recipe_invalid_env_line`

- [ ] **Step 1: Write the failing test for i18n keys**

```python
# In tests/test_recipe_edit_window.py
from atbclone.core.i18n import t, set_language

def test_recipe_advanced_i18n_keys():
    set_language("zh_CN")
    assert "高级参数" in t("win_recipe_btn_advanced_expand")
    assert "收起" in t("win_recipe_btn_advanced_collapse")
    assert "环境变量" in t("win_recipe_env_injection")
    assert "启动参数" in t("win_recipe_launch_args")
    assert "软链接白名单" in t("win_recipe_symlink_whitelist")
    assert "应用类型" in t("win_recipe_app_type")

    set_language("en_US")
    assert "Advanced" in t("win_recipe_btn_advanced_expand")
    assert "Collapse" in t("win_recipe_btn_advanced_collapse")
    assert "Environment" in t("win_recipe_env_injection")
    assert "Launch" in t("win_recipe_launch_args")
    assert "Whitelist" in t("win_recipe_symlink_whitelist")
    assert "Application" in t("win_recipe_app_type")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_recipe_edit_window.py -k test_recipe_advanced_i18n_keys`
Expected: FAIL with KeyError or missing translations.

- [ ] **Step 3: Add translation definitions to `src/atbclone/core/i18n.py`**

Add bilingual dictionaries for all the new keys under the recipe editing section in `src/atbclone/core/i18n.py`.

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_recipe_edit_window.py -k test_recipe_advanced_i18n_keys`
Expected: PASS

---

### Task 2: Implement Environment Injection and List Parsing & Formatting Helpers

**Files:**
- Modify: `src/atbclone/gui/windows/recipe_edit.py`
- Test: `tests/test_recipe_edit_window.py`

**Interfaces:**
- Produces:
  - `format_env_injection(env: dict[str, str]) -> str`
  - `parse_env_injection(text: str) -> tuple[dict[str, str], str | None]`
  - `format_list_lines(items: list[str]) -> str`
  - `parse_list_lines(text: str) -> list[str]`

- [ ] **Step 1: Write the failing tests for parsing functions**

```python
# In tests/test_recipe_edit_window.py
from atbclone.gui.windows.recipe_edit import (
    format_env_injection,
    parse_env_injection,
    format_list_lines,
    parse_list_lines,
)

def test_env_injection_formatting_and_parsing():
    env = {
        "HOME": "{{ATB_DATA_DIR}}/Home",
        "TMPDIR": "{{ATB_DATA_DIR}}/Tmp",
        "FOO": "bar=baz",
    }
    formatted = format_env_injection(env)
    parsed, err = parse_env_injection(formatted)
    assert err is None
    assert parsed == env

    # Test with comments and whitespace
    text_with_noise = """
    # This is a comment
    HOME = {{ATB_DATA_DIR}}/Home

    TMPDIR={{ATB_DATA_DIR}}/Tmp
    # Another comment
    """
    parsed_noise, err_noise = parse_env_injection(text_with_noise)
    assert err_noise is None
    assert parsed_noise == {
        "HOME": "{{ATB_DATA_DIR}}/Home",
        "TMPDIR": "{{ATB_DATA_DIR}}/Tmp",
    }

def test_env_injection_syntax_errors():
    invalid_text = "HOME={{ATB_DATA_DIR}}\nINVALID_LINE_NO_EQUALS"
    parsed, err = parse_env_injection(invalid_text)
    assert err is not None
    assert "Line 2" in err

    empty_key_text = "=some_value"
    parsed, err = parse_env_injection(empty_key_text)
    assert err is not None

def test_list_formatting_and_parsing():
    items = ["--user-data-dir={{ATB_DATA_DIR}}", "--disable-gpu", "--flag=1"]
    formatted = format_list_lines(items)
    parsed = parse_list_lines(formatted)
    assert parsed == items

    text_with_blanks = "\n  --arg1  \n\n# comment\n  --arg2\n"
    assert parse_list_lines(text_with_blanks) == ["--arg1", "--arg2"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_recipe_edit_window.py -k "test_env_injection or test_list"`
Expected: FAIL with ImportError / not defined.

- [ ] **Step 3: Implement helper functions in `src/atbclone/gui/windows/recipe_edit.py`**

Implement `format_env_injection`, `parse_env_injection`, `format_list_lines`, and `parse_list_lines`.

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_recipe_edit_window.py -k "test_env_injection or test_list"`
Expected: PASS

---

### Task 3: Build Collapsible Advanced UI Section & Connect Form to Recipe Model

**Files:**
- Modify: `src/atbclone/gui/windows/recipe_edit.py`
- Test: `tests/test_recipe_edit_window.py`

**Interfaces:**
- Consumes: `Recipe`, `ProxyConfig`, `SUPPORTED_LANGUAGES`, parsing helpers, i18n `t()`
- Produces:
  - `RecipeEditWindow` with collapsible `advanced_box`, `ScrollContainer`, and full fields extraction/validation in `get_recipe_from_form()` / `on_save_press()`.

- [ ] **Step 1: Write failing test for RecipeEditWindow with advanced params**

```python
# In tests/test_recipe_edit_window.py
import pytest
from atbclone.recipes.models import Recipe, ProxyConfig
from atbclone.gui.windows.recipe_edit import RecipeEditWindow

def test_recipe_edit_window_form_roundtrip():
    original_recipe = Recipe(
        bundle_id="com.example.testapp",
        app_name="Test App",
        strategy="soft_clone",
        strip_sandbox=True,
        proxy=ProxyConfig(enabled=True, type="socks5", host="10.0.0.1", port=1080),
        environment_injection={"HOME": "{{ATB_DATA_DIR}}/Home", "MY_VAR": "val123"},
        launch_args=["--flag1", "--user-data-dir={{ATB_DATA_DIR}}"],
        symlink_whitelist=["Library/Application Support/TestApp"],
        language="zh_CN",
        app_type="electron",
    )

    win = RecipeEditWindow(title="Edit", recipe=original_recipe)
    # Check populated form values
    assert win.input_bundle_id.value == "com.example.testapp"
    assert win.input_app_name.value == "Test App"
    assert win.select_strategy.value == "soft_clone"
    assert win.switch_strip_sandbox.value is True
    assert win.switch_proxy.value is True

    # Check advanced values
    recipe_out, err = win.get_recipe_from_form()
    assert err is None
    assert recipe_out is not None
    assert recipe_out.bundle_id == "com.example.testapp"
    assert recipe_out.environment_injection == original_recipe.environment_injection
    assert recipe_out.launch_args == original_recipe.launch_args
    assert recipe_out.symlink_whitelist == original_recipe.symlink_whitelist
    assert recipe_out.language == "zh_CN"
    assert recipe_out.app_type == "electron"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_recipe_edit_window.py -k test_recipe_edit_window_form_roundtrip`
Expected: FAIL.

- [ ] **Step 3: Implement `RecipeEditWindow` enhancements**

1. Add controls for:
   - `self.select_app_type`
   - `self.select_language`
   - `self.input_env_injection`
   - `self.input_launch_args`
   - `self.input_symlink_whitelist`
   - `self.btn_toggle_advanced`
2. Implement collapse / expand toggle behavior.
3. Wrap main form in `toga.ScrollContainer(horizontal=False)`.
4. Update `get_recipe_from_form()` to parse advanced fields and validate syntax.
5. Update `on_save_press()` to handle syntax error messages with `self.error_dialog()`.

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_recipe_edit_window.py`
Expected: PASS.

---

### Task 4: Full Regression Testing & UI Smoke Verification

**Files:**
- Test: `tests/`

- [ ] **Step 1: Run full test suite**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/`
Expected: All tests pass with 100% green.

- [ ] **Step 2: Verify custom recipe save and load end-to-end**

Run test validating `RecipeService` saving and loading the new custom recipe containing `environment_injection` and `launch_args`.
