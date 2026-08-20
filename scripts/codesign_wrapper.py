#!/usr/bin/env python3
"""Codesign Wrapper with Exponential Backoff Retry for Timestamp Server Failures.

Intercepts calls to `codesign` and automatically retries with exponential backoff
(2s, 4s, 8s, 16s, 32s, up to 60s) when Apple's timestamp service is temporarily
unavailable or encounters network timeouts.
"""

import subprocess
import sys
import time

REAL_CODESIGN = "/usr/bin/codesign"
BACKOFF_DELAYS = [2, 4, 8, 16, 32, 60]


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


def main():
    args = sys.argv[1:]
    cmd = [REAL_CODESIGN] + args

    for attempt, delay in enumerate(BACKOFF_DELAYS):
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if res.returncode == 0:
            if res.stdout:
                sys.stdout.buffer.write(res.stdout)
            if res.stderr:
                sys.stderr.buffer.write(res.stderr)
            sys.exit(0)

        err_str = res.stderr.decode("utf-8", errors="replace")
        if is_retryable_error(err_str):
            target_name = args[0] if args else "file"
            # Extract cleaner filename if possible
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
