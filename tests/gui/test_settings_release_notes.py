"""Tests for SettingsView ReleaseNotes button integration."""

import pytest
import toga

from atbclone.core.i18n import set_language, t
from atbclone.gui.views.settings_view import SettingsView
from atbclone.gui.windows.release_notes import ReleaseNotesWindow


def test_settings_view_release_notes_button_exists(toga_app):
    set_language("zh")
    view = SettingsView()
    assert hasattr(view, "btn_release_notes")
    assert view.btn_release_notes.text == t("settings_btn_release_notes")
    assert "更新日志" in view.btn_release_notes.text
    set_language(None)


def test_settings_view_open_release_notes_action(toga_app, monkeypatch):
    view = SettingsView()
    shown = []

    def mock_show(self):
        shown.append(self)

    monkeypatch.setattr(ReleaseNotesWindow, "show", mock_show)

    # Call handler
    view.on_open_release_notes(view.btn_release_notes)
    assert len(shown) == 1
    assert isinstance(shown[0], ReleaseNotesWindow)
    assert view.release_notes_window is shown[0]
