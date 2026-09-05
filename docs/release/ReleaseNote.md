[English](ReleaseNote.md) | [简体中文](ReleaseNote_zh.md) | [繁體中文](ReleaseNote_zh_TW.md) | [日本語](ReleaseNote_ja.md) | [한국어](ReleaseNote_ko.md) | [Deutsch](ReleaseNote_de.md) | [Français](ReleaseNote_fr.md) | [Русский](ReleaseNote_ru.md) | [Español](ReleaseNote_es.md)

# ATBClone Release Notes

All notable changes, new features, improvements, and bug fixes for **ATBClone** are documented in this file.

---

## [v1.3.0] - 2026-09-05

### 🔬 Mach-O Headroom Probing & Safety Verification
- **Static Binary Header Inspection**:
  - Added `_check_macho_injection_headroom` to inspect available padding between Mach-O load commands (`sizeofcmds`) and the first section before modifying binaries.
  - Guarantees binary integrity by preventing corruption on applications with tightly packed Mach-O headers.

### 🎛️ Configurable Injection Strategy (`auto`, `dylib`, `launcher`)
- **Flexible Interposition Architecture**:
  - Added `injection_strategy` configuration across Recipe models, CloneTask, CloneRecord, CLI (`--injection-strategy`), and GUI (Clone Wizard, Recipe Editor).
  - **Auto mode** (`auto`): Intelligently probes Mach-O headroom for native Cocoa apps; injects dynamic libraries when headroom is sufficient, or gracefully falls back to native Mach-O C launcher with an explanatory notice.
  - **Dylib mode** (`dylib`): Enforces dynamic library injection, raising a descriptive `CloneError` if headroom is inadequate or binary architecture is unsupported.
  - **Launcher mode** (`launcher`): Forces native Mach-O C launcher wrapper without modifying application binaries.
  - Real-time display of the actual executed injection mode in `CloneDetailWindow` and CLI `inspect`.

### 📚 Comprehensive Documentation Updates
- **In-Depth Guides & Architecture Docs**:
  - Fully updated user manuals in `docs/guide/` (both English and Simplified Chinese) and READMEs with detailed explanations of injection strategies, dylib interception mechanisms, and headroom probing.

### 🧪 Comprehensive Quality Assurance
- **Expanded Test Suite**:
  - Automated test suite expanded to 479 unit, engine, probe, and GUI integration tests with 100% pass rate.

---

## [v1.2.1] - 2026-09-05

### 🧩 Decoupled Dylib Injection via @executable_path (Fix #6)
- **Robust Dynamic Library Interposition**:
  - Migrated dynamic library injection in `HardCloneEngine` from `@rpath` to `@executable_path/../Frameworks/libatbclone_env.dylib`.
  - Completely decouples dylib loading from target binaries' `LC_RPATH`, eliminating launch crashes and dyld symbol resolution failures on applications with non-standard or stripped rpath configurations (e.g., WeChat 4.x and custom Cocoa bundles).
  - Added fallback symlink generation in `Contents/Frameworks/ld/` when an `ld` directory structure is present.

### ⚙️ Automated Build Intermediate Artifacts & Info.plist Synchronization
- **Zero-Drift Version Alignment**:
  - Enhanced `scripts/manage_version.py` with native `PlistVersionTarget` via `plistlib` to automatically track and update `Info.plist` (`CFBundleShortVersionString` & `CFBundleVersion`) and `installer/resources/welcome.html`.
  - Added build intermediate artifact inspection and drift detection to `scripts/manage_version.py --show`.
  - Hardened `scripts/build_gui.sh` to guarantee both short and internal bundle versions are synchronized during GUI packaging.

### 🧪 Comprehensive Quality Assurance
- **Expanded Test Suite**:
  - Automated test suite expanded to 468 unit, engine, version management, and GUI integration tests with 100% pass rate.

---

## [v1.2.0] - 2026-09-02

### 🔔 Native Dylib Injection for macOS Notifications & Menu Bar Status Items
- **Notification Center & Tray Item Resolution (Fix #5)**:
  - Enabled native dynamic library (`.dylib`) interpose injection in `HardCloneEngine`.
  - Interposes NSUserNotificationCenter and NSStatusItem APIs, resolving missing macOS notification banners and menu bar tray status items for hard cloned applications.

### 🌓 Dynamic Dark Mode Awareness & Visual Theme Polish
- **System Appearance Tracking (Fix #4)**:
  - Added real-time macOS system appearance tracking to dynamically adapt GUI theme tokens when toggling between Dark and Light modes.
- **Card Layout & Contrast Improvements**:
  - Optimized card layout grid spacing and enlarged default application window width for improved readability.
  - Enhanced text contrast in Logs and Release Notes windows, meeting WCAG 2.1 AA legibility standards.

### 📖 Documentation & Screenshot Updates
- **Path Standards & Asset Refreshes**:
  - Updated default clone installation path across documentation to `~/ATBClone/Apps`.
  - Refreshed high-resolution GUI application screenshots in documentation and asset directories.

### 🧪 Comprehensive Quality Assurance
- **Expanded Test Suite**:
  - Automated test suite expanded to 462 unit, engine, recipe, theme, and GUI integration tests with 100% pass rate.

---

## [v1.1.1] - 2026-08-30

### 🧹 Automatic Stale Framework Version Pruning
- **Disk Optimization & Code Signing Verification**:
  - `HardCloneEngine` now automatically prunes orphaned/stale framework versions inside `Contents/Frameworks/*.framework/Versions/` (often left behind by in-place updates of Google Chrome, Chromium, and Electron apps).
  - Eliminates `"embedded framework contains modified or invalid version"` errors during codesign verification while saving hundreds of megabytes of disk space per cloned application.

### 🛡️ Deep Entitlements Sanitization with Python Plistlib
- **Atomic Extraction & Security Policy Filtering**:
  - Upgraded entitlements extraction to use secure atomic temporary files (`${TMPDIR:-/tmp}/atb_ent_XXXXXX`).
  - Integrated Python `plistlib` filtering to reliably purge restricted Apple developer, application-group, iCloud, and sandbox entitlement prefixes (`com.apple.developer.`, `keychain-access-groups`, `com.apple.security.application-groups`, `com.apple.security.app-sandbox`).
  - Multi-stage recursive code signing across dynamic libraries, Mach-O binaries, frameworks, and embedded helper apps.

### 🧪 Comprehensive Quality Assurance
- **Expanded Test Suite**:
  - Automated test suite expanded to 455 unit, engine, recipe, prober, and GUI integration tests with 100% pass rate.

---

## [v1.1.0] - 2026-08-29

### 🤖 First-Class AI Client & LLM Tool Ecosystem Support
- **Claude Desktop & Claude Code Multi-Instance Support**:
  - Automatically injects `CLAUDE_CONFIG_DIR`, replicates and isolates `~/.claude` and `~/.claude.json` configuration directories per clone.
  - Preserves `CFBundleName` across cloned bundles to ensure Claude helper processes locate the host application without lookup crashes.
- **Google Antigravity & Gemini Ecosystem**:
  - Injects `GEMINI_HOME` and `ANTIGRAVITY_HOME` environment variables, isolating `~/.gemini` data directories.
- **OpenAI ChatGPT & Codex CLI**:
  - Injects `CODEX_HOME` and replicates `~/.codex` configuration directories for simultaneous multi-account execution.

### 🔑 Automatic macOS Keychain Symlinking
- **Keychain Redirection & Crash Prevention**:
  - Automatically establishes symlinks to `Library/Keychains` when `HOME` environment redirection is enabled, eliminating missing keychain alerts, login item crashes, and credential storage errors.

### 🛡️ AMFI Entitlements Sanitization & Hardened Runtime Security
- **Ad-Hoc Signing Stability on macOS Sonoma & Sequoia**:
  - Automatically sanitizes restricted team-scoped entitlements (`com.apple.application-identifier`, `com.apple.developer.team-identifier`, `keychain-access-groups`) during ad-hoc re-signing.
  - Prevents Apple Mobile File Integrity (AMFI) `SIGKILL` termination on embedded helper processes.

### 🚀 ProcessSingleton Mach-O Patching Generalization
- **Broad AI & Electron Multi-Instance Support**:
  - Generalized Mach-O ProcessSingleton patching and injected `--user-data-dir` arguments across AI client recipes to prevent single-instance locks.

### 🧪 Comprehensive Quality Assurance
- **Expanded Test Suite**:
  - Automated test suite expanded to 453 unit, engine, recipe, prober, and GUI integration tests with 100% pass rate.

---

## [v1.0.2] - 2026-08-26

### 🛡️ Enhanced Sandbox Stripping & Hard Clone Stability
- **Universal Sandbox Stripping for Hard Clones**:
  - Configured `strip_sandbox: true` across recipes utilizing the Hard Clone strategy, preventing sandbox container permission deadlocks and permission conflicts on modified Mach-O bundles.
  - Enhanced WeChat (微信) hard clone configuration with guaranteed runtime directory structures (`Caches`, `Containers`, `Preferences`) in wrapper scripts.

### 📚 Recipe Curations & Upstream Limitation Documentation
- **Built-in Recipe Refinement**:
  - Removed experimental WeCom (企业微信) built-in recipe due to upstream CEF deep IPC anti-multi-instance architectural constraints, and added clear troubleshooting documentation.
  - Documented best practices for third-party application multi-instance configurations and recipe authoring.

### 🧪 Comprehensive Quality Assurance
- **Full Test Coverage**:
  - Verified 443 automated unit, recipe, engine, and GUI integration tests with 100% pass rate.

---

## [v1.0.1] - 2026-08-26

### 🎨 Apple Design HIG Audit & Visual Refinements
- **macOS Human Interface Guidelines Compliance**:
  - Comprehensive Apple Design HIG audit across all desktop views and dialogs.
  - Eliminated distracting emoji decorations in favor of native SF Pro typography hierarchies and clean iconography.
  - Enhanced sidebar navigation with native Cocoa selection highlights.
  - Polished light and dark mode color contrast ratios exceeding WCAG 2.1 AA legibility standards.
  - Improved empty states, card shadows, window drag responsiveness, and consistent widget padding.

### 📜 Reverse Chronological Logs & UI Layout Fixes
- **Real-Time Logs Enhancement (`LogsView`)**:
  - Configured log display to render in reverse chronological order (newest log entries at the top), significantly improving live diagnostic efficiency.
- **Multilingual Button Width Adaptations**:
  - Removed rigid fixed widths from Refresh and Browse buttons across windows to prevent text clipping in English, German, French, Russian, and Spanish.

### 🛡️ Clone Engine Resilience & Extended Attribute Toleration
- **Bundle Permissions & `xattr` Error Handling**:
  - Automatically enforces user write permissions (`chmod -R u+w`) on cloned app bundles prior to Mach-O modification and code signing.
  - Added fault-tolerant error handling for macOS extended attribute clearance (`xattr -cr`) on read-only system snapshots or protected files, eliminating cloning failures.

### 🧪 Test Suite & Quality Assurance
- **Expanded Coverage**:
  - Automated test suite expanded to 443 unit, engine, and GUI integration tests with 100% pass rate.

---

## [v1.0.0] - 2026-08-24

### 🚀 Official 1.0.0 Milestone Release
- **Production-Ready macOS App Cloning**:
  - ATBClone reaches version 1.0.0, establishing a complete, mature, and zero-compromise application cloning ecosystem for macOS (Apple Silicon & Intel).
  - Offers seamless dual-engine architectures: zero-disk-overhead Soft Clones (CLI-wrapper & bundle virtualization) and completely isolated Hard Clones (Mach-O binary manipulation, deep signing, container virtualization).

### 🧬 Deep CEF (Chromium Embedded Framework) Patching & WeCom Support
- **Hybrid Framework Multi-Instance Engine**:
  - Implemented scoped Chromium Embedded Framework (CEF) binary patching specifically designed for complex enterprise hybrid applications such as WeCom (企业微信).
  - Resolved `GpuDataManager` FATAL crashes across helper subprocesses and sanitized nested helper bundle identifiers (`.helper.atbclone.X`).
  - Integrated symlink whitelists and disabled internal sandbox collisions to guarantee reliable multi-instance execution.

### 🛡️ Full-Bundle Recursive Re-Signing & Entitlements Sanitization
- **Nested Binary & Framework Security**:
  - `HardCloneEngine` now performs thorough recursive re-signing across all nested binaries, embedded Frameworks, Helper apps, XPC services, and dynamic libraries (`.dylib`).
  - Preserves JIT and hardened runtime entitlements while generating clean temporary entitlements outside bundle structures to prevent code signature verification pollution.
- **Framework ProcessSingleton Binary Patching**:
  - Introduced `patch_framework_singleton` recipe field to dynamically patch framework-level process singleton locks directly in Mach-O binary structures without unstable dynamic library interposing.

### 📋 Enhanced Detail Views & Native Clipboard Integration
- **Diagnostic Export**:
  - Re-architected `CloneDetailWindow` using multiline Cocoa text views and direct `NSPasteboard` integration for selectable text and instantaneous markdown diagnostic summary exporting.

### 🧪 Comprehensive Quality Assurance
- **Full Test Coverage**:
  - Automated test suite expanded to 441 unit, engine, recipe, prober, and GUI integration tests with 100% pass rate.

---

## [v0.9.9] - 2026-08-24

### 📋 Selectable Text & "Copy All Details" in Clone Details Window
- **Interactive Information Extraction**:
  - Enabled Cocoa native text selectable mode across all labels in `CloneDetailWindow` so users can highlight and copy any individual path, bundle ID, or argument directly.
  - Added a dedicated "Copy All Details" button in the footer to copy a complete markdown-formatted diagnostic report of the clone to the clipboard with visual feedback.

### 🎨 macOS Native UI Design & Token Refinements
- **Theme & Component Optimization**:
  - Polished color palette tokens in `Theme` for light and dark modes (`BG_APP`, `BG_CARD`, `BG_HOVER`, `BORDER`, `TEXT_PRIMARY`, `TEXT_MUTED`, `ACCENT`).
  - Improved card containers, rounded borders, and consistent widget spacing across `CloneListView`, `RecipeListView`, `ProbeView`, `DoctorView`, `SettingsView`, and dialog windows.

### 📖 Comprehensive Multilingual User Manual (`docs/guide/`)
- **Complete End-to-End User Documentation**:
  - Published comprehensive user manuals in English (`docs/guide/en/`) and Simplified Chinese (`docs/guide/zh-cn/`).
  - Covers Chapter 1 (Basic Operations & Lifecycle), Chapter 2 (Advanced Custom Recipes), Chapter 3 (Under the Hood & Framework Architecture), and Chapter 4 (FAQ, Troubleshooting, & Diagnostics).

### 🧪 Test Suite & Quality Assurance
- **Extended Test Coverage**:
  - Automated test suite expanded to 431 tests with 100% pass rate.

---

## [v0.9.8] - 2026-08-24

### 🔒 Sandbox Entitlements Extraction & Hard Clone Stability
- **Source App Entitlements Preservation**:
  - Enhanced `HardCloneEngine` to extract and preserve original entitlements directly from source Mach-O binaries via `codesign -d --entitlements :-`.
  - Added robust validation to guard against generating empty or corrupt entitlements during ad-hoc and Developer ID re-signing.
- **Built-in Recipes Sandbox Container Isolation**:
  - Refined built-in recipe configurations by enforcing `strip_sandbox: false` across hard-clone applications (including WeChat, QQ, WeWork, WPS Office, LINE, Skype, and CapCut).
  - Ensures complete sandbox container isolation (`~/Library/Containers/<new_bundle_id>`) to prevent credential leakage and cross-instance interference.

### 📚 Documentation & Schema Modernization
- **Multilingual Documentation Updates**:
  - Synchronized English (`README.md`) and Simplified Chinese (`README_zh.md`) documentation with current schema standards, including `app_type`, `strip_sandbox`, runtime architecture classifications, and CLI/GUI workflows.

### 🧪 Test Suite & Quality Assurance
- **Robust Verification**:
  - Verified all 428 unit, core engine, and GUI integration tests pass with 100% success rate.

---

## [v0.9.7] - 2026-08-24

### 🔍 Intelligent Application Architecture Detection & Language Adaptation
- **`app_type` Architecture Recognition**:
  - Introduced `app_type` field (`electron`, `chromium`, `qt`, `flutter`, `native_cocoa`, `java`, `unknown`) to the Recipe model.
  - Automatically recognizes application runtime frameworks via `AppProber.detect_app_type` by inspecting bundle frameworks, dylibs, and JVM structures.
  - Standardized all 34 built-in recipes with explicit `app_type` and `strip_sandbox` configurations.
- **Framework-Adaptive Language Injection**:
  - Dynamically injects locale flags customized per runtime framework (`--lang=` for Chromium/Electron, `-AppleLanguages` for Native Cocoa, `-user.language` for Java).

### 🧬 Mach-O Binary Argument Probing & Validation
- **Intelligent Data Directory Probing**:
  - Implemented `BinaryArgumentProber` to scan Mach-O executable string tables, automatically extracting supported user data directory CLI flags (`--user-data-dir`, `--profile-directory`, `--datadir`, etc.) for unknown applications.
- **Launch Argument Validation**:
  - Added `LaunchArgumentValidator` to prune unsupported or conflicting CLI flags during clone creation, preventing application crashes.

### 📋 Clone Injected Parameters Inspection & Copy
- **`CloneInspector` & Details View Enhancement**:
  - Implemented `CloneInspector` to parse and extract runtime injected environment variables, proxy settings, language overrides, and launch flags from clone bundles.
  - Added an "Injected Parameters" card in `CloneDetailWindow` with a one-click copy button and visual feedback.

### ⚙️ Recipe Editor Window Advanced Customization
- **GUI Recipe Editing (`RecipeEditWindow`)**:
  - Added advanced configuration fields including application framework type selection, launch arguments editor, proxy settings, environment variables, and symlink whitelists.

### 🧪 Test Suite Expansion
- **Comprehensive Coverage**:
  - Expanded automated test suite to 428 unit and GUI integration tests.

---

## [v0.9.6] - 2026-08-24

### 🖱️ Native Cocoa Table Header Sorting
- **Interactive Column Sorting in Lists**:
  - Implemented native Cocoa `NSTableViewHeaderView` click-to-sort patch supporting column sorting across `CloneListView` and `RecipeListView`.
  - Supports bidirectional sorting (ascending / descending) with visual sort indicators on table headers and toolbar sort controls synchronization.
  - Automatically preserves active item selection across sort operations.

### 📦 Multi-Selection & Batch Operations
- **Batch Clones Management (`CloneListView`)**:
  - Added multi-row selection support (`multiple_select=True`) with dynamic toolbar button state management.
  - Supports batch clone updates and batch removals with purge data confirmation dialogs.
- **Batch Recipe Deletion with Smart Protection (`RecipeListView`)**:
  - Multi-selection deletion for custom recipes.
  - Scenario-based confirmation dialogs: protects builtin read-only recipes, alerts users when mixing custom and builtin recipes, and accurately reports batch deletion progress.
  - Integrated busy state locking to prevent concurrent operations during batch executions.

### 🛠️ Xcode Command Line Tools Diagnostic & Doctor View Enhancement
- **Startup Diagnostic Checks**:
  - Added automated environment checks for Xcode Command Line Tools readiness (`xcode-select -p`, `codesign`, `lipo`, `otool`, `install_name_tool`).
  - Provides clear diagnostic guidance and installation commands in the Doctor View when tools are missing.

### ℹ️ Standard macOS About Dialog Metadata
- **Cocoa About Dialog Fix**:
  - Properly mapped version numbers, app name, and copyright metadata in the standard macOS "About ATBClone" dialog.

### 🧪 Test Suite Expansion
- **Comprehensive Coverage**:
  - Expanded automated test suite to 369 unit and GUI integration tests.

---

## [v0.9.5] - 2026-08-23

### 📝 Auto-Wrapping `WrappingLabel` Component & Text Formatting
- **Multiline Text Wrapping Support**:
  - Implemented the `WrappingLabel` component to solve macOS Cocoa Toga single-line text constraint limitations.
  - Automatically calculates dynamic intrinsic height based on the container width (`cellSizeForBounds_`) while leaving width unconstrained, completely preventing long pathnames and text from expanding windows horizontally.
- **Prober & Detail View Formatting**:
  - Applied `WrappingLabel` across `ProbeView` (Prober analysis reports, compatibility evaluations, sandbox status), `CloneDetailWindow` (launch arguments, bundle id, data directories), and `WizardWindow` (strategy descriptions and advice).

### 🧪 Test Hermeticity & State Isolation
- **Dynamic Configuration & Test Isolation**:
  - Enhanced `StateManager` and `RecipeLoader` to dynamically evaluate configuration paths at runtime rather than module import time.
  - Ensured unit tests remain strictly hermetic and isolated from local user state and custom recipe files.
- **Testing**:
  - Expanded automated test suite to 347 unit and GUI integration tests.

---

## [v0.9.4] - 2026-08-23

### 📁 Visible Default Data Directory Migration (`~/ATBClone`)
- **Intuitive User Data Management**:
  - Migrated the default ATBClone root directory from hidden `~/.atbclone` to user-accessible `~/ATBClone` (including `~/ATBClone/Data/`, `~/ATBClone/clones.yaml`, and logs).
  - Makes managing, backing up, and inspecting clone storage and configurations straightforward via macOS Finder and Terminal.

### 🏷️ Exact Application Display Name Enforcement & Localization Override
- **Consistent Bundle Naming**:
  - Enhanced both `SoftCloneEngine` and `HardCloneEngine` to clean up localized strings (`InfoPlist.strings`) and remove `LSHasLocalizedDisplayName` within cloned app bundles.
  - Ensures Finder, Dock, Spotlight, and Activity Monitor strictly display the custom clone display name instead of falling back to system-localized default titles.

### 🔄 Instant LaunchServices Registration
- **Automated Cache Refresh**:
  - Automatically registers newly generated or updated clones with macOS LaunchServices (`lsregister -f`), immediately reflecting icon and metadata updates across Finder, Dock, and Spotlight without requiring system reboots.

### 📦 Test Suite & Documentation
- **Updated References**:
  - Reflected new `~/ATBClone` default path across CLI documentation, GUI settings, and all 341 unit and integration tests.

---

## [v0.9.3] - 2026-08-21

### 🛡️ Enhanced App Inspection & Wizard Validation for iOS Wrapper Apps
- **Interactive Wizard Pre-check & Error Dialog**:
  - Upgraded `AppInspector.inspect_app` to detect iOS-on-Mac (Designed for iPad/iPhone) wrapper applications directly during file selection or drag-and-drop.
  - In the GUI Creation Wizard (`WizardWindow`), selecting an unsupported iOS wrapper application now immediately triggers a localized warning dialog and resets the input, preventing invalid workflows upfront.

### 🍏 Clean macOS Exit & Cocoa Memory Target Teardown
- **Crash Prevention on Application Termination**:
  - Enhanced `TrayService.disable()` and `ATBCloneApp.exit_app()` to safely unbind Cocoa status item targets and selectors, eliminating dangling Objective-C pointers during shutdown.
  - Implemented clean Cocoa event loop termination (`NSApp.terminate_` / `os._exit(0)`), completely resolving crash-on-exit / segmentation fault issues when quitting via the Menu Bar tray or `Cmd+Q`.

### 📦 Test Suite Expansion
- **Comprehensive Testing**:
  - Expanded test coverage to 341 automated unit and GUI integration tests.

---

## [v0.9.2] - 2026-08-21

### 🍏 Dynamic macOS Dock Icon Hiding & System Tray Polishing
- **Automatic Dock Icon Management**:
  - Implemented dynamic macOS Dock icon visibility management via AppKit activation policies (`NSApplicationActivationPolicy`).
  - When minimizing or closing the window to the system tray (`minimize_to_tray` enabled), the Dock icon is automatically hidden from the macOS Dock (`NSApplicationActivationPolicyAccessory`).
  - When restoring the window from the menu bar tray, the Dock icon seamlessly reappears (`NSApplicationActivationPolicyRegular`) with instant focus.
- **Dock Reopen Handler**:
  - Added native `AppDelegate` patch for `applicationShouldHandleReopen:hasVisibleWindows:` to smoothly restore and focus the main window when clicking the application in macOS Finder or Dock.

### 📦 Asset Footprint Optimization & Testing
- **Optimized Image Resources**:
  - Compressed and optimized application icon assets (`logo.icns` and `logo.png`), reducing bundle overhead.
- **Testing**:
  - Expanded automated test suite to 338 unit and GUI integration tests.

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
