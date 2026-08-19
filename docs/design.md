# ATBClone (艾特智能分身) 项目架构与设计说明书

## 1. 项目概述 (Project Overview)

**项目名称**：ATBClone (隶属 AIToBox/艾特创思 ATB 工具矩阵)
**项目定位**：macOS 平台地表最强、极客级别的原生应用多开与沙盒隔离引擎。
**技术栈**：Python 3 + PySide6 (UI) + 原生 Bash/AppleScript (底层提权与逻辑)
**分发方式**：独立分发 (DMG 包提供下载) + 开发者 ID 签名 (Developer ID Application) + 苹果官方公证 (Notarization)。**绝不上架 Mac App Store**，以换取最高系统权限。

---

## 2. 设计目标 (Design Goals)

ATBClone 旨在解决传统多开工具（如简单的 `cp` 命令或 App Store 内沙盒妥协产物）的固有缺陷，实现真正的“四重隔离”：

1. **数据与缓存隔离**：分身应用拥有独立的沙盒或伪装 `$HOME` 目录，多账号同时登录，本地数据库互不锁死。
2. **视觉与交互隔离**：在 Spotlight (聚焦搜索) 和 Dock (程序坞) 中，分身拥有完全独立的图标和自定义名称。
3. **安全权限 (TCC) 隔离**：分身与原应用拥有独立的系统权限控制（如麦克风、摄像头、本地网络开关互不干扰）。
4. **网络流量隔离**：允许为指定的分身应用单独注入代理环境变量，实现单应用独立 IP（防关联指纹隔离）。

---

## 3. 核心分身策略与原理命令 (Cloning Strategies & Mechanics)

系统内置一套 **App Recipes (配方引擎)**，根据拖入应用的 `Bundle ID` 自动匹配最优克隆模式，或允许高级用户手动干预。

### 模式一：软分身 (Soft Clone / 启动器模式)

* **适用场景**：Chrome、Edge、VS Code 等自带数据隔离参数的应用；或仅需简单多开账号、无需严格独立 Dock 图标和 TCC 权限的场景。
* **核心原理**：不拷贝数百 MB 的原应用实体，仅构建一个轻量级的 `.app` 外壳，通过启动参数和软链接（Symlink）重定向数据。
* **执行步骤与原理命令**：
1. 创建伪应用目录结构：`mkdir -p ~/.atbclone/Apps/ChromeATB.app/Contents/MacOS`
2. 生成独立的 `Info.plist`，赋予自定义名称和图标。
3. 创建启动脚本并赋予执行权限 `chmod +x`：
```bash
#!/bin/bash
ORIGINAL_BIN="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
USER_DATA="$HOME/.atbclone/Data/ChromeATB"
# 直接带参数启动原版二进制，瞬间秒开
exec "$ORIGINAL_BIN" --user-data-dir="$USER_DATA" >/dev/null 2>&1 &

```


4. **智能软链接补全 (Smart Symlink)**：如果劫持了 `$HOME`，自动将 `~/Library/Keychains`、`~/.ssh` 软链接到伪 `$HOME` 目录中，防止凭据丢失。



### 模式二：硬分身 + 壳劫持 (Hard Clone + Wrapper Hijack / 深度沙盒模式)

* **适用场景**：微信、Telegram、Notion 等绝大多数普通应用；需要严格 TCC 权限隔离和防关联网络隔离的场景。
* **核心原理**：结合系统级身份伪装与进程启动劫持。这也就是 ATBClone 独创的“三板斧”技术。
* **执行步骤与原理命令** (需经由 `osascript` 提权执行)：
1. **物理拷贝**：
`cp -R "/Applications/WeChat.app" "/Applications/WeChat_ATB.app"`
2. **修改身份 (基因重组)**：
`/usr/libexec/PlistBuddy -c 'Set :CFBundleIdentifier com.tencent.xinWeChat.ATB' /Applications/WeChat_ATB.app/Contents/Info.plist`
3. **沙盒剥离 (Sandbox Stripping - 核心！)**：
检测是否存在苹果沙盒限制。如果有，提取 Entitlements，用 Python 正则移除 `<key>com.apple.security.app-sandbox</key>`，为后续重签做准备。
4. **壳劫持与网络隔离注入 (Wrapper Hijack)**：
* 重命名原二进制：`mv "Contents/MacOS/WeChat" "Contents/MacOS/WeChat.bin"`
* 写入同名中间代理脚本 `Contents/MacOS/WeChat`，进行环境欺骗：
```bash
#!/bin/bash
DIR=$(dirname "$0")
# 数据隔离
export HOME="/Users/Shared/ATBClone/WeChat_Data"
export TMPDIR="/Users/Shared/ATBClone/WeChat_Tmp"
# 单应用独立 IP 代理 (可选)
export HTTP_PROXY="http://127.0.0.1:1080"
export HTTPS_PROXY="http://127.0.0.1:1080"

exec "$DIR/WeChat.bin" "$@"

```


* 赋权：`chmod +x "Contents/MacOS/WeChat"`


5. **清理隔离属性**：
`xattr -cr "/Applications/WeChat_ATB.app"`
6. **本地临时重签 (Ad-Hoc 签名)**：
`codesign --force --deep --sign - "/Applications/WeChat_ATB.app"` (若有修改过 Entitlements，此处需附加 `--entitlements` 参数注入新的授权文件)。



---

## 4. 技术难点与架构解法 (Technical Solutions)

为了让 Python + PySide6 打造出原生级别丝滑体验，在工程实现上必须攻克以下壁垒：

### 难点一：跨语言提权与进度 UI 阻塞

* **现象**：`osascript` 提权执行 Shell 是阻塞的，UI 会转彩虹圈，且无法获取实时拷贝和签名进度。
* **ATB 解法**：
* **脚本落盘化**：Python 拼接好所有完整的 Bash 命令后，不直接执行，而是写入 `/tmp/atb_clone_task.sh`，并在每条耗时命令后加入 `echo "[ATB_PROGRESS] 拷贝完成 30%..." >> /tmp/atb_clone.log`。
* **异步执行与监听**：PySide6 启动一个 `QThread`，先触发 `osascript` 运行 `.sh`，主线程利用 `QFileSystemWatcher` 或轮询实时读取 `.log` 文件的最新行，通过信号槽 (`Signal`) 推送给进度条。



### 难点二：Xcode CLT 依赖缺失问题

* **现象**：`codesign` 的深度签名依赖 Xcode Command Line Tools，若直接静默执行会在素人电脑上暴毙。
* **ATB 解法**：
* 启动克隆前，执行防御性检查 `xcode-select -p`。
* 缺失时，弹窗拦截并执行 `os.system("xcode-select --install")`，优雅唤起系统原生的 2GB 命令行工具下载弹窗，等待用户安装完毕后再继续。



### 难点三：Chromium 系应用的 IPC 崩溃 (特例处理)

* **现象**：采用“硬分身”处理 Chrome 时，因为内部 Helper 子进程的 Mach Port 通信校验，直接导致白屏或 Aw, Snap! 崩溃。
* **ATB 解法**：在“App Recipes”规则引擎中写死硬编码判断，检测到 `com.google.Chrome` 等 Chromium 内核 ID 时，**强制降级**推荐使用“软分身”模式，或者在 UI 上给出极客提示，引导用户使用系统原生 PWA 机制。

---

## 5. 项目结构与代码骨架 (Project Structure)

```text
ATBClone/
├── main.py                     # PySide6 主程序入口
├── core/
│   ├── recipes.yaml            # 云端下发/本地内置的应用克隆特征规则库
│   ├── environment_check.py    # xcode-select 与 codesign 依赖探针
│   ├── plist_manager.py        # 封装 PlistBuddy 的读取与篡改逻辑
│   ├── entitlements_stripper.py# 提取并正则剔除 Sandbox 限制节点
│   └── code_signer.py          # xattr 清理与 codesign Ad-Hoc 签名封装
├── executor/
│   ├── shell_generator.py      # 生成提权用的 bash 脚本与 Wrapper 壳
│   └── async_task_runner.py    # QThread 异步提权执行器 + 日志监听器
└── ui/
    ├── main_window.py          # 极简拖拽风格主窗口
    ├── advanced_settings.py    # 独立网络代理/目录隔离策略设置面板
    └── progress_dialog.py      # 实时 Shell 输出与进度追踪面板

```

---

## 6. 未来延展：构建“极客共创生态”

ATBClone 的终极壁垒不是代码，而是 **Recipes (配置规则)**。每个应用（如 QQ、飞书、Line）对目录劫持的容忍度都不同。

* **开放 YAML 规则库**：允许用户在界面调整环境变量、需软链接的敏感系统目录。
* **一键导出导入**：用户调通了某个小众应用的“完美分身配置”后，可以生成一段类似 Dockerfile 的 yaml 文本分享到社区。工具在运行时会自动拉取 Github 上的最佳实践配方，实现“一键克隆，开箱即用”。
对于硬分身来说，“母体更新”是一个毁灭性的打击（老版本分身可能无法登录服务器）；而对于冷门应用，官方无法覆盖所有适配规则，必须把“调教权”交还给用户。


---

## 7. 生命周期管理：母体更新追踪与无损重构 (Update Synchronization)

**设计痛点**：硬分身相当于为应用拍了一个“物理快照”。当原版应用（如微信）通过 App Store 更新后，分身应用依然停留在老版本。如果用户手动去删除旧分身、重新克隆，不仅繁琐，还容易引发恐慌（担心聊天记录等数据丢失）。

**ATB 解法：版本巡检与“数据-逻辑分离”架构**

由于在之前的“壳劫持”设计中，我们已经将应用本体（`/Applications/WeChat_ATB.app`）与用户数据（`~/.atbclone/Data/WeChat/`）进行了**物理级解耦**，因此分身的升级其实可以做到“丝滑且无损”。

* **静默版本巡检 (Version Polling)**：
* 在 ATBClone 主界面启动时，或后台驻留一个极轻量的 `QTimer` 轮询任务。
* 使用 Python 的 `plistlib` 模块，静默对比原应用与分身应用 `Info.plist` 中的 `CFBundleShortVersionString`（可见版本号）和 `CFBundleVersion`（构建版本号）。


* **平滑升级机制 (Seamless Upgrade)**：
* 当检测到版本不一致时，UI 弹出提示：“检测到母体 [微信] 已升级至 v3.8.1，当前分身 [WeChat_ATB] 仍为 v3.8.0。是否一键同步更新？”
* 用户点击“同步”后，ATBClone 在后台静默执行以下逻辑：
1. 杀死当前运行的分身进程。
2. 直接删除旧的 `/Applications/WeChat_ATB.app`（由于数据全在 `~/.atbclone/` 下，这个删除动作**完全不会丢失任何用户聊天记录和登录状态**）。
3. 按照“硬分身”规则，重新走一遍 `拷贝 -> 篡改 -> 壳劫持 -> 剥离沙盒 -> 重签` 的自动化流程。
4. 新分身启动，自动挂载原有的假 `$HOME` 数据目录，完美继承旧数据。





---

## 8. 极客工坊：自定义应用隔离规则 (Custom Recipe Editor)

**设计痛点**：每天都有无数的新应用诞生，每个应用存放数据的方式、沙盒的严格程度千奇百怪。我们不可能在代码里穷举所有的分身策略。

**ATB 解法：所见即所得的“配方编辑器” (GUI Rule Builder)**

为高级用户（Power Users）提供一个可视化的面板，允许他们像配置 Docker 容器一样，为未知应用编写**自定义隔离规则 (Recipe)**。这些规则在本地被保存为 YAML 格式。

**自定义面板核心功能模块**：

1. **应用探针 (App Inspector)**：
* 用户将未知 App 拖入编辑器，Python 自动解析并展示其 `Bundle ID`、是否包含沙盒标识（Sandbox Entitlements）、可执行文件入口路径。


2. **分身模式选择 (Strategy Selector)**：
* 单选框：[ ] 软分身（仅启动器） [ ] 硬分身（深度重签）。


3. **启动参数注入区 (CLI Args Builder)**：
* 专门针对类似 Chrome 的应用。用户可以填入：`--user-data-dir={{ATB_DATA_DIR}}` （支持系统内置宏变量替代真实路径）。


4. **环境劫持配置区 (Environment Hijacker)**：
* **强行挂载目录**：允许用户自定义需要伪装的环境变量。例如勾选并填入 `HOME = {{ATB_DATA_DIR}}/Home`，`TMPDIR = {{ATB_DATA_DIR}}/Tmp`。
* **智能软链接避坑 (Symlink Bypass)**：提供一个表格，允许用户填入**不要被隔离**的系统级白名单路径（例如 `~/Library/Keychains`）。在构建假 `$HOME` 时，工具会自动把这些白名单目录软链接回用户的真实宿主目录，防止应用报错。


5. **一键导出与分享 (Import/Export)**：
* 用户调教好一个新应用后，点击“导出 Recipe”，生成一段极简的 YAML 代码：
```yaml
# ==========================================
# ATBClone Recipe - Cursor (示例配置)
# ==========================================

# 目标应用的 Bundle ID 和名称
bundle_id: com.cursor.mac
app_name: Cursor

# 克隆策略: hard_clone (硬分身) 或 soft_clone (软分身)
strategy: hard_clone

# 是否强制移除 macOS 沙盒限制 (适用于上架 Mac App Store 的应用)
strip_sandbox: true

# 环境变量注入 (用于欺骗应用，实现数据隔离)
environment_injection:
  # 强制将应用的家目录重定向到 ATB 专属隔离区
  HOME: "{{ATB_DATA_DIR}}/Cursor_Home"

# 软链接白名单 (将伪装的隔离区内的特定目录链接回真实宿主环境)
symlink_whitelist:
  - Library/Keychains  # 保留钥匙串访问，防止登录状态掉线
  - .ssh               # 保留 SSH 密钥，确保 Git 功能正常使用

```


* 这使得 ATBClone 具备了病毒式传播的社交属性——用户可以在论坛里直接互传 YAML 配方，一键解决新应用的多开难题。

