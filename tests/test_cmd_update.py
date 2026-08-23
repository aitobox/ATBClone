"""Unit tests for the `update` CLI command."""

from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
from click.testing import CliRunner

from atbclone.cli.main import cli
from atbclone.core.clone_task import CloneTask
from atbclone.core.models import AppInfo
from atbclone.core.state import CloneRecord
from atbclone.executor.runner import CloneError
from atbclone.recipes.models import Recipe


@pytest.fixture
def mock_record_user_dir(tmp_path: Path) -> CloneRecord:
    source_app = tmp_path / "WeChat.app"
    source_app.mkdir(parents=True, exist_ok=True)
    return CloneRecord(
        clone_name="WeChat2",
        source_app="WeChat",
        source_path=str(source_app),
        bundle_id="com.tencent.xinWeChat",
        strategy="hard_clone",
        dest_path=str(Path.home() / "Applications" / "WeChat2.app"),
        data_dir=str(Path.home() / "ATBClone" / "Data" / "WeChat2"),
        created_at="2026-08-18T20:00:00+00:00",
        proxy_enabled=False,
        proxy_summary="",
        new_bundle_id="com.tencent.xinWeChat.atbclone.2",
    )


@pytest.fixture
def mock_record_admin_dir(tmp_path: Path) -> CloneRecord:
    source_app = tmp_path / "WeChat.app"
    source_app.mkdir(parents=True, exist_ok=True)
    return CloneRecord(
        clone_name="WeChat2",
        source_app="WeChat",
        source_path=str(source_app),
        bundle_id="com.tencent.xinWeChat",
        strategy="hard_clone",
        dest_path="/Applications/WeChat2.app",
        data_dir=str(Path.home() / "ATBClone" / "Data" / "WeChat2"),
        created_at="2026-08-18T20:00:00+00:00",
        proxy_enabled=False,
        proxy_summary="",
        new_bundle_id="com.tencent.xinWeChat.atbclone.2",
    )


@pytest.fixture
def mock_record_soft_clone(tmp_path: Path) -> CloneRecord:
    source_app = tmp_path / "Chrome.app"
    source_app.mkdir(parents=True, exist_ok=True)
    return CloneRecord(
        clone_name="Chrome2",
        source_app="Google Chrome",
        source_path=str(source_app),
        bundle_id="com.google.Chrome",
        strategy="soft_clone",
        dest_path=str(Path.home() / "Applications" / "Chrome2.app"),
        data_dir=str(Path.home() / "ATBClone" / "Data" / "Chrome2"),
        created_at="2026-08-18T20:00:00+00:00",
        proxy_enabled=True,
        proxy_summary="http://127.0.0.1:8080",
        new_bundle_id="com.google.Chrome.atbclone.2",
    )


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
def mock_hard_recipe() -> Recipe:
    return Recipe(
        bundle_id="com.tencent.xinWeChat",
        app_name="WeChat",
        strategy="hard_clone",
    )


@pytest.fixture
def mock_soft_recipe() -> Recipe:
    return Recipe(
        bundle_id="com.google.Chrome",
        app_name="Google Chrome",
        strategy="soft_clone",
    )


def test_update_not_found():
    runner = CliRunner()
    with patch("atbclone.cli.cmd_update.StateManager.get", return_value=None):
        result = runner.invoke(cli, ["update", "WeChat2"])
        assert result.exit_code == 1
        assert "Error:" in result.output
        assert "Clone 'WeChat2' not found." in result.output


def test_update_source_missing(mock_record_user_dir: CloneRecord):
    runner = CliRunner()
    mock_record_user_dir.source_path = "/nonexistent/path/WeChat.app"
    with patch("atbclone.cli.cmd_update.StateManager.get", return_value=mock_record_user_dir):
        result = runner.invoke(cli, ["update", "WeChat2"])
        assert result.exit_code == 1
        assert "Error:" in result.output
        assert "Source app not found" in result.output


def test_update_success_hard_clone(
    mock_record_user_dir: CloneRecord,
    mock_app_info: AppInfo,
    mock_hard_recipe: Recipe,
):
    runner = CliRunner()
    with patch("atbclone.cli.cmd_update.StateManager.get", return_value=mock_record_user_dir), \
         patch("atbclone.cli.cmd_update.Runner.run") as mock_runner, \
         patch("atbclone.cli.cmd_update.AppInspector.inspect", return_value=mock_app_info) as mock_inspect, \
         patch("atbclone.cli.cmd_update.RecipeLoader.match", return_value=mock_hard_recipe) as mock_match, \
         patch("atbclone.cli.cmd_update.HardCloneEngine.execute") as mock_hard_exec, \
         patch("atbclone.cli.cmd_update.SoftCloneEngine.execute") as mock_soft_exec, \
         patch("atbclone.cli.cmd_update.StateManager.add") as mock_state_add:

        result = runner.invoke(cli, ["update", "WeChat2"])
        assert result.exit_code == 0
        assert "Updating WeChat2..." in result.output
        assert "Success! Updated WeChat2" in result.output

        # Verify step 1: rm -rf old .app
        mock_runner.assert_called_once()
        script, needs_admin = mock_runner.call_args[0]
        assert needs_admin is False
        assert f"rm -rf {mock_record_user_dir.dest_path}" in script
        assert mock_record_user_dir.data_dir not in script

        # Verify step 2: inspect and clone
        mock_inspect.assert_called_once_with(mock_record_user_dir.source_path)
        mock_match.assert_called_once_with(mock_app_info.bundle_id)
        mock_hard_exec.assert_called_once()
        mock_soft_exec.assert_not_called()

        task, task_needs_admin = mock_hard_exec.call_args[0]
        assert isinstance(task, CloneTask)
        assert task.dest_path == Path(mock_record_user_dir.dest_path)
        assert task.data_dir == Path(mock_record_user_dir.data_dir)
        assert task.clone_name == "WeChat2"
        assert task.new_bundle_id == "com.tencent.xinWeChat.atbclone.2"
        assert task_needs_admin is False

        # Verify state update
        mock_state_add.assert_called_once()
        updated_rec = mock_state_add.call_args[0][0]
        assert updated_rec.clone_name == "WeChat2"
        assert updated_rec.created_at != "2026-08-18T20:00:00+00:00"


def test_update_success_soft_clone(
    mock_record_soft_clone: CloneRecord,
    mock_soft_recipe: Recipe,
    tmp_path: Path,
):
    runner = CliRunner()
    chrome_info = AppInfo(
        path=Path(mock_record_soft_clone.source_path),
        bundle_id="com.google.Chrome",
        app_name="Google Chrome",
        executable=Path(mock_record_soft_clone.source_path) / "Contents" / "MacOS" / "Google Chrome",
        has_sandbox=True,
    )

    with patch("atbclone.cli.cmd_update.StateManager.get", return_value=mock_record_soft_clone), \
         patch("atbclone.cli.cmd_update.Runner.run") as mock_runner, \
         patch("atbclone.cli.cmd_update.AppInspector.inspect", return_value=chrome_info), \
         patch("atbclone.cli.cmd_update.RecipeLoader.match", return_value=mock_soft_recipe), \
         patch("atbclone.cli.cmd_update.HardCloneEngine.execute") as mock_hard_exec, \
         patch("atbclone.cli.cmd_update.SoftCloneEngine.execute") as mock_soft_exec, \
         patch("atbclone.cli.cmd_update.StateManager.add") as mock_state_add:

        result = runner.invoke(cli, ["update", "Chrome2"])
        assert result.exit_code == 0
        assert "Updating Chrome2..." in result.output
        assert "Success! Updated Chrome2" in result.output

        mock_soft_exec.assert_called_once()
        mock_hard_exec.assert_not_called()

        task, needs_admin = mock_soft_exec.call_args[0]
        assert task.clone_name == "Chrome2"
        assert task.recipe.proxy.enabled is True
        assert task.recipe.proxy.host == "127.0.0.1"
        assert task.recipe.proxy.port == 8080

        mock_state_add.assert_called_once()


def test_update_rm_fails(mock_record_user_dir: CloneRecord):
    runner = CliRunner()
    with patch("atbclone.cli.cmd_update.StateManager.get", return_value=mock_record_user_dir), \
         patch("atbclone.cli.cmd_update.Runner.run", side_effect=CloneError("Permission denied")), \
         patch("atbclone.cli.cmd_update.HardCloneEngine.execute") as mock_hard_exec, \
         patch("atbclone.cli.cmd_update.StateManager.add") as mock_state_add:

        result = runner.invoke(cli, ["update", "WeChat2"])
        assert result.exit_code == 1
        assert "Error:" in result.output
        assert "Permission denied" in result.output

        mock_hard_exec.assert_not_called()
        mock_state_add.assert_not_called()


def test_update_engine_fails(
    mock_record_user_dir: CloneRecord,
    mock_app_info: AppInfo,
    mock_hard_recipe: Recipe,
):
    runner = CliRunner()
    with patch("atbclone.cli.cmd_update.StateManager.get", return_value=mock_record_user_dir), \
         patch("atbclone.cli.cmd_update.Runner.run"), \
         patch("atbclone.cli.cmd_update.AppInspector.inspect", return_value=mock_app_info), \
         patch("atbclone.cli.cmd_update.RecipeLoader.match", return_value=mock_hard_recipe), \
         patch("atbclone.cli.cmd_update.HardCloneEngine.execute", side_effect=CloneError("Re-clone failed")), \
         patch("atbclone.cli.cmd_update.StateManager.add") as mock_state_add:

        result = runner.invoke(cli, ["update", "WeChat2"])
        assert result.exit_code == 1
        assert "Error:" in result.output
        assert "Re-clone failed" in result.output
        mock_state_add.assert_not_called()


def test_update_admin_elevation(
    mock_record_admin_dir: CloneRecord,
    mock_app_info: AppInfo,
    mock_hard_recipe: Recipe,
):
    runner = CliRunner()
    with patch("atbclone.cli.cmd_update.StateManager.get", return_value=mock_record_admin_dir), \
         patch("atbclone.cli.cmd_update.Runner.run") as mock_runner, \
         patch("atbclone.cli.cmd_update.AppInspector.inspect", return_value=mock_app_info), \
         patch("atbclone.cli.cmd_update.RecipeLoader.match", return_value=mock_hard_recipe), \
         patch("atbclone.cli.cmd_update.HardCloneEngine.execute") as mock_hard_exec, \
         patch("atbclone.cli.cmd_update.StateManager.add"):

        result = runner.invoke(cli, ["update", "WeChat2"])
        assert result.exit_code == 0

        mock_runner.assert_called_once()
        _, needs_admin = mock_runner.call_args[0]
        assert needs_admin is True

        mock_hard_exec.assert_called_once()
        _, engine_needs_admin = mock_hard_exec.call_args[0]
        assert engine_needs_admin is True


def test_update_fallback_bundle_id_when_empty(
    mock_record_user_dir: CloneRecord,
    mock_app_info: AppInfo,
    mock_hard_recipe: Recipe,
):
    mock_record_user_dir.new_bundle_id = ""
    runner = CliRunner()
    with patch("atbclone.cli.cmd_update.StateManager.get", return_value=mock_record_user_dir), \
         patch("atbclone.cli.cmd_update.Runner.run"), \
         patch("atbclone.cli.cmd_update.AppInspector.inspect", return_value=mock_app_info), \
         patch("atbclone.cli.cmd_update.RecipeLoader.match", return_value=mock_hard_recipe), \
         patch("atbclone.cli.cmd_update.HardCloneEngine.execute") as mock_hard_exec, \
         patch("atbclone.cli.cmd_update.StateManager.add"):

        result = runner.invoke(cli, ["update", "WeChat2"])
        assert result.exit_code == 0

        task, _ = mock_hard_exec.call_args[0]
        assert task.new_bundle_id == "com.tencent.xinWeChat.atbclone.2"


def test_update_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["update", "--help"])
    assert result.exit_code == 0
    assert "CLONE_NAME" in result.output
