[English](ReleaseNote.md) | [简体中文](ReleaseNote_zh.md) | [繁體中文](ReleaseNote_zh_TW.md) | [日本語](ReleaseNote_ja.md) | [한국어](ReleaseNote_ko.md) | [Deutsch](ReleaseNote_de.md) | [Français](ReleaseNote_fr.md) | [Русский](ReleaseNote_ru.md) | [Español](ReleaseNote_es.md)

# ATBClone リリースノート (Release Notes)

このドキュメントには、**ATBClone** のすべての重要な更新、新機能、パフォーマンスの改善、およびバグ修正が記録されています。

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
