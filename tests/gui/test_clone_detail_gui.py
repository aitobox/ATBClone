"""Tests for CloneDetailWindow component."""

import subprocess
from unittest.mock import MagicMock
import pytest
import toga

from atbclone.core.state import CloneRecord
from atbclone.gui.windows.clone_detail import CloneDetailWindow, copy_to_clipboard


def test_copy_to_clipboard(monkeypatch):
    class DummyPopen:
        def __init__(self, *args, **kwargs):
            self.returncode = 0

        def communicate(self, data):
            return (b"", b"")

    monkeypatch.setattr(subprocess, "Popen", lambda *args, **kwargs: DummyPopen())
    assert copy_to_clipboard("test command") is True


def test_clone_detail_window_initializes(tmp_path):
    record = CloneRecord(
        clone_name="TestApp_Clone",
        source_app="TestApp",
        source_path="/Applications/TestApp.app",
        bundle_id="com.google.Chrome",
        strategy="soft_clone",
        dest_path=str(tmp_path / "Clone.app"),
        data_dir=str(tmp_path / "Data"),
        created_at="2026-08-24T00:00:00Z",
        language="zh-Hans",
        proxy_enabled=True,
        proxy_summary="http://127.0.0.1:7890",
    )
    win = CloneDetailWindow(record)
    assert "TestApp_Clone" in win.title
    assert hasattr(win, "details")
    assert win.details is not None
    assert win.content is not None
    assert win.label_clone_name.text == "TestApp_Clone"
    assert "com.google.Chrome" in win.label_bundle_id.text


def test_clone_detail_copy_button_action(tmp_path, monkeypatch):
    class DummyPopen:
        def __init__(self, *args, **kwargs):
            self.returncode = 0

        def communicate(self, data):
            return (b"", b"")

    monkeypatch.setattr(subprocess, "Popen", lambda *args, **kwargs: DummyPopen())

    record = CloneRecord(
        clone_name="TestApp_Clone",
        source_app="TestApp",
        source_path="/Applications/TestApp.app",
        bundle_id="com.google.Chrome",
        strategy="soft_clone",
        dest_path=str(tmp_path / "Clone.app"),
        data_dir=str(tmp_path / "Data"),
        created_at="2026-08-24T00:00:00Z",
        language="zh-Hans",
        proxy_enabled=True,
        proxy_summary="http://127.0.0.1:7890",
    )
    win = CloneDetailWindow(record)
    assert win.btn_copy_cmd is not None
    win._on_copy_cmd(win.btn_copy_cmd)
    assert win.btn_copy_cmd.text != ""
