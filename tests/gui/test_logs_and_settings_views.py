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
    logger.info("Log entry 1 (Oldest)")
    logger.info("Log entry 2 (Older)")

    view = LogsView()
    # Verify disk content loaded in reverse chronological order (newest on top)
    assert "Log entry 1 (Oldest)" in view.log_text.value
    assert "Log entry 2 (Older)" in view.log_text.value
    assert view.log_text.value.index("Log entry 2 (Older)") < view.log_text.value.index("Log entry 1 (Oldest)")

    # Verify live streaming prepends to top
    logger.info("Log entry 3 (Newest live)")
    assert "Log entry 3 (Newest live)" in view.log_text.value
    assert view.log_text.value.index("Log entry 3 (Newest live)") < view.log_text.value.index("Log entry 2 (Older)")

    # Verify filter
    view.on_filter_logs("live")
    assert "Log entry 3 (Newest live)" in view.log_text.value
    assert "Log entry 1" not in view.log_text.value

    # Reset filter
    view.on_filter_logs("")
    assert "Log entry 1 (Oldest)" in view.log_text.value
    assert view.log_text.value.index("Log entry 3 (Newest live)") < view.log_text.value.index("Log entry 1 (Oldest)")

    # Verify clear
    view.on_clear_logs(None)
    assert "Log entry 1" not in view.log_text.value
    assert "Log file cleared by user" in view.log_text.value
    assert "Log file cleared by user" in read_logs(log_file=log_file)



def test_settings_view_open_finder_and_save():
    mock_app = MagicMock()
    mock_app.main_window = MagicMock()
    view = SettingsView(app=mock_app)

    assert "ATBClone" in view.input_base_dir.value

    with patch("subprocess.Popen") as mock_popen:
        view.on_open_data_dir_in_finder(None)
        open_calls = [c for c in mock_popen.call_args_list if c[0] and isinstance(c[0][0], list) and c[0][0][0] == "open"]
        assert len(open_calls) >= 1
        args = open_calls[0][0][0]
        assert args[0] == "open"


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


def test_settings_view_default_proxy_auth_keychain(tmp_path, monkeypatch):
    async def _test():
        from unittest.mock import AsyncMock
        from atbclone.core import config
        from atbclone.core.config import get_config_value
        from atbclone.core.keychain import (
            set_mock_mode,
            clear_mock_storage,
            get_default_proxy_password,
        )

        set_mock_mode(True)
        clear_mock_storage()

        test_cfg_file = tmp_path / "config.yaml"
        monkeypatch.setattr(config, "DEFAULT_CONFIG_FILE", test_cfg_file)
        monkeypatch.setattr(config, "DEFAULT_ATB_DIR", tmp_path)

        mock_app = MagicMock()
        mock_app.main_window = MagicMock()
        mock_app.main_window.info_dialog = AsyncMock()

        view = SettingsView(app=mock_app)
        assert view.switch_proxy.value is False
        assert view.switch_proxy_auth.value is False

        # Configure proxy and auth
        view.switch_proxy.value = True
        view.select_proxy_type.value = "https"
        view.input_proxy_host.value = "proxy.corp.internal"
        view.input_proxy_port.value = "8080"
        view.switch_proxy_auth.value = True
        view.input_proxy_user.value = "global_user"
        view.input_proxy_pass.value = "global_pass_888"

        await view.on_save_settings(None)

        # Verify config saved
        cfg = get_config_value("default_proxy", {})
        assert cfg.get("enabled") is True
        assert cfg.get("type") == "https"
        assert cfg.get("host") == "proxy.corp.internal"
        assert cfg.get("port") == 8080
        assert cfg.get("username") == "global_user"
        # Password must NOT be in config dict or file
        assert "password" not in cfg
        assert "global_pass_888" not in test_cfg_file.read_text(encoding="utf-8")

        # Password must be in Keychain
        assert get_default_proxy_password() == "global_pass_888"

        # Reopen SettingsView and verify prefill
        view2 = SettingsView(app=mock_app)
        assert view2.switch_proxy.value is True
        assert view2.select_proxy_type.value == "https"
        assert view2.input_proxy_host.value == "proxy.corp.internal"
        assert view2.input_proxy_port.value == "8080"
        assert view2.switch_proxy_auth.value is True
        assert view2.input_proxy_user.value == "global_user"
        assert view2.input_proxy_pass.value == "global_pass_888"

        # Turn off proxy auth and save
        view2.switch_proxy_auth.value = False
        await view2.on_save_settings(None)

        assert get_default_proxy_password() is None

    asyncio.run(_test())


def test_settings_view_proxy_validation_errors(tmp_path: Path, monkeypatch):
    async def _test():
        from unittest.mock import AsyncMock
        from atbclone.core import config
        test_cfg_file = tmp_path / "config.yaml"
        monkeypatch.setattr(config, "DEFAULT_CONFIG_FILE", test_cfg_file)
        monkeypatch.setattr(config, "DEFAULT_ATB_DIR", tmp_path)

        mock_app = MagicMock()
        mock_app.main_window = MagicMock()
        mock_app.main_window.error_dialog = AsyncMock()
        mock_app.main_window.info_dialog = AsyncMock()

        view = SettingsView(app=mock_app)
        view.switch_proxy.value = True
        view.input_proxy_port.value = "invalid_port"

        await view.on_save_settings(None)
        mock_app.main_window.error_dialog.assert_awaited_once()
        mock_app.main_window.info_dialog.assert_not_awaited()

        mock_app.main_window.error_dialog.reset_mock()
        view.input_proxy_port.value = "1080"
        view.switch_proxy_auth.value = True
        view.input_proxy_user.value = "user with space"
        await view.on_save_settings(None)
        mock_app.main_window.error_dialog.assert_awaited_once()
        mock_app.main_window.info_dialog.assert_not_awaited()

    asyncio.run(_test())




