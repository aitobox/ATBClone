"""Regression coverage for icons surviving GUI and CLI rebuilds."""

import asyncio
import plistlib
import shlex
import shutil
import subprocess
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from atbclone.cli.main import cli
from atbclone.core.engines import CloneEngine
from atbclone.core.models import AppInfo
from atbclone.core.state import CloneRecord
from atbclone.gui.services.clone_service import CloneService
from atbclone.recipes.models import Recipe


@pytest.mark.parametrize("frontend", ["cli", "gui"])
@pytest.mark.parametrize("strategy", ["soft_clone", "hard_clone"])
@pytest.mark.parametrize("custom", [False, True])
def test_update_preserves_installed_icon(tmp_path, frontend, strategy, custom):
    """Rebuild twice using the installed icon, without the original selected file."""
    source = tmp_path / "Original.app"
    source.mkdir()
    dest = tmp_path / "Clone's App.app"
    resources = dest / "Contents/Resources"
    resources.mkdir(parents=True)
    if custom:
        (resources / "ATBCloneIcon.icns").write_bytes(b"installed custom icon")
    record = CloneRecord(
        clone_name="Clone", source_app="Original", source_path=str(source),
        bundle_id="com.test.original", strategy=strategy, dest_path=str(dest),
        data_dir=str(tmp_path / "Data"), created_at="old",
        new_bundle_id="com.test.clone",
    )
    info = AppInfo(source, "com.test.original", "Original", source / "Contents/MacOS/Original", False)
    recipe = Recipe(bundle_id=info.bundle_id, app_name="Original", strategy=strategy)
    module = "atbclone.cli.cmd_update" if frontend == "cli" else "atbclone.gui.services.clone_service"
    saved_paths = []

    def rebuild(task, needs_admin):
        """Exercise the real icon installation after the old bundle is removed."""
        if custom:
            assert task.icon_path is not None
            assert task.icon_path.read_bytes() == b"installed custom icon"
            saved_paths.append(task.icon_path)
        else:
            assert task.icon_path is None
        shutil.rmtree(dest, ignore_errors=True)
        resources.mkdir(parents=True)
        metadata = dest / "Contents/Info.plist"
        metadata.write_bytes(plistlib.dumps({"CFBundleIconFile": "Original.icns", "CFBundleIconName": "AppIcon"}))
        subprocess.run(["bash", "-ec", CloneEngine._build_icon_cmd(task, shlex.quote(str(resources)), shlex.quote(str(metadata)))], check=True)
        if custom:
            assert (resources / "ATBCloneIcon.icns").read_bytes() == b"installed custom icon"
            assert plistlib.loads(metadata.read_bytes())["CFBundleIconFile"] == "ATBCloneIcon.icns"
            assert "CFBundleIconName" not in plistlib.loads(metadata.read_bytes())

    with patch(f"{module}.StateManager.get", return_value=record), \
         patch(f"{module}.StateManager.load", return_value=[record]), \
         patch(f"{module}.StateManager.add"), \
         patch(f"{module}.AppInspector.inspect", return_value=info), \
         patch(f"{module}.RecipeLoader.match", return_value=recipe), \
         patch(f"{module}.Runner.run", side_effect=lambda script, admin: subprocess.run(["bash", "-ec", script], check=True)), \
         patch(f"{module}.{'SoftCloneEngine' if strategy == 'soft_clone' else 'HardCloneEngine'}.execute", side_effect=rebuild):
        for _ in range(2):
            if frontend == "cli":
                result = CliRunner().invoke(cli, ["update", "Clone"])
                assert result.exit_code == 0, result.output
            else:
                asyncio.run(CloneService(tmp_path / "state.json").update_clone("Clone"))
    assert all(not path.exists() for path in saved_paths)
