import plistlib
from pathlib import Path

import pytest

from atbclone.core.app_inspector import AppInspector
from atbclone.core.models import AppInfo


def test_app_info_model():
    path = Path("/Applications/Test.app")
    exec_path = path / "Contents" / "MacOS" / "Test"
    info = AppInfo(
        path=path,
        bundle_id="com.example.test",
        app_name="Test",
        executable=exec_path,
        has_sandbox=True,
    )
    assert info.path == path
    assert info.bundle_id == "com.example.test"
    assert info.app_name == "Test"
    assert info.executable == exec_path
    assert info.has_sandbox is True


def test_next_available_name_empty_dir(tmp_path: Path):
    name, num = AppInspector.next_available_name("WeChat", tmp_path)
    assert name == "WeChat2"
    assert num == 2


def test_next_available_name_with_existing(tmp_path: Path):
    (tmp_path / "WeChat2.app").mkdir()
    name, num = AppInspector.next_available_name("WeChat", tmp_path)
    assert name == "WeChat3"
    assert num == 3


def test_next_available_name_with_numbered_input(tmp_path: Path):
    (tmp_path / "WeChat2.app").mkdir()
    name, num = AppInspector.next_available_name("WeChat2", tmp_path)
    assert name == "WeChat3"
    assert num == 3


def test_next_available_name_with_high_numbered_input(tmp_path: Path):
    (tmp_path / "WeChat5.app").mkdir()
    name, num = AppInspector.next_available_name("WeChat5", tmp_path)
    assert name == "WeChat6"
    assert num == 6


def test_next_available_name_str_path(tmp_path: Path):
    (tmp_path / "App2.app").mkdir()
    (tmp_path / "App3.app").mkdir()
    name, num = AppInspector.next_available_name("App", str(tmp_path))
    assert name == "App4"
    assert num == 4


def test_inspect_not_found():
    with pytest.raises(FileNotFoundError):
        AppInspector.inspect("/non/existent/App.app")


def test_inspect_mock_app(tmp_path: Path, monkeypatch):
    app_dir = tmp_path / "MockApp.app"
    contents_dir = app_dir / "Contents"
    macos_dir = contents_dir / "MacOS"
    macos_dir.mkdir(parents=True)

    plist_data = {
        "CFBundleIdentifier": "com.mock.app",
        "CFBundleDisplayName": "Mock App Display",
        "CFBundleName": "MockApp",
        "CFBundleExecutable": "MockAppExec",
    }
    plist_path = contents_dir / "Info.plist"
    with open(plist_path, "wb") as f:
        plistlib.dump(plist_data, f)

    exec_file = macos_dir / "MockAppExec"
    exec_file.touch()

    # Mock _run_cmd for codesign
    def mock_run_cmd(cmd: list[str]) -> str:
        if "codesign" in cmd:
            return "[Key] com.apple.security.app-sandbox\n[Value]\n\t[Bool] true"
        return ""

    monkeypatch.setattr(AppInspector, "_run_cmd", staticmethod(mock_run_cmd))

    info = AppInspector.inspect(app_dir)
    assert info.path == app_dir
    assert info.bundle_id == "com.mock.app"
    assert info.app_name == "Mock App Display"
    assert info.executable == exec_file
    assert info.has_sandbox is True


def test_inspect_mock_app_without_sandbox(tmp_path: Path, monkeypatch):
    app_dir = tmp_path / "NoSandbox.app"
    contents_dir = app_dir / "Contents"
    macos_dir = contents_dir / "MacOS"
    macos_dir.mkdir(parents=True)

    plist_data = {
        "CFBundleIdentifier": "com.mock.nosandbox",
        "CFBundleName": "NoSandbox",
        "CFBundleExecutable": "NoSandbox",
    }
    plist_path = contents_dir / "Info.plist"
    with open(plist_path, "wb") as f:
        plistlib.dump(plist_data, f)

    def mock_run_cmd(cmd: list[str]) -> str:
        if "codesign" in cmd:
            return "[Key] com.apple.security.app-sandbox\n[Value]\n\t[Bool] false"
        return ""

    monkeypatch.setattr(AppInspector, "_run_cmd", staticmethod(mock_run_cmd))

    info = AppInspector.inspect(str(app_dir))
    assert info.bundle_id == "com.mock.nosandbox"
    assert info.has_sandbox is False


def test_inspect_fallback_stem_and_run_cmd(tmp_path: Path, monkeypatch):
    app_dir = tmp_path / "FallbackApp.app"
    app_dir.mkdir()

    monkeypatch.setattr(AppInspector, "_run_cmd", staticmethod(lambda cmd: ""))

    info = AppInspector.inspect(app_dir)
    assert info.bundle_id == ""
    assert info.app_name == "FallbackApp"
    assert info.executable == app_dir / "Contents" / "MacOS" / "FallbackApp"
    assert info.has_sandbox is False


def test_run_cmd_error_handling():
    result = AppInspector._run_cmd(["non_existent_binary_12345"])
    assert result == ""


def test_generate_bundle_id_default_num():
    bundle_id = AppInspector.generate_bundle_id("com.google.Chrome")
    assert bundle_id == "com.google.Chrome.atbclone.1"


def test_generate_bundle_id_custom_num():
    bundle_id = AppInspector.generate_bundle_id("com.tencent.xinWeChat", 2)
    assert bundle_id == "com.tencent.xinWeChat.atbclone.2"


def test_generate_bundle_id_large_num():
    bundle_id = AppInspector.generate_bundle_id("org.mozilla.firefox", 10)
    assert bundle_id == "org.mozilla.firefox.atbclone.10"

