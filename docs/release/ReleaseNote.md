[English](ReleaseNote.md) | [简体中文](ReleaseNote_zh.md) | [繁體中文](ReleaseNote_zh_TW.md) | [日本語](ReleaseNote_ja.md) | [한국어](ReleaseNote_ko.md) | [Deutsch](ReleaseNote_de.md) | [Français](ReleaseNote_fr.md) | [Русский](ReleaseNote_ru.md) | [Español](ReleaseNote_es.md)

# ATBClone Release Notes

All notable changes, new features, improvements, and bug fixes for **ATBClone** are documented in this file.

---

## [v0.3.0] - 2026-08-19

### 🌐 Internationalization & Multilingual Support
- **Automatic macOS System Language Detection**:
  - Integrated `atbclone.core.i18n` engine that automatically detects macOS system UI language preferences via `AppleLanguages` and `AppleLocale`.
  - Seamlessly switches CLI interactive wizards, prompts, table headers, and error logs between English and Chinese.
  - Added `ATBCLONE_LANG` environment variable override (`ATBCLONE_LANG=en` / `ATBCLONE_LANG=zh`) for manual language switching.
- **Multilingual Documentation**:
  - Standardized English as default `Readme.md` with full Chinese translation in `Readme_zh.md`.
  - Comprehensive Release Notes across 9 languages: English, Simplified Chinese, Traditional Chinese, Japanese, Korean, German, French, Russian, and Spanish.

### 🛠️ CLI & Build Improvements
- **Interactive Wizard i18n**: Fully translated `atbclone wizard` interactive prompts, display name customizations, custom icon pickers, and proxy configurations.
- **Standalone Binary**: Rebuilt `./dist/ATBCloneCli` using Nuitka with embedded multilingual resources and sandbox compatibility (`PYTHONNOUSERSITE=1`).
- **Comprehensive Test Suite**: Added `test_i18n.py` and upgraded all 186 unit tests to support bilingual assertions across test environments.

---

## [v0.2.0] - 2026-08-18

### 🚀 Major Features
- **Interactive Cloning Wizard (`atbclone wizard`)**:
  - Step-by-step CLI terminal guide with support for dragging and dropping `.app` paths.
  - Automatic clone name incrementing (e.g., `WeChat2`, `WeChat3`).
  - Support for custom application display names and custom `.icns` application icons.
  - Interactive network proxy setup (HTTP & SOCKS5) with authentication support.
- **Intelligent Deep App Prober (`atbclone probe`)**:
  - Automatically inspects Mach-O architectures (arm64, x86_64, Universal), frameworks (Electron, Flutter, Chromium, Qt, Cocoa), and code signing sandbox entitlements (`com.apple.security.app-sandbox`).
  - Dynamically determines the optimal cloning strategy (`hard_clone` vs `soft_clone`) for unlisted applications and outputs recommended Recipe YAMLs.
  - Integrated automatic fallback to prober in `atbclone clone` when no built-in recipe exists.
- **Standalone Binary Packaging**:
  - Added `scripts/build_cli.sh` to compile a zero-dependency, single-file native macOS arm64 binary (`dist/ATBCloneCli`) via Nuitka.

### ⚡ Improvements & Fixes
- Enhanced privilege elevation using native single-prompt macOS `osascript` authorization for `/Applications` output paths.
- Improved command line path escaping with `shlex.quote` to protect against spaces and special characters.

---

## [v0.1.0] - 2026-08-17

### 🌟 Initial Release
- **Dual-Engine Cloning Mechanism**:
  - **Hard Clone Engine**: Full App Bundle duplication, `Info.plist` modification, `HOME` / `TMPDIR` data directory isolation, optional App Sandbox stripping, and ad-hoc code re-signing.
  - **Soft Clone Engine**: Lightweight launcher wrapper for Chromium browsers and code editors with automated `--user-data-dir` and proxy injection.
- **18+ Built-in Recipes**:
  - Instant Messaging: WeChat, QQ, Telegram, LINE, Slack, Discord, Skype.
  - AI Clients: ChatGPT (Codex), Gemini, Antigravity, Antigravity IDE.
  - Browsers & Editors: Google Chrome, Microsoft Edge, Firefox, Arc, Cursor, VS Code, Zed.
- **CLI Commands**:
  - `clone`: Clone applications with optional custom names, directories, and proxies.
  - `list`: View all active clones with creation time, strategy, and proxy status in Rich tables.
  - `update`: Synchronize clones after main app updates while preserving user data.
  - `remove`: Delete clones with optional data directory purging.
  - `recipe`: List built-in recipes and inspect local recipe overrides.
  - `doctor`: Automated environment self-checks (`codesign`, `xcode-select`, `PlistBuddy`).
