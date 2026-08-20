"""Resource management and asset path resolution for ATBClone."""

from pathlib import Path
import sys
from typing import Optional


def get_resource_dir() -> Path:
    """Resolve the root directory containing static assets and resources.

    Resolution order:
    1. Repository root / 'resource' (during local development / source runs)
    2. macOS App Bundle Contents/Resources/resource or Contents/Resources
    3. Frozen bundle directory (sys._MEIPASS or package directory)
    """
    # 1. Check direct development workspace root
    module_dir = Path(__file__).resolve().parent  # src/atbclone/core
    src_dir = module_dir.parent.parent  # src
    repo_root = src_dir.parent  # project root
    candidate_repo = repo_root / "resource"
    if candidate_repo.is_dir():
        return candidate_repo

    # 2. Check macOS app bundle Contents/Resources
    if hasattr(sys, "executable") and sys.executable:
        exe_path = Path(sys.executable).resolve()
        # Typical structure: ATBClone.app/Contents/MacOS/ATBClone -> Resources
        app_contents = exe_path.parent.parent
        bundle_res = app_contents / "Resources" / "resource"
        if bundle_res.is_dir():
            return bundle_res
        bundle_res_direct = app_contents / "Resources"
        if bundle_res_direct.is_dir():
            return bundle_res_direct

    # 3. Check PyInstaller / Nuitka frozen directory
    if hasattr(sys, "_MEIPASS"):
        meipass_res = Path(sys._MEIPASS) / "resource"
        if meipass_res.is_dir():
            return meipass_res

    # 4. Fallback to package-relative directory
    pkg_res = module_dir.parent / "resource"
    if pkg_res.is_dir():
        return pkg_res

    # Default fallback
    return candidate_repo


def get_resource_path(relative_path: str) -> Path:
    """Resolve the absolute path to a specific resource file."""
    base_dir = get_resource_dir()
    resolved = (base_dir / relative_path).resolve()
    if not resolved.exists():
        # Also try direct relative to repo root if base_dir was altered
        module_dir = Path(__file__).resolve().parent
        fallback = (module_dir.parent.parent.parent / "resource" / relative_path).resolve()
        if fallback.exists():
            return fallback
    return resolved


def get_app_icon_path(prefer_format: str = "png") -> Optional[Path]:
    """Retrieve absolute path to application logo icon (.png or .icns)."""
    fmt = prefer_format.lower().lstrip(".")
    if fmt == "icns":
        candidate = get_resource_path("images/logo.icns")
        if candidate.exists():
            return candidate
        fallback_png = get_resource_path("images/logo.png")
        return fallback_png if fallback_png.exists() else None

    # Default prefer png
    candidate = get_resource_path("images/logo.png")
    if candidate.exists():
        return candidate
    fallback_icns = get_resource_path("images/logo.icns")
    return fallback_icns if fallback_icns.exists() else None
