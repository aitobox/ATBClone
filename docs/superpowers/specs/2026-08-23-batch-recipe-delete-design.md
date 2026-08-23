# Design Specification: Batch Deletion of Custom Recipes in "My Rules" (Recipe List) View

- **Topic**: Batch custom recipe deletion via multi-selection in RecipeListView
- **Date**: 2026-08-23
- **Status**: Approved

## 1. Overview & Objectives

In ATBClone's GUI, the "Clone Recipes / My Rules" (`RecipeListView`) view displays both built-in recipes and custom user-defined recipes in either Grid (Card) or Table (List) modes. Currently, the Table mode only supports selecting a single recipe at a time for editing or deletion.

This specification outlines the architecture and UI/UX behavior to enable native multi-selection in the Recipe Table View (`toga.Table` with `multiple_select=True`) and support executing batch deletion of custom recipes:
1. **Multi-Selection**: Support macOS native multi-selection gestures (Cmd+Click, Shift+Click, Cmd+A) on the recipe table.
2. **Selective Batch Deletion**: Accurately distinguish between built-in rules and custom rules when multi-selecting.
3. **Smart Skip Logic**: When a selection contains both custom and built-in rules, allow batch deleting the custom rules while safely skipping built-in rules, with explicit user notification in the confirmation dialog.
4. **Progress & Error Reporting**: Provide live deletion progress on the action button and summary reporting for any failures.

---

## 2. UI / UX Design

### 2.1 Multi-Selection Mechanism
- `toga.Table` is instantiated with `multiple_select=True`.
- On macOS, users can use native selection gestures:
  - `Cmd + Click` to toggle selection of individual recipe rows.
  - `Shift + Click` to select a continuous range of rows.
  - `Cmd + A` to select all visible rows.

### 2.2 Responsive Bottom Action Bar
The bottom action buttons adapt dynamically based on the number of selected recipes and whether they are custom or built-in:

| Selection State | Edit (编辑) | Delete (删除) Button State | Delete Button Text |
| :--- | :--- | :--- | :--- |
| **0 items selected** | Disabled | Disabled | `🗑️ 删除` (`btn_delete`) |
| **1 item: Custom Recipe** | Enabled | Enabled | `🗑️ 删除` (`btn_delete`) |
| **1 item: Built-in Recipe** | Enabled | Disabled | `🗑️ 删除` (`btn_delete`) |
| **N items (≥ 2): All Custom ($N$ custom, $0$ builtin)** | Disabled | Enabled | `🗑️ 批量删除 (N)` (`btn_batch_delete`) |
| **N items (≥ 2): Mixed ($C$ custom, $B$ builtin, $C > 0$)** | Disabled | Enabled | `🗑️ 批量删除 (C)` (`btn_batch_delete`) |
| **N items (≥ 2): All Built-in ($0$ custom, $N$ builtin)** | Disabled | Disabled | `🗑️ 删除` (`btn_delete`) |

---

## 3. Workflow & Confirmation Dialogs

### 3.1 Confirmation Dialog Scenarios
When the user clicks the Delete button:

1. **Scenario A: Single Custom Recipe**
   - Dialog Title: `dialog_recipe_delete_confirm_title` ("删除规则" / "Delete Recipe")
   - Dialog Message: `dialog_recipe_delete_confirm_msg` ("确定要删除自定义规则 '{name}' 吗？")
   - Action: If confirmed, delete the single custom recipe.

2. **Scenario B: Pure Custom Recipes Multi-selection ($C \ge 2, B = 0$)**
   - Dialog Title: `dialog_recipe_batch_delete_confirm_title` ("确认批量删除规则" / "Confirm Batch Deletion")
   - Dialog Message: `dialog_recipe_batch_delete_confirm_msg` ("确定要删除选中的 {count} 个自定义规则吗？\n{names}")
   - Action: If confirmed, proceed to batch delete.

3. **Scenario C: Mixed Selection ($C \ge 1, B \ge 1$)**
   - Dialog Title: `dialog_recipe_batch_delete_confirm_mixed_title` ("确认批量删除规则" / "Confirm Batch Deletion")
   - Dialog Message: `dialog_recipe_batch_delete_confirm_mixed_msg`
     ```text
     选中的项目中包含 {custom_count} 个自定义规则与 {builtin_count} 个内置规则。
     系统将删除自定义规则并自动跳过内置规则。

     待删除规则：
     {names}

     是否继续？
     ```
   - Action: If confirmed, proceed to batch delete only the custom recipes.

### 3.2 Execution Loop & Error Handling
1. **Button Feedback**: Disable `btn_delete` and update text to `t("btn_deleting_progress", current=i, total=len(custom_items))` (e.g. `🗑️ 正在删除 (1/3)...`).
2. **Sequential Deletion**: Call `await self.recipe_service.delete_custom_recipe(item["bundle_id"])` for each custom rule.
3. **Failure Collection**: If any deletion fails, append `(app_name, error_str)` to `failed_list`.
4. **Cleanup & Refresh**:
   - Reload recipes via `await self.refresh_recipes()`.
   - Restore table selection / focus if appropriate using Cocoa `NSMutableIndexSet`.
   - If `failed_list` is non-empty, display an error dialog summarizing failed items and reasons.
   - Re-evaluate selection states via `on_table_select`.

---

## 4. Internationalization (i18n)

Add the following keys across all 9 supported languages (`en`, `zh`, `zh_TW`, `ja`, `ko`, `de`, `fr`, `ru`, `es`) in `src/atbclone/core/i18n.py`:

- `dialog_recipe_delete_confirm_title`: `删除规则` / `Delete Recipe`
- `dialog_recipe_delete_confirm_msg`: `确定要删除自定义规则 '{name}' 吗？` / `Are you sure you want to delete custom recipe '{name}'?`
- `dialog_recipe_batch_delete_confirm_title`: `确认批量删除规则` / `Confirm Batch Deletion`
- `dialog_recipe_batch_delete_confirm_msg`: `确定要删除选中的 {count} 个自定义规则吗？\n{names}` / `Are you sure you want to delete {count} selected custom recipes?\n{names}`
- `dialog_recipe_batch_delete_confirm_mixed_title`: `确认批量删除规则` / `Confirm Batch Deletion`
- `dialog_recipe_batch_delete_confirm_mixed_msg`: `选中的项目中包含 {custom_count} 个自定义规则与 {builtin_count} 个内置规则。\n系统将删除自定义规则并自动跳过内置规则。\n\n待删除规则：\n{names}\n\n是否继续？` / `Selected items contain {custom_count} custom recipe(s) and {builtin_count} built-in recipe(s).\nThe system will delete the custom recipes and skip built-in recipes.\n\nRecipes to delete:\n{names}\n\nDo you want to continue?`

---

## 5. Implementation Files

- **`src/atbclone/core/i18n.py`**:
  - Define new recipe delete dialog confirmation keys with 9-language translations.
- **`src/atbclone/gui/views/recipe_list.py`**:
  - Configure `toga.Table(..., multiple_select=True)`.
  - Add helper `_extract_bundle_id` and `get_selected_recipe_items()`.
  - Update `on_table_select` to dynamically control `btn_edit` and `btn_delete` based on custom/builtin rule counts.
  - Refactor `on_delete_recipe` to handle single, pure batch, and mixed batch scenarios with dialogs, progress indicators, and error summaries.
  - Preserve multi-selection across table refresh/sort via Cocoa index sets.
- **`tests/gui/test_recipe_list_view.py`**:
  - Add unit tests covering table multi-select extraction, button states, mixed-selection handling, and batch deletion workflows.
