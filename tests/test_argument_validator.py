"""Unit tests for LaunchArgumentValidator."""

from pathlib import Path
import pytest

from atbclone.core.argument_prober import LaunchArgumentValidator


def test_validator_framework_whitelist_chromium(tmp_path: Path):
    dummy_bin = tmp_path / "chrome_bin"
    dummy_bin.write_bytes(b"empty")
    args = ["--user-data-dir=/tmp/data", "--lang=zh-CN", "--no-sandbox"]
    valid, pruned = LaunchArgumentValidator.validate_and_filter(dummy_bin, args, app_type="chromium")
    assert valid == args
    assert pruned == []


def test_validator_framework_whitelist_electron(tmp_path: Path):
    dummy_bin = tmp_path / "electron_bin"
    dummy_bin.write_bytes(b"empty")
    args = ["--user-data-dir=/tmp/data", "--lang=en-US"]
    valid, pruned = LaunchArgumentValidator.validate_and_filter(dummy_bin, args, app_type="electron")
    assert valid == args
    assert pruned == []


def test_validator_framework_whitelist_firefox(tmp_path: Path):
    dummy_bin = tmp_path / "firefox_bin"
    dummy_bin.write_bytes(b"empty")
    args = ["-profile", "/tmp/data", "-no-remote"]
    valid, pruned = LaunchArgumentValidator.validate_and_filter(dummy_bin, args, app_type="firefox")
    assert valid == args
    assert pruned == []


def test_validator_cocoa_apple_args(tmp_path: Path):
    dummy_bin = tmp_path / "cocoa_bin"
    dummy_bin.write_bytes(b"empty")
    args = ["-AppleLanguages", '("zh-Hans")', "-AppleLocale", "zh_CN"]
    valid, pruned = LaunchArgumentValidator.validate_and_filter(dummy_bin, args, app_type="cocoa")
    assert valid == args
    assert pruned == []


def test_validator_prune_unsupported_args(tmp_path: Path):
    dummy_bin = tmp_path / "native_bin"
    dummy_bin.write_bytes(b"MachO_HEADER\x00--supported-flag\x00")
    args = ["--supported-flag=123", "--unsupported-flag=456", "--user-data-dir=/tmp/data"]
    valid, pruned = LaunchArgumentValidator.validate_and_filter(dummy_bin, args, app_type="cocoa")
    assert "--supported-flag=123" in valid
    assert "--unsupported-flag=456" in pruned
    assert "--user-data-dir=/tmp/data" in pruned


def test_validator_prune_space_separated_unsupported_args(tmp_path: Path):
    dummy_bin = tmp_path / "native_bin"
    dummy_bin.write_bytes(b"MachO_HEADER\x00CocoaApp\x00")
    args = ["-profile", "/tmp/data", "--unsupported"]
    valid, pruned = LaunchArgumentValidator.validate_and_filter(dummy_bin, args, app_type="generic")
    assert valid == []
    assert "-profile" in pruned
    assert "--unsupported" in pruned


def test_validator_empty_args(tmp_path: Path):
    dummy_bin = tmp_path / "native_bin"
    dummy_bin.write_bytes(b"MachO_HEADER")
    valid, pruned = LaunchArgumentValidator.validate_and_filter(dummy_bin, [], app_type="generic")
    assert valid == []
    assert pruned == []


def test_validator_with_app_bundle_dir(tmp_path: Path):
    app_dir = tmp_path / "CustomApp.app"
    macos_dir = app_dir / "Contents" / "MacOS"
    macos_dir.mkdir(parents=True)
    exe = macos_dir / "CustomApp"
    exe.write_bytes(b"MachO_HEADER\x00--my-custom-flag\x00")
    plist = app_dir / "Contents" / "Info.plist"
    plist.write_bytes(b"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key><string>CustomApp</string>
</dict>
</plist>""")

    args = ["--my-custom-flag=1", "--bad-flag=2"]
    valid, pruned = LaunchArgumentValidator.validate_and_filter(app_dir, args, app_type="generic")
    assert valid == ["--my-custom-flag=1"]
    assert pruned == ["--bad-flag=2"]

