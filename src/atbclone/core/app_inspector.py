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
        path = Path(app_path)
        if not path.exists():
            raise FileNotFoundError(f"App not found: {app_path}")

        plist_path = path / "Contents" / "Info.plist"
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
        if "com.apple.security.app-sandbox" in entitlements:
            # Check for boolean true (either structured codesign format or XML format)
            if re.search(r"com\.apple\.security\.app-sandbox.*?(true|\[Bool\]\s*true)", entitlements, re.IGNORECASE | re.DOTALL):
                if not re.search(r"com\.apple\.security\.app-sandbox\s*\n\s*\[Value\]\s*\n\s*\[Bool\]\s*false", entitlements, re.IGNORECASE):
                    has_sandbox = True
            elif "<false/>" not in entitlements and "[Bool] false" not in entitlements:
                has_sandbox = True

        executable = path / "Contents" / "MacOS" / executable_name

        return AppInfo(
            path=path,
            bundle_id=bundle_id,
            app_name=app_name,
            executable=executable,
            has_sandbox=has_sandbox,
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
