# Clone Details Injected Parameters & Environment Design

## Overview
Enhance the "Clone Details" (`CloneDetailWindow`) dialog in ATBClone to display rich, structured runtime information regarding injected launch parameters (`--data-dir`, `--lang=...`, `-AppleLanguages`, etc.), injected environment variables (`HOME`, `LANG`, `LC_ALL`, `HTTP_PROXY`, etc.), and the full launcher `exec` command with a quick copy action.

## User Goals & Requirements
- When inspecting a clone in the GUI details dialog, users want to clearly understand what parameters and environment settings were injected into the clone's wrapper script.
- Provide structured breakdown of:
  1. Injected Launch Arguments (e.g. `--user-data-dir=...`, `--lang=zh-CN`)
  2. Injected Environment Variables (e.g. `HOME=...`, `LANG=...`, proxy settings)
  3. Full Launch Command / Exec Line with one-click copy to clipboard.
- Work reliably regardless of whether the clone's wrapper script is on disk or needs dynamic fallback computation from its Recipe and configuration.

## Architecture & Components

### 1. `CloneInspector` (`src/atbclone/core/clone_inspector.py`)
A dedicated core inspection utility that extracts and resolves runtime injection metadata for any `CloneRecord`.

- **Data Structure (`InjectedDetails`)**:
  ```python
  @dataclass
  class InjectedDetails:
      launch_args: list[str]
      env_vars: dict[str, str]
      exec_command: str
      source_type: str  # "wrapper_script" | "recipe_fallback"
  ```
- **Inspection Strategy (Hybrid)**:
  1. **Primary path (Disk inspection)**:
     - Check `{record.dest_path}/Contents/MacOS/*` for executable wrapper script.
     - Parse `export KEY="VALUE"` lines into `env_vars`.
     - Parse `exec <target_bin> <args...> "$@"` lines using `shlex.split` to extract `launch_args` and `exec_command`.
  2. **Fallback path (Recipe reconstruction)**:
     - If the wrapper file is not on disk or unreadable, query `RecipeLoader.match(record.bundle_id)`.
     - Reconstruct `env_vars`, `launch_args`, and `exec_command` using `record.data_dir`, `record.language`, and `record.proxy_summary` through `build_language_wrapper_snippet`.

### 2. GUI Layer (`src/atbclone/gui/windows/clone_detail.py`)
- Window size upgraded to `(560, 580)`.
- Wrapped in a `toga.ScrollContainer` for clean, responsive vertical scrolling.
- UI Layout divided into two distinct visual cards:
  - **Card 1: Basic Information (`基本信息`)**:
    - Clone Name (bold title)
    - Source App & Path
    - Bundle ID & New Bundle ID
    - Strategy, Language, Proxy Status
    - Destination Path, Data Storage Path, Created Date
  - **Card 2: Injected Launch Configuration (`注入与启动参数`)**:
    - Launch Arguments list (or "(None)" if none injected)
    - Environment Variables list
    - Exec Command box with a "Copy Command" (`复制命令`) button using macOS clipboard helper (`pbcopy`).
- Bottom action bar with "Close" (`关闭`) button.

### 3. Localization (`src/atbclone/core/i18n.py`)
Add localized keys for all 9 supported languages (`en`, `zh`, `zh_TW`, `ja`, `ko`, `de`, `fr`, `ru`, `es`):
- `win_detail_section_basic`: "Basic Information" / "基本信息"
- `win_detail_section_injected`: "Injected Parameters & Environment" / "注入与启动参数"
- `win_detail_launch_args`: "Launch Arguments" / "启动参数"
- `win_detail_env_vars`: "Environment Variables" / "环境变量"
- `win_detail_exec_cmd`: "Launch Command" / "启动命令"
- `win_detail_btn_copy_cmd`: "Copy Command" / "复制命令"
- `win_detail_cmd_copied`: "Copied!" / "已复制"
- `win_detail_none`: "None" / "无"

## Testing & Verification
- **Unit Tests**:
  - `tests/test_clone_inspector.py`:
    - Test parsing bash wrapper script with environment variables and launch args.
    - Test fallback reconstruction when wrapper script is missing.
    - Test edge cases (spaces in paths, empty args, proxy enabled/disabled).
- **Regression Tests**:
  - Run full test suite with `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/`.
- **Manual Verification**:
  - Open details dialog on existing clones and verify accurate display and copy functionality.
