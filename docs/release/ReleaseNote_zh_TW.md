[English](ReleaseNote.md) | [简体中文](ReleaseNote_zh.md) | [繁體中文](ReleaseNote_zh_TW.md) | [日本語](ReleaseNote_ja.md) | [한국어](ReleaseNote_ko.md) | [Deutsch](ReleaseNote_de.md) | [Français](ReleaseNote_fr.md) | [Русский](ReleaseNote_ru.md) | [Español](ReleaseNote_es.md)

# ATBClone 更新日誌 (Release Notes)

本檔案記錄了 **ATBClone** 的所有重要更新、新功能、效能最佳化及問題修復。

---

## [v0.6.0] - 2026-08-19

### 📂 自訂資料儲存目錄支援
- **分身資料儲存路徑自訂 (`--data-dir`)**：
  - `atbclone clone` 指令新增 `--data-dir` 參數，支援為分身指定自訂資料儲存路徑（例如外接式 SSD 或特定工作目錄）。
  - `atbclone wizard` 互動式精靈全面支援自訂資料目錄的提示與設定。
  - Recipe 模型與分身引擎全面支援動態資料目錄變數解析。

### 🗑️ 增強的分身移除與資料清理 (`atbclone remove`)
- **安全資料清理選項與確認機制**：
  - `atbclone remove` 新增 `--purge-data` 參數，支援非互動式一鍵徹底清理分身應用程式本體及對應的資料目錄。
  - 新增 `--keep-data` 參數，僅移除應用程式本體並保留使用者聊天記錄與設定檔。
  - 互動式移除精靈增加多語言確認提示，支援使用者自主選擇是否清理資料，並提供安全提示。
  - 完善孤立殘留資料目錄與權限異常的安全診斷處理。

### 🆔 Bundle ID 產生標準化與多語言更新
- **標準化 Bundle ID 產生邏輯**：
  - 引入 `AppInspector.generate_bundle_id` 統一產生規則，確保 `clone`、`wizard` 與 `update` 指令間 Bundle ID 格式嚴格一致。
- **多語言在地化完善**：
  - 9 種語言全面整合資料目錄設定、移除確認與清理狀態提示。
- **測試套件擴充**：
  - 自動化測試案例擴充至 213 項，全面涵蓋自訂目錄與移除清理邏輯。

---

## [v0.5.0] - 2026-08-19

### 🔐 蘋果官方代碼簽署與公證支援 (Code Signing & Notarization)
- **強化執行階段 (Hardened Runtime) 與代碼簽署**：
  - 深度整合 Apple Developer ID Application 開發者憑證簽署機制，啟用 `--options runtime` 強化執行階段、時間戳記及自訂 JIT / 執行授權檔 (`scripts/entitlements.plist`)。
  - 新增 `scripts/notarize.sh` 自動化公證腳本，支援透過鑰匙圈憑證 (`--keychain-profile`) 呼叫 `xcrun notarytool` 一鍵完成蘋果官方公證與 Gatekeeper 安全驗證。
  - `scripts/build_cli.sh` 與 `scripts/release.sh` 全面支援 `--sign-identity`、`--skip-sign` 及 `--notarize` 編譯與發布選項，未設定憑證時自動降級至 ad-hoc 本機簽署。

### 🚀 Chromium 瀏覽器硬分身與啟動參數注入
- **硬分身引擎支援 `launch_args` 注入**：
  - 增強 `HardCloneEngine`，使其在環境變數隔離之外，同時支援向二進位啟動器動態注入 `--user-data-dir={{ATB_DATA_DIR}}` 等啟動參數。
  - 將 **Google Chrome**、**Microsoft Edge**、**Arc Browser** 預設配方升級為 `hard_clone` 策略，實現完整的 App Bundle 獨立複製與 Dock/Finder 專屬識別。
- **CLI 支援策略覆寫**：
  - `atbclone clone` 命令列新增 `--strategy` 參數（可選 `hard_clone` 或 `soft_clone`），允許使用者手動覆寫預設策略。

### ⚡ 行程管理與測試套件擴充
- **行程轉發最佳化**：最佳化 `SoftCloneEngine` 啟動包裝腳本，使用標準 `exec "$@"` 進行參數轉發與行程接管。
- **自動化測試擴充**：測試套件案例擴展至 199 項，全面涵蓋代碼簽署流程、公證腳本語法與硬分身參數注入。

---

## [v0.4.0] - 2026-08-19

### 🌐 9 國語言全面在地化與文件體系
- **CLI 全指令 9 語言多語言支援**：
  - 擴展 `atbclone.core.i18n` 多語言模組，全面支援英語、簡體中文、繁體中文、日語、韓語、德語、法語、俄語、西班牙語 9 種語言。
  - 所有終端指令（`wizard`、`clone`、`probe`、`list`、`recipe`、`doctor`、`update`、`remove`、`version`）皆已實現多語言提示、Rich 表格與錯誤日誌輸出。
- **多語言 Release Notes 標準化**：
  - 規範化 `docs/release/` 目錄下的 9 國語言更新日誌管理與語言導覽體系。

### 🔄 自動化發布與版本同步流水線
- **9 語言 ReleaseNotes 自動校驗機制**：
  - 升級 `scripts/manage_version.py` 與 `scripts/release.sh`，在發布時自動校驗並同步 `docs/release/` 下全部 9 份 ReleaseNotes。
  - 增加 `--check-notes` 版本完整性檢查指令，杜絕遺漏多語言發布文件。
- **測試套件擴充**：
  - 自動化測試案例擴充至 191 項，全面涵蓋多語言字典渲染與發布流程校驗。

---

## [v0.3.0] - 2026-08-19

### 🌐 國際化與多語言支援 (i18n)
- **macOS 系統語言自動偵測**：
  - 內建 `atbclone.core.i18n` 多語言引擎，透過 `AppleLanguages` 與 `AppleLocale` 自動偵測 macOS 系統偏好語言。
  - CLI 互動式精靈、終端提示、表格欄位及狀態日誌自動於中文與英文間智慧切換。
  - 支援透過環境變數 `ATBCLONE_LANG`（例如 `ATBCLONE_LANG=zh` 或 `ATBCLONE_LANG=en`）手動指定語言。
- **多語言文件體系**：
  - 預設採用英文版 `Readme.md`，中文完整文件命名為 `Readme_zh.md`。
  - 發布涵蓋 9 種語言的 Release Notes：英文、簡體中文、繁體中文、日語、韓語、德語、法語、俄語、西班牙語。

### 🛠️ CLI 與建置打包最佳化
- **精靈國際化全面整合**：`atbclone wizard` 互動提示、自訂顯示名稱、自訂 `.icns` 圖示選取及代理設定全面支援雙語。
- **獨立二進位檔建置升級**：使用 Nuitka 重新打包 `./dist/ATBCloneCli`，內嵌多語言字典並增強沙盒建置相容性（`PYTHONNOUSERSITE=1`）。
- **自動化測試套件**：新增 `test_i18n.py` 測試案例，全部 186 項自動化測試皆支援雙語環境驗證並全數通過。

---

## [v0.2.0] - 2026-08-18

### 🚀 重大新功能
- **互動式分身精靈 (`atbclone wizard`)**：
  - 終端互動式操作流程，支援直接拖放 `.app` 應用程式路徑至終端機。
  - 分身名稱自動累加偵測（例如 `WeChat2`、`WeChat3`）。
  - 支援設定自訂應用程式顯示名稱及自訂 `.icns` 應用程式圖示。
  - 互動式設定專屬網路代理（HTTP / SOCKS5），支援帳號密碼鑑權。
- **智慧深度應用程式探測器 (`atbclone probe`)**：
  - 自動分析任意 macOS 應用程式的 Mach-O 架構（arm64、x86_64、Universal）、開發框架（Electron、Flutter、Chromium、Qt、Cocoa）及沙盒權限（`com.apple.security.app-sandbox`）。
  - 為未預設配方的應用程式動態推薦最佳分身策略（`hard_clone` / `soft_clone`）並產生標準 Recipe YAML。
  - `atbclone clone` 支援自動觸發探測引擎，無須手動指定配方即可一鍵分身未知應用程式。
- **獨立二進位檔打包建置**：
  - 新增 `scripts/build_cli.sh` 建置腳本，基於 Nuitka 編譯零外部依賴的 macOS 原生 arm64 單一執行檔（`dist/ATBCloneCli`）。

### ⚡ 最佳化與修復
- 最佳化 `/Applications` 目標路徑的提權邏輯，採用原生 macOS `osascript` 授權對話框，單次輸入密碼即可完成提權操作。
- 全面採用 `shlex.quote` 對執行路徑進行跳脫保護，杜絕空格與特殊字元引發的路徑異常。

---

## [v0.1.0] - 2026-08-17

### 🌟 初始版本發布
- **雙引擎分身架構**：
  - **硬分身引擎 (Hard Clone)**：完整複製 App Bundle，修改 `Info.plist`，劫持二進位啟動腳本注入獨立 `HOME` / `TMPDIR`，依需求解除沙盒，重新執行 ad-hoc 簽署。
  - **軟分身引擎 (Soft Clone)**：針對 Chromium 瀏覽器與現代編輯器產生輕量化啟動器，注入獨立 `--user-data-dir` 與代理環境變數。
- **18+ 款主流應用程式預設配方**：
  - 即時通訊：微信 (WeChat)、QQ、Telegram、LINE、Slack、Discord、Skype。
  - AI 客戶端：ChatGPT (Codex)、Gemini、Antigravity、Antigravity IDE。
  - 瀏覽器與開發工具：Google Chrome、Microsoft Edge、Firefox、Arc、Cursor、VS Code、Zed。
- **完整 CLI 指令集**：
  - `clone`：建立應用程式分身，支援自訂名稱、輸出目錄及網路代理。
  - `list`：Rich 表格檢視已建立分身、策略類型、建立時間及代理狀態。
  - `update`：主應用程式升級後一鍵同步分身，保留全部聊天記錄與設定資料。
  - `remove`：安全移除分身，支援可選清理資料目錄。
  - `recipe`：檢視內建配方列表及本機自訂配方覆寫。
  - `doctor`：自動化環境自我檢查（檢查 `codesign`、`xcode-select`、`PlistBuddy` 等工具鏈）。
