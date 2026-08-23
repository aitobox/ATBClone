# Batch Clone Operations Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enable multi-selection in "My Clones" (`CloneListView`) Table View and provide responsive batch "Update" and "Delete" operations with confirmation and progress feedback.

**Architecture:** Configure `toga.Table` with `multiple_select=True`, implement robust selection parsing in `get_selected_records()`, adapt bottom action buttons dynamically for 0, 1, or N selected items, and provide sequential batch execution loops for updates and deletions with busy locks, dual confirmation dialogs for deletion, and error summary dialogs.

**Tech Stack:** Python 3.12, Toga (toga-cocoa), pytest, pytest-asyncio, ATBClone Core & GUI Services.

## Global Constraints

- Native macOS pattern compliant, PySide6/Toga compatible.
- Zero external third-party dependencies outside the project's standard stack.
- Multi-language support across all 9 languages in `src/atbclone/core/i18n.py`.
- Safe busy-lock protection on `_busy_clones`.

---

### Task 1: Add Multi-language Keys for Batch Operations

**Files:**
- Modify: `src/atbclone/core/i18n.py`
- Test: `tests/test_i18n.py`

**Interfaces:**
- Produces:
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

- [ ] **Step 1: Write failing test for new i18n keys**

Add test in `tests/test_i18n.py`:
```python
def test_batch_operation_i18n_keys():
    from atbclone.core.i18n import t, set_language
    for lang in ("zh", "en", "ja"):
        set_language(lang)
        msg_up = t("btn_batch_update", count=3)
        assert "3" in msg_up
        msg_del = t("btn_batch_delete", count=2)
        assert "2" in msg_del
        msg_up_prog = t("btn_updating_progress", current=1, total=3)
        assert "1/3" in msg_up_prog
        msg_del_prog = t("btn_deleting_progress", current=2, total=4)
        assert "2/4" in msg_del_prog
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_i18n.py::test_batch_operation_i18n_keys -v`
Expected: FAIL with key missing / KeyError

- [ ] **Step 3: Add dictionary entries in `src/atbclone/core/i18n.py`**

Add entries for all 9 supported languages:
```python
    "btn_batch_update": {
        "en": "Update Selected ({count})",
        "zh": "批量更新 ({count})",
        "zh_TW": "批次更新 ({count})",
        "ja": "一括更新 ({count})",
        "ko": "일괄 업데이트 ({count})",
        "de": "Ausgewählte aktualisieren ({count})",
        "fr": "Mettre à jour la sélection ({count})",
        "ru": "Обновить выбранные ({count})",
        "es": "Actualizar seleccionados ({count})",
    },
    "btn_batch_delete": {
        "en": "Delete Selected ({count})",
        "zh": "批量删除 ({count})",
        "zh_TW": "批次刪除 ({count})",
        "ja": "一括削除 ({count})",
        "ko": "일괄 삭제 ({count})",
        "de": "Ausgewählte löschen ({count})",
        "fr": "Supprimer la sélection ({count})",
        "ru": "Удалить выбранные ({count})",
        "es": "Eliminar seleccionados ({count})",
    },
    "btn_updating_progress": {
        "en": "Updating ({current}/{total})...",
        "zh": "正在更新 ({current}/{total})...",
        "zh_TW": "正在更新 ({current}/{total})...",
        "ja": "更新中 ({current}/{total})...",
        "ko": "업데이트 중 ({current}/{total})...",
        "de": "Wird aktualisiert ({current}/{total})...",
        "fr": "Mise à jour ({current}/{total})...",
        "ru": "Обновление ({current}/{total})...",
        "es": "Actualizando ({current}/{total})...",
    },
    "btn_deleting_progress": {
        "en": "Deleting ({current}/{total})...",
        "zh": "正在删除 ({current}/{total})...",
        "zh_TW": "正在刪除 ({current}/{total})...",
        "ja": "削除中 ({current}/{total})...",
        "ko": "삭제 중 ({current}/{total})...",
        "de": "Wird gelöscht ({current}/{total})...",
        "fr": "Suppression ({current}/{total})...",
        "ru": "Удаление ({current}/{total})...",
        "es": "Eliminando ({current}/{total})...",
    },
    "dialog_batch_delete_confirm_title": {
        "en": "Confirm Batch Deletion",
        "zh": "确认批量删除",
        "zh_TW": "確認批次刪除",
        "ja": "一括削除の確認",
        "ko": "일괄 삭제 확인",
        "de": "Massenlöschung bestätigen",
        "fr": "Confirmer la suppression groupée",
        "ru": "Подтверждение массового удаления",
        "es": "Confirmar eliminación por lotes",
    },
    "dialog_batch_delete_confirm_msg": {
        "en": "Are you sure you want to delete {count} selected clones?\n{names}",
        "zh": "确定要删除选中的 {count} 个分身应用吗？\n{names}",
        "zh_TW": "確定要刪除選取的 {count} 個分身應用程式嗎？\n{names}",
        "ja": "選択した {count} 件のクローンを削除してもよろしいですか？\n{names}",
        "ko": "선택한 {count}개의 클론을 삭제하시겠습니까?\n{names}",
        "de": "Möchten Sie die {count} ausgewählten Klone wirklich löschen?\n{names}",
        "fr": "Voulez-vous vraiment supprimer les {count} clones sélectionnés ?\n{names}",
        "ru": "Вы уверены, что хотите удалить выбранные клоны ({count})?\n{names}",
        "es": "¿Seguro que desea eliminar los {count} clones seleccionados?\n{names}",
    },
    "dialog_batch_delete_data_confirm_title": {
        "en": "Clean Data Directories",
        "zh": "清理用户数据目录",
        "zh_TW": "清理使用者資料目錄",
        "ja": "データディレクトリの削除",
        "ko": "데이터 디렉토리 정리",
        "de": "Datenverzeichnisse bereinigen",
        "fr": "Nettoyer les répertoires de données",
        "ru": "Очистить каталоги данных",
        "es": "Limpiar directorios de datos",
    },
    "dialog_batch_delete_data_confirm_msg": {
        "en": "Do you also want to delete the user data and config directories for these {count} clones?\nSelecting 'Cancel' will keep data directories and only remove the clone applications.",
        "zh": "是否同时清理这 {count} 个分身的用户数据与配置目录？\n选择“取消”将保留数据目录，仅删除分身应用本体。",
        "zh_TW": "是否同時清理這 {count} 個分身的使用者資料與設定目錄？\n選擇「取消」將保留資料目錄，僅刪除分身應用程式本體。",
        "ja": "これら {count} 件のクローンのユーザーデータと設定ディレクトリも削除しますか？\n「キャンセル」を選択すると、データは保持され、アプリ本体のみが削除されます。",
        "ko": "이 {count}개 클론의 사용자 데이터 및 설정 디렉토리도 함께 삭제하시겠습니까?\n'취소'를 선택하면 데이터는 유지되고 클론 앱만 삭제됩니다.",
        "de": "Möchten Sie auch die Benutzerdaten- und Konfigurationsverzeichnisse dieser {count} Klone löschen?\nWenn Sie 'Abbrechen' wählen, bleiben die Daten erhalten.",
        "fr": "Voulez-vous également supprimer les données utilisateur de ces {count} clones ?\nChoisir 'Annuler' conservera les données.",
        "ru": "Удалить также каталоги пользовательских данных и конфигураций для этих {count} клонов?\nПри отмене данные сохранятся.",
        "es": "¿Desea eliminar también los directorios de datos y configuración de estos {count} clones?\nAl cancelar, se conservarán los datos.",
    },
    "dialog_batch_summary_title": {
        "en": "Batch Operation Results",
        "zh": "批量操作结果",
        "zh_TW": "批次操作結果",
        "ja": "一括操作の結果",
        "ko": "일괄 작업 결과",
        "de": "Ergebnisse der Massenoperation",
        "fr": "Résultats de l'opération groupée",
        "ru": "Результаты массовой операции",
        "es": "Resultados de la operación por lotes",
    },
    "dialog_batch_summary_msg": {
        "en": "Operation completed: {success} succeeded, {failed} failed.\n\nFailure details:\n{errors}",
        "zh": "操作完成：{success} 个成功，{failed} 个失败。\n\n失败详情：\n{errors}",
        "zh_TW": "操作完成：{success} 個成功，{failed} 個失敗。\n\n失敗詳情：\n{errors}",
        "ja": "処理完了: 成功 {success} 件、失敗 {failed} 件。\n\n失敗の詳細:\n{errors}",
        "ko": "작업 완료: 성공 {success}개, 실패 {failed}개.\n\n실패 세부 정보:\n{errors}",
        "de": "Vorgang abgeschlossen: {success} erfolgreich, {failed} fehlgeschlagen.\n\nFehlerdetails:\n{errors}",
        "fr": "Opération terminée : {success} réussis, {failed} échoués.\n\nDétails des erreurs :\n{errors}",
        "ru": "Операция завершена: успешно — {success}, с ошибкой — {failed}.\n\nПодробности ошибок:\n{errors}",
        "es": "Operación completada: {success} correctos, {failed} fallidos.\n\nDetalles de fallos:\n{errors}",
    },
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_i18n.py::test_batch_operation_i18n_keys -v`
Expected: PASS

---

### Task 2: Multi-Selection Parsing and Dynamic Button States in CloneListView

**Files:**
- Modify: `src/atbclone/gui/views/clone_list.py`
- Test: `tests/gui/test_clone_views.py`

**Interfaces:**
- Consumes: `toga.Table`, `CloneRecord`, `i18n.t`
- Produces:
  - `CloneListView.get_selected_records() -> list[CloneRecord]`
  - `CloneListView.get_selected_record() -> Optional[CloneRecord]` (returns record if len == 1, else None)
  - `CloneListView.on_table_select(widget)`: updates button texts and enabled states for 0, 1, or N items.

- [ ] **Step 1: Write failing unit test for selection parsing & button state transitions**

Add test in `tests/gui/test_clone_views.py`:
```python
def test_clone_list_view_multi_selection():
    view = CloneListView()
    r1 = CloneRecord(clone_name="App1", source_app="A1", source_path="/p1", bundle_id="b1", strategy="hard_clone", dest_path="/d1", data_dir="/data1", created_at="2026-08-20T10:00:00")
    r2 = CloneRecord(clone_name="App2", source_app="A2", source_path="/p2", bundle_id="b2", strategy="soft_clone", dest_path="/d2", data_dir="/data2", created_at="2026-08-20T11:00:00")
    view._filtered_clones = [r1, r2]

    # Case 1: 0 items selected
    with patch.object(view, "get_selected_records", return_value=[]):
        view.on_table_select(view.table)
        assert view.btn_launch_table.enabled is False
        assert view.btn_update_table.enabled is False
        assert view.btn_delete_table.enabled is False

    # Case 2: 1 item selected
    with patch.object(view, "get_selected_records", return_value=[r1]):
        view.on_table_select(view.table)
        assert view.btn_launch_table.enabled is True
        assert view.btn_update_table.enabled is True
        assert view.btn_delete_table.enabled is True
        assert "(" not in view.btn_update_table.text

    # Case 3: 2 items selected (Multi-select)
    with patch.object(view, "get_selected_records", return_value=[r1, r2]):
        view.on_table_select(view.table)
        assert view.btn_launch_table.enabled is False
        assert view.btn_open_dir_table.enabled is False
        assert view.btn_edit_table.enabled is False
        assert view.btn_detail_table.enabled is False
        assert view.btn_update_table.enabled is True
        assert view.btn_delete_table.enabled is True
        assert "2" in view.btn_update_table.text
        assert "2" in view.btn_delete_table.text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/gui/test_clone_views.py::test_clone_list_view_multi_selection -v`
Expected: FAIL (missing `get_selected_records` or button text assertion fails)

- [ ] **Step 3: Update `src/atbclone/gui/views/clone_list.py`**

1. Set `multiple_select=True` in `self.table = toga.Table(..., multiple_select=True)`.
2. Implement `get_selected_records(self, selection=None) -> list[CloneRecord]`:
```python
    def get_selected_records(self, selection=None) -> list[CloneRecord]:
        sel = selection if selection is not None else self.table.selection
        if sel is None:
            return []
        
        # Normalize selection to a collection of row items
        items = sel if isinstance(sel, (list, tuple, set)) else [sel]
        if not items:
            return []

        selected_names = set()
        known_names = {r.clone_name for r in self._filtered_clones}

        for item in items:
            clone_name = getattr(item, "Name", None) or getattr(item, "clone_name", None) or getattr(item, t("list_col_name"), None)
            if not clone_name and hasattr(item, "_raw"):
                clone_name = item._raw[0]
            if not clone_name and isinstance(item, (tuple, list)) and len(item) > 0:
                clone_name = item[0]
            if not clone_name and hasattr(item, "__dict__"):
                for k, v in item.__dict__.items():
                    if not k.startswith("_") and isinstance(v, str) and v in known_names:
                        clone_name = v
                        break
            if clone_name and clone_name in known_names:
                selected_names.add(clone_name)

        return [r for r in self._filtered_clones if r.clone_name in selected_names]

    def get_selected_record(self, row=None) -> Optional[CloneRecord]:
        records = self.get_selected_records(row)
        return records[0] if len(records) == 1 else None
```
3. Update `on_table_select(self, widget: toga.Table)`:
```python
    def on_table_select(self, widget: toga.Table):
        records = self.get_selected_records()
        count = len(records)
        has_busy = any(r.clone_name in self._busy_clones for r in records)

        if count == 0:
            self.btn_launch_table.enabled = False
            self.btn_open_dir_table.enabled = False
            self.btn_update_table.enabled = False
            self.btn_update_table.text = t("btn_update")
            self.btn_edit_table.enabled = False
            self.btn_detail_table.enabled = False
            self.btn_delete_table.enabled = False
            self.btn_delete_table.text = t("btn_delete")
        elif count == 1:
            self.btn_launch_table.enabled = not has_busy
            self.btn_open_dir_table.enabled = True
            self.btn_update_table.enabled = not has_busy
            self.btn_update_table.text = t("btn_update")
            self.btn_edit_table.enabled = not has_busy
            self.btn_detail_table.enabled = True
            self.btn_delete_table.enabled = not has_busy
            self.btn_delete_table.text = t("btn_delete")
        else:  # count >= 2
            self.btn_launch_table.enabled = False
            self.btn_open_dir_table.enabled = False
            self.btn_update_table.enabled = not has_busy
            self.btn_update_table.text = t("btn_batch_update", count=count)
            self.btn_edit_table.enabled = False
            self.btn_detail_table.enabled = False
            self.btn_delete_table.enabled = not has_busy
            self.btn_delete_table.text = t("btn_batch_delete", count=count)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/gui/test_clone_views.py::test_clone_list_view_multi_selection -v`
Expected: PASS

---

### Task 3: Implement Batch Update and Batch Delete Orchestration with Confirmation & Summary

**Files:**
- Modify: `src/atbclone/gui/views/clone_list.py`
- Test: `tests/gui/test_clone_views.py`

**Interfaces:**
- Consumes: `CloneService.update_clone`, `CloneService.remove_clone`, `CloneListView.get_selected_records`
- Produces:
  - `CloneListView.on_update_clone(records)` (accepts single record, list of records, or None)
  - `CloneListView.on_delete_clone(records)` (accepts single record, list of records, or None)

- [ ] **Step 1: Write failing unit test for batch update and batch delete flows**

Add tests in `tests/gui/test_clone_views.py`:
```python
def test_clone_list_view_batch_update_flow(tmp_path):
    async def _test():
        state_file = tmp_path / "clones.yaml"
        service = CloneService(state_file=state_file)
        r1 = CloneRecord(clone_name="A1", source_app="App1", source_path="/p1", bundle_id="b1", strategy="hard_clone", dest_path="/d1", data_dir="/data1", created_at="2026-08-20T10:00:00")
        r2 = CloneRecord(clone_name="A2", source_app="App2", source_path="/p2", bundle_id="b2", strategy="soft_clone", dest_path="/d2", data_dir="/data2", created_at="2026-08-20T11:00:00")
        service.state_manager.add(r1)
        service.state_manager.add(r2)

        view = CloneListView(clone_service=service)
        await view.refresh_clones()

        with patch.object(service, "update_clone", new_callable=AsyncMock) as mock_up:
            await view.on_update_clone([r1, r2])
            assert mock_up.await_count == 2
            mock_up.assert_any_await("A1")
            mock_up.assert_any_await("A2")

    asyncio.run(_test())


def test_clone_list_view_batch_delete_flow(tmp_path):
    async def _test():
        state_file = tmp_path / "clones.yaml"
        service = CloneService(state_file=state_file)
        r1 = CloneRecord(clone_name="A1", source_app="App1", source_path="/p1", bundle_id="b1", strategy="hard_clone", dest_path="/d1", data_dir="/data1", created_at="2026-08-20T10:00:00")
        r2 = CloneRecord(clone_name="A2", source_app="App2", source_path="/p2", bundle_id="b2", strategy="soft_clone", dest_path="/d2", data_dir="/data2", created_at="2026-08-20T11:00:00")
        service.state_manager.add(r1)
        service.state_manager.add(r2)

        view = CloneListView(clone_service=service)
        mock_app = MagicMock()
        mock_win = MagicMock()
        mock_win.confirm_dialog = AsyncMock(side_effect=[True, True])
        mock_app.main_window = mock_win
        view.app_instance = mock_app
        await view.refresh_clones()

        with patch.object(service, "remove_clone", new_callable=AsyncMock) as mock_rm:
            await view.on_delete_clone([r1, r2])
            assert mock_rm.await_count == 2
            mock_rm.assert_any_await("A1", with_data=True)
            mock_rm.assert_any_await("A2", with_data=True)

    asyncio.run(_test())
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/gui/test_clone_views.py::test_clone_list_view_batch_update_flow tests/gui/test_clone_views.py::test_clone_list_view_batch_delete_flow -v`
Expected: FAIL

- [ ] **Step 3: Implement batch update & delete logic in `CloneListView`**

Update `btn_update_table` and `btn_delete_table` callbacks:
```python
        self.btn_update_table = toga.Button(
            t("btn_update"),
            on_press=lambda w: asyncio.create_task(self.on_update_clone(self.get_selected_records())),
            enabled=False,
            style=Pack(margin_right=6, height=28, font_size=12.5),
        )
        self.btn_delete_table = toga.Button(
            t("btn_delete"),
            on_press=lambda w: asyncio.create_task(self.on_delete_clone(self.get_selected_records())),
            enabled=False,
            style=Pack(height=28, font_size=12.5),
        )
```

Implement `on_update_clone`:
```python
    async def on_update_clone(self, target: Optional[CloneRecord | list[CloneRecord]] = None):
        if target is None:
            records = self.get_selected_records()
        elif isinstance(target, CloneRecord):
            records = [target]
        else:
            records = list(target)

        if not records:
            return

        active_records = [r for r in records if r.clone_name not in self._busy_clones]
        if not active_records:
            return

        for r in active_records:
            self._busy_clones.add(r.clone_name)

        total = len(active_records)
        failed_list: list[tuple[str, str]] = []

        if hasattr(self, "btn_update_table") and self.btn_update_table:
            self.btn_update_table.enabled = False

        try:
            for idx, r in enumerate(active_records, 1):
                if hasattr(self, "btn_update_table") and self.btn_update_table:
                    if total > 1:
                        self.btn_update_table.text = t("btn_updating_progress", current=idx, total=total)
                    else:
                        self.btn_update_table.text = t("btn_updating")
                try:
                    await self.clone_service.update_clone(r.clone_name)
                except Exception as e:
                    logger.error(f"Failed to update clone '{r.clone_name}': {e}")
                    failed_list.append((r.clone_name, str(e)))
            await self.refresh_clones()
        finally:
            for r in active_records:
                self._busy_clones.discard(r.clone_name)
            if hasattr(self, "btn_update_table") and self.btn_update_table:
                self.btn_update_table.text = t("btn_update")
            self.on_table_select(self.table)

        if failed_list and self.app_instance and hasattr(self.app_instance, "main_window"):
            succ_count = total - len(failed_list)
            err_details = "\n".join(f"- {name}: {err}" for name, err in failed_list)
            if total > 1:
                await self.app_instance.main_window.error_dialog(
                    t("dialog_batch_summary_title"),
                    t("dialog_batch_summary_msg", success=succ_count, failed=len(failed_list), errors=err_details),
                )
            else:
                await self.app_instance.main_window.error_dialog(
                    t("dialog_update_error_title"),
                    failed_list[0][1],
                )
```

Implement `on_delete_clone`:
```python
    async def on_delete_clone(self, target: Optional[CloneRecord | list[CloneRecord]] = None):
        if target is None:
            records = self.get_selected_records()
        elif isinstance(target, CloneRecord):
            records = [target]
        else:
            records = list(target)

        if not records:
            return

        active_records = [r for r in records if r.clone_name not in self._busy_clones]
        if not active_records:
            return

        total = len(active_records)
        delete_data = False

        if self.app_instance and hasattr(self.app_instance, "main_window"):
            if total == 1:
                record = active_records[0]
                confirmed = await self.app_instance.main_window.confirm_dialog(
                    t("dialog_delete_confirm_title"),
                    t("dialog_delete_confirm_msg", name=record.clone_name),
                )
                if not confirmed:
                    return

                delete_data = await self.app_instance.main_window.confirm_dialog(
                    t("dialog_delete_data_confirm_title"),
                    t("dialog_delete_data_confirm_msg", path=record.data_dir),
                )
            else:
                names_summary = ", ".join(r.clone_name for r in active_records[:6])
                if total > 6:
                    names_summary += f" ... (+{total - 6})"
                confirmed = await self.app_instance.main_window.confirm_dialog(
                    t("dialog_batch_delete_confirm_title"),
                    t("dialog_batch_delete_confirm_msg", count=total, names=names_summary),
                )
                if not confirmed:
                    return

                delete_data = await self.app_instance.main_window.confirm_dialog(
                    t("dialog_batch_delete_data_confirm_title"),
                    t("dialog_batch_delete_data_confirm_msg", count=total),
                )

        for r in active_records:
            self._busy_clones.add(r.clone_name)

        failed_list: list[tuple[str, str]] = []
        if hasattr(self, "btn_delete_table") and self.btn_delete_table:
            self.btn_delete_table.enabled = False

        try:
            for idx, r in enumerate(active_records, 1):
                if hasattr(self, "btn_delete_table") and self.btn_delete_table:
                    if total > 1:
                        self.btn_delete_table.text = t("btn_deleting_progress", current=idx, total=total)
                    else:
                        self.btn_delete_table.text = t("btn_delete")
                try:
                    await self.clone_service.remove_clone(r.clone_name, with_data=delete_data)
                except Exception as e:
                    logger.error(f"Failed to delete clone '{r.clone_name}': {e}")
                    failed_list.append((r.clone_name, str(e)))
            await self.refresh_clones()
        finally:
            for r in active_records:
                self._busy_clones.discard(r.clone_name)
            if hasattr(self, "btn_delete_table") and self.btn_delete_table:
                self.btn_delete_table.text = t("btn_delete")
            self.on_table_select(self.table)

        if failed_list and self.app_instance and hasattr(self.app_instance, "main_window"):
            succ_count = total - len(failed_list)
            err_details = "\n".join(f"- {name}: {err}" for name, err in failed_list)
            if total > 1:
                await self.app_instance.main_window.error_dialog(
                    t("dialog_batch_summary_title"),
                    t("dialog_batch_summary_msg", success=succ_count, failed=len(failed_list), errors=err_details),
                )
            else:
                await self.app_instance.main_window.error_dialog(
                    t("dialog_delete_error_title", default="Delete Error"),
                    failed_list[0][1],
                )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/gui/test_clone_views.py::test_clone_list_view_batch_update_flow tests/gui/test_clone_views.py::test_clone_list_view_batch_delete_flow -v`
Expected: PASS

---

### Task 4: Full Test Suite Verification

**Files:**
- Test: `tests/gui/test_clone_views.py`, `tests/test_i18n.py`, full `tests/`

- [ ] **Step 1: Run all GUI and Core test suites**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/`
Expected: All tests PASS with 0 failures

- [ ] **Step 2: Commit all changes**

```bash
git add src/atbclone/core/i18n.py src/atbclone/gui/views/clone_list.py tests/test_i18n.py tests/gui/test_clone_views.py
git commit -m "feat(gui): support batch update and delete in clone list view"
```
