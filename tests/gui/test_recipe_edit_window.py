import pytest
from unittest.mock import AsyncMock, patch

from atbclone.core.i18n import t, set_language
from atbclone.recipes.models import Recipe, ProxyConfig
from atbclone.gui.windows.recipe_edit import (
    RecipeEditWindow,
    format_env_injection,
    parse_env_injection,
    format_list_lines,
    parse_list_lines,
)


def test_recipe_advanced_i18n_keys():
    set_language("zh_CN")
    assert "高级参数" in t("win_recipe_btn_advanced_expand")
    assert "收起" in t("win_recipe_btn_advanced_collapse")
    assert "环境变量" in t("win_recipe_env_injection")
    assert "启动参数" in t("win_recipe_launch_args")
    assert "软链接白名单" in t("win_recipe_symlink_whitelist")
    assert "应用类型" in t("win_recipe_app_type")

    set_language("en_US")
    assert "Advanced" in t("win_recipe_btn_advanced_expand")
    assert "Collapse" in t("win_recipe_btn_advanced_collapse")
    assert "Environment" in t("win_recipe_env_injection")
    assert "Launch" in t("win_recipe_launch_args")
    assert "Whitelist" in t("win_recipe_symlink_whitelist")
    assert "App" in t("win_recipe_app_type")


def test_env_injection_formatting_and_parsing():
    env = {
        "HOME": "{{ATB_DATA_DIR}}/Home",
        "TMPDIR": "{{ATB_DATA_DIR}}/Tmp",
        "FOO": "bar=baz",
    }
    formatted = format_env_injection(env)
    parsed, err = parse_env_injection(formatted)
    assert err is None
    assert parsed == env

    # Test with comments and whitespace
    text_with_noise = """
    # This is a comment
    HOME = {{ATB_DATA_DIR}}/Home

    TMPDIR={{ATB_DATA_DIR}}/Tmp
    # Another comment
    """
    parsed_noise, err_noise = parse_env_injection(text_with_noise)
    assert err_noise is None
    assert parsed_noise == {
        "HOME": "{{ATB_DATA_DIR}}/Home",
        "TMPDIR": "{{ATB_DATA_DIR}}/Tmp",
    }


def test_env_injection_syntax_errors():
    set_language("en_US")
    invalid_text = "HOME={{ATB_DATA_DIR}}\nINVALID_LINE_NO_EQUALS"
    parsed, err = parse_env_injection(invalid_text)
    assert err is not None
    assert "line 2" in err.lower()

    set_language("zh_CN")
    parsed_zh, err_zh = parse_env_injection(invalid_text)
    assert err_zh is not None
    assert "第 2 行" in err_zh

    empty_key_text = "=some_value"
    parsed, err = parse_env_injection(empty_key_text)
    assert err is not None


def test_list_formatting_and_parsing():
    items = ["--user-data-dir={{ATB_DATA_DIR}}", "--disable-gpu", "--flag=1"]
    formatted = format_list_lines(items)
    parsed = parse_list_lines(formatted)
    assert parsed == items

    text_with_blanks = "\n  --arg1  \n\n# comment\n  --arg2\n"
    assert parse_list_lines(text_with_blanks) == ["--arg1", "--arg2"]


def test_recipe_edit_window_form_roundtrip():
    original_recipe = Recipe(
        bundle_id="com.example.testapp",
        app_name="Test App",
        strategy="soft_clone",
        strip_sandbox=True,
        proxy=ProxyConfig(enabled=True, type="socks5", host="10.0.0.1", port=1080),
        environment_injection={"HOME": "{{ATB_DATA_DIR}}/Home", "MY_VAR": "val123"},
        launch_args=["--flag1", "--user-data-dir={{ATB_DATA_DIR}}"],
        symlink_whitelist=["Library/Application Support/TestApp"],
        language="zh-Hans",
        app_type="electron",
    )

    win = RecipeEditWindow(title="Edit", recipe=original_recipe)
    # Check populated basic form values
    assert win.input_bundle_id.value == "com.example.testapp"
    assert win.input_app_name.value == "Test App"
    assert win.select_strategy.value == "soft_clone"
    assert win.switch_strip_sandbox.value is True
    assert win.switch_proxy.value is True

    # Test toggling advanced section
    assert win.advanced_expanded is False
    win.on_toggle_advanced(win.btn_toggle_advanced)
    assert win.advanced_expanded is True
    assert win.advanced_box in win.form_box.children
    win.on_toggle_advanced(win.btn_toggle_advanced)
    assert win.advanced_expanded is False
    assert win.advanced_box not in win.form_box.children

    # Check extracted recipe values
    recipe_out = win.get_recipe_from_form()
    assert recipe_out.bundle_id == "com.example.testapp"
    assert recipe_out.environment_injection == original_recipe.environment_injection
    assert recipe_out.launch_args == original_recipe.launch_args
    assert recipe_out.symlink_whitelist == original_recipe.symlink_whitelist
    assert recipe_out.language == "zh-Hans"
    assert recipe_out.app_type == "electron"


def test_recipe_edit_window_invalid_env_raises():
    set_language("zh_CN")
    win = RecipeEditWindow(title="New Recipe", recipe=None)
    win.input_bundle_id.value = "com.test.err"
    win.input_app_name.value = "ErrApp"
    win.input_env_injection.value = "INVALID_NO_EQUALS"

    with pytest.raises(ValueError) as excinfo:
        win.get_recipe_from_form()
    assert "第 1 行" in str(excinfo.value)
