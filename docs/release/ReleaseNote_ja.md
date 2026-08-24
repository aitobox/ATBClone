[English](ReleaseNote.md) | [简体中文](ReleaseNote_zh.md) | [繁體中文](ReleaseNote_zh_TW.md) | [日本語](ReleaseNote_ja.md) | [한국어](ReleaseNote_ko.md) | [Deutsch](ReleaseNote_de.md) | [Français](ReleaseNote_fr.md) | [Русский](ReleaseNote_ru.md) | [Español](ReleaseNote_es.md)

# ATBClone リリースノート (Release Notes)

このドキュメントには、**ATBClone** のすべての重要な更新、新機能、パフォーマンスの改善、およびバグ修正が記録されています。

---

## [v0.9.9] - 2026-08-24

### 📋 クローン詳細画面のテキスト選択と「全情報のコピー」機能
- **テキスト選択と一括コピーの対応**:
  - `CloneDetailWindow` 内のすべてのラベルで Cocoa ネイティブの選択可能モード（`setSelectable_`）を有効化し、パスや Bundle ID を直接ハイライトコピー可能に。
  - フッターに「すべての情報をコピー」ボタンを追加し、クローンの完全な診断サマリーをクリップボードに Markdown 形式で出力。

### 🎨 macOS ネイティブ UI デザインとスペーシングの最適化
- **テーマカラーとカードスタイルの調整**:
  - `Theme` におけるライト・ダークモードのカラートークン（`BG_APP`、`BG_CARD`、`BG_HOVER`、`BORDER`、`TEXT_PRIMARY`、`TEXT_MUTED`、`ACCENT`）を洗練。
  - カードコンテナの角丸、パディング、コンポーネント間隔を最適化し、各画面のネイティブ感を向上。

### 📖 包括的な多言語ユーザーマニュアルの公開 (`docs/guide/`)
- **詳細な公式ドキュメント**:
  - 英語（`docs/guide/en/`）および中国語（`docs/guide/zh-cn/`）の包括的ユーザーマニュアルを公開。
  - 第1章（基本操作とライフサイクル）、第2章（高度なカスタムレシピ）、第3章（内部アーキテクチャ）、第4章（FAQ・診断・トラブルシューティング）を網羅。

### 🧪 テストスイート拡充
- **品質検証**:
  - 自動テストスイートを 431 件に拡大。

---

## [v0.9.8] - 2026-08-24

### 🔒 サンドボックス Entitlements の正確な継承とハードクローンの安定化
- **元アプリの署名権限（Entitlements）保持**:
  - `HardCloneEngine` を強化し、`codesign -d --entitlements :-` を通じて元の Mach-O バイナリからネイティブ権限を正確に抽出・継承。
  - 再署名時の空または不正な Entitlements の生成を防止する安全ガードを追加。
- **組み込みレシピにおけるサンドボックスコンテナの完全分離**:
  - WeChat、QQ、WeWork、WPS Office、LINE、Skype、CapCut を含むハードクローンレシピで `strip_sandbox: false` を徹底。
  - 各クローンが独立したコンテナ（`~/Library/Containers/<new_bundle_id>`）で隔離実行され、セッションやデータの競合を防止。

### 📚 ドキュメントとスキーマ仕様の同期
- **多言語ドキュメントの改訂**:
  - 英語（`README.md`）および中国語（`README_zh.md`）ドキュメントを最新の `app_type`、`strip_sandbox`、CLI/GUI ガイドに合わせて更新。

### 🧪 品質検証
- **テストスイートの全件パス**:
  - 全 428 件の自動テスト（ユニット、クローンエンジン、GUI 統合）が 100% 成功。

---

## [v0.9.7] - 2026-08-24

### 🔍 アプリケーションアーキテクチャの自動認識と適応型言語注入
- **フレームワーク種別の認識 (`app_type`)**:
  - Recipe モデルに `app_type` フィールド（`electron`、`chromium`、`qt`、`flutter`、`native_cocoa`、`java`、`unknown`）を追加。
  - `AppProber.detect_app_type` により、Frameworks や dylib、JVM 構成を解析してアプリのランタイムを自動判定。
  - 全 34 種類の組み込みレシピで `app_type` および `strip_sandbox` を標準化。
- **アーキテクチャ適応型言語パラメータ注入**:
  - フレームワークに応じて最適な言語引数を動的適用（Chromium/Electron では `--lang=`、Native Cocoa では `-AppleLanguages`、Java では `-user.language`）。

### 🧬 Mach-O バイナリ引数の自動診断と検証
- **未知アプリのデータディレクトリ引数自動検出**:
  - `BinaryArgumentProber` を実装し、Mach-O バイナリの文字列テーブルをスキャンしてサポートされている引数（`--user-data-dir`、`--profile-directory`、`--datadir` など）を自動検出。
- **起動引数の検証とサニタイズ**:
  - `LaunchArgumentValidator` により、非対応または競合する起動引数を自動除外して安定動作を保証。

### 📋 クローン注入パラメータの詳細表示とコピー機能
- **注入パラメータ解析 (`CloneInspector`)**:
  - `CloneInspector` により、クローン内の環境変数、プロキシ設定、言語オーバーライド、起動引数を抽出。
  - `CloneDetailWindow` に「注入パラメータ」カードを追加し、ワンクリックでクリップボードにコピー可能に。

### ⚙️ レシピ編集ウィンドウの高度な設定機能
- **GUI レシピ編集の強化 (`RecipeEditWindow`)**:
  - アプリタイプ選択、起動引数編集、プロキシ設定、環境変数、シンボリックリンクのホワイトリスト設定に対応。

### 🧪 テストスイート拡充
- **網羅的な品質検証**:
  - 自動テストスイートを 428 件に拡大。

---

## [v0.9.6] - 2026-08-24

### 🖱️ ネイティブ Cocoa テーブルヘッダーのクリックソート
- **インタラクティブなカラムソート**:
  - `CloneListView` および `RecipeListView` に Cocoa `NSTableViewHeaderView` クリックソートパッチを適用。
  - カラムヘッダークリックによる昇順・降順の切り替え、ソート矢印インジケーターの表示、ツールバーとの双方向同期に対応。
  - ソート後も選択状態を自動的に保持。

### 📦 複数選択と一括操作機能
- **クローンの一括管理 (`CloneListView`)**:
  - 複数行選択（`multiple_select=True`）とツールバーボタンの動的状態連動をサポート。
  - 複数クローンの一括更新および一括削除（データ完全削除確認付き）に対応。
- **レシピの一括削除と保護機能 (`RecipeListView`)**:
  - カスタムレシピの一括選択削除。
  - シチュエーション別の確認ダイアログ（組み込み読み取り専用レシピの保護、混在選択時のフィルタリング削除、カスタムレシピの一括削除）。
  - 一括処理中のビジーロック機構を搭載。

### 🛠️ Xcode Command Line Tools の診断とヘルスチェック強化
- **起動時ツールチェーン診断**:
  - `DoctorService` において、Xcode Command Line Tools（`xcode-select -p`, `codesign`, `lipo`, `otool`, `install_name_tool`）のインストール状態を自動診断し、ガイダンスを表示。

### ℹ️ macOS ネイティブ「このアプリについて」のメタデータ表示
- **Cocoa About ダイアログの修正**:
  - `orderFrontStandardAboutPanelWithOptions:` を適切に構成し、バージョン番号や著作権情報を正確に表示。

### 🧪 テストスイート拡充
- **網羅的な検証**:
  - 自動テストスイートを 369 件に拡大。

---

## [v0.9.5] - 2026-08-23

### 📝 自動折り返し `WrappingLabel` コンポーネントの実装とレイアウト最適化
- **複数行テキストの自動折り返し対応**:
  - macOS Cocoa の Toga Label が単行計算によりウィンドウを横に拡大してしまう問題を解決する `WrappingLabel` を新規実装。
  - `NSTextField` と `cellSizeForBounds_` を活用し、コンテナ幅に応じて高さを動的に再計算し、長大なパスや引数による文字欠けやウィンドウ肥大化を防止。
- **診断レポートおよび詳細画面の表示改善**:
  - `ProbeView`（アプリ診断レポート、互換性評価、サンドボックス状況）、`CloneDetailWindow`（起動引数、Bundle ID、データパス）、`WizardWindow` に `WrappingLabel` を適用。

### 🧪 テストの完全な独立性と状態分離
- **動的パス解決とテスト環境の隔離**:
  - `StateManager` および `RecipeLoader` を見直し、設定パスを実行時に動的取得するよう改善。テスト実行とローカルユーザー状態・カスタム設定ファイルの完全な分離を実現。
- **テストの網羅性**:
  - 自動テストスイートを 347 件に拡大。

---

## [v0.9.4] - 2026-08-23

### 📁 デフォルトデータディレクトリの可視化移行 (`~/ATBClone`)
- **データ管理の直感性向上**:
  - ATBClone のデフォルトルートディレクトリを隠しフォルダ `~/.atbclone` からユーザーディレクトリ直下の `~/ATBClone`（データディレクトリ `~/ATBClone/Data/`、状態管理 `~/ATBClone/clones.yaml`）に移行。
  - Finder やターミナルからのデータバックアップやストレージ確認が容易に。

### 🏷️ クローンアプリ表示名の確実な適用とローカライズ文字列のクリーンアップ
- **表示名の上書き徹底**:
  - `SoftCloneEngine` および `HardCloneEngine` を強化し、`LSHasLocalizedDisplayName` を削除するとともに各言語リソース内の `InfoPlist.strings` を自動クリーンアップ。
  - Finder、Dock、Spotlight、アクティビティモニタで常にユーザー指定のクローン名が表示されるよう改善。

### 🔄 LaunchServices 自動登録による即時反映
- **メタデータキャッシュの即時更新**:
  - クローン作成・更新時に `lsregister -f` を自動実行し、macOS 側のアイコンやメタデータを即座に反映。

### 📦 ドキュメントとテストの更新
- **全般的な同期**:
  - CLI ヘルプ、GUI 設定画面、README、および 341 件の全自動テストを新パスに対応。

---

## [v0.9.3] - 2026-08-21

### 🛡️ アプリ検査の強化とウィザードでの iOS ラッパーアプリ即時ブロック
- **ウィザード事前検証と警告ダイアログ**:
  - `AppInspector.inspect_app` を強化し、ドラッグ＆ドロップ時に `UIDeviceFamily` / `LSRequiresIPhoneOS` を即座に検査して `is_ios_wrapper` を判定。
  - GUI ウィザード（`WizardWindow`）において、iOS ラッパーアプリが選択された場合に即座に多言語警告ダイアログを表示して入力をリセットし、分かりやすい事前案内を実現。

### 🍏 macOS 終了処理の最適化と Cocoa リソース解放
- **終了時クラッシュ (Crash on Exit) の完全防止**:
  - `TrayService.disable()` および `ATBCloneApp.exit_app()` を見直し、終了時に Cocoa メニューおよびステータスアイテムの target/action を安全に解除。
  - 標準的な Cocoa イベントループ終了処理（`NSApp.terminate_` / `os._exit(0)`）を適用し、トレイメニューの「終了」や `Cmd+Q` での終了時クラッシュを解消。

### 📦 テストスイート拡充
- **テストの網羅性**:
  - 自動テストスイートを 341 件に拡大。

---

## [v0.9.2] - 2026-08-21

### 🍏 macOS Dock アイコンの動的非表示およびトレイ連携の強化
- **Dock アイコンの自動表示・非表示切り替え**:
  - Cocoa AppKit のアクティベーションポリシー（`NSApplicationActivationPolicy`）を利用した動的な Dock アイコン管理を実装。
  - 「トレイに最小化」有効時、ウィンドウを閉じたりトレイに格納すると、Dock アイコンが完全に非表示化（`NSApplicationActivationPolicyAccessory`）。
  - メニューバートレイから復元すると、即座に標準モード（`NSApplicationActivationPolicyRegular`）に戻り、Dock アイコンが再表示されてウィンドウが最前面化。
- **Dock クリック時のウィンドウ復元 (Reopen Handler)**:
  - `AppDelegate` に `applicationShouldHandleReopen:hasVisibleWindows:` を実装し、Dock クリック時にスムーズにメイン画面を復元。

### 📦 リソースサイズ最適化とテスト拡充
- **アプリアイコンの軽量化**:
  - `logo.icns` および `logo.png` を最適化・圧縮し、アプリサイズとメモリ使用量を削減。
- **テストの網羅性**:
  - 自動テストスイートを 338 件に拡大。

---

## [v0.9.1] - 2026-08-21

### 🛡️ iOS-on-Mac（Designed for iPad/iPhone）アプリの検出と安全な拒否
- **未対応アーキテクチャの安全なハンドリング**:
  - `AppProber` および各クローンエンジン（`SoftCloneEngine` / `HardCloneEngine`）を強化し、Apple Silicon 向け iOS/iPadOS ラッパーアプリ（`Wrapper/` ディレクトリまたは `UIDeviceFamily` / `LSRequiresIPhoneOS=True` を含むアプリ）を正確に検出。
  - CLI（`atbclone clone`, `atbclone wizard`）および GUI ウィザードにおいて、iOS ラッパーアプリのクローン作成を適切にブロックし、多言語エラーメッセージ（`error_ios_wrapper_unsupported`）を表示して破損や起動失敗を防止。

### 🎨 ビルドスクリプトによるアプリアイコン自動生成
- **動的な `.icns` 変換**:
  - `scripts/build_gui.sh` において、DMG 作成時に `sips` および `iconutil` を使用して PNG から高解像度 `.icns` アイコンを自動生成する処理を追加。
  - パッケージング工程におけるリソース同梱および検証を強化。

### 🌐 多言語ローカライズの拡充
- **エラーメッセージの翻訳**:
  - iOS ラッパーアプリ非対応の警告メッセージを 9 言語すべてに追加。
- **テストの拡充**:
  - 自動テストスイートを 336 件に拡大。

---

## [v0.9.0] - 2026-08-21

### 🌐 クローンごとの独立言語およびロケール (Locale) 分離サポート
- **クローン専用の言語設定 (`--language` / `--locale`)**:
  - 各クローンアプリに対して、macOS システム設定や元アプリの言語と異なる専用の表示言語・ロケールを指定可能に。
  - CLI（`atbclone clone`, `atbclone wizard`）に `--language` / `--locale` オプションを追加し、GUI ウィザードおよび編集画面に言語選択ドロップダウンを統合。
  - ソフトクローンのラッパースクリプトおよびハードクローンのバイナリに `AppleLanguages` と `AppleLocale` のシステム環境設定を自動注入。
  - BCP-47 言語タグに対応した `atbclone.core.locale` モジュールを新規実装。

### 🆔 複数クローン作成時の Bundle ID 自動採番と衝突回避
- **一意な Bundle ID の自動決定**:
  - `AppInspector.find_next_bundle_id` を導入し、登録済みクローンとファイルシステムを走査して重複のない連番 Bundle ID（`com.vendor.app.atb1`, `atb2` 等）を自動生成。

### 🍏 メニューバートレイからのウィンドウ復元およびライフサイクルの改善
- **確実なアクティベーションと復元**:
  - システムトレイ（`TrayService`）からメイン画面を表示する際の Cocoa 最前面化・最小化解除・アクティブ化処理を強化。
  - 「トレイに最小化」有効時、ウィンドウを閉じる操作（`Cmd+W` または赤ボタン）をフックしてトレイに常駐する挙動を修正。
  - トレイアイコンの左クリック、右クリック、Control+クリックの動作を安定化。

### ⚡ クローン更新時の競合解消とクリーンな再生成
- **アトミックな更新処理**:
  - `clone update` 実行時にターゲット先を確実に事前クリーンアップし、競合状態を防止。
  - GUI 側のクローンカードおよび一覧の更新同期を改善。

### 🎨 UI タイポグラフィ調整とドキュメント拡充
- **表示品質の向上**:
  - Cocoa テーブルの行の高さを 34px に最適化し、ドロップダウン内の文字欠けを解消。
  - README に GUI 操作ガイド、ダウンロード手順、高解像度スクリーンショットを追加。
- **テストの拡充**:
  - 自動テストスイートを 329 件に拡大。

---

## [v0.8.0] - 2026-08-20

### 🎨 macOS HIG ネイティブデザインおよびアクセシビリティの全面刷新
- **Apple デザインガイドラインの完全準拠**:
  - Apple Human Interface Guidelines (HIG) に厳格に準拠するよう GUI デザインを刷新。ネイティブカラーパレット、標準フォント階層（11pt〜22pt）、快適な余白設計を統一。
  - Cocoa テーブルの動的パッチ（`patch_cocoa`）を導入：行の高さを 40px に拡張し、ヘッダーおよびセルフォントを拡大して視認性を大幅向上。
  - ウィザード、設定、編集ウィンドウにおける入力欄、ドロップダウン、スイッチ、ボタン、ラベルのサイズを最適化。
  - テーブル下部のアクションフッターを洗練された macOS ネイティブツールバー形式に改修。
  - 各管理画面の初期表示モードを **リスト表示 (List View)** に統一。

### 💾 ストレージ設定の統合とサブディレクトリ自動同期
- **ストレージ管理の最適化**:
  - 設定画面（`SettingsView`）を整理し、ルートストレージディレクトリと各サブパス（`clones.yaml`, `Data/`, `logs/`, `recipes/`）を動的に自動連動・同期。
  - パスの有効性および存在ステータスをリアルタイム表示。

### 🌐 HTTPS プロキシプロトコルのサポート
- **プロキシ機能の拡張**:
  - Recipe モデル、CLI（`atbclone clone`, `atbclone wizard`）、および GUI ネットワーク設定において `https://` プロキシスキームを完全サポート。

### 📦 アプリケーションパッケージングの強化とテスト拡充
- **モジュール実行エントリポイントと DMG ビルド改善**:
  - `src/atbclone/__main__.py` を追加し、`python -m atbclone` での直接起動に対応。
  - `scripts/build_gui.sh` に詳細な Bundle 整合性検証、アイコン検証、コード署名確認ステップを追加。
- **テストの網羅性**:
  - 自動テストスイートを 304 件に拡大し、UI パッチおよびプロキシ動作の検証を強化。

---

## [v0.7.0] - 2026-08-20

### 🖥️ ネイティブ BeeWare Toga デスクトップ GUI アプリケーション
- **洗練された Ice-Blue デスクトップインターフェース**:
  - BeeWare Toga をベースにした macOS ネイティブデスクトップアプリ（`atbclone-gui`）を新規リリース。
  - 流暢なサイドバーナビゲーションとカードグリッドレイアウトを採用し、クローン管理（`ClonesView`）、アプリ詳細分析（`ProbeView`）、レシピ管理（`RecipesView`）、ログビューア（`LogsView`）、全体設定（`SettingsView`）を統合。
  - `.app` のドラッグ＆ドロップに対応した直感的なクローン作成ウィザードを搭載。

### 🍏 ネイティブ macOS メニューバートレイおよび最小化機能
- **メニューバートレイサービス (TrayService)**:
  - `NSStatusBar` および `NSStatusItem` を使用したネイティブメニューバーアイコンを統合。クイックメニュー（メイン画面表示、クローン作成、クイック起動、設定、終了）を提供。
  - 「トレイに最小化」設定を追加し、Cocoa Selector および `NSWindowDelegate` によるスムーズなトレイ収納・復帰を実現。

### 📖 GUI リリースノート閲覧ウィンドウ
- **内蔵 Release Notes ビューア**:
  - 設定画面からワンクリックで開ける `ReleaseNotesWindow` を実装。
  - 9 言語の動的切り替えドロップダウンを備え、ローカライズされた Markdown ログをリアルタイム表示。

### 📝 統合操作ログシステム (Unified Logger)
- **ファイル永続化とリアルタイムストリーミング**:
  - CLI と GUI で共有可能な `atbclone.core.logger` を導入。ファイル保存（`~/.atbclone/logs/atbclone.log`）とブロードキャスト（`LogBroadcastHandler`）を両立。
  - GUI ログ画面でリアルタイム更新、ログレベル絞り込み、検索、エクスポート、ログ消去をサポート。

### 📦 レシピの拡充とテストスイート
- **公式レシピの追加**: **Claude Desktop** (`com.anthropic.claudefordesktop`)、**Telegram** (`ru.keepcoder.Telegram`)、**Cursor** などの人気ツールに対応。
- **テストの拡充**: 自動テストスイートを 299 件に拡大し、GUI 画面およびトレイ動作を網羅。

---

## [v0.6.0] - 2026-08-19

### 📂 カスタムデータディレクトリのサポート
- **クローンデータ保存先の自由な指定 (`--data-dir`)**:
  - `atbclone clone` コマンドに `--data-dir` オプションを追加し、外付け SSD や任意の作業ディレクトリへのデータ保存に対応。
  - 対話型ウィザード（`atbclone wizard`）において、カスタムデータディレクトリの設定ステップを統合。
  - Recipe モデルおよび各クローンエンジンにおいて、動的データディレクトリ変数の解決を完全サポート。

### 🗑️ クローン削除およびデータクリーンアップの強化 (`atbclone remove`)
- **安全なデータ削除制御オプション**:
  - `atbclone remove` に `--purge-data` オプションを追加し、アプリ本体と関連ユーザーデータを一括で完全削除可能に。
  - `--keep-data` オプションにより、アプリ本体のみをアンインストールして設定データを保持する動作をサポート。
  - 対話型削除プロンプトにおいて、データ保持か完全削除かを明確に選択できる確認ダイアログを実装。
  - 残留データディレクトリおよび権限エラーに対する診断・エラーハンドリングを強化。

### 🆔 Bundle ID 生成の標準化と多言語対応
- **Bundle ID 生成の統一**:
  - `AppInspector.generate_bundle_id` を導入し、`clone`、`wizard`、`update` 間での Bundle ID 命名規則を標準化。
- **多言語ローカライズの拡充**:
  - データディレクトリ入力、削除確認、パージ結果のログメッセージを 9 言語すべてに適用。
- **テストスイートの拡充**:
  - 自動テストを 213 件に拡大し、カスタムパスおよび削除処理の網羅的検証を達成。

---

## [v0.5.0] - 2026-08-19

### 🔐 Apple コード署名および公証（Notarization）パイプライン
- **Hardened Runtime と公式署名の統合**:
  - Apple Developer ID Application 証明書によるコード署名、`--options runtime`（Hardened Runtime）、タイムスタンプ、および専用 JIT / 実行権限設定（`scripts/entitlements.plist`）を完全統合。
  - Keychain 資格情報（`--keychain-profile`）を使用して `xcrun notarytool` 経由で Apple 公証を一括実行する `scripts/notarize.sh` を追加。
  - `scripts/build_cli.sh` および `scripts/release.sh` において `--sign-identity`、`--skip-sign`、`--notarize` オプションをサポートし、証明書未設定時は自動的に ad-hoc 署名へフォールバック。

### 🚀 Chromium ブラウザのハードクローン対応および起動引数注入
- **`HardCloneEngine` による起動引数の注入**:
  - 環境変数分離に加え、バイナリラッパーへ `--user-data-dir={{ATB_DATA_DIR}}` などの起動引数を動的に注入できるよう `HardCloneEngine` を強化。
  - **Google Chrome**、**Microsoft Edge**、**Arc Browser** の組み込みレシピを `hard_clone` にアップグレードし、App Bundle の完全複製と独立した Dock/Finder アイデンティティを実現。
- **CLI 戦略上書きオプション**:
  - `atbclone clone` コマンドに `--strategy`（`hard_clone` または `soft_clone`）オプションを追加し、レシピ設定の手動変更に対応。

### ⚡ プロセス管理およびテストスイート拡充
- **プロセス制御の改善**: `SoftCloneEngine` のラッパースクリプトを標準の `exec "$@"` による引数転送に最適化。
- **テストの網羅性向上**: 自動テストスイートを 199 件に拡大し、署名・公証スクリプトおよびクローン戦略の検証を強化。

---

## [v0.4.0] - 2026-08-19

### 🌐 9 言語対応の包括的 CLI およびドキュメント体系
- **CLI コマンド全体の 9 言語ローカライズ**:
  - `atbclone.core.i18n` 多言語エンジンを拡張し、英語、簡体字中国語、繁体字中国語、日本語、韓国語、ドイツ語、フランス語、ロシア語、スペイン語の計 9 言語に完全対応。
  - すべての CLI コマンド（`wizard`、`clone`、`probe`、`list`、`recipe`、`doctor`、`update`、`remove`、`version`）において、案内、テーブル表示、エラーログの多言語化を実現。
- **多言語リリースノートの標準化**:
  - `docs/release/` 配下に 9 言語のリリースノートを整備し、言語切り替えナビゲーションを統一。

### 🔄 リリース自動化とバージョン同期パイプライン
- **9 言語リリースノートの自動検証**:
  - `scripts/manage_version.py` および `scripts/release.sh` を強化し、タグ作成前に `docs/release/` 内の全 9 ファイルのバージョン記載を自動検証。
  - ドキュメント記載漏れを防ぐ `--check-notes` 検証オプションを追加。
- **テストスイートの拡充**:
  - 自動テストを 191 件に拡充し、多言語描画とリリースワークフローの網羅的検証を達成。

---

## [v0.3.0] - 2026-08-19

### 🌐 国際化と多言語対応 (i18n)
- **macOS システム言語の自動検出**:
  - `AppleLanguages` および `AppleLocale` を介して macOS システムの言語設定を自動判定する `atbclone.core.i18n` エンジンを統合しました。
  - CLI の対話型ウィザード、プロンプト、テーブルヘッダー、エラーログが日本語/英語/中国語の環境に応じて自動的に最適化されます。
  - `ATBCLONE_LANG` 環境変数（例: `ATBCLONE_LANG=en` / `ATBCLONE_LANG=zh`）を使用した言語の手動上書き指定をサポート。
- **多言語ドキュメント体制の拡充**:
  - デフォルトの `Readme.md` を英語化し、中国語ドキュメントを `Readme_zh.md` に移行。
  - 9 つの言語に対応したリリースノートを公開：英語、簡体字中国語、繁体字中国語、日本語、韓国語、ドイツ語、フランス語、ロシア語、スペイン語。

### 🛠️ CLI およびビルドパッケージの改善
- **対話型ウィザードの国際化**: `atbclone wizard` の入力案内、カスタム表示名、`.icns` アイコン選択、プロキシ設定の多言語化を完了。
- **スタンドアロンバイナリの強化**: Nuitka により `./dist/ATBCloneCli` を再ビルド。サンドボックス環境でのコンパイル互換性（`PYTHONNOUSERSITE=1`）を向上。
- **テストスイートの拡充**: `test_i18n.py` を追加し、全 186 件の自動テストが正常にパスすることを確認。

---

## [v0.2.0] - 2026-08-18

### 🚀 主な新機能
- **対話型クローンウィザード (`atbclone wizard`)**:
  - ターミナルでのドラッグ＆ドロップによる `.app` パス入力に対応。
  - クローン名の自動連番検出（例: `WeChat2`, `WeChat3`）。
  - カスタムアプリケーション表示名およびカスタム `.icns` アイコンの適用をサポート。
  - HTTP / SOCKS5 プロキシの対話型設定（認証付きプロキシにも対応）。
- **高度なアプリケーション分析プロバー (`atbclone probe`)**:
  - 任意の macOS アプリの Mach-O アーキテクチャ（arm64, x86_64, Universal）、フレームワーク（Electron, Flutter, Chromium, Qt, Cocoa）、サンドボックス権限（`com.apple.security.app-sandbox`）を自動解析。
  - レシピが未登録のアプリに対しても最適なクローン戦略（`hard_clone` / `soft_clone`）を推奨し、標準 Recipe YAML を自動生成。
  - `atbclone clone` 実行時に未知のアプリを検出した場合、プロバーエンジンが自動作動。
- **単一実行可能ファイルのビルド**:
  - Nuitka を使用して外部依存関係のないネイティブ macOS arm64 単一バイナリ（`dist/ATBCloneCli`）を生成する `scripts/build_cli.sh` を追加。

### ⚡ 改善と修正
- `/Applications` ディレクトリへの出力時における権限昇格を macOS ネイティブの `osascript` 認証ダイアログに統合し、1 回のパスワード入力でスムーズに処理。
- `shlex.quote` による厳格なパスエスケープ処理を全域に適用し、空白や特殊文字を含むパスでの安全性を向上。

---

## [v0.1.0] - 2026-08-17

### 🌟 初期リリース
- **デュアルエンジンクローン機能**:
  - **ハードクローン (Hard Clone)**: App Bundle 全体の複製、`Info.plist` の変更、独立した `HOME` / `TMPDIR` の注入、サンドボックス解除、および ad-hoc 再署名。
  - **ソフトクローン (Soft Clone)**: Chromium 系ブラウザやエディタ向けに、`--user-data-dir` とプロキシ変数を注入する軽量ラッパーを生成。
- **18 以上の主要アプリに対応する組み込みレシピ**:
  - メッセンジャー: WeChat, QQ, Telegram, LINE, Slack, Discord, Skype.
  - AI クライアント: ChatGPT (Codex), Gemini, Antigravity, Antigravity IDE.
  - ブラウザ・エディタ: Google Chrome, Microsoft Edge, Firefox, Arc, Cursor, VS Code, Zed.
- **充実した CLI コマンド群**:
  - `clone`: アプリケーションのクローンを作成。
  - `list`: クローン済みアプリの一覧、戦略、作成日時、プロキシ設定を表示。
  - `update`: メインアプリの更新後、ユーザーデータを保持したままクローンを安全に同期。
  - `remove`: クローンを安全に削除（データディレクトリの削除オプション付き）。
  - `recipe`: 組み込みレシピの確認およびローカル上書き機能。
  - `doctor`: 環境ツールチェーン（`codesign`, `xcode-select`, `PlistBuddy`）の自動診断。
