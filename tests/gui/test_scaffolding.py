from pathlib import Path
import pytest


def test_gui_module_exports_main():
    import atbclone.gui
    assert hasattr(atbclone.gui, "main") or hasattr(atbclone.gui, "build_app")


def test_build_gui_script_exists_and_executable():
    script = Path(__file__).resolve().parent.parent.parent / "scripts" / "build_gui.sh"
    assert script.exists()
    assert script.stat().st_mode & 0o111  # executable


def test_codesign_wrapper_exists_and_retryable_logic():
    script = Path(__file__).resolve().parent.parent.parent / "scripts" / "codesign_wrapper.py"
    assert script.exists()
    assert script.stat().st_mode & 0o111

    # Import wrapper helper
    import importlib.util
    spec = importlib.util.spec_from_file_location("codesign_wrapper", script)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    assert mod.is_retryable_error("The timestamp service is not available.")
    assert mod.is_retryable_error("Connection timed out to Apple server")
    assert not mod.is_retryable_error("unsupported format for signature")
    assert mod.BACKOFF_DELAYS == [2, 4, 8, 16, 32, 60]


def test_atbclone_package_main_module_exists():
    root = Path(__file__).resolve().parent.parent.parent
    main_py = root / "src" / "atbclone" / "__main__.py"
    assert main_py.exists(), "src/atbclone/__main__.py must exist for Briefcase and python -m atbclone"
    
    app_py = root / "src" / "atbclone" / "app.py"
    assert app_py.exists(), "src/atbclone/app.py must exist"


def test_atbclone_module_runnable_as_main():
    import runpy
    details = runpy._get_module_details("atbclone")
    assert details[0] == "atbclone.__main__"
    assert details[1].origin.endswith("__main__.py")



