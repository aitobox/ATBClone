from dataclasses import dataclass
from pathlib import Path


@dataclass
class AppInfo:
    path: Path
    bundle_id: str
    app_name: str
    executable: Path
    has_sandbox: bool
    is_ios_app: bool = False
    relative_plist_path: Path = Path("Contents/Info.plist")
    relative_executable_path: Path = Path("Contents/MacOS")
    relative_resources_path: Path = Path("Contents/Resources")

