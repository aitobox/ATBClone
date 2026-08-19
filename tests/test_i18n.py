"""Unit tests for atbclone.core.i18n module and language switching across all 9 supported languages."""

import os
from unittest.mock import patch
from click.testing import CliRunner
import pytest

from atbclone.cli.main import cli
from atbclone.core.i18n import (
    SUPPORTED_LANGUAGES,
    detect_system_language,
    get_language,
    is_chinese,
    normalize_lang_code,
    set_language,
    t,
)
from atbclone.core.models import AppInfo
from atbclone.recipes.models import Recipe


@pytest.fixture
def mock_app_info(tmp_path) -> AppInfo:
    app_dir = tmp_path / "WeChat.app"
    app_dir.mkdir(parents=True, exist_ok=True)
    return AppInfo(
        path=app_dir,
        bundle_id="com.tencent.xinWeChat",
        app_name="WeChat",
        executable=app_dir / "Contents" / "MacOS" / "WeChat",
        has_sandbox=True,
    )


@pytest.fixture
def mock_hard_recipe() -> Recipe:
    return Recipe(
        bundle_id="com.tencent.xinWeChat",
        app_name="WeChat",
        strategy="hard_clone",
        environment_injection={"HOME": "{{ATB_DATA_DIR}}/Home"},
    )



@pytest.fixture(autouse=True)
def reset_i18n_lang():
    """Ensure clean language state before and after each test."""
    set_language(None)
    yield
    set_language(None)


def test_normalize_lang_code():
    assert normalize_lang_code("zh-Hans-CN") == "zh"
    assert normalize_lang_code("zh_CN") == "zh"
    assert normalize_lang_code("zh-Hant-TW") == "zh_TW"
    assert normalize_lang_code("zh_TW") == "zh_TW"
    assert normalize_lang_code("zh_HK") == "zh_TW"
    assert normalize_lang_code("ja-JP") == "ja"
    assert normalize_lang_code("ja") == "ja"
    assert normalize_lang_code("ko-KR") == "ko"
    assert normalize_lang_code("ko") == "ko"
    assert normalize_lang_code("de-DE") == "de"
    assert normalize_lang_code("de") == "de"
    assert normalize_lang_code("fr-FR") == "fr"
    assert normalize_lang_code("fr") == "fr"
    assert normalize_lang_code("ru-RU") == "ru"
    assert normalize_lang_code("ru") == "ru"
    assert normalize_lang_code("es-ES") == "es"
    assert normalize_lang_code("es") == "es"
    assert normalize_lang_code("en-US") == "en"
    assert normalize_lang_code("unknown_lang") == "en"


def test_i18n_override_env():
    for lang in ("zh", "zh_TW", "ja", "ko", "de", "fr", "ru", "es", "en"):
        with patch.dict(os.environ, {"ATBCLONE_LANG": lang}):
            assert detect_system_language() == lang


def test_i18n_macos_apple_languages():
    cases = [
        ('(\n    "zh-Hans-CN",\n    "en-US"\n)', "zh"),
        ('(\n    "zh-Hant-TW",\n    "en-US"\n)', "zh_TW"),
        ('(\n    "ja-JP",\n    "en-US"\n)', "ja"),
        ('(\n    "ko-KR",\n    "en-US"\n)', "ko"),
        ('(\n    "de-DE",\n    "en-US"\n)', "de"),
        ('(\n    "fr-FR",\n    "en-US"\n)', "fr"),
        ('(\n    "ru-RU",\n    "en-US"\n)', "ru"),
        ('(\n    "es-ES",\n    "en-US"\n)', "es"),
        ('(\n    "en-US",\n    "zh-Hans-CN"\n)', "en"),
    ]
    for apple_langs, expected in cases:
        with patch.dict(os.environ, {"ATBCLONE_LANG": ""}), \
             patch("subprocess.check_output") as mock_sub:
            mock_sub.return_value = apple_langs
            assert detect_system_language() == expected


def test_i18n_macos_apple_locale():
    cases = [
        ("zh_CN", "zh"),
        ("zh_TW", "zh_TW"),
        ("ja_JP", "ja"),
        ("ko_KR", "ko"),
        ("de_DE", "de"),
        ("fr_FR", "fr"),
        ("ru_RU", "ru"),
        ("es_ES", "es"),
        ("en_US", "en"),
    ]
    for locale, expected in cases:
        with patch.dict(os.environ, {"ATBCLONE_LANG": ""}), \
             patch("subprocess.check_output", side_effect=[Exception("no AppleLanguages"), locale]):
            assert detect_system_language() == expected


def test_i18n_env_lang_fallback():
    cases = [
        ("zh_CN.UTF-8", "zh"),
        ("zh_TW.UTF-8", "zh_TW"),
        ("ja_JP.UTF-8", "ja"),
        ("ko_KR.UTF-8", "ko"),
        ("de_DE.UTF-8", "de"),
        ("fr_FR.UTF-8", "fr"),
        ("ru_RU.UTF-8", "ru"),
        ("es_ES.UTF-8", "es"),
        ("en_US.UTF-8", "en"),
    ]
    for env_val, expected in cases:
        with patch.dict(os.environ, {"LANG": env_val, "ATBCLONE_LANG": ""}), \
             patch("subprocess.check_output", side_effect=Exception("no defaults")):
            assert detect_system_language() == expected


def test_i18n_translation_lookup_all_languages():
    expected_clone_names = {
        "en": "Clone name",
        "zh": "分身名称",
        "zh_TW": "分身名稱",
        "ja": "クローン名",
        "ko": "클론 이름",
        "de": "Klon-Name",
        "fr": "Nom du clone",
        "ru": "Имя клона",
        "es": "Nombre del clon",
    }
    for lang, expected in expected_clone_names.items():
        set_language(lang)
        assert t("wizard_prompt_clone_name") == expected

    set_language("zh")
    assert is_chinese() is True
    set_language("zh_TW")
    assert is_chinese() is True
    set_language("ja")
    assert is_chinese() is False


def test_wizard_all_languages(tmp_path, mock_app_info: AppInfo, mock_hard_recipe: Recipe):
    test_cases = [
        ("en", "ATBClone Wizard", "Clone name"),
        ("zh", "ATBClone 小向导", "分身名称"),
        ("zh_TW", "ATBClone 小精靈", "分身名稱"),
        ("ja", "ATBClone ウィザード", "クローン名"),
        ("ko", "ATBClone 마법사", "클론 이름"),
        ("de", "ATBClone Assistent", "Klon-Name"),
        ("fr", "Assistant ATBClone", "Nom du clone"),
        ("ru", "Мастер ATBClone", "Имя клона"),
        ("es", "Asistente ATBClone", "Nombre del clon"),
    ]

    for lang, expected_title, expected_prompt in test_cases:
        runner = CliRunner(env={"ATBCLONE_LANG": lang})
        inputs = f"{mock_app_info.path}\n\n\n\n\n\n\n\n"

        with patch("atbclone.cli.cmd_wizard.AppInspector.inspect", return_value=mock_app_info), \
             patch("atbclone.cli.cmd_wizard.RecipeLoader.match", return_value=mock_hard_recipe), \
             patch("atbclone.cli.cmd_wizard.AppInspector.next_available_name", return_value=("WeChat2", 2)), \
             patch("atbclone.cli.cmd_wizard.HardCloneEngine.execute"), \
             patch("atbclone.cli.cmd_wizard.StateManager.add"):

            result = runner.invoke(cli, ["wizard"], input=inputs)
            assert result.exit_code == 0
            assert expected_title in result.output
            assert expected_prompt in result.output


def test_new_data_dir_i18n_keys():
    for lang in ("en", "zh", "zh_TW", "ja", "ko", "de", "fr", "ru", "es"):
        set_language(lang)
        msg = t("clone_err_data_dir_not_supported", app_name="Zed")
        assert "Zed" in msg
        assert t("wizard_prompt_data_dir") != ""
        assert "/tmp/test" in t("wizard_confirm_data_dir", data_dir="/tmp/test")
        assert "/tmp/test" in t("remove_prompt_delete_data", data_dir="/tmp/test")

