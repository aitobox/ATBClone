# App Clone Language & Locale Management Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement comprehensive language and locale management for cloned applications in ATBClone, ensuring apps automatically inherit the host system language by default and can be manually configured per clone across GUI, CLI, and Recipes.

**Architecture:** A centralized `locale.py` module defines supported presets and resolves system preferences into multi-layer injection configurations: Cocoa launch arguments (`-AppleLanguages`, `-AppleLocale`), Chromium flags (`--lang`), POSIX environment variables (`LANG`, `LC_ALL`), and isolated `$HOME` preference synchronization (`.GlobalPreferences.plist`, `.CFUserTextEncoding`). `Recipe`, `CloneTask`, `CloneRecord`, `CloneEngine`, CLI, and GUI windows are updated to support language selection.

**Tech Stack:** Python 3.12, PySide6 / Toga GUI, Click CLI, Pydantic, Pytest, macOS defaults/AppKit/Cocoa environment.

## Global Constraints
- Target macOS native patterns, PySide6 / Toga, Python 3.12+
- Dev env command: `conda activate ATBClone` / `conda run -n ATBClone`
- Test command: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/`
- Preserve backward compatibility for existing state files and recipes missing the `language` field.

---

### Task 1: Core Locale Resolver (`src/atbclone/core/locale.py`) & Unit Tests

**Files:**
- Create: `src/atbclone/core/locale.py`
- Create: `tests/test_locale.py`

**Interfaces:**
- Consumes: Standard Python `os`, `subprocess`, `pathlib`, `shlex`
- Produces:
  - `SUPPORTED_LANGUAGES: dict[str, dict[str, Any]]`
  - `get_system_apple_languages() -> list[str]`
  - `get_system_apple_locale() -> str`
  - `resolve_language_config(language: str) -> LanguageConfig`
  - `build_language_wrapper_snippet(language: str, data_dir_has_home: bool = True) -> tuple[str, list[str]]`

- [ ] **Step 1: Write the failing tests in `tests/test_locale.py`**

```python
"""Tests for locale and language resolver."""

import pytest
from unittest.mock import patch
from atbclone.core.locale import (
    SUPPORTED_LANGUAGES,
    LanguageConfig,
    resolve_language_config,
    build_language_wrapper_snippet,
)


def test_supported_languages_contains_presets():
    assert "system" in SUPPORTED_LANGUAGES
    assert "zh-Hans" in SUPPORTED_LANGUAGES
    assert "zh-Hant" in SUPPORTED_LANGUAGES
    assert "en" in SUPPORTED_LANGUAGES
    assert "ja" in SUPPORTED_LANGUAGES
    assert "ko" in SUPPORTED_LANGUAGES


def test_resolve_language_zh_hans():
    config = resolve_language_config("zh-Hans")
    assert isinstance(config, LanguageConfig)
    assert config.lang_id == "zh-Hans"
    assert config.apple_locale == "zh_CN"
    assert "zh-Hans" in config.apple_languages
    assert config.posix_lang == "zh_CN.UTF-8"
    assert config.chromium_lang == "zh-CN"


def test_resolve_language_en():
    config = resolve_language_config("en")
    assert config.apple_locale == "en_US"
    assert "en-US" in config.apple_languages
    assert config.posix_lang == "en_US.UTF-8"
    assert config.chromium_lang == "en-US"


def test_resolve_language_fallback_to_system_for_unknown():
    config = resolve_language_config("unknown_lang")
    assert config.lang_id == "system"


def test_build_language_wrapper_snippet():
    env_snippet, args = build_language_wrapper_snippet("zh-Hans")
    assert "export LANG=\"zh_CN.UTF-8\"" in env_snippet
    assert "export LC_ALL=\"zh_CN.UTF-8\"" in env_snippet
    assert "-AppleLanguages" in args
    assert "-AppleLocale" in args
    assert "zh_CN" in args
    assert "--lang=zh-CN" in args
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_locale.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'atbclone.core.locale'`

- [ ] **Step 3: Implement `src/atbclone/core/locale.py`**

```python
"""Locale and Language environment resolver for ATBClone."""

from dataclasses import dataclass, field
from pathlib import Path
import re
import shlex
import subprocess
from typing import Any

from atbclone.core.logger import get_logger

logger = get_logger("core.locale")

SUPPORTED_LANGUAGES: dict[str, dict[str, Any]] = {
    "system": {
        "label_key": "lang_system",
        "default_locale": "zh_CN",
        "default_languages": ["zh-Hans-CN", "zh-Hans", "en"],
        "posix_lang": "zh_CN.UTF-8",
        "chromium_lang": "zh-CN",
    },
    "zh-Hans": {
        "label_key": "lang_zh_hans",
        "apple_locale": "zh_CN",
        "apple_languages": ["zh-Hans-CN", "zh-Hans", "en"],
        "posix_lang": "zh_CN.UTF-8",
        "chromium_lang": "zh-CN",
    },
    "zh-Hant": {
        "label_key": "lang_zh_hant",
        "apple_locale": "zh_TW",
        "apple_languages": ["zh-Hant-TW", "zh-Hant", "en"],
        "posix_lang": "zh_TW.UTF-8",
        "chromium_lang": "zh-TW",
    },
    "en": {
        "label_key": "lang_en",
        "apple_locale": "en_US",
        "apple_languages": ["en-US", "en"],
        "posix_lang": "en_US.UTF-8",
        "chromium_lang": "en-US",
    },
    "ja": {
        "label_key": "lang_ja",
        "apple_locale": "ja_JP",
        "apple_languages": ["ja-JP", "ja", "en"],
        "posix_lang": "ja_JP.UTF-8",
        "chromium_lang": "ja-JP",
    },
    "ko": {
        "label_key": "lang_ko",
        "apple_locale": "ko_KR",
        "apple_languages": ["ko-KR", "ko", "en"],
        "posix_lang": "ko_KR.UTF-8",
        "chromium_lang": "ko-KR",
    },
}


@dataclass
class LanguageConfig:
    lang_id: str
    apple_languages: list[str] = field(default_factory=list)
    apple_locale: str = "zh_CN"
    posix_lang: str = "zh_CN.UTF-8"
    chromium_lang: str = "zh-CN"


def get_system_apple_languages() -> list[str]:
    """Retrieve host system AppleLanguages from macOS defaults."""
    try:
        res = subprocess.run(
            ["defaults", "read", "-g", "AppleLanguages"],
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        )
        if res.returncode == 0 and res.stdout.strip():
            # Parse output like '(\n    "zh-Hans-CN",\n    "en-US"\n)'
            matches = re.findall(r'"([^"]+)"', res.stdout)
            if matches:
                return matches
    except Exception as e:
        logger.debug(f"Failed to read AppleLanguages from defaults: {e}")
    return ["zh-Hans-CN", "zh-Hans", "en"]


def get_system_apple_locale() -> str:
    """Retrieve host system AppleLocale from macOS defaults."""
    try:
        res = subprocess.run(
            ["defaults", "read", "-g", "AppleLocale"],
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        )
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip()
    except Exception as e:
        logger.debug(f"Failed to read AppleLocale from defaults: {e}")
    return "zh_CN"


def resolve_language_config(language: str | None) -> LanguageConfig:
    """Resolve a language identifier into concrete LanguageConfig."""
    lang_key = language if language in SUPPORTED_LANGUAGES else "system"

    if lang_key == "system":
        sys_langs = get_system_apple_languages()
        sys_loc = get_system_apple_locale()
        primary_lang = sys_langs[0] if sys_langs else "zh-Hans"
        
        # Determine chromium lang and posix lang based on primary_lang
        if "zh" in primary_lang.lower():
            posix = "zh_CN.UTF-8" if "hant" not in primary_lang.lower() and "tw" not in primary_lang.lower() else "zh_TW.UTF-8"
            chrom = "zh-CN" if "hant" not in primary_lang.lower() and "tw" not in primary_lang.lower() else "zh-TW"
        elif "ja" in primary_lang.lower():
            posix = "ja_JP.UTF-8"
            chrom = "ja-JP"
        elif "ko" in primary_lang.lower():
            posix = "ko_KR.UTF-8"
            chrom = "ko-KR"
        else:
            posix = f"{sys_loc}.UTF-8"
            chrom = primary_lang

        return LanguageConfig(
            lang_id="system",
            apple_languages=sys_langs,
            apple_locale=sys_loc,
            posix_lang=posix,
            chromium_lang=chrom,
        )

    preset = SUPPORTED_LANGUAGES[lang_key]
    return LanguageConfig(
        lang_id=lang_key,
        apple_languages=preset["apple_languages"],
        apple_locale=preset["apple_locale"],
        posix_lang=preset["posix_lang"],
        chromium_lang=preset["chromium_lang"],
    )


def build_language_wrapper_snippet(language: str | None) -> tuple[str, list[str]]:
    """Build shell export commands and launch arguments for wrapper script."""
    cfg = resolve_language_config(language)

    env_lines = [
        f'export LANG="{cfg.posix_lang}"',
        f'export LC_ALL="{cfg.posix_lang}"',
    ]

    # Preference directory sync block for isolated HOME
    pref_sync_block = (
        'REAL_HOME="${REAL_USER_HOME:-$HOME}"\n'
        'if [ -n "$HOME" ] && [ "$HOME" != "$REAL_HOME" ]; then\n'
        '    mkdir -p "$HOME/Library/Preferences"\n'
        '    if [ ! -f "$HOME/Library/Preferences/.GlobalPreferences.plist" ] && [ -f "$REAL_HOME/Library/Preferences/.GlobalPreferences.plist" ]; then\n'
        '        cp "$REAL_HOME/Library/Preferences/.GlobalPreferences.plist" "$HOME/Library/Preferences/.GlobalPreferences.plist" 2>/dev/null || true\n'
        '    fi\n'
        '    if [ ! -f "$HOME/.CFUserTextEncoding" ] && [ -f "$REAL_HOME/.CFUserTextEncoding" ]; then\n'
        '        cp "$REAL_HOME/.CFUserTextEncoding" "$HOME/.CFUserTextEncoding" 2>/dev/null || true\n'
        '    fi\n'
        'fi'
    )

    env_snippet = "\n".join(env_lines) + "\n" + pref_sync_block

    # Format Cocoa -AppleLanguages array argument: '("zh-Hans-CN", "zh-Hans", "en")'
    quoted_langs = ", ".join(f'"{l}"' for l in cfg.apple_languages)
    apple_langs_arg = f"({quoted_langs})"

    launch_args = [
        "-AppleLanguages",
        apple_langs_arg,
        "-AppleLocale",
        cfg.apple_locale,
        f"--lang={cfg.chromium_lang}",
    ]

    return env_snippet, launch_args
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_locale.py -v`
Expected: PASS

---

### Task 2: Update Data Models (`Recipe`, `CloneTask`, `CloneRecord`) & Backward Compatibility

**Files:**
- Modify: `src/atbclone/recipes/models.py`
- Modify: `src/atbclone/core/clone_task.py`
- Modify: `src/atbclone/core/state.py`
- Modify: `tests/test_state.py`

**Interfaces:**
- Consumes: `LanguageConfig`, `SUPPORTED_LANGUAGES` from `locale.py`
- Produces: `Recipe.language`, `CloneTask.language`, `CloneRecord.language` with default value `"system"`

- [ ] **Step 1: Write the failing tests in `tests/test_state.py`**

Test that `CloneRecord` defaults `language="system"`, and loading an older YAML without `language` sets `language="system"`.

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_state.py -v`

- [ ] **Step 3: Update `Recipe`, `CloneTask`, and `CloneRecord`**

1. In `src/atbclone/recipes/models.py`:
   Add `language: str = "system"` to `Recipe`.
2. In `src/atbclone/core/clone_task.py`:
   Add `language: str = "system"` to `CloneTask`.
3. In `src/atbclone/core/state.py`:
   Add `language: str = "system"` to `CloneRecord`.
   In `StateManager.load()`, ensure missing `language` default is populated.

- [ ] **Step 4: Run tests to verify they pass**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_state.py -v`
Expected: PASS

---

### Task 3: Engines Wrapper Script Generation (`src/atbclone/core/engines.py`)

**Files:**
- Modify: `src/atbclone/core/engines.py`
- Modify: `tests/test_engines.py`

**Interfaces:**
- Consumes: `build_language_wrapper_snippet` from `atbclone.core.locale`
- Produces: Wrapper scripts in `SoftCloneEngine` and `HardCloneEngine` containing language environment exports, isolated home sync, and language launch arguments.

- [ ] **Step 1: Update `tests/test_engines.py` with language assertions**

Verify generated wrapper scripts include `LANG`, `LC_ALL`, `-AppleLanguages`, `-AppleLocale`, `--lang`, and isolated HOME sync.

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_engines.py -v`

- [ ] **Step 3: Update `CloneEngine`, `SoftCloneEngine`, and `HardCloneEngine` in `src/atbclone/core/engines.py`**

Implement `_build_language_snippet(task: CloneTask)` in `CloneEngine` and embed the language environment & arguments into the wrapper body.

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/test_engines.py -v`
Expected: PASS

---

### Task 4: Internationalization (i18n) Translations (`src/atbclone/core/i18n.py`)

**Files:**
- Modify: `src/atbclone/core/i18n.py`
- Modify: `tests/test_i18n.py`

**Interfaces:**
- Produces:
  - `lang_system`, `lang_zh_hans`, `lang_zh_hant`, `lang_en`, `lang_ja`, `lang_ko`
  - `wizard_label_language`, `edit_label_language`, `card_label_language`

- [ ] **Step 1: Add unit tests for new i18n keys**
- [ ] **Step 2: Update dictionaries in `src/atbclone/core/i18n.py`**
- [ ] **Step 3: Run pytest to verify passes**

---

### Task 5: CLI Support (`src/atbclone/cli/cmd_clone.py`)

**Files:**
- Modify: `src/atbclone/cli/cmd_clone.py`
- Modify: `tests/test_cli.py`

**Interfaces:**
- Produces: `--language` / `-l` CLI option with choices `["system", "zh-Hans", "zh-Hant", "en", "ja", "ko"]`

- [ ] **Step 1: Add test for CLI `--language` option in `tests/test_cli.py`**
- [ ] **Step 2: Add `@click.option("--language", "-l", ...)` to `cmd_clone.py` and pass to `CloneTask` / `CloneRecord`**
- [ ] **Step 3: Run `pytest tests/test_cli.py` to verify passes**

---

### Task 6: GUI Integration (Wizard, Clone Edit, Clone Detail, Clone Service)

**Files:**
- Modify: `src/atbclone/gui/windows/wizard.py`
- Modify: `src/atbclone/gui/windows/clone_edit.py`
- Modify: `src/atbclone/gui/windows/clone_detail.py`
- Modify: `src/atbclone/gui/components/clone_card.py`
- Modify: `src/atbclone/gui/services/clone_service.py`

**Interfaces:**
- Produces:
  - Language selection dropdown in Wizard Step 3
  - Language selection dropdown in Clone Edit dialog
  - Language badge in Clone Card and Detail views
  - Preserving and updating language in `CloneService.create_clone` and `CloneService.update_clone`

- [ ] **Step 1: Add language selector to Wizard Step 3 (`wizard.py`)**
- [ ] **Step 2: Add language selector to Clone Edit dialog (`clone_edit.py`)**
- [ ] **Step 3: Update `CloneService` to pass `language` to `CloneTask` and `CloneRecord`**
- [ ] **Step 4: Update Clone Card & Detail to display current language setting**

---

### Task 7: Full Test Suite Verification

- [ ] **Step 1: Run full pytest suite**
Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/`
Expected: All tests pass (0 failures).

- [ ] **Step 2: Manual end-to-end check of wrapper script generation**
Verify generated wrapper contains valid bash syntax and proper quote escaping.
