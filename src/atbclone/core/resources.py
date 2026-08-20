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


LANGUAGE_RELEASE_NOTE_FILES: dict[str, str] = {
    "en": "ReleaseNote.md",
    "zh": "ReleaseNote_zh.md",
    "zh_TW": "ReleaseNote_zh_TW.md",
    "ja": "ReleaseNote_ja.md",
    "ko": "ReleaseNote_ko.md",
    "de": "ReleaseNote_de.md",
    "fr": "ReleaseNote_fr.md",
    "ru": "ReleaseNote_ru.md",
    "es": "ReleaseNote_es.md",
}


def get_release_notes_dir() -> Path:
    """Resolve directory containing multilingual release notes documents."""
    module_dir = Path(__file__).resolve().parent  # src/atbclone/core
    src_dir = module_dir.parent.parent  # src
    repo_root = src_dir.parent  # project root

    # 1. Direct development workspace docs/release
    candidate_repo = repo_root / "docs" / "release"
    if candidate_repo.is_dir():
        return candidate_repo

    # 2. macOS App Bundle Contents/Resources/docs/release or Contents/Resources/release
    if hasattr(sys, "executable") and sys.executable:
        exe_path = Path(sys.executable).resolve()
        app_contents = exe_path.parent.parent
        bundle_docs = app_contents / "Resources" / "docs" / "release"
        if bundle_docs.is_dir():
            return bundle_docs
        bundle_rel = app_contents / "Resources" / "release"
        if bundle_rel.is_dir():
            return bundle_rel

    # 3. Frozen bundle directory (sys._MEIPASS)
    if hasattr(sys, "_MEIPASS"):
        meipass_docs = Path(sys._MEIPASS) / "docs" / "release"
        if meipass_docs.is_dir():
            return meipass_docs
        meipass_rel = Path(sys._MEIPASS) / "release"
        if meipass_rel.is_dir():
            return meipass_rel

    # 4. Fallback resource/docs/release or package-level docs/release
    resource_docs = get_resource_dir() / "docs" / "release"
    if resource_docs.is_dir():
        return resource_docs

    return candidate_repo


def get_release_notes_path(lang: str | None = None) -> Path | None:
    """Resolve path to localized release note markdown file for given language."""
    from atbclone.core.i18n import normalize_lang_code, get_language

    target_lang = normalize_lang_code(lang) if lang else get_language()
    filename = LANGUAGE_RELEASE_NOTE_FILES.get(target_lang, "ReleaseNote.md")

    release_dir = get_release_notes_dir()
    target_file = release_dir / filename
    if target_file.exists():
        return target_file

    # Fallback to English default
    fallback = release_dir / "ReleaseNote.md"
    if fallback.exists():
        return fallback
    return None

