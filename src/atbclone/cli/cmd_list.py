"""CLI command for listing cloned applications."""

from datetime import datetime
import click
from rich.console import Console
from rich.table import Table

from atbclone.core.i18n import t
from atbclone.core.state import StateManager

console = Console()


def _format_created_at(created_at: str) -> str:
    """Format created_at timestamp string for display."""
    if not created_at:
        return ""
    try:
        dt = datetime.fromisoformat(created_at)
        if dt.tzinfo is not None:
            return dt.astimezone().strftime("%Y-%m-%d %H:%M")
        if len(created_at) <= 10:
            return created_at
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return created_at[:16] if len(created_at) >= 16 else created_at


@click.command(name="list")
def list_clones() -> None:
    """List all cloned applications."""
    records = StateManager().load()
    if not records:
        console.print(t("list_no_clones"))
        return

    table = Table()
    table.add_column(t("list_col_name"))
    table.add_column(t("list_col_source_app"))
    table.add_column(t("list_col_bundle_id"))
    table.add_column(t("list_col_strategy"))
    table.add_column(t("list_col_created_at"))
    table.add_column(t("list_col_proxy"))

    for r in records:
        proxy_display = r.proxy_summary if r.proxy_enabled else t("list_proxy_disabled")
        table.add_row(
            r.clone_name,
            r.source_app,
            r.bundle_id,
            r.strategy,
            _format_created_at(r.created_at),
            proxy_display,
        )

    console.print(table)
