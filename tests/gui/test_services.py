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

        # Duplicate recipe test with automatic sequence suffix (.atbclone.N)
        orig_recipe = await service.get_recipe("com.tencent.xinWeChat")
        assert orig_recipe is not None
        dup1 = await service.duplicate_recipe(orig_recipe)
        assert dup1.app_name == f"{orig_recipe.app_name}_2"
        assert dup1.bundle_id == f"{orig_recipe.bundle_id}.atbclone.2"
        assert (tmp_path / "recipes" / f"{dup1.bundle_id}.yaml").exists()

        # Duplicate again to get _3
        dup2 = await service.duplicate_recipe(orig_recipe)
        assert dup2.app_name == f"{orig_recipe.app_name}_3"
        assert dup2.bundle_id == f"{orig_recipe.bundle_id}.atbclone.3"

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
