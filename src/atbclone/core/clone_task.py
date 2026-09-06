"""CloneTask dataclass — bundles all parameters for a single clone operation."""

from dataclasses import dataclass
from pathlib import Path

from atbclone.recipes.models import Recipe

from .models import AppInfo
from atbclone.validation import (
    validate_bundle_id,
    validate_clone_name,
    validate_display_name,
    validate_path_component,
)


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

    def __post_init__(self) -> None:
        """Validate every field that the engines interpolate into generated scripts.

        CloneTask is the single chokepoint shared by CLI, GUI and update flows,
        so untrusted values are rejected here before any shell script is built.
        """
        validate_clone_name(self.clone_name)
        validate_bundle_id(self.new_bundle_id, field="new_bundle_id")
        if self.display_name is not None:
            validate_display_name(self.display_name)
        validate_path_component(str(self.dest_path), field="dest_path")
        validate_path_component(str(self.data_dir), field="data_dir")
