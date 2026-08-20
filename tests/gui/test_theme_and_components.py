from unittest.mock import MagicMock
from atbclone.gui.theme import Theme
from atbclone.gui.components.top_bar import TopHeaderBar


def test_theme_constants():
    assert Theme.BG_WINDOW == "#F5F5F7"
    assert Theme.BG_SIDEBAR == "#ECECF0"
    assert Theme.ACCENT_BLUE == "#007AFF"
    assert Theme.BG_CARD == "#FFFFFF"


def test_top_header_bar_initialization():
    on_search = MagicMock()
    on_view_change = MagicMock()
    on_action = MagicMock()

    bar = TopHeaderBar(
        title="全部应用 > 分身管理 (3)",
        search_placeholder="搜索应用...",
        on_search=on_search,
        on_view_change=on_view_change,
        on_action=on_action,
        action_label="+ 新建分身",
    )
    assert bar.label_title.text == "全部应用 > 分身管理 (3)"
    assert bar.btn_action.text == "+ 新建分身"
    assert bar.input_search.placeholder == "搜索应用..."

    bar.input_search.value = "WeChat"
    on_search.assert_called_with("WeChat")

    bar.update_title("全部应用 > 分身管理 (4)")
    assert bar.label_title.text == "全部应用 > 分身管理 (4)"

    # Test with filter and sort callbacks
    on_filter = MagicMock()
    on_sort = MagicMock()
    bar2 = TopHeaderBar(
        search_placeholder="🔍 搜索...",
        filter_items=["全部", "Hard", "Soft"],
        on_filter_change=on_filter,
        sort_items=["最新", "最早"],
        on_sort_change=on_sort,
        on_view_change=on_view_change,
    )
    assert bar2.current_view_mode == "list"
    bar2.set_view_mode("grid")
    assert bar2.current_view_mode == "grid"
    on_view_change.assert_called_with("grid")

