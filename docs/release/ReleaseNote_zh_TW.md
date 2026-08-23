[English](ReleaseNote.md) | [简体中文](ReleaseNote_zh.md) | [繁體中文](ReleaseNote_zh_TW.md) | [日本語](ReleaseNote_ja.md) | [한국어](ReleaseNote_ko.md) | [Deutsch](ReleaseNote_de.md) | [Français](ReleaseNote_fr.md) | [Русский](ReleaseNote_ru.md) | [Español](ReleaseNote_es.md)

# ATBClone 更新日誌 (Release Notes)

本檔案記錄了 **ATBClone** 的所有重要更新、新功能、效能最佳化及問題修復。

---

## [v0.9.6] - 2026-08-24

### 🖱️ 原生 Cocoa 表格標頭點擊排序
- **清單標頭互動式升降序排序**：
  - 針對分身清單 (`CloneListView`) 與規則清單 (`RecipeListView`) 實作原生 Cocoa `NSTableViewHeaderView` 點擊排序修補程式。
  - 支援點擊標頭欄位進行升序/降序切換，標頭即時顯示排序箭頭指示器，並與工具列排序下拉選單雙向同步。
  - 排序後自動保持目前選取的資料行，杜絕畫面跳動與焦點遺失。

### 📦 清單多選與批次管理操作
- **分身批次管理 (`CloneListView`)**：
  - 支援多行選取 (`multiple_select=True`)，工具列動作按鈕依據選取數量動態啟用或停用。
  - 支援批次更新分身與批次刪除分身（聯動資料清理確認對話方塊）。
- **規則批次刪除與情境化保護 (`RecipeListView`)**：
  - 支援多選批次刪除自訂規則。
  - 智慧情境化提示：內建唯讀規則受保護提示、混合選取（自訂+內建規則）篩選刪除確認、純自訂規則批次刪除確認。
  - 引入並行 Busy 互斥鎖，確保批次作業執行期間介面安全鎖定。

### 🛠️ Xcode 命令列工具環境診斷與健康檢查升級
- **啟動環境就緒檢查**：
  - 增強 `DoctorService` 與健康檢查頁面，新增針對 Xcode 命令列工具 (`xcode-select -p`, `codesign`, `lipo`, `otool`, `install_name_tool`) 的診斷檢查與指引。

### ℹ️ macOS 原生「關於」對話方塊中繼資料最佳化
- **標準關於對話方塊資訊修復**：
  - 規範 Cocoa `orderFrontStandardAboutPanelWithOptions:` 呼叫，準確呈現應用程式版本號、版權與技術堆疊中繼資料。

### 🧪 測試套件擴充
- **全面涵蓋**：
  - 自動化測試案例擴充至 369 項，涵蓋標頭排序、批次分身/規則作業及健康診斷。

---

## [v0.9.5] - 2026-08-23

### 📝 全新多行自動換行 `WrappingLabel` 元件與排版最佳化
- **長文字自適應自動換行**：
  - 針對 macOS Cocoa 下 Toga Label 單行計算導致長文字橫向撐大容器和視窗的缺陷，實作 `WrappingLabel` 原生多行自適應元件。
  - 基於 `NSTextField` 與 `cellSizeForBounds_` 動態依據容器寬度重新計算高度，寬度保持彈性無約束，杜絕長路徑、長參數導致的文字截斷與視窗形變。
- **探測分析報告與詳細資料頁體驗打磨**：
  - 在 `ProbeView`（應用程式探測報告、相容性評估、沙箱狀態）、`CloneDetailWindow`（執行參數、Bundle ID、資料目錄）與 `WizardWindow`（策略建議）中全面套用 `WrappingLabel`。

### 🧪 測試封閉性與狀態隔離
- **動態設定求值與測試解耦**：
  - 最佳化 `StateManager` 與 `RecipeLoader`，將預設儲存路徑從模組匯入期求值改為執行階段動態求值，徹底隔離測試案例與使用者本機狀態及自訂規則檔案。
- **測試套件擴充**：
  - 自動化測試案例擴充至 347 項，新增 `WrappingLabel` 寬度自適應與高度重新計算專項測試。

---

## [v0.9.4] - 2026-08-23

### 📁 預設根資料目錄遷移至使用者可見目錄 (`~/ATBClone`)
- **直覺便捷的資料與設定管理**：
  - 將 ATBClone 預設根目錄從隱藏的 `~/.atbclone` 遷移至使用者主目錄下的可見資料夾 `~/ATBClone`（包含 `~/ATBClone/Data/` 資料目錄、`~/ATBClone/clones.yaml` 狀態檔案與記錄檔）。
  - 使用者在 Finder 或終端機中查詢分身資料、備份與管理儲存空間更加直覺便捷。

### 🏷️ 應用程式顯示名稱精確覆蓋與多語言在地化清理
- **徹底消除系統語言預設名稱干擾**：
  - 增強 `SoftCloneEngine` 與 `HardCloneEngine`，在產生分身時自動移除 `Info.plist` 中的 `LSHasLocalizedDisplayName`，並清理資源套件中各語言的 `InfoPlist.strings`（如 `CFBundleDisplayName`、`CFBundleName`）。
  - 確保 Finder、Dock 欄、Spotlight 焦點搜尋和活動監視器中嚴格顯示使用者自訂的分身名稱，杜絕被原應用程式多語言覆蓋。

### 🔄 LaunchServices 服務自動註冊與即時重新整理
- **圖示與中繼資料即時生效**：
  - 在分身建立與更新流程最後自動執行 `lsregister -f` 強制註冊，確保 macOS 立即重新整理分身圖示與 Bundle 資訊，無需重新啟動系統或 Finder。

### 📦 文件與測試套件同步
- **全域路徑更新**：
  - 同步更新 CLI 說明資訊、GUI 設定頁面說明、README 及全套 341 項自動化測試。

---

## [v0.9.3] - 2026-08-21

### 🛡️ 應用程式檢查增強與精靈 iOS 移植應用程式友善攔截
- **精靈前置檢查與錯誤對話方塊**：
  - 增強 `AppInspector.inspect_app` 邏輯，在使用者選取或拖放應用程式時直接分析 `UIDeviceFamily` / `LSRequiresIPhoneOS` 及 `Wrapper/` 結構並標記 `is_ios_wrapper`。
  - 在 GUI 建立精靈 (`WizardWindow`) 中，一旦選入 iOS 移植應用程式，立即彈出多語言警告對話方塊並清空輸入欄位，將不相容攔截前置至第一步，提供更明確的引導。

### 🍏 macOS 結束流程最佳化與 Cocoa 記憶體解綁
- **修復結束時偶發崩潰 (Crash on Exit)**：
  - 最佳化 `TrayService.disable()` 與 `ATBCloneApp.exit_app()`，在結束前安全解綁並重設 Cocoa 狀態列選單與圖示 target/action，消除野指標與懸掛選取器。
  - 採用標準的 Cocoa 事件迴圈終止流程 (`NSApp.terminate_` / `os._exit(0)`)，徹底解決透過系統匣「結束」或 `Cmd+Q` 結束程式時偶發的崩潰問題。

### 📦 測試套件擴充
- **自動化測試增強**：
  - 自動化測試案例擴充至 341 項，全面涵蓋 iOS 移植應用程式精靈對話方塊攔截與安全結束流程。

---

## [v0.9.2] - 2026-08-21

### 🍏 macOS Dock 欄圖示動態隱藏與系統匣體驗增強
- **Dock 欄圖示動態顯示/隱藏**：
  - 基於 Cocoa AppKit 執行原則 (`NSApplicationActivationPolicy`) 實現 Dock 欄圖示動態顯隱控制。
  - 開啟「最小化至系統匣」後，當視窗最小化或關閉至系統匣時，自動將 App 切換為背景配件模式 (`NSApplicationActivationPolicyAccessory`)，完全隱藏 Dock 欄圖示。
  - 從頂部選單列系統匣還原視窗時，自動無縫恢復為標準模式 (`NSApplicationActivationPolicyRegular`)，重新顯示 Dock 圖示並置頂焦點。
- **Dock 點擊還原視窗回應 (Reopen Handler)**：
  - 注入原生 `AppDelegate` 的 `applicationShouldHandleReopen:hasVisibleWindows:` 方法，支援在 Dock 欄點擊應用程式圖示時平滑喚起並啟動主視窗。

### 📦 資源體積最佳化與測試擴充
- **圖示資源瘦身**：
  - 對應用程式圖示資源 (`logo.icns`, `logo.png`) 進行無損壓縮與最佳化，顯著降低打包體積與記憶體佔用。
- **測試套件擴充**：
  - 自動化測試案例擴充至 338 項，全面涵蓋 Dock 欄原則切換與生命週期還原。

---

## [v0.9.1] - 2026-08-21

### 🛡️ iOS-on-Mac (Designed for iPad/iPhone) 相容應用程式偵測與攔截
- **優雅識別與安全攔截**：
  - 增強 `AppProber` 探測引擎及分身引擎 (`SoftCloneEngine` / `HardCloneEngine`)，精準識別基於 Apple Silicon 執行的 iOS/iPadOS 移植封裝應用程式（如包含 `Wrapper/` 目錄或 `UIDeviceFamily` / `LSRequiresIPhoneOS=True` 的應用程式）。
  - 在 CLI 命令列 (`atbclone clone`, `atbclone wizard`) 及 GUI 互動精靈中友善攔截並提示不支援複製此類 iOS 移植應用程式 (`error_ios_wrapper_unsupported`)，避免產生損壞的分身及啟動崩潰。

### 🎨 打包指令碼自動化圖示資源產生
- **動態 `.icns` 圖示編譯**：
  - 最佳化 `scripts/build_gui.sh`，在產生 macOS DMG 安裝套件時自動呼叫 `sips` 與 `iconutil` 將 PNG 圖示動態編譯為多解析度 `.icns` 資源。
  - 增強 CLI 與 GUI 建置指令碼中的資源打包與完整性驗證。

### 🌐 多語言在地化完善
- **新增錯誤提示多語言支援**：
  - 9 種語言全面補齊針對 iOS 移植應用程式的攔截提示文案。
- **測試套件擴充**：
  - 自動化測試案例擴充至 336 項，全面涵蓋 iOS 移植應用程式探測與攔截邏輯。

---

## [v0.9.0] - 2026-08-21

### 🌐 分身獨立語言與地區 (Locale) 隔離支援
- **分身專屬執行語言設定 (`--language` / `--locale`)**：
  - 支援為每個分身單獨指定介面顯示語言與地區設定，完全獨立於 macOS 系統語言及原應用程式的語言偏好。
  - `atbclone clone` 與 `atbclone wizard` 命令列新增 `--language` / `--locale` 參數，GUI 建立精靈與編輯對話方塊同步提供視覺化語言選擇下拉選單。
  - 自動向軟分身啟動指令碼及硬分身二進位注入 `AppleLanguages` 與 `AppleLocale` 系統偏好與環境變數。
  - 引入 `atbclone.core.locale` 模組，全面支援 BCP-47 語言代碼與地區標籤解析。

### 🆔 多分身 Bundle ID 自動遞增與衝突消除
- **確定性唯一識別碼解析**：
  - 引入 `AppInspector.find_next_bundle_id` 演算法，動態掃描狀態記錄與檔案系統，確保連續建立同一應用程式分身時產生嚴格唯一且無衝突的 Bundle ID (`com.vendor.app.atb1`, `atb2`, `atb3` 等)。

### 🍏 系統選單列系統匣喚醒與視窗生命週期最佳化
- **無縫系統匣視窗還原與啟動**：
  - 徹底修復從系統選單列圖示 (`TrayService`) 還原主視窗時的 Cocoa 啟動、取消最小化及置頂焦點邏輯。
  - 支援在開啟「最小化至系統匣」時攔截視窗關閉事件（`Cmd+W` 或紅綠燈關閉按鈕），平滑隱藏至選單列而不結束程式。
  - 完善系統匣圖示的左鍵、右鍵及 Ctrl+點擊回應。

### ⚡ 分身更新並行競爭修復與目標路徑清理
- **不可部分完成更新流程**：
  - 修復 `clone update` 時的並行競爭問題，在重新產生分身前強制對目標路徑進行徹底清理，確保資料和程式碼更新的不可部分完成性與穩定性。
  - 最佳化 GUI 中分身卡片與清單的即時重新整理同步。

### 🎨 GUI 排版字型大小最佳化與文件完善
- **視覺體驗打磨**：
  - 調整 Cocoa 原生表格行高至 34px，最佳化下拉選單文字字型大小，杜絕文字截斷與溢出。
  - README 新增桌面端安裝指引、GUI 操作圖文教學及高解析度螢幕截圖。
- **測試套件擴充**：
  - 自動化測試案例擴充至 329 項，全面涵蓋語言隔離、Bundle ID 遞增與系統匣生命週期。

---

## [v0.8.0] - 2026-08-20

### 🎨 深度適配蘋果 macOS HIG 原生視覺與互動規範
- **原生設計語言與無障礙體驗升級**：
  - 全面重構 GUI 視覺設計，嚴格遵循 Apple Human Interface Guidelines (HIG)：統一步調色彩體系、系統字型階梯（11pt–22pt）與呼吸感間距。
  - 透過執行階段注入 (`patch_cocoa`) 最佳化 Cocoa 原生表格呈現：行高擴增至 40px，重構表頭樣式並放大儲存格字型，大幅提升大螢幕閱讀體驗。
  - 全面放大精靈視窗、全域設定與編輯對話方塊中的輸入框、下拉選單、開關、按鈕及標籤控制項尺寸。
  - 表格底部操作列最佳化為精緻優雅的 macOS 原生工具列風格。
  - 全面預設啟用 **清單檢視 (List View)**，提供更清晰、高效的分身與配方瀏覽體驗。

### 💾 儲存設定整合與子目錄動態連動
- **儲存管理體驗最佳化**：
  - 重組全域設定 (`SettingsView`)，將根儲存目錄整合進儲存管理專區。修改根目錄時，自動動態連動更新所有衍生子路徑 (`clones.yaml`、`Data/`、`logs/`、`recipes/`)。
  - 提供即時的路徑有效性與目錄狀態提示。

### 🌐 全面支援 HTTPS 代理協定
- **代理支援拓展**：
  - Recipe 模型、CLI (`atbclone clone`, `atbclone wizard`) 與 GUI 網路設定全面支援 `https://` 代理協定（支援包含使用者名稱與密碼認證）。

### 📦 打包體系最佳化與測試擴充
- **模組執行入口與 DMG 打包增強**：
  - 新增 `src/atbclone/__main__.py` 入口，支援透過 `python -m atbclone` 直接執行。
  - 增強 `scripts/build_gui.sh` 打包指令碼，加入嚴格的 Bundle 完整性驗證、圖示資源檢查與簽署驗證。
- **測試套件擴充**：
  - 自動化測試案例擴充至 304 項，全面涵蓋 GUI 修補、視覺元件與代理模型。

---

## [v0.7.0] - 2026-08-20

### 🖥️ 原生 BeeWare Toga 圖形桌面客戶端
- **全新冰藍 (Ice-Blue) 現代桌面介面**：
  - 正式發布基於 BeeWare Toga 構建的 macOS 原生桌面客戶端 (`atbclone-gui`)。
  - 採用流體側邊欄導覽與卡片網格佈局，內建分身管理 (`ClonesView`)、應用深度探測 (`ProbeView`)、配方管理 (`RecipesView`)、即時記錄 (`LogsView`) 與全域設定 (`SettingsView`)。
  - 支援拖放 `.app` 的圖形化分身建立精靈，提供即時建立狀態與動畫反饋。

### 🍏 原生 macOS 狀態列系統匣與最小化支援
- **選單列系統匣服務 (TrayService)**：
  - 深度整合原生 `NSStatusBar` 與 `NSStatusItem` 狀態列圖示，提供快捷選單（開啟主視窗、建立分身、快速啟動、偏好設定、結束）。
  - 支援「最小化至系統匣」偏好設定，透過 Cocoa Selector 與 `NSWindowDelegate` 實現平滑的視窗隱藏與系統匣恢復。

### 📖 GUI 專屬多語言更新日誌檢視器
- **內建 Release Notes 視窗**：
  - 全域設定介面新增「檢視更新日誌」按鈕，可獨立開啟 `ReleaseNotesWindow`。
  - 內建 9 種語言動態切換下拉選單，即時轉譯多語言 Markdown 更新日誌。

### 📝 統一操作日誌系統 (Unified Logger)
- **檔案保存與即時廣播流**：
  - 引入 `atbclone.core.logger`，統一 CLI 與 GUI 日志輸出，支援檔案儲存 (`~/.atbclone/logs/atbclone.log`) 與記憶體廣播流 (`LogBroadcastHandler`)。
  - GUI 記錄檢視支援即時串流更新、等級篩選、關鍵字搜尋、日誌匯出與磁碟清理。

### 📦 配方庫擴充與測試套件升級
- **新增主流應用配方**：新增 **Claude Desktop** (`com.anthropic.claudefordesktop`)、修正 **Telegram** (`ru.keepcoder.Telegram`)、**Cursor** 等熱門工具配方。
- **自動化測試擴充**：測試套件案例大幅擴展至 299 項，全面涵蓋 GUI 視圖、系統匣服務與核心邏輯。

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
  - 將 **Google Chrome**、**Microsoft Edge**、**Arc Browser** 預設規則升級為 `hard_clone` 策略，實現完整的 App Bundle 獨立複製與 Dock/Finder 專屬識別。
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
  - 為未預設規則的應用程式動態推薦最佳分身策略（`hard_clone` / `soft_clone`）並產生標準 Recipe YAML。
  - `atbclone clone` 支援自動觸發探測引擎，無須手動指定分身規則即可一鍵分身未知應用程式。
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
- **18+ 款主流應用程式預設分身規則**：
  - 即時通訊：微信 (WeChat)、QQ、Telegram、LINE、Slack、Discord、Skype。
  - AI 客戶端：ChatGPT (Codex)、Gemini、Antigravity、Antigravity IDE。
  - 瀏覽器與開發工具：Google Chrome、Microsoft Edge、Firefox、Arc、Cursor、VS Code、Zed。
- **完整 CLI 指令集**：
  - `clone`：建立應用程式分身，支援自訂名稱、輸出目錄及網路代理。
  - `list`：Rich 表格檢視已建立分身、策略類型、建立時間及代理狀態。
  - `update`：主應用程式升級後一鍵同步分身，保留全部聊天記錄與設定資料。
  - `remove`：安全移除分身，支援可選清理資料目錄。
  - `recipe`：檢視內建規則列表及本機自訂規則覆寫。
  - `doctor`：自動化環境自我檢查（檢查 `codesign`、`xcode-select`、`PlistBuddy` 等工具鏈）。
