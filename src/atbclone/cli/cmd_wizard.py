"""CLI command for wizard interactive cloning."""

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


@click.command(name="wizard")
def wizard() -> None:
    """交互式分身向导"""
    console.print("🧙 ATBClone 小向导\n")

    # 1. 请输入要分身的 .app 路径
    while True:
        app_path_input = click.prompt("请输入要分身的 .app 路径")
        app_path_str = app_path_input.strip().strip("'\"")
        app_path = Path(app_path_str).expanduser().resolve()
        if not (app_path.exists() and (app_path_str.rstrip("/").endswith(".app") or app_path.name.endswith(".app"))):
            console.print("[bold red]错误: 路径不存在或不是 .app 应用，请重新输入。[/bold red]")
            continue
        break

    # 2. 检测应用...
    console.print("\n检测应用...")
    info = AppInspector.inspect(str(app_path))
    recipe = RecipeLoader.match(info.bundle_id)
    console.print(f"应用: {info.app_name} ({info.bundle_id})")
    console.print(f"策略: {recipe.strategy}\n")

    # 3. 分身名称 [default: auto-numbered]
    out_path = Path.home() / "Applications"
    clone_name, num = AppInspector.next_available_name(info.app_name, out_path)
    clone_name = click.prompt("分身名称", default=clone_name)

    # 4. 输出目录 [default: ~/Applications]
    output_dir = click.prompt("输出目录", default=str(Path.home() / "Applications"))
    out_path = Path(output_dir).expanduser().resolve()

    # 5. 是否配置代理?
    use_proxy = click.confirm("是否配置代理", default=False)
    proxy_host = None
    proxy_port = None
    proxy_type = "http"
    if use_proxy:
        proxy_host = click.prompt("代理地址", default="127.0.0.1")
        proxy_port = click.prompt("代理端口", default=1080, type=int)
        proxy_type = click.prompt("代理类型", default="http", type=click.Choice(["http", "socks5"]))

    # 6. 确认信息
    dest_path = out_path / f"{clone_name}.app"
    proxy_status = "已配置" if use_proxy else "未配置"
    console.print("\n即将创建分身:")
    console.print(f"  名称: {clone_name}")
    console.print(f"  目标: {dest_path}")
    console.print(f"  策略: {recipe.strategy}")
    console.print(f"  代理: {proxy_status}\n")

    if not click.confirm("确认执行", default=True):
        return

    # 7. 执行 clone (same logic as cmd_clone.py)
    new_bundle_id = f"{info.bundle_id}.atb{num}"
    data_dir = Path.home() / ".atbclone" / "Data" / clone_name

    task = CloneTask(
        source=info,
        dest_path=dest_path,
        data_dir=data_dir,
        recipe=recipe,
        clone_name=clone_name,
        new_bundle_id=new_bundle_id,
    )

    if use_proxy and proxy_host:
        task.recipe.proxy.enabled = True
        task.recipe.proxy.host = proxy_host
        task.recipe.proxy.port = proxy_port or task.recipe.proxy.port
        task.recipe.proxy.type = proxy_type

    out_path.mkdir(parents=True, exist_ok=True)
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
