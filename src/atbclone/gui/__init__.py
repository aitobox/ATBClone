"""ATBClone GUI Package (BeeWare Toga)."""

from atbclone.core.resources import get_app_icon_path
from .patch_cocoa import patch_cocoa_widgets

# Apply macOS Cocoa patches early
patch_cocoa_widgets()


def build_app():
    from .app import ATBCloneApp
    patch_cocoa_widgets()
    icon_path = get_app_icon_path("png")
    return ATBCloneApp("ATBClone", "com.atbclone.app", icon=icon_path)


def main():
    import os
    import sys

    app = build_app()
    try:
        app.main_loop()
    finally:
        # On macOS packaged applications (Briefcase / native C launcher),
        # popping the native C autorelease pool after Py_Finalize can crash
        # (SIGSEGV in new_threadstate via ctypes/rubicon-objc).
        # We explicitly call os._exit(0) to terminate the process cleanly.
        try:
            sys.stdout.flush()
            sys.stderr.flush()
        except Exception:
            pass
        os._exit(0)


__all__ = ["build_app", "main", "patch_cocoa_widgets"]

