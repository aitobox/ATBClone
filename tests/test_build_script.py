"""Tests for build_cli.sh, release.sh, notarize.sh and entitlements integrity."""

import os
import plistlib
import subprocess
from pathlib import Path


def test_build_script_exists_and_executable():
    root = Path(__file__).parent.parent
    script = root / "scripts" / "build_cli.sh"
    assert script.exists(), "scripts/build_cli.sh does not exist"
    assert os.access(script, os.X_OK), "scripts/build_cli.sh is not executable"


def test_build_script_bash_syntax():
    root = Path(__file__).parent.parent
    script = root / "scripts" / "build_cli.sh"
    result = subprocess.run(
        ["bash", "-n", str(script)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Bash syntax error: {result.stderr}"


def test_build_script_contains_required_flags():
    root = Path(__file__).parent.parent
    script = root / "scripts" / "build_cli.sh"
    content = script.read_text(encoding="utf-8")
    assert "--onefile" in content
    assert "ATBCloneCli" in content
    assert "--include-package=atbclone" in content
    assert "--include-package-data=atbclone" in content
    assert "src/atbclone_entry.py" in content
    assert "--include-package=pydantic_core" in content
    # Code signing additions
    assert "codesign" in content
    assert "--options runtime" in content
    assert "--timestamp" in content
    assert "entitlements.plist" in content
    assert "security find-identity" in content
    assert 'TEAM_ID="WC7C59Q92T"' in content
    assert "Shanghai Tianzhi Cloud Information Technology Co., LTD" in content


def test_build_script_help_output():
    root = Path(__file__).parent.parent
    script = root / "scripts" / "build_cli.sh"
    result = subprocess.run(
        ["bash", str(script), "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Usage:" in result.stdout
    assert "--sign" in result.stdout
    assert "--notarize" in result.stdout


def test_entry_point_uses_absolute_imports():
    root = Path(__file__).parent.parent
    entry = root / "src" / "atbclone_entry.py"
    assert entry.exists(), "src/atbclone_entry.py does not exist"
    content = entry.read_text(encoding="utf-8")
    assert "from atbclone.cli.main import cli" in content
    assert "from .cli" not in content


def test_release_script_exists_and_executable():
    root = Path(__file__).parent.parent
    script = root / "scripts" / "release.sh"
    assert script.exists(), "scripts/release.sh does not exist"
    assert os.access(script, os.X_OK), "scripts/release.sh is not executable"


def test_release_script_bash_syntax():
    root = Path(__file__).parent.parent
    script = root / "scripts" / "release.sh"
    result = subprocess.run(
        ["bash", "-n", str(script)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Bash syntax error: {result.stderr}"


def test_release_script_help_output():
    root = Path(__file__).parent.parent
    script = root / "scripts" / "release.sh"
    result = subprocess.run(
        ["bash", str(script), "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Usage:" in result.stdout
    assert "--sign" in result.stdout


def test_notarize_script_exists_and_executable():
    root = Path(__file__).parent.parent
    script = root / "scripts" / "notarize.sh"
    assert script.exists(), "scripts/notarize.sh does not exist"
    assert os.access(script, os.X_OK), "scripts/notarize.sh is not executable"


def test_notarize_script_bash_syntax():
    root = Path(__file__).parent.parent
    script = root / "scripts" / "notarize.sh"
    result = subprocess.run(
        ["bash", "-n", str(script)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Bash syntax error: {result.stderr}"


def test_notarize_script_help_output():
    root = Path(__file__).parent.parent
    script = root / "scripts" / "notarize.sh"
    result = subprocess.run(
        ["bash", str(script), "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Usage:" in result.stdout
    assert "notarytool" in result.stdout


def test_entitlements_plist_validity():
    root = Path(__file__).parent.parent
    plist_path = root / "scripts" / "entitlements.plist"
    assert plist_path.exists(), "scripts/entitlements.plist does not exist"
    data = plistlib.loads(plist_path.read_bytes())
    assert data.get("com.apple.security.cs.allow-jit") is True
    assert data.get("com.apple.security.cs.allow-unsigned-executable-memory") is True
    assert data.get("com.apple.security.cs.disable-library-validation") is True
    assert data.get("com.apple.security.cs.allow-dyld-environment-variables") is True


def test_pyproject_contains_briefcase_icon():
    root = Path(__file__).parent.parent
    content = (root / "pyproject.toml").read_text(encoding="utf-8")
    assert 'icon = "resource/images/logo"' in content


def test_build_cli_contains_macos_icon_flag():
    root = Path(__file__).parent.parent
    content = (root / "scripts" / "build_cli.sh").read_text(encoding="utf-8")
    assert "--macos-app-icon=" in content
    assert "--include-data-dir=resource=resource" in content


def test_build_gui_references_icon():
    root = Path(__file__).parent.parent
    content = (root / "scripts" / "build_gui.sh").read_text(encoding="utf-8")
    assert "logo.icns" in content or "ATBClone.icns" in content or "icon" in content
    assert "atbclone.icns" in content


def test_build_gui_syncs_latest_icons_and_resources():
    root = Path(__file__).parent.parent
    content = (root / "scripts" / "build_gui.sh").read_text(encoding="utf-8")
    assert 'cp -f "resource/images/logo.icns" "${APP_BUNDLE}/Contents/Resources/atbclone.icns"' in content
    assert 'cp -f "resource/images/logo.icns" "${APP_BUNDLE}/Contents/Resources/ATBClone.icns"' in content
    assert 'Contents/Resources/resource/images' in content


def test_build_gui_bundle_integrity_checks():
    root = Path(__file__).parent.parent
    content = (root / "scripts" / "build_gui.sh").read_text(encoding="utf-8")
    assert "Python.framework" in content
    assert "Contents/MacOS/ATBClone" in content
    assert "__main__.py" in content
    assert "briefcase build macOS -u" in content


def test_build_gui_bash_syntax():
    root = Path(__file__).parent.parent
    script = root / "scripts" / "build_gui.sh"
    result = subprocess.run(
        ["bash", "-n", str(script)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Bash syntax error: {result.stderr}"


def test_build_gui_contains_xattr_sanitization():
    root = Path(__file__).parent.parent
    content = (root / "scripts" / "build_gui.sh").read_text(encoding="utf-8")
    assert "sanitize_filesystem" in content
    assert "xattr -cr" in content
    assert "codesign_wrapper.py" in content


def test_codesign_wrapper_logic():
    import importlib.util

    root = Path(__file__).parent.parent
    wrapper_path = root / "scripts" / "codesign_wrapper.py"
    assert wrapper_path.exists()
    assert os.access(wrapper_path, os.X_OK)

    spec = importlib.util.spec_from_file_location("codesign_wrapper", str(wrapper_path))
    assert spec and spec.loader
    wrapper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(wrapper)

    assert wrapper.is_detritus_error("resource fork, Finder information, or similar detritus not allowed")
    assert wrapper.is_detritus_error("detritus not allowed")
    assert not wrapper.is_detritus_error("invalid argument")

    assert wrapper.is_retryable_error("timestamp service is not available")
    assert wrapper.is_retryable_error("Operation timed out")
    assert not wrapper.is_retryable_error("code object is not signed at all")

    extracted = wrapper.extract_targets(["--sign", "-", "--force", "--entitlements", "Entitlements.plist", "build/App.app"])
    assert extracted == ["build/App.app"]


def test_build_release_packages_script_exists_and_executable():
    root = Path(__file__).parent.parent
    script = root / "scripts" / "build_release_packages.sh"
    assert script.exists(), "scripts/build_release_packages.sh does not exist"
    assert os.access(script, os.X_OK), "scripts/build_release_packages.sh is not executable"


def test_build_release_packages_bash_syntax():
    root = Path(__file__).parent.parent
    script = root / "scripts" / "build_release_packages.sh"
    result = subprocess.run(
        ["bash", "-n", str(script)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Bash syntax error: {result.stderr}"


def test_build_release_packages_help():
    root = Path(__file__).parent.parent
    script = root / "scripts" / "build_release_packages.sh"
    result = subprocess.run(
        ["bash", str(script), "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Usage:" in result.stdout
    assert "ATBCloneCli-<VERSION>-arm64.tar.gz" in result.stdout
    assert "ATBClone-<VERSION>-arm64.dmg" in result.stdout
    assert "--sign" in result.stdout
    assert "--notarize" in result.stdout


def test_build_release_packages_content_contracts():
    root = Path(__file__).parent.parent
    script = root / "scripts" / "build_release_packages.sh"
    content = script.read_text(encoding="utf-8")
    assert "ATBCloneCli-${TARGET_VERSION}-arm64.tar.gz" in content
    assert "ATBClone-${TARGET_VERSION}-arm64.dmg" in content
    assert "-Wl,-needed_framework,AppKit" in content
    assert "checksums.txt" in content
    assert "scripts/build_cli.sh" in content
    assert "scripts/build_gui.sh" in content


def test_release_workflow_syntax_and_structure():
    import yaml

    root = Path(__file__).parent.parent
    workflow_path = root / ".github" / "workflows" / "release.yml"
    assert workflow_path.exists(), ".github/workflows/release.yml does not exist"

    data = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))
    assert data["name"] == "Release"
    on_trigger = data.get("on") or data.get(True)
    assert on_trigger is not None, "Missing 'on' trigger configuration"
    assert "push" in on_trigger
    assert "tags" in on_trigger["push"]
    assert "workflow_dispatch" in on_trigger

    job = data["jobs"]["build-and-release"]
    assert job["runs-on"] == "macos-14"
    assert data["permissions"]["contents"] == "write"

    workflow_text = workflow_path.read_text(encoding="utf-8")
    assert "MAC_CERTS_P12_BASE64" in workflow_text
    assert "MAC_CERTS_PASSWORD" in workflow_text
    assert "MAC_PROVISION_PROFILE_BASE64" in workflow_text
    assert "APPLE_ID" in workflow_text
    assert "APPLE_PASSWORD" in workflow_text
    assert "APPLE_TEAM_ID" in workflow_text
    assert "ATBCloneCli-${VERSION}-arm64.tar.gz" in workflow_text
    assert "ATBClone-${VERSION}-arm64.dmg" in workflow_text
    assert "gh release create" in workflow_text
    assert "build_release_packages.sh" in workflow_text


def test_build_cli_notarize_args_guard():
    root = Path(__file__).parent.parent
    script = root / "scripts" / "build_cli.sh"
    content = script.read_text(encoding="utf-8")
    assert "${#NOTARIZE_ARGS[@]}" in content




