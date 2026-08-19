"""ATBCloneCli standalone entry point.

Uses absolute imports so Nuitka --onefile can compile this as __main__
without triggering "attempted relative import with no known parent package".
"""
from atbclone.cli.main import cli

if __name__ == "__main__":
    cli()
