# Chapter 4: FAQ & Diagnostic Troubleshooting

This chapter answers frequently asked questions regarding data privacy, account safety, storage paths, and macOS permissions. It also provides a step-by-step guide for using the built-in **Doctor** diagnostic tool and copying diagnostic data from the Clone Details dialog to submit a GitHub Issue.

---

## 📑 Table of Contents

- [Frequently Asked Questions (FAQ)](#frequently-asked-questions-faq)
  - [1. Will creating a clone affect my original app's data?](#1-will-creating-a-clone-affect-my-original-apps-data)
  - [2. Where is cloned data stored, and how do I back it up?](#2-where-is-cloned-data-stored-and-how-do-i-back-it-up)
  - [3. Will my account get banned for multi-instancing?](#3-will-my-account-get-banned-for-multi-instancing)
  - [4. Do I need Administrator (Root / Sudo) privileges?](#4-do-i-need-administrator-root--sudo-privileges)
  - [5. What should I do if macOS says "App is damaged and can't be opened"?](#5-what-should-i-do-if-macos-says-app-is-damaged-and-cant-be-opened)
  - [6. How do I change the clone's icon?](#6-how-do-i-change-the-clones-icon)
- [System Diagnostics (Doctor Tab)](#system-diagnostics-doctor-tab)
- [Reporting Issues to GitHub (Step-by-Step Guide)](#reporting-issues-to-github-step-by-step-guide)
  - [Step 1: Open Clone Details](#step-1-open-clone-details)
  - [Step 2: Copy Application Information from Clone Details](#step-2-copy-application-information-from-clone-details)
  - [Step 3: Submit Issue on GitHub](#step-3-submit-issue-on-github)
- [Community & Support](#community--support)

---

## ❓ Frequently Asked Questions (FAQ)

### 1. Will creating a clone affect my original app's data?
**No. Never.**

ATBClone enforces strict physical and container-level isolation:
* The primary application continues reading and writing to its original standard paths (such as `~/Library/Application Support/` or `~/Library/Containers/<OriginalBundleID>`).
* The clone operates exclusively inside its own isolated folder (e.g., `~/ATBClone/Data/<CloneName>/`).
* Both instances run concurrently without database locking, preference collisions, or cache pollution.

---

### 2. Where is cloned data stored, and how do I back it up?
By default, all user data (databases, local chat archives, cache, cookies, and preferences) is stored in:
`~/ATBClone/Data/<CloneName>/`

```text
~/ATBClone/
├── config.yaml           # User configuration & preferences
├── clones.yaml           # Registry of all created clones
├── recipes/              # User custom recipe directory
└── Data/
    ├── WeChat2/          # WeChat clone data sandbox
    │   ├── Home/         # Isolated $HOME directory
    │   └── Tmp/          # Isolated $TMPDIR directory
    └── Telegram-Work/    # Telegram clone data sandbox
```

#### How to Back Up or Migrate:
* **To Back Up**: Copy or compress the `~/ATBClone/Data/<CloneName>` folder to an external backup drive or cloud storage.
* **To Migrate to a New Mac**: Copy your entire `~/ATBClone/` directory to the new Mac, install ATBClone, and clone your apps using the same names. Your accounts and chat histories will be immediately recognized!

---

### 3. Will my account get banned for multi-instancing?
**ATBClone operates strictly at the macOS operating system environment level.**

* **No Reverse-Engineering / Code Injection**: ATBClone does **not** use runtime code hooking (such as Frida, Cycript, or dynamic dylib injection) and does **not** tamper with in-memory application logic or network packets.
* **Pure Environment Deception**: The application runs completely unmodified; it is simply presented with an isolated `$HOME` directory and custom bundle identifier.
* **Anti-Fingerprint Proxy Isolation**: By configuring a dedicated HTTP or SOCKS5 proxy per clone, each instance can connect via a distinct IP address, preventing IP-level association across multiple accounts.

> [!IMPORTANT]
> While ATBClone provides safe, clean OS-level sandbox isolation, you must still comply with the terms of service of individual platforms (e.g., avoiding abusive mass messaging or unauthorized bot automation).

---

### 4. Do I need Administrator (Root / Sudo) privileges?
* **When installing to `~/ATBClone/Apps` (Default & Recommended)**: **Zero administrator privileges or passwords required.** Everything runs in standard user space.
* **When installing to system `/Applications`**: macOS will prompt you once via standard native system dialog for authorization to write to the global application folder.

---

### 5. What should I do if macOS says "App is damaged and can't be opened"?
This is caused by macOS Gatekeeper flagging modified application bundles with the quarantine extended attribute (`com.apple.quarantine`).

#### Solution:
Open Terminal and run the quarantine removal command:
```bash
xattr -cr "/path/to/YourClonedApp.app"
```
Or simply select the clone inside ATBClone and click **"Update"** to allow ATBClone to automatically strip quarantine attributes and refresh the ad-hoc signature.

---

### 6. How do I change the clone's icon?
1. Open Finder and locate your clone in `~/ATBClone/Apps`.
2. Select the app and press `Cmd + I` (Get Info).
3. Drag any `.icns` or `.png` image file onto the small application icon at the top-left of the Info inspector window.

---

## 🩺 System Diagnostics (Doctor Tab)

If you encounter unexpected behavior during cloning or signing, run our built-in system diagnostic check:

```text
+-------------------------------------------------------------+
|  🩺 System Doctor                                           |
|                                                             |
|  System Environment Checks:                                 |
|  [✔] macOS Architecture: Apple Silicon (arm64)              |
|  [✔] Xcode Command Line Tools: Installed (/Library/...)     |
|  [✔] Code Signing Utility (codesign): Available             |
|  [✔] Plist Processor (PlistBuddy): Available                |
|  [✔] Application Directory Permissions: Writable            |
|  [✔] Data Directory Permissions: Writable                   |
|                                                             |
|  [ Re-run Diagnostics 🔄 ]                                  |
+-------------------------------------------------------------+
```

1. Click **"Doctor"** (`🩺`) in the ATBClone sidebar navigation.
2. The Doctor probe automatically validates:
   * **Xcode Command Line Tools (`xcode-select -p`)**: Ensures Apple developer tools are installed for code signing.
   * **Codesign & PlistBuddy**: Verifies system binary utilities.
   * **Storage Directory Access**: Checks read/write permissions for `~/ATBClone/Apps` and `~/ATBClone/Data`.
3. If any item shows an error or warning, follow the on-screen resolution tips (e.g., running `xcode-select --install`).

---

## 🐛 Reporting Issues to GitHub (Step-by-Step Guide)

If you find an application that fails to clone, or crashes upon opening after cloning, please report it to our GitHub repository:

### Step 1: Open Clone Details
1. Open the ATBClone main window.
2. In either **Card Grid View** or **Table View**, select the problematic clone.
3. Click the **"Details"** (`ℹ️` / `详情`) button to open the Clone Details dialog.

```text
+-------------------------------------------------------------+
|  ℹ️ Clone Details - WeChat2                                 |
|                                                             |
|  Basic Information:                                         |
|  • Source App:      /Applications/WeChat.app                |
|  • Bundle ID:       com.tencent.xinWeChat                   |
|  • New Bundle ID:   com.tencent.xinWeChat.atbclone.WeChat2  |
|  • Strategy:        hard_clone                              |
|  • Destination:     /Users/username/ATBClone/Apps/WeChat2.app|
|  • Data Directory:  /Users/username/ATBClone/Data/WeChat2   |
|  • Proxy:           http://127.0.0.1:7890                   |
|                                                             |
|  Injected Parameters & Environment:                         |
|  • Launch Args:     --user-data-dir=...                     |
|  • Env Vars:        HOME=..., TMPDIR=...                    |
|  • Exec Command:    env HOME=... /path/to/WeChat.bin        |
|                                                             |
|  [ Close ]                                                  |
+-------------------------------------------------------------+
```

---

### Step 2: Copy Application Information from Clone Details
The Clone Details dialog displays all critical runtime parameters:
* **Basic Information**: Exact source path, mutated bundle identifier, strategy, and directory destinations.
* **Launch Arguments**: Injected command-line parameters.
* **Environment Variables**: Injected `$HOME`, `$TMPDIR`, and proxy configurations.
* **Execution Command**: The exact startup command.

Simply select and copy the configuration and environment text from the dialog.

---

### Step 3: Submit Issue on GitHub
1. Navigate to the official ATBClone Issues page:
   👉 **[https://github.com/aitobox/ATBClone/issues](https://github.com/aitobox/ATBClone/issues)**
2. Click **"New Issue"**.
3. Fill out the issue template with:
   * **App Name & Version**: e.g., WeChat v3.8.7.
   * **macOS Version & Chip**: e.g., macOS 14.5 Sonoma on M2 Max.
   * **Cloning Strategy**: `hard_clone` or `soft_clone`.
   * **Clone Details Information**: Paste the text copied from the Clone Details dialog directly into the issue description, along with any error messages from the ATBClone **Logs** tab.

Our core maintainers will review the issue and release an updated recipe or fix in the next version!

---

## 🤝 Community & Support

* **GitHub Repository**: [https://github.com/aitobox/ATBClone](https://github.com/aitobox/ATBClone)
* **Release Downloads**: [https://github.com/aitobox/ATBClone/releases](https://github.com/aitobox/ATBClone/releases)
* **Issues & Feedback**: [https://github.com/aitobox/ATBClone/issues](https://github.com/aitobox/ATBClone/issues)

Thank you for using ATBClone! 🚀
