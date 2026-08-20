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

# Default JSON configuration file for user preferences (language, default paths, etc.)
DEFAULT_CONFIG_FILE: Path = DEFAULT_ATB_DIR / "config.json"


def load_config() -> dict:
    """Load configuration dictionary from disk."""
    import json
    if not DEFAULT_CONFIG_FILE.exists():
        return {}
    try:
        with open(DEFAULT_CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_config(cfg: dict) -> None:
    """Persist configuration dictionary to disk."""
    import json
    DEFAULT_ATB_DIR.mkdir(parents=True, exist_ok=True)
    with open(DEFAULT_CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


def get_config_value(key: str, default: any = None) -> any:
    """Retrieve a single configuration value."""
    cfg = load_config()
    return cfg.get(key, default)


def set_config_value(key: str, value: any) -> None:
    """Update and persist a single configuration value."""
    cfg = load_config()
    cfg[key] = value
    save_config(cfg)

