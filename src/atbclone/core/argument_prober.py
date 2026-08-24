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

    @staticmethod
    def extract_binary_strings(
        binary_path: Path | str,
        min_len: int = 3,
        max_bytes: int = 15_000_000,
    ) -> set[str]:
        """Extract printable ASCII strings from a binary executable file."""
        path = Path(binary_path).expanduser().resolve()
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
