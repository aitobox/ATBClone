#!/usr/bin/env python3
"""ATBClone Application Prober & Recipe Generator.

Inspects a macOS .app bundle to detect its runtime framework, sandbox status,
and code signing entitlements, then generates an appropriate Recipe YAML.
"""

import argparse
import plistlib
import subprocess
import sys
from pathlib import Path
import yaml

from atbclone.core.app_inspector import AppInspector
from atbclone.core.app_prober import AppProber
from atbclone.recipes.loader import RecipeLoader


def inspect_entitlements(app_path: Path) -> dict:
    """Extract code signing entitlements as a dictionary."""
    return AppProber.inspect_entitlements(app_path)


def detect_frameworks(app_path: Path) -> list[str]:
    """Detect notable frameworks inside Contents/Frameworks/."""
    return AppProber.detect_frameworks(app_path)


def analyze_app(app_path: Path) -> dict:
    """Perform comprehensive inspection and determine clone strategy."""
    app_info = AppInspector.inspect(app_path)
    entitlements = inspect_entitlements(app_path)
    frameworks = detect_frameworks(app_path)
    result = AppProber.analyze(
        app_path,
        app_info=app_info,
        entitlements=entitlements,
        frameworks=frameworks,
    )
    recipe_data = {
        "bundle_id": result.recipe.bundle_id,
        "app_name": result.recipe.app_name,
        "strategy": result.recipe.strategy,
        "strip_sandbox": result.recipe.strip_sandbox,
    }
    if result.recipe.environment_injection:
        recipe_data["environment_injection"] = result.recipe.environment_injection
    if result.recipe.launch_args:
        recipe_data["launch_args"] = result.recipe.launch_args

    return {
        "app_info": result.app_info,
        "has_sandbox": result.has_sandbox,
        "frameworks": result.frameworks,
        "reason": result.reason,
        "recipe": recipe_data,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Probe a macOS .app bundle and generate an ATBClone Recipe.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("app_path", type=Path, help="Path to the .app bundle (e.g. /Applications/WeChat.app)")
    parser.add_argument("--save", action="store_true", help="Save generated recipe directly to ~/.atbclone/recipes/")
    parser.add_argument("--output", "-o", type=Path, help="Custom output path to save recipe YAML")

    args = parser.parse_args(argv)
    app_path = args.app_path.expanduser().resolve()

    if not app_path.exists() or not str(app_path).endswith(".app"):
        print(f"[-] Error: Invalid .app path '{app_path}'", file=sys.stderr)
        return 1

    analysis = analyze_app(app_path)
    info = analysis["app_info"]
    recipe_dict = analysis["recipe"]

    yaml_str = yaml.dump(recipe_dict, sort_keys=False, allow_unicode=True)

    print("======================================================")
    print(f"  🔍 Probed Application: {info.app_name}")
    print(f"  Bundle ID    : {info.bundle_id}")
    print(f"  Executable   : {info.executable}")
    print(f"  Sandbox      : {'Yes (com.apple.security.app-sandbox)' if analysis['has_sandbox'] else 'No'}")
    print(f"  Strategy     : {recipe_dict['strategy']}")
    print(f"  Analysis     : {analysis['reason']}")
    print("======================================================")
    print("\n--- Generated Recipe YAML ---")
    print(yaml_str.strip())
    print("-----------------------------")

    if args.save:
        target_dir = RecipeLoader.get_local_dir()
        target_dir.mkdir(parents=True, exist_ok=True)
        target_file = target_dir / f"{info.bundle_id}.yaml"
        target_file.write_text(yaml_str, encoding="utf-8")
        print(f"\n[✔] Saved recipe to: {target_file}")
    elif args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(yaml_str, encoding="utf-8")
        print(f"\n[✔] Saved recipe to: {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
