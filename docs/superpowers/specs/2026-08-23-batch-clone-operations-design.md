# Design Specification: Batch Update and Delete in "My Clones" List View

- **Topic**: Batch clone operations (Update and Delete) via multi-selection in Table View
- **Date**: 2026-08-23
- **Status**: Approved

## 1. Overview & Objectives

In ATBClone's GUI, the "My Clones" (`CloneListView`) view provides two presentation modes: a Grid View (Card view) and a Table View (List view). Currently, the Table View only allows selecting a single clone row at a time to perform actions (Launch, Open Dir, Update, Edit, Detail, Delete).

This specification outlines the architecture and UI/UX behavior to enable native multi-selection in the Table View (`toga.Table` with `multiple_select=True`) and support executing batch operations:
1. **Batch Update**: Sequentially re-clone/update multiple selected clone instances with live button progress and final error summary reporting.
2. **Batch Delete**: Dual confirmation prompts (app removal & optional data directory deletion) followed by sequential deletion with live progress and final error summary reporting.

---

## 2. UI / UX Design

### 2.1 Multi-Selection Mechanism
- `toga.Table` is instantiated with `multiple_select=True`.
- On macOS, users can use native selection gestures:
  - `Cmd + Click` to toggle selection of individual rows.
  - `Shift + Click` to select a continuous range of rows.
  - `Cmd + A` to select all rows.

### 2.2 Responsive Bottom Action Bar
The bottom action buttons adapt dynamically based on the number of selected clones:

| Selection Count | Launch (启动) | Open Dir (打开目录) | Update (更新) | Edit (编辑) | Detail (详情) | Delete (删除) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **0 items** | Disabled | Disabled | Disabled (`更新`) | Disabled | Disabled | Disabled (`删除`) |
| **1 item** | Enabled | Enabled | Enabled (`更新`) | Enabled | Enabled | Enabled (`删除`) |
| **N items (≥ 2)** | Disabled | Disabled | Enabled (`批量更新 (N)`) | Disabled | Disabled | Enabled (`批量删除 (N)`) |

*Note*: If any selected clone is currently in `_busy_clones`, action buttons are safely disabled to prevent concurrent mutation.

---

## 3. Workflow & Error Handling

### 3.1 Batch Update (`on_update_clones_action`)
1. **Trigger**: User clicks `批量更新 (N)`.
2. **Busy Protection**: Add all selected clone names to `_busy_clones`. Disable action buttons.
3. **Sequential Execution**:
   - Loop through selected `CloneRecord`s one by one.
   - Update button text to `正在更新 (i/N)...` (or localized `btn_updating_progress`).
   - Call `await self.clone_service.update_clone(record.clone_name)`.
   - If an exception occurs, record `(record.clone_name, error_message)` in a `failed_list` without aborting the remaining items.
4. **Cleanup & Summary**:
   - Remove records from `_busy_clones`.
   - Call `await self.refresh_clones()`.
   - If `failed_list` is non-empty, display an error dialog summarizing succeeded and failed items with reasons.
   - Reset button states via `on_table_select`.

### 3.2 Batch Delete (`on_delete_clones_action`)
1. **Confirmation Flow**:
   - **Dialog 1 (App deletion confirmation)**: Prompt `确认要删除选中的 N 个分身应用吗？` listing the clone names. If cancelled by user, abort immediately.
   - **Dialog 2 (Data directory cleanup confirmation)**: Prompt `是否同时清理这 N 个分身的用户数据与配置目录？`. Record `delete_data: bool`.
2. **Busy Protection**: Add selected clone names to `_busy_clones`. Disable action buttons.
3. **Sequential Execution**:
   - Loop through selected records.
   - Update button text to `正在删除 (i/N)...` (or localized `btn_deleting_progress`).
   - Call `await self.clone_service.remove_clone(record.clone_name, with_data=delete_data)`.
   - Record any failures in `failed_list`.
4. **Cleanup & Summary**:
   - Remove from `_busy_clones`.
   - Call `await self.refresh_clones()`.
   - If `failed_list` is non-empty, display summary error dialog.
   - Reset button states via `on_table_select`.

---

## 4. Internationalization (i18n) Keys

Add the following keys across all 9 supported languages (`en`, `zh`, `zh_TW`, `ja`, `ko`, `de`, `fr`, `ru`, `es`) in `src/atbclone/core/i18n.py`:

- `btn_batch_update`: `批量更新 ({count})` / `Update Selected ({count})`
- `btn_batch_delete`: `批量删除 ({count})` / `Delete Selected ({count})`
- `btn_updating_progress`: `正在更新 ({current}/{total})...` / `Updating ({current}/{total})...`
- `btn_deleting_progress`: `正在删除 ({current}/{total})...` / `Deleting ({current}/{total})...`
- `dialog_batch_delete_confirm_title`: `确认批量删除` / `Confirm Batch Deletion`
- `dialog_batch_delete_confirm_msg`: `确定要删除选中的 {count} 个分身应用吗？\n{names}`
- `dialog_batch_delete_data_confirm_title`: `清理用户数据目录` / `Clean Data Directories`
- `dialog_batch_delete_data_confirm_msg`: `是否同时清理这 {count} 个分身的用户数据与配置目录？\n选择“取消”将保留数据目录，仅删除分身应用本体。`
- `dialog_batch_summary_title`: `批量操作结果` / `Batch Operation Results`
- `dialog_batch_summary_msg`: `操作完成：{success} 个成功，{failed} 个失败。\n\n失败详情：\n{errors}`

---

## 5. Implementation Files

- **`src/atbclone/core/i18n.py`**: Add batch operation dictionary keys and translations.
- **`src/atbclone/gui/views/clone_list.py`**:
  - `toga.Table(..., multiple_select=True)`
  - `get_selected_records() -> list[CloneRecord]`
  - Dynamic button updates in `on_table_select`
  - Refactored `on_update_clone` and `on_delete_clone` with batch support
- **`tests/test_gui_clone_list.py`**: Unit tests verifying selection parsing and batch orchestration logic.
