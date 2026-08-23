import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from atbclone.core.app_prober import ProbeResult
from atbclone.core.models import AppInfo
from atbclone.recipes.models import Recipe
from atbclone.gui.services.doctor_service import DoctorCheckItem, DoctorService
from atbclone.gui.services.probe_service import ProbeService
from atbclone.gui.services.recipe_service import RecipeService
from atbclone.gui.views.doctor_view import DoctorView
from atbclone.gui.views.probe_view import ProbeView


def test_doctor_view_render():
    async def _test():
        doctor_service = DoctorService()
        view = DoctorView(doctor_service=doctor_service)
        await view.run_checks()
        assert len(view.table.data) >= 3
        assert hasattr(view, "btn_install_xcode")

    asyncio.run(_test())


def test_doctor_view_install_button_visibility():
    async def _test():
        doctor_service = DoctorService()
        view = DoctorView(doctor_service=doctor_service)

        # Mock check_environment with missing xcode-select
        items_missing = [
            DoctorCheckItem(name="codesign", passed=False, details="Not found"),
            DoctorCheckItem(name="xcode-select", passed=False, details="Not found"),
            DoctorCheckItem(name="PlistBuddy", passed=True, details="/usr/libexec/PlistBuddy"),
        ]
        with patch.object(doctor_service, "check_environment", new=AsyncMock(return_value=items_missing)):
            await view.run_checks()
            assert view.btn_install_xcode.style.visibility == "visible"

        # Mock check_environment with all passing
        items_passed = [
            DoctorCheckItem(name="codesign", passed=True, details="/usr/bin/codesign"),
            DoctorCheckItem(name="xcode-select", passed=True, details="/Library/Developer/CommandLineTools"),
            DoctorCheckItem(name="PlistBuddy", passed=True, details="/usr/libexec/PlistBuddy"),
        ]
        with patch.object(doctor_service, "check_environment", new=AsyncMock(return_value=items_passed)):
            await view.run_checks()
            assert view.btn_install_xcode.style.visibility == "hidden"

    asyncio.run(_test())


def test_doctor_view_action_install_xcode():
    async def _test():
        doctor_service = DoctorService()
        mock_app = MagicMock()
        mock_app.main_window.info_dialog = AsyncMock()

        view = DoctorView(doctor_service=doctor_service, app=mock_app)

        with patch.object(doctor_service, "trigger_xcode_install", new=AsyncMock(return_value=(True, "launched"))) as mock_trigger:
            await view.action_install_xcode()
            assert mock_trigger.called
            assert mock_app.main_window.info_dialog.called

    asyncio.run(_test())



def test_probe_view_display_result(tmp_path):
    async def _test():
        probe_service = ProbeService()
        recipe_service = RecipeService(custom_recipes_dir=tmp_path / "recipes")
        view = ProbeView(probe_service=probe_service, recipe_service=recipe_service)

        mock_probe_result = ProbeResult(
            app_info=AppInfo(
                path=Path("/Applications/ATBCmder.app"),
                bundle_id="com.example.atbcmder",
                app_name="ATBCmder",
                executable=Path("/Applications/ATBCmder.app/Contents/MacOS/ATBCmder"),
                has_sandbox=True,
            ),
            has_sandbox=True,
            frameworks=[],
            strategy="hard_clone",
            reason="Sandboxed native app",
            recipe=Recipe(
                bundle_id="com.example.atbcmder",
                app_name="ATBCmder",
                strategy="hard_clone",
                strip_sandbox=True,
            ),
        )

        with patch.object(probe_service, "probe_app", new=AsyncMock(return_value=mock_probe_result)):
            view.input_path.value = "/Applications/ATBCmder.app"
            await view.do_probe()

            assert "ATBCmder" in view.label_app_name.text
            assert "com.example.atbcmder" in view.label_bundle_id.text
            assert "Hard Clone" in view.label_strategy.text or "hard_clone" in view.label_strategy.text
            assert view.btn_save_recipe.enabled is True

            # Test saving probed recipe to custom recipes
            await view.save_probed_recipe()
            assert (tmp_path / "recipes" / "com.example.atbcmder.yaml").exists()

    asyncio.run(_test())
