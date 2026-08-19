"""Unit tests for the `clone` CLI command."""

from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
from click.testing import CliRunner

from atbclone.cli.main import cli
from atbclone.core.clone_task import CloneTask
from atbclone.core.models import AppInfo
from atbclone.executor.runner import CloneError
from atbclone.recipes.models import Recipe


@pytest.fixture
def mock_app_info(tmp_path: Path) -> AppInfo:
    app_dir = tmp_path / "WeChat.app"
    app_dir.mkdir(parents=True, exist_ok=True)
    return AppInfo(
        path=app_dir,
        bundle_id="com.tencent.xinWeChat",
        app_name="WeChat",
        executable=app_dir / "Contents" / "MacOS" / "WeChat",
        has_sandbox=True,
    )


@pytest.fixture
def mock_soft_recipe() -> Recipe:
    return Recipe(
        bundle_id="com.google.Chrome",
        app_name="Google Chrome",
        strategy="soft_clone",
    )


@pytest.fixture
def mock_hard_recipe() -> Recipe:
    return Recipe(
        bundle_id="com.tencent.xinWeChat",
        app_name="WeChat",
        strategy="hard_clone",
    )


def test_clone_soft_success(tmp_path: Path, mock_app_info: AppInfo, mock_soft_recipe: Recipe):
    runner = CliRunner()
    output_dir = tmp_path / "Applications"

    with patch("atbclone.cli.cmd_clone.AppInspector.inspect", return_value=mock_app_info) as mock_inspect, \
         patch("atbclone.cli.cmd_clone.RecipeLoader.match", return_value=mock_soft_recipe) as mock_match, \
         patch("atbclone.cli.cmd_clone.AppInspector.next_available_name", return_value=("WeChat2", 2)) as mock_next_name, \
         patch("atbclone.cli.cmd_clone.SoftCloneEngine.execute") as mock_soft_exec, \
         patch("atbclone.cli.cmd_clone.HardCloneEngine.execute") as mock_hard_exec, \
         patch("atbclone.cli.cmd_clone.StateManager.add"):

        result = runner.invoke(
            cli,
            ["clone", str(mock_app_info.path), "--output-dir", str(output_dir)],
        )

        assert result.exit_code == 0
        assert "Starting clone: WeChat -> WeChat2" in result.output
        assert "Success! Clone created at" in result.output
        assert str(output_dir / "WeChat2.app") in result.output

        mock_inspect.assert_called_once_with(str(mock_app_info.path))
        mock_match.assert_called_once_with(mock_app_info.bundle_id)
        mock_next_name.assert_called_once_with("WeChat", output_dir)
        mock_soft_exec.assert_called_once()
        mock_hard_exec.assert_not_called()

        task, needs_admin = mock_soft_exec.call_args[0]
        assert isinstance(task, CloneTask)
        assert task.source == mock_app_info
        assert task.dest_path == output_dir / "WeChat2.app"
        assert task.clone_name == "WeChat2"
        assert task.new_bundle_id == "com.tencent.xinWeChat.atbclone.2"
        assert task.data_dir == Path.home() / ".atbclone" / "Data" / "WeChat2"


def test_clone_hard_success(tmp_path: Path, mock_app_info: AppInfo, mock_hard_recipe: Recipe):
    runner = CliRunner()
    output_dir = tmp_path / "Applications"

    with patch("atbclone.cli.cmd_clone.AppInspector.inspect", return_value=mock_app_info), \
         patch("atbclone.cli.cmd_clone.RecipeLoader.match", return_value=mock_hard_recipe), \
         patch("atbclone.cli.cmd_clone.AppInspector.next_available_name", return_value=("WeChat2", 2)), \
         patch("atbclone.cli.cmd_clone.SoftCloneEngine.execute") as mock_soft_exec, \
         patch("atbclone.cli.cmd_clone.HardCloneEngine.execute") as mock_hard_exec, \
         patch("atbclone.cli.cmd_clone.StateManager.add"):

        result = runner.invoke(
            cli,
            ["clone", str(mock_app_info.path), "--output-dir", str(output_dir)],
        )

        assert result.exit_code == 0
        assert "Starting clone: WeChat -> WeChat2" in result.output
        assert "Success! Clone created at" in result.output
        mock_soft_exec.assert_not_called()
        mock_hard_exec.assert_called_once()


def test_clone_error_handling(tmp_path: Path, mock_app_info: AppInfo, mock_soft_recipe: Recipe):
    runner = CliRunner()
    output_dir = tmp_path / "Applications"

    with patch("atbclone.cli.cmd_clone.AppInspector.inspect", return_value=mock_app_info), \
         patch("atbclone.cli.cmd_clone.RecipeLoader.match", return_value=mock_soft_recipe), \
         patch("atbclone.cli.cmd_clone.AppInspector.next_available_name", return_value=("WeChat2", 2)), \
         patch("atbclone.cli.cmd_clone.SoftCloneEngine.execute", side_effect=CloneError("Permission denied")):

        result = runner.invoke(
            cli,
            ["clone", str(mock_app_info.path), "--output-dir", str(output_dir)],
        )

        assert result.exit_code == 1
        assert "Error: Permission denied" in result.output


def test_clone_generic_exception_handling(tmp_path: Path, mock_app_info: AppInfo, mock_soft_recipe: Recipe):
    runner = CliRunner()
    output_dir = tmp_path / "Applications"

    with patch("atbclone.cli.cmd_clone.AppInspector.inspect", return_value=mock_app_info), \
         patch("atbclone.cli.cmd_clone.RecipeLoader.match", return_value=mock_soft_recipe), \
         patch("atbclone.cli.cmd_clone.AppInspector.next_available_name", return_value=("WeChat2", 2)), \
         patch("atbclone.cli.cmd_clone.SoftCloneEngine.execute", side_effect=RuntimeError("Unexpected failure")):

        result = runner.invoke(
            cli,
            ["clone", str(mock_app_info.path), "--output-dir", str(output_dir)],
        )

        assert result.exit_code == 1
        assert "Error: Unexpected failure" in result.output


def test_clone_name_override(tmp_path: Path, mock_app_info: AppInfo, mock_soft_recipe: Recipe):
    runner = CliRunner()
    output_dir = tmp_path / "Applications"

    with patch("atbclone.cli.cmd_clone.AppInspector.inspect", return_value=mock_app_info), \
         patch("atbclone.cli.cmd_clone.RecipeLoader.match", return_value=mock_soft_recipe), \
         patch("atbclone.cli.cmd_clone.AppInspector.next_available_name", return_value=("WorkChat2", 2)) as mock_next_name, \
         patch("atbclone.cli.cmd_clone.SoftCloneEngine.execute") as mock_soft_exec, \
         patch("atbclone.cli.cmd_clone.StateManager.add"):

        result = runner.invoke(
            cli,
            [
                "clone",
                str(mock_app_info.path),
                "--name",
                "WorkChat",
                "--output-dir",
                str(output_dir),
            ],
        )

        assert result.exit_code == 0
        mock_next_name.assert_called_once_with("WorkChat", output_dir)
        assert "Starting clone: WeChat -> WorkChat2" in result.output
        assert str(output_dir / "WorkChat2.app") in result.output

        task, _ = mock_soft_exec.call_args[0]
        assert task.clone_name == "WorkChat2"
        assert task.new_bundle_id == "com.tencent.xinWeChat.atbclone.2"


def test_clone_output_dir_admin_detection(tmp_path: Path, mock_app_info: AppInfo, mock_soft_recipe: Recipe):
    runner = CliRunner()
    system_app_dir = Path("/Applications")

    with patch("atbclone.cli.cmd_clone.AppInspector.inspect", return_value=mock_app_info), \
         patch("atbclone.cli.cmd_clone.RecipeLoader.match", return_value=mock_soft_recipe), \
         patch("atbclone.cli.cmd_clone.AppInspector.next_available_name", return_value=("WeChat2", 2)), \
         patch("atbclone.cli.cmd_clone.Path.mkdir"), \
         patch("atbclone.cli.cmd_clone.SoftCloneEngine.execute") as mock_soft_exec, \
         patch("atbclone.cli.cmd_clone.StateManager.add"):

        result = runner.invoke(
            cli,
            [
                "clone",
                str(mock_app_info.path),
                "--output-dir",
                str(system_app_dir),
            ],
        )

        assert result.exit_code == 0
        task, needs_admin = mock_soft_exec.call_args[0]
        assert needs_admin is True
        assert task.dest_path == system_app_dir / "WeChat2.app"


def test_clone_default_output_dir(tmp_path: Path, mock_app_info: AppInfo, mock_soft_recipe: Recipe):
    runner = CliRunner()
    default_dir = Path.home() / "Applications"

    with patch("atbclone.cli.cmd_clone.AppInspector.inspect", return_value=mock_app_info), \
         patch("atbclone.cli.cmd_clone.RecipeLoader.match", return_value=mock_soft_recipe), \
         patch("atbclone.cli.cmd_clone.AppInspector.next_available_name", return_value=("WeChat2", 2)) as mock_next_name, \
         patch("atbclone.cli.cmd_clone.Path.mkdir"), \
         patch("atbclone.cli.cmd_clone.SoftCloneEngine.execute") as mock_soft_exec, \
         patch("atbclone.cli.cmd_clone.StateManager.add"):

        result = runner.invoke(
            cli,
            ["clone", str(mock_app_info.path)],
        )

        assert result.exit_code == 0
        mock_next_name.assert_called_once_with("WeChat", default_dir)
        task, needs_admin = mock_soft_exec.call_args[0]
        assert needs_admin is False
        assert task.dest_path == default_dir / "WeChat2.app"



def test_clone_help_command():
    runner = CliRunner()
    result = runner.invoke(cli, ["clone", "--help"])
    assert result.exit_code == 0
    assert "--name" in result.output
    assert "--display-name" in result.output
    assert "--icon" in result.output
    assert "--strategy" in result.output
    assert "--output-dir" in result.output
    assert "--proxy-host" in result.output
    assert "--proxy-port" in result.output
    assert "--proxy-type" in result.output
    assert "APP_PATH" in result.output


def test_clone_nonexistent_app_fails():
    runner = CliRunner()
    result = runner.invoke(cli, ["clone", "/nonexistent/path/App.app"])
    assert result.exit_code != 0
    assert "does not exist" in result.output or "Error" in result.output


def test_clone_strategy_override(tmp_path: Path, mock_app_info: AppInfo, mock_soft_recipe: Recipe):
    """--strategy overrides the recipe strategy."""
    runner = CliRunner()
    output_dir = tmp_path / "Applications"

    with patch("atbclone.cli.cmd_clone.AppInspector.inspect", return_value=mock_app_info), \
         patch("atbclone.cli.cmd_clone.RecipeLoader.match", return_value=mock_soft_recipe), \
         patch("atbclone.cli.cmd_clone.AppInspector.next_available_name", return_value=("WeChat2", 2)), \
         patch("atbclone.cli.cmd_clone.HardCloneEngine.execute") as mock_hard_exec, \
         patch("atbclone.cli.cmd_clone.StateManager.add"):

        result = runner.invoke(
            cli,
            [
                "clone",
                str(mock_app_info.path),
                "--output-dir", str(output_dir),
                "--strategy", "hard_clone",
            ],
        )

        assert result.exit_code == 0
        mock_hard_exec.assert_called_once()



def test_clone_custom_display_name(tmp_path: Path, mock_app_info: AppInfo, mock_soft_recipe: Recipe):
    """--display-name is passed into CloneTask.display_name (supports Unicode/Chinese)."""
    runner = CliRunner()
    output_dir = tmp_path / "Applications"

    with patch("atbclone.cli.cmd_clone.AppInspector.inspect", return_value=mock_app_info), \
         patch("atbclone.cli.cmd_clone.RecipeLoader.match", return_value=mock_soft_recipe), \
         patch("atbclone.cli.cmd_clone.AppInspector.next_available_name", return_value=("WeChat2", 2)), \
         patch("atbclone.cli.cmd_clone.SoftCloneEngine.execute") as mock_soft_exec, \
         patch("atbclone.cli.cmd_clone.StateManager.add"):

        result = runner.invoke(
            cli,
            [
                "clone",
                str(mock_app_info.path),
                "--output-dir", str(output_dir),
                "--display-name", "我的微信",
            ],
        )

        assert result.exit_code == 0
        task, _ = mock_soft_exec.call_args[0]
        assert task.display_name == "我的微信"


def test_clone_default_display_name_is_none(tmp_path: Path, mock_app_info: AppInfo, mock_soft_recipe: Recipe):
    """When --display-name is omitted, task.display_name should be None (engine falls back to clone_name)."""
    runner = CliRunner()
    output_dir = tmp_path / "Applications"

    with patch("atbclone.cli.cmd_clone.AppInspector.inspect", return_value=mock_app_info), \
         patch("atbclone.cli.cmd_clone.RecipeLoader.match", return_value=mock_soft_recipe), \
         patch("atbclone.cli.cmd_clone.AppInspector.next_available_name", return_value=("WeChat2", 2)), \
         patch("atbclone.cli.cmd_clone.SoftCloneEngine.execute") as mock_soft_exec, \
         patch("atbclone.cli.cmd_clone.StateManager.add"):

        result = runner.invoke(
            cli,
            ["clone", str(mock_app_info.path), "--output-dir", str(output_dir)],
        )

        assert result.exit_code == 0
        task, _ = mock_soft_exec.call_args[0]
        assert task.display_name is None


def test_clone_custom_icon(tmp_path: Path, mock_app_info: AppInfo, mock_soft_recipe: Recipe):
    """--icon is resolved to Path and passed into CloneTask.icon_path."""
    runner = CliRunner()
    output_dir = tmp_path / "Applications"
    icon_file = tmp_path / "custom.icns"
    icon_file.touch()

    with patch("atbclone.cli.cmd_clone.AppInspector.inspect", return_value=mock_app_info), \
         patch("atbclone.cli.cmd_clone.RecipeLoader.match", return_value=mock_soft_recipe), \
         patch("atbclone.cli.cmd_clone.AppInspector.next_available_name", return_value=("WeChat2", 2)), \
         patch("atbclone.cli.cmd_clone.SoftCloneEngine.execute") as mock_soft_exec, \
         patch("atbclone.cli.cmd_clone.StateManager.add"):

        result = runner.invoke(
            cli,
            [
                "clone",
                str(mock_app_info.path),
                "--output-dir", str(output_dir),
                "--icon", str(icon_file),
            ],
        )

        assert result.exit_code == 0
        task, _ = mock_soft_exec.call_args[0]
        assert task.icon_path == icon_file


def test_clone_icon_non_icns_rejected(tmp_path: Path, mock_app_info: AppInfo, mock_soft_recipe: Recipe):
    """--icon with a non-.icns file should exit with an error before cloning."""
    runner = CliRunner()
    output_dir = tmp_path / "Applications"
    bad_icon = tmp_path / "icon.png"
    bad_icon.touch()

    with patch("atbclone.cli.cmd_clone.AppInspector.inspect", return_value=mock_app_info), \
         patch("atbclone.cli.cmd_clone.RecipeLoader.match", return_value=mock_soft_recipe), \
         patch("atbclone.cli.cmd_clone.AppInspector.next_available_name", return_value=("WeChat2", 2)), \
         patch("atbclone.cli.cmd_clone.SoftCloneEngine.execute") as mock_soft_exec:

        result = runner.invoke(
            cli,
            [
                "clone",
                str(mock_app_info.path),
                "--output-dir", str(output_dir),
                "--icon", str(bad_icon),
            ],
        )

        assert result.exit_code == 1
        assert ".icns" in result.output
        mock_soft_exec.assert_not_called()


def test_clone_default_icon_is_none(tmp_path: Path, mock_app_info: AppInfo, mock_soft_recipe: Recipe):
    """When --icon is omitted, task.icon_path should be None."""
    runner = CliRunner()
    output_dir = tmp_path / "Applications"

    with patch("atbclone.cli.cmd_clone.AppInspector.inspect", return_value=mock_app_info), \
         patch("atbclone.cli.cmd_clone.RecipeLoader.match", return_value=mock_soft_recipe), \
         patch("atbclone.cli.cmd_clone.AppInspector.next_available_name", return_value=("WeChat2", 2)), \
         patch("atbclone.cli.cmd_clone.SoftCloneEngine.execute") as mock_soft_exec, \
         patch("atbclone.cli.cmd_clone.StateManager.add"):

        result = runner.invoke(
            cli,
            ["clone", str(mock_app_info.path), "--output-dir", str(output_dir)],
        )

        assert result.exit_code == 0
        task, _ = mock_soft_exec.call_args[0]
        assert task.icon_path is None



def test_clone_with_proxy_options(tmp_path: Path, mock_app_info: AppInfo, mock_soft_recipe: Recipe):
    runner = CliRunner()
    output_dir = tmp_path / "Applications"

    with patch("atbclone.cli.cmd_clone.AppInspector.inspect", return_value=mock_app_info), \
         patch("atbclone.cli.cmd_clone.RecipeLoader.match", return_value=mock_soft_recipe), \
         patch("atbclone.cli.cmd_clone.AppInspector.next_available_name", return_value=("WeChat2", 2)), \
         patch("atbclone.cli.cmd_clone.SoftCloneEngine.execute") as mock_soft_exec, \
         patch("atbclone.cli.cmd_clone.StateManager.add") as mock_state_add:

        result = runner.invoke(
            cli,
            [
                "clone",
                str(mock_app_info.path),
                "--output-dir",
                str(output_dir),
                "--proxy-host",
                "127.0.0.1",
                "--proxy-port",
                "1080",
                "--proxy-type",
                "socks5",
            ],
        )

        assert result.exit_code == 0
        mock_soft_exec.assert_called_once()
        task, _ = mock_soft_exec.call_args[0]
        assert task.recipe.proxy.enabled is True
        assert task.recipe.proxy.host == "127.0.0.1"
        assert task.recipe.proxy.port == 1080
        assert task.recipe.proxy.type == "socks5"

        mock_state_add.assert_called_once()
        record = mock_state_add.call_args[0][0]
        assert record.proxy_enabled is True
        assert record.proxy_summary == "socks5://127.0.0.1:1080"


def test_clone_proxy_host_without_explicit_port(tmp_path: Path, mock_app_info: AppInfo, mock_soft_recipe: Recipe):
    runner = CliRunner()
    output_dir = tmp_path / "Applications"

    with patch("atbclone.cli.cmd_clone.AppInspector.inspect", return_value=mock_app_info), \
         patch("atbclone.cli.cmd_clone.RecipeLoader.match", return_value=mock_soft_recipe), \
         patch("atbclone.cli.cmd_clone.AppInspector.next_available_name", return_value=("WeChat2", 2)), \
         patch("atbclone.cli.cmd_clone.SoftCloneEngine.execute") as mock_soft_exec, \
         patch("atbclone.cli.cmd_clone.StateManager.add") as mock_state_add:

        result = runner.invoke(
            cli,
            [
                "clone",
                str(mock_app_info.path),
                "--output-dir",
                str(output_dir),
                "--proxy-host",
                "10.0.0.1",
            ],
        )

        assert result.exit_code == 0
        mock_soft_exec.assert_called_once()
        task, _ = mock_soft_exec.call_args[0]
        assert task.recipe.proxy.enabled is True
        assert task.recipe.proxy.host == "10.0.0.1"
        assert task.recipe.proxy.port == 1080
        assert task.recipe.proxy.type == "http"


def test_clone_state_persistence_success(tmp_path: Path, mock_app_info: AppInfo, mock_soft_recipe: Recipe):
    from datetime import datetime

    runner = CliRunner()
    output_dir = tmp_path / "Applications"

    with patch("atbclone.cli.cmd_clone.AppInspector.inspect", return_value=mock_app_info), \
         patch("atbclone.cli.cmd_clone.RecipeLoader.match", return_value=mock_soft_recipe), \
         patch("atbclone.cli.cmd_clone.AppInspector.next_available_name", return_value=("WeChat2", 2)), \
         patch("atbclone.cli.cmd_clone.SoftCloneEngine.execute"), \
         patch("atbclone.cli.cmd_clone.StateManager.add") as mock_state_add:

        result = runner.invoke(
            cli,
            ["clone", str(mock_app_info.path), "--output-dir", str(output_dir)],
        )

        assert result.exit_code == 0
        mock_state_add.assert_called_once()
        record = mock_state_add.call_args[0][0]
        assert record.clone_name == "WeChat2"
        assert record.source_app == "WeChat"
        assert record.source_path == str(mock_app_info.path)
        assert record.bundle_id == "com.tencent.xinWeChat"
        assert record.strategy == "soft_clone"
        assert record.dest_path == str(output_dir / "WeChat2.app")
        assert record.data_dir == str(Path.home() / ".atbclone" / "Data" / "WeChat2")
        assert datetime.fromisoformat(record.created_at) is not None
        assert record.proxy_enabled is False
        assert record.proxy_summary == ""


def test_clone_failure_does_not_persist_state(tmp_path: Path, mock_app_info: AppInfo, mock_soft_recipe: Recipe):
    runner = CliRunner()
    output_dir = tmp_path / "Applications"

    with patch("atbclone.cli.cmd_clone.AppInspector.inspect", return_value=mock_app_info), \
         patch("atbclone.cli.cmd_clone.RecipeLoader.match", return_value=mock_soft_recipe), \
         patch("atbclone.cli.cmd_clone.AppInspector.next_available_name", return_value=("WeChat2", 2)), \
         patch("atbclone.cli.cmd_clone.SoftCloneEngine.execute", side_effect=CloneError("fail")), \
         patch("atbclone.cli.cmd_clone.StateManager.add") as mock_state_add:

        result = runner.invoke(
            cli,
            ["clone", str(mock_app_info.path), "--output-dir", str(output_dir)],
        )

        assert result.exit_code == 1
        mock_state_add.assert_not_called()


def test_clone_unlisted_app_auto_probes(tmp_path: Path):
    from atbclone.core.app_prober import ProbeResult

    runner = CliRunner()
    output_dir = tmp_path / "Applications"
    app_dir = tmp_path / "UnlistedApp.app"
    app_dir.mkdir(parents=True, exist_ok=True)

    unlisted_info = AppInfo(
        path=app_dir,
        bundle_id="com.unlisted.app",
        app_name="UnlistedApp",
        executable=app_dir / "Contents" / "MacOS" / "UnlistedApp",
        has_sandbox=False,
    )
    probed_recipe = Recipe(
        bundle_id="com.unlisted.app",
        app_name="UnlistedApp",
        strategy="hard_clone",
        strip_sandbox=False,
        environment_injection={"HOME": "{{ATB_DATA_DIR}}/Home"},
    )
    probe_result = ProbeResult(
        app_info=unlisted_info,
        has_sandbox=False,
        frameworks=[],
        strategy="hard_clone",
        reason="Native macOS application (Non-sandboxed)",
        recipe=probed_recipe,
    )

    with patch("atbclone.cli.cmd_clone.AppInspector.inspect", return_value=unlisted_info), \
         patch("atbclone.cli.cmd_clone.AppProber.analyze", return_value=probe_result) as mock_analyze, \
         patch("atbclone.cli.cmd_clone.AppInspector.next_available_name", return_value=("UnlistedApp2", 2)), \
         patch("atbclone.cli.cmd_clone.HardCloneEngine.execute") as mock_hard_exec, \
         patch("atbclone.cli.cmd_clone.StateManager.add"):

        result = runner.invoke(
            cli,
            ["clone", str(app_dir), "--output-dir", str(output_dir)],
        )

        assert result.exit_code == 0
        assert "No pre-configured recipe found for 'com.unlisted.app'" in result.output
        assert "Probing application architecture and entitlements" in result.output
        assert "Probed Strategy:" in result.output
        mock_analyze.assert_called_once_with(str(app_dir))
        mock_hard_exec.assert_called_once()



