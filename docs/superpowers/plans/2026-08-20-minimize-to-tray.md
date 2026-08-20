# Minimize to System Tray Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement macOS system tray (`NSStatusItem`) support in ATBClone, allowing users to enable "Minimize to Tray" in Global Settings with left-click window focus, right-click context menu (Show/Quit), and window minimize button interception.

**Architecture:** A decoupled `TrayService` manages the Cocoa `NSStatusItem` lifecycle and events (left vs right click). `SettingsView` provides a toggle switch for `minimize_to_tray` backed by `config.json`. `ATBCloneApp` hooks window minimization notifications to hide the main window when tray mode is active.

**Tech Stack:** Python 3.12, BeeWare Toga, Cocoa AppKit (`toga_cocoa.libs.appkit`, `rubicon.objc`), pytest.

## Global Constraints

- Target macOS native patterns, PySide6/Toga, Python 3.12+ with `conda run -n ATBClone` for dev environment.
- Test command: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/`.
- Zero external third-party dependencies (use built-in `toga_cocoa` / `rubicon.objc`).
- Graceful degradation on non-macOS / headless / CI environments.

---

### Task 1: i18n Localized Strings for Tray & Window Preferences

**Files:**
- Modify: `src/atbclone/core/i18n.py`
- Test: `tests/test_i18n.py`

**Interfaces:**
- Produces:
  - `settings_card_tray`
  - `settings_switch_minimize_to_tray`
  - `settings_hint_minimize_to_tray`
  - `tray_menu_show`
  - `tray_menu_quit`

- [ ] **Step 1: Write the failing test for new i18n keys**

Add test to `tests/test_i18n.py`:
```python
def test_tray_i18n_keys():
    from atbclone.core.i18n import t, set_language, SUPPORTED_LANGUAGES

    keys = [
        "settings_card_tray",
        "settings_switch_minimize_to_tray",
        "settings_hint_minimize_to_tray",
        "tray_menu_show",
        "tray_menu_quit",
    ]
    for lang in SUPPORTED_LANGUAGES:
        set_language(lang)
        for k in keys:
            val = t(k)
            assert val != k, f"Missing translation for key '{k}' in language '{lang}'"
            assert len(val) > 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_i18n.py::test_tray_i18n_keys -v`
Expected: FAIL with missing translations.

- [ ] **Step 3: Add translations across all 9 languages in `src/atbclone/core/i18n.py`**

```python
    "settings_card_tray": {
        "en": "🪟 Window & Tray Preferences",
        "zh": "🪟 窗口与系统托盘偏好",
        "zh_TW": "🪟 視窗與系統托盤偏好",
        "ja": "🪟 ウィンドウとトレイ設定",
        "ko": "🪟 창 및 시스템 트레이 환경설정",
        "de": "🪟 Fenster- & Taskleisteneinstellungen",
        "fr": "🪟 Préférences de fenêtre et barre d'état",
        "ru": "🪟 Настройки окна и системного трея",
        "es": "🪟 Preferencias de ventana y bandeja del sistema",
    },
    "settings_switch_minimize_to_tray": {
        "en": "Minimize to System Tray",
        "zh": "最小化到系统托盘",
        "zh_TW": "最小化到系統托盤",
        "ja": "システムトレイに最小化",
        "ko": "시스템 트레이로 최소화",
        "de": "In die Taskleiste minimieren",
        "fr": "Réduire dans la barre d'état",
        "ru": "Сворачивать в системный трей",
        "es": "Minimizar a la bandeja del sistema",
    },
    "settings_hint_minimize_to_tray": {
        "en": "Hide main window to menu bar when clicking minimize button (-)",
        "zh": "点击窗口最小化按钮（-）时隐藏到顶部菜单栏状态栏",
        "zh_TW": "點擊視窗最小化按鈕（-）時隱藏至頂部功能表列狀態列",
        "ja": "最小化ボタン（-）をクリックしたときに上部メニューバーに非表示",
        "ko": "최소화 버튼(-) 클릭 시 상단 메뉴 바로 숨김",
        "de": "Hauptfenster beim Klicken auf Minimieren (-) in die Menüleiste ausblenden",
        "fr": "Masquer la fenêtre principale dans la barre des menus lors du clic sur réduire (-)",
        "ru": "Скрывать главное окно в строку меню при нажатии кнопки свернуть (-)",
        "es": "Ocultar la ventana principal en la barra de menú al hacer clic en minimizar (-)",
    },
    "tray_menu_show": {
        "en": "Show ATBClone",
        "zh": "显示主界面",
        "zh_TW": "顯示主介面",
        "ja": "メイン画面を表示",
        "ko": "메인 화면 표시",
        "de": "Hauptfenster anzeigen",
        "fr": "Afficher l'interface principale",
        "ru": "Показать главное окно",
        "es": "Mostrar ventana principal",
    },
    "tray_menu_quit": {
        "en": "Quit ATBClone",
        "zh": "退出 ATBClone",
        "zh_TW": "結束 ATBClone",
        "ja": "ATBClone を終了",
        "ko": "ATBClone 종료",
        "de": "ATBClone beenden",
        "fr": "Quitter ATBClone",
        "ru": "Выйти из ATBClone",
        "es": "Salir de ATBClone",
    },
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_i18n.py::test_tray_i18n_keys -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/atbclone/core/i18n.py tests/test_i18n.py
git commit -m "feat(i18n): add localized strings for tray and window preferences"
```

---

### Task 2: Implement `TrayService`

**Files:**
- Create: `src/atbclone/gui/services/tray_service.py`
- Test: `tests/gui/test_tray_service.py`

**Interfaces:**
- Consumes: `atbclone.core.i18n.t`, `atbclone.core.resources.get_app_icon_path`
- Produces: `TrayService` with methods:
  - `is_enabled: bool`
  - `enable() -> bool`
  - `disable() -> None`
  - `on_tray_clicked(sender)`
  - `retranslate() -> None`

- [ ] **Step 1: Write the failing unit tests for `TrayService`**

Create `tests/gui/test_tray_service.py`:
```python
import sys
from unittest.mock import MagicMock, patch
import pytest

from atbclone.gui.services.tray_service import TrayService


class DummyApp:
    def __init__(self):
        self.shown = False
        self.exited = False

    def show_main_window(self):
        self.shown = True

    def exit_application(self):
        self.exited = True


def test_tray_service_init_disabled():
    app = DummyApp()
    service = TrayService(app=app)
    assert not service.is_enabled


def test_tray_service_enable_and_disable():
    app = DummyApp()
    service = TrayService(app=app)
    with patch("atbclone.gui.services.tray_service.NSStatusBar") as mock_sb:
        mock_item = MagicMock()
        mock_sb.systemStatusBar.return_value.statusItemWithLength_.return_value = mock_item
        with patch("atbclone.gui.services.tray_service.sys.platform", "darwin"):
            success = service.enable()
            assert success is True
            assert service.is_enabled is True

            service.disable()
            assert service.is_enabled is False
            mock_sb.systemStatusBar.return_value.removeStatusItem_.assert_called_once_with(mock_item)


def test_tray_service_fallback_on_non_macos():
    app = DummyApp()
    service = TrayService(app=app)
    with patch("atbclone.gui.services.tray_service.sys.platform", "linux"):
        success = service.enable()
        assert success is False
        assert service.is_enabled is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/gui/test_tray_service.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'atbclone.gui.services.tray_service'`

- [ ] **Step 3: Implement `TrayService` in `src/atbclone/gui/services/tray_service.py`**

```python
"""macOS Cocoa native menu bar status item (tray) service for ATBClone."""

import sys
from pathlib import Path
from typing import Any, Optional

from atbclone.core.i18n import t
from atbclone.core.logger import get_logger
from atbclone.core.resources import get_app_icon_path

logger = get_logger("gui.tray")

try:
    from toga_cocoa.libs.appkit import (
        NSApplication,
        NSStatusBar,
        NSMenu,
        NSMenuItem,
        NSImage,
    )
    from rubicon.objc import NSObject, objc_method, NSSize
except Exception:
    NSApplication = None
    NSStatusBar = None
    NSMenu = None
    NSMenuItem = None
    NSImage = None
    NSObject = object
    objc_method = lambda fn: fn
    NSSize = None


class TrayCallbackTarget(NSObject):
    """Objective-C target object to receive Cocoa NSStatusBarButton click events."""

    @objc_method
    def onTrayClicked_(self, sender: Any) -> None:
        if hasattr(self, "_tray_service") and self._tray_service:
            self._tray_service._handle_click(sender)

    @objc_method
    def onMenuShow_(self, sender: Any) -> None:
        if hasattr(self, "_tray_service") and self._tray_service:
            self._tray_service.on_menu_show()

    @objc_method
    def onMenuQuit_(self, sender: Any) -> None:
        if hasattr(self, "_tray_service") and self._tray_service:
            self._tray_service.on_menu_quit()


class TrayService:
    """Manages the lifecycle, appearance, and event dispatch of the macOS status tray icon."""

    def __init__(self, app: Any):
        self.app = app
        self._status_item: Any = None
        self._target: Any = None
        self._is_enabled: bool = False

    @property
    def is_enabled(self) -> bool:
        return self._is_enabled

    def enable(self) -> bool:
        if self._is_enabled or sys.platform != "darwin" or NSStatusBar is None:
            return False
        try:
            # -1 represents NSVariableStatusItemLength; -2 represents NSSquareStatusItemLength
            self._status_item = NSStatusBar.systemStatusBar.statusItemWithLength_(-2)
            button = self._status_item.button
            if button is not None:
                icon_path = get_app_icon_path("png")
                if icon_path and Path(icon_path).exists() and NSImage is not None:
                    img = NSImage.alloc().initWithContentsOfFile_(str(icon_path))
                    if img and NSSize:
                        img.setSize_(NSSize(18, 18))
                        button.setImage_(img)
                if hasattr(button, "setToolTip_"):
                    button.setToolTip_("ATBClone")

                self._target = TrayCallbackTarget.alloc().init()
                self._target._tray_service = self

                button.setTarget_(self._target)
                button.setAction_("onTrayClicked:")
                # NSEventMaskLeftMouseUp = 1 << 2, NSEventMaskRightMouseUp = 1 << 3
                if hasattr(button, "sendActionOn_"):
                    button.sendActionOn_((1 << 2) | (1 << 3))

            self._is_enabled = True
            logger.info("System tray icon enabled successfully.")
            return True
        except Exception as e:
            logger.warning(f"Failed to enable system tray icon: {e}")
            self._status_item = None
            self._is_enabled = False
            return False

    def disable(self) -> None:
        if not self._is_enabled or self._status_item is None or NSStatusBar is None:
            self._is_enabled = False
            return
        try:
            NSStatusBar.systemStatusBar.removeStatusItem_(self._status_item)
        except Exception as e:
            logger.warning(f"Error removing status item: {e}")
        self._status_item = None
        self._target = None
        self._is_enabled = False
        logger.info("System tray icon disabled.")

    def _handle_click(self, sender: Any) -> None:
        """Handle left vs right mouse button click events."""
        try:
            current_event = NSApplication.sharedApplication.currentEvent
            event_type = getattr(current_event, "type", None)
            # NSEventTypeRightMouseUp = 3, NSEventTypeRightMouseDown = 3, or check event type
            if event_type == 3 or (isinstance(event_type, int) and event_type in (3, 8)):
                self.show_context_menu()
            else:
                self.on_menu_show()
        except Exception as e:
            logger.debug(f"Error determining click event type: {e}")
            self.on_menu_show()

    def show_context_menu(self) -> None:
        """Build and popup the context NSMenu for right-click."""
        if not self._status_item or NSMenu is None or NSMenuItem is None:
            return
        try:
            menu = NSMenu.alloc().init()
            menu.setAutoenablesItems_(True)

            item_show = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                t("tray_menu_show"),
                "onMenuShow:",
                "",
            )
            item_show.setTarget_(self._target)
            menu.addItem_(item_show)

            sep = NSMenuItem.separatorItem()
            menu.addItem_(sep)

            item_quit = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                t("tray_menu_quit"),
                "onMenuQuit:",
                "",
            )
            item_quit.setTarget_(self._target)
            menu.addItem_(item_quit)

            if hasattr(self._status_item, "popUpStatusItemMenu_"):
                self._status_item.popUpStatusItemMenu_(menu)
        except Exception as e:
            logger.warning(f"Failed to popup context menu: {e}")

    def on_menu_show(self) -> None:
        if self.app and hasattr(self.app, "show_main_window"):
            self.app.show_main_window()

    def on_menu_quit(self) -> None:
        if self.app and hasattr(self.app, "exit_application"):
            self.app.exit_application()

    def retranslate(self) -> None:
        # Context menu is rebuilt dynamically on each right-click with current t() strings
        pass
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/gui/test_tray_service.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/atbclone/gui/services/tray_service.py tests/gui/test_tray_service.py
git commit -m "feat(gui): implement native macOS TrayService"
```

---

### Task 3: Add Window & Tray Settings to `SettingsView`

**Files:**
- Modify: `src/atbclone/gui/views/settings_view.py`
- Test: `tests/gui/test_logs_and_settings_views.py`

**Interfaces:**
- Consumes: `atbclone.core.config.get_config_value`, `atbclone.core.config.set_config_value`, `TrayService`
- Produces: `SettingsView.switch_minimize_to_tray`

- [ ] **Step 1: Write the failing test for SettingsView tray toggle**

Add test in `tests/gui/test_logs_and_settings_views.py`:
```python
def test_settings_minimize_to_tray_switch():
    from atbclone.gui.views.settings_view import SettingsView
    from atbclone.core.config import set_config_value, get_config_value

    set_config_value("minimize_to_tray", True)
    view = SettingsView()
    assert hasattr(view, "switch_minimize_to_tray")
    assert view.switch_minimize_to_tray.value is True

    # Test toggling updates config
    view.switch_minimize_to_tray.value = False
    view._on_minimize_to_tray_changed(view.switch_minimize_to_tray)
    assert get_config_value("minimize_to_tray") is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/gui/test_logs_and_settings_views.py::test_settings_minimize_to_tray_switch -v`
Expected: FAIL (missing `switch_minimize_to_tray`).

- [ ] **Step 3: Modify `src/atbclone/gui/views/settings_view.py`**

Add the "Window & Tray Preferences" card:
```python
        # ── Card: Window & Tray Preferences ────────────────────────────────── #
        card_tray = toga.Box(style=Pack(direction=COLUMN, margin_bottom=15, background_color=Theme.BG_CARD))
        card_tray.add(toga.Label(t("settings_card_tray"), style=Pack(font_weight="bold", font_size=14, margin_bottom=8, color=Theme.TEXT_PRIMARY)))

        current_tray_cfg = bool(get_config_value("minimize_to_tray", False))
        self.switch_minimize_to_tray = toga.Switch(
            t("settings_switch_minimize_to_tray"),
            value=current_tray_cfg,
            on_change=self._on_minimize_to_tray_changed,
            style=Pack(margin_bottom=4),
        )
        card_tray.add(self.switch_minimize_to_tray)
        card_tray.add(toga.Label(t("settings_hint_minimize_to_tray"), style=Pack(font_size=11, color=Theme.TEXT_MUTED)))
        content_box.add(card_tray)
```
And add the change handler:
```python
    def _on_minimize_to_tray_changed(self, widget: toga.Switch) -> None:
        val = bool(widget.value)
        set_config_value("minimize_to_tray", val)
        if self.app_instance and hasattr(self.app_instance, "tray_service") and self.app_instance.tray_service:
            if val:
                self.app_instance.tray_service.enable()
            else:
                self.app_instance.tray_service.disable()
```
And in `on_save_settings`, persist `minimize_to_tray`.

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/gui/test_logs_and_settings_views.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/atbclone/gui/views/settings_view.py tests/gui/test_logs_and_settings_views.py
git commit -m "feat(gui): add minimize to tray toggle in SettingsView"
```

---

### Task 4: Integrate TrayService & Window Minimize Interception in `ATBCloneApp`

**Files:**
- Modify: `src/atbclone/gui/app.py`
- Test: `tests/gui/test_app_integration.py`

**Interfaces:**
- Consumes: `TrayService`, `get_config_value`
- Produces:
  - `ATBCloneApp.tray_service`
  - `ATBCloneApp.show_main_window()`
  - `ATBCloneApp.exit_application()`
  - Window minimization interception to hide window when tray enabled

- [ ] **Step 1: Write failing test for app tray integration**

Add tests to `tests/gui/test_app_integration.py`:
```python
def test_app_tray_service_initialized():
    from atbclone.gui.app import ATBCloneApp
    from atbclone.core.config import set_config_value

    set_config_value("minimize_to_tray", False)
    app = ATBCloneApp()
    app.startup()
    assert hasattr(app, "tray_service")
    assert app.tray_service is not None

def test_app_show_main_window():
    from atbclone.gui.app import ATBCloneApp
    app = ATBCloneApp()
    app.startup()
    app.show_main_window()
    assert app.main_window.visible
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/gui/test_app_integration.py::test_app_tray_service_initialized -v`
Expected: FAIL

- [ ] **Step 3: Modify `src/atbclone/gui/app.py`**

1. Import `TrayService` and `get_config_value`.
2. In `startup()`:
   ```python
   self.tray_service = TrayService(app=self)
   if get_config_value("minimize_to_tray", False):
       self.tray_service.enable()

   # Hook Cocoa window miniaturization
   self._setup_window_tray_behavior()
   ```
3. Add helper methods:
   ```python
   def _setup_window_tray_behavior(self):
       if sys.platform != "darwin":
           return
       try:
           from toga_cocoa.libs.appkit import NSNotificationCenter
           native_win = getattr(getattr(self.main_window, "_impl", None), "native", None)
           if native_win:
               def on_miniaturize(notification):
                   if self.tray_service and self.tray_service.is_enabled:
                       # Hide window without docking
                       native_win.orderOut_(None)

               # Register observer for NSWindowWillMiniaturizeNotification
               NSNotificationCenter.defaultCenter.addObserver_selector_name_object_(
                   self.tray_service._target if hasattr(self.tray_service, "_target") else None,
                   None,
                   "NSWindowWillMiniaturizeNotification",
                   native_win,
               )
       except Exception:
           pass

   def show_main_window(self):
       """Bring main window to front and activate application."""
       try:
           if hasattr(self, "main_window") and self.main_window:
               self.main_window.show()
               if sys.platform == "darwin":
                   from toga_cocoa.libs.appkit import NSApplication
                   native_win = getattr(getattr(self.main_window, "_impl", None), "native", None)
                   if native_win and hasattr(native_win, "makeKeyAndOrderFront_"):
                       native_win.makeKeyAndOrderFront_(None)
                   NSApplication.sharedApplication.activateIgnoringOtherApps_(True)
       except Exception:
           pass

   def exit_application(self):
       """Cleanly exit the ATBClone application."""
       if hasattr(self, "tray_service") and self.tray_service:
           self.tray_service.disable()
       self.exit()
   ```
4. In `retranslate_ui()`, add:
   ```python
   if hasattr(self, "tray_service") and self.tray_service:
       self.tray_service.retranslate()
   ```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/gui/test_app_integration.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/atbclone/gui/app.py tests/gui/test_app_integration.py
git commit -m "feat(gui): integrate TrayService and window minimize hook in ATBCloneApp"
```

---

### Task 5: Full Regression Testing & Verification

**Files:**
- Test: All test suites in `tests/`

- [ ] **Step 1: Run complete test suite**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/ -v`
Expected: All 280+ tests pass with 0 errors.

- [ ] **Step 2: Final commit**

```bash
git commit -m "test: verify full test suite for minimize to tray feature"
```
