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
        "apple_locale": "zh_CN",
        "apple_languages": ["zh-Hans-CN", "zh-Hans", "en"],
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

        if "zh" in primary_lang.lower():
            if "hant" in primary_lang.lower() or "tw" in primary_lang.lower() or "hk" in primary_lang.lower():
                posix = "zh_TW.UTF-8"
                chrom = "zh-TW"
            else:
                posix = "zh_CN.UTF-8"
                chrom = "zh-CN"
        elif "ja" in primary_lang.lower():
            posix = "ja_JP.UTF-8"
            chrom = "ja-JP"
        elif "ko" in primary_lang.lower():
            posix = "ko_KR.UTF-8"
            chrom = "ko-KR"
        elif "en" in primary_lang.lower():
            posix = "en_US.UTF-8"
            chrom = "en-US"
        else:
            posix = f"{sys_loc}.UTF-8" if sys_loc else "zh_CN.UTF-8"
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
        apple_languages=list(preset["apple_languages"]),
        apple_locale=str(preset["apple_locale"]),
        posix_lang=str(preset["posix_lang"]),
        chromium_lang=str(preset["chromium_lang"]),
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
