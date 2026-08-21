"""Tests for locale and language resolver."""

import pytest
from unittest.mock import patch
from atbclone.core.locale import (
    SUPPORTED_LANGUAGES,
    LanguageConfig,
    resolve_language_config,
    build_language_wrapper_snippet,
    get_system_apple_languages,
    get_system_apple_locale,
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
    assert "zh-Hans" in config.apple_languages or "zh-Hans-CN" in config.apple_languages
    assert config.posix_lang == "zh_CN.UTF-8"
    assert config.chromium_lang == "zh-CN"


def test_resolve_language_en():
    config = resolve_language_config("en")
    assert config.apple_locale == "en_US"
    assert "en-US" in config.apple_languages
    assert config.posix_lang == "en_US.UTF-8"
    assert config.chromium_lang == "en-US"


def test_resolve_language_ja():
    config = resolve_language_config("ja")
    assert config.apple_locale == "ja_JP"
    assert "ja-JP" in config.apple_languages
    assert config.posix_lang == "ja_JP.UTF-8"
    assert config.chromium_lang == "ja-JP"


def test_resolve_language_ko():
    config = resolve_language_config("ko")
    assert config.apple_locale == "ko_KR"
    assert "ko-KR" in config.apple_languages
    assert config.posix_lang == "ko_KR.UTF-8"
    assert config.chromium_lang == "ko-KR"


def test_resolve_language_fallback_to_system_for_unknown():
    config = resolve_language_config("unknown_lang")
    assert config.lang_id == "system"


def test_resolve_language_system_mock():
    with patch("atbclone.core.locale.get_system_apple_languages", return_value=["zh-Hans-CN", "en"]), \
         patch("atbclone.core.locale.get_system_apple_locale", return_value="zh_CN"):
        config = resolve_language_config("system")
        assert config.lang_id == "system"
        assert config.apple_locale == "zh_CN"
        assert "zh-Hans-CN" in config.apple_languages
        assert config.posix_lang == "zh_CN.UTF-8"
        assert config.chromium_lang == "zh-CN"


def test_resolve_language_zh_hant():
    config = resolve_language_config("zh-Hant")
    assert config.apple_locale == "zh_TW"
    assert "zh-Hant-TW" in config.apple_languages
    assert config.posix_lang == "zh_TW.UTF-8"
    assert config.chromium_lang == "zh-TW"


def test_build_language_wrapper_snippet():
    env_snippet, args = build_language_wrapper_snippet("zh-Hans")
    assert "export LANG=\"zh_CN.UTF-8\"" in env_snippet
    assert "export LC_ALL=\"zh_CN.UTF-8\"" in env_snippet
    assert "GlobalPreferences.plist" in env_snippet
    assert "-AppleLanguages" in args
    assert "-AppleLocale" in args
    assert "zh_CN" in args
    assert "--lang=zh-CN" in args


def test_build_language_wrapper_snippet_system_none():
    env_snippet, args = build_language_wrapper_snippet(None)
    assert "export LANG=" in env_snippet
    assert "-AppleLanguages" in args
