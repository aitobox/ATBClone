"""WrappingLabel widget for multiline text wrapping in Toga Cocoa without expanding layout width."""

import math
import sys
from typing import Any
import toga
from travertino.size import at_least

from atbclone.gui.patch_cocoa import configure_cocoa_wrapping_label


class WrappingLabel(toga.Label):
    """A Toga Label subclass that automatically wraps text across multiple lines.

    Standard Toga Label on macOS computes single-line intrinsic width, which
    causes parent containers and windows to widen horizontally when text is long.
    WrappingLabel configures Cocoa NSTextField for word wrapping, keeps intrinsic width
    unconstrained (None), and computes intrinsic height dynamically based on the
    allocated layout or window width.
    """

    def __init__(self, text: str = "", **kwargs: Any):
        super().__init__(text, **kwargs)
        self._last_layout_width: float = 0.0
        self._configure_wrapping()

    def _configure_wrapping(self) -> None:
        if sys.platform != "darwin":
            return
        try:
            native = getattr(getattr(self, "_impl", None), "native", None)
            configure_cocoa_wrapping_label(native)

            impl = getattr(self, "_impl", None)
            if impl is not None:
                impl.rehint = self._custom_rehint
                orig_set_bounds = impl.set_bounds

                def _wrapped_set_bounds(x: float, y: float, width: float, height: float) -> None:
                    orig_set_bounds(x, y, width, height)
                    if abs(width - self._last_layout_width) > 5 and width > 50:
                        self._last_layout_width = width
                        self._custom_rehint()

                impl.set_bounds = _wrapped_set_bounds
                self._custom_rehint()
        except Exception:
            pass

    def _get_target_width(self) -> float:
        w = 0.0
        try:
            if hasattr(self, "layout") and self.layout and self.layout.content_width > 50:
                w = float(self.layout.content_width)
            elif hasattr(self, "_impl") and self._impl.native and self._impl.native.superview:
                pw = float(self._impl.native.superview.frame.size.width)
                margin = (getattr(self.style, "margin_left", 0) or 0) + (getattr(self.style, "margin_right", 0) or 0)
                if pw > margin + 50:
                    w = pw - margin
            if w <= 50 and hasattr(self, "window") and self.window and self.window.size:
                w = max(200.0, float(self.window.size[0]) - 320.0)
        except Exception:
            pass
        return max(200.0, w or 580.0)

    def _custom_rehint(self) -> None:
        if sys.platform != "darwin":
            return
        try:
            native = getattr(getattr(self, "_impl", None), "native", None)
            if native is None:
                return
            from toga_cocoa.libs import NSPoint, NSRect, NSSize

            target_w = self._get_target_width()
            bounds = NSRect(NSPoint(0, 0), NSSize(target_w, 10000))
            cell = getattr(native, "cell", None)
            if cell is not None and hasattr(cell, "cellSizeForBounds_"):
                cell_size = cell.cellSizeForBounds_(bounds)
                h = max(16.0, math.ceil(cell_size.height) + 2)
            else:
                h = 16.0
            self.intrinsic.width = None
            self.intrinsic.height = at_least(h)
        except Exception:
            self.intrinsic.width = None
            self.intrinsic.height = at_least(16.0)
