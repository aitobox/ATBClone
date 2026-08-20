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
    app = build_app()
    return app.main_loop()


__all__ = ["build_app", "main", "patch_cocoa_widgets"]

