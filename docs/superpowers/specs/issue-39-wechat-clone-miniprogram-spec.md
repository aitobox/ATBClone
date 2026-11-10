# Specification: Issue #39 - WeChat Clone Mini Programs Runtime Fix

## 1. Background & Problem Statement

WeChat (`com.tencent.xinWeChat`) is an AppKit/Cocoa application, but it embeds Tencent's proprietary mini programs subsystem, `WeChatAppEx.app`, located at `Contents/MacOS/WeChatAppEx.app`. Inside `WeChatAppEx.app`, it embeds `WeChatAppEx Framework.framework`—a heavily customized Chromium Embedded Framework (CEF / WMPF) engine that orchestrates multiple helper applications (`WeChatAppEx Helper.app`, `WeChatAppEx Helper (GPU).app`, `WeChatAppEx Helper (Renderer).app`, `WeChatAppEx Helper (Plugin).app`, `WeApp.app`, etc.) under `Versions/C/Helpers/`.

When cloning WeChat using ATBClone's physical hard clone (`hard_clone`), users reported that mini programs completely fail to open (resulting in a blank white window or unclickable interface).

Root cause analysis revealed two core architectural defects:
1. **Process Aliasing Scope Violation**:
   In `HardCloneEngine._build_process_name_cmd`, executable binaries are renamed to match the clone name for network proxy (`PROCESS-NAME`) matching. ADR 0001 (`docs/adr/0001-process-aliasing-scope-and-helper-preservation.md`) mandated that auxiliary helper binaries and nested sub-applications must remain 100% untampered on disk. However, this preservation was conditioned solely on `is_chromium`. Because WeChat's recipe specifies `app_type: cocoa`, `is_chromium` evaluated to `False`. The engine traversed into `WeChatAppEx.app` and renamed `WeChatAppEx` to `WeChat2-WeChatAppEx`, and helpers to `WeChat2-WeChatAppEx Helper*`. Because `WeChatAppEx Framework` hardcodes the binary name `WeChatAppEx` and its helper paths, Chromium IPC and helper dispatch failed immediately (`posix_spawnp ... No such file or directory (2)`).
2. **AMFI Sandbox Inheritance Denial**:
   In `HardCloneEngine.execute`, when `strip_sandbox: true` is configured, codesigning stripped `com.apple.security.app-sandbox` from entitlements, but left `com.apple.security.inherit: true` intact. On macOS with Apple Mobile File Integrity (AMFI), if an application is launched by an unsandboxed, ad-hoc signed parent process, any child binary declaring `com.apple.security.inherit: true` is immediately killed by the kernel with SIGTRAP (`Returncode: -5`).
3. **Codesigning Hierarchy**:
   Nested helper applications within framework bundles must be codesigned from deepest to shallowest (inside-out) to guarantee valid code seals.

## 2. Architecture & Design

### 2.1 Multi-Layer Fingerprint Detection & Helper Preservation (`src/atbclone/core/engines.py`)

In `HardCloneEngine._build_process_name_cmd`:
- Expand `is_chromium` detection to recognize embedded CEF, WMPF, and WeChatAppEx architectures regardless of root `app_type`:
  - `Contents/**/WeChatAppEx*.framework`
  - `Contents/**/WeChatAppEx.app`
  - `Contents/**/WMPF*.framework`
  - `Contents/**/*Helper*.app` (recursive helper matching across any folder)
- Ensure that inside `_build_process_name_cmd`:
  - Any path that is inside a nested `.app` bundle (i.e. having any `.app` directory in its relative path under `Contents/`) is strictly exempt from binary renaming and Info.plist modifications.
  - When `is_chromium` or embedded helpers are detected, process renaming is strictly restricted to the root `main` binary and `entry` launcher.

### 2.2 Codesigning & Entitlements Stripping (`src/atbclone/core/engines.py`)

In `HardCloneEngine.execute`:
- When `task.recipe.strip_sandbox` is `True`:
  - Strip `com.apple.security.inherit` in addition to `com.apple.security.app-sandbox` using `PlistBuddy` and Python plist filtering.
  - Add `com.apple.security.inherit` to the `restricted` prefix/tuple in Python entitlements cleaner.
- Sign nested bundles in inside-out (reverse depth) order:
  - Sign dynamic libraries (`.dylib`, `.so`).
  - Sign nested `.app` and `.framework` bundles sorted by path length descending (deepest first), ensuring helpers inside `Versions/C/Helpers/` are signed before the enclosing framework.
  - Sign the outer parent application bundle.

## 3. Implementation Task List

- [x] Task 1: Enhance `_build_process_name_cmd` in `src/atbclone/core/engines.py` to detect `WeChatAppEx` / embedded CEF frameworks and preserve nested sub-apps from renaming.
- [x] Task 2: Update codesigning logic in `HardCloneEngine.execute` to strip `com.apple.security.inherit` when `strip_sandbox: true`, and enforce inside-out reverse-depth signing.
- [x] Task 3: Add comprehensive regression tests in `tests/test_process_names.py` verifying preservation of WeChat mini program runtime (`WeChatAppEx.app`) and nested helpers.
- [x] Task 4: Run full project test suite (`PYTHONPATH=src conda run -n ATBClone python -m pytest tests/`) to ensure 100% pass with zero regressions.
- [x] Task 5: Perform stress-test audit via `grill-me` before transitioning to code review.
