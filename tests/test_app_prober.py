"""Unit tests for atbclone.core.app_prober."""

from pathlib import Path
from unittest.mock import patch

from atbclone.core.app_prober import AppProber
from atbclone.core.models import AppInfo


def test_app_prober_native_non_sandboxed(tmp_path: Path):
    app_dir = tmp_path / "MyNative.app"
    app_dir.mkdir()

    mock_info = AppInfo(
        path=app_dir,
        bundle_id="com.example.native",
        app_name="MyNative",
        executable=app_dir / "Contents" / "MacOS" / "MyNative",
        has_sandbox=False,
    )

    with patch.object(AppProber, "inspect_entitlements", return_value={}), \
         patch.object(AppProber, "detect_frameworks", return_value=[]):
        result = AppProber.analyze(app_dir, app_info=mock_info)
        assert result.strategy == "hard_clone"
        assert result.has_sandbox is False
        assert result.recipe.strip_sandbox is False
        assert result.recipe.environment_injection["HOME"] == "{{ATB_DATA_DIR}}/Home"
        assert result.recipe.environment_injection["TMPDIR"] == "{{ATB_DATA_DIR}}/Tmp"


def test_app_prober_native_sandboxed(tmp_path: Path):
    app_dir = tmp_path / "SandboxedApp.app"
    app_dir.mkdir()

    mock_info = AppInfo(
        path=app_dir,
        bundle_id="com.example.sandboxed",
        app_name="SandboxedApp",
        executable=app_dir / "Contents" / "MacOS" / "SandboxedApp",
        has_sandbox=True,
    )

    with patch.object(AppProber, "inspect_entitlements", return_value={"com.apple.security.app-sandbox": True}), \
         patch.object(AppProber, "detect_frameworks", return_value=[]):
        result = AppProber.analyze(app_dir, app_info=mock_info)
        assert result.strategy == "hard_clone"
        assert result.has_sandbox is True
        assert result.recipe.strip_sandbox is True


def test_app_prober_chromium(tmp_path: Path):
    app_dir = tmp_path / "ChromiumApp.app"
    app_dir.mkdir()

    mock_info = AppInfo(
        path=app_dir,
        bundle_id="com.google.chrome.beta",
        app_name="ChromiumApp",
        executable=app_dir / "Contents" / "MacOS" / "ChromiumApp",
        has_sandbox=False,
    )

    with patch.object(AppProber, "inspect_entitlements", return_value={}), \
         patch.object(AppProber, "detect_frameworks", return_value=[]):
        result = AppProber.analyze(app_dir, app_info=mock_info)
        assert result.strategy == "soft_clone"
        assert result.recipe.launch_args == ["--user-data-dir={{ATB_DATA_DIR}}"]


def test_app_prober_electron_framework(tmp_path: Path):
    app_dir = tmp_path / "ElectronApp.app"
    app_dir.mkdir()

    mock_info = AppInfo(
        path=app_dir,
        bundle_id="com.custom.electronapp",
        app_name="ElectronApp",
        executable=app_dir / "Contents" / "MacOS" / "ElectronApp",
        has_sandbox=False,
    )

    with patch.object(AppProber, "inspect_entitlements", return_value={}), \
         patch.object(AppProber, "detect_frameworks", return_value=["Electron Framework.framework"]):
        result = AppProber.analyze(app_dir, app_info=mock_info)
        assert result.strategy == "soft_clone"
        assert result.recipe.launch_args == ["--user-data-dir={{ATB_DATA_DIR}}"]


def test_app_prober_firefox(tmp_path: Path):
    app_dir = tmp_path / "FirefoxNightly.app"
    app_dir.mkdir()

    mock_info = AppInfo(
        path=app_dir,
        bundle_id="org.mozilla.firefoxnightly",
        app_name="FirefoxNightly",
        executable=app_dir / "Contents" / "MacOS" / "firefox",
        has_sandbox=False,
    )

    with patch("atbclone.core.app_prober.AppInspector.inspect", return_value=mock_info), \
         patch.object(AppProber, "inspect_entitlements", return_value={}), \
         patch.object(AppProber, "detect_frameworks", return_value=[]):
        recipe = AppProber.probe(app_dir)
        assert recipe.strategy == "soft_clone"
        assert recipe.launch_args == ["-profile", "{{ATB_DATA_DIR}}"]
