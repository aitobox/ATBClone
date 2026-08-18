# ATBClone CLI Design Specification

## Overview
ATBClone is a macOS native application cloning and sandbox isolation engine. This document specifies the design for the initial CLI version, written in Python, based on the ATBClone architecture. It implements both Soft Clone (symlink/launcher) and Hard Clone (physical copy + wrapper hijack + resign) strategies, driven by a Recipe rule engine.

## Architecture
We use a layered modular package design (`src/atbclone/`).

```text
ATBClone/
├── src/atbclone/
│   ├── cli/             # Click-based CLI commands (clone, list, recipe, wizard, doctor)
│   ├── core/            # Business logic (inspector, clone engines, code signer, env checker)
│   ├── recipes/         # Recipe loading, Pydantic models, builtin YAMLs
│   └── executor/        # Shell script generation and execution (osascript for privilege escalation)
```

## CLI Interface (Click-based)
- `atbclone clone <app_path> [options]` - Core command. Auto-matches recipes. Options for name, mode, proxy, output-dir.
- `atbclone list`, `atbclone remove`, `atbclone update` - Manage clones.
- `atbclone recipe <list|show|export|import>` - Manage YAML rules.
- `atbclone wizard` - Interactive terminal UI for guided cloning.
- `atbclone doctor` - Environment checks (xcode-select, codesign).

## Clone Engines
### Soft Clone
For apps supporting data dir flags (Chrome, Edge, VS Code).
Creates a lightweight `.app` wrapper in the target directory containing a bash script that launches the original binary with `--user-data-dir` (or equivalent) pointing to an isolated directory.

### Hard Clone
For standard macOS apps (WeChat, Telegram).
1. Physical copy of the app.
2. Modify `CFBundleIdentifier` and `CFBundleName`.
3. Wrapper Hijack: Rename original binary, insert bash wrapper to inject env vars (`HOME`, `TMPDIR`, `HTTP_PROXY`, etc.).
4. Sandbox Stripping: If app is sandboxed, remove `com.apple.security.app-sandbox` from entitlements.
5. Clear quarantine attributes (`xattr -cr`).
6. Ad-Hoc Resign: `codesign --force --deep --sign -`.

Execution Strategy: The `executor` module generates a single shell script for the hard clone process (with `set -e` for atomicity). If writing to a system directory like `/Applications`, it executes via a single `osascript` prompt to request admin privileges once. Target directories like `~/Applications` do not require privilege escalation.

## Recipe Engine
Defined via YAML and validated with Pydantic. Supports `hard_clone` and `soft_clone` strategies.
Includes environment variable injection, symlink whitelists, launch args, and proxy configuration.
A safety guard forces `soft_clone` for Chromium-based bundles.

**Builtin Recipes:**
- **Hard Clone:** WeChat, QQ, Telegram, LINE (strip sandbox), Slack, Discord, Skype (strip sandbox), ChatGPT (Codex) (strip sandbox), Antigravity, Antigravity IDE, Gemini (strip sandbox)
- **Soft Clone:** Chrome, Edge, Firefox, Arc, Cursor, Windsurf, Trae, VS Code, Zed

## Proxy Support
First-class support for injecting HTTP/SOCKS5 proxies per clone via the wrapper script (`HTTP_PROXY`, `HTTPS_PROXY`, `NO_PROXY`, etc.). Fully effective for Electron and CLI tools inside the clone.

## Error Handling & Packaging
- Atomic operations: If any step fails, the partially created clone is removed to avoid orphaned bundles.
- `atbclone doctor` runs implicitly to ensure Xcode CLT (`codesign`, `PlistBuddy`) is available.
- Distributed as a Python package (`pipx install atbclone`) using `pyproject.toml`.
- Uses `rich` for elegant terminal UI formatting (progress bars, tables, colors).
