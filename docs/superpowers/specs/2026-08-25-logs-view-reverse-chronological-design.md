# ATBClone GUI LogsView Reverse Chronological Ordering Design

## 1. Overview & Goals

This document specifies the technical design for displaying runtime and persisted logs in reverse chronological order (newest log entries shown at the very top) within the ATBClone GUI `LogsView`.

### Goals
- Present the most recent log entries at the top of the `LogsView` text area so users immediately see current application events and errors without manual scrolling.
- Display historical disk logs in newest-to-oldest order upon loading or refreshing.
- Immediately prepend newly arriving live log broadcast events to the top of the display.
- Maintain keyword search filtering functionality across reverse-chronologically sorted logs.

---

## 2. Architecture & Data Flow

### 2.1 Component: `LogsView` (`src/atbclone/gui/views/logs_view.py`)

- **Internal Buffer**: `self._raw_log_lines: list[str]` stores log lines in descending time order (Index 0 = latest log entry).

### 2.2 Disk Reload Flow (`reload_from_disk`)
1. Call `read_logs()` to retrieve the tail of the persistent log file (which is written chronologically from top to bottom).
2. Split content into non-empty lines:
   ```python
   lines = [line for line in content.strip().split("\n") if line.strip()]
   ```
3. Invert the order so index 0 becomes the most recent log line:
   ```python
   self._raw_log_lines = list(reversed(lines))
   ```
4. Invoke `self._update_log_display()`.

### 2.3 Live Broadcast Stream Flow (`_on_live_log_entry`)
1. Listener receives an incoming formatted log record string `entry: str`.
2. If non-empty, prepend the entry directly to the head of the buffer:
   ```python
   self._raw_log_lines.insert(0, entry.strip())
   ```
3. Invoke `self._update_log_display()`.

### 2.4 Filter and Render Flow (`_update_log_display`)
1. Filter `self._raw_log_lines` against the active query (case-insensitive):
   ```python
   if not query:
       filtered = self._raw_log_lines
   else:
       filtered = [line for line in self._raw_log_lines if query in line.lower()]
   ```
2. Set text content:
   ```python
   self.log_text.value = "\n".join(filtered)
   ```
3. Update top bar title with item count:
   ```python
   if query:
       self.top_bar.update_title(t("logs_title_filtered", count=len(filtered), total=len(self._raw_log_lines)))
   else:
       self.top_bar.update_title(t("logs_title", total=len(self._raw_log_lines)))
   ```

---

## 3. Testing & Verification

### 3.1 GUI Unit Tests (`tests/gui/test_logs_and_settings_views.py`)
- Verify that when pre-existing logs are loaded from disk, the latest line appears before earlier lines in `view.log_text.value`.
- Verify that when a new log is broadcast live, it appears above previous log entries in `view.log_text.value`.
- Verify filtering and clearing behave as expected with reverse-chronological order.

### 3.2 Regression Testing
- Run full pytest test suite:
  ```bash
  PYTHONPATH=src conda run -n ATBClone python -m pytest tests/
  ```
