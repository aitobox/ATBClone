import click
from rich.console import Console

from atbclone import __version__
from .cmd_clone import clone
from .cmd_doctor import doctor
from .cmd_list import list_clones
from .cmd_probe import probe
from .cmd_recipe import recipe
from .cmd_remove import remove
from .cmd_update import update
from .cmd_version import version
from .cmd_wizard import wizard

console = Console()


@click.group()
@click.version_option(__version__, "-v", "--version", message="%(prog)s %(version)s")
def cli():
    """ATBClone - macOS application cloning engine."""


cli.add_command(clone)
cli.add_command(doctor)
cli.add_command(list_clones)
cli.add_command(probe)
cli.add_command(recipe)
cli.add_command(remove)
cli.add_command(update)
cli.add_command(version)
cli.add_command(wizard)



if __name__ == "__main__":
    cli()

