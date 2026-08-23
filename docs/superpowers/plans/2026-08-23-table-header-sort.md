# Table Header Sorting Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement native macOS table header sorting (with native chevron indicators and ascending/descending toggle) for all Table widgets, with two-way sync for CloneListView and RecipeListView.

**Architecture:** Inject `tableView:didClickTableColumn:` onto `TogaTable` in `patch_cocoa.py` to control native macOS sort indicators and invoke automatic/custom sorting. Integrate custom header sort handlers and toolbar sync into `CloneListView` and `RecipeListView`.

**Tech Stack:** Python 3.12, BeeWare Toga, Cocoa / rubicon-objc, pytest.

## Global Constraints
- Target macOS native patterns, PySide6/Toga Cocoa, Python 3.12+.
- Zero third-party runtime dependencies outside existing environment.
- Test command: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/`
- All tests must pass cleanly.

---

### Task 1: Cocoa Native Table Header Sorting Patch

**Files:**
- Modify: `src/atbclone/gui/patch_cocoa.py`
- Create: `tests/gui/test_table_header_sort.py`

**Interfaces:**
- Consumes: `TogaTable` from `toga_cocoa.widgets.table`, `NSImage` from `toga_cocoa.libs`.
- Produces: `tableView_didClickTableColumn_` delegate method on `TogaTable`, automatic sorting support, and `on_header_sort` callback interface on `toga.Table`.

- [ ] **Step 1: Write the unit tests for Cocoa Table header sorting**

Create `tests/gui/test_table_header_sort.py`:
```python
"""Tests for Cocoa Table header sorting patch."""

import pytest
import toga
from unittest.mock import MagicMock
from atbclone.gui.patch_cocoa import patch_cocoa_widgets, configure_cocoa_table


def test_table_header_sort_generic():
    """Verify generic Table sorts data on header click."""
    patch_cocoa_widgets()
    table = toga.Table(columns=["Name", "Age"])
    table.data = [
        ("Charlie", 30),
        ("Alice", 25),
        ("Bob", 20),
    ]

    # Native delegate method check
    impl = table._impl
    native_table = impl.native_table
    assert hasattr(native_table, "tableView_didClickTableColumn_")

    col_name = native_table.tableColumns[0]
    # First click: sort ascending
    native_table.tableView_didClickTableColumn_(native_table, col_name)
    assert [r.name for r in table.data] == ["Alice", "Bob", "Charlie"]

    # Second click: sort descending
    native_table.tableView_didClickTableColumn_(native_table, col_name)
    assert [r.name for r in table.data] == ["Charlie", "Bob", "Alice"]

    # Click age column: sort ascending
    col_age = native_table.tableColumns[1]
    native_table.tableView_didClickTableColumn_(native_table, col_age)
    assert [r.age for r in table.data] == [20, 25, 30]


def test_table_custom_header_sort_callback():
    """Verify custom on_header_sort callback is called if defined."""
    patch_cocoa_widgets()
    table = toga.Table(columns=["Title", "Count"])
    table.data = [("A", 1), ("B", 2)]
    
    mock_cb = MagicMock()
    table.on_header_sort = mock_cb

    native_table = table._impl.native_table
    col = native_table.tableColumns[0]
    native_table.tableView_didClickTableColumn_(native_table, col)

    mock_cb.assert_called_once()
    args, kwargs = mock_cb.call_args
    assert args[0] == 0  # col index
    assert args[2] is True  # ascending
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/gui/test_table_header_sort.py`
Expected: FAIL with AttributeError or missing `tableView_didClickTableColumn_`.

- [ ] **Step 3: Implement Cocoa Table header sorting patch in `patch_cocoa.py`**

In `src/atbclone/gui/patch_cocoa.py`:
- Add `tableView_didClickTableColumn_` to `TogaTable` with sort state tracking (`_sort_col_id`, `_sort_ascending`).
- Set `NSAscendingSortIndicator` / `NSDescendingSortIndicator` on the clicked column.
- Highlight the clicked column with `setHighlightedTableColumn_`.
- If `interface` has `on_header_sort`, call it.
- Otherwise perform default safe sorting on `interface.data`.

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/gui/test_table_header_sort.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/atbclone/gui/patch_cocoa.py tests/gui/test_table_header_sort.py
git commit -m "feat: implement native Cocoa Table header sorting patch"
```

---

### Task 2: CloneListView Header Sorting & Toolbar Sync Integration

**Files:**
- Modify: `src/atbclone/gui/views/clone_list.py`
- Modify: `tests/gui/test_clone_views.py`

**Interfaces:**
- Consumes: `table.on_header_sort` from Task 1, `self._filtered_clones`.
- Produces: `on_table_header_sort` in `CloneListView` with full column sorting and toolbar sync.

- [ ] **Step 1: Write test for CloneListView header sorting**

Add to `tests/gui/test_clone_views.py`:
```python
@pytest.mark.asyncio
async def test_clone_list_view_table_header_sort():
    view = CloneListView()
    view._raw_clones = [
        CloneRecord(clone_name="Beta", source_app="App2", bundle_id="b.app", strategy="soft_clone", dest_path="/p2", data_dir="/d2", created_at="2026-08-20T10:00:00"),
        CloneRecord(clone_name="Alpha", source_app="App1", bundle_id="a.app", strategy="hard_clone", dest_path="/p1", data_dir="/d1", created_at="2026-08-21T10:00:00"),
    ]
    view._apply_filter()
    
    # Sort column 0 (Name) ASC
    view.on_table_header_sort(0, view.table.columns[0], ascending=True)
    assert [r.clone_name for r in view._filtered_clones] == ["Alpha", "Beta"]
    assert view.top_bar.sort_select.value == view.sort_name

    # Sort column 0 (Name) DESC
    view.on_table_header_sort(0, view.table.columns[0], ascending=False)
    assert [r.clone_name for r in view._filtered_clones] == ["Beta", "Alpha"]

    # Sort column 4 (Created At) DESC
    view.on_table_header_sort(4, view.table.columns[4], ascending=False)
    assert [r.clone_name for r in view._filtered_clones] == ["Alpha", "Beta"]
    assert view.top_bar.sort_select.value == view.sort_newest
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/gui/test_clone_views.py -k test_clone_list_view_table_header_sort`
Expected: FAIL with AttributeError (`on_table_header_sort` missing).

- [ ] **Step 3: Implement `on_table_header_sort` in `CloneListView`**

In `src/atbclone/gui/views/clone_list.py`:
- Attach `self.table.on_header_sort = self.on_table_header_sort`.
- Implement `on_table_header_sort(self, col_index: int, column, ascending: bool)`:
  - Column 0 (Name): sort by `clone_name.lower()` (ASC -> sync `sort_name`).
  - Column 1 (Source App): sort by `source_app.lower()`.
  - Column 2 (Strategy): sort by `strategy`.
  - Column 3 (Proxy): sort by `(proxy_enabled, proxy_summary)`.
  - Column 4 (Created At): sort by `created_at` (DESC -> sync `sort_newest`, ASC -> sync `sort_oldest`).
  - Update `_filtered_clones` and re-render.

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/gui/test_clone_views.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/atbclone/gui/views/clone_list.py tests/gui/test_clone_views.py
git commit -m "feat: add table header sorting and toolbar sync in CloneListView"
```

---

### Task 3: RecipeListView & DoctorView Header Sorting Integration

**Files:**
- Modify: `src/atbclone/gui/views/recipe_list.py`
- Modify: `src/atbclone/gui/views/doctor_view.py`
- Modify: `tests/gui/test_recipe_ui.py`
- Modify: `tests/gui/test_probe_and_doctor_ui.py`

**Interfaces:**
- Consumes: `table.on_header_sort` from Task 1.
- Produces: `on_table_header_sort` in `RecipeListView` with toolbar sync.

- [ ] **Step 1: Write test for RecipeListView header sorting**

Add to `tests/gui/test_recipe_ui.py`:
```python
def test_recipe_list_view_table_header_sort():
    view = RecipeListView()
    view._raw_recipes = [
        {"app_name": "Zed", "bundle_id": "dev.zed.Zed", "strategy": "hard_clone", "is_builtin": True, "recipe": None},
        {"app_name": "Ableton", "bundle_id": "com.ableton.live", "strategy": "soft_clone", "is_builtin": False, "recipe": None},
    ]
    view._apply_filter()

    # Sort column 0 (App Name) ASC
    view.on_table_header_sort(0, view.table.columns[0], ascending=True)
    assert [r["app_name"] for r in view._filtered_recipes] == ["Ableton", "Zed"]
    assert view.top_bar.sort_select.value == view.sort_name_asc

    # Sort column 0 (App Name) DESC
    view.on_table_header_sort(0, view.table.columns[0], ascending=False)
    assert [r["app_name"] for r in view._filtered_recipes] == ["Zed", "Ableton"]
    assert view.top_bar.sort_select.value == view.sort_name_desc

    # Sort column 2 (Strategy) ASC
    view.on_table_header_sort(2, view.table.columns[2], ascending=True)
    assert view.top_bar.sort_select.value == view.sort_strategy
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/gui/test_recipe_ui.py -k test_recipe_list_view_table_header_sort`
Expected: FAIL.

- [ ] **Step 3: Implement `on_table_header_sort` in `RecipeListView`**

In `src/atbclone/gui/views/recipe_list.py`:
- Attach `self.table.on_header_sort = self.on_table_header_sort`.
- Implement `on_table_header_sort`:
  - Column 0 (App Name): sort by `app_name.lower()` (ASC -> `sort_name_asc`, DESC -> `sort_name_desc`).
  - Column 1 (Bundle ID): sort by `bundle_id.lower()`.
  - Column 2 (Strategy): sort by `strategy` (ASC -> `sort_strategy`).
  - Column 3 (Origin): sort by `is_builtin`.
  - Update `_filtered_recipes` and re-render.

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/gui/test_recipe_ui.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/atbclone/gui/views/recipe_list.py tests/gui/test_recipe_ui.py
git commit -m "feat: add table header sorting and toolbar sync in RecipeListView"
```

---

### Task 4: Full Suite Verification & Regression Check

**Files:**
- Verify: All test files across the repository

- [ ] **Step 1: Run full test suite**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/`
Expected: 350+ passed, 0 failures.

- [ ] **Step 2: Verify code formatting and linting**

Run: `PYTHONPATH=src conda run -n ATBClone python -m flake8 src/ tests/ || true`

- [ ] **Step 3: Final commit and summary**
