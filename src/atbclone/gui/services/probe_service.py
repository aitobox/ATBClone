"""Probe Service for async app analysis and recipe extraction."""

import asyncio
from pathlib import Path

from atbclone.core.app_prober import AppProber, ProbeResult


class ProbeService:
    async def probe_app(self, app_path: Path | str) -> ProbeResult:
        loop = asyncio.get_running_loop()
        path = Path(app_path).expanduser().resolve()
        return await loop.run_in_executor(None, lambda: AppProber.analyze(path))
