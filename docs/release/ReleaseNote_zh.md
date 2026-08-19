[English](ReleaseNote.md) | [简体中文](ReleaseNote_zh.md) | [繁體中文](ReleaseNote_zh_TW.md) | [日本語](ReleaseNote_ja.md) | [한국어](ReleaseNote_ko.md) | [Deutsch](ReleaseNote_de.md) | [Français](ReleaseNote_fr.md) | [Русский](ReleaseNote_ru.md) | [Español](ReleaseNote_es.md)

# ATBClone 更新日志 (Release Notes)

本文档记录了 **ATBClone** 的所有重要更新、新功能、性能优化及问题修复。

---

## [v0.3.0] - 2026-08-19

### 🌐 国际化与多语言支持 (i18n)
- **macOS 系统语言自动探测**：
  - 内置 `atbclone.core.i18n` 多语言引擎，通过 `AppleLanguages` 与 `AppleLocale` 自动探测 macOS 系统偏好语言。
  - CLI 交互式向导、终端提示、表格表头及状态日志自动在中文与英文间智能切换。
  - 支持通过环境变量 `ATBCLONE_LANG`（如 `ATBCLONE_LANG=zh` 或 `ATBCLONE_LANG=en`）强制指定运行语言。
- **多语言文档体系**：
  - 默认采用英文版 `Readme.md`，中文完整文档重命名为 `Readme_zh.md`。
  - 发布涵盖 9 种语言的 Release Notes：英文、简体中文、繁体中文、日语、韩语、德语、法语、俄语、西班牙语。

### 🛠️ CLI 与构建打包优化
- **向导国际化全面接入**：`atbclone wizard` 交互提示、自定义显示名称、自定义 `.icns` 图标选择及代理设置全部支持双语。
- **独立二进制构建升级**：使用 Nuitka 重新打包 `./dist/ATBCloneCli`，内嵌多语言字典并增强沙盒构建兼容性（`PYTHONNOUSERSITE=1`）。
- **自动化测试套件**：新增 `test_i18n.py` 测试用例，全部 186 项自动化测试均支持双语环境验证并通过。

---

## [v0.2.0] - 2026-08-18

### 🚀 重大新功能
- **交互式克隆向导 (`atbclone wizard`)**：
  - 终端交互式操作流，支持直接拖拽 `.app` 应用路径到终端。
  - 分身名称自动自增探测（如 `WeChat2`、`WeChat3`）。
  - 支持配置自定义应用显示名称及自定义 `.icns` 应用图标。
  - 交互式配置专属网络代理（HTTP / SOCKS5），支持账号密码鉴权。
- **智能深度应用探测器 (`atbclone probe`)**：
  - 自动分析任意 macOS 应用的 Mach-O 架构（arm64、x86_64、Universal）、开发框架（Electron、Flutter、Chromium、Qt、Cocoa）及沙盒权限（`com.apple.security.app-sandbox`）。
  - 为未预置配方的应用动态推荐最佳分身策略（`hard_clone` / `soft_clone`）并生成标准 Recipe YAML。
  - `atbclone clone` 支持自动触发探测引擎，无需手动指定配方即可一键分身未知应用。
- **独立二进制打包构建**：
  - 增加 `scripts/build_cli.sh` 构建脚本，基于 Nuitka 编译零外部依赖的 macOS 原生 arm64 单文件可执行文件（`dist/ATBCloneCli`）。

### ⚡ 优化与修复
- 优化 `/Applications` 目标路径的提权逻辑，采用原生 macOS `osascript` 授权弹窗，单次输入密码即可完成提权操作。
- 全面采用 `shlex.quote` 对执行路径进行转义保护，杜绝空格与特殊字符引发的路径异常。

---

## [v0.1.0] - 2026-08-17

### 🌟 初始版本发布
- **双引擎克隆架构**：
  - **硬克隆引擎 (Hard Clone)**：完整复制 App Bundle，修改 `Info.plist`，劫持二进制启动脚本注入独立 `HOME` / `TMPDIR`，按需解除沙盒，重新执行 ad-hoc 签名。
  - **软克隆引擎 (Soft Clone)**：针对 Chromium 浏览器和现代编辑器生成轻量级启动器，注入独立 `--user-data-dir` 与代理环境变量。
- **18+ 款主流应用预置配方**：
  - 即时通讯：微信 (WeChat)、QQ、Telegram、LINE、Slack、Discord、Skype。
  - AI 客户端：ChatGPT (Codex)、Gemini、Antigravity、Antigravity IDE。
  - 浏览器与开发工具：Google Chrome、Microsoft Edge、Firefox、Arc、Cursor、VS Code、Zed。
- **完整 CLI 命令集**：
  - `clone`：创建应用分身，支持自定义名称、输出目录及网络代理。
  - `list`：Rich 表格查看已创建分身、策略类型、创建时间及代理状态。
  - `update`：主应用升级后一键同步分身，保留全部聊天记录与配置数据。
  - `remove`：安全卸载分身，支持可选清理数据目录。
  - `recipe`：查看内置配方列表及本地自定义配方覆盖。
  - `doctor`：自动化环境自检（检查 `codesign`、`xcode-select`、`PlistBuddy` 等工具链）。
