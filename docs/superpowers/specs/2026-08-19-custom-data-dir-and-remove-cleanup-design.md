# ATBClone Custom Data Directory & Remove Cleanup Design Specification

## Overview
This document specifies the design for supporting custom data directories (`--data-dir`) in `atbclone clone` and `atbclone wizard`, intelligent app capability detection (allowing custom data directory only when the application supports data directory redirection/isolation), and interactive data cleanup during `atbclone remove`.

## Problem Statement
Currently:
1. `atbclone remove <clone_name>` only deletes the `.app` bundle when called without flags, silently leaving the data directory (`~/.atbclone/Data/<clone_name>`) on disk. Users may not realize `--with-data` is required.
2. `atbclone clone` and `atbclone wizard` hardcode the data directory to `~/.atbclone/Data/<clone_name>`, without allowing users to specify a custom storage location (e.g. on external SSDs or custom workspaces).
3. Applications that do not isolate data (e.g. apps without `{{ATB_DATA_DIR}}` in launch args or environment variables) should not misleadingly accept a `--data-dir` flag.

## Key Changes

### 1. Capability Detection (`supports_data_dir`)
Add a helper in the core/recipe module (e.g., `atbclone.recipes.models` or `atbclone.core.app_prober`):
```python
def supports_data_dir(recipe: Recipe) -> bool:
    """Return True if the recipe uses {{ATB_DATA_DIR}} in launch args or environment injection."""
    has_in_args = any("{{ATB_DATA_DIR}}" in arg for arg in recipe.launch_args)
    has_in_env = any("{{ATB_DATA_DIR}}" in val for val in recipe.environment_injection.values())
    return has_in_args or has_in_env
```
- **Supported**:
  - Chromium / Electron / Firefox apps (with launch args like `--user-data-dir={{ATB_DATA_DIR}}` or `-profile {{ATB_DATA_DIR}}`).
  - Native sandboxed or hijacked apps (with `HOME: {{ATB_DATA_DIR}}/Home`, `TMPDIR: {{ATB_DATA_DIR}}/Tmp`).
- **Unsupported**:
  - Apps with no data isolation rules (e.g. Zed).

### 2. `atbclone clone` CLI Enhancements
- Add `--data-dir` option:
  `@click.option("--data-dir", default=None, help="Custom data storage directory for this clone.")`
- Behavior:
  - If `--data-dir` is provided:
    - Check `supports_data_dir(recipe)`. If False, print error `t("clone_err_data_dir_not_supported", app_name=info.app_name)` and exit with code 1.
    - If True, resolve path: `target_data_dir = Path(data_dir).expanduser().resolve()`.
  - If `--data-dir` is not provided:
    - Default to `DEFAULT_DATA_DIR / clone_name`.
  - Pass `target_data_dir` to `CloneTask` and store in `CloneRecord.data_dir`.

### 3. `atbclone wizard` Interactive Wizard Enhancements
- Before proxy setup, check `supports_data_dir(recipe)`:
  - If True: prompt user for data storage path with default `~/.atbclone/Data/<clone_name>`.
  - If False: skip the prompt and use default path silently.
- Display the configured data directory in the wizard confirmation summary table.

### 4. `atbclone remove` Command & Interactive Cleanup
- Option specification:
  - `--with-data` / `--keep-data` / `--no-with-data` (default `None` / tri-state).
- Interactive logic:
  - If `--with-data` is passed: `delete_data = True`.
  - If `--keep-data` or `--no-with-data` is passed: `delete_data = False`.
  - If flag is not passed:
    - In an interactive terminal (`sys.stdin.isatty()`): prompt `click.confirm(t("remove_prompt_delete_data", data_dir=record.data_dir), default=False)` to set `delete_data`.
    - In a non-interactive pipe/CI environment: `delete_data = False`.
- Removal Execution:
  - Check privilege requirements for both `dest_path` and `data_dir` if `delete_data` is True:
    `needs_admin = not Path(record.dest_path).is_relative_to(Path.home()) or (delete_data and not Path(record.data_dir).is_relative_to(Path.home()))`
  - Generate and execute shell script:
    ```bash
    #!/bin/bash
    set -e
    rm -rf /path/to/App.app
    rm -rf /path/to/DataDir # only if delete_data is True
    ```
  - Remove entry from `clones.yaml`.

### 5. i18n Dictionary Updates (`src/atbclone/core/i18n.py`)
Add strings for:
- `clone_err_data_dir_not_supported` (en / zh)
- `wizard_prompt_data_dir` (en / zh)
- `wizard_confirm_data_dir` (en / zh)
- `remove_prompt_delete_data` (en / zh)

## Testing Strategy
- `tests/test_cmd_remove.py`:
  - Test remove without flags with interactive "y" response deletes both app and data dir.
  - Test remove without flags with interactive "n" response deletes only app.
  - Test explicit `--with-data` flag.
  - Test explicit `--keep-data` flag.
  - Test non-interactive environment fallback to keep data.
  - Test admin privilege elevation when data_dir is under system directory.
- `tests/test_cmd_clone.py`:
  - Test cloning with valid custom `--data-dir` on supported app (e.g. Chrome / WeChat).
  - Test cloning with `--data-dir` on unsupported app (e.g. Zed) returns exit code 1 with error.
- `tests/test_cmd_wizard.py`:
  - Test wizard prompting for custom data dir on supported app.
  - Test wizard skipping custom data dir prompt on unsupported app.
- `tests/test_recipes.py`:
  - Unit tests for `supports_data_dir` function across various recipes.
