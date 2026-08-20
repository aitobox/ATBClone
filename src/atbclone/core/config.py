"""Configuration constants and path defaults for ATBClone."""

from pathlib import Path

# Base configuration directory for ATBClone
DEFAULT_ATB_DIR: Path = Path.home() / ".atbclone"

# Default state file storing clone records
DEFAULT_STATE_FILE: Path = DEFAULT_ATB_DIR / "clones.yaml"

# Default root directory for application clone data storage
DEFAULT_DATA_DIR: Path = DEFAULT_ATB_DIR / "Data"

# Default directory for user-defined / override recipes
DEFAULT_RECIPES_DIR: Path = DEFAULT_ATB_DIR / "recipes"

# Default directory for wrapper applications
DEFAULT_APPS_DIR: Path = DEFAULT_ATB_DIR / "Apps"

# Default log file for runtime and operations
DEFAULT_LOG_FILE: Path = DEFAULT_ATB_DIR / "atbclone.log"
