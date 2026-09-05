"""Tests for CloneInspector utility."""

from pathlib import Path
import pytest

from atbclone.core.clone_inspector import CloneInspector, InjectedDetails
from atbclone.core.state import CloneRecord


def test_parse_wrapper_script_basic():
    script = """#!/bin/bash
REAL_USER_HOME="$HOME"
export LANG="zh_CN.UTF-8"
export LC_ALL="zh_CN.UTF-8"
export HTTP_PROXY="http://127.0.0.1:7890"
exec "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --user-data-dir="/Users/test/Data" --lang=zh-CN "$@"
"""
    details = CloneInspector.parse_wrapper_script(script)
    assert details.env_vars.get("LANG") == "zh_CN.UTF-8"
    assert details.env_vars.get("LC_ALL") == "zh_CN.UTF-8"
    assert details.env_vars.get("HTTP_PROXY") == "http://127.0.0.1:7890"
    assert '--user-data-dir=/Users/test/Data' in details.launch_args or '--user-data-dir="/Users/test/Data"' in details.launch_args
    assert '--lang=zh-CN' in details.launch_args
    assert "Google Chrome" in details.exec_command
    assert details.source_type == "wrapper_script"


def test_parse_wrapper_script_complex_cocoa():
    script = """#!/bin/bash
REAL_USER_HOME="$HOME"
export HOME="/Users/test/Data"
export LANG="zh_CN.UTF-8"
exec "$(dirname "$0")/WeChat.bin" -AppleLanguages '("zh-Hans-CN", "zh-Hans", "en")' -AppleLocale zh_CN "$@"
"""
    details = CloneInspector.parse_wrapper_script(script)
    assert details.env_vars.get("HOME") == "/Users/test/Data"
    assert details.env_vars.get("LANG") == "zh_CN.UTF-8"
    assert "-AppleLanguages" in details.launch_args
    assert '-AppleLocale' in details.launch_args
    assert details.source_type == "wrapper_script"


def test_inspect_fallback_when_file_not_found(tmp_path):
    record = CloneRecord(
        clone_name="TestApp_Clone",
        source_app="TestApp",
        source_path="/Applications/TestApp.app",
        bundle_id="com.google.Chrome",
        strategy="soft_clone",
        dest_path=str(tmp_path / "NonExistent.app"),
        data_dir=str(tmp_path / "Data"),
        created_at="2026-08-24T00:00:00Z",
        language="zh-Hans",
        proxy_enabled=True,
        proxy_summary="http://127.0.0.1:8080",
    )
    details = CloneInspector.inspect(record)
    assert details.source_type == "recipe_fallback"
    assert any("user-data-dir" in arg for arg in details.launch_args) or any("lang" in arg for arg in details.launch_args)
    assert details.env_vars.get("HTTP_PROXY") == "http://127.0.0.1:8080"


def test_inspect_detects_dylib_strategy(tmp_path):
    app_path = tmp_path / "DylibApp.app"
    frameworks_dir = app_path / "Contents" / "Frameworks"
    frameworks_dir.mkdir(parents=True)
    (frameworks_dir / "libatbclone_env.dylib").write_bytes(b"\x00")

    record = CloneRecord(
        clone_name="DylibClone",
        source_app="DylibApp",
        source_path="/Applications/DylibApp.app",
        bundle_id="com.example.dylib",
        strategy="hard_clone",
        dest_path=str(app_path),
        data_dir=str(tmp_path / "Data"),
        created_at="2026-08-24T00:00:00Z",
    )
    details = CloneInspector.inspect(record)
    assert details.injection_strategy == "dylib"


def test_inspect_detects_launcher_strategy(tmp_path):
    app_path = tmp_path / "LauncherApp.app"
    macos_dir = app_path / "Contents" / "MacOS"
    macos_dir.mkdir(parents=True)
    (macos_dir / "App.bin").write_bytes(b"\x00")

    record = CloneRecord(
        clone_name="LauncherClone",
        source_app="LauncherApp",
        source_path="/Applications/LauncherApp.app",
        bundle_id="com.example.launcher",
        strategy="hard_clone",
        dest_path=str(app_path),
        data_dir=str(tmp_path / "Data"),
        created_at="2026-08-24T00:00:00Z",
    )
    details = CloneInspector.inspect(record)
    assert details.injection_strategy == "launcher"
