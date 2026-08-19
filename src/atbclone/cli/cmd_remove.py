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
    "--with-data/--keep-data",
    "with_data",
    default=None,
    help="Also delete or keep the data directory.",
)
@click.option(
    "--no-with-data",
    "no_with_data",
    is_flag=True,
    hidden=True,
    help="Alias for --keep-data",
)
def remove(clone_name: str, with_data: bool | None, no_with_data: bool) -> None:
    """Remove a cloned application."""
    sm = StateManager()
    record = sm.get(clone_name)
    if record is None:
        console.print(t("remove_err_not_found", clone_name=clone_name))
        sys.exit(1)

    if no_with_data:
        with_data = False

    delete_data = False
    if with_data is True:
        delete_data = True
    elif with_data is False:
        delete_data = False
    else:
        # Prompt interactively
        try:
            delete_data = click.confirm(
                t("remove_prompt_delete_data", data_dir=record.data_dir),
                default=False,
            )
        except click.Abort:
            sys.exit(1)

    needs_admin = (
        not Path(record.dest_path).is_relative_to(Path.home())
        or (delete_data and not Path(record.data_dir).is_relative_to(Path.home()))
    )

    lines = [
        "#!/bin/bash",
        "set -e",
        f"rm -rf {shlex.quote(record.dest_path)}",
    ]

    if delete_data:
        lines.append(f"rm -rf {shlex.quote(record.data_dir)}")

    script = "\n".join(lines) + "\n"

    try:
        Runner.run(script, needs_admin)
    except (CloneError, Exception) as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)

    sm.remove(clone_name)
    console.print(t("remove_success", clone_name=clone_name))
