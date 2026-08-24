"""Intelligent Mach-O binary argument probing and launch argument validation."""

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any

from atbclone.core.logger import get_logger

logger = get_logger("core.argument_prober")


@dataclass
class ArgumentProbeResult:
    flag: str | None = None
    template: str | None = None
    syntax: str = "equals"  # "equals" or "space"
    reason: str = ""


class BinaryArgumentProber:
    """Probes Mach-O binary strings to detect custom data directory CLI arguments."""

    # Candidate data directory patterns in priority order
    CANDIDATE_PATTERNS: list[tuple[str, str, str]] = [
        # (flag_token, default_template, syntax_style)
        ("--user-data-dir", "--user-data-dir={{ATB_DATA_DIR}}", "equals"),
        ("--data-dir", "--data-dir={{ATB_DATA_DIR}}", "equals"),
        ("--datadir", "--datadir={{ATB_DATA_DIR}}", "equals"),
        ("--profile-directory", "--profile-directory={{ATB_DATA_DIR}}", "equals"),
        ("-profile", "-profile {{ATB_DATA_DIR}}", "space"),
        ("--profile", "--profile={{ATB_DATA_DIR}}", "equals"),
        ("--config-dir", "--config-dir={{ATB_DATA_DIR}}", "equals"),
        ("--config-path", "--config-path={{ATB_DATA_DIR}}", "equals"),
        ("--storage-path", "--storage-path={{ATB_DATA_DIR}}", "equals"),
        ("--app-data", "--app-data={{ATB_DATA_DIR}}", "equals"),
        ("-Didea.config.path", "-Didea.config.path={{ATB_DATA_DIR}}/config", "equals"),
    ]

    @classmethod
    def resolve_executable_path(cls, target_path: Path | str) -> Path:
        """Resolve a path (which may be a .app directory or a direct binary) to the executable Mach-O binary."""
        path = Path(target_path).expanduser().resolve()
        if path.is_dir():
            plist_path = path / "Contents" / "Info.plist"
            if plist_path.is_file():
                try:
                    import plistlib

                    with plist_path.open("rb") as f:
                        plist_data = plistlib.load(f)
                    exe_name = plist_data.get("CFBundleExecutable")
                    if exe_name:
                        candidate = path / "Contents" / "MacOS" / exe_name
                        if candidate.is_file():
                            return candidate
                except Exception:
                    pass
            macos_dir = path / "Contents" / "MacOS"
            if macos_dir.is_dir():
                for c in macos_dir.iterdir():
                    if c.is_file() and not c.name.startswith(".") and not c.name.endswith(".bin"):
                        return c
        return path

    @classmethod
    def extract_binary_strings(
        cls,
        binary_path: Path | str,
        min_len: int = 3,
        max_bytes: int = 15_000_000,
    ) -> set[str]:
        """Extract printable ASCII strings from a binary executable file."""
        path = cls.resolve_executable_path(binary_path)
        if not path.is_file():
            return set()

        pattern = re.compile(rb"[\x20-\x7E]{" + str(min_len).encode() + rb",}")
        strings: set[str] = set()

        try:
            with open(path, "rb") as f:
                data = f.read(max_bytes)
                for match in pattern.finditer(data):
                    try:
                        strings.add(match.group(0).decode("ascii"))
                    except UnicodeDecodeError:
                        pass
        except (OSError, PermissionError) as e:
            logger.warning(f"Failed to read binary strings from '{path}': {e}")

        return strings

    @classmethod
    def probe_data_dir_argument(cls, binary_path: Path | str) -> ArgumentProbeResult:
        """Inspect binary to find candidate data directory arguments."""
        path = Path(binary_path).expanduser().resolve()
        if not path.is_file():
            return ArgumentProbeResult(reason="Binary file not found.")

        strings = cls.extract_binary_strings(path)
        if not strings:
            return ArgumentProbeResult(reason="No printable strings extracted from binary.")

        # Match candidates in priority order
        for flag, template, syntax in cls.CANDIDATE_PATTERNS:
            # Check if flag exists in any extracted string
            flag_token = flag.lstrip("-")
            for s in strings:
                if flag in s or (flag_token in s and (f"--{flag_token}" in s or f"-{flag_token}" in s)):
                    reason = f"Detected CLI data directory parameter '{flag}' via binary static analysis."
                    logger.info(f"Probed argument for '{path.name}': {flag} ({reason})")
                    return ArgumentProbeResult(
                        flag=flag,
                        template=template,
                        syntax=syntax,
                        reason=reason,
                    )

        return ArgumentProbeResult(
            reason="No custom data directory CLI argument detected. Degraded to HOME/TMPDIR environment isolation.",
        )


class LaunchArgumentValidator:
    """Validates and filters launch arguments against framework whitelists and binary capabilities."""

    FRAMEWORK_WHITELISTS: dict[str, set[str]] = {
        "chromium": {
            "--user-data-dir",
            "--no-first-run",
            "--no-default-browser-check",
            "--lang",
            "--disk-cache-dir",
            "--profile-directory",
            "--no-sandbox",
            "--disable-gpu",
            "--enable-features",
            "--disable-features",
            "--remote-debugging-port",
            "--app",
            "--incognito",
            "--guest",
        },
        "electron": {
            "--user-data-dir",
            "--no-first-run",
            "--no-default-browser-check",
            "--lang",
            "--disk-cache-dir",
            "--profile-directory",
            "--no-sandbox",
            "--disable-gpu",
            "--enable-features",
            "--disable-features",
            "--remote-debugging-port",
            "--app",
            "--incognito",
            "--guest",
        },
        "firefox": {
            "-profile",
            "--profile",
            "-P",
            "-no-remote",
            "-headless",
            "-private",
            "-new-instance",
            "-new-window",
            "-new-tab",
        },
        "cocoa": {
            "-AppleLanguages",
            "-AppleLocale",
            "-NSDocumentRevisionsDebugMode",
        },
    }

    # System-level arguments accepted by almost all macOS Cocoa runtimes
    UNIVERSAL_SYSTEM_FLAGS: set[str] = {
        "-AppleLanguages",
        "-AppleLocale",
        "-NSDocumentRevisionsDebugMode",
    }

    @classmethod
    def _extract_flag_name(cls, arg: str) -> str:
        """Extract the base flag from an argument (e.g. '--data-dir=/tmp' -> '--data-dir')."""
        if arg.startswith("--"):
            return arg.split("=")[0]
        elif arg.startswith("-D"):
            return arg.split("=")[0]
        elif arg.startswith("-"):
            return arg.split("=")[0]
        return arg

    @classmethod
    def validate_and_filter(
        cls,
        binary_path: Path | str,
        launch_args: list[str],
        app_type: str | None = None,
    ) -> tuple[list[str], list[str]]:
        """Validate launch arguments and prune any unsupported flags.

        Returns:
            tuple[list[str], list[str]]: (validated_args, pruned_args)
        """
        if not launch_args:
            return [], []

        app_type_norm = (app_type or "generic").lower()
        fw_whitelist = cls.FRAMEWORK_WHITELISTS.get(app_type_norm, set())

        # Extract binary strings if needed for unknown flags
        binary_strings: set[str] | None = None
        path = Path(binary_path).expanduser().resolve()

        validated: list[str] = []
        pruned: list[str] = []

        i = 0
        while i < len(launch_args):
            arg = launch_args[i]
            flag = cls._extract_flag_name(arg)

            # 1. Universal macOS flags
            if flag in cls.UNIVERSAL_SYSTEM_FLAGS:
                validated.append(arg)
                # Check if this flag expects a following value argument (e.g. -AppleLanguages '("zh-Hans")')
                if i + 1 < len(launch_args) and not launch_args[i + 1].startswith("-"):
                    validated.append(launch_args[i + 1])
                    i += 1
                i += 1
                continue

            # 2. Known framework whitelist flags
            if flag in fw_whitelist or any(arg.startswith(f"{w}=") or arg == w for w in fw_whitelist):
                validated.append(arg)
                # If flag is separated like "-profile" "/path"
                if i + 1 < len(launch_args) and not launch_args[i + 1].startswith("-") and flag in {"-profile", "-P"}:
                    validated.append(launch_args[i + 1])
                    i += 1
                i += 1
                continue

            # 3. If app_type is a known framework (chromium/electron/firefox) and flag starts with standard prefix, check whitelist
            # For custom/unknown apps or custom flags: check binary strings
            if binary_strings is None:
                binary_strings = BinaryArgumentProber.extract_binary_strings(path)

            flag_token = flag.lstrip("-")
            is_supported = False
            if binary_strings:
                # Check if flag exists in binary strings
                for s in binary_strings:
                    if flag in s or (flag_token and flag_token in s and (f"--{flag_token}" in s or f"-{flag_token}" in s)):
                        is_supported = True
                        break

            if is_supported:
                validated.append(arg)
                if i + 1 < len(launch_args) and not launch_args[i + 1].startswith("-") and not "=" in arg:
                    validated.append(launch_args[i + 1])
                    i += 1
            else:
                logger.warning(
                    f"Pruned unsupported launch argument '{arg}' for executable '{path.name}' (app_type='{app_type_norm}')"
                )
                pruned.append(arg)
                # If next token was an argument value for this unsupported flag, skip it as well
                if i + 1 < len(launch_args) and not launch_args[i + 1].startswith("-") and not "=" in arg:
                    i += 1

            i += 1

        return validated, pruned

