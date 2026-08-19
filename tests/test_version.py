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
    assert "synchronized at v0.1.0" in captured.out


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
    assert "All package targets and ReleaseNotes are synchronized" in captured.out
    assert "ReleaseNote.md" in captured.out
    assert "ReleaseNote_zh.md" in captured.out


def test_release_note_targets_count_and_languages():
    targets = mv.get_release_note_targets()
    assert len(targets) == 9
    filenames = [t.filename for t in targets]
    assert "ReleaseNote.md" in filenames
    assert "ReleaseNote_zh.md" in filenames
    assert "ReleaseNote_zh_TW.md" in filenames
    assert "ReleaseNote_ja.md" in filenames
    assert "ReleaseNote_ko.md" in filenames
    assert "ReleaseNote_de.md" in filenames
    assert "ReleaseNote_fr.md" in filenames
    assert "ReleaseNote_ru.md" in filenames
    assert "ReleaseNote_es.md" in filenames

    # All real docs/release/ files must exist and have latest version 0.3.0
    for t in targets:
        assert t.exists(), f"File {t.filename} should exist"
        assert t.read_latest_version() == "0.3.0"
        assert t.has_version("0.3.0")
        assert t.has_version("0.2.0")
        assert t.has_version("0.1.0")
        assert not t.has_version("9.9.9")


def test_check_release_notes_current():
    synced, missing = mv.check_release_notes("0.3.0")
    assert synced is True
    assert missing == []


def test_check_release_notes_missing():
    synced, missing = mv.check_release_notes("9.9.9")
    assert synced is False
    assert len(missing) == 9


def test_release_note_target_tmp_path(tmp_path):
    rel_dir = tmp_path / "docs" / "release"
    rel_dir.mkdir(parents=True)
    rn_en = rel_dir / "ReleaseNote.md"
    rn_en.write_text("# Release Notes\n\n## [v1.0.0] - 2026-08-20\n\n- Feature\n", encoding="utf-8")

    target = mv.ReleaseNoteTarget("ReleaseNote.md", "English", rn_en)
    assert target.exists() is True
    assert target.read_latest_version() == "1.0.0"
    assert target.has_version("1.0.0") is True
    assert target.has_version("2.0.0") is False

    target_missing = mv.ReleaseNoteTarget("NonExist.md", "English", rel_dir / "NonExist.md")
    assert target_missing.exists() is False
    assert target_missing.read_latest_version() is None
    assert target_missing.has_version("1.0.0") is False


def test_main_cli_check_notes(capsys):
    ret = mv.main(["--check-notes", "0.3.0"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "All 9 ReleaseNotes in docs/release/ contain entry for v0.3.0" in captured.out

    ret_fail = mv.main(["--check-notes", "9.9.9"])
    assert ret_fail == 1
    captured_fail = capsys.readouterr()
    assert "Missing v9.9.9 entry in 9 ReleaseNotes file(s)" in captured_fail.out

