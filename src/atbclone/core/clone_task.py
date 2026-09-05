"""CloneTask dataclass — bundles all parameters for a single clone operation."""

from dataclasses import dataclass
from pathlib import Path

from atbclone.recipes.models import Recipe

from .models import AppInfo


@dataclass
class CloneTask:
    """All parameters required to perform one clone operation."""

    source: AppInfo
    dest_path: Path
    data_dir: Path
    recipe: Recipe
    clone_name: str
    new_bundle_id: str
    display_name: str | None = None  # Dock/Finder label; defaults to clone_name when None
    icon_path: Path | None = None    # Custom .icns; defaults to copying src Resources when None
    language: str = "system"         # Desired locale/language; defaults to "system"
    injection_strategy: str = "auto" # "auto" | "dylib" | "launcher"
    actual_injection_strategy: str = "auto" # Recorded actual strategy executed ("dylib" | "launcher")
