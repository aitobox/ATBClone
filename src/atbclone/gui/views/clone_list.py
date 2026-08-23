"""Cloned Applications Dual-View (Card Grid & Table) View."""

import asyncio
import subprocess
from typing import Optional
from pathlib import Path
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER

from atbclone.core.i18n import t
from atbclone.core.logger import get_logger
from atbclone.core.state import CloneRecord
from atbclone.gui.services.clone_service import CloneService
from atbclone.gui.components.top_bar import TopHeaderBar
from atbclone.gui.components.clone_card import CloneCard
from atbclone.gui.windows.clone_detail import CloneDetailWindow
from atbclone.gui.windows.clone_edit import CloneEditWindow
from atbclone.gui.theme import Theme

logger = get_logger("gui.clone_list")


class CloneListView(toga.Box):
    """View rendering application clones with large section title, top-aligned controls, and dual Card/Table views."""

    FILTER_ALL = "🏷️ 全部策略"
    FILTER_HARD = "⚡️ 物理克隆 (Hard)"
    FILTER_SOFT = "🍃 软包装 (Soft)"
    FILTER_PROXY = "🌐 启用代理"

    SORT_NEWEST = "🔽 最新创建"
    SORT_NAME = "🔽 应用名称 (A-Z)"
    SORT_OLDEST = "🔼 最早创建"

    def __init__(self, clone_service: Optional[CloneService] = None, app: Optional[toga.App] = None):
        super().__init__(style=Pack(direction=COLUMN, flex=1, background_color=Theme.BG_WINDOW))
        self.clone_service = clone_service or CloneService()
        self.app_instance = app
        self._raw_clones: list[CloneRecord] = []
        self._filtered_clones: list[CloneRecord] = []
        self._busy_clones: set[str] = set()
        self.view_mode: str = "list"  # "grid" or "list"
        self.search_query: str = ""

        # Filter and Sort definitions
        self.filter_all = t("view_clones_filter_all")
        self.filter_hard = t("view_clones_filter_hard")
        self.filter_soft = t("view_clones_filter_soft")
        self.filter_proxy = t("view_clones_filter_proxy")

        self.sort_newest = t("view_clones_sort_newest")
        self.sort_name = t("view_clones_sort_name")
        self.sort_oldest = t("view_clones_sort_oldest")

        self.selected_filter: str = self.filter_all
        self.selected_sort: str = self.sort_newest

        # Top Header Bar with big section title and compact pinned toolbar
        self.top_bar = TopHeaderBar(
            title=t("view_clones_title", count=0),
            action_label=t("btn_new_clone"),
            on_action=self.on_action_new_clone,
            search_placeholder=t("view_clones_search_placeholder"),
            on_search=self.on_search_query_changed,
            filter_items=[self.filter_all, self.filter_hard, self.filter_soft, self.filter_proxy],
            on_filter_change=self.on_filter_changed,
            sort_items=[self.sort_newest, self.sort_name, self.sort_oldest],
            on_sort_change=self.on_sort_changed,
            view_modes=[t("topbar_view_list"), t("topbar_view_grid")],
            on_view_change=self.on_view_mode_changed,
            on_refresh=lambda w: asyncio.create_task(self.refresh_clones()),
        )
        self.add(self.top_bar)

        # Content container pinned right below header
        self.content_container = toga.Box(style=Pack(direction=COLUMN, flex=1, margin=(0, 24, 20, 24)))
        self.add(self.content_container)

        # Grid view scroll container & flow box
        self.grid_scroll = toga.ScrollContainer(style=Pack(flex=1), horizontal=False)
        self.grid_box = toga.Box(style=Pack(direction=COLUMN, margin=4))
        self.grid_scroll.content = self.grid_box

        # Table view & action bar
        self.table_box = toga.Box(style=Pack(direction=COLUMN, flex=1))
        self.table = toga.Table(
            columns=[
                t("list_col_name"),
                t("list_col_source_app"),
                t("list_col_strategy"),
                t("list_col_proxy"),
                t("list_col_created_at"),
            ],
            multiple_select=True,
            on_select=self.on_table_select,
            on_activate=self.on_table_activate,
            style=Pack(flex=1),
        )
        self.table.on_header_sort = self.on_table_header_sort
        self.table_box.add(self.table)

        self.btn_launch_table = toga.Button(t("btn_launch"), on_press=lambda w: asyncio.create_task(self.on_launch_clone(self.get_selected_record())), enabled=False, style=Pack(margin_right=6, height=28, font_size=12.5, font_weight="bold"))
        self.btn_open_dir_table = toga.Button(t("btn_open_clone_dir"), on_press=lambda w: asyncio.create_task(self.on_open_clone_dir(self.get_selected_record())), enabled=False, style=Pack(margin_right=6, height=28, font_size=12.5))
        self.btn_update_table = toga.Button(t("btn_update"), on_press=lambda w: asyncio.create_task(self.on_update_clone(self.get_selected_records())), enabled=False, style=Pack(margin_right=6, height=28, font_size=12.5))
        self.btn_edit_table = toga.Button(t("btn_edit"), on_press=lambda w: asyncio.create_task(self.on_edit_clone(self.get_selected_record())), enabled=False, style=Pack(margin_right=6, height=28, font_size=12.5))
        self.btn_detail_table = toga.Button(t("btn_detail"), on_press=lambda w: asyncio.create_task(self.on_detail_clone(self.get_selected_record())), enabled=False, style=Pack(margin_right=6, height=28, font_size=12.5))
        self.btn_delete_table = toga.Button(t("btn_delete"), on_press=lambda w: asyncio.create_task(self.on_delete_clone(self.get_selected_records())), enabled=False, style=Pack(height=28, font_size=12.5))

        actions_box = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin_top=8))
        actions_box.add(self.btn_launch_table)
        actions_box.add(self.btn_open_dir_table)
        actions_box.add(self.btn_update_table)
        actions_box.add(self.btn_edit_table)
        actions_box.add(self.btn_detail_table)
        actions_box.add(self.btn_delete_table)
        self.table_box.add(actions_box)

        # Empty state label
        self.label_empty = toga.Label(
            t("view_clones_empty_hint"),
            style=Pack(margin=(40, 20, 40, 20), font_size=14, color=Theme.TEXT_MUTED),
        )

        self._render_current_view()

    def on_view_mode_changed(self, mode: str):
        self.view_mode = mode
        self._render_current_view()

    def on_search_query_changed(self, query: str):
        self.search_query = query.lower()
        self._apply_filter()

    def on_filter_changed(self, filter_val: str):
        self.selected_filter = filter_val
        self._apply_filter()

    def on_sort_changed(self, sort_val: str):
        self.selected_sort = sort_val
        self._apply_filter()

    def on_table_header_sort(self, col_index: int, column, ascending: bool):
        """Handle header click sorting for Table view and synchronize with toolbar."""
        if col_index == 0:  # Name
            self._filtered_clones.sort(key=lambda r: r.clone_name.lower(), reverse=not ascending)
            if ascending:
                self.selected_sort = self.sort_name
                if hasattr(self.top_bar, "select_sort") and self.top_bar.select_sort:
                    self.top_bar.select_sort.value = self.sort_name
        elif col_index == 1:  # Source App
            self._filtered_clones.sort(key=lambda r: r.source_app.lower(), reverse=not ascending)
        elif col_index == 2:  # Strategy
            self._filtered_clones.sort(key=lambda r: r.strategy.lower(), reverse=not ascending)
        elif col_index == 3:  # Proxy
            self._filtered_clones.sort(key=lambda r: (r.proxy_enabled, r.proxy_summary), reverse=not ascending)
        elif col_index == 4:  # Created At
            self._filtered_clones.sort(key=lambda r: r.created_at, reverse=not ascending)
            target_sort = self.sort_oldest if ascending else self.sort_newest
            self.selected_sort = target_sort
            if hasattr(self.top_bar, "select_sort") and self.top_bar.select_sort:
                self.top_bar.select_sort.value = target_sort

        self._render_current_view()

    def on_action_new_clone(self, widget: toga.Button):
        if self.app_instance and hasattr(self.app_instance, "action_new_clone"):
            self.app_instance.action_new_clone(widget)

    def _apply_filter(self):
        items = list(self._raw_clones)

        # 1. Search Query Filter
        if self.search_query:
            items = [
                r for r in items
                if self.search_query in r.clone_name.lower()
                or self.search_query in r.source_app.lower()
                or self.search_query in r.bundle_id.lower()
                or self.search_query in r.strategy.lower()
            ]

        # 2. Strategy / Proxy Category Filter
        filter_hard_keys = (getattr(self, "filter_hard", ""), self.FILTER_HARD)
        filter_soft_keys = (getattr(self, "filter_soft", ""), self.FILTER_SOFT)
        filter_proxy_keys = (getattr(self, "filter_proxy", ""), self.FILTER_PROXY)

        if self.selected_filter in filter_hard_keys or "hard" in str(self.selected_filter).lower() or "物理" in str(self.selected_filter):
            items = [r for r in items if r.strategy == "hard_clone"]
        elif self.selected_filter in filter_soft_keys or "soft" in str(self.selected_filter).lower() or "软" in str(self.selected_filter):
            items = [r for r in items if r.strategy == "soft_clone"]
        elif self.selected_filter in filter_proxy_keys or "proxy" in str(self.selected_filter).lower() or "代理" in str(self.selected_filter):
            items = [r for r in items if r.proxy_enabled]

        # 3. Sort
        sort_name_keys = (getattr(self, "sort_name", ""), self.SORT_NAME)
        sort_oldest_keys = (getattr(self, "sort_oldest", ""), self.SORT_OLDEST)
        if self.selected_sort in sort_name_keys or "name" in str(self.selected_sort).lower() or "名称" in str(self.selected_sort):
            items.sort(key=lambda r: r.clone_name.lower())
        elif self.selected_sort in sort_oldest_keys or "oldest" in str(self.selected_sort).lower() or "最早" in str(self.selected_sort):
            items.sort(key=lambda r: r.created_at)
        else:  # self.sort_newest
            items.sort(key=lambda r: r.created_at, reverse=True)

        self._filtered_clones = items
        self._render_current_view()

    def _render_current_view(self):
        while len(self.content_container.children) > 0:
            self.content_container.remove(self.content_container.children[0])

        total_count = len(self._raw_clones)
        filter_count = len(self._filtered_clones)
        if self.search_query or self.selected_filter != self.filter_all:
            self.top_bar.update_title(t("view_clones_title_filtered", filter_count=filter_count, total_count=total_count))
        else:
            self.top_bar.update_title(t("view_clones_title", count=total_count))

        if not self._filtered_clones:
            self.content_container.add(self.label_empty)
            return

        if self.view_mode == "grid":
            while len(self.grid_box.children) > 0:
                self.grid_box.remove(self.grid_box.children[0])

            # Chunk into multi-row grid (2 cards per row)
            ROW_SIZE = 2
            for i in range(0, len(self._filtered_clones), ROW_SIZE):
                chunk = self._filtered_clones[i:i + ROW_SIZE]
                row_box = toga.Box(style=Pack(direction=ROW, margin_bottom=12))
                for record in chunk:
                    card = CloneCard(
                        record=record,
                        on_launch=lambda r: asyncio.create_task(self.on_launch_clone(r)),
                        on_open_dir=lambda r: asyncio.create_task(self.on_open_clone_dir(r)),
                        on_update=lambda r: asyncio.create_task(self.on_update_clone(r)),
                        on_edit=lambda r: asyncio.create_task(self.on_edit_clone(r)),
                        on_detail=lambda r: asyncio.create_task(self.on_detail_clone(r)),
                        on_delete=lambda r: asyncio.create_task(self.on_delete_clone(r)),
                    )
                    row_box.add(card)
                self.grid_box.add(row_box)

            self.content_container.add(self.grid_scroll)
        else:
            prev_sel_records = self.get_selected_records()
            prev_sel_names = {r.clone_name for r in prev_sel_records}

            table_data = []
            for r in self._filtered_clones:
                proxy_str = r.proxy_summary if r.proxy_enabled else t("list_proxy_disabled")
                table_data.append((
                    r.clone_name,
                    r.source_app,
                    r.strategy,
                    proxy_str,
                    r.created_at[:19] if len(r.created_at) >= 19 else r.created_at,
                ))
            self.table.data = table_data
            self.content_container.add(self.table_box)

            if prev_sel_names:
                try:
                    from rubicon.objc import ObjCClass
                    NSMutableIndexSet = ObjCClass("NSMutableIndexSet")
                    index_set = NSMutableIndexSet.alloc().init()
                    for idx, r in enumerate(self._filtered_clones):
                        if r.clone_name in prev_sel_names:
                            index_set.addIndex_(idx)
                    native = getattr(getattr(self.table, "_impl", None), "native_table", None)
                    if native is not None and index_set.count > 0:
                        native.selectRowIndexes_byExtendingSelection_(index_set, False)
                except Exception:
                    pass

            self.on_table_select(self.table)

    def on_table_select(self, widget: toga.Table):
        records = self.get_selected_records()
        if not records:
            single = self.get_selected_record()
            if single:
                records = [single]

        count = len(records)
        has_busy = any(r.clone_name in self._busy_clones for r in records)

        if count == 0:
            self.btn_launch_table.enabled = False
            self.btn_open_dir_table.enabled = False
            self.btn_update_table.enabled = False
            self.btn_update_table.text = t("btn_update")
            self.btn_edit_table.enabled = False
            self.btn_detail_table.enabled = False
            self.btn_delete_table.enabled = False
            self.btn_delete_table.text = t("btn_delete")
        elif count == 1:
            self.btn_launch_table.enabled = not has_busy
            self.btn_open_dir_table.enabled = True
            self.btn_update_table.enabled = not has_busy
            self.btn_update_table.text = t("btn_update")
            self.btn_edit_table.enabled = not has_busy
            self.btn_detail_table.enabled = True
            self.btn_delete_table.enabled = not has_busy
            self.btn_delete_table.text = t("btn_delete")
        else:  # count >= 2
            self.btn_launch_table.enabled = False
            self.btn_open_dir_table.enabled = False
            self.btn_update_table.enabled = not has_busy
            self.btn_update_table.text = t("btn_batch_update", count=count)
            self.btn_edit_table.enabled = False
            self.btn_detail_table.enabled = False
            self.btn_delete_table.enabled = not has_busy
            self.btn_delete_table.text = t("btn_batch_delete", count=count)

    async def on_table_activate(self, widget: toga.Table, row=None, **kwargs):
        record = self.get_selected_record(row)
        if record:
            await self.on_edit_clone(record)

    def _extract_clone_name(self, item, known_names: set[str]) -> Optional[str]:
        if item is None:
            return None
        if isinstance(item, str):
            return item if item in known_names else None
        name = getattr(item, "Name", None) or getattr(item, "clone_name", None) or getattr(item, t("list_col_name"), None)
        if name and name in known_names:
            return name
        if hasattr(item, "_raw") and item._raw and isinstance(item._raw[0], str) and item._raw[0] in known_names:
            return item._raw[0]
        if isinstance(item, (tuple, list)) and len(item) > 0:
            if isinstance(item[0], str) and item[0] in known_names:
                return item[0]
        if hasattr(item, "__dict__"):
            for k, v in item.__dict__.items():
                if not k.startswith("_") and isinstance(v, str) and v in known_names:
                    return v
        return None

    def get_selected_records(self, selection=None) -> list[CloneRecord]:
        sel = selection if selection is not None else self.table.selection
        if sel is None:
            return []

        known_names = {r.clone_name for r in self._filtered_clones}
        selected_names: set[str] = set()

        single_name = self._extract_clone_name(sel, known_names)
        if single_name:
            selected_names.add(single_name)
        elif isinstance(sel, (list, tuple, set)):
            for item in sel:
                name = self._extract_clone_name(item, known_names)
                if name:
                    selected_names.add(name)

        return [r for r in self._filtered_clones if r.clone_name in selected_names]

    def get_selected_record(self, row=None) -> Optional[CloneRecord]:
        if row is not None:
            records = self.get_selected_records(row)
            return records[0] if len(records) == 1 else None
        records = self.get_selected_records()
        return records[0] if len(records) == 1 else None

    async def refresh_clones(self):
        self._raw_clones = await self.clone_service.list_clones()
        self._apply_filter()

    async def on_launch_clone(self, record: Optional[CloneRecord]):
        if not record:
            return
        dest_path = Path(record.dest_path)
        logger.info(f"Launching clone '{record.clone_name}' at '{dest_path}'")
        if not dest_path.exists():
            logger.error(f"Cannot launch clone '{record.clone_name}': file does not exist at '{dest_path}'")
            if self.app_instance and hasattr(self.app_instance, "main_window"):
                await self.app_instance.main_window.error_dialog(
                    t("dialog_launch_error_title"),
                    t("dialog_launch_error_not_found", path=str(dest_path)),
                )
            return

        loop = asyncio.get_running_loop()
        try:
            await loop.run_in_executor(None, lambda: subprocess.Popen(["open", str(dest_path)]))
            logger.info(f"Successfully triggered open for clone '{record.clone_name}'")
        except Exception as e:
            logger.error(f"Failed to launch clone '{record.clone_name}': {e}")
            if self.app_instance and hasattr(self.app_instance, "main_window"):
                await self.app_instance.main_window.error_dialog(t("dialog_launch_error_title"), t("dialog_launch_error_failed", error=str(e)))

    async def on_open_clone_dir(self, record: Optional[CloneRecord]):
        if not record:
            return
        dest_path = Path(record.dest_path)
        logger.info(f"Opening directory for clone '{record.clone_name}' at '{dest_path}'")
        loop = asyncio.get_running_loop()
        try:
            if dest_path.exists():
                await loop.run_in_executor(None, lambda: subprocess.Popen(["open", "-R", str(dest_path)]))
            elif dest_path.parent.exists():
                await loop.run_in_executor(None, lambda: subprocess.Popen(["open", str(dest_path.parent)]))
            else:
                logger.error(f"Cannot open directory for clone '{record.clone_name}': path does not exist at '{dest_path}'")
                if self.app_instance and hasattr(self.app_instance, "main_window"):
                    await self.app_instance.main_window.error_dialog(
                        t("dialog_launch_error_title"),
                        t("dialog_launch_error_not_found", path=str(dest_path)),
                    )
        except Exception as e:
            logger.error(f"Failed to open directory for clone '{record.clone_name}': {e}")
            if self.app_instance and hasattr(self.app_instance, "main_window"):
                await self.app_instance.main_window.error_dialog(t("dialog_launch_error_title"), str(e))

    async def on_detail_clone(self, record: Optional[CloneRecord]):
        if not record:
            return
        win = CloneDetailWindow(record=record)
        win.show()

    async def on_edit_clone(self, record: Optional[CloneRecord]):
        if not record:
            return

        async def _save_cb(updated_record: CloneRecord):
            await self.clone_service.update_clone_record(updated_record)
            if (
                updated_record.language != record.language
                or updated_record.proxy_summary != record.proxy_summary
                or updated_record.proxy_enabled != record.proxy_enabled
            ):
                try:
                    await self.clone_service.update_clone(updated_record.clone_name)
                except Exception as e:
                    logger.warning(f"Failed to auto-update clone after edit: {e}")
            await self.refresh_clones()

        win = CloneEditWindow(record=record, on_save=_save_cb)
        win.show()

    async def on_update_clone(self, target: Optional[CloneRecord | list[CloneRecord]] = None):
        if target is None:
            records = self.get_selected_records()
        elif isinstance(target, CloneRecord):
            records = [target]
        else:
            records = list(target)

        if not records:
            return

        active_records = [r for r in records if r.clone_name not in self._busy_clones]
        if not active_records:
            return

        for r in active_records:
            self._busy_clones.add(r.clone_name)

        total = len(active_records)
        failed_list: list[tuple[str, str]] = []

        if hasattr(self, "btn_update_table") and self.btn_update_table:
            self.btn_update_table.enabled = False

        try:
            for idx, r in enumerate(active_records, 1):
                if hasattr(self, "btn_update_table") and self.btn_update_table:
                    if total > 1:
                        self.btn_update_table.text = t("btn_updating_progress", current=idx, total=total)
                    else:
                        self.btn_update_table.text = t("btn_updating")
                try:
                    await self.clone_service.update_clone(r.clone_name)
                except Exception as e:
                    logger.error(f"Failed to update clone '{r.clone_name}': {e}")
                    failed_list.append((r.clone_name, str(e)))
            await self.refresh_clones()
        finally:
            for r in active_records:
                self._busy_clones.discard(r.clone_name)
            if hasattr(self, "btn_update_table") and self.btn_update_table:
                self.btn_update_table.text = t("btn_update")
            self.on_table_select(self.table)

        if failed_list and self.app_instance and hasattr(self.app_instance, "main_window"):
            succ_count = total - len(failed_list)
            err_details = "\n".join(f"- {name}: {err}" for name, err in failed_list)
            if total > 1:
                await self.app_instance.main_window.error_dialog(
                    t("dialog_batch_summary_title"),
                    t("dialog_batch_summary_msg", success=succ_count, failed=len(failed_list), errors=err_details),
                )
            else:
                await self.app_instance.main_window.error_dialog(
                    t("dialog_update_error_title"),
                    failed_list[0][1],
                )

    async def on_delete_clone(self, target: Optional[CloneRecord | list[CloneRecord]] = None):
        if target is None:
            records = self.get_selected_records()
        elif isinstance(target, CloneRecord):
            records = [target]
        else:
            records = list(target)

        if not records:
            return

        active_records = [r for r in records if r.clone_name not in self._busy_clones]
        if not active_records:
            return

        total = len(active_records)
        delete_data = False

        if self.app_instance and hasattr(self.app_instance, "main_window"):
            if total == 1:
                record = active_records[0]
                confirmed = await self.app_instance.main_window.confirm_dialog(
                    t("dialog_delete_confirm_title"),
                    t("dialog_delete_confirm_msg", name=record.clone_name),
                )
                if not confirmed:
                    return

                delete_data = await self.app_instance.main_window.confirm_dialog(
                    t("dialog_delete_data_confirm_title"),
                    t("dialog_delete_data_confirm_msg", path=record.data_dir),
                )
            else:
                names_summary = ", ".join(r.clone_name for r in active_records[:6])
                if total > 6:
                    names_summary += f" ... (+{total - 6})"
                confirmed = await self.app_instance.main_window.confirm_dialog(
                    t("dialog_batch_delete_confirm_title"),
                    t("dialog_batch_delete_confirm_msg", count=total, names=names_summary),
                )
                if not confirmed:
                    return

                delete_data = await self.app_instance.main_window.confirm_dialog(
                    t("dialog_batch_delete_data_confirm_title"),
                    t("dialog_batch_delete_data_confirm_msg", count=total),
                )

        for r in active_records:
            self._busy_clones.add(r.clone_name)

        failed_list: list[tuple[str, str]] = []
        if hasattr(self, "btn_delete_table") and self.btn_delete_table:
            self.btn_delete_table.enabled = False

        try:
            for idx, r in enumerate(active_records, 1):
                if hasattr(self, "btn_delete_table") and self.btn_delete_table:
                    if total > 1:
                        self.btn_delete_table.text = t("btn_deleting_progress", current=idx, total=total)
                    else:
                        self.btn_delete_table.text = t("btn_delete")
                try:
                    await self.clone_service.remove_clone(r.clone_name, with_data=delete_data)
                except Exception as e:
                    logger.error(f"Failed to delete clone '{r.clone_name}': {e}")
                    failed_list.append((r.clone_name, str(e)))
            await self.refresh_clones()
        finally:
            for r in active_records:
                self._busy_clones.discard(r.clone_name)
            if hasattr(self, "btn_delete_table") and self.btn_delete_table:
                self.btn_delete_table.text = t("btn_delete")
            self.on_table_select(self.table)

        if failed_list and self.app_instance and hasattr(self.app_instance, "main_window"):
            succ_count = total - len(failed_list)
            err_details = "\n".join(f"- {name}: {err}" for name, err in failed_list)
            if total > 1:
                await self.app_instance.main_window.error_dialog(
                    t("dialog_batch_summary_title"),
                    t("dialog_batch_summary_msg", success=succ_count, failed=len(failed_list), errors=err_details),
                )
            else:
                await self.app_instance.main_window.error_dialog(
                    t("dialog_error_title"),
                    failed_list[0][1],
                )

