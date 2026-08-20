"""Clone Service for async clone operations."""

import asyncio
from datetime import datetime, timezone
from pathlib import Path
import shlex
from urllib.parse import urlparse

from atbclone.core.app_inspector import AppInspector
from atbclone.core.clone_task import CloneTask
from atbclone.core.config import DEFAULT_DATA_DIR, DEFAULT_STATE_FILE
from atbclone.core.engines import HardCloneEngine, SoftCloneEngine
from atbclone.core.state import CloneRecord, StateManager
from atbclone.executor.runner import Runner
from atbclone.recipes.loader import RecipeLoader


class CloneService:
    def __init__(self, state_file: Path = DEFAULT_STATE_FILE):
        self.state_file = Path(state_file)
        self.state_manager = StateManager(state_file=self.state_file)

    async def list_clones(self) -> list[CloneRecord]:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.state_manager.load)

    async def get_clone(self, clone_name: str) -> CloneRecord | None:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, lambda: self.state_manager.get(clone_name))

    async def create_clone(self, task: CloneTask) -> CloneRecord:
        loop = asyncio.get_running_loop()

        def _execute():
            dest_path = task.dest_path
            try:
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                task.data_dir.mkdir(parents=True, exist_ok=True)
            except Exception:
                pass

            needs_admin = not dest_path.is_relative_to(Path.home())
            if task.recipe.strategy == "soft_clone":
                SoftCloneEngine.execute(task, needs_admin)
            else:
                HardCloneEngine.execute(task, needs_admin)

            record = CloneRecord(
                clone_name=task.clone_name,
                source_app=task.source.app_name,
                source_path=str(task.source.path),
                bundle_id=task.source.bundle_id,
                strategy=task.recipe.strategy,
                dest_path=str(task.dest_path),
                data_dir=str(task.data_dir),
                created_at=datetime.now(timezone.utc).isoformat(),
                proxy_enabled=task.recipe.proxy.enabled,
                proxy_summary=task.recipe.proxy.url if task.recipe.proxy.enabled else "",
                new_bundle_id=task.new_bundle_id,
            )
            self.state_manager.add(record)
            return record

        return await loop.run_in_executor(None, _execute)

    async def update_clone(self, clone_name: str) -> CloneRecord:
        loop = asyncio.get_running_loop()

        def _execute():
            record = self.state_manager.get(clone_name)
            if record is None:
                raise ValueError(f"Clone {clone_name} not found")
            if not Path(record.source_path).exists():
                raise FileNotFoundError(f"Source app not found: {record.source_path}")

            dest_path = Path(record.dest_path)
            needs_admin = not dest_path.is_relative_to(Path.home())

            script = f"#!/bin/bash\nset -e\nrm -rf {shlex.quote(str(dest_path))}\n"
            Runner.run(script, needs_admin)

            info = AppInspector.inspect(record.source_path)
            recipe = RecipeLoader.match(info.bundle_id)
            data_dir = Path(record.data_dir)
            new_bundle_id = record.new_bundle_id or AppInspector.generate_bundle_id(record.bundle_id, 1)

            task = CloneTask(
                source=info,
                dest_path=dest_path,
                data_dir=data_dir,
                recipe=recipe,
                clone_name=record.clone_name,
                new_bundle_id=new_bundle_id,
            )

            if record.proxy_enabled and record.proxy_summary:
                parsed = urlparse(record.proxy_summary)
                task.recipe.proxy.enabled = True
                if parsed.scheme:
                    task.recipe.proxy.type = parsed.scheme  # type: ignore[assignment]
                if parsed.hostname:
                    task.recipe.proxy.host = parsed.hostname
                if parsed.port:
                    task.recipe.proxy.port = parsed.port
                if parsed.username:
                    task.recipe.proxy.username = parsed.username
                if parsed.password:
                    task.recipe.proxy.password = parsed.password

            if record.strategy == "soft_clone":
                SoftCloneEngine.execute(task, needs_admin)
            else:
                HardCloneEngine.execute(task, needs_admin)

            record.created_at = datetime.now(timezone.utc).isoformat()
            self.state_manager.add(record)
            return record

        return await loop.run_in_executor(None, _execute)

    async def update_clone_record(self, record: CloneRecord) -> None:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, lambda: self.state_manager.add(record))

    async def remove_clone(self, clone_name: str, with_data: bool = False) -> bool:
        loop = asyncio.get_running_loop()

        def _execute():
            record = self.state_manager.get(clone_name)
            if record is None:
                return False

            needs_admin = (
                not Path(record.dest_path).is_relative_to(Path.home())
                or (with_data and not Path(record.data_dir).is_relative_to(Path.home()))
            )

            lines = [
                "#!/bin/bash",
                "set -e",
                f"rm -rf {shlex.quote(record.dest_path)}",
            ]
            if with_data:
                lines.append(f"rm -rf {shlex.quote(record.data_dir)}")

            script = "\n".join(lines) + "\n"
            Runner.run(script, needs_admin)
            return self.state_manager.remove(clone_name)

        return await loop.run_in_executor(None, _execute)
