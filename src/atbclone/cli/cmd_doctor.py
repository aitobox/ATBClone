"""Doctor command for checking environment prerequisites."""

import subprocess
import sys
import click
from rich.console import Console

console = Console()


@click.command()
def doctor():
    """Check environment prerequisites (xcode-select, codesign, PlistBuddy)."""
    checks = {
        "codesign": "which codesign",
        "xcode-select": "xcode-select -p",
        "PlistBuddy": "ls /usr/libexec/PlistBuddy",
    }
    all_passed = True

    console.print("[bold]Running environment checks:[/bold]")
    for name, cmd in checks.items():
        try:
            out = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, text=True).strip()
            console.print(f"[green]✓ {name}[/green]: {out}")
        except subprocess.CalledProcessError:
            console.print(f"[red]✗ {name}[/red]: Missing! Run 'xcode-select --install'")
            all_passed = False

    if not all_passed:
        sys.exit(1)
