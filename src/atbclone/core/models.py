from dataclasses import dataclass
from pathlib import Path


@dataclass
class AppInfo:
    path: Path
    bundle_id: str
    app_name: str
    executable: Path
    has_sandbox: bool
