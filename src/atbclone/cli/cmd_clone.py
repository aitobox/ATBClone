"""CLI command for cloning macOS applications."""

import sys
from datetime import datetime, timezone
from pathlib import Path
import click
from rich.console import Console

from atbclone.core.app_inspector import AppInspector
from atbclone.core.app_prober import AppProber
from atbclone.core.clone_task import CloneTask
from atbclone.core.config import DEFAULT_APPS_DIR, DEFAULT_DATA_DIR
from atbclone.core.engines import HardCloneEngine, SoftCloneEngine
from atbclone.core.i18n import t
from atbclone.core.locale import SUPPORTED_LANGUAGES
from atbclone.core.logger import get_logger
from atbclone.core.state import CloneRecord, StateManager
from atbclone.executor.runner import CloneError
from atbclone.recipes import RecipeLoader, supports_data_dir

console = Console()
logger = get_logger("cli.clone")


@click.command()
@click.argument("app_path", type=click.Path(exists=True))
@click.option("--name", help="Clone application name.")
@click.option("--display-name", default=None, help="Display name shown in Dock/Finder (supports Unicode, defaults to --name).")
@click.option("--icon", default=None, type=click.Path(exists=True, dir_okay=False), help="Path to custom icon file (.icns, defaults to original app icon).")
@click.option("--strategy", default=None, type=click.Choice(["hard_clone", "soft_clone"]), help="Override cloning strategy (hard_clone or soft_clone).")
@click.option("--language", "-l", default="system", type=click.Choice(list(SUPPORTED_LANGUAGES.keys())), help="Target locale/language (system, zh-Hans, zh-Hant, en, ja, ko).")
@click.option("--output-dir", default=str(DEFAULT_APPS_DIR), help="Target output directory for the cloned application.")
@click.option("--data-dir", default=None, help="Custom data storage directory for this clone.")
@click.option("--proxy-host", default=None, help="Proxy host (overrides recipe)")
@click.option("--proxy-port", default=None, type=int, help="Proxy port")
@click.option("--proxy-type", default="http", type=click.Choice(["http", "https", "socks5"]), help="Proxy type")
def clone(
    app_path: str,
    name: str | None,
    display_name: str | None,
    icon: str | None,
    strategy: str | None,
    language: str,
    output_dir: str,
    data_dir: str | None,
    proxy_host: str | None,
    proxy_port: int | None,
    proxy_type: str,
) -> None:
    """Clone a macOS application."""
    # Validate icon file extension early for a friendly error message
    if icon and not icon.lower().endswith(".icns"):
        console.print(t("clone_err_icon_icns"), soft_wrap=True)
        sys.exit(1)

    out_path = Path(output_dir).expanduser().resolve()
    out_path.mkdir(parents=True, exist_ok=True)

    info = AppInspector.inspect(app_path)
    if getattr(info, "is_ios_app", False):
        console.print(t("clone_err_ios_wrapper_unsupported_cli"), soft_wrap=True)
        sys.exit(1)

    if RecipeLoader.has_recipe(info.bundle_id):
        recipe = RecipeLoader.match(info.bundle_id)
    else:
        console.print(t("clone_no_recipe_found", bundle_id=info.bundle_id), soft_wrap=True)
        console.print(t("clone_probing"), soft_wrap=True)
        probe_result = AppProber.analyze(app_path)
        recipe = probe_result.recipe
        console.print(
            t("clone_probed_strategy", strategy=recipe.strategy, sandbox="Yes" if probe_result.has_sandbox else "No"),
            soft_wrap=True,
        )

    if strategy:
        recipe.strategy = strategy  # type: ignore[assignment]

    if data_dir:
        if not supports_data_dir(recipe):
            console.print(t("clone_err_data_dir_not_supported", app_name=info.app_name), soft_wrap=True)
            sys.exit(1)
        target_data_dir = Path(data_dir).expanduser().resolve()
    else:
        target_data_dir = DEFAULT_DATA_DIR / (name or info.app_name)

    clone_name, num = AppInspector.next_available_name(name or info.app_name, out_path)
    existing_records = StateManager().load()
    existing_bundle_ids = {r.new_bundle_id for r in existing_records if r.new_bundle_id}
    new_bundle_id = AppInspector.resolve_bundle_id(
        info.bundle_id,
        clone_name=clone_name,
        existing_bundle_ids=existing_bundle_ids,
    )
    dest_path = out_path / f"{clone_name}.app"

    # If data_dir was not specified, compute data_dir using the resolved unique clone_name
    if not data_dir:
        target_data_dir = DEFAULT_DATA_DIR / clone_name

    task = CloneTask(
        source=info,
        dest_path=dest_path,
        data_dir=target_data_dir,
        recipe=recipe,
        clone_name=clone_name,
        new_bundle_id=new_bundle_id,
        display_name=display_name or None,
        icon_path=Path(icon) if icon else None,
        language=language,
    )

    if proxy_host:
        task.recipe.proxy.enabled = True
        task.recipe.proxy.host = proxy_host
        task.recipe.proxy.port = proxy_port or task.recipe.proxy.port
        task.recipe.proxy.type = proxy_type

    needs_admin = not dest_path.is_relative_to(Path.home())

    logger.info(f"Starting clone creation: name='{clone_name}', source='{app_path}', strategy='{recipe.strategy}', dest='{dest_path}', language='{language}'")
    console.print(t("starting_clone", app_name=info.app_name, clone_name=clone_name), soft_wrap=True)
    try:
        if recipe.strategy == "soft_clone":
            SoftCloneEngine.execute(task, needs_admin)
        else:
            HardCloneEngine.execute(task, needs_admin)

        record = CloneRecord(
            clone_name=clone_name,
            source_app=info.app_name,
            source_path=str(app_path),
            bundle_id=info.bundle_id,
            strategy=recipe.strategy,
            dest_path=str(dest_path),
            data_dir=str(target_data_dir),
            created_at=datetime.now(timezone.utc).isoformat(),
            proxy_enabled=task.recipe.proxy.enabled,
            proxy_summary=task.recipe.proxy.url if task.recipe.proxy.enabled else "",
            new_bundle_id=new_bundle_id,
            language=language,
            display_name=display_name or None,
        )
        StateManager().add(record)

        logger.info(f"Clone '{clone_name}' created successfully at '{dest_path}'")
        console.print(t("clone_success", dest_path=dest_path), soft_wrap=True)
    except (CloneError, Exception) as e:
        logger.error(f"Failed to create clone '{clone_name}': {e}")
        console.print(t("clone_error", error=e), soft_wrap=True)
        sys.exit(1)
