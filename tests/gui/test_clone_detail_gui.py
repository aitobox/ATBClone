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
    assert isinstance(win.text_content, toga.MultilineTextInput)
    assert win.text_content.readonly is True
    assert "com.google.Chrome" in win.text_content.value
    assert "TestApp" in win.text_content.value


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


def test_clone_detail_get_summary_text_and_copy_all(tmp_path, monkeypatch):
    copied = []

    def mock_copy(text):
        copied.append(text)
        return True

    monkeypatch.setattr("atbclone.gui.windows.clone_detail.copy_to_clipboard", mock_copy)

    record = CloneRecord(
        clone_name="TestApp_Clone",
        source_app="TestApp",
        source_path="/Applications/TestApp.app",
        bundle_id="com.google.Chrome",
        new_bundle_id="com.google.Chrome.clone1",
        strategy="hard_clone",
        dest_path=str(tmp_path / "Clone.app"),
        data_dir=str(tmp_path / "Data"),
        created_at="2026-08-24T00:00:00Z",
        language="zh-Hans",
        proxy_enabled=True,
        proxy_summary="http://127.0.0.1:7890",
    )
    win = CloneDetailWindow(record)
    summary = win.get_summary_text()
    assert "TestApp_Clone" in summary
    assert "TestApp" in summary
    assert "/Applications/TestApp.app" in summary
    assert "com.google.Chrome" in summary
    assert "com.google.Chrome.clone1" in summary
    assert str(tmp_path / "Data") in summary
    assert "http://127.0.0.1:7890" in summary

    assert win.btn_copy_all is not None
    win._on_copy_all(win.btn_copy_all)
    assert len(copied) == 1
    assert "TestApp_Clone" in copied[0]
    assert win.btn_copy_all.text != ""


def test_clone_detail_labels_are_selectable(tmp_path):
    import sys
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
    )
    win = CloneDetailWindow(record)
    for lbl in [
        win.label_clone_name,
        win.label_source_app,
        win.label_source_path,
        win.label_bundle_id,
        win.label_new_bundle_id,
        win.label_strategy,
        win.label_language,
        win.label_dest_path,
        win.label_data_dir,
        win.label_created_at,
        win.label_proxy,
    ]:
        assert lbl.selectable is True
        if sys.platform == "darwin":
            native = getattr(getattr(lbl, "_impl", None), "native", None)
            if native is not None:
                assert native.isSelectable() is True
