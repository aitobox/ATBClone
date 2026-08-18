import click
from rich.console import Console

from .cmd_clone import clone
from .cmd_doctor import doctor
from .cmd_list import list_clones
from .cmd_recipe import recipe
from .cmd_remove import remove
from .cmd_update import update

console = Console()


@click.group()
def cli():
    """ATBClone - macOS 应用多开引擎"""


cli.add_command(clone)
cli.add_command(doctor)
cli.add_command(list_clones)
cli.add_command(recipe)
cli.add_command(remove)
cli.add_command(update)


if __name__ == "__main__":
    cli()

