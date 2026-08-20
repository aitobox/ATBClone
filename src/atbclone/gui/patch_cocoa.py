"""macOS Cocoa native widget patches and tweaks for BeeWare Toga."""

import sys
from typing import Any

_is_patched = False


def configure_cocoa_text_field(native_text_field: Any) -> None:
    """Configure an NSTextField for smooth single-line text editing and horizontal scrolling.

    By default, Toga Cocoa NSTextFieldCell has wraps=True and isScrollable=False.
    When long text (e.g. file paths) exceeds the text field width, Cocoa wraps the text
    vertically into line 2 (which is hidden/clipped in a single-line frame) instead of
    scrolling horizontally, causing cursor jumps and unexpected text displacement.

    This helper configures:
    - cell.setScrollable_(True)
    - cell.setWraps_(False)
    - cell.setLineBreakMode_(2)  # NSLineBreakByClipping
    - native.setUsesSingleLineMode_(True)
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
    except Exception:
        pass


def patch_cocoa_widgets() -> None:
    """Apply monkeypatches to toga_cocoa widget implementations on macOS.

    Ensures all single-line TextInput widgets in the app automatically support
    horizontal scrolling, clipping line break mode, and smooth cursor movement.
    """
    global _is_patched
    if _is_patched or sys.platform != "darwin":
        return

    try:
        from toga_cocoa.widgets.textinput import TextInput as CocoaTextInput

        _orig_create = CocoaTextInput.create

        def _patched_create(self):
            _orig_create(self)
            configure_cocoa_text_field(self.native)

        CocoaTextInput.create = _patched_create
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

