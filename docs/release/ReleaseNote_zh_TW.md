[English](ReleaseNote.md) | [简体中文](ReleaseNote_zh.md) | [繁體中文](ReleaseNote_zh_TW.md) | [日本語](ReleaseNote_ja.md) | [한국어](ReleaseNote_ko.md) | [Deutsch](ReleaseNote_de.md) | [Français](ReleaseNote_fr.md) | [Русский](ReleaseNote_ru.md) | [Español](ReleaseNote_es.md)

# ATBClone 更新日誌 (Release Notes)

本檔案記錄了 **ATBClone** 的所有重要更新、新功能、效能最佳化及問題修復。

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
