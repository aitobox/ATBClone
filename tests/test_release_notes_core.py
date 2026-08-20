"""Tests for ReleaseNotes i18n keys and resource path resolution."""

from pathlib import Path
import pytest

from atbclone.core.i18n import SUPPORTED_LANGUAGES, t, set_language
from atbclone.core.resources import (
    LANGUAGE_RELEASE_NOTE_FILES,
    get_release_notes_dir,
    get_release_notes_path,
)


def test_release_notes_i18n_keys():
    keys = [
        "settings_btn_release_notes",
        "release_notes_window_title",
        "release_notes_lang_label",
        "release_notes_btn_open_external",
        "release_notes_btn_close",
        "release_notes_err_not_found",
    ]
    for lang in SUPPORTED_LANGUAGES:
        set_language(lang)
        for key in keys:
            val = t(key, path="test.md")
            assert val != key, f"Missing translation for {key} in language {lang}"
            assert len(val.strip()) > 0
    set_language(None)


def test_release_notes_path_resolution_all_languages():
    release_dir = get_release_notes_dir()
    assert release_dir.is_dir(), f"Release notes directory not found: {release_dir}"

    for lang, filename in LANGUAGE_RELEASE_NOTE_FILES.items():
        path = get_release_notes_path(lang)
        assert path is not None, f"Path was None for lang {lang}"
        assert path.exists(), f"Release note file does not exist: {path}"
        assert path.name == filename
        # Verify non-empty file
        content = path.read_text(encoding="utf-8")
        assert len(content) > 50


def test_release_notes_path_fallback():
    # Invalid lang should fallback to English or default
    path = get_release_notes_path("invalid_lang_code")
    assert path is not None
    assert path.exists()
    assert path.name == "ReleaseNote.md"
