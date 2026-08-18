"""CLI command for cloning macOS applications."""

import sys
from datetime import datetime, timezone
from pathlib import Path
import click
from rich.console import Console

from atbclone.core.app_inspector import AppInspector
from atbclone.core.clone_task import CloneTask
from atbclone.core.engines import HardCloneEngine, SoftCloneEngine
from atbclone.core.state import CloneRecord, StateManager
from atbclone.executor.runner import CloneError
from atbclone.recipes.loader import RecipeLoader

console = Console()


@click.command()
@click.argument("app_path", type=click.Path(exists=True))
@click.option("--name", help="分身名称")
@click.option("--output-dir", default=str(Path.home() / "Applications"), help="输出目录")
@click.option("--proxy-host", default=None, help="Proxy host (overrides recipe)")
@click.option("--proxy-port", default=None, type=int, help="Proxy port")
@click.option("--proxy-type", default="http", type=click.Choice(["http", "socks5"]), help="Proxy type")
def clone(
    app_path: str,
    name: str | None,
    output_dir: str,
    proxy_host: str | None,
    proxy_port: int | None,
    proxy_type: str,
) -> None:
    """克隆应用"""
    out_path = Path(output_dir).expanduser().resolve()
    out_path.mkdir(parents=True, exist_ok=True)

    info = AppInspector.inspect(app_path)
    recipe = RecipeLoader.match(info.bundle_id)

    clone_name, num = AppInspector.next_available_name(name or info.app_name, out_path)
    new_bundle_id = f"{info.bundle_id}.atb{num}"
    dest_path = out_path / f"{clone_name}.app"
    data_dir = Path.home() / ".AIToBox" / "Data" / clone_name

    task = CloneTask(
        source=info,
        dest_path=dest_path,
        data_dir=data_dir,
        recipe=recipe,
        clone_name=clone_name,
        new_bundle_id=new_bundle_id,
    )

    if proxy_host:
        task.recipe.proxy.enabled = True
        task.recipe.proxy.host = proxy_host
        task.recipe.proxy.port = proxy_port or task.recipe.proxy.port
        task.recipe.proxy.type = proxy_type

    needs_admin = not dest_path.is_relative_to(Path.home())

    console.print(f"[bold green]Starting clone:[/bold green] {info.app_name} -> {clone_name}", soft_wrap=True)
    try:
        if recipe.strategy == "soft_clone":
            SoftCloneEngine.execute(task, needs_admin)
        else:
            HardCloneEngine.execute(task, needs_admin)

        record = CloneRecord(
            clone_name=clone_name,
            source_app=info.app_name,
            source_path=str(app_path),
            bundle_id=info.bundle_id,
            strategy=recipe.strategy,
            dest_path=str(dest_path),
            data_dir=str(data_dir),
            created_at=datetime.now(timezone.utc).isoformat(),
            proxy_enabled=task.recipe.proxy.enabled,
            proxy_summary=task.recipe.proxy.url if task.recipe.proxy.enabled else "",
            new_bundle_id=new_bundle_id,
        )
        StateManager().add(record)

        console.print(f"[bold green]Success![/bold green] Clone created at {dest_path}", soft_wrap=True)
    except (CloneError, Exception) as e:
        console.print(f"[bold red]Error:[/bold red] {e}", soft_wrap=True)
        sys.exit(1)
