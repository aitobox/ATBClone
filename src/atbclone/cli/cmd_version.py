"""CLI command to display version and environment information."""

import platform
import sys

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from atbclone import __version__
from atbclone.core.config import DEFAULT_DATA_DIR, DEFAULT_STATE_FILE
from atbclone.core.i18n import t

console = Console()


@click.command()
@click.option("--short", "-s", is_flag=True, help="Only output the version number.")
def version(short: bool) -> None:
    """Display ATBClone version and environment information."""
    if short:
        console.print(__version__)
        return

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Key", style="bold cyan")
    table.add_column("Value", style="white")

    table.add_row(t("version_row_version"), f"v{__version__}")
    table.add_row(t("version_row_python"), f"{platform.python_implementation()} {platform.python_version()}")
    table.add_row(t("version_row_platform"), f"{platform.system()} {platform.release()} ({platform.machine()})")
    table.add_row(t("version_row_executable"), sys.executable)
    table.add_row(t("version_row_state"), str(DEFAULT_STATE_FILE))
    table.add_row(t("version_row_data"), str(DEFAULT_DATA_DIR))

    panel = Panel(
        table,
        title=t("version_panel_title"),
        border_style="green",
        expand=False,
    )
    console.print(panel)
