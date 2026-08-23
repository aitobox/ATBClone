# Table Header Sorting Design Spec

## Overview
This document specifies the design for adding native macOS table header sorting (clicking column headers to toggle ascending/descending sort with native chevron indicators) to all `toga.Table` widgets across ATBClone.

## Context & Requirements
- Target platform: macOS native (Cocoa via Toga / `rubicon-objc`), Python 3.12+.
- Existing views with tables:
  - `CloneListView` (`src/atbclone/gui/views/clone_list.py`)
  - `RecipeListView` (`src/atbclone/gui/views/recipe_list.py`)
  - `DoctorView` (`src/atbclone/gui/views/doctor_view.py`)
- Requirements:
  1. Clicking any column header triggers sorting in ascending order (`▲`).
  2. Clicking the same column header toggles sorting to descending order (`▼`).
  3. Clicking a different column header switches sorting to that column in ascending order.
  4. Native macOS sort indicator icons (`NSAscendingSortIndicator` / `NSDescendingSortIndicator`) appear in the active column header.
  5. Fallback auto-sorting for generic `toga.Table` instances: safely compares strings (case-insensitive), numbers, booleans, and None values.
  6. Integration & two-way sync: in `CloneListView` and `RecipeListView`, header sorting re-orders the underlying filtered items, preserves selection, and synchronizes with the top bar's sort dropdown where applicable.

## Technical Architecture

### 1. Cocoa Native Table Patch (`src/atbclone/gui/patch_cocoa.py`)
- Patch `TogaTable` (subclass of `NSTableView`) to implement the `tableView:didClickTableColumn:` delegate method:
  ```python
  @objc_method
  def tableView_didClickTableColumn_(self, tableView, tableColumn) -> None:
      ...
  ```
- Manage sorting state on `TogaTable`:
  - `_sort_col_id`: ID/Identifier of current sorted column
  - `_sort_ascending`: Boolean indicating sort direction (True = Ascending, False = Descending)
- Update native Cocoa column indicators:
  - For clicked column: `tableView.setIndicatorImage_inTableColumn_(NSImage.imageNamed_("NSAscendingSortIndicator" if ascending else "NSDescendingSortIndicator"), tableColumn)`
  - For all other columns: `tableView.setIndicatorImage_inTableColumn_(None, other_column)`
  - Highlight current column: `tableView.setHighlightedTableColumn_(tableColumn)`
- Dispatch sort:
  - If `interface` has `on_header_sort` callable attribute: `interface.on_header_sort(col_index, toga_col, ascending)`
  - Else default automatic sort:
    - Determine column index and accessor.
    - Extract rows from `interface.data`.
    - Sort rows using safe comparator (handling `None`, string case-insensitivity, numbers).
    - If ascending is False, reverse.
    - Update `interface.data` and retain current selection if possible.

### 2. View-Level Coordination

#### `CloneListView` (`src/atbclone/gui/views/clone_list.py`)
- Custom handler / sync on table header click:
  - Column 0 (Clone Name): Sorts by `clone_name.lower()`. Syncs top bar to `sort_name` (if ASC).
  - Column 1 (Source App): Sorts by `source_app.lower()`.
  - Column 2 (Strategy): Sorts by `strategy.lower()`.
  - Column 3 (Proxy): Sorts by proxy enabled / proxy summary.
  - Column 4 (Created At): Sorts by `created_at`. Syncs top bar to `sort_newest` (DESC) or `sort_oldest` (ASC).
- Table selection preservation: `get_selected_record()` continues to resolve records by unique identifiers across sort reorders.

#### `RecipeListView` (`src/atbclone/gui/views/recipe_list.py`)
- Custom handler / sync on table header click:
  - Column 0 (App Name): Sorts by `app_name.lower()`. Syncs top bar to `sort_name_asc` / `sort_name_desc`.
  - Column 1 (Bundle ID): Sorts by `bundle_id.lower()`.
  - Column 2 (Strategy): Sorts by `strategy`. Syncs top bar to `sort_strategy`.
  - Column 3 (Origin): Sorts by `is_builtin`.
- Table selection preservation: `get_selected_recipe_item()` resolves recipes correctly after sorting.

#### `DoctorView` (`src/atbclone/gui/views/doctor_view.py`)
- Default automatic sorting handles status icons, check items, details, and hints cleanly.

## Testing & Verification Plan
1. **Automated Unit Tests** (`tests/gui/test_table_header_sort.py`):
   - Test `tableView_didClickTableColumn_` callback invocation and column toggling.
   - Test sort indicator assignment (`NSAscendingSortIndicator`, `NSDescendingSortIndicator`).
   - Test default generic table data sorting with mixed types and case-insensitivity.
   - Test `CloneListView` table header sorting with selection preservation.
   - Test `RecipeListView` table header sorting with top bar synchronization.
2. **Full Regression Suite**:
   - Run `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/` to ensure all tests pass.
