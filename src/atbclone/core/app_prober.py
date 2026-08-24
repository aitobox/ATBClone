"""Core application prober and dynamic recipe generator."""

import plistlib
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from atbclone.core.app_inspector import AppInspector
from atbclone.core.models import AppInfo
from atbclone.recipes.models import AppType, Recipe


@dataclass
class ProbeResult:
    app_info: AppInfo
    has_sandbox: bool
    frameworks: list[str]
    strategy: str
    reason: str
    recipe: Recipe
    raw_entitlements: dict[str, Any] = field(default_factory=dict)


class AppProber:
    """Probes local macOS .app bundles to determine optimal cloning strategies."""

    @staticmethod
    def inspect_entitlements(app_path: Path | str) -> dict[str, Any]:
        """Extract code signing entitlements as a dictionary."""
        try:
            res = subprocess.run(
                ["codesign", "-d", "--entitlements", ":-", str(app_path)],
                capture_output=True,
                check=False,
            )
            if res.returncode == 0 and res.stdout:
                return plistlib.loads(res.stdout)
        except Exception:
            pass
        return {}

    @staticmethod
    def detect_frameworks(app_path: Path | str) -> list[str]:
        """Detect notable frameworks and dynamic libraries inside Contents/Frameworks/ or Wrapper/*.app/Frameworks/."""
        path = Path(app_path).expanduser().resolve()
        frameworks_dir = path / "Contents" / "Frameworks"
        if not frameworks_dir.is_dir() and (path / "Wrapper").is_dir():
            for inner in (path / "Wrapper").glob("*.app"):
                fw = inner / "Frameworks"
                if fw.is_dir():
                    frameworks_dir = fw
                    break
        if not frameworks_dir.is_dir():
            return []
        return [
            p.name
            for p in frameworks_dir.iterdir()
            if p.name.endswith(".framework") or p.name.endswith(".dylib")
        ]

    @classmethod
    def detect_app_type(
        cls,
        app_path: Path | str = "",
        bundle_id: str = "",
        frameworks: list[str] | None = None,
    ) -> AppType:
        """Detect the application runtime framework / app type."""
        if frameworks is None and app_path:
            frameworks = cls.detect_frameworks(app_path)
        if frameworks is None:
            frameworks = []

        bid_lower = bundle_id.lower()
        fw_lower = [f.lower() for f in frameworks]

        # 1. Electron detection (Framework or bundle ID)
        if any("electron" in f for f in fw_lower) or any(
            k in bid_lower for k in ["electron", "vscode", "com.microsoft.vscode", "slack", "discord", "lark", "notion"]
        ):
            return "electron"

        # 2. Chromium detection (Framework or bundle ID)
        if any("chromium" in f or "google chrome" in f for f in fw_lower) or any(
            k in bid_lower for k in ["chrome", "chromium", "microsoft.edge", "arc", "brave"]
        ):
            return "chromium"

        # 3. Firefox / Gecko detection
        if any("xul" in f for f in fw_lower) or "firefox" in bid_lower or "torbrowser" in bid_lower:
            return "firefox"

        # 4. Standard Cocoa (AppKit / SwiftUI) vs Generic
        if app_path:
            path = Path(app_path).expanduser().resolve()
            if (path / "Contents" / "MacOS").is_dir() or (path / "Contents" / "Info.plist").is_file():
                return "cocoa"

        if bundle_id:
            return "cocoa"

        return "generic"

    @classmethod
    def analyze(
        cls,
        app_path: Path | str,
        app_info: AppInfo | None = None,
        entitlements: dict[str, Any] | None = None,
        frameworks: list[str] | None = None,
    ) -> ProbeResult:
        """Perform comprehensive inspection and determine clone strategy and recipe."""
        path = Path(app_path).expanduser().resolve()
        if app_info is None:
            app_info = AppInspector.inspect(path)
        if entitlements is None:
            entitlements = cls.inspect_entitlements(path)
        if frameworks is None:
            frameworks = cls.detect_frameworks(path)

        has_sandbox = bool(entitlements.get("com.apple.security.app-sandbox", False))
        if not has_sandbox and app_info.has_sandbox:
            has_sandbox = True

        app_type = cls.detect_app_type(path, bundle_id=app_info.bundle_id, frameworks=frameworks)

        # iOS/iPadOS app on Apple Silicon Mac detection
        if getattr(app_info, "is_ios_app", False):
            strategy = "hard_clone"
            strip_sandbox = False
            launch_args = []
            env_injection: dict[str, str] = {}
            reason = "iOS/iPadOS Wrapper application on Mac (not supported for cloning)."
        # Chromium / Electron detection
        elif app_type in ("chromium", "electron"):
            strategy = "soft_clone"
            strip_sandbox = False
            launch_args = ["--user-data-dir={{ATB_DATA_DIR}}"]
            env_injection = {}
            reason = "Chromium/Electron framework detected; supports --user-data-dir parameter."
        elif app_type == "firefox":
            strategy = "soft_clone"
            strip_sandbox = False
            launch_args = ["-profile", "{{ATB_DATA_DIR}}"]
            env_injection = {}
            reason = "Firefox/Gecko framework detected; supports -profile parameter."
        else:
            strategy = "hard_clone"
            strip_sandbox = has_sandbox
            launch_args = []
            env_injection = {
                "HOME": "{{ATB_DATA_DIR}}/Home",
                "TMPDIR": "{{ATB_DATA_DIR}}/Tmp",
            }
            reason = (
                f"Native macOS application ({'Sandboxed' if has_sandbox else 'Non-sandboxed'}); "
                f"requires binary wrapper hijack with HOME/TMPDIR isolation."
            )

        recipe = Recipe(
            bundle_id=app_info.bundle_id,
            app_name=app_info.app_name,
            strategy=strategy,  # type: ignore[arg-type]
            strip_sandbox=strip_sandbox,
            environment_injection=env_injection,
            launch_args=launch_args,
            app_type=app_type,
        )

        return ProbeResult(
            app_info=app_info,
            has_sandbox=has_sandbox,
            frameworks=frameworks,
            strategy=strategy,
            reason=reason,
            recipe=recipe,
            raw_entitlements=entitlements,
        )

    @classmethod
    def probe(cls, app_path: Path | str) -> Recipe:
        """Convenience method returning a dynamically generated Recipe."""
        return cls.analyze(app_path).recipe
