"""Doctor Service for environment diagnostic checks."""

import asyncio
from dataclasses import dataclass
import shutil
import subprocess
import sys


@dataclass
class DoctorCheckItem:
    name: str
    passed: bool
    details: str
    hint: str = ""


class DoctorService:
    async def check_environment(self) -> list[DoctorCheckItem]:
        loop = asyncio.get_running_loop()

        def _checks():
            items = []

            # 1. codesign
            codesign_path = shutil.which("codesign")
            if codesign_path:
                items.append(DoctorCheckItem(
                    name="codesign",
                    passed=True,
                    details=codesign_path,
                ))
            else:
                items.append(DoctorCheckItem(
                    name="codesign",
                    passed=False,
                    details="Not found",
                    hint="Install Xcode Command Line Tools: xcode-select --install",
                ))

            # 2. xcode-select
            try:
                out = subprocess.check_output("xcode-select -p", shell=True, stderr=subprocess.STDOUT, text=True).strip()
                items.append(DoctorCheckItem(
                    name="xcode-select",
                    passed=True,
                    details=out,
                ))
            except Exception:
                items.append(DoctorCheckItem(
                    name="xcode-select",
                    passed=False,
                    details="Not found",
                    hint="Run: xcode-select --install",
                ))

            # 3. PlistBuddy
            plistbuddy = "/usr/libexec/PlistBuddy"
            if shutil.which(plistbuddy) or Path(plistbuddy).exists():
                items.append(DoctorCheckItem(
                    name="PlistBuddy",
                    passed=True,
                    details=plistbuddy,
                ))
            else:
                items.append(DoctorCheckItem(
                    name="PlistBuddy",
                    passed=False,
                    details="Not found in /usr/libexec/PlistBuddy",
                    hint="Standard macOS system utility missing",
                ))

            # 4. Python version
            py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            if sys.version_info >= (3, 10):
                items.append(DoctorCheckItem(
                    name="Python",
                    passed=True,
                    details=f"Python {py_ver}",
                ))
            else:
                items.append(DoctorCheckItem(
                    name="Python",
                    passed=False,
                    details=f"Python {py_ver} (requires >= 3.10)",
                    hint="Upgrade your Python installation",
                ))

            return items

        from pathlib import Path
        return await loop.run_in_executor(None, _checks)
