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

    asyncio.run(_test())

