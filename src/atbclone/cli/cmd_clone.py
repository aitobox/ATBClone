"""CLI command for cloning macOS applications."""

import sys
from pathlib import Path
import click
from rich.console import Console

from atbclone.core.app_inspector import AppInspector
from atbclone.core.clone_task import CloneTask
from atbclone.core.engines import HardCloneEngine, SoftCloneEngine
from atbclone.executor.runner import CloneError
from atbclone.recipes.loader import RecipeLoader

console = Console()


@click.command()
@click.argument("app_path", type=click.Path(exists=True))
@click.option("--name", help="分身名称")
@click.option("--output-dir", default=str(Path.home() / "Applications"), help="输出目录")
def clone(app_path: str, name: str | None, output_dir: str) -> None:
    """克隆应用"""
    out_path = Path(output_dir).expanduser()
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
    needs_admin = not dest_path.is_relative_to(Path.home())

    console.print(f"[bold green]Starting clone:[/bold green] {info.app_name} -> {clone_name}", soft_wrap=True)
    try:
        if recipe.strategy == "soft_clone":
            SoftCloneEngine.execute(task, needs_admin)
        else:
            HardCloneEngine.execute(task, needs_admin)
        console.print(f"[bold green]Success![/bold green] Clone created at {dest_path}", soft_wrap=True)
    except (CloneError, Exception) as e:
        console.print(f"[bold red]Error:[/bold red] {e}", soft_wrap=True)
        sys.exit(1)
