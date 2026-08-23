"""Recipe List Dual-View (Cards & Table) View."""

import asyncio
from typing import Any, Optional
from pathlib import Path
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER

from atbclone.core.i18n import t
from atbclone.recipes.models import Recipe
from atbclone.gui.services.recipe_service import RecipeService
from atbclone.gui.windows.recipe_edit import RecipeEditWindow
from atbclone.gui.components.top_bar import TopHeaderBar
from atbclone.gui.theme import Theme


class RecipeListView(toga.Box):
    """View managing built-in and custom clone recipes with search and dual views."""

    FILTER_ALL = "🏷️ 全部来源"
    FILTER_BUILTIN = "📦 内置规则"
    FILTER_CUSTOM = "✏️ 自定义规则"

    SORT_NAME_ASC = "🔽 应用名称 (A-Z)"
    SORT_NAME_DESC = "🔼 应用名称 (Z-A)"
    SORT_STRATEGY = "⚡️ 克隆策略"

    def __init__(self, recipe_service: Optional[RecipeService] = None, app: Optional[toga.App] = None):
        super().__init__(style=Pack(direction=COLUMN, flex=1, background_color=Theme.BG_WINDOW))
        self.recipe_service = recipe_service or RecipeService()
        self.app_instance = app
        self._raw_recipes: list[dict] = []
        self._filtered_recipes: list[dict] = []
        self._busy_recipes: set[str] = set()
        self.view_mode: str = "list"  # "grid" or "list"
        self.search_query: str = ""

        # Localized filter and sort labels
        self.filter_all = t("view_recipes_filter_all")
        self.filter_builtin = t("view_recipes_filter_builtin")
        self.filter_custom = t("view_recipes_filter_custom")

        self.sort_name_asc = t("view_recipes_sort_name_asc")
        self.sort_name_desc = t("view_recipes_sort_name_desc")
        self.sort_strategy = t("view_recipes_sort_strategy")

        self.selected_filter: str = self.filter_all
        self.selected_sort: str = self.sort_name_asc

        # Top Header Bar
        self.top_bar = TopHeaderBar(
            title=t("view_recipes_title", count=0),
            action_label=t("btn_new_recipe"),
            on_action=self.on_new_recipe,
            search_placeholder=t("view_recipes_search_placeholder"),
            on_search=self.on_search_query_changed,
            filter_items=[self.filter_all, self.filter_builtin, self.filter_custom],
            on_filter_change=self.on_filter_changed,
            sort_items=[self.sort_name_asc, self.sort_name_desc, self.sort_strategy],
            on_sort_change=self.on_sort_changed,
            view_modes=[t("topbar_view_list"), t("topbar_view_grid")],
            on_view_change=self.on_view_mode_changed,
            on_refresh=lambda w: asyncio.create_task(self.refresh_recipes()),
        )
        self.add(self.top_bar)

        # Content container
        self.content_container = toga.Box(style=Pack(direction=COLUMN, flex=1, margin=(0, 24, 20, 24)))
        self.add(self.content_container)

        # Grid view scroll container & flow box
        self.grid_scroll = toga.ScrollContainer(style=Pack(flex=1), horizontal=False)
        self.grid_box = toga.Box(style=Pack(direction=COLUMN, margin=4))
        self.grid_scroll.content = self.grid_box

        # Table view container & action bar
        self.table_box = toga.Box(style=Pack(direction=COLUMN, flex=1))
        self.table = toga.Table(
            columns=[
                t("recipe_col_app_name"),
                t("recipe_col_bundle_id"),
                t("recipe_col_strategy"),
                t("view_recipes_col_origin"),
            ],
            multiple_select=True,
            on_select=self.on_table_select,
            on_activate=self.on_table_activate,
            style=Pack(flex=1),
        )
        self.table.on_header_sort = self.on_table_header_sort
        self.table_box.add(self.table)

        self.btn_edit = toga.Button(t("btn_edit"), on_press=self.on_edit_recipe, enabled=False, style=Pack(margin_right=6, height=28, font_size=12.5, font_weight="bold"))
        self.btn_delete = toga.Button(t("btn_delete"), on_press=self.on_delete_recipe, enabled=False, style=Pack(height=28, font_size=12.5))

        actions_box = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin_top=8))
        actions_box.add(self.btn_edit)
        actions_box.add(self.btn_delete)
        self.table_box.add(actions_box)

        # Empty state label
        self.label_empty = toga.Label(
            t("view_recipes_empty_hint"),
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
        if col_index == 0:  # App Name
            self._filtered_recipes.sort(key=lambda r: r["app_name"].lower(), reverse=not ascending)
            target_sort = self.sort_name_asc if ascending else self.sort_name_desc
            self.selected_sort = target_sort
            if hasattr(self.top_bar, "select_sort") and self.top_bar.select_sort:
                self.top_bar.select_sort.value = target_sort
        elif col_index == 1:  # Bundle ID
            self._filtered_recipes.sort(key=lambda r: r["bundle_id"].lower(), reverse=not ascending)
        elif col_index == 2:  # Strategy
            self._filtered_recipes.sort(key=lambda r: (r["strategy"].lower(), r["app_name"].lower()), reverse=not ascending)
            if ascending:
                self.selected_sort = self.sort_strategy
                if hasattr(self.top_bar, "select_sort") and self.top_bar.select_sort:
                    self.top_bar.select_sort.value = self.sort_strategy
        elif col_index == 3:  # Origin
            self._filtered_recipes.sort(key=lambda r: (not r.get("is_builtin", False), r["app_name"].lower()), reverse=not ascending)

        self._render_current_view()

    def _apply_filter(self):
        items = list(self._raw_recipes)
        if self.search_query:
            items = [
                r for r in items
                if self.search_query in r["app_name"].lower()
                or self.search_query in r["bundle_id"].lower()
                or self.search_query in r["strategy"].lower()
                or self.search_query in ("built-in" if r["is_builtin"] else "custom")
            ]

        if hasattr(self, "selected_filter"):
            filter_builtin_keys = (getattr(self, "filter_builtin", ""), self.FILTER_BUILTIN)
            filter_custom_keys = (getattr(self, "filter_custom", ""), self.FILTER_CUSTOM)
            if self.selected_filter in filter_builtin_keys or "builtin" in str(self.selected_filter).lower() or "内置" in str(self.selected_filter):
                items = [r for r in items if r.get("is_builtin")]
            elif self.selected_filter in filter_custom_keys or "custom" in str(self.selected_filter).lower() or "自定义" in str(self.selected_filter):
                items = [r for r in items if not r.get("is_builtin")]

        # Sort
        if hasattr(self, "selected_sort"):
            sort_desc_keys = (getattr(self, "sort_name_desc", ""), self.SORT_NAME_DESC)
            sort_strat_keys = (getattr(self, "sort_strategy", ""), self.SORT_STRATEGY)
            if self.selected_sort in sort_desc_keys or "desc" in str(self.selected_sort).lower() or "z-a" in str(self.selected_sort).lower():
                items.sort(key=lambda r: r["app_name"].lower(), reverse=True)
            elif self.selected_sort in sort_strat_keys or "strat" in str(self.selected_sort).lower() or "策略" in str(self.selected_sort):
                items.sort(key=lambda r: (r["strategy"], r["app_name"].lower()))
            else:  # self.sort_name_asc
                items.sort(key=lambda r: r["app_name"].lower())
        else:
            items.sort(key=lambda r: r["app_name"].lower())

        self._filtered_recipes = items
        self._render_current_view()

    def _render_current_view(self):
        while len(self.content_container.children) > 0:
            self.content_container.remove(self.content_container.children[0])

        total_count = len(self._raw_recipes)
        filter_count = len(self._filtered_recipes)
        if self.search_query or (hasattr(self, "selected_filter") and self.selected_filter != self.filter_all):
            self.top_bar.update_title(t("view_recipes_title_filtered", filter_count=filter_count, total_count=total_count))
        else:
            self.top_bar.update_title(t("view_recipes_title", count=total_count))

        if not self._filtered_recipes:
            self.content_container.add(self.label_empty)
            return

        if self.view_mode == "grid":
            while len(self.grid_box.children) > 0:
                self.grid_box.remove(self.grid_box.children[0])

            # Chunk into multi-row grid (2 cards per row)
            ROW_SIZE = 2
            for i in range(0, len(self._filtered_recipes), ROW_SIZE):
                chunk = self._filtered_recipes[i : i + ROW_SIZE]
                row_box = toga.Box(style=Pack(direction=ROW, margin_bottom=12))
                for item in chunk:
                    card = self._create_recipe_card(item)
                    row_box.add(card)
                self.grid_box.add(row_box)
            self.content_container.add(self.grid_scroll)
        else:
            prev_sel_items = self.get_selected_recipe_items()
            prev_sel_bundle_ids = {r["bundle_id"] for r in prev_sel_items}

            table_data = []
            for r in self._filtered_recipes:
                origin = t("view_recipes_origin_builtin") if r["is_builtin"] else t("view_recipes_origin_custom")
                table_data.append((
                    r["app_name"],
                    r["bundle_id"],
                    r["strategy"],
                    origin,
                ))
            self.table.data = table_data
            self.content_container.add(self.table_box)

            if prev_sel_bundle_ids:
                try:
                    from rubicon.objc import ObjCClass
                    NSMutableIndexSet = ObjCClass("NSMutableIndexSet")
                    index_set = NSMutableIndexSet.alloc().init()
                    for idx, r in enumerate(self._filtered_recipes):
                        if r["bundle_id"] in prev_sel_bundle_ids:
                            index_set.addIndex_(idx)
                    native = getattr(getattr(self.table, "_impl", None), "native_table", None)
                    if native is not None and index_set.count > 0:
                        native.selectRowIndexes_byExtendingSelection_(index_set, False)
                except Exception:
                    pass

            self.on_table_select(self.table)

    def _create_recipe_card(self, item: dict) -> toga.Box:
        recipe: Recipe = item["recipe"]
        is_builtin = item.get("is_builtin", False)

        card = toga.Box(style=Pack(direction=COLUMN, margin=(6, 8, 8, 8), width=340, background_color=Theme.BG_CARD))

        # Header
        header = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin=(12, 14, 6, 14)))
        header.add(toga.Label(f"📖 {recipe.app_name}", style=Pack(font_weight="bold", font_size=15, flex=1, color=Theme.TEXT_PRIMARY)))
        origin_text = f"[{t('view_recipes_origin_builtin')}]" if is_builtin else f"[{t('view_recipes_origin_custom')}]"
        origin_color = Theme.ACCENT_BLUE if is_builtin else Theme.BTN_SUCCESS
        header.add(toga.Label(origin_text, style=Pack(font_size=12, font_weight="bold", color=origin_color)))
        card.add(header)

        # Body
        body = toga.Box(style=Pack(direction=COLUMN, margin=(0, 14, 10, 14)))
        body.add(toga.Label(f"Bundle ID: {recipe.bundle_id}", style=Pack(font_size=12.5, color=Theme.TEXT_MUTED, margin_bottom=3)))
        is_soft = recipe.strategy == "soft_clone"
        strat_badge = t("card_strategy_soft") if is_soft else t("card_strategy_hard")
        body.add(toga.Label(f"策略: {strat_badge}", style=Pack(font_size=12, color=Theme.TEXT_TERTIARY)))
        card.add(body)

        # Footer
        actions = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin=(0, 14, 12, 14)))
        btn_edit = toga.Button(t("btn_edit"), on_press=lambda w: self._open_edit_dialog(recipe), style=Pack(font_weight="bold", font_size=13, height=30, margin_right=6, flex=1))
        actions.add(btn_edit)

        if not is_builtin:
            btn_del = toga.Button("🗑️", on_press=lambda w: asyncio.create_task(self._delete_recipe_direct(recipe.bundle_id, recipe.app_name)), style=Pack(width=34, height=30))
            actions.add(btn_del)

        card.add(actions)
        return card

    def on_table_select(self, widget: toga.Table):
        selected_items = self.get_selected_recipe_items()
        if not selected_items:
            single = self.get_selected_recipe_item()
            if single:
                selected_items = [single]

        count = len(selected_items)
        custom_items = [r for r in selected_items if not r.get("is_builtin", False)]
        custom_count = len(custom_items)
        has_busy = any(r["bundle_id"] in self._busy_recipes for r in selected_items)

        if count == 0:
            self.btn_edit.enabled = False
            self.btn_delete.enabled = False
            self.btn_delete.text = t("btn_delete")
        elif count == 1:
            self.btn_edit.enabled = not has_busy
            self.btn_delete.enabled = (custom_count == 1) and not has_busy
            self.btn_delete.text = t("btn_delete")
        else:  # count >= 2
            self.btn_edit.enabled = False
            if custom_count > 0:
                self.btn_delete.enabled = not has_busy
                self.btn_delete.text = t("btn_batch_delete", count=custom_count)
            else:
                self.btn_delete.enabled = False
                self.btn_delete.text = t("btn_delete")

    def on_table_activate(self, widget: toga.Table, row=None, **kwargs):
        item = self.get_selected_recipe_item(row)
        if not item or not item.get("recipe"):
            return
        self._open_edit_dialog(item["recipe"])

    def _extract_bundle_id(self, item, known_bundle_ids: set[str]) -> Optional[str]:
        if item is None:
            return None
        if isinstance(item, str):
            return item if item in known_bundle_ids else None
        bundle_id = (
            getattr(item, "bundle_id", None)
            or getattr(item, "Bundle ID", None)
            or getattr(item, t("recipe_col_bundle_id"), None)
        )
        if bundle_id and bundle_id in known_bundle_ids:
            return bundle_id
        if hasattr(item, "_raw") and item._raw and len(item._raw) > 1 and isinstance(item._raw[1], str) and item._raw[1] in known_bundle_ids:
            return item._raw[1]
        if isinstance(item, (tuple, list)) and len(item) > 1:
            if isinstance(item[1], str) and item[1] in known_bundle_ids:
                return item[1]
        if hasattr(item, "__dict__"):
            for k, v in item.__dict__.items():
                if not k.startswith("_") and isinstance(v, str) and v in known_bundle_ids:
                    return v
        return None

    def get_selected_recipe_items(self, selection=None) -> list[dict]:
        sel = selection if selection is not None else self.table.selection
        if sel is None:
            return []

        known_bundle_ids = {r["bundle_id"] for r in self._filtered_recipes}
        selected_ids: set[str] = set()

        single_id = self._extract_bundle_id(sel, known_bundle_ids)
        if single_id:
            selected_ids.add(single_id)
        elif isinstance(sel, (list, tuple, set)):
            for item in sel:
                bid = self._extract_bundle_id(item, known_bundle_ids)
                if bid:
                    selected_ids.add(bid)

        return [r for r in self._filtered_recipes if r["bundle_id"] in selected_ids]

    def get_selected_recipe_item(self, row=None) -> Optional[dict]:
        if row is not None:
            items = self.get_selected_recipe_items(row)
            return items[0] if len(items) == 1 else None
        items = self.get_selected_recipe_items()
        return items[0] if len(items) == 1 else None

    async def refresh_recipes(self):
        self._raw_recipes = await self.recipe_service.list_all_recipes()
        self._apply_filter()

    async def on_new_recipe(self, widget: toga.Button):
        async def _save_cb(recipe: Recipe):
            await self.recipe_service.save_custom_recipe(recipe)
            await self.refresh_recipes()

        win = RecipeEditWindow(title=t("win_recipe_new_title"), recipe=None, on_save=_save_cb)
        win.show()

    def _open_edit_dialog(self, recipe: Recipe):
        async def _save_cb(updated_recipe: Recipe):
            await self.recipe_service.save_custom_recipe(updated_recipe)
            await self.refresh_recipes()

        win = RecipeEditWindow(title=t("win_recipe_edit_title", name=recipe.app_name), recipe=recipe, on_save=_save_cb)
        win.show()

    async def on_edit_recipe(self, widget: toga.Button):
        item = self.get_selected_recipe_item()
        if not item or not item.get("recipe"):
            return
        if item["bundle_id"] in self._busy_recipes:
            return
        self._open_edit_dialog(item["recipe"])

    async def _delete_recipe_direct(self, bundle_id: str, app_name: Optional[str] = None):
        if bundle_id in self._busy_recipes:
            return
        if self.app_instance and hasattr(self.app_instance, "main_window"):
            name = app_name or bundle_id
            confirmed = await self.app_instance.main_window.confirm_dialog(
                t("dialog_recipe_delete_confirm_title"),
                t("dialog_recipe_delete_confirm_msg", name=name),
            )
            if not confirmed:
                return

        self._busy_recipes.add(bundle_id)
        try:
            deleted = await self.recipe_service.delete_custom_recipe(bundle_id)
            if deleted:
                await self.refresh_recipes()
        finally:
            self._busy_recipes.discard(bundle_id)

    async def on_delete_recipe(self, widget: toga.Button):
        selected_items = self.get_selected_recipe_items()
        if not selected_items:
            single = self.get_selected_recipe_item()
            if single:
                selected_items = [single]

        custom_items = [r for r in selected_items if not r.get("is_builtin", False)]
        builtin_items = [r for r in selected_items if r.get("is_builtin", False)]

        if not custom_items:
            return

        active_items = [r for r in custom_items if r["bundle_id"] not in self._busy_recipes]
        if not active_items:
            return

        total_custom = len(active_items)
        total_builtin = len(builtin_items)

        if self.app_instance and hasattr(self.app_instance, "main_window"):
            if total_custom == 1 and total_builtin == 0:
                item = active_items[0]
                confirmed = await self.app_instance.main_window.confirm_dialog(
                    t("dialog_recipe_delete_confirm_title"),
                    t("dialog_recipe_delete_confirm_msg", name=item["app_name"]),
                )
                if not confirmed:
                    return
            elif total_builtin == 0:
                names_summary = ", ".join(r["app_name"] for r in active_items[:6])
                if total_custom > 6:
                    names_summary += f" ... (+{total_custom - 6})"
                confirmed = await self.app_instance.main_window.confirm_dialog(
                    t("dialog_recipe_batch_delete_confirm_title"),
                    t("dialog_recipe_batch_delete_confirm_msg", count=total_custom, names=names_summary),
                )
                if not confirmed:
                    return
            else:  # Mixed selection: total_custom >= 1 and total_builtin >= 1
                names_summary = ", ".join(r["app_name"] for r in active_items[:6])
                if total_custom > 6:
                    names_summary += f" ... (+{total_custom - 6})"
                confirmed = await self.app_instance.main_window.confirm_dialog(
                    t("dialog_recipe_batch_delete_confirm_mixed_title"),
                    t(
                        "dialog_recipe_batch_delete_confirm_mixed_msg",
                        custom_count=total_custom,
                        builtin_count=total_builtin,
                        names=names_summary,
                    ),
                )
                if not confirmed:
                    return

        for r in active_items:
            self._busy_recipes.add(r["bundle_id"])

        failed_list: list[tuple[str, str]] = []
        if hasattr(self, "btn_delete") and self.btn_delete:
            self.btn_delete.enabled = False

        try:
            for idx, r in enumerate(active_items, 1):
                if total_custom > 1:
                    self.btn_delete.text = t("btn_deleting_progress", current=idx, total=total_custom)
                else:
                    self.btn_delete.text = t("btn_delete")
                try:
                    await self.recipe_service.delete_custom_recipe(r["bundle_id"])
                except Exception as e:
                    failed_list.append((r["app_name"], str(e)))
            await self.refresh_recipes()
        finally:
            for r in active_items:
                self._busy_recipes.discard(r["bundle_id"])
            if hasattr(self, "btn_delete") and self.btn_delete:
                self.btn_delete.text = t("btn_delete")
            self.on_table_select(self.table)

        if failed_list and self.app_instance and hasattr(self.app_instance, "main_window"):
            succ_count = total_custom - len(failed_list)
            err_details = "\n".join(f"- {name}: {err}" for name, err in failed_list)
            if total_custom > 1:
                await self.app_instance.main_window.error_dialog(
                    t("dialog_batch_summary_title"),
                    t("dialog_batch_summary_msg", success=succ_count, failed=len(failed_list), errors=err_details),
                )
            else:
                await self.app_instance.main_window.error_dialog(
                    t("dialog_error_title"),
                    failed_list[0][1],
                )

