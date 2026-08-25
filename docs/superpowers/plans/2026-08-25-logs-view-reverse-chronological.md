# LogsView Reverse Chronological Ordering Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Modify the ATBClone GUI `LogsView` so that log messages are displayed in reverse chronological order (newest log at the very top), for both loaded disk logs and live-streamed logs.

**Architecture:** Update `LogsView` internal buffer storage to maintain newest entries at index 0 (`reversed(lines)` on disk load, `insert(0, entry)` on live broadcast). Update GUI test assertions in `test_logs_and_settings_views.py` to verify reverse chronological display order.

**Tech Stack:** Python 3.12, Toga / Cocoa GUI, pytest.

## Global Constraints
- Target macOS native patterns, Toga / Cocoa GUI, Python 3.12+.
- Dev environment command: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/`

---

### Task 1: Update Tests for LogsView Reverse Chronological Order

**Files:**
- Modify: `tests/gui/test_logs_and_settings_views.py:10-38`

**Interfaces:**
- Consumes: `LogsView`, `setup_logging`, `get_logger`, `read_logs` from `atbclone.gui.views.logs_view` and `atbclone.core.logger`.
- Produces: Test assertions validating newest log line appears before older log line in `view.log_text.value`.

- [ ] **Step 1: Write the failing / updated test**

Update `test_logs_view_file_backed_and_live_sync` in `tests/gui/test_logs_and_settings_views.py`:

```python
def test_logs_view_file_backed_and_live_sync(tmp_path):
    log_file = tmp_path / "test_logsview.log"
    setup_logging(log_file=log_file)
    logger = get_logger("ui_test")
    logger.info("Log entry 1 (Oldest)")
    logger.info("Log entry 2 (Older)")

    view = LogsView()
    # Verify disk content loaded in reverse chronological order (newest on top)
    assert "Log entry 1 (Oldest)" in view.log_text.value
    assert "Log entry 2 (Older)" in view.log_text.value
    assert view.log_text.value.index("Log entry 2 (Older)") < view.log_text.value.index("Log entry 1 (Oldest)")

    # Verify live streaming prepends to top
    logger.info("Log entry 3 (Newest live)")
    assert "Log entry 3 (Newest live)" in view.log_text.value
    assert view.log_text.value.index("Log entry 3 (Newest live)") < view.log_text.value.index("Log entry 2 (Older)")

    # Verify filter
    view.on_filter_logs("live")
    assert "Log entry 3 (Newest live)" in view.log_text.value
    assert "Log entry 1" not in view.log_text.value

    # Reset filter
    view.on_filter_logs("")
    assert "Log entry 1 (Oldest)" in view.log_text.value
    assert view.log_text.value.index("Log entry 3 (Newest live)") < view.log_text.value.index("Log entry 1 (Oldest)")

    # Verify clear
    view.on_clear_logs(None)
    assert "Log entry 1" not in view.log_text.value
    assert "Log file cleared by user" in view.log_text.value
    assert "Log file cleared by user" in read_logs(log_file=log_file)
```

- [ ] **Step 2: Run test to verify it fails on current code**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/gui/test_logs_and_settings_views.py::test_logs_view_file_backed_and_live_sync`
Expected: FAIL with `AssertionError: assert view.log_text.value.index("Log entry 2 (Older)") < view.log_text.value.index("Log entry 1 (Oldest)")`

---

### Task 2: Implement Reverse Chronological Ordering in LogsView

**Files:**
- Modify: `src/atbclone/gui/views/logs_view.py:55-69`

**Interfaces:**
- Consumes: `read_logs()`, `add_log_listener()`.
- Produces: `LogsView.reload_from_disk()`, `LogsView._on_live_log_entry()`.

- [ ] **Step 1: Update `reload_from_disk` and `_on_live_log_entry` in `src/atbclone/gui/views/logs_view.py`**

In `src/atbclone/gui/views/logs_view.py`:
```python
    def reload_from_disk(self):
        """Read all log entries from the persistent log file on disk (reversed, latest first)."""
        content = read_logs()
        if content:
            lines = [line for line in content.strip().split("\n") if line.strip()]
            self._raw_log_lines = list(reversed(lines))
        else:
            self._raw_log_lines = []
        self._update_log_display()

    def _on_live_log_entry(self, entry: str):
        """Listener callback for new log messages emitted anywhere in the app (inserted at top)."""
        if entry.strip():
            self._raw_log_lines.insert(0, entry.strip())
            self._update_log_display()
```

- [ ] **Step 2: Run tests to verify all pass**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/gui/test_logs_and_settings_views.py`
Expected: PASS (5/5 passed)

- [ ] **Step 3: Run full test suite regression**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/`
Expected: PASS (all tests pass)
