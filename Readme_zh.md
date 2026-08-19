[中文版](Readme_zh.md)  [English](Readme.md)

# ATBClone (macOS 应用多开引擎)

> 🚀 **ATBClone** 是一个专为 macOS 设计的现代化应用程序多开（Multi-Instancing）与分身管理引擎。支持独立数据隔离、独立网络代理（HTTP / SOCKS5）、自动化配方匹配、重签名与沙盒解除。

---

## ✨ 核心特性

- 📦 **双引擎克隆机制**：
  - **硬克隆 (Hard Clone)**：适用于原生与社交应用（微信、QQ、Telegram、AI 客户端等）。完整复制 App Bundle，修改 `Info.plist` 与 Bundle Identifier，通过二进制劫持脚本注入独立的 `HOME` / `TMPDIR` 数据目录，可选解除 Sandbox 限制并执行 Ad-hoc 重签名。
  - **软克隆 (Soft Clone)**：适用于 Chromium 系列应用及现代编辑器（Chrome、Edge、Arc、Cursor、VS Code 等）。创建轻量级 Wrapper 包，自动注入独立的 `--user-data-dir` / `--profile` 启动参数与代理环境变量。
- 🔍 **智能应用探测 (App Prober)**：遇到未预设配方的任意 macOS 应用程序时，自动分析其 Mach-O 架构、Frameworks 与代码签名沙盒权限，动态决定软/硬克隆策略并提取推荐配方。
- 🌐 **独立网络代理**：支持为每个分身单独指定 HTTP 或 SOCKS5 代理（支持认证），分身流量与系统及原应用互不干扰。
- 📑 **规则引擎 (Recipe Engine)**：内置 18+ 常用应用与 AI Agent 工具配方，支持通过 `~/.atbclone/recipes/` 本地优先级覆盖自定义规则。
- 🪄 **交互式向导 (Wizard)**：命令行交互式一步步引导，支持终端路径拖拽、自动识别并编号、即时配置代理。
- 🔄 **生命周期管理**：提供分身列表查看（`list`）、原版本升级后一键重克隆且保留聊天数据（`update`）、安全删除分身及可选清理数据（`remove`）。
- 🛡️ **安全与提权设计**：写入 `~/Applications` 无需管理员权限；写入 `/Applications` 自动使用 macOS 原生单次 `osascript` 授权；全流程使用原子脚本与 `shlex.quote` 路径防护。

---

## 📋 内置配方支持 (Built-in Recipes)

| 类别 | 应用名称 | Bundle Identifier | 克隆策略 | 沙盒解除 (Strip Sandbox) |
| :--- | :--- | :--- | :--- | :---: |
| **即时通讯** | 微信 (WeChat) | `com.tencent.xinWeChat` | Hard Clone | ✘ |
| | QQ | `com.tencent.qq` | Hard Clone | ✘ |
| | Telegram | `ph.telegra.Telegraph` | Hard Clone | ✘ |
| | LINE | `jp.naver.line.mac` | Hard Clone | ✅ |
| | Slack | `com.tinyspeck.slackmacgap` | Hard Clone | ✘ |
| | Discord | `com.hnc.Discord` | Hard Clone | ✘ |
| | Skype | `com.skype.skype` | Hard Clone | ✅ |
| **AI 客户端** | ChatGPT (Codex) | `com.openai.codex` | Hard Clone | ✅ |
| | Gemini | `com.google.GeminiMacOS` | Hard Clone | ✅ |
| | Antigravity | `com.google.antigravity` | Hard Clone | ✘ |
| | Antigravity IDE | `com.google.antigravity-ide` | Hard Clone | ✘ |
| **浏览器** | Google Chrome | `com.google.Chrome` | Soft Clone | — |
| | Microsoft Edge | `com.microsoft.edgemac` | Soft Clone | — |
| | Firefox | `org.mozilla.firefox` | Soft Clone | — |
| | Arc Browser | `company.thebrowser.Browser` | Soft Clone | — |
| **开发工具** | Cursor | `com.todesktop.230313mzl4w4u92` | Soft Clone | — |
| | VS Code | `com.microsoft.VSCode` | Soft Clone | — |
| | Zed | `dev.zed.Zed` | Soft Clone | — |

---

## 🛠️ 环境依赖

- **操作系统**：macOS 13.0+ (Apple Silicon arm64 / Intel x86_64)
- **Python**：Python 3.12+（`build_cli.sh` 编译时强制要求；推荐使用 Conda）
- **系统开发工具**：已安装 Xcode Command Line Tools（提供 `codesign`, `xcode-select`, `PlistBuddy`）

```bash
# 安装 Xcode Command Line Tools (若尚未安装)
xcode-select --install
```

---

## 📦 安装与配置

### 1. 从源码安装（开发模式）

```bash
# 1. 切换到项目目录并激活环境 (如 Conda)
conda activate ATBClone

# 2. 安装项目及其开发依赖
pip install -e ".[dev]"

# 3. 运行环境自检
atbclone doctor
```

---

## 🚀 快速上手与使用指南

### 1. 交互式向导（推荐新手使用）

无需记忆参数，根据终端提示一步步操作：
```bash
atbclone wizard
```
*流程包括：拖入 `.app` 路径 ➔ 自动匹配配方 ➔ 设置分身名称 ➔ 选择输出路径 ➔ 可选配置代理 ➔ 确认生成。*

---

### 2. 命令行快速克隆 (`clone`)

#### 基础克隆（自动递增编号，默认输出至 `~/Applications`）
```bash
atbclone clone /Applications/WeChat.app
```

#### 指定分身名称与输出目录
```bash
atbclone clone /Applications/WeChat.app --name "微信工作版" --output-dir ~/Applications
```

#### 未预设配方应用克隆（自动触发深度探测）
克隆未内置规则的应用时，ATBClone 会自动触发 App Prober 探测架构与沙盒权限，动态生成最佳配方后执行克隆：
```bash
atbclone clone /Applications/ATBCmder.app --name "ATBCmder-Work"
```

#### 为分身配置专属独立网络代理 (HTTP / SOCKS5)
```bash
# 配置 HTTP 代理
atbclone clone /Applications/Telegram.app \
  --name "Telegram-Proxy" \
  --proxy-host 127.0.0.1 \
  --proxy-port 7890 \
  --proxy-type http

# 配置 SOCKS5 代理
atbclone clone /Applications/ChatGPT.app \
  --name "ChatGPT-US" \
  --proxy-host 127.0.0.1 \
  --proxy-port 1080 \
  --proxy-type socks5
```

---

### 3. 查看分身列表 (`list`)

通过漂亮的 Rich 表格查看所有由 ATBClone 管理的分身状态：
```bash
atbclone list
```
输出示例：
```
┏━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 名称     ┃ 原 APP  ┃ Bundle ID            ┃ 策略       ┃ 创建时间         ┃ 代理                   ┃
┡━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 微信2    │ 微信    │ com.tencent.xinWeChat │ hard_clone │ 2026-08-18 22:30 │ 未开启                 │
│ TG-Proxy │ Telegram│ ph.telegra.Telegraph │ hard_clone │ 2026-08-18 22:45 │ http://127.0.0.1:7890  │
│ Chrome2  │ Chrome  │ com.google.Chrome    │ soft_clone │ 2026-08-18 23:00 │ 未开启                 │
└──────────┴─────────┴━━━━━━━━━━━━━━━━━━━━━━┴━━━━━━━━━━━━┴━━━━━━━━━━━━━━━━━━┴━━━━━━━━━━━━━━━━━━━━━━━━┘
```

---

### 4. 更新原应用后的分身同步 (`update`)

当 App Store 或官网更新了主应用版本时，一键更新分身，**保留所有聊天记录与登录状态（数据目录不丢失）**：
```bash
atbclone update 微信2
```

---

### 5. 删除分身 (`remove`)

#### 仅删除分身应用本体（默认保留历史数据）
```bash
atbclone remove 微信2
```

#### 同时彻底删除分身应用及数据目录
```bash
atbclone remove 微信2 --with-data
```
*注：删除数据目录为不可逆操作，系统会要求用户二次键入 `y` 确认。*

---

### 6. 配方管理与自定义扩展 (`recipe`)

#### 列出所有内置应用配方
```bash
atbclone recipe list
```

#### 查看特定应用的配方 YAML
```bash
atbclone recipe show com.tencent.xinWeChat
```

#### 自定义与覆盖配方
在 `~/.atbclone/recipes/<bundle_id>.yaml` 放置 YAML 规则文件即可自动优先加载覆盖：
```yaml
# 示例：~/.atbclone/recipes/com.example.customapp.yaml
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

### 7. 深度应用探测与配方生成 (`probe`)

对任意本地 `.app` 进行深度架构与代码签名权限探测，分析其运行内核（Chromium / Electron / Gecko / Native）、沙盒状态，并输出推荐的 ATBClone Recipe YAML：

#### 基础探测与终端展示
```bash
atbclone probe /Applications/ATBCmder.app
```

#### 探测并直接保存至本地配方库 (`~/.atbclone/recipes/<bundle_id>.yaml`)
```bash
atbclone probe /Applications/ATBCmder.app --save
```

#### 导出配方到指定文件
```bash
atbclone probe /Applications/ATBCmder.app -o /path/to/recipe.yaml
```

#### 机器可读 JSON 输出
```bash
atbclone probe /Applications/ATBCmder.app --json
```

---

### 8. 查看版本与系统信息 (`version`)

```bash
# 查看详细系统与运行环境信息
atbclone version

# 仅输出版本号
atbclone version --short
# 或
atbclone --version
```

---

## 🏷️ 语义化版本管理 (Version Management)

项目采用标准的语义化版本号格式 `x.y.z`（当前版本：`0.1.0`），并提供了专用的版本管理脚本 `scripts/manage_version.py`：

```bash
# 1. 检查各配置文件版本是否一致
python scripts/manage_version.py --show

# 2. 语义化升级版本 (patch: 0.1.0 -> 0.1.1, minor: 0.1.0 -> 0.2.0, major: 0.1.0 -> 1.0.0)
python scripts/manage_version.py --bump patch
python scripts/manage_version.py --bump minor
python scripts/manage_version.py --bump major

# 3. 指定显式版本
python scripts/manage_version.py 0.2.0

# 4. 预览变更（不实际写入文件）
python scripts/manage_version.py --bump patch --dry-run
```

*脚本会自动同步更新 `pyproject.toml`、`src/atbclone/__init__.py` 等目标文件的版本定义。*

---

## 🏗️ 构建与打包为独立二进制 (Build)

项目提供了基于 [Nuitka](https://nuitka.net/) 的全自动单文件二进制构建脚本，可将整个 CLI 打包为无需 Python 环境依赖的独立可执行文件：

```bash
# 执行打包脚本
bash scripts/build_cli.sh
```

构建完成后将在 `dist/` 目录生成独立二进制文件：
```bash
# 验证打包产物
./dist/ATBCloneCli --help
./dist/ATBCloneCli version
./dist/ATBCloneCli doctor
./dist/ATBCloneCli probe /Applications/ATBCmder.app
```

---

## 🧪 运行测试

本项目严格遵循 TDD 与自动化验证规范，包含完整的单元测试与集成测试：

```bash
PYTHONPATH=src conda run -n ATBClone python -m pytest tests/ -v
```

---

## 📂 目录与数据存储架构

```
~/.atbclone/
├── clones.yaml           # 全局分身状态追踪记录
├── recipes/              # 用户自定义配方存放目录 (可选覆盖)
└── Data/                 # 各分身独立的数据隔离目录
    ├── 微信2/
    │   ├── Home/         # 隔离的独立用户主目录
    │   └── Tmp/          # 隔离的临时目录
    └── Chrome2/          # Chrome 独立 User Data 目录
```

```
src/atbclone/
├── cli/                  # CLI 命令行层 (Click + Rich)
│   ├── cmd_clone.py      # 克隆主命令 (支持未配置配方自动探测)
│   ├── cmd_doctor.py     # 环境检测
│   ├── cmd_list.py       # 分身列表
│   ├── cmd_probe.py      # 应用深度架构探测与配方生成
│   ├── cmd_recipe.py     # 配方管理
│   ├── cmd_remove.py     # 分身删除
│   ├── cmd_update.py     # 分身更新
│   ├── cmd_version.py    # 版本与系统信息展示
│   └── cmd_wizard.py     # 交互式向导
├── core/                 # 核心领域模型与克隆引擎
│   ├── app_inspector.py  # App 元数据检查与自动编号
│   ├── app_prober.py     # 深度架构探测、沙盒检查与动态配方生成
│   ├── clone_task.py     # 克隆任务实体
│   ├── engines.py        # Soft & Hard 克隆执行引擎
│   ├── models.py         # 基础模型
│   └── state.py          # YAML 状态管理
├── executor/             # 底层执行器 (Direct Subprocess / AppleScript 提权)
│   └── runner.py
└── recipes/              # 配方模型、加载器与 18 个内置规则
    ├── builtin/          # 内置 YAML 配方
    ├── loader.py         # 规则匹配与优先级加载
    └── models.py         # Pydantic 校验模型
```

---

## 📄 License 与 Release Notes

- **开源协议**: MIT License.
- **更新日志 (Release Notes)**: [English](docs/release/ReleaseNote.md) | [简体中文](docs/release/ReleaseNote_zh.md) | [繁體中文](docs/release/ReleaseNote_zh_TW.md) | [日本語](docs/release/ReleaseNote_ja.md) | [한국어](docs/release/ReleaseNote_ko.md) | [Deutsch](docs/release/ReleaseNote_de.md) | [Français](docs/release/ReleaseNote_fr.md) | [Русский](docs/release/ReleaseNote_ru.md) | [Español](docs/release/ReleaseNote_es.md)

