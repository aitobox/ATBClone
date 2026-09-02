#!/usr/bin/env python3
"""Codesign Wrapper with Exponential Backoff Retry and Detritus Auto-Clean.

1. Intercepts calls to `codesign` and automatically cleans extended attributes (xattrs)
   and AppleDouble/FinderInfo detritus if codesign fails with "detritus not allowed".
2. Retries with exponential backoff (2s, 4s, 8s, 16s, 32s, up to 60s) when Apple's
   timestamp service is temporarily unavailable or encounters network timeouts.
"""

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

REAL_CODESIGN = "/usr/bin/codesign"
BACKOFF_DELAYS = [2, 4, 8, 16, 32, 60]


def is_detritus_error(stderr_text: str) -> bool:
    keywords = [
        "detritus not allowed",
        "resource fork",
        "finder information",
    ]
    lower = stderr_text.lower()
    return any(k in lower for k in keywords)


def clean_target_detritus(target: str) -> bool:
    """Strip extended attributes, .DS_Store, and AppleDouble files on target path."""
    p = Path(target)
    if not p.exists():
        return False
    try:
        # Run xattr -cr
        subprocess.run(["xattr", "-cr", str(p)], capture_output=True, check=False)
        # Run dot_clean if on macOS
        if shutil.which("dot_clean"):
            subprocess.run(["dot_clean", "-m", str(p)], capture_output=True, check=False)
        # If directory, recursively remove .DS_Store and ._* files
        if p.is_dir():
            for item in p.rglob(".DS_Store"):
                try:
                    item.unlink()
                except OSError:
                    pass
            for item in p.rglob("._*"):
                try:
                    item.unlink()
                except OSError:
                    pass
        return True
    except Exception:
        return False


def is_retryable_error(stderr_text: str) -> bool:
    keywords = [
        "timestamp service is not available",
        "timestamp service",
        "the timestamp service",
        "timed out",
        "network is unreachable",
        "connection reset",
        "could not connect",
        "resource temporarily unavailable",
        "operation timed out",
    ]
    lower = stderr_text.lower()
    return any(k in lower for k in keywords)


def extract_targets(args: list[str]) -> list[str]:
    targets = []
    skip_next = False
    for arg in args:
        if skip_next:
            skip_next = False
            continue
        if arg in ("-s", "--sign", "-i", "--identifier", "-r", "--requirement", "--entitlements", "--prefix", "--keychain"):
            skip_next = True
            continue
        if arg.startswith("-"):
            continue
        targets.append(arg)
    return targets


def main():
    args = sys.argv[1:]
    cmd = [REAL_CODESIGN] + args

    detritus_cleaned = False

    for attempt, delay in enumerate(BACKOFF_DELAYS):
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if res.returncode == 0:
            if res.stdout:
                sys.stdout.buffer.write(res.stdout)
            if res.stderr:
                sys.stderr.buffer.write(res.stderr)
            sys.exit(0)

        err_str = res.stderr.decode("utf-8", errors="replace")

        # Check for detritus / resource fork error and auto-clean
        if not detritus_cleaned and is_detritus_error(err_str):
            targets = extract_targets(args)
            if targets:
                for tgt in targets:
                    clean_target_detritus(tgt)
                print(
                    f"[codesign-retry] 🧹 Cleared extended attributes & detritus for {targets}. Retrying codesign...",
                    file=sys.stderr,
                    flush=True,
                )
                detritus_cleaned = True
                continue

        if is_retryable_error(err_str):
            target_name = args[0] if args else "file"
            for arg in args:
                if not arg.startswith("-") and ("." in arg or "/" in arg):
                    target_name = arg.rsplit("/", 1)[-1]
                    break

            print(
                f"[codesign-retry] ⚠️ Timestamp service unavailable for '{target_name}'. "
                f"Retrying in {delay}s (attempt {attempt + 1}/{len(BACKOFF_DELAYS)})...",
                file=sys.stderr,
                flush=True,
            )
            time.sleep(delay)
            continue
        else:
            # Non-retryable error (syntax, unsupported format, etc.)
            sys.stdout.buffer.write(res.stdout)
            sys.stderr.buffer.write(res.stderr)
            sys.exit(res.returncode)

    # Final attempt after all backoffs
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    sys.stdout.buffer.write(res.stdout)
    sys.stderr.buffer.write(res.stderr)
    sys.exit(res.returncode)


if __name__ == "__main__":
    main()
