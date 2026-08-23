import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from atbclone.core.state import CloneRecord
from atbclone.recipes.models import ProxyConfig
from atbclone.gui.services.clone_service import CloneService
from atbclone.gui.views.clone_list import CloneListView
from atbclone.gui.windows.clone_detail import CloneDetailWindow
from atbclone.gui.windows.clone_edit import CloneEditWindow


def test_clone_detail_window():
    record = CloneRecord(
        clone_name="WeChat2",
        source_app="WeChat",
        source_path="/Applications/WeChat.app",
        bundle_id="com.tencent.xinWeChat",
        strategy="hard_clone",
        dest_path="/Users/test/Applications/WeChat2.app",
        data_dir="/Users/test/ATBClone/Data/WeChat2",
        created_at="2026-08-19T20:00:00Z",
        proxy_enabled=True,
        proxy_summary="http://127.0.0.1:7890",
        new_bundle_id="com.tencent.xinWeChat.clone1",
    )
    window = CloneDetailWindow(record=record)
    assert window.label_clone_name.text == "WeChat2"
    assert "com.tencent.xinWeChat" in window.label_bundle_id.text
    assert "http://127.0.0.1:7890" in window.label_proxy.text


def test_clone_edit_window_save():
    record = CloneRecord(
        clone_name="WeChat2",
        source_app="WeChat",
        source_path="/Applications/WeChat.app",
        bundle_id="com.tencent.xinWeChat",
        strategy="hard_clone",
        dest_path="/Users/test/Applications/WeChat2.app",
        data_dir="/Users/test/ATBClone/Data/WeChat2",
        created_at="2026-08-19T20:00:00Z",
        proxy_enabled=False,
        proxy_summary="",
        new_bundle_id="com.tencent.xinWeChat.clone1",
    )
    on_save = AsyncMock()
    window = CloneEditWindow(record=record, on_save=on_save)

    window.switch_proxy.value = True
    window.select_proxy_type.value = "socks5"
    window.input_proxy_host.value = "127.0.0.1"
    window.input_proxy_port.value = "1080"

    updated = window.get_updated_record()
    assert updated.proxy_enabled is True
    assert "socks5://127.0.0.1:1080" in updated.proxy_summary


def test_clone_list_view_refresh(tmp_path):
    async def _test():
        state_file = tmp_path / "clones.yaml"
        service = CloneService(state_file=state_file)
        record = CloneRecord(
            clone_name="TG2",
            source_app="Telegram",
            source_path="/Applications/Telegram.app",
            bundle_id="ru.keepcoder.Telegram",
            strategy="hard_clone",
            dest_path=str(tmp_path / "TG2.app"),
            data_dir=str(tmp_path / "data"),
            created_at="2026-08-19T00:00:00Z",
        )
        service.state_manager.add(record)

        view = CloneListView(clone_service=service)
        await view.refresh_clones()
        assert len(view._raw_clones) == 1
        assert view.view_mode == "list"
        assert len(view.table.data) == 1

        # Toggle to grid mode
        view.on_view_mode_changed("grid")
        assert view.view_mode == "grid"

        # Search filter
        view.on_search_query_changed("NotMatching")
        assert len(view._filtered_clones) == 0

        view.on_search_query_changed("TG")
        assert len(view._filtered_clones) == 1

        # Clear search and test strategy filter
        view.on_search_query_changed("")
        view.on_filter_changed(CloneListView.FILTER_SOFT)
        assert len(view._filtered_clones) == 0

        view.on_filter_changed(CloneListView.FILTER_HARD)
        assert len(view._filtered_clones) == 1

        # Sort
        view.on_sort_changed(CloneListView.SORT_NAME)
        assert len(view._filtered_clones) == 1

        # Table selection enables open_dir button
        with patch.object(view, "get_selected_record", return_value=record):
            view.on_table_select(view.table)
            assert view.btn_launch_table.enabled is True
            assert view.btn_open_dir_table.enabled is True

        # Deselect disables open_dir button
        with patch.object(view, "get_selected_record", return_value=None):
            view.on_table_select(view.table)
            assert view.btn_launch_table.enabled is False
            assert view.btn_open_dir_table.enabled is False

        # Test on_open_clone_dir when file exists
        (tmp_path / "TG2.app").mkdir(exist_ok=True)
        with patch("subprocess.Popen") as mock_popen:
            await view.on_open_clone_dir(record)
            mock_popen.assert_called_once_with(["open", "-R", str(tmp_path / "TG2.app")])

        # Test on_update_clone with busy lock guard
        with patch.object(service, "update_clone", new_callable=AsyncMock) as mock_up:
            await view.on_update_clone(record)
            mock_up.assert_awaited_once_with("TG2")

        # When already busy, on_update_clone should no-op
        view._busy_clones.add("TG2")
        with patch.object(service, "update_clone", new_callable=AsyncMock) as mock_up:
            await view.on_update_clone(record)
            mock_up.assert_not_awaited()
        view._busy_clones.clear()

        # Test double-click (on_activate) on table row opens edit window
        with patch.object(view, "on_edit_clone", new_callable=AsyncMock) as mock_edit:
            await view.on_table_activate(view.table, row=view.table.data[0])
            mock_edit.assert_awaited_once_with(record)

    asyncio.run(_test())


def test_clone_list_view_table_header_sort():
    view = CloneListView()
    view._raw_clones = [
        CloneRecord(clone_name="Beta", source_app="App2", source_path="/Applications/App2.app", bundle_id="b.app", strategy="soft_clone", dest_path="/p2", data_dir="/d2", created_at="2026-08-20T10:00:00"),
        CloneRecord(clone_name="Alpha", source_app="App1", source_path="/Applications/App1.app", bundle_id="a.app", strategy="hard_clone", dest_path="/p1", data_dir="/d1", created_at="2026-08-21T10:00:00"),
    ]
    view._apply_filter()

    # Sort column 0 (Name) ASC
    view.on_table_header_sort(0, view.table.columns[0], ascending=True)
    assert [r.clone_name for r in view._filtered_clones] == ["Alpha", "Beta"]
    assert view.top_bar.select_sort.value == view.sort_name

    # Sort column 0 (Name) DESC
    view.on_table_header_sort(0, view.table.columns[0], ascending=False)
    assert [r.clone_name for r in view._filtered_clones] == ["Beta", "Alpha"]

    # Sort column 1 (Source App) ASC
    view.on_table_header_sort(1, view.table.columns[1], ascending=True)
    assert [r.source_app for r in view._filtered_clones] == ["App1", "App2"]

    # Sort column 2 (Strategy) ASC
    view.on_table_header_sort(2, view.table.columns[2], ascending=True)
    assert [r.strategy for r in view._filtered_clones] == ["hard_clone", "soft_clone"]

    # Sort column 4 (Created At) DESC
    view.on_table_header_sort(4, view.table.columns[4], ascending=False)
    assert [r.clone_name for r in view._filtered_clones] == ["Alpha", "Beta"]
    assert view.top_bar.select_sort.value == view.sort_newest

    # Sort column 4 (Created At) ASC
    view.on_table_header_sort(4, view.table.columns[4], ascending=True)
    assert [r.clone_name for r in view._filtered_clones] == ["Beta", "Alpha"]
    assert view.top_bar.select_sort.value == view.sort_oldest



