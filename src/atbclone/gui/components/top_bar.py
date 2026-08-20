"""Unified Top Header Bar component matching modern macOS layout specifications."""

from typing import Callable, List, Optional
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER
from atbclone.gui.theme import Theme


class TopHeaderBar(toga.Box):
    """Top header panel with a large section title and a compact pinned action toolbar."""

    VIEW_GRID = "🔲 卡片视图"
    VIEW_LIST = "📋 列表视图"

    def __init__(
        self,
        title: Optional[str] = None,
        action_label: Optional[str] = "+ 新建分身",
        on_action: Optional[Callable[[toga.Button], None]] = None,
        search_placeholder: str = "🔍 搜索...",
        on_search: Optional[Callable[[str], None]] = None,
        filter_items: Optional[List[str]] = None,
        on_filter_change: Optional[Callable[[str], None]] = None,
        sort_items: Optional[List[str]] = None,
        on_sort_change: Optional[Callable[[str], None]] = None,
        view_modes: Optional[List[str]] = None,
        on_view_change: Optional[Callable[[str], None]] = None,
        on_refresh: Optional[Callable[[toga.Button], None]] = None,
    ):
        super().__init__(style=Pack(direction=COLUMN, margin=(16, 20, 10, 20)))
        self.on_search_cb = on_search
        self.on_view_change_cb = on_view_change
        self.on_filter_cb = on_filter_change
        self.on_sort_cb = on_sort_change
        self.current_view_mode: str = "grid"

        # 1. Big Feature Area Section Title Row (大标题 + 紧随其后的新建/操作主按钮)
        title_row = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin_bottom=10))
        if title:
            self.label_title = toga.Label(
                title,
                style=Pack(font_weight="bold", font_size=20, margin_right=12, color=Theme.TEXT_PRIMARY),
            )
            title_row.add(self.label_title)
        else:
            self.label_title = None

        if on_action and action_label:
            self.btn_action = toga.Button(
                action_label,
                on_press=on_action,
                style=Pack(font_weight="bold", height=32),
            )
            title_row.add(self.btn_action)
        else:
            self.btn_action = None

        self.add(title_row)

        # Divider separating title row from action toolbar
        self.divider = toga.Divider(style=Pack(margin=(4, 0, 14, 0)))
        self.add(self.divider)

        # 2. Pinned Compact Action Toolbar Row
        toolbar_row = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin_bottom=2))

        # (a) Search input (only add when on_search callback is provided)
        if on_search:
            self.input_search = toga.TextInput(
                placeholder=search_placeholder,
                on_change=self._handle_search,
                style=Pack(width=180, margin_right=10),
            )
            toolbar_row.add(self.input_search)
        else:
            self.input_search = None

        # (b) Filter dropdown
        if filter_items and on_filter_change:
            self.select_filter = toga.Selection(
                items=filter_items,
                on_change=self._handle_filter,
                style=Pack(width=140, margin_right=10),
            )
            toolbar_row.add(self.select_filter)

        # (c) Sort dropdown
        if sort_items and on_sort_change:
            self.select_sort = toga.Selection(
                items=sort_items,
                on_change=self._handle_sort,
                style=Pack(width=130, margin_right=10),
            )
            toolbar_row.add(self.select_sort)

        # (d) View Mode dropdown (卡片视图 / 列表视图 下拉单选框)
        if on_view_change:
            view_items = view_modes or [self.VIEW_GRID, self.VIEW_LIST]
            self.select_view = toga.Selection(
                items=view_items,
                on_change=self._handle_view_change,
                style=Pack(width=115, margin_right=10),
            )
            toolbar_row.add(self.select_view)

        # (e) Flexible horizontal spacer
        toolbar_row.add(toga.Box(style=Pack(flex=1)))

        # (f) Refresh Button at far right
        if on_refresh:
            self.btn_refresh = toga.Button("🔄 刷新", on_press=on_refresh, style=Pack(width=72))
            toolbar_row.add(self.btn_refresh)

        if len(toolbar_row.children) > 1 or (len(toolbar_row.children) == 1 and on_refresh):
            self.add(toolbar_row)

    def _handle_search(self, widget: toga.TextInput):
        if self.on_search_cb:
            self.on_search_cb(widget.value.strip())

    def _handle_filter(self, widget: toga.Selection):
        if self.on_filter_cb and widget.value is not None:
            self.on_filter_cb(str(widget.value))

    def _handle_sort(self, widget: toga.Selection):
        if self.on_sort_cb and widget.value is not None:
            self.on_sort_cb(str(widget.value))

    def _handle_view_change(self, widget: toga.Selection):
        if widget.value is not None:
            val_str = str(widget.value)
            mode = "list" if ("列表" in val_str or "List" in val_str) else "grid"
            self.current_view_mode = mode
            if self.on_view_change_cb:
                self.on_view_change_cb(mode)

    def set_view_mode(self, mode: str):
        """Programmatically switch view mode."""
        self.current_view_mode = mode
        if hasattr(self, "select_view"):
            for item in self.select_view.items:
                item_val = getattr(item, "value", item)
                item_str = str(item_val)
                if mode == "list" and ("列表" in item_str or "List" in item_str):
                    self.select_view.value = item_val
                    break
                elif mode == "grid" and ("卡片" in item_str or "Grid" in item_str):
                    self.select_view.value = item_val
                    break
        if self.on_view_change_cb:
            self.on_view_change_cb(mode)

    def update_title(self, new_title: str):
        if self.label_title:
            self.label_title.text = new_title
