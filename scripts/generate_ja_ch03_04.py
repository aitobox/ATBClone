import os

JA_DIR = "docs/guide/ja"

ch03 = """# 第3章：動作原理の解説と高度な設定パラメータ

本章では、ATBClone の深層アーキテクチャ、ソフトクローンとハードクローンの低レベル実装、バイナリラッパーハイジャック技術、そして高度なカスタムレシピを作成するための全パラメータと動的マクロについて詳細に解説します。

---

## 📑 目次

- [クローン分離アーキテクチャの比較](#_1)
  - [ソフトクローン (Soft Clone) の内部構造](#soft-clone)
  - [ハードクローン (Hard Clone) の内部構造](#hard-clone)
- [ハードクローン「3つのコア技術」解説](#3)
  - [1. バンドル識別子 (Bundle ID) の改変](#1-bundle-id)
  - [2. バイナリラッパーハイジャック (Wrapper Hijack)](#2-wrapper-hijack)
  - [3. サンドボックス剥離とアドホック再署名](#3-)
- [データとロジックの完全分離設計](#_2)
- [高度なレシピパラメータ解説](#_3)
  - [1. environment_injection (環境変数注入)](#1-environment_injection)
  - [2. symlink_whitelist (シンボリックリンク白名単)](#2-symlink_whitelist)
  - [3. launch_arguments (起動引数)](#3-launch_arguments)
  - [4. plist_overrides (Info.plist 上書き)](#4-plist_overrides-infoplist-)
  - [5. 動的パス環境変数マクロ](#5)
- [高度なカスタムレシピの完全な YAML サンプル](#yaml)

---

## 🏗️ クローン分離アーキテクチャの比較

### ソフトクローン (Soft Clone) の内部構造
ソフトクローンは、Chromium や Electron、またはコマンドライン引数によるデータディレクトリ切り替えに対応したアプリケーション向けの手法です。親アプリのバイナリ（数十〜数百MB）を複製せず、軽量なランチャースクリプト（約数KB）のみを生成します。

```text
[Soft Clone ランチャー] 
       │ 起動引数を付与して呼び出し
       ▼
/Applications/Cursor.app/Contents/MacOS/Cursor --user-data-dir="~/ATBClone/Data/Cursor-Work"
```

* **メリット**：ディスク消費がほぼゼロ、作成・アップデートが一瞬で完了。
* **制限事項**：Dock でアプリアイコンが元の親アプリにグループ化される場合があり、システム TCC 権限は親アプリと共有されます。

---

### ハードクローン (Hard Clone) の内部構造
ハードクローンは、WeChat、LINE、Telegram、Discord、Slack など、独立したシステム識別と完全なデータ隔離が必要なすべてのネイティブアプリに対応します。

```mermaid
graph TD
    A[親アプリ /Applications/WeChat.app] -->|App バンドル完全複製| B[クローンアプリ ~/ATBClone/Apps/WeChat-2.app]
    B --> C[1. CFBundleIdentifier を固有値に変更]
    B --> D[2. オリジナル実行バイナリを .real にリネーム]
    B --> E[3. ラッパーシェルスクリプトをバイナリ位置に配置]
    B --> F[4. サンドボックス Entitlements 剥離 & 再署名]
    
    E -->|起動時に環境変数を差し替え| G["HOME=~/ATBClone/Data/WeChat-2"]
    G --> H[WeChat.real を起動]
```

---

## ⚡ ハードクローン「3つのコア技術」解説

### 1. バンドル識別子 (Bundle ID) の改変
`Info.plist` 内の `CFBundleIdentifier`（例：`com.tencent.xinWeChat`）を固有のクローン用識別子（例：`com.tencent.xinWeChat.atbclone.work`）に書き換えます。これにより、macOS システムはこれを完全に別のアプリとして認識し、通知設定、TCC 安全許可、ウィンドウ管理が完全に独立します。

### 2. バイナリラッパーハイジャック (Wrapper Hijack)
ハードクローンの中核技術です：
1. `Contents/MacOS/<Executable>` を `<Executable>.real` にリネームします。
2. 同名の POSIX シェルスクリプトを新規作成し、実行権限（`chmod +x`）を付与します。
3. ラッパー内で以下の環境変数をフック・再定義してから、バックグラウンドの `.real` バイナリを実行します：
   * `export HOME="<Isolated Data Dir>"`
   * `export TMPDIR="<Isolated Data Dir>/tmp"`
   * `export XDG_DATA_HOME="<Isolated Data Dir>/Library/Application Support"`
   * `export XDG_CONFIG_HOME="<Isolated Data Dir>/Library/Preferences"`

これにより、親アプリ側のコードを一行も改変することなく、あらゆるファイル I/O とローカルストレージアクセスを強制的に独立したデータフォルダへ誘導します。

### 3. サンドボックス剥離とアドホック再署名
macOS の App Sandbox が有効なアプリは、システムによって厳密に `~/Library/Containers/<BundleID>` へのアクセスしか許可されません。ATBClone はバイナリから `com.apple.security.app-sandbox` フラグを取り除き、macOS 標準の `codesign -f -s -` コマンドでアドホック再署名を行います。これにより、アプリは任意のカスタムデータディレクトリへ自在にアクセスできるようになります。

---

## 💎 データとロジックの完全分離設計

ATBClone は **「プログラムロジック（Apps）」** と **「ユーザーデータ（Data）」** を完全に分離して管理します：

* **ロジック層 (`~/ATBClone/Apps/`)**：いつでも安全に再作成・削除・上書き同期が可能。
* **データ層 (`~/ATBClone/Data/`)**：ユーザーのチャット履歴、ローカルキャッシュ、設定情報が永続化。

親アプリがバージョンアップされた際も、古いクローンアプリ本体を置き換えるだけで、データフォルダは一切手を触れずに保持されるため、安全かつ確実な無損失アップデートが保証されます。

---

## ⚙️ 高度なレシピパラメータ解説

### 1. environment_injection (環境変数注入)
クローンアプリ起動時に追加で注入する環境変数をキー・バリュー形式で指定します：

```yaml
environment_injection:
  ELECTRON_ENABLE_LOGGING: "1"
  NODE_ENV: "production"
  SSL_CERT_FILE: "{DATA_DIR}/certs/ca.pem"
```

### 2. symlink_whitelist (シンボリックリンク白名単)
分離された環境内でも、特定のシステムリソースやフォント、ハードウェア支援機能のみ親アプリと共有したい場合に使用します：

```yaml
symlink_whitelist:
  - "~/Library/Fonts"
  - "~/Library/ColorSync"
```

### 3. launch_arguments (起動引数)
起動時に自動付与されるコマンドラインフラグを設定します：

```yaml
launch_arguments:
  - "--disable-gpu-shader-disk-cache"
  - "--no-first-run"
```

### 4. plist_overrides (Info.plist 上書き)
`Info.plist` の特定キーをカスタマイズします：

```yaml
plist_overrides:
  NSHighResolutionCapable: true
  LSUIElement: false
```

### 5. 動的パス環境変数マクロ
レシピ内の文字列に以下のマクロを埋め込むと、実行時に実際のパスへと自動置換されます：

* `{DATA_DIR}`：対象クローンの専用データ保存先パス。
* `{CLONE_NAME}`：クローンアプリの表示名。
* `{BUNDLE_ID}`：生成された新しい Bundle Identifier。
* `{HOST_APP}`：元の親アプリのフルパス。

---

## 📋 高度なカスタムレシピの完全な YAML サンプル

```yaml
version: "1.0"
name: "Discord"
description: "Discord 用のプロキシ＆環境変数注入付きハードクローン設定"

bundle_id: "com.hnc.discord"
strategy: "hard_clone"
strip_sandbox: true

injection_mode: "wrapper_hijack"

# ネットワークプロキシ
proxy:
  type: "socks5"
  host: "127.0.0.1"
  port: 10808

# 環境変数注入
environment_injection:
  DISCORD_USER_DATA_DIR: "{DATA_DIR}/discord_data"

# 起動引数
launch_arguments:
  - "--start-minimized"

# シンボリックリンク共有白名単
symlink_whitelist:
  - "~/Library/Audio"
```
"""

# 04-faq-and-troubleshooting.md
ch04 = """# 第4章：よくある質問 (FAQ)・システム診断・フィードバック

本章では、ユーザーからよく寄せられる疑問、セキュリティやアカウント保護に関する注意事項、内蔵診断ツール「Doctor」による環境チェック、そして不具合発生時の GitHub Issue 報告手順を解説します。

---

## 📑 目次

- [よくある質問 (FAQ)](#faq)
  - [1. クローンを作成すると元のアプリのデータに影響はありますか？](#1)
  - [2. クローンのデータはどこに保存されますか？バックアップと移行方法は？](#2)
  - [3. アカウントが BAN されるリスクはありますか？](#3-ban)
  - [4. 管理者パスワード (Root / Sudo) は必要ですか？](#4-root-sudo)
  - [5. 「開発元が未確認のため開けません」または破損エラーが出た場合の対処法は？](#5)
  - [6. クローンのアプリアイコンを変更するには？](#6)
  - [7. メッセンジャー系アプリでメニューバー常駐や通知が機能しない場合の対処法は？](#7)
- [システム環境診断 (Doctor ツール)](#doctor)
- [問題の発見と GitHub Issue 報告手順 (標準トラブルシューティング)](#github-issue)
  - [ステップ 1: メイン画面で異常が発生したクローンを選択し「詳細」を開く](#1_1)
  - [ステップ 2: 「クローン詳細」から診断レポートをコピー](#2_1)
  - [ステップ 3: GitHub Issue に投稿](#3-github-issue)
- [コミュニティとサポート](#_1)

---

## ❓ よくある質問 (FAQ)

### 1. クローンを作成すると元のアプリのデータに影響はありますか？
**全く影響ありません。**
ATBClone は完全な独立データディレクトリ（`~/ATBClone/Data/<クローン名>`）を分離して使用します。元の親アプリのデータやキャッシュディレクトリには一切触れません。

### 2. クローンのデータはどこに保存されますか？バックアップと移行方法は？
* **保存場所**：デフォルトで `~/ATBClone/Data/<クローン名>` にすべて保存されます。
* **バックアップと移行**：ダッシュボードでクローンの **「フォルダを開く」** アイコンをクリックし、表示されたフォルダを外付け SSD や別の Mac にコピーするだけで、完全にデータ移行が可能です。

### 3. アカウントが BAN されるリスクはありますか？
ATBClone は **「非侵入型（Non-Invasive）サンドボックス分離技術」** を採用しています。アプリの通信プロトコルを偽装したり、メモリ内のゲームデータを改ざんしたりする「チートツール / フック」ではありません。macOS ネイティブの安全な環境変数差し替えにより動作するため、公式アプリそのものが動作している状態とシステム上区別されず、安全にご利用いただけます。

さらに、**独立プロキシ機能**を併用することで、アプリごとに IP アドレスを分散させ、同一 IP からの複数アカウント同時アクセスによる検知リスクも低減できます。

### 4. 管理者パスワード (Root / Sudo) は必要ですか？
**一切不要です。**
ATBClone のすべての複製、バイナリラッパー生成、アドホック署名、データ管理は、すべて現在のユーザー権限（User Space）内で完結します。システムファイル（`/System`）を改ざんすることはありません。

### 5. 「開発元が未確認のため開けません」または破損エラーが出た場合の対処法は？
macOS Gatekeeper のセキュリティ保護によるものです。以下のいずれかの方法で解消できます：
1. **Finder から右クリックで開く**：クローンアプリ（`.app`）を右クリック（二本指タップ）し、**「開く」** を選択してダイアログで「開く」をクリック。
2. **ターミナルコマンドで隔離属性を解除**：
   ```bash
   xattr -cr ~/ATBClone/Apps/<クローン名>.app
   ```

### 6. クローンのアプリアイコンを変更するには？
1. ATBClone ダッシュボードで対象クローンカードの **「編集」** をクリックします。
2. アイコン表示領域に、お好みの `.png` または `.icns` 画像をドラッグ＆ドロップして保存します。

### 7. メッセンジャー系アプリでメニューバー常駐や通知が機能しない場合の対処法は？
一部のアプリ（WeChat や Slack など）は、ハードクローン時に Bundle ID が変更されると通知センターへの登録がリセットされる場合があります：
* macOS の **「システム設定 ➔ 通知」** を開き、クローンアプリ名（例：`WeChat-Work`）の通知が許可されているか確認してください。

---

## 🩺 システム環境診断 (Doctor ツール)

環境の依存関係や権限が正常か確認するには、内蔵の Doctor ツールをご利用ください：

* **GUI から**：左サイドバーの **「システム環境健診 (Doctor)」** をクリック。
* **CLI から**：
  ```bash
  atbclone doctor
  ```

Doctor ツールは以下を自動チェックします：
* [✔] macOS バージョン互換性 (macOS 12+ Monterey / Ventura / Sonoma / Sequoia)
* [✔] Xcode Command Line Tools または `codesign` コマンドの稼働状態
* [✔] アプリおよびデータ保存ディレクトリの書き込み権限
* [✔] ビルトインレシピ定義の構文整合性

---

## 🐞 問題の発見と GitHub Issue 報告手順 (標準トラブルシューティング)

アプリの起動に失敗したり異常が発生した場合は、以下の手順で正確な診断情報を取得してご報告いただけます：

### ステップ 1: メイン画面で異常が発生したクローンを選択し「詳細」を開く
対象クローンカードをクリックし、ツールバーの **「詳細 (Details)」** ボタンを押します。

### ステップ 2: 「クローン詳細」から診断レポートをコピー
「分身詳細」ダイアログが表示されます。ここには以下の技術情報が自動収集されています：
* 基礎情報（クローン名、戦略、Bundle ID、元アプリパス）
* 実行可能バイナリ種別とアーキテクチャ（arm64 / x86_64）
* 注入された環境変数とプロキシ設定
* 直近のクラッシュログ・起動ログの抜粋

下部の **「診断情報をコピー (Copy Diagnostic Info)」** ボタンをクリックします。

### ステップ 3: GitHub Issue に投稿
1. ブラウザで [ATBClone Issues](https://github.com/aitobox/ATBClone/issues) を開きます。
2. **「New Issue」** をクリックし、「Bug Report」を選択します。
3. コピーした診断情報を貼り付けて送信してください。開発チームが迅速に原因を調査します。

---

## 💬 コミュニティとサポート

* **GitHub 公式リポジトリ**：[https://github.com/aitobox/ATBClone](https://github.com/aitobox/ATBClone)
* **ドキュメント公式サイト**：[https://clone.aitobox.com](https://clone.aitobox.com)
* **ディスカッション・Q&A**：[GitHub Discussions](https://github.com/aitobox/ATBClone/discussions)
"""

with open(f"{JA_DIR}/03-under-the-hood-and-internals.md", "w", encoding="utf-8") as f:
    f.write(ch03)
print("✓ Created ja/03-under-the-hood-and-internals.md")

with open(f"{JA_DIR}/04-faq-and-troubleshooting.md", "w", encoding="utf-8") as f:
    f.write(ch04)
print("✓ Created ja/04-faq-and-troubleshooting.md")
