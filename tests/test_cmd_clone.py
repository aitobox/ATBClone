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
         patch("atbclone.cli.cmd_clone.HardCloneEngine.execute") as mock_hard_exec:

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
        assert task.new_bundle_id == "com.tencent.xinWeChat.atb2"
        assert task.data_dir == Path.home() / ".AIToBox" / "Data" / "WeChat2"


def test_clone_hard_success(tmp_path: Path, mock_app_info: AppInfo, mock_hard_recipe: Recipe):
    runner = CliRunner()
    output_dir = tmp_path / "Applications"

    with patch("atbclone.cli.cmd_clone.AppInspector.inspect", return_value=mock_app_info), \
         patch("atbclone.cli.cmd_clone.RecipeLoader.match", return_value=mock_hard_recipe), \
         patch("atbclone.cli.cmd_clone.AppInspector.next_available_name", return_value=("WeChat2", 2)), \
         patch("atbclone.cli.cmd_clone.SoftCloneEngine.execute") as mock_soft_exec, \
         patch("atbclone.cli.cmd_clone.HardCloneEngine.execute") as mock_hard_exec:

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
         patch("atbclone.cli.cmd_clone.SoftCloneEngine.execute") as mock_soft_exec:

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
        assert task.new_bundle_id == "com.tencent.xinWeChat.atb2"


def test_clone_output_dir_admin_detection(tmp_path: Path, mock_app_info: AppInfo, mock_soft_recipe: Recipe):
    runner = CliRunner()
    system_app_dir = Path("/Applications")

    with patch("atbclone.cli.cmd_clone.AppInspector.inspect", return_value=mock_app_info), \
         patch("atbclone.cli.cmd_clone.RecipeLoader.match", return_value=mock_soft_recipe), \
         patch("atbclone.cli.cmd_clone.AppInspector.next_available_name", return_value=("WeChat2", 2)), \
         patch("atbclone.cli.cmd_clone.Path.mkdir"), \
         patch("atbclone.cli.cmd_clone.SoftCloneEngine.execute") as mock_soft_exec:

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
         patch("atbclone.cli.cmd_clone.SoftCloneEngine.execute") as mock_soft_exec:

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
    assert "--output-dir" in result.output
    assert "APP_PATH" in result.output


def test_clone_nonexistent_app_fails():
    runner = CliRunner()
    result = runner.invoke(cli, ["clone", "/nonexistent/path/App.app"])
    assert result.exit_code != 0
    assert "does not exist" in result.output or "Error" in result.output

