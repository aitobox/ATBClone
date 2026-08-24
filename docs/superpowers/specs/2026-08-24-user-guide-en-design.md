# ATBClone English User Manual Architecture & Design Document

**Document Title**: ATBClone Comprehensive English User Guide & Manual
**Target Directory**: `docs/guide/en/`
**Target Audience**: Beginner / Everyday macOS Users (with Advanced & Power User Deep-Dives)
**Date**: 2026-08-24

---

## 1. Overview & Goals

The goal of this guide is to provide a beginner-friendly, beautifully structured, step-by-step English user manual for ATBClone (macOS Application Cloning Engine). It covers the complete GUI workflow, single and batch clone lifecycle management, niche app recipe authoring, deep architectural mechanics (soft vs. hard clone, sandbox stripping, wrapper hijack), comprehensive FAQ, and diagnostic issue reporting.

---

## 2. Directory & Chapter Structure

The documentation will be modularized into 5 dedicated files inside `docs/guide/en/`:

```text
docs/guide/en/
├── README.md                           # Master navigation index and quick learning paths
├── 01-basic-operations.md              # 7-step wizard creation & complete lifecycle management
├── 02-advanced-custom-recipes.md       # Prober scanning, custom recipe editor & basic parameter guide
├── 03-under-the-hood-and-internals.md  # Core isolation mechanics & advanced parameter reference
└── 04-faq-and-troubleshooting.md       # High-frequency FAQ, Doctor diagnostics & GitHub Issue filing
```

---

## 3. Detailed Chapter Breakdown

### Chapter 0: `README.md` (Navigation & Guide Roadmap)
* **Introduction**: What is ATBClone, why quadruple isolation matters (Data, Visual, TCC permissions, Network proxy).
* **Audience Paths**:
  * *Everyday Users*: Follow Chapter 1 for quick cloning and daily use.
  * *Power Users*: Read Chapter 2 and 3 for custom recipes and engine mechanics.
  * *Troubleshooting*: Jump to Chapter 4 for FAQs and diagnostics.
* **Quick Glossary**: App bundle, Bundle Identifier, Hard Clone, Soft Clone, Recipe, Data Directory.

### Chapter 1: `01-basic-operations.md` (Basic Operations & Clone Management)
* **Step-by-Step Creation (7-Step Wizard)**:
  1. *Step 1: Select Primary Application*: Drag-and-drop or browse from `/Applications`.
  2. *Step 2: Strategy & Recipe Matching*: Auto-detection from 33+ built-in recipes or Prober dynamic analysis.
  3. *Step 3: Clone Identity & Language*: Setting Clone Name (e.g. `WeChat2`), Display Title in Dock/Finder, and independent UI language locale.
  4. *Step 4: Destination Directory*: Installing to `~/Applications` (zero-password user space) vs `/Applications` (system space).
  5. *Step 5: Dedicated Data Directory*: Auto-configured `~/ATBClone/Data/<Name>` or custom external SSD storage.
  6. *Step 6: Network Proxy*: Optional dedicated HTTP / SOCKS5 proxy configuration per clone.
  7. *Step 7: Summary & Execution*: Review parameters and create with one click.
* **Managing Cloned Applications**:
  * Launching clones from GUI, Spotlight, or Dock.
  * Opening the isolated Data Directory directly via "Open Dir".
  * Editing clone configurations (display name, language, proxy settings).
  * Updating clones seamlessly after primary app updates (preserving 100% user data and chat history).
  * Batch operations: multi-select clones in Table view for batch updating or batch deletion.
  * Safe Deletion: choosing between App-only removal (keeping user data) or complete cleanup.

### Chapter 2: `02-advanced-custom-recipes.md` (Custom Recipes for Niche Apps)
* **Why Custom Recipes are Needed**: Handling uncommon or specialized apps not in the built-in library.
* **Workflow A: Using the Built-in App Prober**:
  * Navigating to the Prober tab.
  * Inspecting Mach-O architecture, embedded frameworks (Electron, Chromium, Cocoa, etc.), and sandbox entitlements.
  * Generating a recipe YAML file and clicking "Save as Recipe".
* **Workflow B: Visual Recipe Editor**:
  * Navigating to "Recipes" tab -> clicking "New Recipe" or "Edit".
  * Visual form filling for unlisted apps.
* **Basic Recipe Parameters Reference**:
  * `bundle_id`: Target application bundle identifier.
  * `app_name`: Human-readable application title.
  * `strategy`: `hard_clone` (full binary duplicate + wrapper hijack) vs `soft_clone` (lightweight launcher + launch arguments).
  * `strip_sandbox`: When to strip macOS App Sandbox entitlements (`true`/`false`).
  * `proxy`: Dedicated HTTP/HTTPS/SOCKS5 proxy settings (enabled, host, port).

### Chapter 3: `03-under-the-hood-and-internals.md` (Architecture, Mechanics & Advanced Parameters)
* **Core Cloning Mechanics**:
  * **Soft Clone (Launcher Mode)**: Lightweight `.app` shell, passing `--user-data-dir` or `--profile` CLI arguments, smart symlinks for keychain/credentials.
  * **Hard Clone (Deep Sandbox Mode)**:
    1. Physical App Bundle duplication.
    2. Modifying `CFBundleIdentifier` in `Info.plist` (identity mutation).
    3. Sandbox stripping & Ad-hoc code re-signing (`codesign --force --deep`).
    4. Binary Wrapper Hijack: Replacing executable with an environment wrapper script that sets `HOME`, `TMPDIR`, and proxy env vars before launching the renamed binary (`.bin`).
  * **Data-Logic Decoupling**: Why clones can be updated or re-signed without ever losing user data.
* **Advanced Recipe Parameters Reference**:
  * `app_type`: `cocoa`, `electron`, `chromium`, `firefox`, `generic` and their isolation implications.
  * `environment_injection`: Dictionary of environment variables (e.g. `HOME: "{{ATB_DATA_DIR}}/Home"`, `TMPDIR: "{{ATB_DATA_DIR}}/Tmp"`).
  * `launch_args`: Custom command-line arguments list.
  * `symlink_whitelist`: Host directories symlinked back into the pseudo-home (e.g. `Library/Keychains`, `.ssh`, `Library/Fonts`).
  * Path Macros: `{{ATB_DATA_DIR}}`, `{{CLONE_NAME}}`, `{{BUNDLE_ID}}`.

### Chapter 4: `04-faq-and-troubleshooting.md` (FAQ & Issue Reporting)
* **Beginner FAQs**:
  * Will cloning affect my original application data? (Strict isolation explained).
  * Where is clone data stored, and how do I back it up?
  * Will my account get banned? (Explaining pure local OS-level isolation, independent proxy routing, zero memory injection, and platform policies).
  * Do I need Administrator / Root permissions?
  * How do I fix "App is damaged or can't be opened" (Gatekeeper & `xattr -cr`).
* **System Diagnostics with Doctor**:
  * Checking Xcode Command Line Tools (`xcode-select -p`), codesign utilities, and disk permissions.
* **Diagnostic Extraction & GitHub Issue Reporting**:
  * Main Clone List -> select malfunctioning clone -> click "Details" (`详情`).
  * Inspecting Injected Parameters, Launch Arguments, and Execution Commands.
  * One-click copying diagnostic commands and info.
  * Navigating to GitHub Issues and pasting structured diagnostics for fast developer support.

---

## 4. Verification Plan

* Verify that all 5 markdown files are created with correct syntax and valid relative cross-links.
* Verify accurate terminology matching the current codebase (`v0.9.7`).
* Confirm zero missing sections according to user specifications.
