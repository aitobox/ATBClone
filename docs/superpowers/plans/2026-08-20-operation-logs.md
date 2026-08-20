# ATBClone Unified Operation Logging Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a unified operation logging system for ATBClone that writes all GUI and CLI operations to `~/.atbclone/atbclone.log` and displays, filters, live-streams, and clears them in the GUI LogsView interface.

**Architecture:** Python standard `logging` library with a UTF-8 `RotatingFileHandler` writing to the base working directory, combined with an in-memory `BroadcastHandler` for zero-polling real-time UI log streaming. `LogsView` loads persisted history from disk on launch/switch, supports search keyword filtering, and disk-level log clearing.

**Tech Stack:** Python 3.12, `logging`, `logging.handlers.RotatingFileHandler`, Toga (BeeWare), Pytest.

## Global Constraints
- Target macOS native patterns, Python 3.12+, conda environment `ATBClone`.
- Zero external third-party dependencies for logging (use standard library `logging`).
- Default log path: `~/.atbclone/atbclone.log` (`DEFAULT_LOG_FILE = DEFAULT_ATB_DIR / "atbclone.log"`).
- UTF-8 encoding for all file I/O to safely support Chinese paths and application names.
- Test command: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/`.

---

### Task 1: Core Logger Module & Configuration

**Files:**
- Modify: `src/atbclone/core/config.py`
- Create: `src/atbclone/core/logger.py`
- Test: `tests/test_logger.py`

**Interfaces:**
- Produces:
  - `DEFAULT_LOG_FILE: Path` in `config.py`
  - `get_logger(name: str | None = None) -> logging.Logger`
  - `read_logs(limit_lines: int = 2000) -> str`
  - `clear_logs() -> None`
  - `get_log_file_path() -> Path`
  - `add_log_listener(callback: Callable[[str], None]) -> None`
  - `remove_log_listener(callback: Callable[[str], None]) -> None`

- [ ] **Step 1: Write the failing test for logger**

```python
# tests/test_logger.py
from pathlib import Path
import tempfile
import logging
import pytest
from atbclone.core.logger import (
    get_logger,
    read_logs,
    clear_logs,
    get_log_file_path,
    add_log_listener,
    remove_log_listener,
    setup_logging,
)

def test_logger_file_writing_and_reading(tmp_path):
    log_file = tmp_path / "test.log"
    setup_logging(log_file=log_file)

    logger = get_logger("test_module")
    logger.info("Hello ATBClone Test")
    logger.error("Something went wrong")

    content = read_logs(log_file=log_file)
    assert "Hello ATBClone Test" in content
    assert "[INFO] [test_module]" in content
    assert "Something went wrong" in content
    assert "[ERROR] [test_module]" in content

def test_clear_logs(tmp_path):
    log_file = tmp_path / "test_clear.log"
    setup_logging(log_file=log_file)
    logger = get_logger("test_clear")
    logger.info("Record 1")
    assert "Record 1" in read_logs(log_file=log_file)

    clear_logs(log_file=log_file)
    content = read_logs(log_file=log_file)
    assert "Record 1" not in content
    assert "Log file cleared by user" in content

def test_broadcast_listener():
    messages = []
    def _listener(msg: str):
        messages.append(msg)

    add_log_listener(_listener)
    try:
        logger = get_logger("broadcast_test")
        logger.info("Live broadcast message")
        assert any("Live broadcast message" in m for m in messages)
    finally:
        remove_log_listener(_listener)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_logger.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'atbclone.core.logger'`

- [ ] **Step 3: Implement `config.py` and `logger.py`**

In `src/atbclone/core/config.py`:
```python
# Default log file for runtime and operations
DEFAULT_LOG_FILE: Path = DEFAULT_ATB_DIR / "atbclone.log"
```

In `src/atbclone/core/logger.py`:
```python
"""Unified Logging System for ATBClone."""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Callable, List, Optional
from atbclone.core.config import DEFAULT_ATB_DIR, DEFAULT_LOG_FILE

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
    _initialized_log_file.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("atbclone")
    logger.setLevel(logging.INFO)

    # Clear existing handlers if re-initializing
    logger.handlers.clear()

    formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # File Handler (10MB, 3 backups, UTF-8)
    file_handler = RotatingFileHandler(
        str(_initialized_log_file),
        maxBytes=10 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Broadcast Handler for UI
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_logger.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/atbclone/core/config.py src/atbclone/core/logger.py tests/test_logger.py
git commit -m "feat(core): add unified logger module with file persistence and broadcast stream"
```

---

### Task 2: CLI Commands Logging Integration

**Files:**
- Modify: `src/atbclone/cli/cmd_clone.py`
- Modify: `src/atbclone/cli/cmd_remove.py`
- Modify: `src/atbclone/cli/cmd_update.py`
- Modify: `src/atbclone/cli/cmd_probe.py`
- Modify: `src/atbclone/cli/cmd_recipe.py`
- Modify: `src/atbclone/cli/cmd_doctor.py`
- Test: `tests/test_cli_logging.py`

**Interfaces:**
- Consumes: `get_logger` from `atbclone.core.logger`
- Produces: CLI commands automatically log their operations (start, success, errors) to `atbclone.log`.

- [ ] **Step 1: Write integration tests for CLI logging**

```python
# tests/test_cli_logging.py
from pathlib import Path
from unittest.mock import patch
import pytest
from atbclone.core.logger import read_logs, setup_logging
from atbclone.cli.main import app
from typer.testing import CliRunner

runner = CliRunner()

def test_cli_clone_and_doctor_logging(tmp_path):
    log_file = tmp_path / "atbclone.log"
    setup_logging(log_file=log_file)

    with patch("atbclone.core.app_prober.AppProber.probe_app") as mock_probe:
        result = runner.invoke(app, ["doctor"])
        assert result.exit_code == 0
        content = read_logs(log_file=log_file)
        assert "[INFO] [atbclone.cli.doctor]" in content
        assert "doctor" in content.lower()
```

- [ ] **Step 2: Add logging calls to CLI command files**
  - In `cmd_clone.py`: log start clone, recipe matched, execution success/error.
  - In `cmd_remove.py`: log removal of clone and data directory.
  - In `cmd_update.py`: log update starting and update completion.
  - In `cmd_probe.py`: log probe start, detected frameworks/strategy, saved recipes.
  - In `cmd_recipe.py`: log viewing/saving recipes.
  - In `cmd_doctor.py`: log running doctor checks and final summary.

- [ ] **Step 3: Run CLI tests**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_cmd_*.py tests/test_cli_logging.py`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add src/atbclone/cli/ tests/test_cli_logging.py
git commit -m "feat(cli): integrate unified logger into all CLI commands"
```

---

### Task 3: GUI Services & Windows Logging Integration

**Files:**
- Modify: `src/atbclone/gui/services/clone_service.py`
- Modify: `src/atbclone/gui/services/probe_service.py`
- Modify: `src/atbclone/gui/services/recipe_service.py`
- Modify: `src/atbclone/gui/services/doctor_service.py`
- Modify: `src/atbclone/gui/views/clone_list.py`
- Modify: `src/atbclone/gui/views/settings_view.py`
- Modify: `src/atbclone/gui/windows/wizard.py`

**Interfaces:**
- Consumes: `get_logger` from `atbclone.core.logger`
- Produces: Structured log records on all GUI asynchronous actions and user interactions.

- [ ] **Step 1: Write service logging tests**

```python
# Add test in tests/gui/test_services.py
def test_services_write_logs(tmp_path):
    log_file = tmp_path / "gui_service.log"
    setup_logging(log_file=log_file)
    ...
```

- [ ] **Step 2: Add logger calls to GUI services and views**
  - `clone_service.py`: log `create_clone`, `update_clone`, `remove_clone`, `update_clone_record`.
  - `probe_service.py`: log `probe_app` start and result.
  - `recipe_service.py`: log saving, deleting, and duplicating custom recipes.
  - `doctor_service.py`: log checking environment and summary.
  - `clone_list.py`: log launching clone (`on_launch_clone`).
  - `settings_view.py`: log saving preferences and opening Finder directory.
  - `wizard.py`: log wizard start, app selection, step transitions, and execution result.

- [ ] **Step 3: Run GUI service tests**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/gui/test_services.py tests/gui/test_clone_views.py tests/gui/test_wizard_window.py`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add src/atbclone/gui/services/ src/atbclone/gui/views/clone_list.py src/atbclone/gui/views/settings_view.py src/atbclone/gui/windows/wizard.py
git commit -m "feat(gui): integrate unified logger into GUI services, wizard, and views"
```

---

### Task 4: GUI LogsView Overhaul with File Persistence & Realtime Stream

**Files:**
- Modify: `src/atbclone/gui/views/logs_view.py`
- Modify: `src/atbclone/gui/app.py`
- Modify: `tests/gui/test_logs_and_settings_views.py`

**Interfaces:**
- Consumes: `read_logs`, `clear_logs`, `add_log_listener`, `remove_log_listener`, `get_logger`
- Produces: Fully interactive LogsView that displays disk logs, live appends new lines, filters by keyword, and clears logs on disk.

- [ ] **Step 1: Write failing test in `tests/gui/test_logs_and_settings_views.py`**

```python
def test_logs_view_file_backed_and_live_sync(tmp_path):
    log_file = tmp_path / "test_logsview.log"
    setup_logging(log_file=log_file)
    logger = get_logger("ui_test")
    logger.info("Pre-existing log entry on disk")

    view = LogsView()
    # Verify disk content loaded
    assert "Pre-existing log entry on disk" in view.log_text.value

    # Verify live streaming
    logger.info("New live streamed event")
    assert "New live streamed event" in view.log_text.value

    # Verify filter
    view.on_filter_logs("live")
    assert "New live streamed event" in view.log_text.value
    assert "Pre-existing" not in view.log_text.value

    # Verify clear
    view.on_clear_logs(None)
    assert "Pre-existing" not in view.log_text.value
    assert "Log file cleared by user" in view.log_text.value
    assert "Log file cleared by user" in read_logs(log_file=log_file)
```

- [ ] **Step 2: Update `LogsView` in `src/atbclone/gui/views/logs_view.py`**

```python
"""Logs View for displaying persistent runtime logs and live execution output."""

from pathlib import Path
from typing import Optional
import toga
from toga.style import Pack
from toga.style.pack import COLUMN
from atbclone.core.logger import (
    add_log_listener,
    clear_logs,
    get_logger,
    read_logs,
    remove_log_listener,
)
from atbclone.gui.components.top_bar import TopHeaderBar
from atbclone.gui.theme import Theme


class LogsView(toga.Box):
    """View presenting persistent application logs and real-time task output."""

    def __init__(self, app: Optional[toga.App] = None):
        super().__init__(style=Pack(direction=COLUMN, flex=1, background_color=Theme.BG_WINDOW))
        self.app_instance = app
        self._raw_log_lines: list[str] = []
        self._current_filter: str = ""

        # Top Header Bar
        self.top_bar = TopHeaderBar(
            title="运行日志",
            search_placeholder="🔍 搜索日志关键字...",
            on_search=self.on_filter_logs,
            action_label="🗑️ 清空日志",
            on_action=self.on_clear_logs,
            on_refresh=self.on_refresh_logs,
        )
        self.add(self.top_bar)

        # Monospace Log Text Area
        self.log_text = toga.MultilineTextInput(
            readonly=True,
            style=Pack(flex=1, margin=(0, 15, 15, 15), font_family="monospace", font_size=12),
        )
        self.add(self.log_text)

        # Load persisted disk logs
        self.reload_from_disk()

        # Register live broadcast listener
        add_log_listener(self._on_live_log_entry)

    def reload_from_disk(self):
        """Read all log entries from the persistent log file on disk."""
        content = read_logs()
        if content:
            self._raw_log_lines = content.strip().split("\n")
        else:
            self._raw_log_lines = []
        self._update_log_display()

    def _on_live_log_entry(self, entry: str):
        """Listener callback for new log messages emitted anywhere in the app."""
        self._raw_log_lines.append(entry)
        self._update_log_display()

    def _update_log_display(self):
        query = self._current_filter.strip().lower()
        if not query:
            filtered = self._raw_log_lines
        else:
            filtered = [line for line in self._raw_log_lines if query in line.lower()]

        self.log_text.value = "\n".join(filtered)
        count = len(filtered)
        total = len(self._raw_log_lines)
        if query:
            self.top_bar.update_title(f"运行日志 (筛选 {count}/{total} 行)")
        else:
            self.top_bar.update_title(f"运行日志 ({total} 行)")

    def on_filter_logs(self, query: str):
        self._current_filter = query
        self._update_log_display()

    def on_clear_logs(self, widget: toga.Button):
        clear_logs()
        self.reload_from_disk()

    def on_refresh_logs(self, widget: toga.Button):
        self.reload_from_disk()

    def log_info(self, message: str):
        get_logger("gui").info(message)

    def log_error(self, message: str):
        get_logger("gui").error(message)
```

- [ ] **Step 3: Update `src/atbclone/gui/app.py`**
In `switch_view("logs")`:
```python
elif view_name == "logs":
    self.content_container.add(self.logs_view)
    self.logs_view.reload_from_disk()
```

- [ ] **Step 4: Run tests in `test_logs_and_settings_views.py`**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/gui/test_logs_and_settings_views.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/atbclone/gui/views/logs_view.py src/atbclone/gui/app.py tests/gui/test_logs_and_settings_views.py
git commit -m "feat(gui): overhaul LogsView with disk persistence, live broadcast, and disk clearing"
```

---

### Task 5: Full Regression Testing & Verification

**Files:**
- Test all test files in `tests/` and `tests/gui/`

- [ ] **Step 1: Run complete test suite**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/`
Expected: All 240+ tests pass with 100% success rate.

- [ ] **Step 2: Verify log output file manually via temporary run**

Verify that running `atbclone doctor` or GUI operations writes well-formatted records into `~/.atbclone/atbclone.log`.

- [ ] **Step 3: Commit final plan documentation and test updates**

```bash
git add docs/superpowers/plans/2026-08-20-operation-logs.md
git commit -m "docs: add implementation plan for operation logs"
```
