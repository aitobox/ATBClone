"""Probe Service for async app analysis and recipe extraction."""

import asyncio
from pathlib import Path

from atbclone.core.app_prober import AppProber, ProbeResult
from atbclone.core.logger import get_logger

logger = get_logger("gui.probe_service")


class ProbeService:
    async def probe_app(self, app_path: Path | str) -> ProbeResult:
        loop = asyncio.get_running_loop()
        path = Path(app_path).expanduser().resolve()
        logger.info(f"Probing app at '{path}'")

        def _do_probe():
            try:
                res = AppProber.analyze(path)
                logger.info(f"Probe completed for '{res.app_info.app_name}' (bundle='{res.app_info.bundle_id}', strategy='{res.strategy}')")
                return res
            except Exception as e:
                logger.error(f"Probe failed for '{path}': {e}")
                raise

        return await loop.run_in_executor(None, _do_probe)
