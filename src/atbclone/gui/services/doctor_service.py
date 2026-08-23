import asyncio
from dataclasses import dataclass
from pathlib import Path
import shutil
import subprocess
import sys

from atbclone.core.i18n import t
from atbclone.core.logger import get_logger

logger = get_logger("gui.doctor_service")


@dataclass
class DoctorCheckItem:
    name: str
    passed: bool
    details: str
    hint: str = ""


class DoctorService:
    async def check_xcode_select_installed(self) -> bool:
        """Non-blocking defensive check for active Xcode Command Line Tools."""
        loop = asyncio.get_running_loop()

        def _check() -> bool:
            try:
                out = subprocess.check_output(
                    "xcode-select -p", shell=True, stderr=subprocess.STDOUT, text=True
                ).strip()
                return bool(out and (Path(out).exists() or out.startswith("/")))
            except Exception as e:
                logger.debug(f"xcode-select -p check failed: {e}")
                return False

        return await loop.run_in_executor(None, _check)

    async def trigger_xcode_install(self) -> tuple[bool, str]:
        """Trigger macOS native Xcode Command Line Tools installer dialog."""
        loop = asyncio.get_running_loop()

        def _install() -> tuple[bool, str]:
            logger.info("Triggering macOS native 'xcode-select --install' command")
            try:
                res = subprocess.run(
                    ["xcode-select", "--install"],
                    capture_output=True,
                    text=True,
                )
                stdout = (res.stdout or "").strip()
                stderr = (res.stderr or "").strip()
                combined = f"{stdout}\n{stderr}".lower()

                if res.returncode == 0 or "install requested" in combined:
                    logger.info("xcode-select --install successfully requested")
                    return True, "launched"
                if "already installed" in combined:
                    logger.info("xcode-select tools are already installed or in progress")
                    return True, "already_installed"
                err_msg = stderr or stdout or f"Return code {res.returncode}"
                logger.warning(f"xcode-select --install failed: {err_msg}")
                return False, err_msg
            except Exception as e:
                logger.error(f"Exception invoking xcode-select --install: {e}")
                return False, str(e)

        return await loop.run_in_executor(None, _install)

    async def check_environment(self) -> list[DoctorCheckItem]:
        loop = asyncio.get_running_loop()
        logger.info("Running GUI environment diagnostic checks")

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
                    hint=t("doctor_hint_xcode_select"),
                ))

            # 2. xcode-select
            try:
                out = subprocess.check_output("xcode-select -p", shell=True, stderr=subprocess.STDOUT, text=True).strip()
                if out and (Path(out).exists() or out.startswith("/")):
                    items.append(DoctorCheckItem(
                        name="xcode-select",
                        passed=True,
                        details=out,
                    ))
                else:
                    items.append(DoctorCheckItem(
                        name="xcode-select",
                        passed=False,
                        details=out or "Not found",
                        hint=t("doctor_hint_xcode_select"),
                    ))
            except Exception:
                items.append(DoctorCheckItem(
                    name="xcode-select",
                    passed=False,
                    details="Not found",
                    hint=t("doctor_hint_xcode_select"),
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

            passed_cnt = sum(1 for i in items if i.passed)
            total_cnt = len(items)
            logger.info(f"Environment diagnostic checks finished: {passed_cnt}/{total_cnt} passed")
            return items

        return await loop.run_in_executor(None, _checks)
