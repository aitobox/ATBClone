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
from atbclone.core.logger import get_logger
from atbclone.core.state import CloneRecord, StateManager
from atbclone.executor.runner import Runner
from atbclone.recipes.loader import RecipeLoader

logger = get_logger("gui.clone_service")


class CloneService:
    def __init__(self, state_file: Path = DEFAULT_STATE_FILE):
        self.state_file = Path(state_file)
        self.state_manager = StateManager(state_file=self.state_file)
        self._busy_clones: set[str] = set()

    async def list_clones(self) -> list[CloneRecord]:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.state_manager.load)

    async def get_clone(self, clone_name: str) -> CloneRecord | None:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, lambda: self.state_manager.get(clone_name))

    async def create_clone(self, task: CloneTask) -> CloneRecord:
        if task.clone_name in self._busy_clones:
            logger.warning(f"Operation already in progress for clone '{task.clone_name}'")
            raise RuntimeError(f"Operation already in progress for '{task.clone_name}'")
        self._busy_clones.add(task.clone_name)
        try:
            loop = asyncio.get_running_loop()

            def _execute():
                dest_path = task.dest_path
                logger.info(f"Starting clone creation: name='{task.clone_name}', source='{task.source.path}', strategy='{task.recipe.strategy}', dest='{dest_path}'")
                try:
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    task.data_dir.mkdir(parents=True, exist_ok=True)
                except Exception:
                    pass

                needs_admin = not dest_path.is_relative_to(Path.home())
                try:
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
                        language=task.language,
                    )
                    self.state_manager.add(record)
                    logger.info(f"Clone '{task.clone_name}' created successfully at '{dest_path}'")
                    return record
                except Exception as e:
                    logger.error(f"Failed to create clone '{task.clone_name}': {e}")
                    raise

            return await loop.run_in_executor(None, _execute)
        finally:
            self._busy_clones.discard(task.clone_name)

    async def update_clone(self, clone_name: str) -> CloneRecord:
        if clone_name in self._busy_clones:
            logger.warning(f"Operation already in progress for clone '{clone_name}'")
            raise RuntimeError(f"Operation already in progress for '{clone_name}'")
        self._busy_clones.add(clone_name)
        try:
            loop = asyncio.get_running_loop()

            def _execute():
                logger.info(f"Updating clone '{clone_name}'")
                record = self.state_manager.get(clone_name)
                if record is None:
                    logger.error(f"Clone '{clone_name}' not found for update")
                    raise ValueError(f"Clone {clone_name} not found")
                if not Path(record.source_path).exists():
                    logger.error(f"Source app not found for clone '{clone_name}': {record.source_path}")
                    raise FileNotFoundError(f"Source app not found: {record.source_path}")

                dest_path = Path(record.dest_path)
                needs_admin = not dest_path.is_relative_to(Path.home())

                script = f"#!/bin/bash\nset -e\nrm -rf {shlex.quote(str(dest_path))}\n"
                Runner.run(script, needs_admin)

                info = AppInspector.inspect(record.source_path)
                recipe = RecipeLoader.match(info.bundle_id)
                data_dir = Path(record.data_dir)
                existing_records = self.state_manager.load()
                existing_bundle_ids = {r.new_bundle_id for r in existing_records if r.new_bundle_id and r.clone_name != clone_name}
                new_bundle_id = record.new_bundle_id or AppInspector.resolve_bundle_id(
                    record.bundle_id,
                    clone_name=record.clone_name,
                    existing_bundle_ids=existing_bundle_ids,
                )

                task = CloneTask(
                    source=info,
                    dest_path=dest_path,
                    data_dir=data_dir,
                    recipe=recipe,
                    clone_name=record.clone_name,
                    new_bundle_id=new_bundle_id,
                    language=record.language,
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

                try:
                    if record.strategy == "soft_clone":
                        SoftCloneEngine.execute(task, needs_admin)
                    else:
                        HardCloneEngine.execute(task, needs_admin)

                    record.created_at = datetime.now(timezone.utc).isoformat()
                    self.state_manager.add(record)
                    logger.info(f"Clone '{clone_name}' updated successfully")
                    return record
                except Exception as e:
                    logger.error(f"Failed to update clone '{clone_name}': {e}")
                    raise

            return await loop.run_in_executor(None, _execute)
        finally:
            self._busy_clones.discard(clone_name)

    async def update_clone_record(self, record: CloneRecord) -> None:
        loop = asyncio.get_running_loop()
        logger.info(f"Updating record for clone '{record.clone_name}'")
        await loop.run_in_executor(None, lambda: self.state_manager.add(record))

    async def remove_clone(self, clone_name: str, with_data: bool = False) -> bool:
        if clone_name in self._busy_clones:
            logger.warning(f"Operation already in progress for clone '{clone_name}'")
            raise RuntimeError(f"Operation already in progress for '{clone_name}'")
        self._busy_clones.add(clone_name)
        try:
            loop = asyncio.get_running_loop()

            def _execute():
                logger.info(f"Removing clone '{clone_name}' (with_data={with_data})")
                record = self.state_manager.get(clone_name)
                if record is None:
                    logger.warning(f"Clone '{clone_name}' not found for removal")
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
                try:
                    Runner.run(script, needs_admin)
                except Exception as e:
                    logger.error(f"Failed to remove clone files for '{clone_name}': {e}")
                    raise
                result = self.state_manager.remove(clone_name)
                if result:
                    logger.info(f"Successfully removed clone '{clone_name}'")
                return result

            return await loop.run_in_executor(None, _execute)
        finally:
            self._busy_clones.discard(clone_name)
