"""CLI commands for managing and inspecting recipes."""

import sys
from pathlib import Path
import click
import yaml  # type: ignore[import-untyped]
from rich.console import Console
from rich.table import Table

from atbclone.recipes.loader import RecipeLoader

console = Console()


@click.group(name="recipe")
def recipe() -> None:
    """管理和查看应用克隆配方"""


@recipe.command(name="list")
def recipe_list() -> None:
    """列出所有内置配方"""
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
    table.add_column("Bundle ID")
    table.add_column("App Name")
    table.add_column("策略")
    table.add_column("Strip Sandbox")

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
    """查看指定应用的配方详情"""
    local_file = RecipeLoader.get_local_dir() / f"{bundle_id}.yaml"
    builtin_file = RecipeLoader.BUILTIN_DIR / f"{bundle_id}.yaml"

    if local_file.is_file():
        console.print("[yellow](local override)[/yellow]")
        console.print(local_file.read_text(encoding="utf-8").rstrip())
    elif builtin_file.is_file():
        console.print(builtin_file.read_text(encoding="utf-8").rstrip())
    else:
        console.print(f"[red]Error:[/red] Recipe for '{bundle_id}' not found.")
        sys.exit(1)
