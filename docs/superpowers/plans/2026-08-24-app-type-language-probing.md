# App Type Probing and Adaptive Language Argument Injection Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement application framework probing and adaptive language/locale argument injection so that Chromium/Electron, Cocoa, Firefox, and Generic applications only receive valid, framework-compatible command-line arguments and environment variables upon clone launch.

**Architecture:** Add `app_type` support (`cocoa`, `chromium`, `electron`, `firefox`, `generic`) to `Recipe` and `AppProber`. Update `locale.build_language_wrapper_snippet` to selectively output CLI arguments based on `app_type` (Chromium/Electron get only `--lang`, Cocoa gets `-AppleLanguages`/`-AppleLocale`, Firefox and Generic get zero CLI language args). Wire `CloneEngine` to resolve `app_type` dynamically from `Recipe` or `AppProber`. Update built-in recipes and test suites.

**Tech Stack:** Python 3.12, PySide6, Pydantic, Pytest

## Global Constraints

- Target macOS native patterns, PySide6, Python 3.12+ with `conda run -n ATBClone` for Python env
- Test command: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/`
- Branch: `main`
- Zero third-party runtime dependencies beyond project stack

---

### Task 1: Add `app_type` to `Recipe` Model

**Files:**
- Modify: `src/atbclone/recipes/models.py:1-35`
- Test: `tests/test_recipe_loader.py` or new test in `tests/test_app_prober.py`

**Interfaces:**
- Produces: `AppType = Literal["cocoa", "chromium", "electron", "firefox", "generic"]`, `Recipe.app_type: AppType | None = None`

- [ ] **Step 1: Write the failing test**

Add to `tests/test_app_prober.py`:
```python
from atbclone.recipes.models import Recipe

def test_recipe_app_type_field():
    r = Recipe(bundle_id="com.example.test", app_name="Test", strategy="hard_clone", app_type="chromium")
    assert r.app_type == "chromium"

    r_default = Recipe(bundle_id="com.example.test2", app_name="Test2", strategy="hard_clone")
    assert r_default.app_type is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_app_prober.py -k test_recipe_app_type_field`
Expected: FAIL (or pass if field already existed, but here `app_type` is not on `Recipe`)

- [ ] **Step 3: Write minimal implementation**

In `src/atbclone/recipes/models.py`:
```python
from typing import Literal
from pydantic import BaseModel, Field

AppType = Literal["cocoa", "chromium", "electron", "firefox", "generic"]

class Recipe(BaseModel):
    bundle_id: str
    app_name: str
    strategy: Literal["hard_clone", "soft_clone"]
    strip_sandbox: bool = False
    proxy: ProxyConfig = Field(default_factory=ProxyConfig)
    environment_injection: dict[str, str] = Field(default_factory=dict)
    symlink_whitelist: list[str] = Field(default_factory=list)
    launch_args: list[str] = Field(default_factory=list)
    language: str = "system"
    app_type: AppType | None = None
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_app_prober.py -k test_recipe_app_type_field`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/atbclone/recipes/models.py tests/test_app_prober.py
git commit -m "feat(recipe): add app_type field to Recipe model"
```

---

### Task 2: Implement Framework Probing in `AppProber`

**Files:**
- Modify: `src/atbclone/core/app_prober.py:1-140`
- Test: `tests/test_app_prober.py`

**Interfaces:**
- Produces: `AppProber.detect_app_type(path: Path | str, bundle_id: str = "", frameworks: list[str] | None = None) -> AppType`, `ProbeResult.app_type: AppType`

- [ ] **Step 1: Write the failing test**

In `tests/test_app_prober.py`:
```python
def test_detect_app_type_chromium(tmp_path: Path):
    assert AppProber.detect_app_type(tmp_path, bundle_id="com.google.Chrome") == "chromium"
    assert AppProber.detect_app_type(tmp_path, bundle_id="com.microsoft.edgemac") == "chromium"
    assert AppProber.detect_app_type(tmp_path, frameworks=["Chromium Framework.framework"]) == "chromium"

def test_detect_app_type_electron(tmp_path: Path):
    assert AppProber.detect_app_type(tmp_path, bundle_id="com.microsoft.VSCode") == "electron"
    assert AppProber.detect_app_type(tmp_path, frameworks=["Electron Framework.framework"]) == "electron"

def test_detect_app_type_firefox(tmp_path: Path):
    assert AppProber.detect_app_type(tmp_path, bundle_id="org.mozilla.firefox") == "firefox"
    assert AppProber.detect_app_type(tmp_path, frameworks=["XUL.framework"]) == "firefox"

def test_detect_app_type_cocoa(tmp_path: Path):
    assert AppProber.detect_app_type(tmp_path, bundle_id="com.tencent.xinWeChat") == "cocoa"
    assert AppProber.detect_app_type(tmp_path, bundle_id="ru.keepcoder.Telegram") == "cocoa"

def test_app_prober_analyze_sets_recipe_app_type(tmp_path: Path):
    app_dir = tmp_path / "Google Chrome.app"
    app_dir.mkdir()
    mock_info = AppInfo(
        path=app_dir,
        bundle_id="com.google.Chrome",
        app_name="Google Chrome",
        executable=app_dir / "Contents" / "MacOS" / "Google Chrome",
        has_sandbox=False,
    )
    with patch.object(AppProber, "inspect_entitlements", return_value={}), \
         patch.object(AppProber, "detect_frameworks", return_value=[]):
        res = AppProber.analyze(app_dir, app_info=mock_info)
        assert res.recipe.app_type == "chromium"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_app_prober.py -k "test_detect_app_type or test_app_prober_analyze_sets_recipe_app_type"`
Expected: FAIL with `AttributeError: type object 'AppProber' has no attribute 'detect_app_type'`

- [ ] **Step 3: Write minimal implementation**

In `src/atbclone/core/app_prober.py`:
```python
from atbclone.recipes.models import AppType, Recipe

# Implement detect_app_type
@classmethod
def detect_app_type(
    cls,
    app_path: Path | str,
    bundle_id: str = "",
    frameworks: list[str] | None = None,
) -> AppType:
    if frameworks is None:
        frameworks = cls.detect_frameworks(app_path)
    bid_lower = bundle_id.lower()
    fw_lower = [f.lower() for f in frameworks]

    # 1. Electron detection
    if any("electron" in f for f in fw_lower) or any(k in bid_lower for k in ["electron", "vscode", "code", "slack", "discord", "lark"]):
        return "electron"

    # 2. Chromium detection
    if any("chromium" in f or "google chrome" in f for f in fw_lower) or any(k in bid_lower for k in ["chrome", "chromium", "microsoft.edge", "arc", "brave"]):
        return "chromium"

    # 3. Firefox / Gecko detection
    if any("xul" in f for f in fw_lower) or "firefox" in bid_lower or "torbrowser" in bid_lower:
        return "firefox"

    # 4. Standard Cocoa vs Generic
    path = Path(app_path).expanduser().resolve()
    if (path / "Contents" / "MacOS").is_dir() or (path / "Contents" / "Info.plist").is_file():
        return "cocoa"

    return "generic"
```
Update `AppProber.analyze()` to set `app_type` on `Recipe` using `detect_app_type`.

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_app_prober.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/atbclone/core/app_prober.py tests/test_app_prober.py
git commit -m "feat(prober): implement detect_app_type and populate recipe.app_type"
```

---

### Task 3: Update `locale.build_language_wrapper_snippet` with Adaptive Args

**Files:**
- Modify: `src/atbclone/core/locale.py:150-190`
- Test: `tests/test_locale.py`

**Interfaces:**
- Produces: `build_language_wrapper_snippet(language: str | None, app_type: str = "cocoa") -> tuple[str, list[str]]`

- [ ] **Step 1: Write the failing test**

In `tests/test_locale.py`:
```python
def test_build_language_wrapper_snippet_chromium():
    env_snippet, args = build_language_wrapper_snippet("zh-Hans", app_type="chromium")
    assert "export LANG=\"zh_CN.UTF-8\"" in env_snippet
    assert "--lang=zh-CN" in args
    assert "-AppleLanguages" not in args
    assert "-AppleLocale" not in args

def test_build_language_wrapper_snippet_electron():
    env_snippet, args = build_language_wrapper_snippet("en", app_type="electron")
    assert "export LANG=\"en_US.UTF-8\"" in env_snippet
    assert "--lang=en-US" in args
    assert "-AppleLanguages" not in args
    assert "-AppleLocale" not in args

def test_build_language_wrapper_snippet_cocoa():
    env_snippet, args = build_language_wrapper_snippet("zh-Hans", app_type="cocoa")
    assert "-AppleLanguages" in args
    assert "-AppleLocale" in args
    assert "--lang=" not in " ".join(args)

def test_build_language_wrapper_snippet_firefox():
    env_snippet, args = build_language_wrapper_snippet("zh-Hans", app_type="firefox")
    assert "export LANG=\"zh_CN.UTF-8\"" in env_snippet
    assert args == []

def test_build_language_wrapper_snippet_generic():
    env_snippet, args = build_language_wrapper_snippet("zh-Hans", app_type="generic")
    assert "export LANG=\"zh_CN.UTF-8\"" in env_snippet
    assert args == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_locale.py -k "test_build_language_wrapper_snippet_chromium or test_build_language_wrapper_snippet_firefox"`
Expected: FAIL (`-AppleLanguages` is unexpectedly present)

- [ ] **Step 3: Write minimal implementation**

In `src/atbclone/core/locale.py`:
```python
def build_language_wrapper_snippet(language: str | None, app_type: str = "cocoa") -> tuple[str, list[str]]:
    """Build shell export commands and launch arguments for wrapper script based on app_type."""
    cfg = resolve_language_config(language)

    env_lines = [
        f'export LANG="{cfg.posix_lang}"',
        f'export LC_ALL="{cfg.posix_lang}"',
    ]

    pref_sync_block = (
        'REAL_USER_HOME="${REAL_USER_HOME:-$HOME}"\n'
        'if [ -n "$HOME" ] && [ "$HOME" != "$REAL_USER_HOME" ]; then\n'
        '    mkdir -p "$HOME/Library/Preferences"\n'
        '    if [ ! -f "$HOME/Library/Preferences/.GlobalPreferences.plist" ] && [ -f "$REAL_USER_HOME/Library/Preferences/.GlobalPreferences.plist" ]; then\n'
        '        cp "$REAL_USER_HOME/Library/Preferences/.GlobalPreferences.plist" "$HOME/Library/Preferences/.GlobalPreferences.plist" 2>/dev/null || true\n'
        '    fi\n'
        '    if [ ! -f "$HOME/.CFUserTextEncoding" ] && [ -f "$REAL_USER_HOME/.CFUserTextEncoding" ]; then\n'
        '        cp "$REAL_USER_HOME/.CFUserTextEncoding" "$HOME/.CFUserTextEncoding" 2>/dev/null || true\n'
        '    fi\n'
        'fi'
    )

    env_snippet = "\n".join(env_lines) + "\n" + pref_sync_block

    normalized_type = (app_type or "cocoa").lower()
    if normalized_type in ("chromium", "electron"):
        launch_args = [f"--lang={cfg.chromium_lang}"]
    elif normalized_type == "cocoa":
        quoted_langs = ", ".join(f'"{l}"' for l in cfg.apple_languages)
        apple_langs_arg = f"({quoted_langs})"
        launch_args = [
            "-AppleLanguages",
            apple_langs_arg,
            "-AppleLocale",
            cfg.apple_locale,
        ]
    else:  # firefox, generic, etc.
        launch_args = []

    return env_snippet, launch_args
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_locale.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/atbclone/core/locale.py tests/test_locale.py
git commit -m "feat(locale): adapt launch args by app_type in build_language_wrapper_snippet"
```

---

### Task 4: Connect App Type Resolution in `CloneEngine` & Update Engine Tests

**Files:**
- Modify: `src/atbclone/core/engines.py:15-25`
- Modify: `tests/test_engines.py`

**Interfaces:**
- Consumes: `AppProber.detect_app_type`, `build_language_wrapper_snippet(lang, app_type)`

- [ ] **Step 1: Write the failing test**

Update/add in `tests/test_engines.py`:
Verify that for `com.google.Chrome` (or recipe with `app_type="chromium"`), `SoftCloneEngine` and `HardCloneEngine` generate wrapper scripts containing `--lang=` and NOT containing `-AppleLanguages`.

```python
def test_soft_clone_chrome_does_not_inject_apple_languages(mock_app_info_with_spaces, base_recipe):
    base_recipe.app_type = "chromium"
    base_recipe.bundle_id = "com.google.Chrome"
    task = CloneTask(
        source=mock_app_info_with_spaces,
        dest_path=Path("/Applications/Google Chrome 2.app"),
        data_dir=Path("/Users/test/Library/Application Support/Google Chrome 2"),
        recipe=base_recipe,
        clone_name="Google Chrome 2",
        new_bundle_id="com.google.Chrome.clone2",
    )
    with patch("atbclone.executor.runner.Runner.run") as mock_run:
        SoftCloneEngine.execute(task, needs_admin=False)
        script, _ = mock_run.call_args[0]
        assert "--lang=" in script
        assert "-AppleLanguages" not in script
        assert "-AppleLocale" not in script
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_engines.py -k test_soft_clone_chrome_does_not_inject_apple_languages`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

In `src/atbclone/core/engines.py`:
```python
    @staticmethod
    def _build_language_env_and_args(task: CloneTask) -> tuple[str, list[str]]:
        """Generate shell exports and launch arguments for language/locale configuration."""
        lang = getattr(task, "language", None) or getattr(task.recipe, "language", "system")
        app_type = getattr(task.recipe, "app_type", None)
        if not app_type and hasattr(task, "source") and task.source and task.source.path:
            from atbclone.core.app_prober import AppProber
            app_type = AppProber.detect_app_type(
                task.source.path,
                bundle_id=task.source.bundle_id,
            )
        return build_language_wrapper_snippet(lang, app_type=app_type or "cocoa")
```
And update existing `test_engines.py` assertions where generic sample apps default to `cocoa` or `chromium` as appropriate.

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_engines.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/atbclone/core/engines.py tests/test_engines.py
git commit -m "feat(engines): resolve app_type in CloneEngine for language argument generation"
```

---

### Task 5: Update Built-in Recipes with `app_type` Declarations

**Files:**
- Modify: `src/atbclone/recipes/builtin/*.yaml`
- Test: `tests/test_recipe_loader.py`

- [ ] **Step 1: Write the failing test**

In `tests/test_recipe_loader.py`:
```python
def test_builtin_recipes_have_valid_app_types():
    from atbclone.recipes.loader import RecipeLoader
    chrome_recipe = RecipeLoader.get("com.google.Chrome")
    assert chrome_recipe is not None
    assert chrome_recipe.app_type == "chromium"

    vscode_recipe = RecipeLoader.get("com.microsoft.VSCode")
    assert vscode_recipe is not None
    assert vscode_recipe.app_type == "electron"

    firefox_recipe = RecipeLoader.get("org.mozilla.firefox")
    assert firefox_recipe is not None
    assert firefox_recipe.app_type == "firefox"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_recipe_loader.py -k test_builtin_recipes_have_valid_app_types`
Expected: FAIL

- [ ] **Step 3: Update built-in YAML recipes**

Add `app_type` to relevant YAML files in `src/atbclone/recipes/builtin/`:
- `com.google.Chrome.yaml`, `com.brave.Browser.yaml`, `com.microsoft.edgemac.yaml`, `company.thebrowser.Browser.yaml` -> `app_type: chromium`
- `com.microsoft.VSCode.yaml`, `com.tinyspeck.slackmacgap.yaml`, `com.electron.lark.yaml`, `com.hnc.Discord.yaml` -> `app_type: electron`
- `org.mozilla.firefox.yaml`, `org.torproject.torbrowser.yaml` -> `app_type: firefox`
- `com.tencent.xinWeChat.yaml`, `com.tencent.qq.yaml`, `ru.keepcoder.Telegram.yaml` -> `app_type: cocoa`

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_recipe_loader.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/atbclone/recipes/builtin/ tests/test_recipe_loader.py
git commit -m "feat(recipes): declare explicit app_type in builtin recipes"
```

---

### Task 6: Full Regression Verification

**Files:**
- Test: Full test suite

- [ ] **Step 1: Run complete test suite**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/`
Expected: All tests pass.

- [ ] **Step 2: Commit any final test adjustments**

```bash
git commit --allow-empty -m "test: full regression tests pass for app type language probing"
```
