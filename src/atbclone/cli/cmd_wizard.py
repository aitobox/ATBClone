"""CLI command for wizard interactive cloning."""

import sys
from datetime import datetime, timezone
from pathlib import Path
import click
from rich.console import Console

from atbclone.core.app_inspector import AppInspector
from atbclone.core.clone_task import CloneTask
from atbclone.core.config import DEFAULT_DATA_DIR
from atbclone.core.engines import HardCloneEngine, SoftCloneEngine
from atbclone.core.i18n import t
from atbclone.core.state import CloneRecord, StateManager
from atbclone.executor.runner import CloneError
from atbclone.recipes import RecipeLoader, supports_data_dir

console = Console()


@click.command(name="wizard")
def wizard() -> None:
    """Interactive cloning wizard."""
    console.print(t("wizard_title"))

    # 1. App path
    while True:
        app_path_input = click.prompt(t("wizard_prompt_app_path"))
        app_path_str = app_path_input.strip().strip("'\"")
        app_path = Path(app_path_str).expanduser().resolve()
        if not (app_path.exists() and (app_path_str.rstrip("/").endswith(".app") or app_path.name.endswith(".app"))):
            console.print(t("wizard_err_invalid_app_path"))
            continue
        break

    # 2. Inspect app
    console.print(t("wizard_detecting_app"))
    info = AppInspector.inspect(str(app_path))
    recipe = RecipeLoader.match(info.bundle_id)
    console.print(t("wizard_app_info", app_name=info.app_name, bundle_id=info.bundle_id))
    console.print(t("wizard_strategy_info", strategy=recipe.strategy))

    # 3. Clone name
    out_path = Path.home() / "Applications"
    clone_name, num = AppInspector.next_available_name(info.app_name, out_path)
    clone_name = click.prompt(t("wizard_prompt_clone_name"), default=clone_name)

    # 4. Display name (Dock/Finder)
    display_name_input = click.prompt(
        t("wizard_prompt_display_name"),
        default="",
    )
    display_name: str | None = display_name_input.strip() or None

    # 5. Custom icon
    icon_path: Path | None = None
    while True:
        icon_input = click.prompt(t("wizard_prompt_icon"), default="")
        icon_str = icon_input.strip().strip("'\"")
        if not icon_str:
            break
        icon_candidate = Path(icon_str).expanduser().resolve()
        if not icon_candidate.exists():
            console.print(t("wizard_err_icon_not_found"))
            continue
        if not icon_str.lower().endswith(".icns"):
            console.print(t("wizard_err_icon_not_icns"))
            continue
        icon_path = icon_candidate
        break

    # 6. Output dir
    output_dir = click.prompt(t("wizard_prompt_output_dir"), default=str(Path.home() / "Applications"))
    out_path = Path(output_dir).expanduser().resolve()

    # 7. Data storage directory (if supported by recipe)
    if supports_data_dir(recipe):
        default_data_dir = str(DEFAULT_DATA_DIR / clone_name)
        data_dir_input = click.prompt(t("wizard_prompt_data_dir"), default=default_data_dir)
        target_data_dir = Path(data_dir_input).expanduser().resolve()
    else:
        target_data_dir = DEFAULT_DATA_DIR / clone_name

    # 8. Proxy setup
    use_proxy = click.confirm(t("wizard_prompt_use_proxy"), default=False)
    proxy_host = None
    proxy_port = None
    proxy_type = "http"
    if use_proxy:
        proxy_host = click.prompt(t("wizard_prompt_proxy_host"), default="127.0.0.1")
        proxy_port = click.prompt(t("wizard_prompt_proxy_port"), default=1080, type=int)
        proxy_type = click.prompt(t("wizard_prompt_proxy_type"), default="http", type=click.Choice(["http", "https", "socks5"]))

    # 9. Confirmation
    dest_path = out_path / f"{clone_name}.app"
    proxy_status = t("wizard_proxy_configured") if use_proxy else t("wizard_proxy_not_configured")
    console.print(t("wizard_confirm_title"))
    console.print(t("wizard_confirm_name", clone_name=clone_name))
    if display_name:
        console.print(t("wizard_confirm_display_name", display_name=display_name))
    if icon_path:
        console.print(t("wizard_confirm_icon", icon_path=icon_path))
    console.print(t("wizard_confirm_target", dest_path=dest_path))
    if supports_data_dir(recipe):
        console.print(t("wizard_confirm_data_dir", data_dir=target_data_dir))
    console.print(t("wizard_confirm_strategy", strategy=recipe.strategy))
    console.print(t("wizard_confirm_proxy", proxy_status=proxy_status))

    if not click.confirm(t("wizard_prompt_confirm"), default=True):
        return

    # 10. Execute clone
    existing_records = StateManager().load()
    existing_bundle_ids = {r.new_bundle_id for r in existing_records if r.new_bundle_id}
    new_bundle_id = AppInspector.resolve_bundle_id(
        info.bundle_id,
        clone_name=clone_name,
        existing_bundle_ids=existing_bundle_ids,
    )

    task = CloneTask(
        source=info,
        dest_path=dest_path,
        data_dir=target_data_dir,
        recipe=recipe,
        clone_name=clone_name,
        new_bundle_id=new_bundle_id,
        display_name=display_name,
        icon_path=icon_path,
    )

    if use_proxy and proxy_host:
        task.recipe.proxy.enabled = True
        task.recipe.proxy.host = proxy_host
        task.recipe.proxy.port = proxy_port or task.recipe.proxy.port
        task.recipe.proxy.type = proxy_type

    out_path.mkdir(parents=True, exist_ok=True)
    needs_admin = not dest_path.is_relative_to(Path.home())

    console.print(t("starting_clone", app_name=info.app_name, clone_name=clone_name), soft_wrap=True)
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
            data_dir=str(target_data_dir),
            created_at=datetime.now(timezone.utc).isoformat(),
            proxy_enabled=task.recipe.proxy.enabled,
            proxy_summary=task.recipe.proxy.url if task.recipe.proxy.enabled else "",
            new_bundle_id=new_bundle_id,
        )
        StateManager().add(record)

        console.print(t("clone_success", dest_path=dest_path), soft_wrap=True)
    except (CloneError, Exception) as e:
        console.print(t("clone_error", error=e), soft_wrap=True)
        sys.exit(1)
