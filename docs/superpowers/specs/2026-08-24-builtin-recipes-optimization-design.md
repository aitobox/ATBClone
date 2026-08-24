# Design Spec: Built-in Recipes Optimization & Standardization

- **Date**: 2026-08-24
- **Status**: Approved
- **Target**: `src/atbclone/recipes/builtin/*.yaml`, `tests/test_recipes.py`

---

## 1. Background & Problem Statement

ATBClone contains 33 built-in YAML recipes in `src/atbclone/recipes/builtin/`.
Following the implementation of intelligent data directory probing, framework detection, and `LaunchArgumentValidator`, an audit of the built-in recipes revealed:
1. **Missing `app_type` declarations**: Over 20 built-in recipes lacked explicit `app_type` fields (such as `electron`, `chromium`, `cocoa`, or `generic`), requiring fallback heuristic detection at runtime.
2. **Inaccurate `strip_sandbox` flags**: Native sandboxed apps like WeChat (`com.tencent.xinWeChat`) and QQ (`com.tencent.qq`) had `strip_sandbox: false`, which can cause container conflicts on newer macOS versions (Sonoma / Sequoia).
3. **Format inconsistencies**: Trailing newlines or redundant empty fields in some YAML files.

---

## 2. Goals & Key Decisions

1. **Explicit `app_type` on all 33 Built-in Recipes**:
   - Assign exact `app_type` (`chromium`, `electron`, `firefox`, `cocoa`, `generic`) to all 33 YAML recipes so framework whitelists and language injections function with maximum reliability.
2. **Accurate `strip_sandbox` for Sandboxed Hard Clones**:
   - Set `strip_sandbox: true` for apps with `com.apple.security.app-sandbox` entitlements (WeChat, QQ, Douyin, CapCut, 剪映, NetEase Music, WPS Office, ChatGPT, Gemini, LINE, etc.).
3. **Preserve Verified Isolation Strategies**:
   - Web browsers and code editors (Chrome, Edge, Brave, Arc, VS Code, Cursor, Firefox, Tor Browser) retain their CLI launch arguments (`--user-data-dir` / `-profile`).
   - Desktop IM and media tools (WeChat, QQ, Lark, Slack, Telegram, CapCut, NetEase Music, etc.) retain their proven `hard_clone` with `HOME`/`TMPDIR` environment isolation.
4. **Automated Schema Integrity Testing**:
   - Enforce in `tests/test_recipes.py` that all built-in recipes contain valid and explicit `app_type` and pass Pydantic validation.

---

## 3. Detailed Recipes Matrix

| File | Bundle ID | App Name | Strategy | `app_type` | `strip_sandbox` | Launch Args / Env Injection |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `com.anthropic.claudefordesktop.yaml` | `com.anthropic.claudefordesktop` | Claude | `hard_clone` | `electron` | `false` | `HOME/TMPDIR` |
| `com.bilibili.bilibiliPC.yaml` | `com.bilibili.bilibiliPC` | 哔哩哔哩 | `hard_clone` | `electron` | `false` | `HOME/TMPDIR` |
| `com.brave.Browser.yaml` | `com.brave.Browser` | Brave Browser | `soft_clone` | `chromium` | `false` | `["--user-data-dir={{ATB_DATA_DIR}}"]` |
| `com.bytedance.douyin.desktop.yaml` | `com.bytedance.douyin.desktop` | 抖音 | `hard_clone` | `electron` | `true` | `HOME/TMPDIR` |
| `com.electron.lark.yaml` | `com.electron.lark` | 飞书 | `hard_clone` | `electron` | `false` | `HOME/TMPDIR` |
| `com.google.Chrome.yaml` | `com.google.Chrome` | Chrome | `hard_clone` | `chromium` | `false` | `["--user-data-dir={{ATB_DATA_DIR}}"]` |
| `com.google.GeminiMacOS.yaml` | `com.google.GeminiMacOS` | Gemini | `hard_clone` | `cocoa` | `true` | `HOME/TMPDIR` |
| `com.google.android.studio.yaml` | `com.google.android.studio` | Android Studio | `hard_clone` | `generic` | `false` | `HOME/TMPDIR` |
| `com.google.antigravity-ide.yaml` | `com.google.antigravity-ide` | Antigravity IDE | `hard_clone` | `electron` | `false` | `HOME/TMPDIR` |
| `com.google.antigravity.yaml` | `com.google.antigravity` | Antigravity | `hard_clone` | `electron` | `false` | `HOME/TMPDIR` |
| `com.hnc.Discord.yaml` | `com.hnc.Discord` | Discord | `hard_clone` | `electron` | `false` | `HOME/TMPDIR` |
| `com.kingsoft.wpsoffice.mac.yaml` | `com.kingsoft.wpsoffice.mac` | WPS Office | `hard_clone` | `cocoa` | `true` | `HOME/TMPDIR` |
| `com.lemon.lvoverseas.yaml` | `com.lemon.lvoverseas` | CapCut | `hard_clone` | `chromium` | `true` | `HOME/TMPDIR` |
| `com.lemon.lvpro.yaml` | `com.lemon.lvpro` | 剪映专业版 | `hard_clone` | `chromium` | `true` | `HOME/TMPDIR` |
| `com.microsoft.VSCode.yaml` | `com.microsoft.VSCode` | VS Code | `soft_clone` | `electron` | `false` | `["--user-data-dir={{ATB_DATA_DIR}}"]` |
| `com.microsoft.edgemac.yaml` | `com.microsoft.edgemac` | Edge | `hard_clone` | `chromium` | `false` | `["--user-data-dir={{ATB_DATA_DIR}}"]` |
| `com.netease.163music.yaml` | `com.netease.163music` | 网易云音乐 | `hard_clone` | `chromium` | `true` | `HOME/TMPDIR` |
| `com.openai.chat.yaml` | `com.openai.chat` | ChatGPT | `hard_clone` | `cocoa` | `true` | `HOME/TMPDIR` |
| `com.openai.codex.yaml` | `com.openai.codex` | ChatGPT | `hard_clone` | `cocoa` | `true` | `HOME/TMPDIR` |
| `com.skype.skype.yaml` | `com.skype.skype` | Skype | `hard_clone` | `electron` | `true` | `HOME/TMPDIR` |
| `com.tencent.WeWorkMac.yaml` | `com.tencent.WeWorkMac` | 企业微信 | `hard_clone` | `chromium` | `true` | `HOME/TMPDIR` |
| `com.tencent.qq.yaml` | `com.tencent.qq` | QQ | `hard_clone` | `electron` | `true` | `HOME/TMPDIR` |
| `com.tencent.xinWeChat.yaml` | `com.tencent.xinWeChat` | 微信 | `hard_clone` | `cocoa` | `true` | `HOME/TMPDIR` + symlinks |
| `com.tinyspeck.slackmacgap.yaml` | `com.tinyspeck.slackmacgap` | Slack | `hard_clone` | `electron` | `false` | `HOME/TMPDIR` |
| `com.todesktop.230313mzl4w4u92.yaml` | `com.todesktop.230313mzl4w4u92` | Cursor | `soft_clone` | `electron` | `false` | `["--user-data-dir={{ATB_DATA_DIR}}"]` |
| `com.valvesoftware.steam.yaml` | `com.valvesoftware.steam` | Steam | `hard_clone` | `cocoa` | `false` | `HOME/TMPDIR` |
| `company.thebrowser.Browser.yaml` | `company.thebrowser.Browser` | Arc | `hard_clone` | `chromium` | `false` | `["--user-data-dir={{ATB_DATA_DIR}}"]` |
| `dev.zed.Zed.yaml` | `dev.zed.Zed` | Zed | `soft_clone` | `generic` | `false` | `launch_args: []` |
| `jp.naver.line.mac.yaml` | `jp.naver.line.mac` | LINE | `hard_clone` | `cocoa` | `true` | `HOME/TMPDIR` |
| `org.mozilla.firefox.yaml` | `org.mozilla.firefox` | Firefox | `soft_clone` | `firefox` | `false` | `["-profile", "{{ATB_DATA_DIR}}"]` |
| `org.telegram.desktop.yaml` | `org.telegram.desktop` | Telegram Desktop | `hard_clone` | `generic` | `false` | `HOME/TMPDIR` |
| `org.torproject.torbrowser.yaml` | `org.torproject.torbrowser` | Tor Browser | `soft_clone` | `firefox` | `false` | `["-profile", "{{ATB_DATA_DIR}}"]` |
| `ru.keepcoder.Telegram.yaml` | `ru.keepcoder.Telegram` | Telegram | `hard_clone` | `cocoa` | `false` | `HOME/TMPDIR` |

---

## 4. Verification Plan

1. **Recipe Validation Unit Tests (`tests/test_recipes.py`)**:
   - Assert all 33 YAML recipes load without error.
   - Assert all recipes have an explicit `app_type` matching `AppType`.
   - Assert required fields (`bundle_id`, `app_name`, `strategy`) are non-empty.
2. **Full Test Suite Regression**:
   - Run `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/`.
