# Comprehensive English User Guide Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a complete, beginner-friendly, beautifully structured 5-part English user manual under `docs/guide/en/` covering all GUI operations, batch management, custom recipes, engine internals, FAQs, and issue reporting.

**Architecture:** Modular documentation structure in Markdown under `docs/guide/en/` with clear cross-links, visual UI walk-throughs, parameter reference tables, and diagnostic issue reporting guides.

**Tech Stack:** Markdown (GitHub Flavored Markdown), Mermaid diagrams, macOS native UI context (PySide6/Toga GUI, macOS 13+).

## Global Constraints

- Target Language: Professional, accessible English (clear for beginners, rigorous for power users).
- Directory: `docs/guide/en/`
- Version Context: ATBClone `v0.9.7` on macOS Apple Silicon & Intel.
- Style: Use tables, callout blocks (`> [!TIP]`, `> [!NOTE]`, `> [!WARNING]`), and step-by-step numbers.

---

### Task 1: Create Master Navigation Index (`docs/guide/en/README.md`)

**Files:**
- Create: `docs/guide/en/README.md`

**Interfaces:**
- Consumes: `docs/superpowers/specs/2026-08-24-user-guide-en-design.md`
- Produces: Master index linking to `01-basic-operations.md`, `02-advanced-custom-recipes.md`, `03-under-the-hood-and-internals.md`, and `04-faq-and-troubleshooting.md`.

- [ ] **Step 1: Write `docs/guide/en/README.md`**

Write the complete master guide index including:
- Welcome to ATBClone & What makes it unique (Quadruple Isolation: Data, Visual, TCC, Network Proxy).
- Quick Start Checklist for everyday users.
- Reading Roadmaps (Beginners ➔ Chapter 1 & 4; Power Users ➔ Chapter 2 & 3; Troubleshooting ➔ Chapter 4).
- Core Concepts & Glossary (App Bundle, Bundle ID, Hard Clone, Soft Clone, Recipe, Data Directory).
- Interactive Table of Contents linking to all chapters.

- [ ] **Step 2: Commit**

```bash
git add docs/guide/en/README.md
git commit -m "docs(guide): add master navigation index in en/README.md"
```

---

### Task 2: Create Chapter 1 — Basic Operations (`docs/guide/en/01-basic-operations.md`)

**Files:**
- Create: `docs/guide/en/01-basic-operations.md`

**Interfaces:**
- Consumes: GUI wizard implementation (`src/atbclone/gui/windows/wizard.py`, `src/atbclone/gui/views/clone_list.py`)
- Produces: Step-by-step creation guide and complete clone lifecycle management guide.

- [ ] **Step 1: Write `docs/guide/en/01-basic-operations.md`**

Write comprehensive documentation detailing:
- Part 1: Step-by-Step 7-Stage Creation Wizard:
  - Step 1: Selecting the Primary Application (`.app` selection / drag-and-drop).
  - Step 2: Auto-detecting & Matching Recipes (Built-in 33+ recipes vs Prober analysis).
  - Step 3: Clone Identity & Localization (Clone Name e.g. `WeChat2`, Finder/Dock Display Name, UI Language selection).
  - Step 4: Installation Destination (`~/Applications` user folder vs `/Applications` system folder).
  - Step 5: Dedicated Data Directory (`~/ATBClone/Data/<Name>` or external SSD storage).
  - Step 6: Network Proxy Configuration (HTTP / SOCKS5 with host/port for independent IP).
  - Step 7: Confirmation & Instant Cloning.
- Part 2: Managing Cloned Applications:
  - Launching Clones (from ATBClone GUI, Spotlight search, or Dock).
  - Direct Data Access ("Open Dir" button to open isolated data storage in Finder).
  - Editing Clones (modifying display title, language locale, and proxy settings).
  - Updating Clones after Host App Updates (zero data loss, seamless synchronization).
  - Batch Operations: Multi-selecting in Table view for batch updating and batch deletion.
  - Safe Deletion: Difference between removing application bundle only vs. purging data directory.

- [ ] **Step 2: Commit**

```bash
git add docs/guide/en/01-basic-operations.md
git commit -m "docs(guide): add chapter 1 basic operations and lifecycle management"
```

---

### Task 3: Create Chapter 2 — Advanced Custom Recipes (`docs/guide/en/02-advanced-custom-recipes.md`)

**Files:**
- Create: `docs/guide/en/02-advanced-custom-recipes.md`

**Interfaces:**
- Consumes: Prober and recipe editor implementations (`src/atbclone/gui/views/probe_view.py`, `src/atbclone/gui/windows/recipe_edit.py`, `src/atbclone/recipes/models.py`)
- Produces: Guide for creating custom recipes for niche/unlisted apps and basic parameters reference.

- [ ] **Step 1: Write `docs/guide/en/02-advanced-custom-recipes.md`**

Write comprehensive documentation detailing:
- Why custom recipes are needed for unlisted or niche applications.
- Method 1: Using the Built-in App Prober (`App Prober` tab):
  - Selecting any target `.app` bundle.
  - Deep inspection of Mach-O architecture (arm64/x86_64), Frameworks (Electron, Chromium, Cocoa, etc.), and Sandbox entitlements.
  - Clicking "Save as Recipe" to register it immediately into the local recipe library (`~/ATBClone/recipes/`).
- Method 2: Using the Visual Recipe Editor (`Recipes` tab ➔ `New Recipe`):
  - Creating and editing recipes with GUI forms.
- Basic Recipe Parameters Reference:
  - `bundle_id`: Unique macOS bundle identifier.
  - `app_name`: Human-readable application title.
  - `strategy`: Choosing between `hard_clone` (full duplication & hijack) and `soft_clone` (launcher wrapper).
  - `strip_sandbox`: When to remove App Sandbox restrictions.
  - `proxy`: Enabling dedicated proxy, setting type (`http`/`https`/`socks5`), host, and port.

- [ ] **Step 2: Commit**

```bash
git add docs/guide/en/02-advanced-custom-recipes.md
git commit -m "docs(guide): add chapter 2 advanced custom recipes and basic parameters"
```

---

### Task 4: Create Chapter 3 — Under the Hood & Advanced Parameters (`docs/guide/en/03-under-the-hood-and-internals.md`)

**Files:**
- Create: `docs/guide/en/03-under-the-hood-and-internals.md`

**Interfaces:**
- Consumes: `docs/design.md`, cloning engines (`src/atbclone/core/engines.py`, `src/atbclone/recipes/models.py`)
- Produces: Deep technical explanation of cloning mechanics and advanced parameter reference.

- [ ] **Step 1: Write `docs/guide/en/03-under-the-hood-and-internals.md`**

Write technical and structural documentation detailing:
- Core Isolation Mechanics:
  - **Soft Clone (Launcher Mode)**:
    - Lightweight `.app` bundle wrapper without binary duplication.
    - CLI argument injection (`--user-data-dir`, `--profile`).
    - Smart credential symlinking.
  - **Hard Clone (Deep Sandbox & Wrapper Hijack Mode)**:
    - Physical bundle duplication.
    - Identity mutation (`CFBundleIdentifier` alteration in `Info.plist`).
    - Sandbox stripping and Ad-hoc code re-signing (`codesign --force --deep`).
    - Binary Wrapper Hijack: Replacing main binary with a launch script that exports `HOME`, `TMPDIR`, and proxy env vars before invoking the renamed `.bin`.
  - **Data-Logic Decoupling**: Why clones can be destroyed and reconstructed during updates without losing any user chat records or settings.
- Advanced Recipe Parameters Reference:
  - `app_type`: `cocoa`, `electron`, `chromium`, `firefox`, `generic` and their structural behaviors.
  - `environment_injection`: Overriding environment variables with dynamic macros like `{{ATB_DATA_DIR}}`.
  - `launch_args`: Passing custom CLI flags.
  - `symlink_whitelist`: Host directory symlinks back into isolated environments (e.g. `Library/Keychains`, `.ssh`, `Library/Fonts`).
  - Path Macros: `{{ATB_DATA_DIR}}`, `{{CLONE_NAME}}`, `{{BUNDLE_ID}}`.

- [ ] **Step 2: Commit**

```bash
git add docs/guide/en/03-under-the-hood-and-internals.md
git commit -m "docs(guide): add chapter 3 under the hood and advanced parameters"
```

---

### Task 5: Create Chapter 4 — FAQ & Troubleshooting (`docs/guide/en/04-faq-and-troubleshooting.md`)

**Files:**
- Create: `docs/guide/en/04-faq-and-troubleshooting.md`

**Interfaces:**
- Consumes: Clone Inspector (`src/atbclone/core/clone_inspector.py`), Clone Detail window (`src/atbclone/gui/windows/clone_detail.py`), Doctor service
- Produces: FAQ guide, Doctor diagnostics walk-through, and step-by-step GitHub issue reporting instructions.

- [ ] **Step 1: Write `docs/guide/en/04-faq-and-troubleshooting.md`**

Write comprehensive documentation detailing:
- High-Frequency FAQs:
  - *Will creating a clone affect my original app's data?* (Explain complete separation).
  * *Where is clone data stored, and how do I back it up or migrate it?* (`~/ATBClone/Data/`).
  * *Will my account get banned for multi-instancing?* (Explain OS-level environment isolation vs memory hooks, dedicated proxy IP, and terms of service).
  * *Why does ATBClone not require root/admin passwords when cloning to `~/Applications`?*
  * *What should I do if macOS says "App is damaged or cannot be opened"?* (Quarantine xattr removal).
- System Diagnostics (Doctor Tab):
  - Running Doctor checks for Xcode Command Line Tools, codesigning tools, and storage permissions.
- Finding Issues & GitHub Issue Reporting:
  - If an app fails to clone or launch after cloning:
  - Step 1: Open ATBClone GUI Clone List.
  - Step 2: Select the malfunctioning clone and click **"Details"** (`详情`).
  - Step 3: Inspect Injected Parameters, Launch Arguments, and Execution Command.
  - Step 4: Click "Copy Command" or copy the detail summary.
  - Step 5: Go to GitHub Issues (`https://github.com/aitobox/ATBClone/issues`), select "New Issue", and paste the cloned app details and log snippets.

- [ ] **Step 2: Commit**

```bash
git add docs/guide/en/04-faq-and-troubleshooting.md
git commit -m "docs(guide): add chapter 4 FAQ, doctor diagnostics, and issue reporting"
```

---

### Task 6: Cross-Linking Verification & Main Documentation Linkage

**Files:**
- Modify: `README.md` (Add links to the new English User Guide)
- Modify: `Readme_zh.md` (Add links to user guide)

**Interfaces:**
- Consumes: Tasks 1-5 outputs.
- Produces: Validated documentation links and accessible guide entry points in top-level READMEs.

- [ ] **Step 1: Verify all markdown files and relative links**

Check that every chapter in `docs/guide/en/` links cleanly to previous and next chapters, and that table of contents anchors work.

- [ ] **Step 2: Update top-level READMEs with Guide links**

Add direct links pointing to `docs/guide/en/README.md`.

- [ ] **Step 3: Commit**

```bash
git add README.md Readme_zh.md docs/guide/en/
git commit -m "docs: add user manual links to project READMEs"
```
