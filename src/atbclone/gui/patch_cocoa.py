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


def configure_cocoa_wrapping_label(native_label: Any, selectable: bool = True) -> None:
    """Configure an NSTextField for multiline text wrapping, selectable text, word breaking, and natural bounds calculation."""
    if sys.platform != "darwin" or native_label is None:
        return
    try:
        cell = getattr(native_label, "cell", None)
        if cell is not None:
            if hasattr(cell, "setWraps_"):
                cell.setWraps_(True)
            if hasattr(cell, "setLineBreakMode_"):
                cell.setLineBreakMode_(0)  # NSLineBreakByWordWrapping
            if hasattr(cell, "setScrollable_"):
                cell.setScrollable_(False)
            if hasattr(cell, "setSelectable_"):
                cell.setSelectable_(selectable)
        if hasattr(native_label, "setMaximumNumberOfLines_"):
            native_label.setMaximumNumberOfLines_(0)
    except Exception:
        pass


def configure_cocoa_multiline_text_view(native_scroll_view: Any, font_size: float = 12.5, readonly: bool = False) -> None:
    """Configure an NSTextView inside an NSScrollView for crisp typography, selection, and readonly support."""
    if sys.platform != "darwin" or native_scroll_view is None:
        return
    try:
        tv = getattr(native_scroll_view, "documentView", None)
        if tv is not None:
            if hasattr(tv, "setSelectable_"):
                tv.setSelectable_(True)
            if hasattr(tv, "setEditable_"):
                tv.setEditable_(not readonly)
            from toga_cocoa.libs import NSFont
            if hasattr(tv, "setFont_"):
                try:
                    tv.setFont_(NSFont.monospacedSystemFontOfSize_weight_(font_size, 0.0))
                except Exception:
                    try:
                        tv.setFont_(NSFont.userFixedPitchFontOfSize_(font_size))
                    except Exception:
                        pass
    except Exception:
        pass


def configure_cocoa_card(native_view: Any, corner_radius: float = 10.0, border_width: float = 0.5) -> None:
    """Configure an NSView container to display as an elevated macOS card with rounded corners and hairline border."""
    if sys.platform != "darwin" or native_view is None:
        return
    try:
        from toga_cocoa.libs.appkit import NSColor
        if hasattr(native_view, "setWantsLayer_"):
            native_view.setWantsLayer_(True)
        elif hasattr(native_view, "wantsLayer"):
            native_view.wantsLayer = True
        layer = getattr(native_view, "layer", None)
        if layer is not None:
            if hasattr(layer, "setCornerRadius_"):
                layer.setCornerRadius_(corner_radius)
            elif hasattr(layer, "cornerRadius"):
                layer.cornerRadius = corner_radius
            if hasattr(layer, "setMasksToBounds_"):
                layer.setMasksToBounds_(True)
            elif hasattr(layer, "masksToBounds"):
                layer.masksToBounds = True
            if hasattr(layer, "setBorderWidth_"):
                layer.setBorderWidth_(border_width)
            elif hasattr(layer, "borderWidth"):
                layer.borderWidth = border_width

            border_color = NSColor.colorWithRed_green_blue_alpha_(0.88, 0.88, 0.90, 1.0)
            if hasattr(border_color, "CGColor"):
                cg_color = border_color.CGColor
                if hasattr(layer, "setBorderColor_"):
                    layer.setBorderColor_(cg_color)
                elif hasattr(layer, "borderColor"):
                    layer.borderColor = cg_color

            # Subtle drop shadow for visual depth (macOS card style)
            if hasattr(native_view, "setShadow_"):
                try:
                    from rubicon.objc import ObjCClass
                    NSShadow = ObjCClass("NSShadow")
                    shadow = NSShadow.alloc().init()
                    shadow.shadowOffset = (0, -1)
                    shadow.shadowBlurRadius = 4.0
                    if hasattr(NSColor, "colorWithRed_green_blue_alpha_"):
                        shadow.shadowColor = NSColor.colorWithRed_green_blue_alpha_(0.0, 0.0, 0.0, 0.08)
                    native_view.setShadow_(shadow)
                except Exception:
                    pass
    except Exception:
        pass


def configure_cocoa_sidebar_active(native_btn: Any, active: bool) -> None:
    """Set or clear the Cocoa-level background highlight on a sidebar button NSView for active state.

    Uses the NSView layer backgroundColor to paint Theme.BG_SIDEBAR_ACTIVE (#DFE1E8)
    behind the active nav item, matching native macOS sidebar selection styling.
    """
    if sys.platform != "darwin" or native_btn is None:
        return
    try:
        from toga_cocoa.libs.appkit import NSColor
        if hasattr(native_btn, "setWantsLayer_"):
            native_btn.setWantsLayer_(True)
        layer = getattr(native_btn, "layer", None)
        if layer is None:
            return
        if active:
            # #DFE1E8 → r=0.875 g=0.882 b=0.910 a=1.0
            bg = NSColor.colorWithRed_green_blue_alpha_(0.875, 0.882, 0.910, 1.0)
        else:
            bg = NSColor.clearColor
        if hasattr(bg, "CGColor"):
            cg = bg.CGColor
            if hasattr(layer, "setBackgroundColor_"):
                layer.setBackgroundColor_(cg)
            elif hasattr(layer, "backgroundColor"):
                layer.backgroundColor = cg
        # Rounded corners for the active highlight pill
        if active:
            if hasattr(layer, "setCornerRadius_"):
                layer.setCornerRadius_(6.0)
        else:
            if hasattr(layer, "setCornerRadius_"):
                layer.setCornerRadius_(0.0)
    except Exception:
        pass


def configure_cocoa_window_movable(window: Any) -> None:
    """Enable window drag from any background area (movableByWindowBackground) on the NSWindow.

    This allows users to drag the window by clicking and dragging in the top bar or content
    area — matching standard macOS single-pane utility app behavior.
    """
    if sys.platform != "darwin" or window is None:
        return
    try:
        native = getattr(getattr(window, "_impl", None), "native", None)
        if native is None:
            native = getattr(window, "native", None)
        if native is not None and hasattr(native, "setMovableByWindowBackground_"):
            native.setMovableByWindowBackground_(True)
    except Exception:
        pass


if sys.platform == "darwin":
    try:
        from toga_cocoa.widgets.table import TogaTable
        from toga_cocoa.libs import NSImage, NSIndexSet
        from rubicon.objc import objc_method

        class ATBTable(TogaTable):
            @objc_method
            def tableView_didClickTableColumn_(self, tableView, tableColumn) -> None:
                try:
                    table_columns = list(self.tableColumns)
                    col_index = -1
                    for idx, col in enumerate(table_columns):
                        if col == tableColumn or str(col.identifier) == str(tableColumn.identifier):
                            col_index = idx
                            break
                    if col_index == -1:
                        return

                    toga_col = getattr(tableColumn, "toga_column", None)
                    if toga_col is None and hasattr(self.interface, "columns") and col_index < len(self.interface.columns):
                        toga_col = self.interface.columns[col_index]

                    clicked_id = str(tableColumn.identifier)
                    curr_id = getattr(self, "_sort_col_id", None)
                    if curr_id == clicked_id:
                        ascending = not getattr(self, "_sort_ascending", True)
                    else:
                        ascending = True

                    self._sort_col_id = clicked_id
                    self._sort_ascending = ascending

                    # Update macOS sort indicator chevrons
                    indicator_name = "NSAscendingSortIndicator" if ascending else "NSDescendingSortIndicator"
                    indicator_img = NSImage.imageNamed_(indicator_name)
                    for col in table_columns:
                        if str(col.identifier) == clicked_id:
                            self.setIndicatorImage_inTableColumn_(indicator_img, col)
                        else:
                            self.setIndicatorImage_inTableColumn_(None, col)

                    if hasattr(self, "setHighlightedTableColumn_"):
                        self.setHighlightedTableColumn_(tableColumn)

                    # If interface has custom handler, invoke it
                    if hasattr(self.interface, "on_header_sort") and callable(self.interface.on_header_sort):
                        self.interface.on_header_sort(col_index, toga_col, ascending)
                        return

                    # Default safe auto-sorting
                    if hasattr(self.interface, "data") and self.interface.data is not None:
                        col_accessor = getattr(toga_col, "accessor", None) or str(col_index)

                        def _safe_sort_key(row):
                            val = None
                            if hasattr(row, col_accessor):
                                val = getattr(row, col_accessor)
                            elif hasattr(toga_col, "value"):
                                try:
                                    val = toga_col.value(row)
                                except Exception:
                                    pass
                            elif isinstance(row, (tuple, list)) and col_index < len(row):
                                val = row[col_index]
                            elif isinstance(row, dict) and col_accessor in row:
                                val = row[col_accessor]

                            if val is None:
                                return (2, "")
                            if isinstance(val, (int, float)):
                                return (0, val)
                            if isinstance(val, bool):
                                return (0, int(val))
                            return (1, str(val).lower())

                        # Preserve selection if any
                        selected_item = getattr(self.interface, "selection", None)

                        if hasattr(self.interface.data, "_data") and isinstance(self.interface.data._data, list):
                            self.interface.data._data.sort(key=_safe_sort_key, reverse=not ascending)
                            self.reloadData()
                            if selected_item is not None and selected_item in self.interface.data._data:
                                new_idx = self.interface.data._data.index(selected_item)
                                self.selectRowIndexes_byExtendingSelection_(NSIndexSet.indexSetWithIndex(new_idx), False)
                        elif isinstance(self.interface.data, list):
                            self.interface.data.sort(key=_safe_sort_key, reverse=not ascending)
                            self.reloadData()
                        else:
                            try:
                                rows = list(self.interface.data)
                                rows.sort(key=_safe_sort_key, reverse=not ascending)
                                self.interface.data = rows
                            except Exception:
                                pass
                except Exception:
                    pass
    except Exception:
        ATBTable = None
else:
    ATBTable = None


def patch_cocoa_widgets() -> None:
    """Apply monkeypatches to toga_cocoa widget implementations on macOS.

    Ensures:
    - All single-line TextInput widgets support horizontal scrolling, clipping mode, and readable 13.5px fonts.
    - All Switch (checkbox) widgets have comfortable 13.5px label fonts.
    - All Selection (dropdown) widgets have comfortable 12.0px option fonts and support set_font.
    - All Table widgets have comfortable row height (34px), crisp 12.5px headers, readable 13.0px cell fonts, and native header sorting.
    """
    global _is_patched
    if _is_patched or sys.platform != "darwin":
        return

    try:
        import toga_cocoa.libs.appkit
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
        if ATBTable is not None:
            try:
                from toga_cocoa.libs import (
                    NSBezelBorder,
                    NSScrollView,
                    NSTableViewColumnAutoresizingStyle,
                    SEL,
                )

                def _patched_table_create(self):
                    self.native = NSScrollView.alloc().init()
                    self.native.hasVerticalScroller = True
                    self.native.hasHorizontalScroller = False
                    self.native.autohidesScrollers = False
                    self.native.borderType = NSBezelBorder

                    self.native_table = ATBTable.alloc().init()
                    self.native_table.interface = self.interface
                    self.native_table.impl = self
                    self.native_table.columnAutoresizingStyle = (
                        NSTableViewColumnAutoresizingStyle.Uniform
                    )
                    self.native_table.usesAlternatingRowBackgroundColors = True
                    self.native_table.allowsMultipleSelection = self.interface.multiple_select
                    self.native_table.allowsColumnReordering = False

                    self.columns = []
                    if not self.interface._show_headings:
                        self.native_table.setHeaderView(None)
                    for index, toga_column in enumerate(self.interface._columns):
                        self._insert_column(index, toga_column)

                    self.native_table.delegate = self.native_table
                    self.native_table.dataSource = self.native_table
                    self.native_table.target = self.native_table
                    self.native_table.doubleAction = SEL("onDoubleClick:")

                    self.native.documentView = self.native_table
                    self.add_constraints()

                    configure_cocoa_table(self.native_table, row_height=34.0)

                CocoaTable.create = _patched_table_create
            except Exception:
                pass

        _orig_icon_setup = TogaIconView.setup

        def _patched_icon_setup(self):
            _orig_icon_setup(self)
            try:
                if hasattr(self, "textField") and self.textField is not None:
                    self.textField.setFont_(NSFont.systemFontOfSize_(13.0))
            except Exception:
                pass

        TogaIconView.setup = _patched_icon_setup

        # 5. Box / Card Surface Patch
        try:
            from toga_cocoa.widgets.box import Box as CocoaBox
            _orig_box_set_bg = CocoaBox.set_background_color

            def _patched_box_set_bg(self, color):
                _orig_box_set_bg(self, color)
                if color is not None:
                    c_str = str(color).upper()
                    if "#FFFFFF" in c_str or "RGBA(255, 255, 255" in c_str or "RGB(255, 255, 255" in c_str or c_str == "WHITE":
                        configure_cocoa_card(self.native, corner_radius=10.0, border_width=0.5)

            CocoaBox.set_background_color = _patched_box_set_bg
        except Exception:
            pass

        # 6. AppDelegate reopen patch (clicking Dock icon restores window)
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

        # 6. About Dialog Patch (ensure version and copyright information are always populated)
        try:
            from toga_cocoa.app import App as CocoaApp
            from toga_cocoa.libs import (
                NSAboutPanelOptionApplicationIcon,
                NSAboutPanelOptionApplicationName,
                NSAboutPanelOptionApplicationVersion,
                NSAboutPanelOptionVersion,
                NSMutableDictionary,
            )

            def _patched_show_about_dialog(self):
                from atbclone import __version__
                options = NSMutableDictionary.alloc().init()

                if (
                    self.interface.icon
                    and hasattr(self.interface.icon, "_impl")
                    and getattr(self.interface.icon._impl, "native", None)
                ):
                    options[NSAboutPanelOptionApplicationIcon] = self.interface.icon._impl.native
                options[NSAboutPanelOptionApplicationName] = self.interface.formal_name or "ATBClone"

                app_ver = self.interface.version or __version__
                options[NSAboutPanelOptionApplicationVersion] = app_ver
                options[NSAboutPanelOptionVersion] = "1"

                author = self.interface.author or "Brain Zhang"
                options["Copyright"] = f"Copyright © {author}"

                self.native.orderFrontStandardAboutPanelWithOptions(options)

            CocoaApp.show_about_dialog = _patched_show_about_dialog
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

