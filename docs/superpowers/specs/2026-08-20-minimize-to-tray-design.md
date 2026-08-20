# Design Spec: Minimize to System Tray Support in ATBClone

## 1. Context & Motivation
ATBClone is a desktop application on macOS built with BeeWare Toga and native Cocoa AppKit integrations. Users running application clones often keep ATBClone running in the background. To improve workflow ergonomics and desktop cleanliness, users require an option in "Global Settings" (全局设置) to minimize ATBClone to the macOS menu bar status tray (`NSStatusItem`).

## 2. Requirements & User Experience

### 2.1 Settings Preference
- Add a new "Window & Tray Preferences" (窗口与托盘偏好) card in `SettingsView`.
- Provide a toggle switch: **"Minimize to System Tray"** (`minimize_to_tray`).
- Default value is `False`.
- The configuration is persisted into `~/.atbclone/config.json`.
- Toggling the switch immediately enables or disables the status bar tray icon.

### 2.2 System Tray Lifecycle & Appearance
- **Dynamic Presence**: When `minimize_to_tray` is enabled, the ATBClone icon appears in the macOS top-right menu bar. When disabled, the status item is removed from the menu bar.
- **Icon**: Displays the application icon (`get_app_icon_path("png")`) sized for the macOS menu bar (18x18 points).
- **Tooltip**: Displays `"ATBClone"`.

### 2.3 Mouse Interactions on Tray Icon
- **Left-Click (Primary Action)**:
  - Immediately restores and brings the ATBClone main window to the front (`makeKeyAndOrderFront:`).
  - Activates the application (`NSApp.activateIgnoringOtherApps:True`).
  - Does not toggle hide if already front; focuses the main interface directly.
- **Right-Click (Context Menu)**:
  - Displays a native Cocoa `NSMenu` popup:
    1. `t("tray_menu_show")` ("显示主界面" / "Show ATBClone") -> Shows and focuses the main window.
    2. Separator line.
    3. `t("tray_menu_quit")` ("退出 ATBClone" / "Quit ATBClone") -> Cleanly terminates the application.

### 2.4 Window Minimize & Close Behavior
- **Window Minimize Button (Yellow `-`)**:
  - When `minimize_to_tray` is `True`: Intercepts minimization, cancels Dock animation, and hides the main window (`orderOut:`).
  - When `minimize_to_tray` is `False`: Normal macOS minimization to Dock.
- **Window Close Button (Red `X`)\**:
  - Exits / closes the application normally.

## 3. Architecture & Component Changes

```
┌─────────────────────────────────────────────────────────────┐
│                       ATBCloneApp                           │
│  - startup()                                                │
│  - show_main_window()                                       │
│  - exit_application()                                       │
│  - on_window_miniaturize()                                  │
└──────────────┬──────────────────────────────┬───────────────┘
               │                              │
               ▼                              ▼
┌──────────────────────────────┐ ┌────────────────────────────┐
│         TrayService          │ │        SettingsView        │
│  - enable() / disable()      │ │  - switch_minimize_to_tray │
│  - NSStatusItem & button     │ │  - persists config.json    │
│  - Left/Right click handler  │ │  - triggers TrayService    │
│  - NSMenu (Show / Quit)      │ └────────────────────────────┘
│  - retranslate()             │
└──────────────────────────────┘
```

### 3.1 `src/atbclone/gui/services/tray_service.py` [NEW]
- Implements `TrayService`:
  - `__init__(app: ATBCloneApp)`
  - `is_enabled: bool`
  - `enable() -> bool`: Creates `NSStatusItem` on macOS `NSStatusBar.systemStatusBar`, attaches target handler for `NSEventMaskLeftMouseUp | NSEventMaskRightMouseUp`.
  - `disable() -> None`: Removes `NSStatusItem` from status bar.
  - `on_tray_clicked(sender)`: Distinguishes left vs right click from `NSApp.currentEvent.type`.
  - `show_context_menu()`: Builds localized `NSMenu` and calls `popUpStatusItemMenu_`.
  - `retranslate()`: Updates menu titles when language changes.
  - Fallbacks gracefully if run on non-macOS or headless environments.

### 3.2 `src/atbclone/gui/views/settings_view.py` [MODIFY]
- Adds `card_tray` with `toga.Switch` for `minimize_to_tray`.
- Loads initial state from `get_config_value("minimize_to_tray", False)`.
- Updates `config.json` on switch change and calls `self.app_instance.tray_service.enable()/disable()`.
- Updates `on_save_settings` to save `minimize_to_tray`.

### 3.3 `src/atbclone/gui/app.py` [MODIFY]
- Instantiates `self.tray_service = TrayService(app=self)` in `startup()`.
- If `get_config_value("minimize_to_tray", False)` is `True`, calls `self.tray_service.enable()`.
- Adds `show_main_window()` method.
- Adds Cocoa window notification observer for `NSWindowWillMiniaturizeNotification` to hide window when tray mode is active.
- Updates `retranslate_ui()` to trigger `self.tray_service.retranslate()`.

### 3.4 `src/atbclone/core/i18n.py` [MODIFY]
- Adds localized strings across 9 languages (en, zh, zh_TW, ja, ko, de, fr, ru, es):
  - `settings_card_tray`
  - `settings_switch_minimize_to_tray`
  - `settings_hint_minimize_to_tray`
  - `tray_menu_show`
  - `tray_menu_quit`

## 4. Verification Plan

### 4.1 Automated Unit Tests
- `tests/gui/test_tray_service.py`:
  - Test `TrayService` initialization, enable, disable, and click dispatching with mocked Cocoa `NSStatusBar` & `NSStatusItem`.
  - Test graceful degradation when Cocoa AppKit is unavailable.
- `tests/gui/test_logs_and_settings_views.py`:
  - Verify settings switch for `minimize_to_tray` reflects saved configuration and calls persistence.
- `tests/test_i18n.py`:
  - Verify all new i18n keys exist and format without error across all 9 languages.
- Run full pytest suite: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/`.

### 4.2 Manual Verification
- Launch application: `conda run -n ATBClone python -m atbclone.app`.
- Go to Global Settings -> Turn ON "Minimize to System Tray".
- Verify ATBClone icon appears in macOS menu bar.
- Click yellow minimize button (-) on main window -> Verify window hides and does not dock.
- Left-click tray icon -> Verify main window reappears immediately in foreground.
- Right-click tray icon -> Verify menu with "显示主界面" and "退出" appears.
- Test language switching -> Verify tray menu updates language.
- Turn OFF "Minimize to System Tray" -> Verify tray icon disappears and minimize behaves normally.
