"""Tests for build_cli.sh script integrity and syntax."""

import os
import subprocess
from pathlib import Path


def test_build_script_exists_and_executable():
    root = Path(__file__).parent.parent
    script = root / "scripts" / "build_cli.sh"
    assert script.exists(), "scripts/build_cli.sh does not exist"
    assert os.access(script, os.X_OK), "scripts/build_cli.sh is not executable"


def test_build_script_bash_syntax():
    root = Path(__file__).parent.parent
    script = root / "scripts" / "build_cli.sh"
    result = subprocess.run(
        ["bash", "-n", str(script)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Bash syntax error: {result.stderr}"


def test_build_script_contains_required_flags():
    root = Path(__file__).parent.parent
    script = root / "scripts" / "build_cli.sh"
    content = script.read_text(encoding="utf-8")
    assert "--onefile" in content
    assert "ATBCloneCli" in content
    assert "--include-package=atbclone" in content
    assert "--include-package-data=atbclone" in content
    assert "src/atbclone/cli/main.py" in content
