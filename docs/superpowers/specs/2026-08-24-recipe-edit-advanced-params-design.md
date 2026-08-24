# Design Specification: Recipe Edit Advanced Parameters Customization

## 1. Background & Goals
In ATBClone, applications are cloned based on configuration rules called **Recipes** (`Recipe` model). Currently, the GUI dialog for creating and editing recipes (`RecipeEditWindow`) only provides input fields for basic attributes (`bundle_id`, `app_name`, `strategy`, `strip_sandbox`, and `proxy`).

Advanced runtime parameters supported by the core cloning engines—such as:
- `environment_injection` (custom environment variables like `HOME` or `TMPDIR`)
- `launch_args` (CLI arguments passed to executable like `--user-data-dir={{ATB_DATA_DIR}}`)
- `symlink_whitelist` (whitelisted paths for soft links)
- `app_type` (`cocoa`, `electron`, `chromium`, `firefox`, `generic`, or unspecified)
- `language` (application display language preference)

cannot currently be viewed or customized through the `RecipeEditWindow` GUI. Users must manually edit raw YAML files in `~/.atbclone/recipes/`.

### Goals
- Enable editing of all advanced recipe attributes directly inside `RecipeEditWindow`.
- Categorize these settings under a dedicated **"高级参数 (专家设置)" (Advanced Parameters / Expert Settings)** section that is **collapsed by default** to keep the interface clean and prevent accidental misconfigurations by standard users.
- Provide intuitive multi-line text editing for environment variables (`KEY=VALUE` per line) and list items (one per line).
- Provide robust syntax validation for environment variables with helpful error feedback.
- Support complete i18n localization (Chinese / English).

---

## 2. UI Layout & Component Architecture

### Window Hierarchy & Sizing
- **Window**: `RecipeEditWindow` (sized at `540 x 580` pixels, resizable).
- **Outer Container**: `toga.ScrollContainer(horizontal=False)` containing the main `form_box`. This ensures all elements remain fully scrollable and accessible regardless of screen size when the advanced section is expanded.

### Layout Structure
1. **Basic Settings Area (Always Visible)**:
   - **Bundle ID** (`toga.TextInput`, read-only when editing an existing recipe, editable when creating a new recipe).
   - **App Name** (`toga.TextInput`).
   - **Clone Strategy** (`toga.Selection`: `hard_clone` / `soft_clone`).
   - **Strip Sandbox** (`toga.Switch`).
   - **Proxy Configuration Header & Controls**:
     - Enable Proxy Switch (`toga.Switch`).
     - Proxy Type (`toga.Selection`: `http`, `https`, `socks5`), Host (`toga.TextInput`), Port (`toga.TextInput`).

2. **Advanced Parameters Disclosure Bar**:
   - A toggle button (`toga.Button`) with text `▶ 高级参数 (专家设置)` when collapsed and `▼ 收起高级参数` when expanded.
   - An informative caution note: `⚠️ 仅供高级定制，错误配置可能导致应用无法启动` (`color=Theme.TEXT_MUTED`, `font_size=11.5`).

3. **Advanced Parameters Body (`advanced_box`, Collapsed by Default)**:
   - **App Type (`app_type`)**: `toga.Selection`
     - Options: `未指定 / 自动探测 (Auto)`, `cocoa`, `electron`, `chromium`, `firefox`, `generic`.
   - **Language Preference (`language`)**: `toga.Selection`
     - Options matching `SUPPORTED_LANGUAGES` (e.g. `跟随系统 (System)`, `简体中文`, `English`, etc.).
   - **Environment Injection (`environment_injection`)**: `toga.MultilineTextInput` (height ~90px).
     - Format: `KEY=VALUE` per line.
     - Supports macro placeholders such as `{{ATB_DATA_DIR}}`.
   - **Launch Arguments (`launch_args`)**: `toga.MultilineTextInput` (height ~80px).
     - Format: one argument per line (e.g. `--user-data-dir={{ATB_DATA_DIR}}`).
   - **Symlink Whitelist (`symlink_whitelist`)**: `toga.MultilineTextInput` (height ~70px).
     - Format: one path per line.

4. **Action Buttons**:
   - `btn_cancel`: Cancels and closes the window.
   - `btn_save`: Validates inputs and triggers the asynchronous `on_save` callback.

---

## 3. Data Parsing & Validation Logic

### Parsing Functions
We introduce reusable helper functions in `recipe_edit.py`:

```python
def format_env_injection(env: dict[str, str]) -> str:
    """Serialize dictionary of env vars to multi-line KEY=VALUE format."""
    return "\n".join(f"{k}={v}" for k, v in env.items())

def parse_env_injection(text: str) -> tuple[dict[str, str], str | None]:
    """
    Parse multi-line KEY=VALUE text into a dict.
    Ignores empty lines and comments (starting with #).
    Returns (env_dict, error_message). If invalid syntax is found, error_message is not None.
    """
    env_dict = {}
    lines = text.strip().splitlines()
    for idx, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            return {}, f"Line {idx}: '{line}' is missing '=' separator."
        key, val = line.split("=", 1)
        key = key.strip()
        val = val.strip()
        if not key:
            return {}, f"Line {idx}: Empty environment variable key."
        env_dict[key] = val
    return env_dict, None

def format_list_lines(items: list[str]) -> str:
    """Serialize list of strings into multi-line text."""
    return "\n".join(items)

def parse_list_lines(text: str) -> list[str]:
    """Parse multi-line text into a list of strings, stripping blanks and comments."""
    result = []
    for raw_line in text.strip().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        result.append(line)
    return result
```

### Save Pipeline
When the user clicks **Save**:
1. Validate required fields (`bundle_id`, `app_name`).
2. Validate proxy port if proxy is enabled.
3. Parse and validate `environment_injection`. If parsing fails, display an error alert with the specific line number and keep the window open.
4. Parse `launch_args` and `symlink_whitelist`.
5. Map selected `app_type` (converting "Auto / Unspecified" to `None`).
6. Map selected `language`.
7. Instantiate the updated `Recipe` model and call `on_save_callback(recipe)`.

---

## 4. Internationalization (i18n)

The following translation keys are added to `src/atbclone/core/i18n.py`:
- `win_recipe_btn_advanced_expand`: "▶ 高级参数 (专家设置)" / "▶ Advanced Settings (Expert)"
- `win_recipe_btn_advanced_collapse`: "▼ 收起高级参数" / "▼ Collapse Advanced Settings"
- `win_recipe_advanced_warning`: "⚠️ 仅供高级定制，错误配置可能导致应用无法启动" / "⚠️ For expert customization only; invalid configurations may prevent apps from launching"
- `win_recipe_app_type`: "应用类型" / "Application Type"
- `win_recipe_app_type_auto`: "自动探测 / 未指定" / "Auto Detect / Unspecified"
- `win_recipe_language`: "界面语言" / "Display Language"
- `win_recipe_env_injection`: "环境变量注入" / "Environment Variables"
- `win_recipe_env_placeholder`: "每行一条 KEY=VALUE，例如：\nHOME={{ATB_DATA_DIR}}/Home\nTMPDIR={{ATB_DATA_DIR}}/Tmp" / "One KEY=VALUE per line, e.g.:\nHOME={{ATB_DATA_DIR}}/Home\nTMPDIR={{ATB_DATA_DIR}}/Tmp"
- `win_recipe_launch_args`: "启动参数" / "Launch Arguments"
- `win_recipe_launch_args_placeholder`: "每行一个启动参数，例如：\n--user-data-dir={{ATB_DATA_DIR}}" / "One argument per line, e.g.:\n--user-data-dir={{ATB_DATA_DIR}}"
- `win_recipe_symlink_whitelist`: "软链接白名单" / "Symlink Whitelist"
- `win_recipe_symlink_placeholder`: "每行一个相对或绝对路径，例如：\nLibrary/Application Support/MyApp" / "One path per line, e.g.:\nLibrary/Application Support/MyApp"
- `dialog_recipe_invalid_env_line`: "环境变量解析错误：{detail}" / "Invalid environment variable format: {detail}"

---

## 5. Verification & Testing

1. **Unit Tests (`tests/test_recipe_edit_window.py`)**:
   - `test_env_injection_formatting_and_parsing()`: Tests valid `KEY=VALUE`, multiple `=` signs in value, placeholders `{{ATB_DATA_DIR}}`, blank lines, comment lines.
   - `test_env_injection_syntax_errors()`: Tests missing `=`, empty key errors.
   - `test_list_formatting_and_parsing()`: Tests `launch_args` and `symlink_whitelist` parsing.
   - `test_recipe_edit_window_initialization_with_advanced_recipe()`: Verifies form controls correctly populate all fields from a fully-populated `Recipe`.
   - `test_recipe_edit_window_get_recipe_from_form()`: Verifies extracting a `Recipe` matches expected advanced values.
2. **Full Regression Test Suite**:
   - `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/`
