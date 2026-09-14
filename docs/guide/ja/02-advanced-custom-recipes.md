# 第2章：カスタムレシピの作成と基本パラメータ

ATBClone は多数の一般的なアプリ向けにビルトインレシピを標準搭載していますが、社内独自ツール、マイナーな専門ソフトウェア、最新アプリなど、未登録のアプリをクローンしたい場合もあります。本章では、**App Prober（スマートプローブ）** を使用した自動分析と、ビジュアルレシピエディタによるカスタムルールの作成手順を解説します。

---

## 📑 目次

- [App Prober による未知アプリの自動診断](#app-prober)
  - [GUI からのワンクリック診断](#gui)
  - [CLI ターミナルからの詳細プローブ](#cli)
  - [診断結果の判定ポイント](#_1)
- [ビジュアルレシピエディタの使い方](#_2)
- [レシピ YAML 構造と基本パラメータ解説](#yaml)
  - [1. bundle_id (バンドル識別子)](#1-bundle_id)
  - [2. strategy (クローン戦略)](#2-strategy)
  - [3. strip_sandbox (サンドボックス剥離)](#3-strip_sandbox)
  - [4. proxy (プロキシ設定)](#4-proxy)
- [カスタムレシピのテストと保存](#_3)

---

## 🔍 App Prober による未知アプリの自動診断

ATBClone は強力な静的・動的解析ツール **App Prober** を内蔵しており、対象アプリの内部バイナリ、署名メタデータ、権限付与リスト（Entitlements）を数秒で網羅的にスキャンします。

### GUI からのワンクリック診断
1. メイン画面のサイドバーまたはツールメニューから **「レシピ管理」** を選択します。
2. 右上の **「アプリを診断 (Probe App)」** ボタンをクリックします。
3. スキャンしたい `.app` を選択すると、解析パネルに以下の情報が即座に展開されます：
   * **フレームワーク種別**：Electron、Chromium、Flutter、Qt、ネイティブ Cocoa/AppKit、Java、NW.js など。
   * **サンドボックス状態**：App Sandbox 有効・無効。
   * **推奨戦略**：`Hard Clone` または `Soft Clone`。

### CLI ターミナルからの詳細プローブ
ターミナルから直接診断を実行することも可能です：

```bash
atbclone probe /Applications/Slack.app
```

出力例：

```text
================================================================================
ATBClone Application Prober
Target: /Applications/Slack.app
================================================================================
[+] Bundle ID: com.tinyspeck.slackmacgap
[+] Executable: /Applications/Slack.app/Contents/MacOS/Slack
[+] Framework: Electron (Chromium-based)
[+] App Sandbox: Enabled (com.apple.security.app-sandbox)
[+] Hardened Runtime: Yes
[+] Recommendation: Strategy=hard_clone, StripSandbox=true
================================================================================
```

### 診断結果の判定ポイント
* **Electron / Chromium 系アプリ**：通常は `soft_clone` で十分機能しますが、複数インスタンスの通知やメニューバー常駐を完全に分離したい場合は、`hard_clone` を選択し `strip_sandbox: true` を設定するのが最も安定します。
* **ネイティブ Cocoa / Sandbox アプリ**：親アプリがサンドボックス内で動作している場合、`hard_clone` かつ `strip_sandbox: true` が必須となります。

---

## 🛠️ ビジュアルレシピエディタの使い方

診断完了後、**「レシピを生成して編集」** をクリックすると、視覚的なフォームエディタが開きます：

```text
+-------------------------------------------------------------+
|  📝 レシピエディタ - Slack.yaml                               |
|                                                             |
|  アプリ識別名:   [ Slack                                  ] |
|  Bundle ID:     [ com.tinyspeck.slackmacgap              ] |
|  クローン戦略:   (●) Hard Clone (ハード)  ( ) Soft Clone   |
|  サンドボックス: [✔] サンドボックス制限を強制解除 (推奨)     |
|  プロキシ設定:   [ http://127.0.0.1:7890                  ] |
|                                                             |
|  [ YAML をプレビュー ]     [ テスト実行 ]     [ レシピを保存 ]  |
+-------------------------------------------------------------+
```

---

## 📜 レシピ YAML 構造と基本パラメータ解説

生成されたレシピファイルはシンプルな YAML 形式で保存されます。以下に代表的な基本構成を示します：

```yaml
version: "1.0"
name: "Slack"
description: "Slack メッセンジャー用の独立マルチインスタンス設定"

# 基本パラメータ
bundle_id: "com.tinyspeck.slackmacgap"
strategy: "hard_clone"
strip_sandbox: true

# ネットワークプロキシ (任意)
proxy:
  type: "http"
  host: "127.0.0.1"
  port: 7890
```

### 1. bundle_id (バンドル識別子)
対象アプリの正規 Bundle Identifier を指定します（例：`com.tencent.xinWeChat`）。この値はクローン生成時に新しい識別子へ自動置換されます。

### 2. strategy (クローン戦略)
* `hard_clone`：バイナリ全体をコピーし、Bundle ID や環境変数ラッパーを注入します。
* `soft_clone`：バイナリは複製せず、データ保存先を指定するコマンドライン引数のみで起動します。

### 3. strip_sandbox (サンドボックス剥離)
`true` に設定すると、Mach-O バイナリおよびコード署名から `com.apple.security.app-sandbox` 権限を完全に除去します。これにより、クローンアプリが親アプリの制限されたデータコンテナ（`~/Library/Containers/`）に束縛されず、指定したカスタムデータフォルダを自由に読み書きできるようになります。

### 4. proxy (プロキシ設定)
クローンアプリの通信トラフィックを特定のプロキシサーバー経由にルーティングします。
* `type`：`http`、`https`、または `socks5`。
* `host`：IP アドレスまたはドメイン（例：`127.0.0.1`）。
* `port`：ポート番号（例：`7890`）。

---

## 💾 カスタムレシピのテストと保存

1. エディタ下部の **「テスト実行 (Dry Run)」** をクリックし、エラーがないか検証します。
2. 問題がなければ **「レシピを保存」** をクリックします。
3. 保存されたカスタムレシピは、次回以降 **「+ 新規クローン」** ウィザードの候補一覧に自動表示されます。
