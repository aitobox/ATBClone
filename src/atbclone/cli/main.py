import click
from rich.console import Console

from .cmd_clone import clone

console = Console()


@click.group()
def cli():
    """ATBClone - macOS 应用多开引擎"""


cli.add_command(clone)


if __name__ == "__main__":
    cli()

