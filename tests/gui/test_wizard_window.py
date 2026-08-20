import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from atbclone.core.models import AppInfo
from atbclone.recipes.models import Recipe
from atbclone.gui.services.clone_service import CloneService
from atbclone.gui.services.probe_service import ProbeService
from atbclone.gui.windows.wizard import WizardWindow


def test_wizard_window_navigation(tmp_path):
    async def _test():
        clone_service = CloneService(state_file=tmp_path / "clones.yaml")
        probe_service = ProbeService()

        wizard = WizardWindow(clone_service=clone_service, probe_service=probe_service)
        assert wizard.current_step == 1
        assert wizard.btn_prev.enabled is False

        # Mock app info for Step 1
        wizard.input_app_path.value = "/Applications/WeChat.app"
        mock_info = AppInfo(
            path=Path("/Applications/WeChat.app"),
            bundle_id="com.tencent.xinWeChat",
            app_name="WeChat",
            executable=Path("/Applications/WeChat.app/Contents/MacOS/WeChat"),
            has_sandbox=False,
        )

        with patch("atbclone.core.app_inspector.AppInspector.inspect", return_value=mock_info):
            await wizard.go_next()
            assert wizard.current_step == 2
            assert wizard.app_info is not None
            assert wizard.app_info.bundle_id == "com.tencent.xinWeChat"

            # Step 2 -> 3
            await wizard.go_next()
            assert wizard.current_step == 3
            assert wizard.input_clone_name.value != ""

            # Step 3 -> 4
            await wizard.go_next()
            assert wizard.current_step == 4

            # Step 4 -> 5
            await wizard.go_next()
            assert wizard.current_step == 5

            # Step 5 -> 6
            await wizard.go_next()
            assert wizard.current_step == 6

            # Step 6 -> 7
            await wizard.go_next()
            assert wizard.current_step == 7
            assert wizard.btn_next.text == "🚀 Clone Now"

    asyncio.run(_test())


def test_wizard_browse_handlers():
    async def _test():
        wizard = WizardWindow()
        mock_open = AsyncMock(return_value=Path("/Applications/Safari.app"))
        mock_folder = AsyncMock(return_value=Path("/Users/test/Applications"))

        with patch.object(wizard.app.main_window, "open_file_dialog", mock_open), \
             patch.object(wizard.app.main_window, "select_folder_dialog", mock_folder):
            await wizard._on_browse_app(None)
            assert wizard.input_app_path.value == "/Applications/Safari.app"
            mock_open.assert_called_once_with(
                title="Select macOS Application",
                file_types=["app"],
                initial_directory=Path("/Applications"),
            )

            await wizard._on_browse_dest(None)
            assert wizard.input_dest_dir.value == "/Users/test/Applications"

            await wizard._on_browse_data(None)
            assert wizard.input_data_dir.value == "/Users/test/Applications"

    asyncio.run(_test())


def test_wizard_name_auto_sync_and_manual_override():
    wizard = WizardWindow()

    # 1. Typing in clone_name automatically updates display_name
    wizard.input_clone_name.value = "GoogleSijidege"
    assert wizard.input_display_name.value == "GoogleSijidege"

    # 2. Typing a further modification to clone_name keeps syncing
    wizard.input_clone_name.value = "GoogleSijidege2"
    assert wizard.input_display_name.value == "GoogleSijidege2"

    # 3. User manually overrides display_name
    wizard.input_display_name.value = "Custom Google Name"
    assert wizard.input_clone_name.value == "GoogleSijidege2"
    assert wizard.input_display_name.value == "Custom Google Name"

    # 4. Editing clone_name does NOT overwrite the custom display_name
    wizard.input_clone_name.value = "GoogleSijidege3"
    assert wizard.input_clone_name.value == "GoogleSijidege3"
    assert wizard.input_display_name.value == "Custom Google Name"

    # 5. Resetting display_name back to match clone_name re-enables sync
    wizard.input_display_name.value = "GoogleSijidege3"
    wizard.input_clone_name.value = "GoogleSijidege4"
    assert wizard.input_display_name.value == "GoogleSijidege4"
