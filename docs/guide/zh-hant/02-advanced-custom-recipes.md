# 第二章：冷門應用規則定製與基礎引數詳解

雖然 ATBClone 內建了 33+ 熱門應用的預設規則，但在日常工作與學習中，您可能會遇到未經適配的冷門小眾軟體（例如企業自研內部辦公工具、特定領域的設計建模軟體、或地區性即時通訊工具）。

本章將介紹如何通過內建的 **App Prober (智慧探針)** 和 **視覺化規則編輯器** 為任意冷門應用建立專屬分身規則，並詳細解析規則中的基礎引數含義。

---

## 📑 本章目錄

- [理解分身規則 (Recipe) 的作用](#理解分身規則-recipe-的作用)
- [方法一：使用 App Prober 智慧探針（強烈推薦）](#方法一使用-app-prober-智慧探針強烈推薦)
- [方法二：使用視覺化規則編輯器](#方法二使用視覺化規則編輯器)
- [規則基礎引數全解](#規則基礎引數全解)
  - [1. `bundle_id`（應用唯一標識）](#1-bundle_id應用唯一標識)
  - [2. `app_name`（應用名稱）](#2-app_name應用名稱)
  - [3. `strategy`（克隆策略）](#3-strategy克隆策略)
  - [4. `strip_sandbox`（沙盒剝離）](#4-strip_sandbox沙盒剝離)
  - [5. `proxy`（獨立代理配置）](#5-proxy獨立代理配置)
  - [6. `injection_strategy`（環境注入模式）](#6-injection_strategy環境注入模式)
- [自定義規則 YAML 完整範例](#自定義規則-yaml-完整範例)
- [下一步指引](#下一步指引)

---

## 🧩 理解分身規則 (Recipe) 的作用

**App Recipe（分身規則）** 是一份結構清晰的 YAML 宣告檔案，它相當於分身引擎的“操作說明書”，用於指導 ATBClone：

* 該應用適合採用哪種克隆引擎（**物理克隆** 還是 **軟包裝**）；
* 如何實現資料重定向（通過環境變數 `$HOME` 劫持還是 `--user-data-dir` 啟動引數）；
* 是否需要移除 Apple App Sandbox 沙盒限制；
* 哪些敏感系統路徑（如鑰匙圈憑據）需要建立符號連結 (Symlink)橋接。

所有使用者自定義的規則均存放在：
`~/ATBClone/recipes/<bundle_id>.yaml`

當您克隆某個應用時，ATBClone 會優先載入您本地的自定義規則，優先順序高於系統內建規則庫。

---

## 🔍 方法一：使用 App Prober 智慧探針（強烈推薦）

**App Prober（應用智慧探針）** 是 ATBClone 內建的二進位制深度靜態分析工具。它能夠毫秒級分析任意 Mach-O 架構、識別底層框架（Electron、CEF、Qt、Flutter、Cocoa 等）、掃描沙盒授權並自動生成最佳克隆規則。

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

### 操作步驟：
1. 點選 ATBClone 側邊欄的 **"智慧探針"**（`🔍`）導航項。
2. 點選 **"瀏覽..."** 選中您想要分析的冷門 `.app` 應用程式包。
3. 點選 **"開始探測"** 按鈕。
4. 探針將在毫秒內完成深度掃描並展示分析結果：
   * **應用名稱與 Bundle ID**：從應用 `Info.plist` 中解析。
   * **沙盒狀態**：檢查是否包含 `com.apple.security.app-sandbox` 授權。
   * **執行時框架**：自動識別 Electron、Chromium、Qt、Flutter、React Native 或原生 Cocoa 框架。
   * **推薦克隆策略**：智慧研判應採用 `hard_clone` 還是 `soft_clone`。
5. 點選 **"儲存為規則 💾"**。

儲存成功後，該規則將立即生效並註冊到您的本地規則庫。此時回到主介面點選 **"+ 新建分身"**，嚮導將直接識別併為您完成完美隔離！

---

## ✏️ 方法二：使用視覺化規則編輯器

如果您想完全手動編寫或微調規則：

1. 點選側邊欄的 **"規則庫"**（`📑`）導航項。
2. 點選右上角的 **"+ 新建規則"** 按鈕。
3. 在彈出的規則編輯面板中填寫基礎資訊：
   * **Bundle ID**：如 `com.company.internaltool`
   * **應用名稱**：如 `InternalTool`
   * **克隆策略**：選擇 `hard_clone` 或 `soft_clone`
   * **剝離沙盒**：按需勾選
   * **代理配置**：設定預設代理引數
4. 點選 **"儲存規則"**。

您也可以在規則庫列表中選中任意內建規則，點選 **"編輯"** 生成一份本地自定義覆蓋規則。

---

## 📖 規則基礎引數全解

以下為規則檔案中各基礎引數的詳細含義與取值說明：

### 1. `bundle_id`（應用唯一標識）
* **型別**：`string`（如 `com.tencent.xinWeChat`、`com.google.Chrome`）
* **說明**：macOS 應用程式的唯一反向域名識別符號。ATBClone 通過匹配此 ID 來索引對應的分身規則。

---

### 2. `app_name`（應用名稱）
* **型別**：`string`（如 `微信`、`Telegram`、`Cursor`）
* **說明**：規則的人類可讀顯示標題。

---

### 3. `strategy`（克隆策略）
* **型別**：`enum`（可選值：`hard_clone` | `soft_clone`）
* **說明**：決定分身引擎採用的底層技術路線。

| 策略型別 | 底層實現機制 | 適用場景與推薦應用 |
| :--- | :--- | :--- |
| **`hard_clone`（物理克隆）** | 完整複製應用實體，修改 `CFBundleIdentifier` 基因身份，注入二進位制啟動劫持指令碼，執行 Ad-hoc 重新簽名。 | 原生 Cocoa 應用、社交軟體（微信、QQ、Telegram、飛書、Discord）及需要獨立 TCC 系統許可權的應用。 |
| **`soft_clone`（軟包裝）** | 僅生成一個輕量級的 `.app` 啟動器外殼，通過注入 `--user-data-dir` 或 `--profile` 引數啟動母體二進位制。 | 瀏覽器（Chrome、Edge、Firefox、Brave）與現代程式碼編輯器（Cursor、VS Code、Zed）。 |

---

### 4. `strip_sandbox`（沙盒剝離）
* **型別**：`boolean`（`true` | `false`，預設建議：`false`）
* **說明**：控制在執行硬克隆時，是否強制移除應用簽名中的 `com.apple.security.app-sandbox` 沙盒限制。

> [!TIP]
>
> * **`false`（預設推薦）**：保持 macOS 原生沙盒隔離機制。分身會使用獨立的 `~/Library/Containers/<新BundleID>` 容器，實現乾淨的資料隔離。
> * **`true`（僅用於嚴格受限的應用）**：如果應用在修改 Bundle ID 後由於沙盒許可權受阻導致白屏或閃退，開啟此選項將徹底剝離沙盒限制。

---

### 5. `proxy`（獨立代理配置）
* **型別**：`object`
* **說明**：定義建立分身時預設使用的網路代理設定。

```yaml
proxy:
  enabled: true       # boolean: 是否默认开启代理 (true/false)
  type: http          # enum: 代理类型，可选 "http"、"https" 或 "socks5"
  host: 127.0.0.1     # string: 代理服务器主机 IP 或域名
  port: 7890          # integer: 代理服务器端口号
```

---

### 6. `injection_strategy`（環境注入模式）
* **型別**：`enum`（可選值：`auto` | `dylib` | `launcher`，預設：`auto`）
* **說明**：配置針對物理克隆（`hard_clone`）應用的環境變數重定向底層機制。

| 注入模式 | 執行機制 | 核心優勢與適用場景 |
| :--- | :--- | :--- |
| **`auto`（預設推薦）** | 智慧靜態探測 Mach-O 頭部 Padding 空間。空間充足時使用 `dylib`，空間不足或需額外引數時自動平滑回退為 `launcher`。 | 絕大多數場景首選。保證對未知軟體的最大相容性與後續更新韌性。 |
| **`dylib`（強制動態庫注入）** | 往 Mach-O 插入 `LC_LOAD_DYLIB`，啟動階段由 dyld 直接呼叫 `libatbclone_env.dylib` 完成環境變數隔離，**零程序替換 (`execv`)**。 | 原生通訊軟體（微信、QQ、Telegram、企業微信）。完美支援頂部狀態列圖示與 macOS 系統通知中心。 |
| **`launcher`（強制啟動器包裝）** | 編譯原生 Mach-O C 二進位制啟動器替代主程式，將原主程式重新命名為 `.bin` 並通過 `execv` 代理啟動。 | 需追加特定命令列啟動引數或 Mach-O 頭部極度緊湊的應用。 |

---

## 📄 自定義規則 YAML 完整範例

下面是一份標準的自定義規則檔案示例：

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

* 想要了解 `environment_injection`、`symlink_whitelist` 等高階引數與底層機制？請閱讀 **[第三章：實現原理解析與高階引數全解](03-under-the-hood-and-internals.md)**。
* 遇到分身無法執行或閃退？請查閱 **[第四章：常見問題 (FAQ)、系統體檢與反饋](04-faq-and-troubleshooting.md)**。
