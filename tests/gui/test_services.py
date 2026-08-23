import asyncio
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

from atbclone.core.app_inspector import AppInspector
from atbclone.core.clone_task import CloneTask
from atbclone.core.models import AppInfo
from atbclone.core.state import CloneRecord
from atbclone.recipes.models import Recipe, ProxyConfig
from atbclone.gui.services.clone_service import CloneService
from atbclone.gui.services.recipe_service import RecipeService
from atbclone.gui.services.probe_service import ProbeService
from atbclone.gui.services.doctor_service import DoctorService, DoctorCheckItem


def test_clone_service_list_clones(tmp_path):
    async def _test():
        state_file = tmp_path / "clones.yaml"
        record = CloneRecord(
            clone_name="WeChat2",
            source_app="WeChat",
            source_path="/Applications/WeChat.app",
            bundle_id="com.tencent.xinWeChat",
            strategy="hard_clone",
            dest_path=str(tmp_path / "WeChat2.app"),
            data_dir=str(tmp_path / "data"),
            created_at="2026-08-19T00:00:00Z",
        )
        service = CloneService(state_file=state_file)
        service.state_manager.add(record)

        clones = await service.list_clones()
        assert len(clones) == 1
        assert clones[0].clone_name == "WeChat2"

    asyncio.run(_test())


def test_clone_service_create_clone(tmp_path):
    async def _test():
        state_file = tmp_path / "clones.yaml"
        service = CloneService(state_file=state_file)

        task = CloneTask(
            source=AppInfo(
                path=Path("/Applications/TestApp.app"),
                bundle_id="com.example.test",
                app_name="TestApp",
                executable=Path("/Applications/TestApp.app/Contents/MacOS/TestApp"),
                has_sandbox=False,
            ),
            dest_path=tmp_path / "TestApp2.app",
            data_dir=tmp_path / "data",
            recipe=Recipe(bundle_id="com.example.test", app_name="TestApp", strategy="soft_clone"),
            clone_name="TestApp2",
            new_bundle_id="com.example.test.clone1",
        )

        with patch("atbclone.core.engines.SoftCloneEngine.execute") as mock_exec:
            record = await service.create_clone(task)
            assert mock_exec.called
            assert record.clone_name == "TestApp2"
            assert service.state_manager.get("TestApp2") is not None

    asyncio.run(_test())


def test_clone_service_remove_clone(tmp_path):
    async def _test():
        state_file = tmp_path / "clones.yaml"
        service = CloneService(state_file=state_file)
        record = CloneRecord(
            clone_name="ToDel",
            source_app="App",
            source_path="/App.app",
            bundle_id="com.app",
            strategy="soft_clone",
            dest_path=str(tmp_path / "ToDel.app"),
            data_dir=str(tmp_path / "data"),
            created_at="2026-08-19T00:00:00Z",
        )
        service.state_manager.add(record)

        with patch("atbclone.executor.runner.Runner.run") as mock_runner:
            success = await service.remove_clone("ToDel", with_data=True)
            assert success is True
            assert mock_runner.called
            assert service.state_manager.get("ToDel") is None

    asyncio.run(_test())


def test_clone_service_update_clone(tmp_path):
    async def _test():
        state_file = tmp_path / "clones.yaml"
        source_app = tmp_path / "WeChat.app"
        source_app.mkdir(parents=True, exist_ok=True)
        (source_app / "Contents").mkdir(parents=True, exist_ok=True)
        (source_app / "Contents" / "MacOS").mkdir(parents=True, exist_ok=True)

        service = CloneService(state_file=state_file)
        record = CloneRecord(
            clone_name="WeChat2",
            source_app="WeChat",
            source_path=str(source_app),
            bundle_id="com.tencent.xinWeChat",
            strategy="hard_clone",
            dest_path=str(tmp_path / "WeChat2.app"),
            data_dir=str(tmp_path / "data"),
            created_at="2026-08-19T00:00:00Z",
        )
        service.state_manager.add(record)

        with patch("atbclone.core.app_inspector.AppInspector.inspect") as mock_inspect, \
             patch("atbclone.core.engines.HardCloneEngine.execute") as mock_exec, \
             patch("atbclone.executor.runner.Runner.run") as mock_runner:
            mock_inspect.return_value = AppInfo(
                path=source_app,
                bundle_id="com.tencent.xinWeChat",
                app_name="WeChat",
                executable=source_app / "Contents" / "MacOS" / "WeChat",
                has_sandbox=True,
            )
            updated = await service.update_clone("WeChat2")
            assert updated.clone_name == "WeChat2"
            assert mock_exec.called
            assert "WeChat2" not in service._busy_clones

    asyncio.run(_test())


def test_clone_service_concurrent_busy_lock(tmp_path):
    async def _test():
        state_file = tmp_path / "clones.yaml"
        service = CloneService(state_file=state_file)
        service._busy_clones.add("WeChat2")

        with pytest.raises(RuntimeError, match="Operation already in progress for 'WeChat2'"):
            await service.update_clone("WeChat2")

        with pytest.raises(RuntimeError, match="Operation already in progress for 'WeChat2'"):
            await service.remove_clone("WeChat2")

        task = MagicMock()
        task.clone_name = "WeChat2"
        with pytest.raises(RuntimeError, match="Operation already in progress for 'WeChat2'"):
            await service.create_clone(task)

    asyncio.run(_test())


def test_recipe_service_crud(tmp_path):
    async def _test():
        service = RecipeService(custom_recipes_dir=tmp_path / "recipes")
        recipes = await service.list_all_recipes()
        assert isinstance(recipes, list)
        assert any(r["bundle_id"] == "com.tencent.xinWeChat" for r in recipes)

        # Save custom recipe
        new_recipe = Recipe(
            bundle_id="com.custom.app",
            app_name="CustomApp",
            strategy="hard_clone",
        )
        await service.save_custom_recipe(new_recipe)
        assert (tmp_path / "recipes" / "com.custom.app.yaml").exists()

        loaded = await service.get_recipe("com.custom.app")
        assert loaded is not None
        assert loaded.app_name == "CustomApp"

        # Duplicate recipe test creates custom override with identical bundle_id
        orig_recipe = await service.get_recipe("com.tencent.xinWeChat")
        assert orig_recipe is not None
        dup1 = await service.duplicate_recipe(orig_recipe)
        assert dup1.app_name == orig_recipe.app_name
        assert dup1.bundle_id == orig_recipe.bundle_id
        assert (tmp_path / "recipes" / f"{orig_recipe.bundle_id}.yaml").exists()

        # Delete custom recipe
        deleted = await service.delete_custom_recipe("com.custom.app")
        assert deleted is True
        assert not (tmp_path / "recipes" / "com.custom.app.yaml").exists()

    asyncio.run(_test())


def test_probe_service():
    async def _test():
        service = ProbeService()
        with patch("atbclone.core.app_prober.AppProber.analyze") as mock_analyze:
            mock_result = MagicMock()
            mock_result.recipe = Recipe(bundle_id="com.test", app_name="Test", strategy="hard_clone")
            mock_result.architecture = "arm64"
            mock_result.engine = "Native"
            mock_result.has_sandbox = False
            mock_analyze.return_value = mock_result

            res = await service.probe_app(Path("/Applications/Test.app"))
            assert res.recipe.bundle_id == "com.test"
            assert res.engine == "Native"

    asyncio.run(_test())


def test_doctor_service():
    async def _test():
        service = DoctorService()
        items = await service.check_environment()
        assert len(items) >= 3
        names = [item.name for item in items]
        assert "codesign" in names
        assert "xcode-select" in names
        assert "PlistBuddy" in names

    asyncio.run(_test())


def test_doctor_service_check_xcode_select_installed():
    async def _test():
        service = DoctorService()
        with patch("subprocess.check_output", return_value="/Library/Developer/CommandLineTools\n"):
            assert await service.check_xcode_select_installed() is True

        with patch("subprocess.check_output", side_effect=Exception("xcode-select: error: unable to get active developer directory")):
            assert await service.check_xcode_select_installed() is False

    asyncio.run(_test())


def test_doctor_service_trigger_xcode_install():
    async def _test():
        service = DoctorService()

        # Case 1: Successfully launched
        mock_ok = MagicMock(returncode=0, stdout="xcode-select: note: install requested for command line developer tools\n", stderr="")
        with patch("subprocess.run", return_value=mock_ok):
            success, status = await service.trigger_xcode_install()
            assert success is True
            assert status == "launched"

        # Case 2: Already installed
        mock_already = MagicMock(returncode=1, stdout="", stderr="xcode-select: error: command line tools are already installed, use \"Software Update\" in System Settings to update\n")
        with patch("subprocess.run", return_value=mock_already):
            success, status = await service.trigger_xcode_install()
            assert success is True
            assert status == "already_installed"

        # Case 3: Error
        mock_err = MagicMock(returncode=2, stdout="", stderr="xcode-select: error: something went wrong")
        with patch("subprocess.run", return_value=mock_err):
            success, status = await service.trigger_xcode_install()
            assert success is False
            assert "something went wrong" in status

        # Case 4: Exception
        with patch("subprocess.run", side_effect=OSError("Command not found")):
            success, status = await service.trigger_xcode_install()
            assert success is False
            assert "Command not found" in status

    asyncio.run(_test())

