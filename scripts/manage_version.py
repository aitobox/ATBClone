#!/usr/bin/env python3
"""ATBClone Version Management Utility.

Handles inspecting, validating, setting, and bumping semantic version (x.y.z)
across all project configuration files and multilingual ReleaseNotes.
"""

import argparse
import plistlib
import re
import sys
from pathlib import Path
from typing import Any, NamedTuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent

VERSION_PATTERN = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")
RELEASE_HEADER_PATTERN = re.compile(r"(?m)^##\s*\[v?(\d+\.\d+\.\d+)\]")

# 9 Supported Languages for Multilingual Release Notes in docs/release/
DOCS_RELEASE_FILES: list[tuple[str, str]] = [
    ("ReleaseNote.md", "English"),
    ("ReleaseNote_zh.md", "简体中文 (Simplified Chinese)"),
    ("ReleaseNote_zh_TW.md", "繁體中文 (Traditional Chinese)"),
    ("ReleaseNote_ja.md", "日本語 (Japanese)"),
    ("ReleaseNote_ko.md", "한국어 (Korean)"),
    ("ReleaseNote_de.md", "Deutsch (German)"),
    ("ReleaseNote_fr.md", "Français (French)"),
    ("ReleaseNote_ru.md", "Русский (Russian)"),
    ("ReleaseNote_es.md", "Español (Spanish)"),
]


class VersionInfo(NamedTuple):
    major: int
    minor: int
    patch: int

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


def parse_version(version_str: str) -> VersionInfo:
    """Parse and validate an x.y.z version string."""
    match = VERSION_PATTERN.match(version_str.strip())
    if not match:
        raise ValueError(
            f"Invalid version format '{version_str}'. Must strictly follow 'x.y.z' (e.g. 0.1.0)."
        )
    return VersionInfo(
        major=int(match.group(1)),
        minor=int(match.group(2)),
        patch=int(match.group(3)),
    )


def bump_version(current: VersionInfo, bump_type: str) -> VersionInfo:
    """Bump version according to semantic versioning rules."""
    if bump_type == "patch":
        return VersionInfo(current.major, current.minor, current.patch + 1)
    elif bump_type == "minor":
        return VersionInfo(current.major, current.minor + 1, 0)
    elif bump_type == "major":
        return VersionInfo(current.major + 1, 0, 0)
    else:
        raise ValueError(f"Invalid bump type '{bump_type}'. Must be 'patch', 'minor', or 'major'.")


class VersionTarget:
    """Represents a code/config file containing a version definition."""

    def __init__(self, path: Path, pattern: re.Pattern, replace_template: str, name: str):
        self.path = path
        self.pattern = pattern
        self.replace_template = replace_template
        self.name = name

    def read_version(self) -> str | None:
        if not self.path.exists():
            return None
        content = self.path.read_text(encoding="utf-8")
        match = self.pattern.search(content)
        return match.group(1) if match else None

    def update_version(self, new_version: str, dry_run: bool = False) -> bool:
        if not self.path.exists():
            return False
        content = self.path.read_text(encoding="utf-8")
        if not self.pattern.search(content):
            return False
        new_content = self.pattern.sub(self.replace_template.format(version=new_version), content)
        if not dry_run:
            self.path.write_text(new_content, encoding="utf-8")
        return True


class PlistVersionTarget:
    """Represents a macOS Info.plist file containing version definitions."""

    def __init__(self, path: Path, name: str):
        self.path = path
        self.name = name

    def read_version(self) -> str | None:
        if not self.path.exists():
            return None
        try:
            with open(self.path, "rb") as f:
                pl = plistlib.load(f)
            return pl.get("CFBundleShortVersionString")
        except Exception:
            return None

    def update_version(self, new_version: str, dry_run: bool = False) -> bool:
        if not self.path.exists():
            return False
        try:
            with open(self.path, "rb") as f:
                pl = plistlib.load(f)
            pl["CFBundleShortVersionString"] = new_version
            pl["CFBundleVersion"] = new_version
            if not dry_run:
                with open(self.path, "wb") as f:
                    plistlib.dump(pl, f)
            return True
        except Exception:
            return False


class ReleaseNoteTarget:
    """Represents a multilingual release note file in docs/release/."""

    def __init__(self, filename: str, language: str, path: Path):
        self.filename = filename
        self.language = language
        self.path = path

    def exists(self) -> bool:
        return self.path.exists()

    def read_latest_version(self) -> str | None:
        if not self.path.exists():
            return None
        content = self.path.read_text(encoding="utf-8")
        match = RELEASE_HEADER_PATTERN.search(content)
        return match.group(1) if match else None

    def has_version(self, version_str: str) -> bool:
        if not self.path.exists():
            return False
        content = self.path.read_text(encoding="utf-8")
        pattern = re.compile(rf"(?m)^##\s*\[v?{re.escape(version_str)}\]")
        return bool(pattern.search(content))


def get_version_targets(root: Path = PROJECT_ROOT) -> list[VersionTarget]:
    """Return list of files that manage the project version."""
    return [
        VersionTarget(
            path=root / "pyproject.toml",
            pattern=re.compile(r'(?m)^version\s*=\s*"([0-9]+\.[0-9]+\.[0-9]+)"'),
            replace_template='version = "{version}"',
            name="pyproject.toml",
        ),
        VersionTarget(
            path=root / "src" / "atbclone" / "__init__.py",
            pattern=re.compile(r'(?m)^__version__\s*=\s*"([0-9]+\.[0-9]+\.[0-9]+)"'),
            replace_template='__version__ = "{version}"',
            name="src/atbclone/__init__.py",
        ),
    ]


def get_build_artifact_targets(root: Path = PROJECT_ROOT) -> list[Any]:
    """Return optional build/packaging intermediate targets if they exist locally."""
    targets: list[Any] = []

    # 1. Briefcase macOS App Info.plist
    app_plist = root / "build" / "atbclone" / "macos" / "app" / "ATBClone.app" / "Contents" / "Info.plist"
    if not app_plist.exists() and (root / "build").exists():
        found = list((root / "build").glob("**/ATBClone.app/Contents/Info.plist"))
        if found:
            app_plist = found[0]

    targets.append(
        PlistVersionTarget(
            path=app_plist,
            name="Info.plist (macOS App)",
        )
    )

    # 2. Briefcase macOS installer welcome.html
    welcome_html = root / "build" / "atbclone" / "macos" / "app" / "installer" / "resources" / "welcome.html"
    if not welcome_html.exists() and (root / "build").exists():
        found = list((root / "build").glob("**/installer/resources/welcome.html"))
        if found:
            welcome_html = found[0]

    targets.append(
        VersionTarget(
            path=welcome_html,
            pattern=re.compile(r"ATBClone\s+([0-9]+\.[0-9]+\.[0-9]+)"),
            replace_template="ATBClone {version}",
            name="installer/welcome.html",
        )
    )

    return targets


def get_release_note_targets(root: Path = PROJECT_ROOT) -> list[ReleaseNoteTarget]:
    """Return list of 9 multilingual release notes in docs/release/."""
    release_dir = root / "docs" / "release"
    return [
        ReleaseNoteTarget(filename, lang, release_dir / filename)
        for filename, lang in DOCS_RELEASE_FILES
    ]


def check_release_notes(version_str: str, root: Path = PROJECT_ROOT) -> tuple[bool, list[str]]:
    """Check if all 9 release notes files contain the specified version entry."""
    targets = get_release_note_targets(root)
    missing = []
    for t in targets:
        if not t.has_version(version_str):
            missing.append(f"{t.filename} ({t.language})")
    return (len(missing) == 0, missing)


def get_current_version(root: Path = PROJECT_ROOT) -> str:
    """Get the authoritative current version from pyproject.toml / __init__.py."""
    targets = get_version_targets(root)
    for target in targets:
        v = target.read_version()
        if v:
            return v
    raise RuntimeError("Could not find a valid version in project files.")


def show_versions(root: Path = PROJECT_ROOT) -> int:
    """Inspect and display version status across all targets."""
    targets = get_version_targets(root)
    versions: dict[str, str | None] = {}
    for target in targets:
        versions[target.name] = target.read_version()

    print("=== ATBClone Version Status ===")
    print("Package Targets:")
    all_matched = True
    first_ver = None
    for name, ver in versions.items():
        status = ver if ver else "[NOT FOUND]"
        print(f"  - {name:<30}: {status}")
        if ver is not None:
            if first_ver is None:
                first_ver = ver
            elif ver != first_ver:
                all_matched = False
        else:
            all_matched = False

    build_targets = [bt for bt in get_build_artifact_targets(root) if bt.path.exists()]
    if build_targets:
        print("\nBuild Artifact Targets (detected in build/):")
        for bt in build_targets:
            bt_ver = bt.read_version()
            status = f"v{bt_ver}" if bt_ver else "[NO VERSION ENTRY]"
            if first_ver and bt_ver != first_ver:
                status += " [OUT OF SYNC]"
            print(f"  - {bt.name:<30}: {status}")

    rn_targets = get_release_note_targets(root)
    rn_matched = True
    if any(t.exists() for t in rn_targets):
        print("\nMultilingual Release Notes (docs/release/):")
        for rn in rn_targets:
            rn_ver = rn.read_latest_version()
            status = f"v{rn_ver}" if rn_ver else "[NO VERSION ENTRY]"
            if not rn.exists():
                status = "[FILE NOT FOUND]"
                rn_matched = False
            elif first_ver and rn_ver != first_ver:
                rn_matched = False
            print(f"  - {rn.filename:<25} ({rn.language:<30}): {status}")

    if all_matched and first_ver:
        if rn_matched:
            print(f"\n[✔] All package targets and ReleaseNotes are synchronized at v{first_ver}")
            return 0
        else:
            print(f"\n[!] Package version is v{first_ver}, but some ReleaseNotes are out of sync or missing this version entry.")
            return 1
    else:
        print("\n[✘] Version mismatch or missing definitions detected!")
        return 1


def apply_version(new_version_str: str, root: Path = PROJECT_ROOT, dry_run: bool = False) -> int:
    """Set all targets to the specified version."""
    # Validate format
    parse_version(new_version_str)

    targets = get_version_targets(root)
    action_str = "[DRY-RUN] Would update" if dry_run else "Updating"
    print(f"{action_str} version to v{new_version_str}...")

    for target in targets:
        old_ver = target.read_version()
        success = target.update_version(new_version_str, dry_run=dry_run)
        if success:
            print(f"  [✔] {target.name} ({old_ver} -> {new_version_str})")
        else:
            print(f"  [✘] {target.name} (failed to update)")

    build_targets = [bt for bt in get_build_artifact_targets(root) if bt.path.exists()]
    if build_targets:
        for bt in build_targets:
            old_ver = bt.read_version()
            success = bt.update_version(new_version_str, dry_run=dry_run)
            if success:
                print(f"  [✔] {bt.name} ({old_ver} -> {new_version_str})")
            else:
                print(f"  [✘] {bt.name} (failed to update)")

    print(f"\n[✔] Version successfully set to {new_version_str}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="ATBClone Semantic Version Manager (x.y.z)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument(
        "--show",
        action="store_true",
        help="Inspect and display version status across all project files and ReleaseNotes.",
    )
    group.add_argument(
        "--bump",
        choices=["patch", "minor", "major"],
        help="Bump semantic version part.",
    )
    group.add_argument(
        "version",
        nargs="?",
        help="Explicit version string in x.y.z format (e.g. 0.1.0).",
    )

    parser.add_argument(
        "--check-notes",
        metavar="VERSION",
        nargs="?",
        const="",
        help="Verify all 9 docs/release/ ReleaseNotes files contain entry for current or specified version.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without modifying files.",
    )

    args = parser.parse_args(argv)

    if args.check_notes is not None:
        target_v = args.check_notes if args.check_notes else get_current_version()
        synced, missing = check_release_notes(target_v)
        if synced:
            print(f"[✔] All 9 ReleaseNotes in docs/release/ contain entry for v{target_v}.")
            return 0
        else:
            print(f"[-] Missing v{target_v} entry in {len(missing)} ReleaseNotes file(s):")
            for m in missing:
                print(f"  - docs/release/{m}")
            return 1

    if args.show or (not args.bump and not args.version):
        return show_versions()

    current_str = get_current_version()
    current_v = parse_version(current_str)

    if args.bump:
        new_v = bump_version(current_v, args.bump)
        new_version_str = str(new_v)
    else:
        new_version_str = args.version

    return apply_version(new_version_str, dry_run=args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
