"""CLI command to display version and environment information."""

import platform
import sys
from pathlib import Path
import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from atbclone import __version__
from atbclone.core.state import STATE_FILE

console = Console()


@click.command()
@click.option("--short", "-s", is_flag=True, help="Only output the version number.")
def version(short: bool) -> None:
    """显示 ATBClone 版本及运行环境信息"""
    if short:
        console.print(__version__)
        return

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Key", style="bold cyan")
    table.add_column("Value", style="white")

    table.add_row("ATBClone Version", f"v{__version__}")
    table.add_row("Python Runtime", f"{platform.python_implementation()} {platform.python_version()}")
    table.add_row("Platform", f"{platform.system()} {platform.release()} ({platform.machine()})")
    table.add_row("Executable", sys.executable)
    table.add_row("State Storage", str(STATE_FILE))
    table.add_row("Data Directory", str(Path.home() / ".AIToBox" / "Data"))

    panel = Panel(
        table,
        title="[bold green]ATBClone System Information[/bold green]",
        border_style="green",
        expand=False,
    )
    console.print(panel)
