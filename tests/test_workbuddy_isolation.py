"""Unit tests for WorkBuddy isolation, recipes, and Electron hard clone guarantees."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from atbclone.core.app_prober import AppProber
from atbclone.core.clone_task import CloneTask
from atbclone.core.engines import HardCloneEngine
from atbclone.core.models import AppInfo
from atbclone.recipes.loader import RecipeLoader
from atbclone.recipes.models import Recipe


def test_workbuddy_builtin_recipes():
    """Verify built-in recipes for WorkBuddy exist and have proper isolation configurations."""
    for bid in ("com.tencent.workbuddy.mac", "com.workbuddy.workbuddy-ai"):
        recipe = RecipeLoader.get(bid)
        assert recipe is not None, f"Recipe for {bid} should exist"
        assert recipe.strategy == "hard_clone"
        assert recipe.app_type == "electron"
        assert recipe.strip_sandbox is True
        assert recipe.strip_url_schemes is True
        assert recipe.patch_workbuddy_isolation is True

        env = recipe.environment_injection
        assert env.get("HOME") == "{{ATB_DATA_DIR}}/Home"
        assert env.get("TMPDIR") == "{{ATB_DATA_DIR}}/Tmp"
        assert env.get("WORKBUDDY_CONFIG_DIR") == "{{ATB_DATA_DIR}}/Config"
        assert env.get("WORKBUDDY_USER_DATA_DIR") == "{{ATB_DATA_DIR}}/UserData"
        assert "Library/Keychains" in recipe.symlink_whitelist


def test_app_prober_workbuddy_dynamic_probe(tmp_path: Path):
    """Verify AppProber accurately assigns WorkBuddy environment variables and hard_clone."""
    app_dir = tmp_path / "WorkBuddy.app"
    app_dir.mkdir()

    mock_info = AppInfo(
        path=app_dir,
        bundle_id="com.tencent.workbuddy.mac",
        app_name="WorkBuddy",
        executable=app_dir / "Contents" / "MacOS" / "WorkBuddy",
        has_sandbox=True,
    )

    with patch.object(AppProber, "inspect_entitlements", return_value={"com.apple.security.app-sandbox": True}), \
         patch.object(AppProber, "detect_frameworks", return_value=["Electron Framework.framework"]):
        result = AppProber.analyze(app_dir, app_info=mock_info)
        assert result.strategy == "hard_clone"
        assert result.recipe.strip_sandbox is True
        assert result.recipe.launch_args == []
        assert result.recipe.environment_injection["HOME"] == "{{ATB_DATA_DIR}}/Home"
        assert result.recipe.environment_injection["TMPDIR"] == "{{ATB_DATA_DIR}}/Tmp"
        assert result.recipe.environment_injection["WORKBUDDY_CONFIG_DIR"] == "{{ATB_DATA_DIR}}/Config"
        assert result.recipe.environment_injection["WORKBUDDY_USER_DATA_DIR"] == "{{ATB_DATA_DIR}}/UserData"


def test_hard_clone_engine_workbuddy_script_generation(tmp_path: Path):
    """Verify HardCloneEngine generates hook compilation, URL stripping, and environment injection for WorkBuddy."""
    src_app = tmp_path / "WorkBuddy.app"
    src_app.mkdir(parents=True)
    (src_app / "Contents" / "MacOS").mkdir(parents=True)
    exe_file = src_app / "Contents" / "MacOS" / "WorkBuddy"
    exe_file.write_text("#!/bin/sh\nexit 0\n")
    exe_file.chmod(0o755)

    dst_app = tmp_path / "WorkBuddy2.app"
    data_dir = tmp_path / "Data" / "WorkBuddy2"

    recipe = RecipeLoader.get("com.tencent.workbuddy.mac")
    assert recipe is not None

    source_info = AppInfo(
        path=src_app,
        bundle_id="com.tencent.workbuddy.mac",
        app_name="WorkBuddy",
        executable=exe_file,
        has_sandbox=True,
    )

    task = CloneTask(
        source=source_info,
        dest_path=dst_app,
        data_dir=data_dir,
        recipe=recipe,
        clone_name="WorkBuddy2",
        new_bundle_id="com.tencent.workbuddy.mac.atbclone.2",
    )

    captured_scripts: list[str] = []

    def fake_run(script: str, needs_admin: bool = False):
        captured_scripts.append(script)

    with patch("atbclone.core.engines.Runner.run", side_effect=fake_run), \
         patch("atbclone.core.engines.HardCloneEngine._build_process_name_cmd", return_value=""):
        HardCloneEngine.execute(task)

    assert len(captured_scripts) == 1
    script = captured_scripts[0]

    # Verify WorkBuddy hook dylib compilation is generated
    assert "libatbclone_workbuddy_hook.dylib" in script
    assert "WORKBUDDY_HOOK_EOF" in script
    assert "Delete :CFBundleURLTypes" in script

    # Verify environment variables are exported in launcher
    assert f'setenv("WORKBUDDY_CONFIG_DIR", "{data_dir}/Config", 1)' in script
    assert f'setenv("WORKBUDDY_USER_DATA_DIR", "{data_dir}/UserData", 1)' in script
    assert f'setenv("HOME", "{data_dir}/Home", 1)' in script
    assert f'setenv("TMPDIR", "{data_dir}/Tmp", 1)' in script
    assert 'setenv("DYLD_INSERT_LIBRARIES"' in script
    assert "../Frameworks/libatbclone_workbuddy_hook.dylib" in script


def test_hard_clone_engine_electron_always_has_home_and_tmpdir(tmp_path: Path):
    """Verify HardCloneEngine always injects HOME and TMPDIR for Electron apps even if custom launch_args exist."""
    src_app = tmp_path / "CustomElectron.app"
    src_app.mkdir(parents=True)
    (src_app / "Contents" / "MacOS").mkdir(parents=True)
    exe_file = src_app / "Contents" / "MacOS" / "CustomElectron"
    exe_file.write_text("#!/bin/sh\nexit 0\n")
    exe_file.chmod(0o755)

    dst_app = tmp_path / "CustomElectronClone.app"
    data_dir = tmp_path / "Data" / "CustomElectronClone"

    # Recipe specifies an arbitrary launch arg with {{ATB_DATA_DIR}} and empty env injection
    recipe = Recipe(
        bundle_id="com.example.customelectron",
        app_name="CustomElectron",
        strategy="hard_clone",
        app_type="electron",
        launch_args=["--user-data-dir={{ATB_DATA_DIR}}"],
        environment_injection={},
    )

    source_info = AppInfo(
        path=src_app,
        bundle_id="com.example.customelectron",
        app_name="CustomElectron",
        executable=exe_file,
        has_sandbox=False,
    )

    task = CloneTask(
        source=source_info,
        dest_path=dst_app,
        data_dir=data_dir,
        recipe=recipe,
        clone_name="CustomElectronClone",
        new_bundle_id="com.example.customelectron.atbclone.1",
    )

    captured_scripts: list[str] = []

    def fake_run(script: str, needs_admin: bool = False):
        captured_scripts.append(script)

    with patch("atbclone.core.engines.Runner.run", side_effect=fake_run), \
         patch("atbclone.core.engines.HardCloneEngine._build_process_name_cmd", return_value=""):
        HardCloneEngine.execute(task)

    assert len(captured_scripts) == 1
    script = captured_scripts[0]

    # Both HOME and TMPDIR must be set despite launch_args containing {{ATB_DATA_DIR}}
    assert f'setenv("HOME", "{data_dir}/Home", 1)' in script
    assert f'setenv("TMPDIR", "{data_dir}/Tmp", 1)' in script
