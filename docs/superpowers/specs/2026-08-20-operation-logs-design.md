# ATBClone Unified Operation Logging System Design

## 1. Overview & Goals

This document specifies the technical design for the unified operation logging system in ATBClone. 

### Goals
- Record all user and background operations across both GUI and CLI into a persistent log file.
- Store the log file in ATBClone's base root working directory (`~/.atbclone/atbclone.log` by default, or configured root directory).
- Enable the GUI "查看日志" (LogsView) interface to read directly from this disk file, display historical logs upon launch, support live append/streaming during runtime, provide search keyword filtering, and offer a disk-backed log clearing mechanism.
- Keep the design lightweight, thread-safe, and zero-dependency using Python's standard `logging` library.

---

## 2. Architecture & Core Logger Module

### 2.1 File Location Configuration
In `src/atbclone/core/config.py`:
```python
DEFAULT_ATB_DIR: Path = Path.home() / ".atbclone"
DEFAULT_LOG_FILE: Path = DEFAULT_ATB_DIR / "atbclone.log"
```

### 2.2 Global Logger (`src/atbclone/core/logger.py`)
- **Logger Name**: `atbclone` (hierarchical: `atbclone.core`, `atbclone.gui`, `atbclone.cli`, etc.).
- **Log Format**: `[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s` with timestamp format `%Y-%m-%d %H:%M:%S`.
- **Handlers**:
  1. `RotatingFileHandler`:
     - Path: `DEFAULT_LOG_FILE` (or configured log path).
     - Encoding: `utf-8`.
     - Max Bytes: 10 MB with 3 backup files (`atbclone.log.1`, etc.).
  2. `BroadcastHandler`:
     - Custom lightweight in-memory `logging.Handler` allowing UI / listeners to register callbacks `Callable[[str], None]`.
     - Emits formatted log strings directly to registered subscribers for live UI updates.
- **Helper APIs**:
  - `get_logger(name: str | None = None) -> logging.Logger`: Returns standard logger instance.
  - `read_logs(limit_lines: int = 2000) -> str`: Reads the latest lines from the disk log file. Returns empty string if file does not exist.
  - `clear_logs() -> None`: Truncates the disk log file and logs an initial reset entry `[INFO] [Logger] Log file cleared by user.`
  - `get_log_file_path() -> Path`: Returns the current log file path.
  - `add_log_listener(callback: Callable[[str], None]) -> None`: Subscribes a callback to live log messages.
  - `remove_log_listener(callback: Callable[[str], None]) -> None`: Unsubscribes a callback.

---

## 3. Operation Logging Coverage

### 3.1 Clone Operations (GUI & CLI)
- **Creation**: Logs initiation with source app, destination path, strategy (`hard_clone`/`soft_clone`), proxy config, completion confirmation, and error exceptions.
- **Update**: Logs starting clone update, rebuilding wrapper/bundle, success/failure status.
- **Removal**: Logs clone deletion and whether the isolated data directory was purged.
- **Launch**: Logs application launch command and target path.
- **Record Edit**: Logs property edits (display name, proxy configurations).

### 3.2 Probing & Recipe Operations
- **App Prober**: Logs target application bundle path, detected frameworks, sandbox status, and deduced cloning strategy.
- **Recipe Management**: Logs creation, modification, duplication, and deletion of custom recipes.

### 3.3 System & Diagnostics
- **Doctor Check**: Logs initiation and summary of environment diagnostics results (e.g. `Passed: 7/7`).
- **Settings**: Logs updates to global directory preferences and proxy presets.

---

## 4. GUI "查看日志" (LogsView) Design

### 4.1 UI Components
- **TopHeaderBar**:
  - Title: `运行日志` with line count (e.g., `运行日志 (42 行)`).
  - Search Input: Real-time case-insensitive keyword filter.
  - Refresh Button (🔄): Explicitly re-reads `atbclone.log` from disk.
  - Action Button (🗑️ 清空日志): Invokes `clear_logs()`, resets file on disk, and updates the text display.
- **MultilineTextInput**:
  - Readonly, monospace font.
  - Initialized on startup and view switch (`switch_view("logs")`) by calling `read_logs()`.

### 4.2 Real-time Sync & State Management
- `LogsView` registers a listener on `BroadcastHandler` in `startup` / `__init__`.
- When new log records occur anywhere in the application, the listener appends them to the internal buffer and updates the text area (respecting current search filter).
- Previous session logs are naturally persisted on disk and loaded immediately when opening the application.

---

## 5. Error Handling & Edge Cases

- **Missing directory/file**: `logger.py` ensures parent directory `~/.atbclone` exists before creating file handlers.
- **Concurrent logging**: Handled safely by Python's built-in `logging` thread locks.
- **Non-blocking UI**: File reads in `LogsView` are light (reading tail up to 2000 lines) and can run asynchronously if needed.
- **UTF-8 Support**: All file I/O and formatters explicitly enforce `utf-8` to support Chinese app names and directories.

---

## 6. Testing & Verification

- **Unit Tests (`tests/test_logger.py`)**:
  - Test logger initialization, file handler writing, format verification.
  - Test `read_logs()` on non-existent and populated log files.
  - Test `clear_logs()` file truncation and reset marker.
  - Test `BroadcastHandler` subscriber callback execution.
- **GUI Tests (`tests/gui/test_logs_and_settings_views.py`)**:
  - Test `LogsView` reading from disk log file.
  - Test live append via broadcast listener.
  - Test keyword search filtering and clearing logs.
- **Full Test Suite Regression**:
  - Run `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/` to ensure all 240+ tests pass.
