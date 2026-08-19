"""CLI command for removing cloned applications."""

import sys
import shlex
from pathlib import Path
import click
from rich.console import Console

from atbclone.core.i18n import t
from atbclone.core.state import StateManager
from atbclone.executor.runner import CloneError, Runner

console = Console()


@click.command(name="remove")
@click.argument("clone_name")
@click.option(
    "--with-data/--no-with-data",
    default=False,
    help="Also delete the data directory.",
)
def remove(clone_name: str, with_data: bool) -> None:
    """Remove a cloned application."""
    sm = StateManager()
    record = sm.get(clone_name)
    if record is None:
        console.print(t("remove_err_not_found", clone_name=clone_name))
        sys.exit(1)

    needs_admin = not Path(record.dest_path).is_relative_to(Path.home())

    lines = [
        "#!/bin/bash",
        "set -e",
        f"rm -rf {shlex.quote(record.dest_path)}",
    ]

    if with_data:
        click.confirm(
            t("remove_confirm_data", data_dir=record.data_dir),
            abort=True,
        )
        lines.append(f"rm -rf {shlex.quote(record.data_dir)}")

    script = "\n".join(lines) + "\n"

    try:
        Runner.run(script, needs_admin)
    except (CloneError, Exception) as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)

    sm.remove(clone_name)
    console.print(t("remove_success", clone_name=clone_name))
