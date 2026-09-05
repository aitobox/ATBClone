# Chapter 2: Custom Recipes for Niche Apps

While ATBClone comes with 33+ pre-configured recipes for popular social, development, and browser applications, you may want to clone an unlisted or niche application (such as internal company software, indie developer tools, or regional messaging clients).

This chapter explains how to create custom recipes using the built-in **App Prober** and **Recipe Editor**, and details what each basic configuration parameter means.

---

## 📑 Table of Contents

- [Understanding App Recipes](#understanding-app-recipes)
- [Method 1: Using the Intelligent App Prober (Recommended)](#method-1-using-the-intelligent-app-prober-recommended)
- [Method 2: Using the Visual Recipe Editor](#method-2-using-the-visual-recipe-editor)
- [Basic Parameters Reference](#basic-parameters-reference)
  - [1. `bundle_id` (Bundle Identifier)](#1-bundle_id-bundle-identifier)
  - [2. `app_name` (Application Name)](#2-app_name-application-name)
  - [3. `strategy` (Cloning Strategy)](#3-strategy-cloning-strategy)
  - [4. `strip_sandbox` (Sandbox Stripping)](#4-strip_sandbox-sandbox-stripping)
  - [5. `proxy` (Proxy Settings)](#5-proxy-proxy-settings)
  - [6. `injection_strategy` (Injection Strategy)](#6-injection_strategy-injection-strategy)
- [Sample Custom Recipe YAML](#sample-custom-recipe-yaml)
- [Next Steps](#next-steps)

---

## 🧩 Understanding App Recipes

An **App Recipe** is a declarative blueprint that instructs ATBClone how to handle an application:

* Which cloning engine to use (**Hard Clone** vs. **Soft Clone**).
* How to isolate user data (e.g., via `$HOME` environment hijack or `--user-data-dir` CLI flags).
* Whether to strip Apple App Sandbox entitlements.
* What system folders (like Keychain credentials) should remain bridged.

All user custom recipes are saved as human-readable `.yaml` files in:
`~/ATBClone/recipes/<bundle_id>.yaml`

Whenever you clone an app, ATBClone checks your custom recipes first, giving them priority over built-in presets.

---

## 🔍 Method 1: Using the Intelligent App Prober (Recommended)

The **App Prober** is ATBClone's built-in binary inspection tool. It inspects Mach-O binary architectures, detects runtime frameworks (Electron, Chromium, Gecko, Cocoa), scans code signatures, and automatically generates the optimal recipe.

```text
+-------------------------------------------------------------+
|  🔍 App Prober                                              |
|                                                             |
|  Target Application:                                        |
|  [/Applications/CustomTool.app               ] [ Browse... ]|
|                                              [ Start Probe ]|
|  ─────────────────────────────────────────────────────────  |
|  Analysis Results:                                          |
|  • Application: CustomTool                                  |
|  • Bundle ID:   com.example.customtool                      |
|  • Sandbox:     Enabled (App Sandbox Detected)              |
|  • Frameworks:  Electron, Node.js                           |
|  • Strategy:    hard_clone                                  |
|                                                             |
|  [ Save as Recipe 💾 ]                                      |
+-------------------------------------------------------------+
```

### Step-by-Step Workflow:
1. Click **"App Prober"** (`🔍`) in the ATBClone sidebar navigation.
2. Click **"Browse..."** and select your niche `.app` bundle.
3. Click **"Start Probe"**.
4. The Prober analyzes the application structure in milliseconds and displays:
   * **App Name & Bundle ID**: Extracted from `Info.plist`.
   * **Sandbox Status**: Checks if `com.apple.security.app-sandbox` is enforced.
   * **Embedded Frameworks**: Detects Electron, Chromium Embedded Framework (CEF), Qt, Flutter, React Native, or Native Cocoa.
   * **Recommended Strategy**: Determines whether `hard_clone` or `soft_clone` is optimal.
5. Click **"Save as Recipe 💾"**.

Once saved, the recipe is immediately registered into your local library. You can now launch the **"+ New Clone"** wizard and clone the app with full isolation support!

---

## ✏️ Method 2: Using the Visual Recipe Editor

If you prefer to manually craft or fine-tune a recipe:

1. Click **"Recipes"** (`📑`) in the sidebar navigation.
2. Click the **"+ New Recipe"** button on the top right.
3. Fill in the basic configuration fields:
   * **Bundle ID**: e.g., `com.company.internalapp`
   * **Application Name**: e.g., `InternalApp`
   * **Strategy**: `hard_clone` or `soft_clone`
   * **Strip Sandbox**: Toggle on/off
   * **Proxy Settings**: Enable dedicated proxy if needed
4. Click **"Save Recipe"**.

You can also click **"Edit"** on any existing built-in or custom recipe in the table to create an override copy.

---

## 📖 Basic Parameters Reference

Below is a detailed guide to all fundamental recipe parameters:

### 1. `bundle_id` (Bundle Identifier)
* **Type**: `string` (e.g., `com.tencent.xinWeChat`, `com.google.Chrome`)
* **Description**: The unique reverse-DNS identifier defined in the app's `Info.plist`. This is the primary lookup key used by ATBClone to match recipes.

---

### 2. `app_name` (Application Name)
* **Type**: `string` (e.g., `WeChat`, `Telegram`, `Cursor`)
* **Description**: The human-readable title of the application shown in the ATBClone interface.

---

### 3. `strategy` (Cloning Strategy)
* **Type**: `enum` (`hard_clone` | `soft_clone`)
* **Description**: Determines the underlying engine used to create and isolate the clone.

| Strategy | Mechanism | When to Use |
| :--- | :--- | :--- |
| **`hard_clone`** | Full application bundle copy, `CFBundleIdentifier` modification, binary launcher hijack, and ad-hoc code re-signing. | Native Cocoa apps, social messengers (WeChat, Telegram, QQ, Lark, Discord), and any app needing complete TCC permission separation. |
| **`soft_clone`** | Generates a lightweight `.app` launcher that runs the primary binary with custom CLI isolation parameters (like `--user-data-dir`). | Chromium browsers, code editors (VS Code, Cursor, Zed), and Firefox/Gecko apps. |

---

### 4. `strip_sandbox` (Sandbox Stripping)
* **Type**: `boolean` (`true` | `false`, default: `false`)
* **Description**: Controls whether ATBClone should extract and remove `<key>com.apple.security.app-sandbox</key>` from the app's code signing entitlements during Hard Clone creation.

> [!TIP]
> * **`false` (Recommended Default)**: Keeps native macOS App Sandbox active. The clone receives a distinct container directory in `~/Library/Containers/<NewBundleID>` for clean sandbox isolation.
> * **`true` (Fallback for strictly locked apps)**: Strips sandbox restrictions if an app crashes when its bundle ID is modified or requires access to shared host utilities.

---

### 5. `proxy` (Proxy Settings)
* **Type**: `object`
* **Description**: Defines a default network proxy configuration for instances created with this recipe.

```yaml
proxy:
  enabled: true       # boolean: true or false
  type: http          # enum: "http", "https", or "socks5"
  host: 127.0.0.1     # string: proxy server IP address or hostname
  port: 7890          # integer: proxy server port
```

---

### 6. `injection_strategy` (Injection Strategy)
* **Type**: `enum` (`auto` | `dylib` | `launcher`, Default: `auto`)
* **Description**: Configures the underlying environment isolation technique for `hard_clone` operations.

| Injection Strategy | Mechanism | Key Benefits & Typical Use Cases |
| :--- | :--- | :--- |
| **`auto` (Default & Recommended)** | Statically inspects the binary Mach-O header padding headroom. If space is sufficient, uses `dylib`; otherwise automatically falls back to `launcher`. | Best for almost all apps. Ensures maximum compatibility and seamless adaptation across app updates. |
| **`dylib` (Forced Dylib Injection)** | Inserts `LC_LOAD_DYLIB` directly into the Mach-O binary. Environment variables are set in-process before `main()`, with **zero `execv` process replacement**. | Native Cocoa/communication apps (WeChat, Telegram, QQ). Fully supports Menu Bar status items (`NSStatusItem`) and macOS Notification Center. |
| **`launcher` (Forced Launcher Packaging)** | Compiles a native Mach-O C launcher and backs up the original binary as `.bin` launched via `execv`. | Apps requiring custom CLI parameters or binaries with tightly packed Mach-O headers. |

---

## 📄 Sample Custom Recipe YAML

Here is what a complete custom recipe file looks like:

```yaml
# ========================================================
# ATBClone Custom Recipe - ExampleApp
# Saved at: ~/ATBClone/recipes/com.example.app.yaml
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

## ⏭️ Next Steps

* To understand how `environment_injection`, `launch_args`, and `symlink_whitelist` work in deep isolation scenarios, continue to **[Chapter 3: Under the Hood & Advanced Parameters](03-under-the-hood-and-internals.md)**.
* For common questions, diagnostics, and issue reporting, visit **[Chapter 4: FAQ & Diagnostic Troubleshooting](04-faq-and-troubleshooting.md)**.
