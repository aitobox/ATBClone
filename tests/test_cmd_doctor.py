"""Unit tests for the `doctor` CLI command."""

import subprocess
from unittest.mock import patch
from click.testing import CliRunner

from atbclone.cli.main import cli


def test_doctor_all_passed():
    runner = CliRunner()

    def mock_check_output(cmd, *args, **kwargs):
        if "codesign" in cmd:
            return "/usr/bin/codesign\n"
        if "xcode-select" in cmd:
            return "/Applications/Xcode.app/Contents/Developer\n"
        if "PlistBuddy" in cmd:
            return "/usr/libexec/PlistBuddy\n"
        return ""

    with patch("subprocess.check_output", side_effect=mock_check_output) as mock_run:
        result = runner.invoke(cli, ["doctor"])
        assert result.exit_code == 0
        assert "Running environment checks:" in result.output
        assert "codesign" in result.output
        assert "/usr/bin/codesign" in result.output
        assert "xcode-select" in result.output
        assert "/Applications/Xcode.app/Contents/Developer" in result.output
        assert "PlistBuddy" in result.output
        assert "/usr/libexec/PlistBuddy" in result.output
        assert "✓" in result.output
        assert "✗" not in result.output
        assert mock_run.call_count == 3


def test_doctor_one_failed():
    runner = CliRunner()

    def mock_check_output(cmd, *args, **kwargs):
        if "codesign" in cmd:
            return "/usr/bin/codesign\n"
        if "xcode-select" in cmd:
            raise subprocess.CalledProcessError(1, cmd)
        if "PlistBuddy" in cmd:
            return "/usr/libexec/PlistBuddy\n"
        return ""

    with patch("subprocess.check_output", side_effect=mock_check_output) as mock_run:
        result = runner.invoke(cli, ["doctor"])
        assert result.exit_code == 1
        assert "Running environment checks:" in result.output
        assert "codesign" in result.output
        assert "✓ codesign" in result.output or "codesign" in result.output
        assert "✗ xcode-select" in result.output or "xcode-select" in result.output
        assert "Missing! Run 'xcode-select --install'" in result.output
        assert mock_run.call_count == 3


def test_doctor_all_failed():
    runner = CliRunner()

    with patch(
        "subprocess.check_output",
        side_effect=subprocess.CalledProcessError(1, "cmd"),
    ) as mock_run:
        result = runner.invoke(cli, ["doctor"])
        assert result.exit_code == 1
        assert "Running environment checks:" in result.output
        assert "✗ codesign" in result.output or "codesign" in result.output
        assert "✗ xcode-select" in result.output or "xcode-select" in result.output
        assert "✗ PlistBuddy" in result.output or "PlistBuddy" in result.output
        assert result.output.count("Missing! Run 'xcode-select --install'") == 3
        assert mock_run.call_count == 3


def test_doctor_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["doctor", "--help"])
    assert result.exit_code == 0
    assert "doctor" in result.output.lower() or "环境检测" in result.output
