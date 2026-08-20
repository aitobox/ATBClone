import asyncio
from unittest.mock import MagicMock, patch
from pathlib import Path
import toga
from atbclone.gui.views.logs_view import LogsView
from atbclone.gui.views.settings_view import SettingsView


def test_logs_view_logging_and_filtering():
    view = LogsView()
    assert "initialized" in view.log_text.value

    view.log_info("Created clone WeChat2")
    view.log_error("Failed to clone QQ")
    assert "WeChat2" in view.log_text.value
    assert "QQ" in view.log_text.value

    # Filter
    view.on_filter_logs("QQ")
    assert "QQ" in view.log_text.value
    assert "WeChat2" not in view.log_text.value

    # Clear
    view.on_clear_logs(None)
    assert view.log_text.value == ""


def test_settings_view_open_finder_and_save():
    async def _test():
        mock_app = MagicMock()
        mock_app.main_window = MagicMock()
        view = SettingsView(app=mock_app)

        assert ".atbclone" in view.input_base_dir.value

        with patch("subprocess.Popen") as mock_popen:
            view.on_open_data_dir_in_finder(None)
            await asyncio.sleep(0.01)
            mock_popen.assert_called_once()
            args = mock_popen.call_args[0][0]
            assert args[0] == "open"

    asyncio.run(_test())
