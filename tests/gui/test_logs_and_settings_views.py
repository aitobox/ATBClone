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

        assert "ATBClone" in view.input_base_dir.value

        with patch("subprocess.Popen") as mock_popen:
            view.on_open_data_dir_in_finder(None)
            await asyncio.sleep(0.01)
            open_calls = [c for c in mock_popen.call_args_list if c[0] and isinstance(c[0][0], list) and c[0][0][0] == "open"]
            assert len(open_calls) >= 1
            args = open_calls[0][0][0]
            assert args[0] == "open"

    asyncio.run(_test())


def test_settings_view_root_dir_sync_subdirectories(tmp_path):
    view = SettingsView()
    custom_root = tmp_path / "CustomATB"
    view.input_base_dir.value = str(custom_root)

    # Subdirectory labels should automatically reflect custom root
    assert str(custom_root / "Apps") in view.label_apps_dir.text
    assert str(custom_root / "Data") in view.label_data_dir.text


def test_settings_minimize_to_tray_switch(tmp_path, monkeypatch):
    from atbclone.core import config
    from atbclone.core.config import set_config_value, get_config_value

    test_cfg_file = tmp_path / "config.yaml"
    monkeypatch.setattr(config, "DEFAULT_CONFIG_FILE", test_cfg_file)
    monkeypatch.setattr(config, "DEFAULT_ATB_DIR", tmp_path)

    set_config_value("minimize_to_tray", True)
    mock_app = MagicMock()
    mock_app.tray_service = MagicMock()
    view = SettingsView(app=mock_app)
    assert hasattr(view, "switch_minimize_to_tray")
    assert view.switch_minimize_to_tray.value is True

    # Test toggling switch to False disables tray service, ensures dock visible, and updates config
    with patch("atbclone.gui.app.set_macos_dock_visible") as mock_dock_vis:
        view.switch_minimize_to_tray.value = False
        assert get_config_value("minimize_to_tray") is False
        mock_app.tray_service.disable.assert_called_once()
        mock_dock_vis.assert_called_with(True)

    # Test toggling switch to True enables tray service and updates config
    view.switch_minimize_to_tray.value = True
    assert get_config_value("minimize_to_tray") is True
    mock_app.tray_service.enable.assert_called_once()


def test_settings_view_labels_rendered_correctly():
    """Verify that settings view labels render real paths without placeholder literals like {dir} or {path}."""
    from atbclone.core.config import DEFAULT_ATB_DIR, DEFAULT_APPS_DIR, DEFAULT_DATA_DIR
    from atbclone.core.i18n import set_language

    for lang in ("zh", "en", "zh_TW", "ja", "ko", "de", "fr", "ru", "es"):
        set_language(lang)
        view = SettingsView()

        # Find all label widgets in view hierarchy
        labels = []

        def _collect_labels(widget):
            if isinstance(widget, toga.Label):
                labels.append(widget.text)
            if hasattr(widget, "children"):
                for c in widget.children:
                    _collect_labels(c)
            if hasattr(widget, "content") and widget.content and widget.content is not widget:
                _collect_labels(widget.content)

        _collect_labels(view)

        # Ensure no label has unresolved placeholders
        for text in labels:
            assert "{dir}" not in text, f"Found unformatted {{dir}} in '{text}' ({lang})"
            assert "{path}" not in text, f"Found unformatted {{path}} in '{text}' ({lang})"
            assert "{ver}" not in text, f"Found unformatted {{ver}} in '{text}' ({lang})"
            assert "{version}" not in text, f"Found unformatted {{version}} in '{text}' ({lang})"

        # Ensure directory paths are present
        joined_texts = "\n".join(labels)
        assert str(DEFAULT_ATB_DIR) in joined_texts
        assert str(DEFAULT_APPS_DIR) in joined_texts
        assert str(DEFAULT_DATA_DIR) in joined_texts



