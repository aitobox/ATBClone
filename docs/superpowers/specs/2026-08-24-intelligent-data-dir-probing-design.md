# Design Spec: Intelligent Data Directory Probing & Launch Argument Filtering

- **Date**: 2026-08-24
- **Status**: Approved
- **Target**: `src/atbclone/core/app_prober.py`, `src/atbclone/core/argument_prober.py`, `src/atbclone/core/engines.py`, `src/atbclone/cli/`, `src/atbclone/gui/`

---

## 1. Background & Problem Statement

ATBClone currently determines data directory isolation based on preset recipes (e.g. for Chromium / Electron / Firefox) and general framework detection:
1. Known frameworks like Chromium / Electron inject `--user-data-dir={{ATB_DATA_DIR}}`.
2. Firefox / Gecko injects `-profile {{ATB_DATA_DIR}}`.
3. Standard native Cocoa apps isolate data through `HOME` and `TMPDIR` environment variables.

However, when encountering **unknown applications**:
- The application might support a custom CLI argument for user data directory (e.g., `--data-dir`, `--datadir`, `--profile`, `--config-dir`, `--storage-path`, etc.) that is not currently detected.
- If a recipe (built-in or user-configured) specifies a CLI launch argument (e.g., `--user-data-dir`) that the target application binary does not actually support, passing it blindly can cause the application to crash on startup with unrecognized argument errors.

---

## 2. Goals & Key Requirements

1. **Intelligent Static Binary Probing**:
   - For unknown / generic applications, inspect the executable binary (Mach-O strings / symbols) to detect if it supports custom data directory CLI arguments.
   - Detect argument format (`=` vs whitespace separated).
2. **Launch Argument Validation & Pruning**:
   - Validate all `launch_args` in recipes against framework whitelists and binary static string fingerprints before generating clone wrapper scripts.
   - **Prune/remove any unsupported launch arguments** so the application will not receive invalid flags.
3. **Graceful Degradation to Environment Isolation**:
   - If an application does not support any CLI data directory arguments (or if invalid arguments are pruned), automatically fall back to `HOME`/`TMPDIR` environment variable isolation under `HardCloneEngine`.

---

## 3. Architecture & Detailed Design

```
┌─────────────────────────────────────────────────────────────┐
│                       AppProber                             │
│ ┌──────────────────────┐   ┌──────────────────────────────┐ │
│ │ 1. Framework Prober  │──>│ 2. Binary Argument Prober    │ │
│ │ (Chromium/Electron/  │   │ (Mach-O Strings Scanner      │ │
│ │  Gecko/JVM/Qt/etc.)  │   │  & Pattern Matcher)          │ │
│ └──────────────────────┘   └──────────────────────────────┘ │
│                                            │                │
│                                            ▼                │
│                            ┌──────────────────────────────┐ │
│                            │ 3. Strategy & Isolation Decider│ │
│                            │ (CLI Flag vs HOME/TMPDIR)    │ │
│                            └──────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                                             │
                                             ▼
┌─────────────────────────────────────────────────────────────┐
│              Launch Argument Validator & Filter             │
│ (Prunes unsupported arguments before generating wrapper)    │
└─────────────────────────────────────────────────────────────┘
                                             │
                                             ▼
┌─────────────────────────────────────────────────────────────┐
│                 CloneEngines (Soft & Hard)                  │
│ (Injects validated launch_args & environment variables)     │
└─────────────────────────────────────────────────────────────┘
```

### 3.1. `BinaryArgumentProber`

Located at `src/atbclone/core/argument_prober.py`:

- **Static String Extraction**:
  - Extracts printable ASCII/UTF-8 character sequences (length >= 3) from the target executable binary.
  - Caches/pools strings for fast multi-pattern matching.
- **Candidate Data Directory Patterns (Priority Order)**:
  1. `user-data-dir` (`--user-data-dir={{ATB_DATA_DIR}}`)
  2. `data-dir` / `datadir` (`--data-dir={{ATB_DATA_DIR}}` or `--datadir={{ATB_DATA_DIR}}`)
  3. `profile` / `profile-dir` / `profile-directory` (`-profile {{ATB_DATA_DIR}}` or `--profile={{ATB_DATA_DIR}}`)
  4. `config-dir` / `config-path` (`--config-dir={{ATB_DATA_DIR}}`)
  5. `storage-path` / `app-data` (`--storage-path={{ATB_DATA_DIR}}`)
  6. `idea.config.path` (`-Didea.config.path={{ATB_DATA_DIR}}/config`)
- **Syntax Deduction**:
  - Check if binary contains `<flag>=` or `<flag> <path>`.
  - Format candidate parameter accordingly with placeholder `{{ATB_DATA_DIR}}`.

### 3.2. `LaunchArgumentValidator`

Located at `src/atbclone/core/argument_prober.py`:

- **Framework Whitelist**:
  - `chromium` / `electron`: `--user-data-dir`, `--lang`, `--disk-cache-dir`, `--profile-directory`, `--no-sandbox`, `--disable-gpu`, etc.
  - `firefox`: `-profile`, `-P`, `-no-remote`, etc.
  - `cocoa`: `-AppleLanguages`, `-AppleLocale`, `-NSDocumentRevisionsDebugMode`, etc.
- **Custom / Unknown Flag Inspection**:
  - Extract the core flag identifier (e.g., `--custom-flag=/path` -> `custom-flag`).
  - Scan the executable binary's string pool.
  - If the flag identifier is present in the binary, keep the argument.
  - If the flag identifier is NOT found in the binary, **prune/strip the argument**.
  - Log warning with pruned argument details.

### 3.3. Engine Integration (`CloneEngines`)

In `src/atbclone/core/engines.py`:
- `SoftCloneEngine.execute()` & `HardCloneEngine.execute()`:
  - Run `LaunchArgumentValidator.validate_and_filter(executable, recipe.launch_args, app_type)` before formatting wrapper arguments.
  - If all data directory arguments are pruned for a native application and no environment injection is configured:
    - Under `HardCloneEngine`, automatically ensure `HOME` and `TMPDIR` isolation is active.

---

## 4. Error Handling & Edge Cases

1. **Non-readable or Protected Binaries**:
   - If binary cannot be read or strings extraction fails, safely fall back to framework detection and environment variable isolation.
2. **Universal Fat Binaries (ARM64 + x86_64)**:
   - Scanning strings in raw binary format works seamlessly across single and fat binaries.
3. **Compound Arguments & Positional Arguments**:
   - For multi-token arguments like `-profile /path/to/dir`, the validator preserves both the flag and its immediate value token if the flag is supported.
4. **App Types with Special Needs**:
   - Sandboxed apps stripped of sandbox under `HardCloneEngine` will receive appropriate environment overrides.

---

## 5. Verification Plan

1. **Unit Tests**:
   - `tests/test_argument_prober.py`:
     - Test Mach-O string extraction and candidate pattern matching for various mock binaries.
     - Test syntax deduction (`=` vs whitespace).
     - Test fallback when no CLI parameters are present.
   - `tests/test_argument_validator.py`:
     - Test framework whitelist passing.
     - Test custom flag validation against binary strings.
     - Test pruning of unsupported arguments.
     - Test argument preservation for supported custom flags.
2. **Integration Tests**:
   - `tests/test_engines.py`:
     - Test that `SoftCloneEngine` and `HardCloneEngine` filter out invalid args when building wrapper scripts.
     - Test that fallback `HOME`/`TMPDIR` is maintained when data-dir args are pruned.
   - `tests/test_app_prober.py`:
     - Test `AppProber.analyze()` on simulated unknown apps with various CLI flags.
3. **Regression Test**:
   - Run full pytest test suite (`PYTHONPATH=src conda run -n ATBClone python -m pytest tests/`) to ensure all 390+ tests pass.
