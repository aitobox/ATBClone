"""Tests for ReleaseNotesWindow component."""

import pytest
import toga

from atbclone.core.i18n import set_language
from atbclone.gui.windows.release_notes import ReleaseNotesWindow, LANGUAGE_DISPLAY_NAMES


def test_release_notes_window_init(toga_app):
    set_language("zh")
    window = ReleaseNotesWindow()
    assert "ATBClone" in window.title
    assert window.size == (780, 580)
    assert window.selection_lang is not None
    assert window.text_content is not None
    # Verify content loaded
    assert len(window.text_content.value) > 50
    assert "ATBClone" in window.text_content.value
    set_language(None)


def test_release_notes_window_lang_switch(toga_app):
    window = ReleaseNotesWindow(initial_lang="en")
    assert window.current_lang == "en"
    assert "Release Notes" in window.text_content.value

    # Switch to ja
    window.switch_language("ja")
    assert window.current_lang == "ja"
    assert len(window.text_content.value) > 50


def test_release_notes_window_missing_file_handling(toga_app):
    window = ReleaseNotesWindow(initial_lang="en")
    # Simulate missing path
    window.current_path = None
    window.load_release_notes("nonexistent_lang_code")
    # Fallback loads default or error message
    assert len(window.text_content.value) > 0


def test_release_notes_window_dropdown_change(toga_app):
    window = ReleaseNotesWindow(initial_lang="en")
    # Simulate changing dropdown selection
    window.selection_lang.value = "日本語 (Japanese)"
    window._on_lang_changed(window.selection_lang)
    assert window.current_lang == "ja"
