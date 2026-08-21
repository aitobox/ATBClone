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


def test_release_notes_window_guards_uninitialized(toga_app):
    window = ReleaseNotesWindow(initial_lang="en")
    window.text_content = None
    # Calling callbacks when text_content is None should not raise AttributeError
    window._on_lang_changed(window.selection_lang)
    window.load_release_notes("zh")


def test_release_notes_window_external_editor(toga_app, monkeypatch):
    window = ReleaseNotesWindow(initial_lang="en")
    called_cmds = []
    monkeypatch.setattr("subprocess.Popen", lambda cmd: called_cmds.append(cmd))
    window.on_open_in_external_editor(window.btn_open_external)
    assert len(called_cmds) == 1
    assert called_cmds[0][0] == "open"

