# 第二章：冷门应用规则定制与基础参数详解

虽然 ATBClone 内置了 33+ 热门应用的预设规则，但在日常工作与学习中，您可能会遇到未经适配的冷门小众软件（例如企业自研内部办公工具、特定领域的设计建模软件、或地区性即时通讯工具）。

本章将介绍如何通过内置的 **App Prober (智能探针)** 和 **可视化规则编辑器** 为任意冷门应用创建专属分身规则，并详细解析规则中的基础参数含义。

---

## 📑 本章目录

- [理解分身规则 (Recipe) 的作用](#理解分身规则-recipe-的作用)
- [方法一：使用 App Prober 智能探针（强烈推荐）](#方法一使用-app-prober-智能探针强烈推荐)
- [方法二：使用可视化规则编辑器](#方法二使用可视化规则编辑器)
- [规则基础参数全解](#规则基础参数全解)
  - [1. `bundle_id`（应用唯一标识）](#1-bundle_id应用唯一标识)
  - [2. `app_name`（应用名称）](#2-app_name应用名称)
  - [3. `strategy`（克隆策略）](#3-strategy克隆策略)
  - [4. `strip_sandbox`（沙盒剥离）](#4-strip_sandbox沙盒剥离)
  - [5. `proxy`（独立代理配置）](#5-proxy独立代理配置)
  - [6. `injection_strategy`（环境注入模式）](#6-injection_strategy环境注入模式)
- [自定义规则 YAML 完整范例](#自定义规则-yaml-完整范例)
- [下一步指引](#下一步指引)

---

## 🧩 理解分身规则 (Recipe) 的作用

**App Recipe（分身规则）** 是一份结构清晰的 YAML 声明文件，它相当于分身引擎的“操作说明书”，用于指导 ATBClone：

* 该应用适合采用哪种克隆引擎（**物理克隆** 还是 **软包装**）；
* 如何实现数据重定向（通过环境变量 `$HOME` 劫持还是 `--user-data-dir` 启动参数）；
* 是否需要移除 Apple App Sandbox 沙盒限制；
* 哪些敏感系统路径（如钥匙串凭据）需要建立软链接桥接。

所有用户自定义的规则均存放在：
`~/ATBClone/recipes/<bundle_id>.yaml`

当您克隆某个应用时，ATBClone 会优先加载您本地的自定义规则，优先级高于系统内置规则库。

---

## 🔍 方法一：使用 App Prober 智能探针（强烈推荐）

**App Prober（应用智能探针）** 是 ATBClone 内置的二进制深度静态分析工具。它能够毫秒级分析任意 Mach-O 架构、识别底层框架（Electron、CEF、Qt、Flutter、Cocoa 等）、扫描沙盒授权并自动生成最佳克隆规则。

```text
+-------------------------------------------------------------+
|  🔍 智能应用探针 (App Prober)                               |
|                                                             |
|  目标应用路径:                                              |
|  [/Applications/CustomTool.app               ] [ 浏览... ]  |
|                                              [ 开始探测 ]   |
|  ─────────────────────────────────────────────────────────  |
|  深度分析结果:                                              |
|  • 应用名称:   CustomTool                                   |
|  • Bundle ID:  com.example.customtool                       |
|  • 沙盒状态:   已启用 (检测到 App Sandbox 限制)              |
|  • 依赖框架:   Electron, Node.js                            |
|  • 推荐策略:   hard_clone (物理克隆)                        |
|                                                             |
|  [ 保存为规则 💾 ]                                          |
+-------------------------------------------------------------+
```

### 操作步骤：
1. 点击 ATBClone 侧边栏的 **"智能探针"**（`🔍`）导航项。
2. 点击 **"浏览..."** 选中您想要分析的冷门 `.app` 应用程序包。
3. 点击 **"开始探测"** 按钮。
4. 探针将在毫秒内完成深度扫描并展示分析结果：
   * **应用名称与 Bundle ID**：从应用 `Info.plist` 中解析。
   * **沙盒状态**：检查是否包含 `com.apple.security.app-sandbox` 授权。
   * **运行时框架**：自动识别 Electron、Chromium、Qt、Flutter、React Native 或原生 Cocoa 框架。
   * **推荐克隆策略**：智能研判应采用 `hard_clone` 还是 `soft_clone`。
5. 点击 **"保存为规则 💾"**。

保存成功后，该规则将立即生效并注册到您的本地规则库。此时回到主界面点击 **"+ 新建分身"**，向导将直接识别并为您完成完美隔离！

---

## ✏️ 方法二：使用可视化规则编辑器

如果您想完全手动编写或微调规则：

1. 点击侧边栏的 **"规则库"**（`📑`）导航项。
2. 点击右上角的 **"+ 新建规则"** 按钮。
3. 在弹出的规则编辑面板中填写基础信息：
   * **Bundle ID**：如 `com.company.internaltool`
   * **应用名称**：如 `InternalTool`
   * **克隆策略**：选择 `hard_clone` 或 `soft_clone`
   * **剥离沙盒**：按需勾选
   * **代理配置**：设置默认代理参数
4. 点击 **"保存规则"**。

您也可以在规则库列表中选中任意内置规则，点击 **"编辑"** 生成一份本地自定义覆盖规则。

---

## 📖 规则基础参数全解

以下为规则文件中各基础参数的详细含义与取值说明：

### 1. `bundle_id`（应用唯一标识）
* **类型**：`string`（如 `com.tencent.xinWeChat`、`com.google.Chrome`）
* **说明**：macOS 应用程序的唯一反向域名标识符。ATBClone 通过匹配此 ID 来索引对应的分身规则。

---

### 2. `app_name`（应用名称）
* **类型**：`string`（如 `微信`、`Telegram`、`Cursor`）
* **说明**：规则的人类可读显示标题。

---

### 3. `strategy`（克隆策略）
* **类型**：`enum`（可选值：`hard_clone` | `soft_clone`）
* **说明**：决定分身引擎采用的底层技术路线。

| 策略类型 | 底层实现机制 | 适用场景与推荐应用 |
| :--- | :--- | :--- |
| **`hard_clone`（物理克隆）** | 完整复制应用实体，修改 `CFBundleIdentifier` 基因身份，注入二进制启动劫持脚本，执行 Ad-hoc 重新签名。 | 原生 Cocoa 应用、社交软件（微信、QQ、Telegram、飞书、Discord）及需要独立 TCC 系统权限的应用。 |
| **`soft_clone`（软包装）** | 仅生成一个轻量级的 `.app` 启动器外壳，通过注入 `--user-data-dir` 或 `--profile` 参数启动母体二进制。 | 浏览器（Chrome、Edge、Firefox、Brave）与现代代码编辑器（Cursor、VS Code、Zed）。 |

---

### 4. `strip_sandbox`（沙盒剥离）
* **类型**：`boolean`（`true` | `false`，默认建议：`false`）
* **说明**：控制在执行硬克隆时，是否强制移除应用签名中的 `com.apple.security.app-sandbox` 沙盒限制。

> [!TIP]
> * **`false`（默认推荐）**：保持 macOS 原生沙盒隔离机制。分身会使用独立的 `~/Library/Containers/<新BundleID>` 容器，实现干净的数据隔离。
> * **`true`（仅用于严格受限的应用）**：如果应用在修改 Bundle ID 后由于沙盒权限受阻导致白屏或闪退，开启此选项将彻底剥离沙盒限制。

---

### 5. `proxy`（独立代理配置）
* **类型**：`object`
* **说明**：定义创建分身时默认使用的网络代理设置。

```yaml
proxy:
  enabled: true       # boolean: 是否默认开启代理 (true/false)
  type: http          # enum: 代理类型，可选 "http"、"https" 或 "socks5"
  host: 127.0.0.1     # string: 代理服务器主机 IP 或域名
  port: 7890          # integer: 代理服务器端口号
```

---

### 6. `injection_strategy`（环境注入模式）
* **类型**：`enum`（可选值：`auto` | `dylib` | `launcher`，默认：`auto`）
* **说明**：配置针对物理克隆（`hard_clone`）应用的环境变量重定向底层机制。

| 注入模式 | 运行机制 | 核心优势与适用场景 |
| :--- | :--- | :--- |
| **`auto`（默认推荐）** | 智能静态探测 Mach-O 头部 Padding 空间。空间充足时使用 `dylib`，空间不足或需额外参数时自动平滑回退为 `launcher`。 | 绝大多数场景首选。保证对未知软件的最大兼容性与后续更新韧性。 |
| **`dylib`（强制动态库注入）** | 往 Mach-O 插入 `LC_LOAD_DYLIB`，启动阶段由 dyld 直接调用 `libatbclone_env.dylib` 完成环境变量隔离，**零进程替换 (`execv`)**。 | 原生通信软件（微信、QQ、Telegram、企业微信）。完美支持顶部状态栏图标与 macOS 系统通知中心。 |
| **`launcher`（强制启动器包装）** | 编译原生 Mach-O C 二进制启动器替代主程序，将原主程序重命名为 `.bin` 并通过 `execv` 代理启动。 | 需追加特定命令行启动参数或 Mach-O 头部极度紧凑的应用。 |

---

## 📄 自定义规则 YAML 完整范例

下面是一份标准的自定义规则文件示例：

```yaml
# ========================================================
# ATBClone 自定义规则 - ExampleApp
# 存放路径: ~/ATBClone/recipes/com.example.app.yaml
# ========================================================

bundle_id: com.example.app
app_name: ExampleApp
strategy: hard_clone
app_type: cocoa
strip_sandbox: false
injection_strategy: auto

proxy:
  enabled: false
  type: http
  host: 127.0.0.1
  port: 7890
```

---

## ⏭️ 下一步指引

* 想要了解 `environment_injection`、`symlink_whitelist` 等高级参数与底层机制？请阅读 **[第三章：实现原理解析与高级参数全解](03-under-the-hood-and-internals.md)**。
* 遇到分身无法运行或闪退？请查阅 **[第四章：常见问题 (FAQ)、系统体检与反馈](04-faq-and-troubleshooting.md)**。
