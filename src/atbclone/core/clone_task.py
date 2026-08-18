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
