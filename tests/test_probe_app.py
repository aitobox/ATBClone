"""Unit tests for scripts/probe_app.py (App Prober and Recipe Generator)."""

from pathlib import Path
from unittest.mock import patch

from atbclone.core.models import AppInfo
import scripts.probe_app as pa


def test_analyze_app_native_sandboxed(tmp_path):
    app_dir = tmp_path / "SandboxedNative.app"
    app_dir.mkdir()

    mock_info = AppInfo(
        path=app_dir,
        bundle_id="com.example.native",
        app_name="SandboxedNative",
        executable="/Contents/MacOS/SandboxedNative",
        has_sandbox=True,
    )

    with patch("scripts.probe_app.AppInspector.inspect", return_value=mock_info),          patch("scripts.probe_app.inspect_entitlements", return_value={"com.apple.security.app-sandbox": True}),          patch("scripts.probe_app.detect_frameworks", return_value=[]):
        analysis = pa.analyze_app(app_dir)
        recipe = analysis["recipe"]

        assert recipe["strategy"] == "hard_clone"
        assert recipe["strip_sandbox"] is True
        assert recipe["environment_injection"]["HOME"] == "{{ATB_DATA_DIR}}/Home"
        assert recipe["environment_injection"]["TMPDIR"] == "{{ATB_DATA_DIR}}/Tmp"
        assert "launch_args" not in recipe


def test_analyze_app_chromium(tmp_path):
    app_dir = tmp_path / "MyChromium.app"
    app_dir.mkdir()

    mock_info = AppInfo(
        path=app_dir,
        bundle_id="com.google.chrome.canary",
        app_name="MyChromium",
        executable="/Contents/MacOS/MyChromium",
        has_sandbox=False,
    )

    with patch("scripts.probe_app.AppInspector.inspect", return_value=mock_info),          patch("scripts.probe_app.inspect_entitlements", return_value={}),          patch("scripts.probe_app.detect_frameworks", return_value=["Chromium Embedded Framework.framework"]):
        analysis = pa.analyze_app(app_dir)
        recipe = analysis["recipe"]

        assert recipe["strategy"] == "soft_clone"
        assert recipe["strip_sandbox"] is False
        assert recipe["launch_args"] == ["--user-data-dir={{ATB_DATA_DIR}}"]
        assert "environment_injection" not in recipe


def test_analyze_app_electron_framework(tmp_path):
    app_dir = tmp_path / "MyElectron.app"
    app_dir.mkdir()

    mock_info = AppInfo(
        path=app_dir,
        bundle_id="com.custom.editor",
        app_name="MyElectron",
        executable="/Contents/MacOS/MyElectron",
        has_sandbox=False,
    )

    with patch("scripts.probe_app.AppInspector.inspect", return_value=mock_info),          patch("scripts.probe_app.inspect_entitlements", return_value={}),          patch("scripts.probe_app.detect_frameworks", return_value=["Electron Framework.framework"]):
        analysis = pa.analyze_app(app_dir)
        recipe = analysis["recipe"]

        assert recipe["strategy"] == "soft_clone"
        assert recipe["launch_args"] == ["--user-data-dir={{ATB_DATA_DIR}}"]


def test_analyze_app_firefox(tmp_path):
    app_dir = tmp_path / "Firefox.app"
    app_dir.mkdir()

    mock_info = AppInfo(
        path=app_dir,
        bundle_id="org.mozilla.firefox",
        app_name="Firefox",
        executable="/Contents/MacOS/firefox",
        has_sandbox=False,
    )

    with patch("scripts.probe_app.AppInspector.inspect", return_value=mock_info),          patch("scripts.probe_app.inspect_entitlements", return_value={}),          patch("scripts.probe_app.detect_frameworks", return_value=[]):
        analysis = pa.analyze_app(app_dir)
        recipe = analysis["recipe"]

        assert recipe["strategy"] == "soft_clone"
        assert recipe["launch_args"] == ["-profile", "{{ATB_DATA_DIR}}"]


def test_main_cli_output_file(tmp_path):
    app_dir = tmp_path / "TestApp.app"
    app_dir.mkdir()
    out_yaml = tmp_path / "custom_output.yaml"

    mock_info = AppInfo(
        path=app_dir,
        bundle_id="com.example.test",
        app_name="TestApp",
        executable="/Contents/MacOS/TestApp",
        has_sandbox=False,
    )

    with patch("scripts.probe_app.AppInspector.inspect", return_value=mock_info),          patch("scripts.probe_app.inspect_entitlements", return_value={}),          patch("scripts.probe_app.detect_frameworks", return_value=[]):
        ret = pa.main([str(app_dir), "--output", str(out_yaml)])
        assert ret == 0
        assert out_yaml.exists()
        assert "bundle_id: com.example.test" in out_yaml.read_text(encoding="utf-8")
