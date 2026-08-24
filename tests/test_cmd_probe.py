"""Unit tests for the `probe` CLI command."""

import json
from pathlib import Path
from unittest.mock import patch
import pytest
import yaml
from click.testing import CliRunner

from atbclone.cli.main import cli
from atbclone.core.app_prober import ProbeResult
from atbclone.core.models import AppInfo
from atbclone.recipes.models import Recipe


@pytest.fixture
def sample_probe_result(tmp_path: Path) -> ProbeResult:
    app_dir = tmp_path / "DemoApp.app"
    app_dir.mkdir(parents=True, exist_ok=True)
    info = AppInfo(
        path=app_dir,
        bundle_id="com.demo.app",
        app_name="DemoApp",
        executable=app_dir / "Contents" / "MacOS" / "DemoApp",
        has_sandbox=False,
    )
    recipe = Recipe(
        bundle_id="com.demo.app",
        app_name="DemoApp",
        strategy="hard_clone",
        strip_sandbox=False,
        environment_injection={
            "HOME": "{{ATB_DATA_DIR}}/Home",
            "TMPDIR": "{{ATB_DATA_DIR}}/Tmp",
        },
    )
    return ProbeResult(
        app_info=info,
        has_sandbox=False,
        frameworks=["Qt6Core.framework"],
        strategy="hard_clone",
        reason="Native macOS application (Non-sandboxed)",
        recipe=recipe,
    )


def test_probe_default_output(tmp_path: Path, sample_probe_result: ProbeResult):
    runner = CliRunner()
    app_path = sample_probe_result.app_info.path

    with patch("atbclone.cli.cmd_probe.AppProber.analyze", return_value=sample_probe_result):
        result = runner.invoke(cli, ["probe", str(app_path)])
        assert result.exit_code == 0
        assert "ATBClone Deep Application Probe" in result.output or "ATBClone 深度应用探测" in result.output
        assert "com.demo.app" in result.output
        assert "DemoApp" in result.output
        assert "hard_clone" in result.output
        assert "Generated Recipe YAML" in result.output or "生成的 Recipe YAML" in result.output


def test_probe_json_mode(tmp_path: Path, sample_probe_result: ProbeResult):
    runner = CliRunner()
    app_path = sample_probe_result.app_info.path

    with patch("atbclone.cli.cmd_probe.AppProber.analyze", return_value=sample_probe_result):
        result = runner.invoke(cli, ["probe", str(app_path), "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["bundle_id"] == "com.demo.app"
        assert data["strategy"] == "hard_clone"
        assert data["has_sandbox"] is False
        assert data["recipe"]["strategy"] == "hard_clone"


def test_probe_save_option(tmp_path: Path, sample_probe_result: ProbeResult):
    runner = CliRunner()
    app_path = sample_probe_result.app_info.path
    local_recipes = tmp_path / "recipes"

    with patch("atbclone.cli.cmd_probe.AppProber.analyze", return_value=sample_probe_result), \
         patch("atbclone.recipes.loader.RecipeLoader.get_local_dir", return_value=local_recipes):
        result = runner.invoke(cli, ["probe", str(app_path), "--save"])
        assert result.exit_code == 0
        assert "Saved recipe to" in result.output or "已保存分身规则至" in result.output or "已保存配方至" in result.output

        saved_file = local_recipes / "com.demo.app.yaml"
        assert saved_file.exists()
        saved_recipe = yaml.safe_load(saved_file.read_text(encoding="utf-8"))
        assert saved_recipe["bundle_id"] == "com.demo.app"
        assert saved_recipe["strategy"] == "hard_clone"


def test_probe_output_option(tmp_path: Path, sample_probe_result: ProbeResult):
    runner = CliRunner()
    app_path = sample_probe_result.app_info.path
    custom_out = tmp_path / "custom_dir" / "my_recipe.yaml"

    with patch("atbclone.cli.cmd_probe.AppProber.analyze", return_value=sample_probe_result):
        result = runner.invoke(cli, ["probe", str(app_path), "-o", str(custom_out)])
        assert result.exit_code == 0
        assert "Saved recipe to" in result.output or "已保存分身规则至" in result.output or "已保存配方至" in result.output
        assert custom_out.exists()
        saved_recipe = yaml.safe_load(custom_out.read_text(encoding="utf-8"))
        assert saved_recipe["bundle_id"] == "com.demo.app"


def test_probe_invalid_app_path(tmp_path: Path):
    runner = CliRunner()
    not_app = tmp_path / "not_an_app.txt"
    not_app.write_text("hello")

    result = runner.invoke(cli, ["probe", str(not_app)])
    assert result.exit_code != 0
    assert "not a valid macOS" in result.output


def test_probe_unknown_app_probes_cli_data_dir_argument(tmp_path: Path):
    app_dir = tmp_path / "CustomCLI.app"
    macos_dir = app_dir / "Contents" / "MacOS"
    macos_dir.mkdir(parents=True)
    exe = macos_dir / "CustomCLI"
    exe.write_bytes(b"MachO_HEADER\x00--data-dir=\x00--other\x00")
    plist = app_dir / "Contents" / "Info.plist"
    plist.write_bytes(b"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleIdentifier</key><string>com.custom.cli</string>
    <key>CFBundleExecutable</key><string>CustomCLI</string>
    <key>CFBundleName</key><string>CustomCLI</string>
</dict>
</plist>""")

    runner = CliRunner()
    result = runner.invoke(cli, ["probe", str(app_dir), "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["strategy"] == "soft_clone"
    assert data["recipe"]["launch_args"] == ["--data-dir={{ATB_DATA_DIR}}"]
    assert "--data-dir" in data["reason"]

