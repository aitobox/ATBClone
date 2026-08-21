"""macOS Cocoa native widget patches and tweaks for BeeWare Toga."""

import sys
from typing import Any

_is_patched = False


def configure_cocoa_text_field(native_text_field: Any, font_size: float = 13.5) -> None:
    """Configure an NSTextField for smooth single-line text editing, horizontal scrolling, and clear typography.

    By default, Toga Cocoa NSTextFieldCell has wraps=True and isScrollable=False.
    When long text (e.g. file paths) exceeds the text field width, Cocoa wraps the text
    vertically into line 2 (which is hidden/clipped in a single-line frame) instead of
    scrolling horizontally, causing cursor jumps and unexpected text displacement.

    This helper configures:
    - cell.setScrollable_(True)
    - cell.setWraps_(False)
    - cell.setLineBreakMode_(2)  # NSLineBreakByClipping
    - native.setUsesSingleLineMode_(True)
    - native.setFont_(NSFont.systemFontOfSize_(font_size))
    """
    if sys.platform != "darwin" or native_text_field is None:
        return
    try:
        cell = getattr(native_text_field, "cell", None)
        if cell is not None:
            if hasattr(cell, "setScrollable_"):
                cell.setScrollable_(True)
            if hasattr(cell, "setWraps_"):
                cell.setWraps_(False)
            if hasattr(cell, "setLineBreakMode_"):
                cell.setLineBreakMode_(2)  # NSLineBreakByClipping
        if hasattr(native_text_field, "setUsesSingleLineMode_"):
            native_text_field.setUsesSingleLineMode_(True)
        if hasattr(native_text_field, "setFont_"):
            from toga_cocoa.libs import NSFont
            native_text_field.setFont_(NSFont.systemFontOfSize_(font_size))
    except Exception:
        pass


def configure_cocoa_table(native_table: Any, row_height: float = 34.0) -> None:
    """Configure an NSTableView with comfortable row height (34px) and crisp 12.5px header fonts."""
    if sys.platform != "darwin" or native_table is None:
        return
    try:
        if hasattr(native_table, "setRowHeight_"):
            native_table.setRowHeight_(row_height)
        if hasattr(native_table, "setUsesAlternatingRowBackgroundColors_"):
            native_table.setUsesAlternatingRowBackgroundColors_(True)
        from toga_cocoa.libs import NSFont
        if hasattr(native_table, "tableColumns"):
            for col in native_table.tableColumns:
                header_cell = getattr(col, "headerCell", None)
                if header_cell and hasattr(header_cell, "setFont_"):
                    header_cell.setFont_(NSFont.boldSystemFontOfSize_(12.5))
    except Exception:
        pass


def patch_cocoa_widgets() -> None:
    """Apply monkeypatches to toga_cocoa widget implementations on macOS.

    Ensures:
    - All single-line TextInput widgets support horizontal scrolling, clipping mode, and readable 13.5px fonts.
    - All Switch (checkbox) widgets have comfortable 13.5px label fonts.
    - All Selection (dropdown) widgets have comfortable 12.0px option fonts and support set_font.
    - All Table widgets have comfortable row height (34px), crisp 12.5px headers, and readable 13.0px cell fonts.
    """
    global _is_patched
    if _is_patched or sys.platform != "darwin":
        return

    try:
        from toga_cocoa.widgets.textinput import TextInput as CocoaTextInput
        from toga_cocoa.widgets.switch import Switch as CocoaSwitch
        from toga_cocoa.widgets.selection import Selection as CocoaSelection
        from toga_cocoa.widgets.table import Table as CocoaTable
        from toga_cocoa.widgets.internal.cells import TogaIconView
        from toga_cocoa.libs import NSFont

        # 1. TextInput Patch
        _orig_create = CocoaTextInput.create

        def _patched_create(self):
            _orig_create(self)
            configure_cocoa_text_field(self.native, font_size=13.5)

        CocoaTextInput.create = _patched_create

        # 2. Switch (Checkbox) Patch
        _orig_switch_create = CocoaSwitch.create

        def _patched_switch_create(self):
            _orig_switch_create(self)
            try:
                if hasattr(self, "native") and self.native is not None:
                    self.native.setFont_(NSFont.systemFontOfSize_(13.5))
            except Exception:
                pass

        CocoaSwitch.create = _patched_switch_create

        # 3. Selection (Dropdown) Patch
        _orig_selection_create = CocoaSelection.create

        def _patched_selection_create(self):
            _orig_selection_create(self)
            try:
                if hasattr(self, "native") and self.native is not None:
                    self.native.setFont_(NSFont.systemFontOfSize_(12.0))
            except Exception:
                pass

        def _patched_selection_set_font(self, font):
            try:
                if font and hasattr(font, "_impl") and hasattr(font._impl, "native"):
                    self.native.font = font._impl.native
            except Exception:
                pass

        CocoaSelection.create = _patched_selection_create
        CocoaSelection.set_font = _patched_selection_set_font

        # 4. Table & IconView Patch
        _orig_table_create = CocoaTable.create

        def _patched_table_create(self):
            _orig_table_create(self)
            configure_cocoa_table(getattr(self, "native_table", None), row_height=34.0)

        CocoaTable.create = _patched_table_create

        _orig_icon_setup = TogaIconView.setup

        def _patched_icon_setup(self):
            _orig_icon_setup(self)
            try:
                if hasattr(self, "textField") and self.textField is not None:
                    self.textField.setFont_(NSFont.systemFontOfSize_(13.0))
            except Exception:
                pass

        TogaIconView.setup = _patched_icon_setup

        # 5. AppDelegate reopen patch (clicking Dock icon restores window)
        try:
            import toga_cocoa.libs.appkit
            from toga_cocoa.app import AppDelegate
            from rubicon.objc import objc_method

            @objc_method
            def _applicationShouldHandleReopen_hasVisibleWindows_(self, sender, flag: bool) -> bool:
                if hasattr(self, "interface") and hasattr(self.interface, "show_main_window"):
                    self.interface.show_main_window()
                return True

            AppDelegate.applicationShouldHandleReopen_hasVisibleWindows_ = _applicationShouldHandleReopen_hasVisibleWindows_
        except Exception:
            pass

        _is_patched = True
    except (ImportError, AttributeError, Exception):
        pass


def configure_cocoa_window(window: Any, floating: bool = True, parent_window: Any = None) -> None:
    """Ensure Cocoa NSWindow stays in front and remains key/active during transitions.

    - floating=True: sets window level to NSFloatingWindowLevel (3) so it stays above main windows.
    - parent_window: optionally attaches as child window to parent window.
    - makeKeyAndOrderFront: brings window to foreground and gives it focus.
    """
    if sys.platform != "darwin" or window is None:
        return
    try:
        native = getattr(getattr(window, "_impl", None), "native", None)
        if native is not None:
            if floating and hasattr(native, "setLevel_"):
                # NSFloatingWindowLevel = 3
                native.setLevel_(3)
            if hasattr(native, "makeKeyAndOrderFront_"):
                native.makeKeyAndOrderFront_(None)

            if parent_window is not None:
                parent_native = getattr(getattr(parent_window, "_impl", None), "native", None)
                if parent_native is not None and hasattr(parent_native, "addChildWindow_ordered_"):
                    # NSWindowAbove = 1
                    parent_native.addChildWindow_ordered_(native, 1)
    except Exception:
        pass

