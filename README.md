[中文版](Readme_zh.md)  [English](Readme.md) | 📖 **[User Guide (EN)](docs/guide/en/README.md)** | **[用户使用手册 (中文)](docs/guide/zh-cn/README.md)**

# ATBClone (macOS Application Cloning Engine)

> 🚀 **ATBClone** is a modern application multi-instancing and clone management engine designed for macOS. It supports isolated user data directories, independent network proxies (HTTP / SOCKS5), automated recipe matching, ad-hoc code re-signing, and sandbox removal.
>
> 📖 **Looking for a beginner-friendly tutorial?** Check out the complete **[ATBClone User Manual (English)](docs/guide/en/README.md)** | **[中文使用手册](docs/guide/zh-cn/README.md)**.

<p align="center">
  <img src="resource/images/screenshot-20260821-110121.png" alt="ATBClone Clones Dashboard" width="49%">
  <img src="resource/images/screenshot-20260821-110133.png" alt="ATBClone Built-in Recipes" width="49%">
</p>

---

## 📥 Download

Visit the [GitHub Releases](https://github.com/aitobox/ATBClone/releases) page to download the latest release of ATBClone.

ATBClone provides two distribution packages with **identical core functionality**:

| Distribution Package | Target Audience | Description |
| :--- | :--- | :--- |
| **`ATBClone-arm-0.9.7.dmg`** | 👶 **General Users (Strongly Recommended)** | macOS Native GUI desktop application installer (`.dmg`). Provides a modern, visual card-based interface with zero terminal knowledge required. |
| **`ATBCloneCli.tar.gz`** | ⚡ **Power Users / Developers** | Standalone binary command-line tool archive (`ATBCloneCli`). Zero Python dependencies required; ideal for terminal power users, automation scripts, and CI/CD pipelines. |

> 💡 **User Guidance**:
> - **Beginners / Everyday Users**: Please **prioritize downloading and using the GUI app (`.dmg`)**. It offers an intuitive visual interface for one-click cloning, app launching, status monitoring, and settings.
> - **Advanced Users / Developers**: Use the **CLI tool (`ATBCloneCli` / `atbclone`)** for fast terminal interaction, batch scripting, deep application probing, and headless workflows.

---

## ✨ Key Features

- 📦 **Dual-Engine Cloning Mechanism**:
  - **Hard Clone**: Designed for native and social applications (WeChat, QQ, Telegram, AI clients, Chrome, Edge, Arc, etc.). Duplicates the entire App Bundle, modifies `Info.plist` and Bundle Identifier, injects isolated `HOME` / `TMPDIR` data directories via binary launcher script hijack, optionally strips App Sandbox restrictions, and performs ad-hoc code re-signing.
  - **Soft Clone**: Designed for modern code editors and browsers (Cursor, VS Code, Firefox, Brave, Tor, Zed, etc.). Generates a lightweight wrapper bundle, automatically injecting isolated `--user-data-dir` / `--profile` launch arguments and proxy environment variables.
- 🔍 **Intelligent App Prober**: Automatically inspects Mach-O architectures, frameworks, and code signing sandbox entitlements for any application without a pre-configured recipe, dynamically determining the optimal soft/hard clone strategy and generating recommended recipes.
- 🌐 **Isolated Network Proxies**: Configure dedicated HTTP or SOCKS5 proxies (with authentication support) per cloned application without interfering with host system or primary application traffic.
- 📑 **Recipe Engine**: 33+ built-in recipes for popular apps and AI Agent tools, with local override support via `~/ATBClone/recipes/`.
- 🪄 **Interactive Wizard**: Step-by-step interactive CLI guide supporting terminal drag-and-drop application paths, automatic name incrementing, custom data directory configuration, and on-the-fly proxy setup.
- 🔄 **Lifecycle Management**: View cloned apps (`list`), re-clone after primary app updates while preserving user and chat data (`update`), and safely remove clones with interactive prompts or flag controls (`remove` with `--with-data` / `--keep-data`).
- 🛡️ **Security & Privilege Elevation**: Writing to `~/Applications` requires no admin privileges; writing to `/Applications` uses native single-prompt macOS `osascript` authorization; robust path escaping via `shlex.quote` throughout.


---

## 🖥️ Graphical User Interface (GUI — Recommended for General Users)

> 💡 **Tip for Everyday Users**: If you prefer not to use the terminal, download `ATBClone-arm-0.9.7.dmg` from [GitHub Releases](https://github.com/aitobox/ATBClone/releases), open the DMG, drag `ATBClone.app` to your `Applications` folder, and launch it directly.

The native macOS desktop interface provides a visual, streamlined experience:

1. **Dashboard & Clone Cards**:
   - Displays all cloned applications in a modern card layout showing app icons, cloning strategies, proxy statuses, and creation timestamps.
   - Launch cloned apps, update after primary app upgrades (preserving chat history and data), or safely remove clones with a single click.
2. **Visual Clone Creation**:
   - Drag and drop or browse for any `.app` bundle from your system.
   - Automatically matches built-in recipes or runs the App Prober on unlisted applications.
   - Customize clone name, display title, custom icon, dedicated data directory (e.g. on external SSDs), and independent HTTP / SOCKS5 proxies.
3. **Built-in Recipe Library**:
   - Explore 33+ pre-configured application recipes (WeChat, QQ, Chrome, Cursor, ChatGPT, Claude, etc.) categorized by type, complete with sandbox stripping rules and isolation strategies.
4. **App Prober (Deep Architecture Inspection)**:
   - Inspect any unknown macOS app's Mach-O architecture, frameworks, and sandbox entitlements, and generate custom recipe YAML files with one click.
5. **System Diagnostics (Doctor)**:
   - Self-check system prerequisites, Xcode command-line tools, codesigning utilities, and storage permissions to ensure optimal stability.
6. **Multi-language & System Tray**:
   - Fully localized across multiple languages (English, 简体中文, 繁體中文, 日本語, 한국어, Deutsch, Français, Русский, Español) with macOS menu bar tray integration.

*(For developers running the GUI from source: run `bash scripts/run_gui.sh` or `python -m atbclone.gui`)*

---

## 🚀 Command Line Interface (CLI — For Power Users & Scripting)

> ⚡ **For Advanced Users & Automation**: The CLI tool (`atbclone` or standalone binary `ATBCloneCli`) provides full control over the cloning engine with scriptable commands, rich terminal tables, and automation support.

### 1. Interactive Wizard (CLI Guided Mode)

No need to memorize CLI options—follow the interactive prompts in your terminal:
```bash
atbclone wizard
```
*Workflow: Drag and drop `.app` path ➔ Auto-match recipe ➔ Set clone name ➔ Set display name and icon ➔ Select destination directory ➔ Custom data directory (if supported) ➔ Optional proxy setup ➔ Confirm and create.*

---

### 2. Command Line Quick Clone (`clone`)

#### Basic Clone (Auto-incremented name, defaults to `~/Applications`)
```bash
atbclone clone /Applications/WeChat.app
```

#### Specify Clone Name and Output Directory
```bash
atbclone clone /Applications/WeChat.app --name "WeChat-Work" --output-dir ~/Applications
```

#### Custom Data Storage Directory (`--data-dir`)
For applications that support data isolation (Chromium series, Firefox, WeChat, etc.), you can specify a custom data storage directory (e.g. on an external SSD or dedicated workspace):
```bash
atbclone clone /Applications/Chrome.app --name "Chrome-Custom" --data-dir /Volumes/ExternalSSD/ChromeData
```
*Note: The prober automatically detects if the application supports data isolation; attempting to set `--data-dir` on unsupported applications (e.g. Zed) will fail with a friendly error.*


#### Clone Applications without Pre-configured Recipes (Auto-triggers Prober)
When cloning an app without a built-in recipe, ATBClone automatically runs App Prober to inspect the architecture and sandbox entitlements, dynamically generates the optimal recipe, and executes the clone:
```bash
atbclone clone /Applications/ATBCmder.app --name "ATBCmder-Work"
```

#### Configure Dedicated Network Proxies (HTTP / SOCKS5)
```bash
# Configure HTTP proxy
atbclone clone /Applications/Telegram.app \
  --name "Telegram-Proxy" \
  --proxy-host 127.0.0.1 \
  --proxy-port 7890 \
  --proxy-type http

# Configure SOCKS5 proxy
atbclone clone /Applications/ChatGPT.app \
  --name "ChatGPT-US" \
  --proxy-host 127.0.0.1 \
  --proxy-port 1080 \
  --proxy-type socks5
```

---

### 3. List Cloned Applications (`list`)

View all clones managed by ATBClone in a Rich-formatted table:
```bash
atbclone list
```
Example output:
```
┏━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 名称     ┃ 原 APP  ┃ Bundle ID            ┃ 策略       ┃ 创建时间         ┃ 代理                   ┃
┡━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 微信2    │ 微信    │ com.tencent.xinWeChat │ hard_clone │ 2026-08-18 22:30 │ 未开启                 │
│ TG-Proxy │ Telegram│ ru.keepcoder.Telegram │ hard_clone │ 2026-08-18 22:45 │ http://127.0.0.1:7890  │
│ Chrome2  │ Chrome  │ com.google.Chrome    │ hard_clone │ 2026-08-18 23:00 │ 未开启                 │
└──────────┴─────────┴━━━━━━━━━━━━━━━━━━━━━━┴━━━━━━━━━━━━┴━━━━━━━━━━━━━━━━━━┴━━━━━━━━━━━━━━━━━━━━━━━━┘
```

---

### 4. Synchronize Clones After Primary App Updates (`update`)

When the primary application is updated via the Mac App Store or website, update your clone with a single command while **preserving all chat history, logins, and data**:
```bash
atbclone update WeChat2
```

---

### 5. Remove Clones (`remove`)

#### Interactive Removal (Recommended)
When executing remove in an interactive terminal, ATBClone prompts whether to also delete the data directory:
```bash
atbclone remove WeChat2
# Interactive prompt: Also delete data directory /Users/.../ATBClone/Data/WeChat2? [y/N]
```

#### Explicitly Remove Application and Data Directory (`--with-data`)
```bash
atbclone remove WeChat2 --with-data
```

#### Explicitly Remove Application Only and Keep Data (`--keep-data`)
```bash
atbclone remove WeChat2 --keep-data
```
*Note: If the application or data directory is located in a root/admin path (e.g. `/Applications`), privilege escalation will be requested automatically once to clean up safely.*


---

### 6. Recipe Management & Custom Extensions (`recipe`)

#### List All Built-in Recipes
```bash
atbclone recipe list
```

#### View Recipe Details for a Specific Bundle ID
```bash
atbclone recipe show com.tencent.xinWeChat
```

#### Custom & Override Recipes
Place a custom YAML recipe in `~/ATBClone/recipes/<bundle_id>.yaml` to automatically take precedence:
```yaml
# Example: ~/ATBClone/recipes/com.example.customapp.yaml
bundle_id: com.example.customapp
app_name: CustomApp
strategy: hard_clone
app_type: cocoa # Options: cocoa, electron, chromium, firefox, generic
strip_sandbox: false # false (recommended): utilizes macOS native container isolation; true: strips App Sandbox
environment_injection:
  HOME: '{{ATB_DATA_DIR}}/Home'
  TMPDIR: '{{ATB_DATA_DIR}}/Tmp'
proxy:
  enabled: true
  type: http
  host: 127.0.0.1
  port: 7890
```

---

### 7. Deep Application Probing & Recipe Generation (`probe`)

Perform deep architecture and code signing inspection on any local `.app` bundle, analyze its engine (Chromium / Electron / Gecko / Native) and sandbox status, and output a recommended ATBClone Recipe YAML:

#### Basic Probing with Terminal Summary
```bash
atbclone probe /Applications/ATBCmder.app
```

#### Probe and Save Directly to Local Repository (`~/ATBClone/recipes/<bundle_id>.yaml`)
```bash
atbclone probe /Applications/ATBCmder.app --save
```

#### Export Generated Recipe to a Specific Path
```bash
atbclone probe /Applications/ATBCmder.app -o /path/to/recipe.yaml
```

#### Output in Machine-Readable JSON
```bash
atbclone probe /Applications/ATBCmder.app --json
```

---

### 8. View Version & System Information (`version`)

```bash
# View detailed system and runtime environment information
atbclone version

# Output version number only
atbclone version --short
# or
atbclone --version
```

---

## 📋 Built-in Recipes

| Category | Application | Bundle Identifier | Strategy | App Type | Strip Sandbox |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **Instant Messaging & Collaboration** | WeChat | `com.tencent.xinWeChat` | Hard Clone | `cocoa` | ✘ |
| | QQ | `com.tencent.qq` | Hard Clone | `electron` | ✘ |
| | WeCom (企业微信) | `com.tencent.WeWorkMac` | Hard Clone | `chromium` | ✘ |
| | Lark (飞书) | `com.electron.lark` | Hard Clone | `electron` | ✘ |
| | Telegram (Native Swift) | `ru.keepcoder.Telegram` | Hard Clone | `cocoa` | ✘ |
| | Telegram Desktop | `org.telegram.desktop` | Hard Clone | `generic` | ✘ |
| | LINE | `jp.naver.line.mac` | Hard Clone | `cocoa` | ✘ |
| | Slack | `com.tinyspeck.slackmacgap` | Hard Clone | `electron` | ✘ |
| | Discord | `com.hnc.Discord` | Hard Clone | `electron` | ✘ |
| | Skype | `com.skype.skype` | Hard Clone | `electron` | ✘ |
| **AI Clients** | Claude | `com.anthropic.claudefordesktop` | Hard Clone | `electron` | ✘ |
| | ChatGPT (Codex) | `com.openai.codex` | Hard Clone | `cocoa` | ✘ |
| | ChatGPT (Standard) | `com.openai.chat` | Hard Clone | `cocoa` | ✘ |
| | Gemini | `com.google.GeminiMacOS` | Hard Clone | `cocoa` | ✘ |
| | Antigravity | `com.google.antigravity` | Hard Clone | `electron` | ✘ |
| | Antigravity IDE | `com.google.antigravity-ide` | Hard Clone | `electron` | ✘ |
| **Browsers** | Google Chrome | `com.google.Chrome` | Hard Clone | `chromium` | ✘ |
| | Microsoft Edge | `com.microsoft.edgemac` | Hard Clone | `chromium` | ✘ |
| | Brave Browser | `com.brave.Browser` | Soft Clone | `chromium` | — |
| | Firefox | `org.mozilla.firefox` | Soft Clone | `firefox` | — |
| | Tor Browser | `org.torproject.torbrowser` | Soft Clone | `firefox` | — |
| | Arc Browser | `company.thebrowser.Browser` | Hard Clone | `chromium` | ✘ |
| **Media & Entertainment** | Bilibili (哔哩哔哩) | `com.bilibili.bilibiliPC` | Hard Clone | `electron` | ✘ |
| | Douyin (抖音) | `com.bytedance.douyin.desktop` | Hard Clone | `electron` | ✘ |
| | Netease Music (网易云音乐) | `com.netease.163music` | Hard Clone | `chromium` | ✘ |
| | Steam | `com.valvesoftware.steam` | Hard Clone | `cocoa` | ✘ |
| **Productivity & Utilities** | WPS Office | `com.kingsoft.wpsoffice.mac` | Hard Clone | `cocoa` | ✘ |
| | VideoFusion (剪映专业版) | `com.lemon.lvpro` | Hard Clone | `chromium` | ✘ |
| | CapCut | `com.lemon.lvoverseas` | Hard Clone | `chromium` | ✘ |
| **Developer Tools** | Cursor | `com.todesktop.230313mzl4w4u92` | Soft Clone | `electron` | — |
| | VS Code | `com.microsoft.VSCode` | Soft Clone | `electron` | — |
| | Android Studio | `com.google.android.studio` | Hard Clone | `generic` | ✘ |
| | Zed | `dev.zed.Zed` | Soft Clone | `generic` | — |

---

## 🛠️ Prerequisites & Development Setup

- **Operating System**: macOS 13.0+ (Apple Silicon arm64 / Intel x86_64)
- **Python**: Python 3.12+ (strictly required for `build_cli.sh` compilation; Conda recommended)
- **System Tools**: Xcode Command Line Tools installed (provides `codesign`, `xcode-select`, `PlistBuddy`)

```bash
# 1. Install Xcode Command Line Tools (if not already installed)
xcode-select --install

# 2. Activate Conda environment and install in development mode
conda activate ATBClone
pip install -e ".[dev,gui]"

# 3. Run environment self-check
atbclone doctor
```

---

## 🏷️ Semantic Version Management

The project adheres to semantic versioning `x.y.z` (current version: `0.9.7`) and provides a dedicated version management script at `scripts/manage_version.py`:

```bash
# 1. Check version consistency across configuration files
python scripts/manage_version.py --show

# 2. Bump semantic version (patch: 0.9.7 -> 0.9.8, minor: 0.9.7 -> 0.10.0, major: 0.9.7 -> 1.0.0)
python scripts/manage_version.py --bump patch
python scripts/manage_version.py --bump minor
python scripts/manage_version.py --bump major

# 3. Set an explicit version
python scripts/manage_version.py 0.9.7

# 4. Preview changes without writing to disk
python scripts/manage_version.py --bump patch --dry-run
```

*The script automatically updates version declarations in `pyproject.toml`, `src/atbclone/__init__.py`, and other configuration files.*

---

## 🏗️ Standalone Binary Packaging (Build)

The project includes automated build scripts to package both the CLI and GUI into standalone binaries:

```bash
# 1. Build CLI standalone binary (dist/ATBCloneCli)
bash scripts/build_cli.sh

# 2. Build GUI DMG installer (dist/ATBClone-0.9.7.dmg)
bash scripts/build_gui.sh
```

The resulting standalone binary will be generated under `dist/`:
```bash
# Verify the built binary
./dist/ATBCloneCli --help
./dist/ATBCloneCli version
./dist/ATBCloneCli doctor
./dist/ATBCloneCli probe /Applications/ATBCmder.app
```

---

## 🧪 Running Tests

This project follows TDD and automated test verification practices, with full unit and integration test suites:

```bash
PYTHONPATH=src conda run -n ATBClone python -m pytest tests/ -v
```

---

## 📂 Directory & Storage Architecture

```
~/ATBClone/
├── config.yaml           # User configuration & preferences (language, tray, etc.)
├── clones.yaml           # Global clone state tracking registry
├── recipes/              # User custom recipe directory (optional overrides)
└── Data/                 # Isolated data directories per clone
    ├── WeChat2/
    │   ├── Home/         # Isolated user home directory
    │   └── Tmp/          # Isolated temporary directory
    └── Chrome2/          # Isolated Chrome User Data directory
```

```
src/atbclone/
├── cli/                  # CLI command layer (Click + Rich)
│   ├── cmd_clone.py      # Main clone command (supports auto-probing)
│   ├── cmd_doctor.py     # Environment checks
│   ├── cmd_list.py       # Clone listing
│   ├── cmd_probe.py      # Deep app architecture probing & recipe generation
│   ├── cmd_recipe.py     # Recipe management
│   ├── cmd_remove.py     # Clone removal
│   ├── cmd_update.py     # Clone update & sync
│   ├── cmd_version.py    # Version & system information
│   └── cmd_wizard.py     # Interactive wizard
├── core/                 # Core domain models & cloning engines
│   ├── app_inspector.py  # App metadata inspection & auto-numbering
│   ├── app_prober.py     # Deep probing, sandbox inspection & recipe extraction
│   ├── clone_task.py     # Clone task entity
│   ├── engines.py        # Soft & Hard cloning execution engines
│   ├── models.py         # Domain models
│   └── state.py          # YAML state management
├── gui/                  # Native macOS GUI desktop application layer (Toga / Briefcase)
│   ├── components/       # Reusable UI widgets (cards, sidebar, top bar)
│   ├── services/         # GUI service bridge (clone, doctor, probe, recipe, tray)
│   └── views/            # GUI views (dashboard, recipes, probe, doctor, settings, logs)
├── executor/             # Low-level executors (Subprocess / AppleScript elevation)
│   └── runner.py
└── recipes/              # Recipe models, loaders & 33 built-in rules
    ├── builtin/          # Built-in YAML recipes
    ├── loader.py         # Recipe matching & priority loader
    └── models.py         # Pydantic validation models
```

## 📖 User Manual & Documentation

For a comprehensive walkthrough of ATBClone GUI, custom recipes, engine mechanics, and troubleshooting:

- 🇺🇸 **[English User Guide](docs/guide/en/README.md)**
  - [Chapter 1: Basic Operations & Clone Management](docs/guide/en/01-basic-operations.md)
  - [Chapter 2: Custom Recipes for Niche Apps](docs/guide/en/02-advanced-custom-recipes.md)
  - [Chapter 3: Under the Hood & Advanced Parameters](docs/guide/en/03-under-the-hood-and-internals.md)
  - [Chapter 4: FAQ & Diagnostic Troubleshooting](docs/guide/en/04-faq-and-troubleshooting.md)
- 🇨🇳 **[简体中文用户使用手册](docs/guide/zh-cn/README.md)**
  - [第一章：基础操作与分身管理](docs/guide/zh-cn/01-basic-operations.md)
  - [第二章：冷门应用规则定制与基础参数详解](docs/guide/zh-cn/02-advanced-custom-recipes.md)
  - [第三章：实现原理解析与高级参数全解](docs/guide/zh-cn/03-under-the-hood-and-internals.md)
  - [第四章：常见问题 (FAQ)、系统体检与反馈](docs/guide/zh-cn/04-faq-and-troubleshooting.md)

---

## 📄 License & Release Notes

- **Documentation**: [English Guide](docs/guide/en/README.md) | [中文手册](docs/guide/zh-cn/README.md)
- **License**: GPL-3.0 License.
- **Release Notes**: [English](docs/release/ReleaseNote.md) | [简体中文](docs/release/ReleaseNote_zh.md) | [繁體中文](docs/release/ReleaseNote_zh_TW.md) | [日本語](docs/release/ReleaseNote_ja.md) | [한국어](docs/release/ReleaseNote_ko.md) | [Deutsch](docs/release/ReleaseNote_de.md) | [Français](docs/release/ReleaseNote_fr.md) | [Русский](docs/release/ReleaseNote_ru.md) | [Español](docs/release/ReleaseNote_es.md)

