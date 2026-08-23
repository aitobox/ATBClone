"""Tests for macOS Cocoa TextInput patch and smooth single-line scrolling."""

import sys
import toga
from atbclone.core.i18n import set_language, t, SUPPORTED_LANGUAGES
from atbclone.gui.patch_cocoa import patch_cocoa_widgets, configure_cocoa_text_field


def test_btn_browse_dir_i18n():
    """Verify btn_browse_dir translation is present across all supported languages."""
    for lang in SUPPORTED_LANGUAGES:
        set_language(lang)
        text = t("btn_browse_dir")
        assert text != "btn_browse_dir"
        assert len(text.strip()) > 0


def test_patch_cocoa_widgets_idempotent():
    """Verify patch_cocoa_widgets can be called multiple times without error."""
    patch_cocoa_widgets()
    patch_cocoa_widgets()


def test_cocoa_textinput_single_line_scrolling():
    """Verify TextInput on macOS Cocoa has single-line scrolling enabled to prevent cursor jumping."""
    patch_cocoa_widgets()
    ti = toga.TextInput(value="/Users/brainzhang/ATBClone/Data/LongPathName")
    assert ti.value == "/Users/brainzhang/ATBClone/Data/LongPathName"

    if sys.platform == "darwin":
        native = getattr(getattr(ti, "_impl", None), "native", None)
        if native is not None and hasattr(native, "cell"):
            cell = native.cell
            # Check cell single-line scrollable properties
            if hasattr(cell, "isScrollable"):
                assert cell.isScrollable() is True
            if hasattr(cell, "wraps"):
                assert cell.wraps is False
            if hasattr(cell, "lineBreakMode"):
                assert cell.lineBreakMode == 2  # NSLineBreakByClipping
            if hasattr(native, "usesSingleLineMode"):
                assert native.usesSingleLineMode is True


def test_configure_cocoa_text_field_mock():
    """Verify configure_cocoa_text_field handles mock objects gracefully."""
    class MockCell:
        def __init__(self):
            self.scrollable = False
            self.wraps = True
            self.line_break_mode = 0

        def setScrollable_(self, val):
            self.scrollable = val

        def setWraps_(self, val):
            self.wraps = val

        def setLineBreakMode_(self, val):
            self.line_break_mode = val

    class MockTextField:
        def __init__(self):
            self.cell = MockCell()
            self.single_line_mode = False

        def setUsesSingleLineMode_(self, val):
            self.single_line_mode = val

    mock_field = MockTextField()
    configure_cocoa_text_field(mock_field)
    if sys.platform == "darwin":
        assert mock_field.cell.scrollable is True
        assert mock_field.cell.wraps is False
        assert mock_field.cell.line_break_mode == 2
        assert mock_field.single_line_mode is True


def test_configure_cocoa_window_mock():
    """Verify configure_cocoa_window sets floating level and orders front."""
    from atbclone.gui.patch_cocoa import configure_cocoa_window

    class MockNativeWindow:
        def __init__(self):
            self.level = 0
            self.ordered_front = False
            self.children = []

        def setLevel_(self, lvl):
            self.level = lvl

        def makeKeyAndOrderFront_(self, sender):
            self.ordered_front = True

        def addChildWindow_ordered_(self, child, order):
            self.children.append((child, order))

    class MockWindow:
        def __init__(self):
            self._impl = type("Impl", (), {"native": MockNativeWindow()})()

    mock_win = MockWindow()
    mock_parent = MockWindow()

    configure_cocoa_window(mock_win, floating=True, parent_window=mock_parent)
    if sys.platform == "darwin":
        assert mock_win._impl.native.level == 3
        assert mock_win._impl.native.ordered_front is True
        assert len(mock_parent._impl.native.children) == 1

