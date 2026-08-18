import click
from rich.console import Console

from .cmd_clone import clone
from .cmd_doctor import doctor
from .cmd_list import list_clones

console = Console()


@click.group()
def cli():
    """ATBClone - macOS 应用多开引擎"""


cli.add_command(clone)
cli.add_command(doctor)
cli.add_command(list_clones)


if __name__ == "__main__":
    cli()

