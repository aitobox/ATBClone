"""Recipe Service for async recipe CRUD."""

import asyncio
from pathlib import Path
import yaml

from atbclone.core.config import DEFAULT_RECIPES_DIR
from atbclone.core.logger import get_logger
from atbclone.recipes.loader import RecipeLoader
from atbclone.recipes.models import Recipe

logger = get_logger("gui.recipe_service")


class RecipeService:
    def __init__(self, custom_recipes_dir: Path | None = None):
        self.custom_recipes_dir = Path(custom_recipes_dir or DEFAULT_RECIPES_DIR)

    async def list_all_recipes(self) -> list[dict]:
        loop = asyncio.get_running_loop()

        def _list():
            recipes_map: dict[str, dict] = {}

            # Built-in recipes
            if RecipeLoader.BUILTIN_DIR.is_dir():
                for f in sorted(RecipeLoader.BUILTIN_DIR.glob("*.yaml")):
                    try:
                        r = RecipeLoader._load_file(f)
                        recipes_map[r.bundle_id] = {
                            "bundle_id": r.bundle_id,
                            "app_name": r.app_name,
                            "strategy": r.strategy,
                            "is_builtin": True,
                            "path": str(f),
                            "recipe": r,
                        }
                    except Exception:
                        pass

            # Local custom overrides / additions
            if self.custom_recipes_dir.is_dir():
                for f in sorted(self.custom_recipes_dir.glob("*.yaml")):
                    try:
                        r = RecipeLoader._load_file(f)
                        recipes_map[r.bundle_id] = {
                            "bundle_id": r.bundle_id,
                            "app_name": r.app_name,
                            "strategy": r.strategy,
                            "is_builtin": False,
                            "path": str(f),
                            "recipe": r,
                        }
                    except Exception:
                        pass

            return list(recipes_map.values())

        return await loop.run_in_executor(None, _list)

    async def get_recipe(self, bundle_id: str) -> Recipe | None:
        loop = asyncio.get_running_loop()

        def _get():
            local_file = self.custom_recipes_dir / f"{bundle_id}.yaml"
            if local_file.is_file():
                return RecipeLoader._load_file(local_file)
            builtin_file = RecipeLoader.BUILTIN_DIR / f"{bundle_id}.yaml"
            if builtin_file.is_file():
                return RecipeLoader._load_file(builtin_file)
            return None

        return await loop.run_in_executor(None, _get)

    async def save_custom_recipe(self, recipe: Recipe) -> Path:
        loop = asyncio.get_running_loop()

        def _save():
            self.custom_recipes_dir.mkdir(parents=True, exist_ok=True)
            target_path = self.custom_recipes_dir / f"{recipe.bundle_id}.yaml"
            data = recipe.model_dump()
            with open(target_path, "w", encoding="utf-8") as f:
                yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)
            logger.info(f"Saved custom recipe for '{recipe.app_name}' (bundle='{recipe.bundle_id}') at '{target_path}'")
            return target_path

        return await loop.run_in_executor(None, _save)

    async def duplicate_recipe(self, original: Recipe) -> Recipe:
        """Create a custom override copy of a recipe preserving its original bundle_id and app_name."""
        data = original.model_dump()
        new_recipe = Recipe(**data)
        logger.info(f"Creating custom recipe override for '{original.app_name}' (bundle='{original.bundle_id}')")
        await self.save_custom_recipe(new_recipe)
        return new_recipe

    async def delete_custom_recipe(self, bundle_id: str) -> bool:
        loop = asyncio.get_running_loop()

        def _delete():
            target_path = self.custom_recipes_dir / f"{bundle_id}.yaml"
            if target_path.is_file():
                target_path.unlink()
                logger.info(f"Deleted custom recipe for bundle='{bundle_id}'")
                return True
            logger.warning(f"Custom recipe for bundle='{bundle_id}' not found for deletion")
            return False

        return await loop.run_in_executor(None, _delete)

