"""CLI command for probing a macOS application and generating an ATBClone recipe."""

import json
import sys
from pathlib import Path
import click
import yaml  # type: ignore[import-untyped]
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from atbclone.core.app_prober import AppProber
from atbclone.core.i18n import t
from atbclone.core.logger import get_logger
from atbclone.recipes.loader import RecipeLoader

console = Console()
logger = get_logger("cli.probe")


@click.command()
@click.argument("app_path", type=click.Path(exists=True))
@click.option("--save", is_flag=True, help="Save recipe to local recipe repository (~/ATBClone/recipes/<bundle_id>.yaml).")
@click.option("-o", "--output", type=click.Path(), help="Save generated recipe YAML to specified file path.")
@click.option("--json", "json_mode", is_flag=True, help="Output probe results in JSON format.")
def probe(app_path: str, save: bool, output: str | None, json_mode: bool) -> None:
    """Probe application architecture, entitlements, and recommended recipe."""
    target = Path(app_path).expanduser().resolve()
    if not target.exists() or not str(target).endswith(".app"):
        console.print(t("probe_err_invalid_app", app_path=app_path), soft_wrap=True)
        sys.exit(1)

    logger.info(f"Probing application at '{target}'")
    try:
        result = AppProber.analyze(target)
    except Exception as e:
        logger.error(f"Failed to probe application '{target}': {e}")
        console.print(t("probe_err_failed", error=e), soft_wrap=True)
        sys.exit(1)

    info = result.app_info
    recipe = result.recipe
    logger.info(f"Probe completed for '{info.app_name}' (bundle='{info.bundle_id}', strategy='{recipe.strategy}', sandbox={result.has_sandbox})")

    recipe_dict = {
        "bundle_id": recipe.bundle_id,
        "app_name": recipe.app_name,
        "strategy": recipe.strategy,
        "strip_sandbox": recipe.strip_sandbox,
    }
    if recipe.environment_injection:
        recipe_dict["environment_injection"] = recipe.environment_injection
    if recipe.launch_args:
        recipe_dict["launch_args"] = recipe.launch_args

    yaml_str = yaml.dump(recipe_dict, sort_keys=False, allow_unicode=True)

    if json_mode:
        data = {
            "app_name": info.app_name,
            "bundle_id": info.bundle_id,
            "executable": str(info.executable),
            "has_sandbox": result.has_sandbox,
            "frameworks": result.frameworks,
            "strategy": result.strategy,
            "reason": result.reason,
            "recipe": recipe_dict,
        }
        click.echo(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Key", style="bold cyan")
        table.add_column("Value")

        table.add_row(t("probe_row_app_name"), info.app_name)
        table.add_row(t("probe_row_bundle_id"), info.bundle_id)
        table.add_row(t("probe_row_executable"), str(info.executable))
        table.add_row(
            t("probe_row_sandbox"),
            "[red]Yes (com.apple.security.app-sandbox)[/red]" if result.has_sandbox else "[green]No (Non-sandboxed)[/green]",
        )
        table.add_row(
            t("probe_row_frameworks"),
            ", ".join(result.frameworks) if result.frameworks else "Native Cocoa / C++ / Qt",
        )
        table.add_row(t("probe_row_strategy"), f"[bold green]{result.strategy}[/bold green]")
        table.add_row(t("probe_row_reason"), result.reason)

        console.print(Panel(table, title=t("probe_title"), border_style="cyan"))
        console.print(f"{t('probe_yaml_header')}")
        console.print(yaml_str.strip())
        console.print("[bold]-------------------------[/bold]\n")

    if save:
        target_dir = RecipeLoader.get_local_dir()
        target_dir.mkdir(parents=True, exist_ok=True)
        target_file = target_dir / f"{info.bundle_id}.yaml"
        target_file.write_text(yaml_str, encoding="utf-8")
        logger.info(f"Saved probed recipe to '{target_file}'")
        console.print(t("probe_saved_to", path=target_file), soft_wrap=True)
    elif output:
        out_file = Path(output).expanduser().resolve()
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(yaml_str, encoding="utf-8")
        logger.info(f"Saved probed recipe to '{out_file}'")
        console.print(t("probe_saved_to", path=out_file), soft_wrap=True)
