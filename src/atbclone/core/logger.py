"""Unified Logging System for ATBClone."""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Callable, List, Optional

from atbclone.core.config import DEFAULT_LOG_FILE

_listeners: List[Callable[[str], None]] = []
_initialized_log_file: Optional[Path] = None


class BroadcastHandler(logging.Handler):
    """In-memory logging handler that forwards formatted log lines to registered listeners."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
            for listener in list(_listeners):
                try:
                    listener(msg)
                except Exception:
                    pass
        except Exception:
            self.handleError(record)


def setup_logging(log_file: Path = DEFAULT_LOG_FILE) -> logging.Logger:
    """Initialize root logger with RotatingFileHandler and BroadcastHandler."""
    global _initialized_log_file
    _initialized_log_file = Path(log_file)

    logger = logging.getLogger("atbclone")
    logger.setLevel(logging.INFO)

    # Clear existing handlers if re-initializing
    logger.handlers.clear()

    formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # File Handler (10MB, 3 backups, UTF-8)
    try:
        _initialized_log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            str(_initialized_log_file),
            maxBytes=10 * 1024 * 1024,
            backupCount=3,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except (OSError, PermissionError):
        pass

    # Broadcast Handler for live subscribers
    broadcast_handler = BroadcastHandler()
    broadcast_handler.setFormatter(formatter)
    logger.addHandler(broadcast_handler)

    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a named logger under the atbclone hierarchy."""
    if _initialized_log_file is None:
        setup_logging()
    if name is None or name == "atbclone":
        return logging.getLogger("atbclone")
    if not name.startswith("atbclone."):
        return logging.getLogger(f"atbclone.{name}")
    return logging.getLogger(name)


def get_log_file_path() -> Path:
    """Get the currently configured log file path."""
    return _initialized_log_file or DEFAULT_LOG_FILE


def read_logs(limit_lines: int = 2000, log_file: Optional[Path] = None) -> str:
    """Read the last N lines from the log file safely."""
    path = Path(log_file) if log_file else get_log_file_path()
    if not path.exists():
        return ""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
            if len(lines) > limit_lines:
                lines = lines[-limit_lines:]
            return "".join(lines)
    except Exception:
        return ""


def clear_logs(log_file: Optional[Path] = None) -> None:
    """Truncate the log file and write a reset marker."""
    path = Path(log_file) if log_file else get_log_file_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.truncate(0)
    except Exception:
        pass
    logger = get_logger("logger")
    logger.info("Log file cleared by user.")


def add_log_listener(callback: Callable[[str], None]) -> None:
    """Add a listener callback for real-time log records."""
    if callback not in _listeners:
        _listeners.append(callback)


def remove_log_listener(callback: Callable[[str], None]) -> None:
    """Remove a registered listener callback."""
    if callback in _listeners:
        _listeners.remove(callback)
