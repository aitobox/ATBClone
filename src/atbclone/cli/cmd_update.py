"""CLI command for updating cloned applications."""

import shlex
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
import click
from rich.console import Console

from atbclone.core.app_inspector import AppInspector
from atbclone.core.clone_task import CloneTask
from atbclone.core.engines import HardCloneEngine, SoftCloneEngine
from atbclone.core.i18n import t
from atbclone.core.logger import get_logger
from atbclone.core.state import StateManager
from atbclone.executor.runner import CloneError, Runner
from atbclone.recipes.loader import RecipeLoader

console = Console()
logger = get_logger("cli.update")


@click.command(name="update")
@click.argument("clone_name")
def update(clone_name: str) -> None:
    """Update a cloned application."""
    sm = StateManager()
    record = sm.get(clone_name)
    if record is None:
        console.print(t("update_err_not_found", clone_name=clone_name))
        sys.exit(1)

    if not Path(record.source_path).exists():
        console.print(t("update_err_source_not_found", source_path=record.source_path))
        sys.exit(1)

    dest_path = Path(record.dest_path)
    needs_admin = not dest_path.is_relative_to(Path.home())

    logger.info(f"Starting update for clone '{clone_name}' (source='{record.source_path}', strategy='{record.strategy}')")
    console.print(t("update_starting", clone_name=clone_name))

    lines = [
        "#!/bin/bash",
        "set -e",
        f"rm -rf {shlex.quote(str(dest_path))}",
    ]
    script = "\n".join(lines) + "\n"

    try:
        Runner.run(script, needs_admin)
    except (CloneError, Exception) as e:
        logger.error(f"Failed to clear old bundle for '{clone_name}': {e}")
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)

    try:
        info = AppInspector.inspect(record.source_path)
        recipe = RecipeLoader.match(info.bundle_id)
        data_dir = Path(record.data_dir)
        existing_records = sm.load()
        existing_bundle_ids = {r.new_bundle_id for r in existing_records if r.new_bundle_id and r.clone_name != record.clone_name}
        new_bundle_id = record.new_bundle_id or AppInspector.resolve_bundle_id(
            record.bundle_id,
            clone_name=record.clone_name,
            existing_bundle_ids=existing_bundle_ids,
        )

        task = CloneTask(
            source=info,
            dest_path=dest_path,
            data_dir=data_dir,
            recipe=recipe,
            clone_name=record.clone_name,
            new_bundle_id=new_bundle_id,
        )

        if record.proxy_enabled and record.proxy_summary:
            parsed = urlparse(record.proxy_summary)
            task.recipe.proxy.enabled = True
            if parsed.scheme:
                task.recipe.proxy.type = parsed.scheme  # type: ignore[assignment]
            if parsed.hostname:
                task.recipe.proxy.host = parsed.hostname
            if parsed.port:
                task.recipe.proxy.port = parsed.port
            if parsed.username:
                task.recipe.proxy.username = parsed.username
            if parsed.password:
                task.recipe.proxy.password = parsed.password

        if record.strategy == "soft_clone":
            SoftCloneEngine.execute(task, needs_admin)
        else:
            HardCloneEngine.execute(task, needs_admin)

        record.created_at = datetime.now(timezone.utc).isoformat()
        sm.add(record)

        logger.info(f"Clone '{clone_name}' updated successfully")
        console.print(t("update_success", clone_name=clone_name))
    except (CloneError, Exception) as e:
        logger.error(f"Failed to update clone '{clone_name}': {e}")
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)
