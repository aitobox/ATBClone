[中文版](Readme_zh.md)  [English](Readme.md)

# ATBClone (macOS Application Cloning Engine)

> 🚀 **ATBClone** is a modern application multi-instancing and clone management engine designed for macOS. It supports isolated user data directories, independent network proxies (HTTP / SOCKS5), automated recipe matching, ad-hoc code re-signing, and sandbox removal.

---

## ✨ Key Features

- 📦 **Dual-Engine Cloning Mechanism**:
  - **Hard Clone**: Designed for native and social applications (WeChat, QQ, Telegram, AI clients, Chrome, Edge, Arc, etc.). Duplicates the entire App Bundle, modifies `Info.plist` and Bundle Identifier, injects isolated `HOME` / `TMPDIR` data directories via binary launcher script hijack, optionally strips App Sandbox restrictions, and performs ad-hoc code re-signing.
  - **Soft Clone**: Designed for modern code editors and browsers (Cursor, VS Code, Firefox, Brave, Tor, Zed, etc.). Generates a lightweight wrapper bundle, automatically injecting isolated `--user-data-dir` / `--profile` launch arguments and proxy environment variables.
- 🔍 **Intelligent App Prober**: Automatically inspects Mach-O architectures, frameworks, and code signing sandbox entitlements for any application without a pre-configured recipe, dynamically determining the optimal soft/hard clone strategy and generating recommended recipes.
- 🌐 **Isolated Network Proxies**: Configure dedicated HTTP or SOCKS5 proxies (with authentication support) per cloned application without interfering with host system or primary application traffic.
- 📑 **Recipe Engine**: 33+ built-in recipes for popular apps and AI Agent tools, with local override support via `~/.atbclone/recipes/`.
- 🪄 **Interactive Wizard**: Step-by-step interactive CLI guide supporting terminal drag-and-drop application paths, automatic name incrementing, custom data directory configuration, and on-the-fly proxy setup.
- 🔄 **Lifecycle Management**: View cloned apps (`list`), re-clone after primary app updates while preserving user and chat data (`update`), and safely remove clones with interactive prompts or flag controls (`remove` with `--with-data` / `--keep-data`).
- 🛡️ **Security & Privilege Elevation**: Writing to `~/Applications` requires no admin privileges; writing to `/Applications` uses native single-prompt macOS `osascript` authorization; robust path escaping via `shlex.quote` throughout.


---

## 📋 Built-in Recipes

| Category | Application | Bundle Identifier | Strategy | Strip Sandbox |
| :--- | :--- | :--- | :--- | :---: |
| **Instant Messaging & Collaboration** | WeChat | `com.tencent.xinWeChat` | Hard Clone | ✘ |
| | QQ | `com.tencent.qq` | Hard Clone | ✘ |
| | WeCom (企业微信) | `com.tencent.WeWorkMac` | Hard Clone | ✅ |
| | Lark (飞书) | `com.electron.lark` | Hard Clone | ✘ |
| | Telegram (Native Swift) | `ru.keepcoder.Telegram` | Hard Clone | ✘ |
| | Telegram Desktop | `org.telegram.desktop` | Hard Clone | ✘ |
| | LINE | `jp.naver.line.mac` | Hard Clone | ✅ |
| | Slack | `com.tinyspeck.slackmacgap` | Hard Clone | ✘ |
| | Discord | `com.hnc.Discord` | Hard Clone | ✘ |
| | Skype | `com.skype.skype` | Hard Clone | ✅ |
| **AI Clients** | Claude | `com.anthropic.claudefordesktop` | Hard Clone | ✘ |
| | ChatGPT (Codex) | `com.openai.codex` | Hard Clone | ✅ |
| | ChatGPT (Standard) | `com.openai.chat` | Hard Clone | ✅ |
| | Gemini | `com.google.GeminiMacOS` | Hard Clone | ✅ |
| | Antigravity | `com.google.antigravity` | Hard Clone | ✘ |
| | Antigravity IDE | `com.google.antigravity-ide` | Hard Clone | ✘ |
| **Browsers** | Google Chrome | `com.google.Chrome` | Hard Clone | ✘ |
| | Microsoft Edge | `com.microsoft.edgemac` | Hard Clone | ✘ |
| | Brave Browser | `com.brave.Browser` | Soft Clone | — |
| | Firefox | `org.mozilla.firefox` | Soft Clone | — |
| | Tor Browser | `org.torproject.torbrowser` | Soft Clone | — |
| | Arc Browser | `company.thebrowser.Browser` | Hard Clone | ✘ |
| **Media & Entertainment** | Bilibili (哔哩哔哩) | `com.bilibili.bilibiliPC` | Hard Clone | ✘ |
| | Douyin (抖音) | `com.bytedance.douyin.desktop` | Hard Clone | ✅ |
| | Netease Music (网易云音乐) | `com.netease.163music` | Hard Clone | ✅ |
| | Steam | `com.valvesoftware.steam` | Hard Clone | ✘ |
| **Productivity & Utilities** | WPS Office | `com.kingsoft.wpsoffice.mac` | Hard Clone | ✅ |
| | VideoFusion (剪映专业版) | `com.lemon.lvpro` | Hard Clone | ✅ |
| | CapCut | `com.lemon.lvoverseas` | Hard Clone | ✅ |
| **Developer Tools** | Cursor | `com.todesktop.230313mzl4w4u92` | Soft Clone | — |
| | VS Code | `com.microsoft.VSCode` | Soft Clone | — |
| | Android Studio | `com.google.android.studio` | Hard Clone | ✘ |
| | Zed | `dev.zed.Zed` | Soft Clone | — |

---

## 🛠️ Prerequisites

- **Operating System**: macOS 13.0+ (Apple Silicon arm64 / Intel x86_64)
- **Python**: Python 3.12+ (strictly required for `build_cli.sh` compilation; Conda recommended)
- **System Tools**: Xcode Command Line Tools installed (provides `codesign`, `xcode-select`, `PlistBuddy`)

```bash
# Install Xcode Command Line Tools (if not already installed)
xcode-select --install
```

---

## 📦 Installation & Setup

### 1. Install from Source (Development Mode)

```bash
# 1. Navigate to the project directory and activate your environment (e.g. Conda)
conda activate ATBClone

# 2. Install the package and development dependencies
pip install -e ".[dev]"

# 3. Run environment self-check
atbclone doctor
```

---

## 🚀 Quick Start & CLI Usage

### 1. Interactive Wizard (Recommended for Beginners)

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
# Interactive prompt: Also delete data directory /Users/.../.atbclone/Data/WeChat2? [y/N]
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
Place a custom YAML recipe in `~/.atbclone/recipes/<bundle_id>.yaml` to automatically take precedence:
```yaml
# Example: ~/.atbclone/recipes/com.example.customapp.yaml
bundle_id: com.example.customapp
app_name: CustomApp
strategy: hard_clone
strip_sandbox: true
environment_injection:
  HOME: "{{ATB_DATA_DIR}}/Home"
  TMPDIR: "{{ATB_DATA_DIR}}/Tmp"
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

#### Probe and Save Directly to Local Repository (`~/.atbclone/recipes/<bundle_id>.yaml`)
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

## 🏷️ Semantic Version Management

The project adheres to semantic versioning `x.y.z` (current version: `0.1.0`) and provides a dedicated version management script at `scripts/manage_version.py`:

```bash
# 1. Check version consistency across configuration files
python scripts/manage_version.py --show

# 2. Bump semantic version (patch: 0.1.0 -> 0.1.1, minor: 0.1.0 -> 0.2.0, major: 0.1.0 -> 1.0.0)
python scripts/manage_version.py --bump patch
python scripts/manage_version.py --bump minor
python scripts/manage_version.py --bump major

# 3. Set an explicit version
python scripts/manage_version.py 0.2.0

# 4. Preview changes without writing to disk
python scripts/manage_version.py --bump patch --dry-run
```

*The script automatically updates version declarations in `pyproject.toml`, `src/atbclone/__init__.py`, and other configuration files.*

---

## 🏗️ Standalone Binary Packaging (Build)

The project includes an automated [Nuitka](https://nuitka.net/)-based single-file build script to package the CLI into a standalone binary with zero Python runtime dependency:

```bash
# Run build script
bash scripts/build_cli.sh
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
~/.atbclone/
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
├── executor/             # Low-level executors (Subprocess / AppleScript elevation)
│   └── runner.py
└── recipes/              # Recipe models, loaders & 33 built-in rules
    ├── builtin/          # Built-in YAML recipes
    ├── loader.py         # Recipe matching & priority loader
    └── models.py         # Pydantic validation models
```

---

## 📄 License & Release Notes

- **License**: GPL-3.0 License.
- **Release Notes**: [English](docs/release/ReleaseNote.md) | [简体中文](docs/release/ReleaseNote_zh.md) | [繁體中文](docs/release/ReleaseNote_zh_TW.md) | [日本語](docs/release/ReleaseNote_ja.md) | [한국어](docs/release/ReleaseNote_ko.md) | [Deutsch](docs/release/ReleaseNote_de.md) | [Français](docs/release/ReleaseNote_fr.md) | [Русский](docs/release/ReleaseNote_ru.md) | [Español](docs/release/ReleaseNote_es.md)

