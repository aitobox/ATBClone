"""Unit tests for the `remove` CLI command."""

from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
from click.testing import CliRunner

from atbclone.cli.main import cli
from atbclone.core.state import CloneRecord
from atbclone.executor.runner import CloneError


@pytest.fixture
def mock_record_user_dir() -> CloneRecord:
    return CloneRecord(
        clone_name="WeChat2",
        source_app="WeChat",
        source_path="/Applications/WeChat.app",
        bundle_id="com.tencent.xinWeChat",
        strategy="hard_clone",
        dest_path=str(Path.home() / "Applications" / "WeChat2.app"),
        data_dir=str(Path.home() / ".atbclone" / "Data" / "WeChat2"),
        created_at="2026-08-18T20:00:00",
        proxy_enabled=False,
        proxy_summary="",
    )


@pytest.fixture
def mock_record_admin_dir() -> CloneRecord:
    return CloneRecord(
        clone_name="WeChat2",
        source_app="WeChat",
        source_path="/Applications/WeChat.app",
        bundle_id="com.tencent.xinWeChat",
        strategy="hard_clone",
        dest_path="/Applications/WeChat2.app",
        data_dir=str(Path.home() / ".atbclone" / "Data" / "WeChat2"),
        created_at="2026-08-18T20:00:00",
        proxy_enabled=False,
        proxy_summary="",
    )


def test_remove_not_found():
    runner = CliRunner()
    with patch("atbclone.cli.cmd_remove.StateManager.get", return_value=None):
        result = runner.invoke(cli, ["remove", "WeChat2"])
        assert result.exit_code == 1
        assert "Error:" in result.output
        assert "Clone 'WeChat2' not found." in result.output


def test_remove_success(mock_record_user_dir: CloneRecord):
    runner = CliRunner()
    with patch("atbclone.cli.cmd_remove.StateManager.get", return_value=mock_record_user_dir), \
         patch("atbclone.cli.cmd_remove.Runner.run") as mock_runner, \
         patch("atbclone.cli.cmd_remove.StateManager.remove") as mock_remove:

        result = runner.invoke(cli, ["remove", "WeChat2"])
        assert result.exit_code == 0
        assert "Success! Removed clone 'WeChat2'" in result.output

        mock_runner.assert_called_once()
        script, needs_admin = mock_runner.call_args[0]
        assert needs_admin is False
        assert f"rm -rf {mock_record_user_dir.dest_path}" in script
        assert mock_record_user_dir.data_dir not in script

        mock_remove.assert_called_once_with("WeChat2")


def test_remove_with_data(mock_record_user_dir: CloneRecord):
    runner = CliRunner()
    with patch("atbclone.cli.cmd_remove.StateManager.get", return_value=mock_record_user_dir), \
         patch("atbclone.cli.cmd_remove.Runner.run") as mock_runner, \
         patch("atbclone.cli.cmd_remove.StateManager.remove") as mock_remove:

        result = runner.invoke(cli, ["remove", "WeChat2", "--with-data"], input="y\n")
        assert result.exit_code == 0
        assert f"Also delete data directory {mock_record_user_dir.data_dir}?" in result.output
        assert "Success! Removed clone 'WeChat2'" in result.output

        mock_runner.assert_called_once()
        script, needs_admin = mock_runner.call_args[0]
        assert needs_admin is False
        assert f"rm -rf {mock_record_user_dir.dest_path}" in script
        assert f"rm -rf {mock_record_user_dir.data_dir}" in script

        mock_remove.assert_called_once_with("WeChat2")


def test_remove_with_data_abort(mock_record_user_dir: CloneRecord):
    runner = CliRunner()
    with patch("atbclone.cli.cmd_remove.StateManager.get", return_value=mock_record_user_dir), \
         patch("atbclone.cli.cmd_remove.Runner.run") as mock_runner, \
         patch("atbclone.cli.cmd_remove.StateManager.remove") as mock_remove:

        result = runner.invoke(cli, ["remove", "WeChat2", "--with-data"], input="n\n")
        assert result.exit_code != 0
        assert "Aborted" in result.output or result.exit_code == 1

        mock_runner.assert_not_called()
        mock_remove.assert_not_called()


def test_remove_runner_error(mock_record_user_dir: CloneRecord):
    runner = CliRunner()
    with patch("atbclone.cli.cmd_remove.StateManager.get", return_value=mock_record_user_dir), \
         patch("atbclone.cli.cmd_remove.Runner.run", side_effect=CloneError("Permission denied")), \
         patch("atbclone.cli.cmd_remove.StateManager.remove") as mock_remove:

        result = runner.invoke(cli, ["remove", "WeChat2"])
        assert result.exit_code == 1
        assert "Error:" in result.output
        assert "Permission denied" in result.output

        mock_remove.assert_not_called()


def test_remove_admin_elevation(mock_record_admin_dir: CloneRecord):
    runner = CliRunner()
    with patch("atbclone.cli.cmd_remove.StateManager.get", return_value=mock_record_admin_dir), \
         patch("atbclone.cli.cmd_remove.Runner.run") as mock_runner, \
         patch("atbclone.cli.cmd_remove.StateManager.remove") as mock_remove:

        result = runner.invoke(cli, ["remove", "WeChat2"])
        assert result.exit_code == 0
        assert "Success! Removed clone 'WeChat2'" in result.output

        mock_runner.assert_called_once()
        script, needs_admin = mock_runner.call_args[0]
        assert needs_admin is True
        assert f"rm -rf {mock_record_admin_dir.dest_path}" in script

        mock_remove.assert_called_once_with("WeChat2")


def test_remove_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["remove", "--help"])
    assert result.exit_code == 0
    assert "CLONE_NAME" in result.output
    assert "--with-data" in result.output
