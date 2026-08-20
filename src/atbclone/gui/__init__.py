"""ATBClone GUI Package (BeeWare Toga)."""

def build_app():
    from .app import ATBCloneApp
    return ATBCloneApp("ATBClone", "com.atbclone.app")


def main():
    app = build_app()
    return app.main_loop()


__all__ = ["build_app", "main"]
