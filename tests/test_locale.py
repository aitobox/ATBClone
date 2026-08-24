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
    assert "de" in SUPPORTED_LANGUAGES
    assert "fr" in SUPPORTED_LANGUAGES
    assert "es" in SUPPORTED_LANGUAGES
    assert "ru" in SUPPORTED_LANGUAGES


def test_resolve_language_de():
    config = resolve_language_config("de")
    assert config.apple_locale == "de_DE"
    assert "de-DE" in config.apple_languages
    assert config.posix_lang == "de_DE.UTF-8"
    assert config.chromium_lang == "de"


def test_resolve_language_fr():
    config = resolve_language_config("fr")
    assert config.apple_locale == "fr_FR"
    assert "fr-FR" in config.apple_languages
    assert config.posix_lang == "fr_FR.UTF-8"
    assert config.chromium_lang == "fr"


def test_resolve_language_es():
    config = resolve_language_config("es")
    assert config.apple_locale == "es_ES"
    assert "es-ES" in config.apple_languages
    assert config.posix_lang == "es_ES.UTF-8"
    assert config.chromium_lang == "es"


def test_resolve_language_ru():
    config = resolve_language_config("ru")
    assert config.apple_locale == "ru_RU"
    assert "ru-RU" in config.apple_languages
    assert config.posix_lang == "ru_RU.UTF-8"
    assert config.chromium_lang == "ru"


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


def test_build_language_wrapper_snippet_default_cocoa():
    env_snippet, args = build_language_wrapper_snippet("zh-Hans")
    assert "export LANG=\"zh_CN.UTF-8\"" in env_snippet
    assert "export LC_ALL=\"zh_CN.UTF-8\"" in env_snippet
    assert "GlobalPreferences.plist" in env_snippet
    assert "-AppleLanguages" in args
    assert "-AppleLocale" in args
    assert "zh_CN" in args
    assert "--lang=" not in " ".join(args)


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


def test_build_language_wrapper_snippet_system_none():
    env_snippet, args = build_language_wrapper_snippet(None, app_type="cocoa")
    assert "export LANG=" in env_snippet
    assert "-AppleLanguages" in args
