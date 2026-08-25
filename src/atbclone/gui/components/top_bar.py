"""Unified Top Header Bar component matching modern macOS layout specifications."""

from typing import Callable, List, Optional
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER
from atbclone.core.i18n import t
from atbclone.gui.theme import Theme


class TopHeaderBar(toga.Box):
    """Top header panel with a large section title and a compact pinned action toolbar."""

    @classmethod
    def get_view_grid_label(cls) -> str:
        return t("topbar_view_grid")

    @classmethod
    def get_view_list_label(cls) -> str:
        return t("topbar_view_list")

    def __init__(
        self,
        title: Optional[str] = None,
        action_label: Optional[str] = None,
        on_action: Optional[Callable[[toga.Button], None]] = None,
        search_placeholder: Optional[str] = None,
        on_search: Optional[Callable[[str], None]] = None,
        filter_items: Optional[List[str]] = None,
        on_filter_change: Optional[Callable[[str], None]] = None,
        sort_items: Optional[List[str]] = None,
        on_sort_change: Optional[Callable[[str], None]] = None,
        view_modes: Optional[List[str]] = None,
        on_view_change: Optional[Callable[[str], None]] = None,
        on_refresh: Optional[Callable[[toga.Button], None]] = None,
    ):
        super().__init__(style=Pack(direction=COLUMN, margin=(18, 24, 12, 24)))
        self.on_search_cb = on_search
        self.on_view_change_cb = on_view_change
        self.on_filter_cb = on_filter_change
        self.on_sort_cb = on_sort_change
        self.current_view_mode: str = "list"

        if action_label is None and on_action:
            action_label = t("btn_new_clone")
        if search_placeholder is None:
            search_placeholder = t("topbar_search_placeholder")

        # 1. Big Feature Area Section Title Row (大标题 + 紧随其后的新建/操作主按钮)
        title_row = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin_bottom=12))
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
                style=Pack(font_weight="bold", font_size=13, height=30),
            )
            title_row.add(self.btn_action)
        else:
            self.btn_action = None

        self.add(title_row)

        # Divider separating title row from action toolbar
        self.divider = toga.Divider(style=Pack(margin=(2, 0, 12, 0)))
        self.add(self.divider)

        # 2. Pinned Compact Action Toolbar Row
        toolbar_row = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin_bottom=2))

        # (a) Search input (only add when on_search callback is provided)
        if on_search:
            self.input_search = toga.TextInput(
                placeholder=search_placeholder,
                on_change=self._handle_search,
                style=Pack(width=190, margin_right=10),
            )
            toolbar_row.add(self.input_search)
        else:
            self.input_search = None

        # (b) Filter dropdown
        if filter_items and on_filter_change:
            self.select_filter = toga.Selection(
                items=filter_items,
                on_change=self._handle_filter,
                style=Pack(width=150, margin_right=10),
            )
            toolbar_row.add(self.select_filter)

        # (c) Sort dropdown
        if sort_items and on_sort_change:
            self.select_sort = toga.Selection(
                items=sort_items,
                on_change=self._handle_sort,
                style=Pack(width=160, margin_right=10),
            )
            toolbar_row.add(self.select_sort)

        # (d) View Mode dropdown (列表视图 / 卡片视图 下拉单选框)
        if on_view_change:
            view_items = view_modes or [t("topbar_view_list"), t("topbar_view_grid")]
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
            self.btn_refresh = toga.Button(t("topbar_btn_refresh"), on_press=on_refresh, style=Pack(height=28, font_size=13))
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
            list_keywords = ("列表", "清單", "list", "liste", "список", "목록", "リスト", "tabla")
            mode = "list" if any(k in val_str.lower() for k in list_keywords) else "grid"
            self.current_view_mode = mode
            if self.on_view_change_cb:
                self.on_view_change_cb(mode)

    def set_view_mode(self, mode: str):
        """Programmatically switch view mode."""
        self.current_view_mode = mode
        if hasattr(self, "select_view"):
            list_keywords = ("列表", "清單", "list", "liste", "список", "목록", "リスト", "tabla")
            for item in self.select_view.items:
                item_val = getattr(item, "value", item)
                item_str = str(item_val).lower()
                is_list_item = any(k in item_str for k in list_keywords)
                if mode == "list" and is_list_item:
                    self.select_view.value = item_val
                    break
                elif mode == "grid" and not is_list_item:
                    self.select_view.value = item_val
                    break
        if self.on_view_change_cb:
            self.on_view_change_cb(mode)

    def update_title(self, new_title: str):
        if self.label_title:
            self.label_title.text = new_title

