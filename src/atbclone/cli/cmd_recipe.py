"""CLI commands for managing and inspecting recipes."""

import sys
from pathlib import Path
import click
import yaml  # type: ignore[import-untyped]
from rich.console import Console
from rich.table import Table

from atbclone.core.i18n import t
from atbclone.core.logger import get_logger
from atbclone.recipes.loader import RecipeLoader

console = Console()
logger = get_logger("cli.recipe")


@click.group(name="recipe")
def recipe() -> None:
    """Manage and inspect application clone recipes."""


@recipe.command(name="list")
def recipe_list() -> None:
    """List all built-in recipes."""
    logger.info("Listing all built-in recipes")
    builtin_dir = RecipeLoader.BUILTIN_DIR
    yaml_files = sorted(builtin_dir.glob("*.yaml"))

    recipes_data = []
    for yf in yaml_files:
        with open(yf, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            recipes_data.append(data)

    # Sort rows by strategy (hard_clone first), then by app_name
    recipes_data.sort(
        key=lambda r: (
            0 if r.get("strategy") == "hard_clone" else 1,
            str(r.get("app_name", "")).lower(),
        )
    )

    table = Table()
    table.add_column(t("recipe_col_bundle_id"))
    table.add_column(t("recipe_col_app_name"))
    table.add_column(t("recipe_col_strategy"))
    table.add_column(t("recipe_col_strip_sandbox"))

    for r in recipes_data:
        strip_sb = "✅" if r.get("strip_sandbox", False) else "✘"
        table.add_row(
            str(r.get("bundle_id", "")),
            str(r.get("app_name", "")),
            str(r.get("strategy", "")),
            strip_sb,
        )

    console.print(table)


@recipe.command(name="show")
@click.argument("bundle_id")
def recipe_show(bundle_id: str) -> None:
    """Show recipe details for a specific bundle ID."""
    logger.info(f"Showing recipe details for bundle_id='{bundle_id}'")
    local_file = RecipeLoader.get_local_dir() / f"{bundle_id}.yaml"
    builtin_file = RecipeLoader.BUILTIN_DIR / f"{bundle_id}.yaml"

    if local_file.is_file():
        console.print(t("recipe_local_override"))
        console.print(local_file.read_text(encoding="utf-8").rstrip())
    elif builtin_file.is_file():
        console.print(builtin_file.read_text(encoding="utf-8").rstrip())
    else:
        logger.error(f"Recipe not found for bundle_id='{bundle_id}'")
        console.print(t("recipe_err_not_found", bundle_id=bundle_id))
        sys.exit(1)


from .cmd_probe import probe as probe_cmd

recipe.add_command(probe_cmd, name="probe")
