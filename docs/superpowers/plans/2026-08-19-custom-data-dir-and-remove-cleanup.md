# Custom Data Directory & Remove Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `--data-dir` support to `atbclone clone` and `atbclone wizard` with app capability validation, and update `atbclone remove` to interactively prompt for data directory cleanup.

**Architecture:** A helper `supports_data_dir(recipe)` checks if a recipe isolates data via `{{ATB_DATA_DIR}}` in launch args or environment variables. CLI commands (`clone`, `wizard`) validate `--data-dir` before configuring `CloneTask`. `cmd_remove` supports `--with-data`, `--keep-data`, or interactive prompts in TTY sessions with proper privilege escalation for system paths.

**Tech Stack:** Python 3.12, Click, Rich, Pytest

## Global Constraints
- Target macOS native patterns, PySide6, Python 3.12+ with `conda run -n ATBClone`
- Test command: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/`
- Zero external runtime dependencies beyond existing packages (click, rich, pydantic, pyyaml)

---

### Task 1: Core Capability Detection (`supports_data_dir`)

**Files:**
- Modify: `src/atbclone/recipes/models.py`
- Test: `tests/test_recipes.py`

**Interfaces:**
- Produces: `supports_data_dir(recipe: Recipe) -> bool` in `atbclone.recipes.models`

- [ ] **Step 1: Write the failing tests in `tests/test_recipes.py`**

```python
def test_supports_data_dir_with_launch_args():
    from atbclone.recipes.models import Recipe, supports_data_dir

    recipe = Recipe(
        bundle_id="com.google.Chrome",
        app_name="Chrome",
        strategy="hard_clone",
        launch_args=["--user-data-dir={{ATB_DATA_DIR}}"],
    )
    assert supports_data_dir(recipe) is True


def test_supports_data_dir_with_env_injection():
    from atbclone.recipes.models import Recipe, supports_data_dir

    recipe = Recipe(
        bundle_id="com.tencent.xinWeChat",
        app_name="WeChat",
        strategy="hard_clone",
        environment_injection={"HOME": "{{ATB_DATA_DIR}}/Home"},
    )
    assert supports_data_dir(recipe) is True


def test_supports_data_dir_unsupported():
    from atbclone.recipes.models import Recipe, supports_data_dir

    recipe = Recipe(
        bundle_id="dev.zed.Zed",
        app_name="Zed",
        strategy="soft_clone",
        launch_args=[],
        environment_injection={},
    )
    assert supports_data_dir(recipe) is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_recipes.py -k "test_supports_data_dir"`
Expected: FAIL (cannot import name `supports_data_dir`)

- [ ] **Step 3: Implement `supports_data_dir` in `src/atbclone/recipes/models.py`**

```python
def supports_data_dir(recipe: Recipe) -> bool:
    """Return True if the recipe uses {{ATB_DATA_DIR}} in launch args or environment injection."""
    has_in_args = any("{{ATB_DATA_DIR}}" in arg for arg in recipe.launch_args)
    has_in_env = any("{{ATB_DATA_DIR}}" in val for val in recipe.environment_injection.values())
    return has_in_args or has_in_env
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_recipes.py -k "test_supports_data_dir"`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/atbclone/recipes/models.py tests/test_recipes.py
git commit -m "feat(recipes): add supports_data_dir capability check"
```

---

### Task 2: i18n Dictionary Additions

**Files:**
- Modify: `src/atbclone/core/i18n.py`
- Test: `tests/test_i18n.py`

**Interfaces:**
- Produces: new keys `clone_err_data_dir_not_supported`, `wizard_prompt_data_dir`, `wizard_confirm_data_dir`, `remove_prompt_delete_data`

- [ ] **Step 1: Write test in `tests/test_i18n.py`**

```python
def test_new_data_dir_i18n_keys():
    from atbclone.core.i18n import t

    msg_en = t("clone_err_data_dir_not_supported", lang="en", app_name="Zed")
    assert "Zed" in msg_en
    assert "does not support custom data directory" in msg_en

    msg_zh = t("clone_err_data_dir_not_supported", lang="zh", app_name="Zed")
    assert "Zed" in msg_zh
    assert "不支持自定义数据目录" in msg_zh

    assert "Data storage directory" in t("wizard_prompt_data_dir", lang="en")
    assert "数据存储目录" in t("wizard_prompt_data_dir", lang="zh")

    assert "/tmp/test" in t("wizard_confirm_data_dir", lang="en", data_dir="/tmp/test")
    assert "Also delete data directory /tmp/test?" in t("remove_prompt_delete_data", lang="en", data_dir="/tmp/test")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_i18n.py -k "test_new_data_dir_i18n_keys"`
Expected: FAIL

- [ ] **Step 3: Update `src/atbclone/core/i18n.py`**

Add the translations:
```python
    "clone_err_data_dir_not_supported": {
        "en": "Error: Application '{app_name}' does not support custom data directory.",
        "zh": "错误：应用 '{app_name}' 不支持自定义数据目录。",
    },
    "wizard_prompt_data_dir": {
        "en": "Data storage directory",
        "zh": "数据存储目录",
    },
    "wizard_confirm_data_dir": {
        "en": "  Data Dir:    {data_dir}",
        "zh": "  数据目录:    {data_dir}",
    },
    "remove_prompt_delete_data": {
        "en": "Also delete data directory {data_dir}?",
        "zh": "是否同时删除数据目录 {data_dir}？",
    },
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_i18n.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/atbclone/core/i18n.py tests/test_i18n.py
git commit -m "feat(i18n): add translations for data directory options"
```

---

### Task 3: CLI `atbclone remove` Interactive Data Cleanup & Permissions

**Files:**
- Modify: `src/atbclone/cli/cmd_remove.py`
- Test: `tests/test_cmd_remove.py`

**Interfaces:**
- Consumes: `StateManager`, `CloneRecord`, `Runner`, `i18n.t`
- Produces: Updated `remove` CLI command with interactive prompt and `--with-data` / `--keep-data` support.

- [ ] **Step 1: Write unit tests in `tests/test_cmd_remove.py`**

```python
def test_remove_interactive_confirm_yes(mock_record_user_dir: CloneRecord):
    runner = CliRunner()
    with patch("atbclone.cli.cmd_remove.StateManager.get", return_value=mock_record_user_dir), \
         patch("atbclone.cli.cmd_remove.Runner.run") as mock_runner, \
         patch("atbclone.cli.cmd_remove.StateManager.remove") as mock_remove:

        result = runner.invoke(cli, ["remove", "WeChat2"], input="y\n")
        assert result.exit_code == 0
        assert f"Also delete data directory {mock_record_user_dir.data_dir}?" in result.output
        assert "Success! Removed clone 'WeChat2'" in result.output

        mock_runner.assert_called_once()
        script, needs_admin = mock_runner.call_args[0]
        assert f"rm -rf {mock_record_user_dir.dest_path}" in script
        assert f"rm -rf {mock_record_user_dir.data_dir}" in script
        mock_remove.assert_called_once_with("WeChat2")


def test_remove_interactive_confirm_no(mock_record_user_dir: CloneRecord):
    runner = CliRunner()
    with patch("atbclone.cli.cmd_remove.StateManager.get", return_value=mock_record_user_dir), \
         patch("atbclone.cli.cmd_remove.Runner.run") as mock_runner, \
         patch("atbclone.cli.cmd_remove.StateManager.remove") as mock_remove:

        result = runner.invoke(cli, ["remove", "WeChat2"], input="n\n")
        assert result.exit_code == 0
        assert f"Also delete data directory {mock_record_user_dir.data_dir}?" in result.output
        assert "Success! Removed clone 'WeChat2'" in result.output

        mock_runner.assert_called_once()
        script, needs_admin = mock_runner.call_args[0]
        assert f"rm -rf {mock_record_user_dir.dest_path}" in script
        assert mock_record_user_dir.data_dir not in script
        mock_remove.assert_called_once_with("WeChat2")


def test_remove_explicit_keep_data(mock_record_user_dir: CloneRecord):
    runner = CliRunner()
    with patch("atbclone.cli.cmd_remove.StateManager.get", return_value=mock_record_user_dir), \
         patch("atbclone.cli.cmd_remove.Runner.run") as mock_runner, \
         patch("atbclone.cli.cmd_remove.StateManager.remove") as mock_remove:

        result = runner.invoke(cli, ["remove", "WeChat2", "--keep-data"])
        assert result.exit_code == 0
        assert "Also delete data directory" not in result.output

        script, _ = mock_runner.call_args[0]
        assert f"rm -rf {mock_record_user_dir.dest_path}" in script
        assert mock_record_user_dir.data_dir not in script


def test_remove_admin_elevation_due_to_data_dir():
    record = CloneRecord(
        clone_name="WeChat2",
        source_app="WeChat",
        source_path="/Applications/WeChat.app",
        bundle_id="com.tencent.xinWeChat",
        strategy="hard_clone",
        dest_path=str(Path.home() / "Applications" / "WeChat2.app"),
        data_dir="/Library/Application Support/WeChat2",
        created_at="2026-08-18T20:00:00",
        proxy_enabled=False,
        proxy_summary="",
    )
    runner = CliRunner()
    with patch("atbclone.cli.cmd_remove.StateManager.get", return_value=record), \
         patch("atbclone.cli.cmd_remove.Runner.run") as mock_runner, \
         patch("atbclone.cli.cmd_remove.StateManager.remove"):

        result = runner.invoke(cli, ["remove", "WeChat2", "--with-data"])
        assert result.exit_code == 0
        script, needs_admin = mock_runner.call_args[0]
        assert needs_admin is True
```

- [ ] **Step 2: Run tests to verify failure**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_cmd_remove.py`
Expected: FAIL

- [ ] **Step 3: Implement interactive cleanup in `src/atbclone/cli/cmd_remove.py`**

```python
"""CLI command for removing cloned applications."""

import sys
import shlex
from pathlib import Path
import click
from rich.console import Console

from atbclone.core.i18n import t
from atbclone.core.state import StateManager
from atbclone.executor.runner import CloneError, Runner

console = Console()


@click.command(name="remove")
@click.argument("clone_name")
@click.option(
    "--with-data/--keep-data",
    "with_data",
    default=None,
    help="Also delete or keep the data directory.",
)
@click.option(
    "--no-with-data",
    "no_with_data",
    is_flag=True,
    hidden=True,
    help="Alias for --keep-data",
)
def remove(clone_name: str, with_data: bool | None, no_with_data: bool) -> None:
    """Remove a cloned application."""
    sm = StateManager()
    record = sm.get(clone_name)
    if record is None:
        console.print(t("remove_err_not_found", clone_name=clone_name))
        sys.exit(1)

    if no_with_data:
        with_data = False

    delete_data = False
    if with_data is True:
        delete_data = True
    elif with_data is False:
        delete_data = False
    else:
        # Prompt interactively if in interactive terminal or click runner
        try:
            delete_data = click.confirm(
                t("remove_prompt_delete_data", data_dir=record.data_dir),
                default=False,
            )
        except click.Abort:
            sys.exit(1)

    needs_admin = (
        not Path(record.dest_path).is_relative_to(Path.home())
        or (delete_data and not Path(record.data_dir).is_relative_to(Path.home()))
    )

    lines = [
        "#!/bin/bash",
        "set -e",
        f"rm -rf {shlex.quote(record.dest_path)}",
    ]

    if delete_data:
        lines.append(f"rm -rf {shlex.quote(record.data_dir)}")

    script = "\n".join(lines) + "\n"

    try:
        Runner.run(script, needs_admin)
    except (CloneError, Exception) as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)

    sm.remove(clone_name)
    console.print(t("remove_success", clone_name=clone_name))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_cmd_remove.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/atbclone/cli/cmd_remove.py tests/test_cmd_remove.py
git commit -m "feat(remove): add interactive data directory cleanup and --keep-data option"
```

---

### Task 4: CLI `atbclone clone` Custom `--data-dir` Support & Capability Check

**Files:**
- Modify: `src/atbclone/cli/cmd_clone.py`
- Test: `tests/test_cmd_clone.py`

**Interfaces:**
- Consumes: `supports_data_dir`, `CloneTask`, `RecipeLoader`, `AppProber`
- Produces: `--data-dir` option on `atbclone clone`

- [ ] **Step 1: Write unit tests in `tests/test_cmd_clone.py`**

```python
def test_clone_with_custom_data_dir_supported(tmp_path):
    runner = CliRunner()
    fake_app = tmp_path / "Chrome.app"
    fake_app.mkdir()
    custom_data = tmp_path / "custom_chrome_data"

    with patch("atbclone.cli.cmd_clone.AppInspector.inspect") as mock_inspect, \
         patch("atbclone.cli.cmd_clone.RecipeLoader.has_recipe", return_value=True), \
         patch("atbclone.cli.cmd_clone.RecipeLoader.match") as mock_match, \
         patch("atbclone.cli.cmd_clone.SoftCloneEngine.execute") as mock_exec, \
         patch("atbclone.cli.cmd_clone.StateManager.add") as mock_add:

        from atbclone.core.models import AppInfo
        from atbclone.recipes.models import Recipe
        mock_inspect.return_value = AppInfo(fake_app, "com.google.Chrome", "Chrome", fake_app / "MacOS/Chrome", False)
        mock_match.return_value = Recipe(
            bundle_id="com.google.Chrome",
            app_name="Chrome",
            strategy="soft_clone",
            launch_args=["--user-data-dir={{ATB_DATA_DIR}}"],
        )

        result = runner.invoke(cli, ["clone", str(fake_app), "--data-dir", str(custom_data)])
        assert result.exit_code == 0
        task = mock_exec.call_args[0][0]
        assert task.data_dir == custom_data.resolve()
        record = mock_add.call_args[0][0]
        assert record.data_dir == str(custom_data.resolve())


def test_clone_with_custom_data_dir_unsupported(tmp_path):
    runner = CliRunner()
    fake_app = tmp_path / "Zed.app"
    fake_app.mkdir()
    custom_data = tmp_path / "custom_zed_data"

    with patch("atbclone.cli.cmd_clone.AppInspector.inspect") as mock_inspect, \
         patch("atbclone.cli.cmd_clone.RecipeLoader.has_recipe", return_value=True), \
         patch("atbclone.cli.cmd_clone.RecipeLoader.match") as mock_match:

        from atbclone.core.models import AppInfo
        from atbclone.recipes.models import Recipe
        mock_inspect.return_value = AppInfo(fake_app, "dev.zed.Zed", "Zed", fake_app / "MacOS/Zed", False)
        mock_match.return_value = Recipe(
            bundle_id="dev.zed.Zed",
            app_name="Zed",
            strategy="soft_clone",
            launch_args=[],
            environment_injection={},
        )

        result = runner.invoke(cli, ["clone", str(fake_app), "--data-dir", str(custom_data)])
        assert result.exit_code == 1
        assert "does not support custom data directory" in result.output
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_cmd_clone.py -k "custom_data_dir"`
Expected: FAIL

- [ ] **Step 3: Update `src/atbclone/cli/cmd_clone.py`**

Add `--data-dir` option:
```python
@click.option("--data-dir", default=None, help="Custom data storage directory for this clone.")
```
Check `supports_data_dir(recipe)`:
```python
    if data_dir:
        if not supports_data_dir(recipe):
            console.print(t("clone_err_data_dir_not_supported", app_name=info.app_name), soft_wrap=True)
            sys.exit(1)
        target_data_dir = Path(data_dir).expanduser().resolve()
    else:
        target_data_dir = DEFAULT_DATA_DIR / clone_name
```
Pass `data_dir=target_data_dir` to `CloneTask` and `CloneRecord`.

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_cmd_clone.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/atbclone/cli/cmd_clone.py tests/test_cmd_clone.py
git commit -m "feat(clone): add --data-dir flag with recipe capability validation"
```

---

### Task 5: CLI `atbclone wizard` Interactive Data Directory Prompt

**Files:**
- Modify: `src/atbclone/cli/cmd_wizard.py`
- Test: `tests/test_cmd_wizard.py`

**Interfaces:**
- Consumes: `supports_data_dir`, `i18n.t`, `DEFAULT_DATA_DIR`

- [ ] **Step 1: Write test in `tests/test_cmd_wizard.py`**

```python
def test_wizard_custom_data_dir_prompt(tmp_path):
    runner = CliRunner()
    fake_app = tmp_path / "Chrome.app"
    fake_app.mkdir()

    with patch("atbclone.cli.cmd_wizard.AppInspector.inspect") as mock_inspect, \
         patch("atbclone.cli.cmd_wizard.RecipeLoader.match") as mock_match, \
         patch("atbclone.cli.cmd_wizard.SoftCloneEngine.execute") as mock_exec, \
         patch("atbclone.cli.cmd_wizard.StateManager.add") as mock_add:

        from atbclone.core.models import AppInfo
        from atbclone.recipes.models import Recipe
        mock_inspect.return_value = AppInfo(fake_app, "com.google.Chrome", "Chrome", fake_app / "MacOS/Chrome", False)
        mock_match.return_value = Recipe(
            bundle_id="com.google.Chrome",
            app_name="Chrome",
            strategy="soft_clone",
            launch_args=["--user-data-dir={{ATB_DATA_DIR}}"],
        )

        custom_dir = str(tmp_path / "custom_data")
        # Inputs: app_path, clone_name, display_name, icon, output_dir, data_dir, use_proxy, confirm
        inputs = f"{fake_app}\n\n\n\n\n{custom_dir}\nn\ny\n"
        result = runner.invoke(cli, ["wizard"], input=inputs)
        assert result.exit_code == 0
        task = mock_exec.call_args[0][0]
        assert task.data_dir == Path(custom_dir).resolve()
        record = mock_add.call_args[0][0]
        assert record.data_dir == str(Path(custom_dir).resolve())
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_cmd_wizard.py -k "test_wizard_custom_data_dir_prompt"`
Expected: FAIL

- [ ] **Step 3: Update `src/atbclone/cli/cmd_wizard.py`**

Import `supports_data_dir`:
```python
from atbclone.recipes.models import RecipeLoader, supports_data_dir
```
In interactive flow:
```python
    # 7. Data storage directory (if supported)
    if supports_data_dir(recipe):
        default_data_dir = str(DEFAULT_DATA_DIR / clone_name)
        data_dir_input = click.prompt(t("wizard_prompt_data_dir"), default=default_data_dir)
        target_data_dir = Path(data_dir_input).expanduser().resolve()
    else:
        target_data_dir = DEFAULT_DATA_DIR / clone_name
```
In confirmation section:
```python
    if supports_data_dir(recipe):
        console.print(t("wizard_confirm_data_dir", data_dir=target_data_dir))
```
Use `data_dir=target_data_dir` in `CloneTask` and `CloneRecord`.

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_cmd_wizard.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/atbclone/cli/cmd_wizard.py tests/test_cmd_wizard.py
git commit -m "feat(wizard): add data storage directory prompt for supported apps"
```

---

### Task 6: Full Test Suite Verification

**Files:**
- Test: All tests in `tests/`

- [ ] **Step 1: Run complete test suite**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/`
Expected: 100% tests pass.
