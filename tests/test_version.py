"""Unit tests for semantic version management and scripts/manage_version.py."""

import re
import pytest
from pathlib import Path

from atbclone import __version__
import scripts.manage_version as mv


def test_atbclone_version_semver_format():
    """Verify package __version__ strictly follows x.y.z format."""
    assert re.match(r"^\d+\.\d+\.\d+$", __version__)
    assert __version__ == mv.get_current_version()


def test_parse_version_valid():
    v = mv.parse_version("0.1.0")
    assert v.major == 0
    assert v.minor == 1
    assert v.patch == 0
    assert str(v) == "0.1.0"

    v2 = mv.parse_version("12.34.56")
    assert v2.major == 12
    assert v2.minor == 34
    assert v2.patch == 56


@pytest.mark.parametrize("invalid_str", ["", "1", "1.0", "1.0.0.0", "v1.0.0", "1.0.a", "1.0.-1"])
def test_parse_version_invalid(invalid_str):
    with pytest.raises(ValueError, match="Invalid version format"):
        mv.parse_version(invalid_str)


def test_bump_version():
    v = mv.parse_version("0.1.0")
    assert str(mv.bump_version(v, "patch")) == "0.1.1"
    assert str(mv.bump_version(v, "minor")) == "0.2.0"
    assert str(mv.bump_version(v, "major")) == "1.0.0"

    v_complex = mv.parse_version("1.9.9")
    assert str(mv.bump_version(v_complex, "patch")) == "1.9.10"
    assert str(mv.bump_version(v_complex, "minor")) == "1.10.0"
    assert str(mv.bump_version(v_complex, "major")) == "2.0.0"


def test_bump_version_invalid_type():
    v = mv.parse_version("0.1.0")
    with pytest.raises(ValueError, match="Invalid bump type"):
        mv.bump_version(v, "build")


def test_version_target_read_and_update(tmp_path):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[project]\nname = "atbclone"\nversion = "0.1.0"\n', encoding="utf-8")

    init_file = tmp_path / "src" / "atbclone" / "__init__.py"
    init_file.parent.mkdir(parents=True)
    init_file.write_text('__version__ = "0.1.0"\n', encoding="utf-8")

    targets = mv.get_version_targets(root=tmp_path)
    assert len(targets) == 2

    assert targets[0].read_version() == "0.1.0"
    assert targets[1].read_version() == "0.1.0"

    # Test dry run
    assert mv.apply_version("0.2.0", root=tmp_path, dry_run=True) == 0
    assert targets[0].read_version() == "0.1.0"
    assert targets[1].read_version() == "0.1.0"

    # Test real update
    assert mv.apply_version("0.2.0", root=tmp_path, dry_run=False) == 0
    assert targets[0].read_version() == "0.2.0"
    assert targets[1].read_version() == "0.2.0"


def test_show_versions_synced(tmp_path, capsys):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[project]\nversion = "0.1.0"\n', encoding="utf-8")
    init_file = tmp_path / "src" / "atbclone" / "__init__.py"
    init_file.parent.mkdir(parents=True)
    init_file.write_text('__version__ = "0.1.0"\n', encoding="utf-8")

    code = mv.show_versions(root=tmp_path)
    captured = capsys.readouterr()
    assert code == 0
    assert "All targets are synchronized at v0.1.0" in captured.out


def test_show_versions_mismatch(tmp_path, capsys):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[project]\nversion = "0.1.0"\n', encoding="utf-8")
    init_file = tmp_path / "src" / "atbclone" / "__init__.py"
    init_file.parent.mkdir(parents=True)
    init_file.write_text('__version__ = "0.2.0"\n', encoding="utf-8")

    code = mv.show_versions(root=tmp_path)
    captured = capsys.readouterr()
    assert code == 1
    assert "Version mismatch or missing definitions detected!" in captured.out


def test_main_cli_show(capsys):
    ret = mv.main(["--show"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "All targets are synchronized" in captured.out
