import click
from rich.console import Console

console = Console()


@click.group()
def cli():
    """ATBClone - macOS 应用多开引擎"""


if __name__ == "__main__":
    cli()
