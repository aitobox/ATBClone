[English](ReleaseNote.md) | [简体中文](ReleaseNote_zh.md) | [繁體中文](ReleaseNote_zh_TW.md) | [日本語](ReleaseNote_ja.md) | [한국어](ReleaseNote_ko.md) | [Deutsch](ReleaseNote_de.md) | [Français](ReleaseNote_fr.md) | [Русский](ReleaseNote_ru.md) | [Español](ReleaseNote_es.md)

# ATBClone Release Notes

All notable changes, new features, improvements, and bug fixes for **ATBClone** are documented in this file.

---

## [v0.9.1] - 2026-08-21

### 🛡️ iOS-on-Mac Wrapper Application Detection & Safe Rejection
- **Graceful Unsupported Architecture Handling**:
  - Enhanced `AppProber`, `SoftCloneEngine`, and `HardCloneEngine` to accurately identify iOS/iPadOS wrapper applications designed for Apple Silicon (apps containing `Wrapper/` or `UIDeviceFamily` with `LSRequiresIPhoneOS=True`).
  - Gracefully rejects cloning iOS-on-Mac wrapper applications with clear, localized error prompts (`error_ios_wrapper_unsupported`) across CLI (`atbclone clone`, `atbclone wizard`) and GUI Creation Wizard, preventing corrupted bundle generation and launch failures.

### 🎨 Automated Icon Resource Pipeline in Packaging Scripts
- **Dynamic `.icns` Generation**:
  - Added automated `.icns` compilation via `sips` and `iconutil` in `scripts/build_gui.sh` during macOS DMG and app bundle generation.
  - Enhanced asset inclusion and integrity verification in packaging workflows.

### 🌐 Multi-Language Localization
- **Localized Error Diagnostics**:
  - Added localized prompt messages for unsupported iOS wrapper apps across all 9 supported languages.
- **Testing**:
  - Expanded test suite to 336 automated unit and GUI integration tests.

---

## [v0.9.0] - 2026-08-21

### 🌐 Per-Clone Independent Language & Locale Isolation
- **Custom Locale & Language Selection (`--language` / `--locale`)**:
  - Added support for running clones in dedicated languages independent from the host system macOS language and primary application settings.
  - CLI commands `atbclone clone` and `atbclone wizard` now support `--language` / `--locale` parameters, and the GUI Creation Wizard / Edit Dialog provide interactive language pickers.
  - Automatically injects `AppleLanguages` and `AppleLocale` macOS user defaults and environment variables into soft clone wrappers and hard clone binary launchers.
  - Added `atbclone.core.locale` helper supporting comprehensive language tag parsing, BCP-47 identifiers, and system locales.

### 🆔 Robust Multi-Instance Bundle ID Resolution
- **Collision-Free Clone Bundle Identifiers**:
  - Introduced `AppInspector.find_next_bundle_id` to dynamically scan active clone states and the file system, ensuring deterministic, collision-free Bundle IDs (`com.vendor.app.atb1`, `atb2`, etc.) when creating multiple instances of the same application.

### 🍏 System Tray Activation & Window Lifecycle Improvements
- **Seamless macOS Menu Bar Tray Experience**:
  - Fixed window activation, deminiaturization, and unhiding when restoring the main window from the system menu bar status item (`TrayService`).
  - Intercepted window close events (`Cmd+W` / red traffic light button) when "Minimize to System Tray" is enabled to cleanly hide the window to the tray rather than terminating.
  - Enhanced status item mouse event handling (left click, right click, and Ctrl+Click).

### ⚡ Clone Update Concurrency & Clean Destination Cleanup
- **Atomic Re-cloning**:
  - Resolved race conditions during clone update operations by enforcing thorough destination bundle cleanup before re-generation.
  - Fixed UI state synchronization and reactive card updates upon clone modification.

### 🎨 GUI Typography, Sizing & Documentation
- **Visual Polish**:
  - Optimized Cocoa table row heights (34px), typography scale, and dropdown selection text sizing to prevent clipping.
  - Added comprehensive download sections, GUI walkthrough guide, and screenshots to documentation.
- **Testing**:
  - Expanded automated test suite to 329 unit and GUI integration tests.

---

## [v0.8.0] - 2026-08-20

### 🎨 macOS Human Interface Guidelines (HIG) Visual Overhaul
- **Native Apple Design System & Accessibility**:
  - Fully overhauled the GUI design to adhere strictly to Apple Human Interface Guidelines: standardized native color palettes, typography scale (11pt–22pt), and comfortable spacing hierarchy.
  - Enhanced Cocoa table rendering via runtime patches (`patch_cocoa`): increased row height to 40px, modernized table headers, and enlarged cell font sizes for crystal-clear readability.
  - Enlarged input fields, dropdown selectors, switches, action buttons, and form labels across the Creation Wizard, Settings, and Detail/Edit dialogs.
  - Refined table action footers into compact native macOS toolbar buttons.
  - Switched default view mode to **List View** across all management views for dense and readable app inspection.

### 💾 Unified Storage Settings & Subdirectory Auto-Sync
- **Streamlined Storage Management**:
  - Reorganized SettingsView to consolidate root storage and path configurations. Modifying the Root Storage directory automatically and reactively updates all derived subdirectories (`clones.yaml`, `Data/`, `logs/`, `recipes/`).
  - Added real-time validation and directory existence status indicators.

### 🌐 HTTPS Proxy Protocol Support
- **Full HTTPS Proxy Integration**:
  - Added support for `https://` proxy schemes across Recipe validation models, CLI (`atbclone clone`, `atbclone wizard`), and GUI network configurations.

### 📦 Application Bundle & Packaging Improvements
- **Direct Module Entrypoint & DMG Enhancements**:
  - Added `src/atbclone/__main__.py` entrypoint allowing direct execution via `python -m atbclone`.
  - Enhanced GUI packaging script (`scripts/build_gui.sh`) with robust bundle integrity validation, resource verification, and DMG creation.
- **Testing**:
  - Expanded automated test suite to 304 unit and GUI integration tests.

---

## [v0.7.0] - 2026-08-20

### 🖥️ Native BeeWare Toga GUI Desktop Application
- **Modern Ice-Blue Graphical Interface**:
  - Introduced the full native macOS desktop application (`atbclone-gui`), built on BeeWare Toga.
  - Implemented responsive sidebar navigation and unified views: Clone Cards Grid (`ClonesView`), App Prober (`ProbeView`), Recipe Manager (`RecipesView`), Logs Viewer (`LogsView`), and Settings (`SettingsView`).
  - Interactive visual wizard for drag-and-drop cloning with real-time feedback.

### 🍏 Native macOS Menu Bar Tray Service & Window Minimization
- **System Menu Bar Tray Integration**:
  - Implemented native `NSStatusBar` & `NSStatusItem` Menu Bar icon (`TrayService`) with quick actions (Open Main Window, Create Clone, Quick Launch, Preferences, Quit).
  - Added "Minimize to System Tray" setting with seamless Cocoa selector registration and `NSWindowDelegate` notifications.

### 📖 GUI Multilingual Release Notes Viewer
- **Integrated Release Notes Window**:
  - Added a dedicated Release Notes viewer accessible directly from the Settings view.
  - Dynamic 9-language switcher dropdown allowing real-time Markdown rendering across all supported languages.

### 📝 Unified Operation Logging System
- **Thread-safe Logging & Live Stream**:
  - Implemented `atbclone.core.logger` with persistent file logging (`~/.atbclone/logs/atbclone.log`) and live memory broadcasting (`LogBroadcastHandler`).
  - Interactive GUI Logs view with live streaming, log level filtering, search, export, and disk log clearing.

### 📦 Enhanced Recipes & Testing
- **New Built-in Recipes**: Added official recipes for **Claude Desktop** (`com.anthropic.claudefordesktop`), **Telegram** (`ru.keepcoder.Telegram`), **Cursor**, and other popular tools.
- **Comprehensive Testing**: Upgraded test suite to 299 automated unit and GUI integration tests.

---

## [v0.6.0] - 2026-08-19

### 📂 Custom Data Directory Support
- **Customizable Clone Data Storage (`--data-dir`)**:
  - Added `--data-dir` option to `atbclone clone`, allowing users to specify custom locations for cloned app user data (e.g. external SSDs or custom workspaces).
  - Integrated custom data directory configuration into the interactive wizard (`atbclone wizard`).
  - Enhanced Recipe data models and engines to resolve dynamic custom data directory variables.

### 🗑️ Enhanced Clone Uninstallation & Cleanup (`atbclone remove`)
- **Safe Data Purging Controls**:
  - Added `--purge-data` flag to `atbclone remove` for automated complete deletion of clone bundle and associated user data directories.
  - Added `--keep-data` flag to preserve isolated data while uninstalling application bundles.
  - Interactive removal confirmation prompts now offer clear choices between preserving or purging data with safety warnings.
  - Enhanced handling of orphan data directories and permission diagnostics during removal.

### 🆔 Bundle ID Standardization & i18n
- **Standardized Bundle Identifier Generation**:
  - Added `AppInspector.generate_bundle_id` helper, standardizing clone bundle ID formatting across `clone`, `wizard`, and `update` commands.
- **Multilingual Support**:
  - Added full translation coverage for data directory prompts, remove confirmation dialogs, and purge status logs across all 9 supported languages.
- **Testing**:
  - Expanded automated test suite to 213 unit tests.

---

## [v0.5.0] - 2026-08-19

### 🔐 Apple Code Signing & Notarization Pipeline
- **Automated Hardened Runtime & Signing**:
  - Integrated Apple Developer ID Application code signing with Hardened Runtime (`--options runtime`), timestamping, and custom JIT / execution entitlements (`scripts/entitlements.plist`).
  - Added `scripts/notarize.sh` for one-command Apple Notarization (`xcrun notarytool submit --wait`) using Keychain API credentials (`--keychain-profile`).
  - Enhanced `scripts/build_cli.sh` and `scripts/release.sh` with `--sign-identity`, `--skip-sign`, and `--notarize` flags with automatic ad-hoc signing fallback.

### 🚀 Chromium Hard Clone & Launch Arguments Injection
- **Hard Clone Engine Support for `launch_args`**:
  - Upgraded `HardCloneEngine` to support dynamic `--user-data-dir={{ATB_DATA_DIR}}` argument injection into binary launch wrappers alongside environment variables.
  - Upgraded built-in recipes for **Google Chrome**, **Microsoft Edge**, and **Arc Browser** to `hard_clone` for complete app bundle duplication and isolated Dock/Finder identities.
- **CLI Strategy Override**:
  - Added `--strategy` option to `atbclone clone` (`--strategy hard_clone` / `--strategy soft_clone`) allowing users to explicitly override default recipe strategies.

### ⚡ Process Forwarding & Test Suite Expansion
- **Process Management**: Improved `SoftCloneEngine` launcher script to use standard `exec "$@"` argument forwarding.
- **Comprehensive Testing**: Expanded automated test suite to 199 unit tests covering code signing, notarization scripts, and strategy overrides.

---

## [v0.4.0] - 2026-08-19

### 🌐 Comprehensive 9-Language CLI & Documentation Ecosystem
- **Full CLI Internationalization Across 9 Languages**:
  - Expanded `atbclone.core.i18n` with full localization support for English, Simplified Chinese, Traditional Chinese, Japanese, Korean, German, French, Russian, and Spanish.
  - All interactive commands (`wizard`, `clone`, `probe`, `list`, `recipe`, `doctor`, `update`, `remove`, `version`) seamlessly render localized prompts, tables, and error diagnostics.
- **Multilingual Release Notes Architecture**:
  - Standardized release note documentation across all 9 supported languages under `docs/release/`.

### 🔄 Automated Release & Version Synchronization Pipeline
- **Automated 9-Language Release Notes Validation**:
  - Enhanced `scripts/manage_version.py` and `scripts/release.sh` with automated checks ensuring all 9 `docs/release/ReleaseNote*.md` files are synchronized and validated before creating release tags.
  - Added `--check-notes` validation flag in version manager to prevent missing release documentation.
- **Enhanced Test Suite**:
  - Upgraded automated test suite to 191 unit tests with full multi-language and release workflow coverage.

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
