"""Tests for the executor runner and exception classes."""

import subprocess
from unittest.mock import patch
import pytest

from atbclone.executor import CloneError, Runner


def test_runner_run_direct_success():
    out = Runner.run("echo 'hello world'", needs_admin=False)
    assert "hello world" in out


def test_runner_run_direct_failure():
    with pytest.raises(CloneError) as exc_info:
        Runner.run("exit 42", needs_admin=False)
    assert "exit 42" in str(exc_info.value) or "Command failed" in str(exc_info.value)


def test_runner_run_default_needs_admin_false():
    out = Runner.run("echo 'default test'")
    assert "default test" in out


def test_runner_run_as_admin_dispatch():
    with patch.object(Runner, "_run_as_admin", return_value="admin ok") as mock_admin:
        out = Runner.run("echo test", needs_admin=True)
        assert out == "admin ok"
        mock_admin.assert_called_once_with("echo test")


def test_runner_run_as_admin_escapes_and_calls_osascript():
    with patch("subprocess.check_output", return_value="mocked osascript output") as mock_subp:
        out = Runner._run_as_admin('echo "hello \\ world"')
        assert out == "mocked osascript output"
        mock_subp.assert_called_once()
        args, kwargs = mock_subp.call_args
        cmd = args[0]
        assert cmd[0] == "/usr/bin/osascript"
        assert cmd[1] == "-e"
        assert 'do shell script "echo \\"hello \\\\ world\\"" with administrator privileges' == cmd[2]


def test_runner_run_as_admin_failure_raises_clone_error():
    with patch("subprocess.check_output", side_effect=subprocess.CalledProcessError(1, "osascript", output="User canceled.")):
        with pytest.raises(CloneError) as exc_info:
            Runner._run_as_admin("some_command")
        assert "Admin command failed" in str(exc_info.value)
        assert "User canceled" in str(exc_info.value)
