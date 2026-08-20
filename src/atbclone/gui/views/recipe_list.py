"""Recipe List Dual-View (Cards & Table) View."""

import asyncio
from typing import Any, Optional
from pathlib import Path
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER

from atbclone.recipes.models import Recipe
from atbclone.gui.services.recipe_service import RecipeService
from atbclone.gui.windows.recipe_edit import RecipeEditWindow
from atbclone.gui.components.top_bar import TopHeaderBar
from atbclone.gui.theme import Theme


class RecipeListView(toga.Box):
    """View managing built-in and custom clone recipes with search and dual views."""

    FILTER_ALL = "🏷️ 全部来源"
    FILTER_BUILTIN = "📦 内置预设"
    FILTER_CUSTOM = "✏️ 自定义配方"

    SORT_NAME_ASC = "🔽 应用名称 (A-Z)"
    SORT_NAME_DESC = "🔼 应用名称 (Z-A)"
    SORT_STRATEGY = "⚡️ 克隆策略"

    def __init__(self, recipe_service: Optional[RecipeService] = None, app: Optional[toga.App] = None):
        super().__init__(style=Pack(direction=COLUMN, flex=1, background_color=Theme.BG_WINDOW))
        self.recipe_service = recipe_service or RecipeService()
        self.app_instance = app
        self._raw_recipes: list[dict] = []
        self._filtered_recipes: list[dict] = []
        self.view_mode: str = "grid"  # "grid" or "list"
        self.search_query: str = ""
        self.selected_filter: str = self.FILTER_ALL
        self.selected_sort: str = self.SORT_NAME_ASC

        # Top Header Bar
        self.top_bar = TopHeaderBar(
            title="预设配方 (0)",
            action_label="+ 新建配方",
            on_action=self.on_new_recipe,
            search_placeholder="🔍 搜索应用配方 / Bundle ID...",
            on_search=self.on_search_query_changed,
            filter_items=[self.FILTER_ALL, self.FILTER_BUILTIN, self.FILTER_CUSTOM],
            on_filter_change=self.on_filter_changed,
            sort_items=[self.SORT_NAME_ASC, self.SORT_NAME_DESC, self.SORT_STRATEGY],
            on_sort_change=self.on_sort_changed,
            view_modes=[TopHeaderBar.VIEW_GRID, TopHeaderBar.VIEW_LIST],
            on_view_change=self.on_view_mode_changed,
            on_refresh=lambda w: asyncio.create_task(self.refresh_recipes()),
        )
        self.add(self.top_bar)

        # Content container
        self.content_container = toga.Box(style=Pack(direction=COLUMN, flex=1, margin=(0, 20, 20, 20)))
        self.add(self.content_container)

        # Grid view scroll container & flow box
        self.grid_scroll = toga.ScrollContainer(style=Pack(flex=1), horizontal=False)
        self.grid_box = toga.Box(style=Pack(direction=COLUMN, margin=5))
        self.grid_scroll.content = self.grid_box

        # Table view container & action bar
        self.table_box = toga.Box(style=Pack(direction=COLUMN, flex=1))
        self.table = toga.Table(
            columns=["App Name", "Bundle ID", "Strategy", "Origin"],
            on_select=self.on_table_select,
            style=Pack(flex=1),
        )
        self.table_box.add(self.table)

        self.btn_edit = toga.Button("✏️ 编辑", on_press=self.on_edit_recipe, enabled=False, style=Pack(margin=4))
        self.btn_copy = toga.Button("📋 复制为自定义", on_press=self.on_copy_recipe, enabled=False, style=Pack(margin=4))
        self.btn_delete = toga.Button("🗑️ 删除", on_press=self.on_delete_recipe, enabled=False, style=Pack(margin=4))

        actions_box = toga.Box(style=Pack(direction=ROW, margin_top=6))
        actions_box.add(self.btn_edit)
        actions_box.add(self.btn_copy)
        actions_box.add(self.btn_delete)
        self.table_box.add(actions_box)

        # Empty state label
        self.label_empty = toga.Label(
            "暂无匹配的配方规则，可点击右上角「+ 新建配方」添加自定义规则。",
            style=Pack(margin=30, font_size=13, color=Theme.TEXT_MUTED),
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
            if self.selected_filter == self.FILTER_BUILTIN:
                items = [r for r in items if r.get("is_builtin")]
            elif self.selected_filter == self.FILTER_CUSTOM:
                items = [r for r in items if not r.get("is_builtin")]

        # Sort
        if hasattr(self, "selected_sort"):
            if self.selected_sort == self.SORT_NAME_DESC:
                items.sort(key=lambda r: r["app_name"].lower(), reverse=True)
            elif self.selected_sort == self.SORT_STRATEGY:
                items.sort(key=lambda r: (r["strategy"], r["app_name"].lower()))
            else:  # SORT_NAME_ASC
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
        if self.search_query or (hasattr(self, "selected_filter") and self.selected_filter != "🏷️ 全部来源"):
            self.top_bar.update_title(f"预设配方 (筛选 {filter_count}/{total_count})")
        else:
            self.top_bar.update_title(f"预设配方 ({total_count})")

        if not self._filtered_recipes:
            self.content_container.add(self.label_empty)
            return

        if self.view_mode == "grid":
            while len(self.grid_box.children) > 0:
                self.grid_box.remove(self.grid_box.children[0])

            # Chunk into multi-row grid (2 cards per row)
            ROW_SIZE = 2
            for i in range(0, len(self._filtered_recipes), ROW_SIZE):
                chunk = self._filtered_recipes[i:i + ROW_SIZE]
                row_box = toga.Box(style=Pack(direction=ROW, margin_bottom=10))
                for item in chunk:
                    card = self._create_recipe_card(item)
                    row_box.add(card)
                self.grid_box.add(row_box)

            self.content_container.add(self.grid_scroll)
        else:
            table_data = []
            for r in self._filtered_recipes:
                origin = "Built-in" if r["is_builtin"] else "Custom"
                table_data.append((
                    r["app_name"],
                    r["bundle_id"],
                    r["strategy"],
                    origin,
                ))
            self.table.data = table_data
            self.content_container.add(self.table_box)
            self.on_table_select(self.table)

    def _create_recipe_card(self, item: dict) -> toga.Box:
        recipe: Recipe = item["recipe"]
        is_builtin = item.get("is_builtin", False)

        card = toga.Box(style=Pack(direction=COLUMN, margin=8, width=290, background_color=Theme.BG_CARD))
        
        # Header
        header = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin_bottom=6))
        header.add(toga.Label(f"📖 {recipe.app_name}", style=Pack(font_weight="bold", font_size=14, flex=1, color=Theme.TEXT_PRIMARY)))
        origin_text = "[内置]" if is_builtin else "[自定义]"
        origin_color = Theme.ACCENT_BLUE if is_builtin else Theme.BTN_SUCCESS
        header.add(toga.Label(origin_text, style=Pack(font_size=11, color=origin_color)))
        card.add(header)

        # Body
        body = toga.Box(style=Pack(direction=COLUMN, margin_bottom=8))
        body.add(toga.Label(f"Bundle ID: {recipe.bundle_id}", style=Pack(font_size=11, color=Theme.TEXT_MUTED, margin_bottom=2)))
        strat_badge = "物理完整克隆 (Hard)" if recipe.strategy == "hard_clone" else "软包装克隆 (Soft)"
        body.add(toga.Label(f"策略: {strat_badge}", style=Pack(font_size=11, color=Theme.TEXT_MUTED, margin_bottom=2)))
        card.add(body)

        # Footer
        actions = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin_top=4))
        btn_copy = toga.Button("📋 复制", on_press=lambda w: asyncio.create_task(self._copy_recipe_direct(recipe)), style=Pack(margin_right=4, flex=1))
        actions.add(btn_copy)

        if not is_builtin:
            btn_edit = toga.Button("✏️", on_press=lambda w: self._open_edit_dialog(recipe), style=Pack(margin_right=4, width=36))
            btn_del = toga.Button("🗑️", on_press=lambda w: asyncio.create_task(self._delete_recipe_direct(recipe.bundle_id)), style=Pack(width=36))
            actions.add(btn_edit)
            actions.add(btn_del)

        card.add(actions)
        return card

    def on_table_select(self, widget: toga.Table):
        selected = self.get_selected_recipe_item()
        if selected is None:
            self.btn_edit.enabled = False
            self.btn_copy.enabled = False
            self.btn_delete.enabled = False
        else:
            self.btn_edit.enabled = not selected.get("is_builtin", False)
            self.btn_copy.enabled = True
            self.btn_delete.enabled = not selected.get("is_builtin", False)

    def get_selected_recipe_item(self) -> Optional[dict]:
        selection = self.table.selection
        if selection is None:
            return None
        bundle_id = getattr(selection, "bundle_id", None) or getattr(selection, "Bundle ID", None)
        if not bundle_id:
            if hasattr(selection, "_raw"):
                bundle_id = selection._raw[1]
        for r in self._filtered_recipes:
            if r["bundle_id"] == bundle_id:
                return r
        return None

    async def refresh_recipes(self):
        self._raw_recipes = await self.recipe_service.list_all_recipes()
        self._apply_filter()

    async def on_new_recipe(self, widget: toga.Button):
        async def _save_cb(recipe: Recipe):
            await self.recipe_service.save_custom_recipe(recipe)
            await self.refresh_recipes()

        win = RecipeEditWindow(title="新建自定义配方", recipe=None, on_save=_save_cb)
        win.show()

    def _open_edit_dialog(self, recipe: Recipe):
        async def _save_cb(updated_recipe: Recipe):
            await self.recipe_service.save_custom_recipe(updated_recipe)
            await self.refresh_recipes()

        win = RecipeEditWindow(title=f"编辑配方: {recipe.app_name}", recipe=recipe, on_save=_save_cb)
        win.show()

    async def on_edit_recipe(self, widget: toga.Button):
        item = self.get_selected_recipe_item()
        if not item or item.get("is_builtin"):
            return
        self._open_edit_dialog(item["recipe"])

    async def _copy_recipe_direct(self, recipe: Recipe):
        await self.recipe_service.duplicate_recipe(recipe)
        await self.refresh_recipes()

    async def on_copy_recipe(self, widget: toga.Button):
        item = self.get_selected_recipe_item()
        if not item:
            return
        await self._copy_recipe_direct(item["recipe"])

    async def _delete_recipe_direct(self, bundle_id: str):
        deleted = await self.recipe_service.delete_custom_recipe(bundle_id)
        if deleted:
            await self.refresh_recipes()

    async def on_delete_recipe(self, widget: toga.Button):
        item = self.get_selected_recipe_item()
        if not item or item.get("is_builtin"):
            return
        await self._delete_recipe_direct(item["bundle_id"])
