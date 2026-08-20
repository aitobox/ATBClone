import asyncio
from pathlib import Path
from unittest.mock import MagicMock, patch
import toga
from atbclone.core.logger import get_logger, read_logs, setup_logging
from atbclone.gui.views.logs_view import LogsView
from atbclone.gui.views.settings_view import SettingsView


def test_logs_view_file_backed_and_live_sync(tmp_path):
    log_file = tmp_path / "test_logsview.log"
    setup_logging(log_file=log_file)
    logger = get_logger("ui_test")
    logger.info("Pre-existing log entry on disk")

    view = LogsView()
    # Verify disk content loaded
    assert "Pre-existing log entry on disk" in view.log_text.value

    # Verify live streaming
    logger.info("New live streamed event")
    assert "New live streamed event" in view.log_text.value

    # Verify filter
    view.on_filter_logs("live")
    assert "New live streamed event" in view.log_text.value
    assert "Pre-existing" not in view.log_text.value

    # Reset filter
    view.on_filter_logs("")
    assert "Pre-existing" in view.log_text.value

    # Verify clear
    view.on_clear_logs(None)
    assert "Pre-existing" not in view.log_text.value
    assert "Log file cleared by user" in view.log_text.value
    assert "Log file cleared by user" in read_logs(log_file=log_file)


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
