#!/usr/bin/env python3
"""ATBClone Version Management Utility.

Handles inspecting, validating, setting, and bumping semantic version (x.y.z)
across all project configuration files.
"""

import argparse
import re
import sys
from pathlib import Path
from typing import NamedTuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent

VERSION_PATTERN = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


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
    """Represents a file containing a version definition."""

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

    if all_matched and first_ver:
        print(f"\n[✔] All targets are synchronized at v{first_ver}")
        return 0
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
        help="Inspect and display version status across all project files.",
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
        "--dry-run",
        action="store_true",
        help="Preview changes without modifying files.",
    )

    args = parser.parse_args(argv)

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
