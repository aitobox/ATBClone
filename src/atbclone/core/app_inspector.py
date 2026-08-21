import plistlib
import re
import subprocess
from pathlib import Path

from .models import AppInfo


class AppInspector:
    @staticmethod
    def _run_cmd(cmd: list[str]) -> str:
        try:
            return subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True).strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return ""

    @classmethod
    def inspect(cls, app_path: str | Path) -> AppInfo:
        path = Path(app_path).expanduser().resolve()
        if not path.exists():
            raise FileNotFoundError(f"App not found: {app_path}")

        # Check bundle layout
        is_ios_app = False
        relative_plist_path = Path("Contents/Info.plist")
        relative_executable_path = Path("Contents/MacOS")
        relative_resources_path = Path("Contents/Resources")

        plist_path = path / "Contents" / "Info.plist"

        if not plist_path.exists():
            # Check iOS on Mac (Apple Silicon wrapper bundle)
            wrapper_dir = path / "Wrapper"
            wrapped_bundle = path / "WrappedBundle"
            if wrapped_bundle.exists() and (wrapped_bundle / "Info.plist").exists():
                is_ios_app = True
                try:
                    target_inner = wrapped_bundle.resolve().relative_to(path.resolve())
                    relative_plist_path = target_inner / "Info.plist"
                    relative_executable_path = target_inner
                    relative_resources_path = target_inner
                    plist_path = path / relative_plist_path
                except Exception:
                    is_ios_app = True
                    relative_plist_path = Path("WrappedBundle/Info.plist")
                    relative_executable_path = Path("WrappedBundle")
                    relative_resources_path = Path("WrappedBundle")
                    plist_path = path / relative_plist_path
            elif wrapper_dir.is_dir():
                inner_apps = list(wrapper_dir.glob("*.app"))
                if inner_apps:
                    is_ios_app = True
                    inner = inner_apps[0]
                    rel_inner = inner.relative_to(path)
                    relative_plist_path = rel_inner / "Info.plist"
                    relative_executable_path = rel_inner
                    relative_resources_path = rel_inner
                    plist_path = inner / "Info.plist"
            elif (path / "Info.plist").exists():
                relative_plist_path = Path("Info.plist")
                relative_executable_path = Path(".")
                relative_resources_path = Path(".")
                plist_path = path / "Info.plist"

        bundle_id = ""
        app_name = ""
        executable_name = ""

        if plist_path.exists():
            try:
                with open(plist_path, "rb") as f:
                    plist_data = plistlib.load(f)
                    bundle_id = plist_data.get("CFBundleIdentifier", "")
                    app_name = plist_data.get("CFBundleDisplayName") or plist_data.get("CFBundleName", "")
                    executable_name = plist_data.get("CFBundleExecutable", "")
            except (plistlib.InvalidFileException, OSError, ValueError):
                pass

        if not bundle_id:
            bundle_id = cls._run_cmd(["defaults", "read", str(plist_path), "CFBundleIdentifier"])
        if not app_name:
            app_name = cls._run_cmd(["defaults", "read", str(plist_path), "CFBundleName"]) or path.stem
        if not executable_name:
            executable_name = cls._run_cmd(["defaults", "read", str(plist_path), "CFBundleExecutable"]) or path.stem

        # Check sandbox entitlements
        entitlements = cls._run_cmd(["codesign", "-d", "--entitlements", "-", str(path)])
        has_sandbox = False
        if is_ios_app:
            has_sandbox = True
        elif "com.apple.security.app-sandbox" in entitlements:
            # Check for boolean true (either structured codesign format or XML format)
            if re.search(r"com\.apple\.security\.app-sandbox.*?(true|\[Bool\]\s*true)", entitlements, re.IGNORECASE | re.DOTALL):
                if not re.search(r"com\.apple\.security\.app-sandbox\s*\n\s*\[Value\]\s*\n\s*\[Bool\]\s*false", entitlements, re.IGNORECASE):
                    has_sandbox = True
            elif "<false/>" not in entitlements and "[Bool] false" not in entitlements:
                has_sandbox = True

        if is_ios_app:
            executable = path / relative_executable_path / executable_name
        else:
            executable = path / "Contents" / "MacOS" / executable_name

        return AppInfo(
            path=path,
            bundle_id=bundle_id,
            app_name=app_name,
            executable=executable,
            has_sandbox=has_sandbox,
            is_ios_app=is_ios_app,
            relative_plist_path=relative_plist_path,
            relative_executable_path=relative_executable_path,
            relative_resources_path=relative_resources_path,
        )

    @staticmethod
    def next_available_name(app_name: str, dest_dir: str | Path) -> tuple[str, int]:
        dest_path = Path(dest_dir)
        match = re.match(r"^(.*?)(\d+)$", app_name)
        if match:
            base_name = match.group(1)
            num = int(match.group(2))
        else:
            base_name = app_name
            num = 1

        n = max(2, num) if num > 1 else 2
        while True:
            candidate = dest_path / f"{base_name}{n}.app"
            if not candidate.exists():
                return f"{base_name}{n}", n
            n += 1

    @staticmethod
    def generate_bundle_id(bundle_id: str, num: int = 1) -> str:
        """Generate standardized bundle identifier for a cloned application instance."""
        return f"{bundle_id}.atbclone.{num}"

    @classmethod
    def resolve_bundle_id(
        cls,
        base_bundle_id: str,
        clone_name: str = "",
        existing_bundle_ids: set[str] | list[str] | None = None,
    ) -> str:
        """Generate a unique bundle identifier for a cloned application instance.

        If clone_name ends with digits (e.g. 'WeChat2', 'WeChat3'), attempts to use that number.
        Ensures uniqueness by avoiding collisions with existing_bundle_ids.
        """
        existing = set(existing_bundle_ids or [])
        num = 1
        match = re.search(r"(\d+)$", clone_name.strip())
        if match:
            try:
                num = int(match.group(1))
            except ValueError:
                num = 1

        candidate = cls.generate_bundle_id(base_bundle_id, num)
        while candidate in existing:
            num += 1
            candidate = cls.generate_bundle_id(base_bundle_id, num)
        return candidate

