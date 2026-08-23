import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from atbclone.recipes.models import Recipe, ProxyConfig
from atbclone.gui.services.recipe_service import RecipeService
from atbclone.gui.views.recipe_list import RecipeListView
from atbclone.gui.windows.recipe_edit import RecipeEditWindow


def test_recipe_edit_window_initialization():
    on_save_mock = AsyncMock()
    recipe = Recipe(
        bundle_id="com.test.app",
        app_name="TestApp",
        strategy="hard_clone",
        strip_sandbox=True,
    )
    window = RecipeEditWindow(
        title="Edit Recipe",
        recipe=recipe,
        on_save=on_save_mock,
    )
    assert window.input_bundle_id.value == "com.test.app"
    assert window.input_app_name.value == "TestApp"
    assert window.select_strategy.value == "hard_clone"
    assert window.switch_strip_sandbox.value is True


def test_recipe_edit_window_save_action():
    on_save_mock = AsyncMock()
    window = RecipeEditWindow(
        title="New Recipe",
        recipe=None,
        on_save=on_save_mock,
    )
    window.input_bundle_id.value = "com.new.app"
    window.input_app_name.value = "NewApp"
    window.select_strategy.value = "soft_clone"
    window.switch_strip_sandbox.value = False

    saved_recipe = window.get_recipe_from_form()
    assert saved_recipe.bundle_id == "com.new.app"
    assert saved_recipe.app_name == "NewApp"
    assert saved_recipe.strategy == "soft_clone"
    assert saved_recipe.strip_sandbox is False


def test_recipe_list_view_refresh(tmp_path):
    async def _test():
        service = RecipeService(custom_recipes_dir=tmp_path / "recipes")
        view = RecipeListView(recipe_service=service)
        await view.refresh_recipes()
        assert len(view._raw_recipes) > 0
        assert view.view_mode == "list"
        assert len(view.table.data) > 0

        # Toggle mode
        view.on_view_mode_changed("grid")
        assert view.view_mode == "grid"

        # Search filter
        view.on_search_query_changed("WeChat")
        assert len(view._filtered_recipes) >= 1

        # Clear search and test origin filter
        view.on_search_query_changed("")
        view.on_filter_changed(RecipeListView.FILTER_BUILTIN)
        assert len(view._filtered_recipes) >= 1

        # Test sorting
        view.on_sort_changed(RecipeListView.SORT_NAME_DESC)
        assert len(view._filtered_recipes) >= 1
        assert view._filtered_recipes[0]["app_name"].lower() >= view._filtered_recipes[-1]["app_name"].lower()

        # Switch back to list view mode
        view.on_view_mode_changed("list")
        assert view.view_mode == "list"
        assert len(view.table.data) >= 1

        # Selection enables edit for all recipes, but delete only for custom
        with patch.object(view, "get_selected_recipe_item", return_value=view._filtered_recipes[0]):
            view.on_table_select(view.table)
            assert view.btn_edit.enabled is True
            assert view.btn_delete.enabled is not view._filtered_recipes[0]["is_builtin"]

        # Deselecting disables both
        with patch.object(view, "get_selected_recipe_item", return_value=None):
            view.on_table_select(view.table)
            assert view.btn_edit.enabled is False
            assert view.btn_delete.enabled is False

        # Test double-click (on_activate) on table row opens edit window
        with patch.object(view, "_open_edit_dialog") as mock_open:
            view.on_table_activate(view.table, row=view.table.data[0])
            mock_open.assert_called_once_with(view._filtered_recipes[0]["recipe"])

    asyncio.run(_test())


def test_recipe_edit_window_bundle_id_readonly_behavior():
    # Existing recipe: readonly bundle_id
    recipe = Recipe(bundle_id="com.tencent.xinWeChat", app_name="WeChat", strategy="hard_clone")
    win1 = RecipeEditWindow(title="Edit", recipe=recipe)
    assert win1.input_bundle_id.readonly is True

    # New recipe: editable bundle_id
    win2 = RecipeEditWindow(title="New", recipe=None)
    assert win2.input_bundle_id.readonly is False


def test_recipe_list_view_table_header_sort():
    view = RecipeListView()
    view._raw_recipes = [
        {"app_name": "Zed", "bundle_id": "dev.zed.Zed", "strategy": "hard_clone", "is_builtin": True, "recipe": None},
        {"app_name": "Ableton", "bundle_id": "com.ableton.live", "strategy": "soft_clone", "is_builtin": False, "recipe": None},
    ]
    view._apply_filter()

    # Sort column 0 (App Name) ASC
    view.on_table_header_sort(0, view.table.columns[0], ascending=True)
    assert [r["app_name"] for r in view._filtered_recipes] == ["Ableton", "Zed"]
    assert view.top_bar.select_sort.value == view.sort_name_asc

    # Sort column 0 (App Name) DESC
    view.on_table_header_sort(0, view.table.columns[0], ascending=False)
    assert [r["app_name"] for r in view._filtered_recipes] == ["Zed", "Ableton"]
    assert view.top_bar.select_sort.value == view.sort_name_desc

    # Sort column 1 (Bundle ID) ASC
    view.on_table_header_sort(1, view.table.columns[1], ascending=True)
    assert [r["bundle_id"] for r in view._filtered_recipes] == ["com.ableton.live", "dev.zed.Zed"]

    # Sort column 2 (Strategy) ASC
    view.on_table_header_sort(2, view.table.columns[2], ascending=True)
    assert [r["strategy"] for r in view._filtered_recipes] == ["hard_clone", "soft_clone"]
    assert view.top_bar.select_sort.value == view.sort_strategy

    # Sort column 3 (Origin) ASC (Builtin first)
    view.on_table_header_sort(3, view.table.columns[3], ascending=True)
    assert [r["is_builtin"] for r in view._filtered_recipes] == [True, False]


def test_recipe_list_view_multi_select_and_button_states():
    view = RecipeListView()
    view._filtered_recipes = [
        {"app_name": "CustomApp1", "bundle_id": "com.custom.app1", "strategy": "hard_clone", "is_builtin": False, "recipe": MagicMock()},
        {"app_name": "CustomApp2", "bundle_id": "com.custom.app2", "strategy": "soft_clone", "is_builtin": False, "recipe": MagicMock()},
        {"app_name": "BuiltinApp1", "bundle_id": "com.builtin.app1", "strategy": "hard_clone", "is_builtin": True, "recipe": MagicMock()},
    ]

    # 1. Zero selection
    with patch.object(view, "get_selected_recipe_items", return_value=[]):
        view.on_table_select(view.table)
        assert view.btn_edit.enabled is False
        assert view.btn_delete.enabled is False
        assert "🗑️" in view.btn_delete.text

    # 2. Single custom selection
    with patch.object(view, "get_selected_recipe_items", return_value=[view._filtered_recipes[0]]):
        view.on_table_select(view.table)
        assert view.btn_edit.enabled is True
        assert view.btn_delete.enabled is True
        assert "🗑️" in view.btn_delete.text

    # 3. Single built-in selection
    with patch.object(view, "get_selected_recipe_items", return_value=[view._filtered_recipes[2]]):
        view.on_table_select(view.table)
        assert view.btn_edit.enabled is True
        assert view.btn_delete.enabled is False

    # 4. Multiple custom selection (2 items)
    with patch.object(view, "get_selected_recipe_items", return_value=[view._filtered_recipes[0], view._filtered_recipes[1]]):
        view.on_table_select(view.table)
        assert view.btn_edit.enabled is False
        assert view.btn_delete.enabled is True
        assert "(2)" in view.btn_delete.text

    # 5. Mixed selection (1 custom + 1 built-in)
    with patch.object(view, "get_selected_recipe_items", return_value=[view._filtered_recipes[0], view._filtered_recipes[2]]):
        view.on_table_select(view.table)
        assert view.btn_edit.enabled is False
        assert view.btn_delete.enabled is True
        assert "(1)" in view.btn_delete.text

    # 6. All built-in multi selection (2 built-in items)
    builtin2 = {"app_name": "BuiltinApp2", "bundle_id": "com.builtin.app2", "strategy": "hard_clone", "is_builtin": True, "recipe": MagicMock()}
    with patch.object(view, "get_selected_recipe_items", return_value=[view._filtered_recipes[2], builtin2]):
        view.on_table_select(view.table)
        assert view.btn_edit.enabled is False
        assert view.btn_delete.enabled is False



