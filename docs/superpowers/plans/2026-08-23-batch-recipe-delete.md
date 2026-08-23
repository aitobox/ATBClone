# Batch Recipe Deletion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enable multi-selection and batch deletion of custom recipes in RecipeListView with smart skip of built-in rules, confirmation dialogs, and live deletion progress.

**Architecture:** Extend toga.Table with multiple_select=True, implement robust multi-row selection extractor and Cocoa index set restoration, enhance action button states, and add scenario-based confirmation dialogs with i18n support.

**Tech Stack:** Python 3.12+, PySide6 / Toga Cocoa, rubicon-objc, pytest, pytest-asyncio

## Global Constraints

- Target macOS native patterns, PySide6 / Toga Cocoa compatibility.
- Branch: `main`
- Zero external third-party dependencies outside the project's standard stack.
- Multi-language support across all 9 languages in `src/atbclone/core/i18n.py`.
- Test command: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/`

---

### Task 1: Add i18n Translation Keys for Recipe Deletion Confirmation Dialogs

**Files:**
- Modify: `src/atbclone/core/i18n.py`
- Test: `tests/test_i18n.py`

**Interfaces:**
- Produces:
  - `dialog_recipe_delete_confirm_title`: `删除规则` / `Delete Recipe`
  - `dialog_recipe_delete_confirm_msg`: `确定要删除自定义规则 '{name}' 吗？` / `Are you sure you want to delete custom recipe '{name}'?`
  - `dialog_recipe_batch_delete_confirm_title`: `确认批量删除规则` / `Confirm Batch Deletion`
  - `dialog_recipe_batch_delete_confirm_msg`: `确定要删除选中的 {count} 个自定义规则吗？\n{names}` / `Are you sure you want to delete {count} selected custom recipes?\n{names}`
  - `dialog_recipe_batch_delete_confirm_mixed_title`: `确认批量删除规则` / `Confirm Batch Deletion`
  - `dialog_recipe_batch_delete_confirm_mixed_msg`: `选中的项目中包含 {custom_count} 个自定义规则与 {builtin_count} 个内置规则。\n系统将删除自定义规则并自动跳过内置规则。\n\n待删除规则：\n{names}\n\n是否继续？` / `Selected items contain {custom_count} custom recipe(s) and {builtin_count} built-in recipe(s).\nThe system will delete the custom recipes and skip built-in recipes.\n\nRecipes to delete:\n{names}\n\nDo you want to continue?`

- [ ] **Step 1: Write failing test for new i18n keys**

Add test in `tests/test_i18n.py`:
```python
def test_recipe_delete_dialog_i18n_keys():
    from atbclone.core.i18n import t, set_language
    for lang in ("zh", "en", "ja"):
        set_language(lang)
        msg_single_title = t("dialog_recipe_delete_confirm_title")
        assert len(msg_single_title) > 0
        msg_single = t("dialog_recipe_delete_confirm_msg", name="TestApp")
        assert "TestApp" in msg_single
        msg_batch_title = t("dialog_recipe_batch_delete_confirm_title")
        assert len(msg_batch_title) > 0
        msg_batch = t("dialog_recipe_batch_delete_confirm_msg", count=3, names="App1, App2, App3")
        assert "3" in msg_batch and "App1" in msg_batch
        msg_mixed_title = t("dialog_recipe_batch_delete_confirm_mixed_title")
        assert len(msg_mixed_title) > 0
        msg_mixed = t("dialog_recipe_batch_delete_confirm_mixed_msg", custom_count=2, builtin_count=1, names="App1, App2")
        assert "2" in msg_mixed and "1" in msg_mixed and "App1" in msg_mixed
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_i18n.py::test_recipe_delete_dialog_i18n_keys -v`
Expected: FAIL with key missing / KeyError

- [ ] **Step 3: Add dictionary entries in `src/atbclone/core/i18n.py`**

Add entries for all 9 supported languages:
```python
    "dialog_recipe_delete_confirm_title": {
        "en": "Delete Recipe",
        "zh": "删除规则",
        "zh_TW": "刪除規則",
        "ja": "レシピを削除",
        "ko": "레시피 삭제",
        "de": "Rezept löschen",
        "fr": "Supprimer la recette",
        "ru": "Удалить рецепт",
        "es": "Eliminar receta",
    },
    "dialog_recipe_delete_confirm_msg": {
        "en": "Are you sure you want to delete custom recipe '{name}'?",
        "zh": "确定要删除自定义规则 '{name}' 吗？",
        "zh_TW": "確定要刪除自訂規則 '{name}' 嗎？",
        "ja": "カスタムレシピ '{name}' を削除してもよろしいですか？",
        "ko": "사용자 정의 레시피 '{name}'을(를) 삭제하시겠습니까?",
        "de": "Möchten Sie das benutzerdefinierte Rezept '{name}' wirklich löschen?",
        "fr": "Êtes-vous sûr de vouloir supprimer la recette personnalisée '{name}' ?",
        "ru": "Вы уверены, что хотите удалить пользовательский рецепт '{name}'?",
        "es": "¿Seguro que desea eliminar la receta personalizada '{name}'?",
    },
    "dialog_recipe_batch_delete_confirm_title": {
        "en": "Confirm Batch Deletion",
        "zh": "确认批量删除规则",
        "zh_TW": "確認批次刪除規則",
        "ja": "一括削除の確認",
        "ko": "일괄 삭제 확인",
        "de": "Massenlöschung bestätigen",
        "fr": "Confirmer la suppression groupée",
        "ru": "Подтверждение массового удаления",
        "es": "Confirmar eliminación por lotes",
    },
    "dialog_recipe_batch_delete_confirm_msg": {
        "en": "Are you sure you want to delete {count} selected custom recipes?\n{names}",
        "zh": "确定要删除选中的 {count} 个自定义规则吗？\n{names}",
        "zh_TW": "確定要刪除選取的 {count} 個自訂規則嗎？\n{names}",
        "ja": "選択した {count} 件のカスタムレシピを削除してもよろしいですか？\n{names}",
        "ko": "선택한 {count}개의 사용자 정의 레시피를 삭제하시겠습니까?\n{names}",
        "de": "Möchten Sie die {count} ausgewählten Rezepte wirklich löschen?\n{names}",
        "fr": "Voulez-vous vraiment supprimer les {count} recettes personnalisées sélectionnées ?\n{names}",
        "ru": "Вы уверены, что хотите удалить выбранные рецепты ({count})?\n{names}",
        "es": "¿Seguro que desea eliminar las {count} recetas seleccionadas?\n{names}",
    },
    "dialog_recipe_batch_delete_confirm_mixed_title": {
        "en": "Confirm Batch Deletion",
        "zh": "确认批量删除规则",
        "zh_TW": "確認批次刪除規則",
        "ja": "一括削除の確認",
        "ko": "일괄 삭제 확인",
        "de": "Massenlöschung bestätigen",
        "fr": "Confirmer la suppression groupée",
        "ru": "Подтверждение массового удаления",
        "es": "Confirmar eliminación por lotes",
    },
    "dialog_recipe_batch_delete_confirm_mixed_msg": {
        "en": "Selected items contain {custom_count} custom recipe(s) and {builtin_count} built-in recipe(s).\nThe system will delete the custom recipes and skip built-in recipes.\n\nRecipes to delete:\n{names}\n\nDo you want to continue?",
        "zh": "选中的项目中包含 {custom_count} 个自定义规则与 {builtin_count} 个内置规则。\n系统将删除自定义规则并自动跳过内置规则。\n\n待删除规则：\n{names}\n\n是否继续？",
        "zh_TW": "選取的項目中包含 {custom_count} 個自訂規則與 {builtin_count} 個內建規則。\n系統將刪除自訂規則並自動跳過內建規則。\n\n待刪除規則：\n{names}\n\n是否繼續？",
        "ja": "選択した項目には {custom_count} 件のカスタムレシピと {builtin_count} 件のプリセットレシピが含まれています。\nカスタムレシピのみが削除され、プリセットレシピはスキップされます。\n\n削除対象:\n{names}\n\n続行しますか？",
        "ko": "선택한 항목에 {custom_count}개의 사용자 정의 레시피와 {builtin_count}개의 기본 레시피가 포함되어 있습니다.\n사용자 정의 레시피만 삭제되고 기본 레시피는 건너뜁니다.\n\n삭제할 레시피:\n{names}\n\n계속하시겠습니까?",
        "de": "Die Auswahl enthält {custom_count} benutzerdefinierte und {builtin_count} integrierte Rezepte.\nNur benutzerdefinierte Rezepte werden gelöscht.\n\nZu löschen:\n{names}\n\nFortfahren?",
        "fr": "La sélection contient {custom_count} recettes personnalisées et {builtin_count} intégrées.\nSeules les personnalisées seront supprimées.\n\nÀ supprimer :\n{names}\n\nContinuer ?",
        "ru": "Выбрано {custom_count} польз. и {builtin_count} встроенных рецептов.\nБудут удалены только пользовательские.\n\nК удалению:\n{names}\n\nПродолжить?",
        "es": "La selección contiene {custom_count} recetas personalizadas y {builtin_count} integradas.\nSolo se eliminarán las personalizadas.\n\nA eliminar:\n{names}\n\n¿Continuar?",
    },
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_i18n.py::test_recipe_delete_dialog_i18n_keys -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/atbclone/core/i18n.py tests/test_i18n.py
git commit -m "feat(i18n): add translation keys for recipe deletion confirmation dialogs"
```

---

### Task 2: Implement Multi-Select Extraction & Button State Management in RecipeListView

**Files:**
- Modify: `src/atbclone/gui/views/recipe_list.py`
- Test: `tests/gui/test_recipe_ui.py`

**Interfaces:**
- Consumes: `toga.Table(multiple_select=True)`, `t("btn_delete")`, `t("btn_batch_delete", count=...)`
- Produces:
  - `_extract_bundle_id(item, known_bundle_ids: set[str]) -> Optional[str]`
  - `get_selected_recipe_items(selection=None) -> list[dict]`
  - `get_selected_recipe_item(row=None) -> Optional[dict]`
  - Dynamic button updates in `on_table_select(self, widget)`

- [ ] **Step 1: Write failing test for multi-selection extraction & button states**

Add test in `tests/gui/test_recipe_ui.py`:
```python
def test_recipe_list_view_multi_select_and_button_states():
    view = RecipeListView()
    view._filtered_recipes = [
        {"app_name": "CustomApp1", "bundle_id": "com.custom.app1", "strategy": "hard_clone", "is_builtin": False, "recipe": MagicMock()},
        {"app_name": "CustomApp2", "bundle_id": "com.custom.app2", "strategy": "soft_clone", "is_builtin": False, "recipe": MagicMock()},
        {"app_name": "BuiltinApp1", "bundle_id": "com.builtin.app1", "strategy": "hard_clone", "is_builtin": True, "recipe": MagicMock()},
    ]

    # 1. Zero selection
    with patch.object(view, "get_selected_recipe_items", return_value=[]):
        view.on_table_select(view.table)
        assert view.btn_edit.enabled is False
        assert view.btn_delete.enabled is False
        assert "🗑️" in view.btn_delete.text

    # 2. Single custom selection
    with patch.object(view, "get_selected_recipe_items", return_value=[view._filtered_recipes[0]]):
        view.on_table_select(view.table)
        assert view.btn_edit.enabled is True
        assert view.btn_delete.enabled is True

    # 3. Single built-in selection
    with patch.object(view, "get_selected_recipe_items", return_value=[view._filtered_recipes[2]]):
        view.on_table_select(view.table)
        assert view.btn_edit.enabled is True
        assert view.btn_delete.enabled is False

    # 4. Multiple custom selection (2 items)
    with patch.object(view, "get_selected_recipe_items", return_value=[view._filtered_recipes[0], view._filtered_recipes[1]]):
        view.on_table_select(view.table)
        assert view.btn_edit.enabled is False
        assert view.btn_delete.enabled is True
        assert "(2)" in view.btn_delete.text

    # 5. Mixed selection (1 custom + 1 built-in)
    with patch.object(view, "get_selected_recipe_items", return_value=[view._filtered_recipes[0], view._filtered_recipes[2]]):
        view.on_table_select(view.table)
        assert view.btn_edit.enabled is False
        assert view.btn_delete.enabled is True
        assert "(1)" in view.btn_delete.text

    # 6. All built-in multi selection (2 built-in items)
    builtin2 = {"app_name": "BuiltinApp2", "bundle_id": "com.builtin.app2", "strategy": "hard_clone", "is_builtin": True, "recipe": MagicMock()}
    with patch.object(view, "get_selected_recipe_items", return_value=[view._filtered_recipes[2], builtin2]):
        view.on_table_select(view.table)
        assert view.btn_edit.enabled is False
        assert view.btn_delete.enabled is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/gui/test_recipe_ui.py::test_recipe_list_view_multi_select_and_button_states -v`
Expected: FAIL with `get_selected_recipe_items` not found / assertion errors

- [ ] **Step 3: Implement multi-select parsing and dynamic buttons in `RecipeListView`**

In `src/atbclone/gui/views/recipe_list.py`:
1. Set `multiple_select=True` on `toga.Table`.
2. Implement `_extract_bundle_id`:
```python
    def _extract_bundle_id(self, item, known_bundle_ids: set[str]) -> Optional[str]:
        if item is None:
            return None
        if isinstance(item, str):
            return item if item in known_bundle_ids else None
        bundle_id = getattr(item, "bundle_id", None) or getattr(item, t("recipe_col_bundle_id"), None)
        if bundle_id and bundle_id in known_bundle_ids:
            return bundle_id
        if hasattr(item, "_raw") and item._raw and len(item._raw) > 1 and item._raw[1] in known_bundle_ids:
            return item._raw[1]
        if isinstance(item, (tuple, list)) and len(item) > 1:
            if item[1] in known_bundle_ids:
                return item[1]
        if hasattr(item, "__dict__"):
            for k, v in item.__dict__.items():
                if not k.startswith("_") and isinstance(v, str) and v in known_bundle_ids:
                    return v
        return None
```
3. Implement `get_selected_recipe_items` & `get_selected_recipe_item`:
```python
    def get_selected_recipe_items(self, selection=None) -> list[dict]:
        sel = selection if selection is not None else self.table.selection
        if sel is None:
            return []

        known_bundle_ids = {r["bundle_id"] for r in self._filtered_recipes}
        selected_ids: set[str] = set()

        single_id = self._extract_bundle_id(sel, known_bundle_ids)
        if single_id:
            selected_ids.add(single_id)
        elif isinstance(sel, (list, tuple, set)):
            for item in sel:
                bid = self._extract_bundle_id(item, known_bundle_ids)
                if bid:
                    selected_ids.add(bid)

        return [r for r in self._filtered_recipes if r["bundle_id"] in selected_ids]

    def get_selected_recipe_item(self, row=None) -> Optional[dict]:
        if row is not None:
            items = self.get_selected_recipe_items(row)
            return items[0] if len(items) == 1 else None
        items = self.get_selected_recipe_items()
        return items[0] if len(items) == 1 else None
```
4. Update `on_table_select`:
```python
    def on_table_select(self, widget: toga.Table):
        selected_items = self.get_selected_recipe_items()
        count = len(selected_items)
        custom_items = [r for r in selected_items if not r.get("is_builtin", False)]
        custom_count = len(custom_items)

        if count == 0:
            self.btn_edit.enabled = False
            self.btn_delete.enabled = False
            self.btn_delete.text = t("btn_delete")
        elif count == 1:
            self.btn_edit.enabled = True
            self.btn_delete.enabled = (custom_count == 1)
            self.btn_delete.text = t("btn_delete")
        else:  # count >= 2
            self.btn_edit.enabled = False
            if custom_count > 0:
                self.btn_delete.enabled = True
                self.btn_delete.text = t("btn_batch_delete", count=custom_count)
            else:
                self.btn_delete.enabled = False
                self.btn_delete.text = t("btn_delete")
```
5. Update `_render_current_view` Table mode to restore multi-selection with `NSMutableIndexSet`:
```python
            prev_sel_items = self.get_selected_recipe_items()
            prev_sel_bundle_ids = {r["bundle_id"] for r in prev_sel_items}

            table_data = []
            for r in self._filtered_recipes:
                origin = t("view_recipes_origin_builtin") if r["is_builtin"] else t("view_recipes_origin_custom")
                table_data.append((
                    r["app_name"],
                    r["bundle_id"],
                    r["strategy"],
                    origin,
                ))
            self.table.data = table_data
            self.content_container.add(self.table_box)

            if prev_sel_bundle_ids:
                try:
                    from rubicon.objc import ObjCClass
                    NSMutableIndexSet = ObjCClass("NSMutableIndexSet")
                    index_set = NSMutableIndexSet.alloc().init()
                    for idx, r in enumerate(self._filtered_recipes):
                        if r["bundle_id"] in prev_sel_bundle_ids:
                            index_set.addIndex_(idx)
                    native = getattr(getattr(self.table, "_impl", None), "native_table", None)
                    if native is not None and index_set.count > 0:
                        native.selectRowIndexes_byExtendingSelection_(index_set, False)
                except Exception:
                    pass

            self.on_table_select(self.table)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/gui/test_recipe_ui.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/atbclone/gui/views/recipe_list.py tests/gui/test_recipe_ui.py
git commit -m "feat(gui): support multi-selection and dynamic button states in recipe list view"
```

---

### Task 3: Implement Scenario-Based Confirmation Dialogs & Batch Deletion Orchestration in RecipeListView

**Files:**
- Modify: `src/atbclone/gui/views/recipe_list.py`
- Test: `tests/gui/test_recipe_ui.py`

**Interfaces:**
- Consumes: `RecipeService.delete_custom_recipe`, `toga.App.main_window.confirm_dialog`, `toga.App.main_window.error_dialog`
- Produces:
  - `on_delete_recipe(self, widget: toga.Button)`

- [ ] **Step 1: Write failing test for recipe deletion workflows**

Add test in `tests/gui/test_recipe_ui.py`:
```python
@pytest.mark.asyncio
async def test_recipe_list_view_delete_workflows():
    service_mock = MagicMock()
    service_mock.delete_custom_recipe = AsyncMock(return_value=True)
    service_mock.list_all_recipes = AsyncMock(return_value=[])

    app_mock = MagicMock()
    main_window_mock = MagicMock()
    main_window_mock.confirm_dialog = AsyncMock(return_value=True)
    main_window_mock.error_dialog = AsyncMock()
    app_mock.main_window = main_window_mock

    view = RecipeListView(recipe_service=service_mock, app=app_mock)
    custom1 = {"app_name": "Custom1", "bundle_id": "com.c1", "strategy": "hard_clone", "is_builtin": False, "recipe": MagicMock()}
    custom2 = {"app_name": "Custom2", "bundle_id": "com.c2", "strategy": "soft_clone", "is_builtin": False, "recipe": MagicMock()}
    builtin1 = {"app_name": "Builtin1", "bundle_id": "com.b1", "strategy": "hard_clone", "is_builtin": True, "recipe": MagicMock()}
    view._filtered_recipes = [custom1, custom2, builtin1]

    # Test Case 1: Single custom delete confirmed
    with patch.object(view, "get_selected_recipe_items", return_value=[custom1]):
        await view.on_delete_recipe(view.btn_delete)
        service_mock.delete_custom_recipe.assert_called_once_with("com.c1")
        assert main_window_mock.confirm_dialog.call_count == 1
    service_mock.delete_custom_recipe.reset_mock()
    main_window_mock.confirm_dialog.reset_mock()

    # Test Case 2: Pure batch delete (2 custom recipes)
    with patch.object(view, "get_selected_recipe_items", return_value=[custom1, custom2]):
        await view.on_delete_recipe(view.btn_delete)
        assert service_mock.delete_custom_recipe.call_count == 2
        service_mock.delete_custom_recipe.assert_any_call("com.c1")
        service_mock.delete_custom_recipe.assert_any_call("com.c2")
    service_mock.delete_custom_recipe.reset_mock()
    main_window_mock.confirm_dialog.reset_mock()

    # Test Case 3: Mixed batch delete (1 custom + 1 built-in) -> only deletes custom
    with patch.object(view, "get_selected_recipe_items", return_value=[custom1, builtin1]):
        await view.on_delete_recipe(view.btn_delete)
        service_mock.delete_custom_recipe.assert_called_once_with("com.c1")
        # Check confirmation message contains custom and builtin notices
        call_args = main_window_mock.confirm_dialog.call_args[0]
        assert "com.c1" in call_args[1] or "Custom1" in call_args[1]
    service_mock.delete_custom_recipe.reset_mock()
    main_window_mock.confirm_dialog.reset_mock()

    # Test Case 4: Pure built-in selection -> no-op
    with patch.object(view, "get_selected_recipe_items", return_value=[builtin1]):
        await view.on_delete_recipe(view.btn_delete)
        service_mock.delete_custom_recipe.assert_not_called()
        main_window_mock.confirm_dialog.assert_not_called()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/gui/test_recipe_ui.py::test_recipe_list_view_delete_workflows -v`
Expected: FAIL

- [ ] **Step 3: Implement `on_delete_recipe` in `RecipeListView`**

In `src/atbclone/gui/views/recipe_list.py`:
```python
    async def on_delete_recipe(self, widget: toga.Button):
        selected_items = self.get_selected_recipe_items()
        custom_items = [r for r in selected_items if not r.get("is_builtin", False)]
        builtin_items = [r for r in selected_items if r.get("is_builtin", False)]

        if not custom_items:
            return

        total_custom = len(custom_items)
        total_builtin = len(builtin_items)

        if self.app_instance and hasattr(self.app_instance, "main_window"):
            if total_custom == 1 and total_builtin == 0:
                item = custom_items[0]
                confirmed = await self.app_instance.main_window.confirm_dialog(
                    t("dialog_recipe_delete_confirm_title"),
                    t("dialog_recipe_delete_confirm_msg", name=item["app_name"]),
                )
                if not confirmed:
                    return
            elif total_builtin == 0:
                names_summary = ", ".join(r["app_name"] for r in custom_items[:6])
                if total_custom > 6:
                    names_summary += f" ... (+{total_custom - 6})"
                confirmed = await self.app_instance.main_window.confirm_dialog(
                    t("dialog_recipe_batch_delete_confirm_title"),
                    t("dialog_recipe_batch_delete_confirm_msg", count=total_custom, names=names_summary),
                )
                if not confirmed:
                    return
            else:  # Mixed selection: total_custom >= 1 and total_builtin >= 1
                names_summary = ", ".join(r["app_name"] for r in custom_items[:6])
                if total_custom > 6:
                    names_summary += f" ... (+{total_custom - 6})"
                confirmed = await self.app_instance.main_window.confirm_dialog(
                    t("dialog_recipe_batch_delete_confirm_mixed_title"),
                    t(
                        "dialog_recipe_batch_delete_confirm_mixed_msg",
                        custom_count=total_custom,
                        builtin_count=total_builtin,
                        names=names_summary,
                    ),
                )
                if not confirmed:
                    return

        failed_list: list[tuple[str, str]] = []
        self.btn_delete.enabled = False

        try:
            for idx, r in enumerate(custom_items, 1):
                if total_custom > 1:
                    self.btn_delete.text = t("btn_deleting_progress", current=idx, total=total_custom)
                else:
                    self.btn_delete.text = t("btn_delete")
                try:
                    await self.recipe_service.delete_custom_recipe(r["bundle_id"])
                except Exception as e:
                    failed_list.append((r["app_name"], str(e)))
            await self.refresh_recipes()
        finally:
            self.btn_delete.text = t("btn_delete")
            self.on_table_select(self.table)

        if failed_list and self.app_instance and hasattr(self.app_instance, "main_window"):
            succ_count = total_custom - len(failed_list)
            err_details = "\n".join(f"- {name}: {err}" for name, err in failed_list)
            if total_custom > 1:
                await self.app_instance.main_window.error_dialog(
                    t("dialog_batch_summary_title"),
                    t("dialog_batch_summary_msg", success=succ_count, failed=len(failed_list), errors=err_details),
                )
            else:
                await self.app_instance.main_window.error_dialog(
                    t("dialog_error_title"),
                    failed_list[0][1],
                )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/gui/test_recipe_ui.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/atbclone/gui/views/recipe_list.py tests/gui/test_recipe_ui.py
git commit -m "feat(gui): implement scenario-based confirmation dialogs and batch recipe deletion"
```

---

### Task 4: Full Test Suite Regression Verification

**Files:**
- Test: `tests/`

- [ ] **Step 1: Run full pytest suite across entire project**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/`
Expected: ALL test suites PASS (366+ tests)

- [ ] **Step 2: Commit any final test adjustments if needed**

```bash
git status
```
