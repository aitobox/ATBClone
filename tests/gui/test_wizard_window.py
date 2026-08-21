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
            assert "Clone" in wizard.btn_next.text or "克隆" in wizard.btn_next.text or "🚀" in wizard.btn_next.text

    asyncio.run(_test())


def test_wizard_browse_handlers():
    async def _test():
        from atbclone.core.i18n import t
        wizard = WizardWindow()
        mock_open = AsyncMock(return_value=Path("/Applications/Safari.app"))
        mock_folder = AsyncMock(return_value=Path("/Users/test/Applications"))

        with patch.object(wizard, "open_file_dialog", mock_open), \
             patch.object(wizard, "select_folder_dialog", mock_folder):
            await wizard._on_browse_app(None)
            assert wizard.input_app_path.value == "/Applications/Safari.app"
            mock_open.assert_called_once_with(
                title=t("dialog_select_app_title"),
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


def test_wizard_execute_clone_bundle_id_resolution(tmp_path: Path):
    async def _test():
        clone_service = CloneService(state_file=tmp_path / "clones.yaml")
        wizard = WizardWindow(clone_service=clone_service)

        wizard.app_info = AppInfo(
            path=Path("/Applications/WeChat.app"),
            bundle_id="com.tencent.xinWeChat",
            app_name="WeChat",
            executable=Path("/Applications/WeChat.app/Contents/MacOS/WeChat"),
            has_sandbox=False,
        )
        wizard.recipe = Recipe(bundle_id="com.tencent.xinWeChat", app_name="WeChat", strategy="hard_clone")
        wizard.input_clone_name.value = "WeChat3"
        wizard.input_dest_dir.value = str(tmp_path / "Apps")
        wizard.input_data_dir.value = str(tmp_path / "Data" / "WeChat3")

        created_task = None
        async def mock_create_clone(task):
            nonlocal created_task
            created_task = task
            return MagicMock()

        wizard.clone_service.create_clone = mock_create_clone
        wizard.info_dialog = AsyncMock()

        await wizard._execute_clone()
        assert created_task is not None
        assert created_task.new_bundle_id == "com.tencent.xinWeChat.atbclone.3"

    asyncio.run(_test())


def test_wizard_execute_clone_ios_app_shows_error(tmp_path: Path):
    async def _test():
        clone_service = CloneService(state_file=tmp_path / "clones.yaml")
        wizard = WizardWindow(clone_service=clone_service)

        wizard.app_info = AppInfo(
            path=Path("/Applications/小宇宙.app"),
            bundle_id="app.podcast.cosmos",
            app_name="小宇宙",
            executable=Path("/Applications/小宇宙.app/Wrapper/Podcast.app/Podcast"),
            has_sandbox=True,
            is_ios_app=True,
        )
        wizard.recipe = Recipe(bundle_id="app.podcast.cosmos", app_name="小宇宙", strategy="hard_clone")
        wizard.input_clone_name.value = "小宇宙2"
        wizard.input_dest_dir.value = str(tmp_path / "Apps")
        wizard.input_data_dir.value = str(tmp_path / "Data" / "小宇宙2")

        mock_create = AsyncMock()
        wizard.clone_service.create_clone = mock_create
        wizard.error_dialog = AsyncMock()

        await wizard._execute_clone()
        mock_create.assert_not_called()
        wizard.error_dialog.assert_called_once()
        error_title, error_message = wizard.error_dialog.call_args[0]
        assert "iOS on Mac Wrapper" in error_message or "不支持 iOS on Mac Wrapper 应用" in error_message

    asyncio.run(_test())


def test_wizard_step1_ios_app_shows_error_dialog(tmp_path: Path):
    async def _test():
        clone_service = CloneService(state_file=tmp_path / "clones.yaml")
        wizard = WizardWindow(clone_service=clone_service)
        wizard.input_app_path.value = "/Applications/小宇宙.app"
        wizard.error_dialog = AsyncMock()

        mock_info = AppInfo(
            path=Path("/Applications/小宇宙.app"),
            bundle_id="app.podcast.cosmos",
            app_name="小宇宙",
            executable=Path("/Applications/小宇宙.app/Wrapper/Podcast.app/Podcast"),
            has_sandbox=True,
            is_ios_app=True,
        )

        with patch("atbclone.core.app_inspector.AppInspector.inspect", return_value=mock_info):
            await wizard.go_next()
            assert wizard.current_step == 1
            wizard.error_dialog.assert_called_once()
            _, err_msg = wizard.error_dialog.call_args[0]
            assert "iOS on Mac Wrapper" in err_msg or "不支持 iOS on Mac Wrapper 应用" in err_msg

    asyncio.run(_test())


