"""CLI command for removing cloned applications."""

import sys
import shlex
from pathlib import Path
import click
from rich.console import Console

from atbclone.core.state import StateManager
from atbclone.executor.runner import CloneError, Runner

console = Console()


@click.command(name="remove")
@click.argument("clone_name")
@click.option(
    "--with-data/--no-with-data",
    default=False,
    help="同时删除数据目录",
)
def remove(clone_name: str, with_data: bool) -> None:
    """删除已克隆的应用"""
    sm = StateManager()
    record = sm.get(clone_name)
    if record is None:
        console.print(f"[red]Error:[/red] Clone '{clone_name}' not found.")
        sys.exit(1)

    needs_admin = not Path(record.dest_path).is_relative_to(Path.home())

    lines = [
        "#!/bin/bash",
        "set -e",
        f"rm -rf {shlex.quote(record.dest_path)}",
    ]

    if with_data:
        click.confirm(
            f"Also delete data directory {record.data_dir}? This is irreversible.",
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
    console.print(f"[bold green]Success![/bold green] Removed clone '{clone_name}'")
