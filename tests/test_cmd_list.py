"""Unit tests for the `list` CLI command."""

from unittest.mock import patch
from click.testing import CliRunner

from atbclone.cli.main import cli
from atbclone.core.state import CloneRecord


def test_list_empty():
    runner = CliRunner(env={"COLUMNS": "120"})
    with patch("atbclone.cli.cmd_list.StateManager.load", return_value=[]):
        result = runner.invoke(cli, ["list"])
        assert result.exit_code == 0
        assert "No clones found." in result.output


def test_list_one_record():
    runner = CliRunner(env={"COLUMNS": "120"})
    mock_records = [
        CloneRecord(
            clone_name="WeChat2",
            source_app="WeChat",
            source_path="/Applications/WeChat.app",
            bundle_id="com.tencent.xinWeChat",
            strategy="hard_clone",
            dest_path="/Users/test/Applications/WeChat2.app",
            data_dir="/Users/test/.atbclone/Data/WeChat2",
            created_at="2026-08-18T20:00:00",
            proxy_enabled=False,
            proxy_summary="",
        )
    ]
    with patch("atbclone.cli.cmd_list.StateManager.load", return_value=mock_records):
        result = runner.invoke(cli, ["list"])
        assert result.exit_code == 0
        assert "WeChat2" in result.output
        assert "WeChat" in result.output
        assert "com.tencent.xinWeChat" in result.output
        assert "hard_clone" in result.output
        assert "2026-08-18" in result.output
        assert "未开启" in result.output


def test_list_multiple_records():
    runner = CliRunner(env={"COLUMNS": "120"})
    mock_records = [
        CloneRecord(
            clone_name="WeChat2",
            source_app="WeChat",
            source_path="/Applications/WeChat.app",
            bundle_id="com.tencent.xinWeChat",
            strategy="hard_clone",
            dest_path="/Users/test/Applications/WeChat2.app",
            data_dir="/Users/test/.atbclone/Data/WeChat2",
            created_at="2026-08-18T20:00:00",
            proxy_enabled=False,
            proxy_summary="",
        ),
        CloneRecord(
            clone_name="Chrome2",
            source_app="Google Chrome",
            source_path="/Applications/Google Chrome.app",
            bundle_id="com.google.Chrome",
            strategy="soft_clone",
            dest_path="/Users/test/Applications/Chrome2.app",
            data_dir="/Users/test/.atbclone/Data/Chrome2",
            created_at="2026-08-18T21:00:00",
            proxy_enabled=True,
            proxy_summary="http://127.0.0.1:7890",
        ),
    ]
    with patch("atbclone.cli.cmd_list.StateManager.load", return_value=mock_records):
        result = runner.invoke(cli, ["list"])
        assert result.exit_code == 0
        assert "WeChat2" in result.output
        assert "Chrome2" in result.output
        assert "com.google.Chrome" in result.output
        assert "soft_clone" in result.output
        assert "http://127.0.0.1:7890" in result.output


def test_list_proxy_shown():
    runner = CliRunner(env={"COLUMNS": "120"})
    mock_records = [
        CloneRecord(
            clone_name="WeChat3",
            source_app="WeChat",
            source_path="/Applications/WeChat.app",
            bundle_id="com.tencent.xinWeChat",
            strategy="hard_clone",
            dest_path="/Users/test/Applications/WeChat3.app",
            data_dir="/Users/test/.atbclone/Data/WeChat3",
            created_at="2026-08-18T22:00:00",
            proxy_enabled=True,
            proxy_summary="socks5://127.0.0.1:1080",
        )
    ]
    with patch("atbclone.cli.cmd_list.StateManager.load", return_value=mock_records):
        result = runner.invoke(cli, ["list"])
        assert result.exit_code == 0
        assert "WeChat3" in result.output
        assert "socks5://127.0.0.1:1080" in result.output
        assert "未开启" not in result.output


def test_list_no_proxy():
    runner = CliRunner(env={"COLUMNS": "120"})
    mock_records = [
        CloneRecord(
            clone_name="WeChat2",
            source_app="WeChat",
            source_path="/Applications/WeChat.app",
            bundle_id="com.tencent.xinWeChat",
            strategy="hard_clone",
            dest_path="/Users/test/Applications/WeChat2.app",
            data_dir="/Users/test/.atbclone/Data/WeChat2",
            created_at="2026-08-18T20:00:00",
            proxy_enabled=False,
            proxy_summary="",
        )
    ]
    with patch("atbclone.cli.cmd_list.StateManager.load", return_value=mock_records):
        result = runner.invoke(cli, ["list"])
        assert result.exit_code == 0
        assert "未开启" in result.output


def test_list_help():
    runner = CliRunner(env={"COLUMNS": "120"})
    result = runner.invoke(cli, ["list", "--help"])
    assert result.exit_code == 0
    assert "list" in result.output.lower() or "查看已克隆的应用列表" in result.output
