from unittest.mock import MagicMock
from atbclone.gui.theme import Theme
from atbclone.gui.components.top_bar import TopHeaderBar


def test_theme_constants_light_mode():
    """Verify Theme tokens reflect the Light palette after apply_mode(False)."""
    Theme.apply_mode(False)
    assert Theme.BG_WINDOW == "#F5F5F7"
    assert Theme.BG_SIDEBAR == "#ECECF0"
    assert Theme.BG_CARD == "#FFFFFF"
    assert Theme.TEXT_PRIMARY == "#1D1D1F"
    assert Theme.TEXT_SECONDARY == "#6E6E73"
    assert Theme.TEXT_TERTIARY == "#6C6C70"
    # Mode-independent tokens remain unchanged
    assert Theme.ACCENT_BLUE == "#007AFF"
    assert Theme.HEIGHT_BTN_PRIMARY == 30
    assert Theme.HEIGHT_BTN_COMPACT == 28
    assert Theme.HEIGHT_INPUT == 28
    assert Theme.CORNER_RADIUS_CARD == 10.0
    assert Theme.BORDER_WIDTH_HAIRLINE == 0.5


def test_theme_constants_dark_mode():
    """Verify Theme tokens reflect the Dark palette after apply_mode(True)."""
    Theme.apply_mode(True)
    assert Theme.BG_WINDOW == "#1C1C1E"
    assert Theme.BG_SIDEBAR == "#2C2C2E"
    assert Theme.BG_CARD == "#2C2C2E"
    assert Theme.TEXT_PRIMARY == "#F5F5F7"
    assert Theme.TEXT_SECONDARY == "#AEAEB2"
    assert Theme.TEXT_TERTIARY == "#8E8E93"
    # Mode-independent tokens remain unchanged
    assert Theme.ACCENT_BLUE == "#007AFF"
    assert Theme.HEIGHT_BTN_PRIMARY == 30
    # Restore Light palette so subsequent tests are unaffected
    Theme.apply_mode(False)



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

