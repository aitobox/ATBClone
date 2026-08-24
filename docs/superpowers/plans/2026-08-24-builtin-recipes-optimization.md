# Built-in Recipes Optimization & Standardization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Standardize and optimize all 33 built-in recipes in `src/atbclone/recipes/builtin/` by adding explicit `app_type` declarations, accurate `strip_sandbox` flags, and schema integrity tests.

**Architecture:** Update built-in YAML files to include explicit `app_type` (`chromium`, `electron`, `firefox`, `cocoa`, `generic`) and accurate `strip_sandbox` values. Enhance `tests/test_recipes.py` to enforce that every recipe in `builtin/` is well-formed with non-null `app_type`.

**Tech Stack:** Python 3.12, YAML, Pydantic, pytest.

## Global Constraints

- Python 3.12 in Conda env `ATBClone`
- No third-party dependencies added
- TDD: write recipe validation test first, then update recipes, verify passing, and commit

---

### Task 1: Add Built-in Recipe Schema Integrity Tests

**Files:**
- Modify: `tests/test_recipes.py`

- [ ] **Step 1: Write failing test in `tests/test_recipes.py`**

```python
def test_all_builtin_recipes_have_explicit_app_type():
    from atbclone.recipes.loader import RecipeLoader
    builtin_dir = RecipeLoader.BUILTIN_DIR
    yaml_files = list(builtin_dir.glob("*.yaml"))
    assert len(yaml_files) >= 30

    missing_app_type = []
    for yf in yaml_files:
        recipe = RecipeLoader._load_file(yf)
        if not recipe.app_type:
            missing_app_type.append(yf.name)

    assert not missing_app_type, f"Builtin recipes missing explicit app_type: {missing_app_type}"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_recipes.py -k test_all_builtin_recipes_have_explicit_app_type`
Expected: FAIL with list of recipes missing `app_type`.

---

### Task 2: Standardize and Update Built-in YAML Recipes

**Files:**
- Modify: all 33 YAML files in `src/atbclone/recipes/builtin/*.yaml`

- [ ] **Step 1: Update all 33 YAML files with explicit `app_type` and correct `strip_sandbox`**

Update:
1. `com.anthropic.claudefordesktop.yaml`: `app_type: electron`
2. `com.bilibili.bilibiliPC.yaml`: `app_type: electron`
3. `com.brave.Browser.yaml`: `app_type: chromium`
4. `com.bytedance.douyin.desktop.yaml`: `app_type: electron`
5. `com.electron.lark.yaml`: `app_type: electron`
6. `com.google.Chrome.yaml`: `app_type: chromium`
7. `com.google.GeminiMacOS.yaml`: `app_type: cocoa`
8. `com.google.android.studio.yaml`: `app_type: generic`
9. `com.google.antigravity-ide.yaml`: `app_type: electron`
10. `com.google.antigravity.yaml`: `app_type: electron`
11. `com.hnc.Discord.yaml`: `app_type: electron`
12. `com.kingsoft.wpsoffice.mac.yaml`: `app_type: cocoa`
13. `com.lemon.lvoverseas.yaml`: `app_type: chromium`
14. `com.lemon.lvpro.yaml`: `app_type: chromium`
15. `com.microsoft.VSCode.yaml`: `app_type: electron`
16. `com.microsoft.edgemac.yaml`: `app_type: chromium`
17. `com.netease.163music.yaml`: `app_type: chromium`
18. `com.openai.chat.yaml`: `app_type: cocoa`
19. `com.openai.codex.yaml`: `app_type: cocoa`
20. `com.skype.skype.yaml`: `app_type: electron`
21. `com.tencent.WeWorkMac.yaml`: `app_type: chromium`
22. `com.tencent.qq.yaml`: `app_type: electron`, `strip_sandbox: true`
23. `com.tencent.xinWeChat.yaml`: `app_type: cocoa`, `strip_sandbox: true`
24. `com.tinyspeck.slackmacgap.yaml`: `app_type: electron`
25. `com.todesktop.230313mzl4w4u92.yaml`: `app_type: electron`
26. `com.valvesoftware.steam.yaml`: `app_type: cocoa`
27. `company.thebrowser.Browser.yaml`: `app_type: chromium`
28. `dev.zed.Zed.yaml`: `app_type: generic`
29. `jp.naver.line.mac.yaml`: `app_type: cocoa`
30. `org.mozilla.firefox.yaml`: `app_type: firefox`
31. `org.telegram.desktop.yaml`: `app_type: generic`
32. `org.torproject.torbrowser.yaml`: `app_type: firefox`
33. `ru.keepcoder.Telegram.yaml`: `app_type: cocoa`

- [ ] **Step 2: Run test to verify it passes**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_recipes.py`
Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add src/atbclone/recipes/builtin/ tests/test_recipes.py
git commit -m "feat(recipes): standardize app_type and strip_sandbox across all builtin recipes"
```

---

### Task 3: Full Test Suite Regression

- [ ] **Step 1: Run full pytest test suite**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/`
Expected: 100% tests passing

- [ ] **Step 2: Commit any remaining changes and document in walkthrough**
