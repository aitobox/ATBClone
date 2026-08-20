"""Doctor command for checking environment prerequisites."""

import subprocess
import sys
import click
from rich.console import Console

from atbclone.core.i18n import t
from atbclone.core.logger import get_logger

console = Console()
logger = get_logger("cli.doctor")


@click.command()
def doctor():
    """Check environment prerequisites (xcode-select, codesign, PlistBuddy)."""
    checks = {
        "codesign": "which codesign",
        "xcode-select": "xcode-select -p",
        "PlistBuddy": "ls /usr/libexec/PlistBuddy",
    }
    all_passed = True

    logger.info("Running environment health checks")
    console.print(t("doctor_running_checks"))
    for name, cmd in checks.items():
        try:
            out = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, text=True).strip()
            console.print(f"[green]✓ {name}[/green]: {out}")
            logger.info(f"Check passed: {name} -> {out}")
        except subprocess.CalledProcessError:
            console.print(f"[red]✗ {name}[/red]: {t('doctor_missing')}")
            logger.error(f"Check failed: {name} is missing or returned error")
            all_passed = False

    if not all_passed:
        logger.error("Environment checks completed with failures")
        sys.exit(1)
    logger.info("All environment health checks passed successfully")
