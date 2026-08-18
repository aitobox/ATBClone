from pathlib import Path
import pytest
from pydantic import ValidationError

from atbclone.recipes import ProxyConfig, Recipe, RecipeLoader


def test_proxy_config_defaults():
    proxy = ProxyConfig()
    assert not proxy.enabled
    assert proxy.type == "http"
    assert proxy.host == "127.0.0.1"
    assert proxy.port == 1080
    assert proxy.username == ""
    assert proxy.password == ""
    assert proxy.no_proxy == "localhost,127.0.0.1,*.local"
    assert proxy.url == "http://127.0.0.1:1080"


def test_proxy_config_with_auth():
    proxy = ProxyConfig(
        enabled=True,
        type="socks5",
        host="proxy.corp.com",
        port=8080,
        username="user1",
        password="secret",
    )
    assert proxy.url == "socks5://user1:secret@proxy.corp.com:8080"


def test_proxy_config_username_only():
    proxy = ProxyConfig(
        enabled=True,
        type="http",
        host="10.0.0.1",
        port=3128,
        username="anonymous",
        password="",
    )
    assert proxy.url == "http://anonymous:@10.0.0.1:3128"


def test_recipe_defaults():
    recipe = Recipe(
        bundle_id="com.example.app",
        app_name="ExampleApp",
        strategy="hard_clone",
    )
    assert recipe.bundle_id == "com.example.app"
    assert recipe.app_name == "ExampleApp"
    assert recipe.strategy == "hard_clone"
    assert not recipe.strip_sandbox
    assert recipe.proxy.enabled is False
    assert recipe.environment_injection == {}
    assert recipe.symlink_whitelist == []
    assert recipe.launch_args == []


def test_chromium_guard():
    # Chrome bundle ID should be forced to soft_clone even if hard_clone requested
    for bid in [
        "com.google.Chrome",
        "org.chromium.Chromium",
        "com.microsoft.edgemac",
        "company.thebrowser.Arc",
        "COM.GOOGLE.CHROME.CANARY",
        "org.chromium.test",
        "com.microsoft.Edge",
        "company.thebrowser.arc.dev",
    ]:
        recipe = Recipe(
            bundle_id=bid,
            app_name="Browser",
            strategy="hard_clone",
        )
        assert recipe.strategy == "soft_clone", f"Failed for {bid}"

    # Non-chromium should keep hard_clone
    recipe = Recipe(
        bundle_id="com.tencent.xinWeChat",
        app_name="WeChat",
        strategy="hard_clone",
    )
    assert recipe.strategy == "hard_clone"


def test_recipe_invalid_strategy():
    with pytest.raises(ValidationError):
        Recipe(
            bundle_id="com.example.app",
            app_name="ExampleApp",
            strategy="invalid_strategy",  # type: ignore
        )


def test_load_builtin_wechat():
    recipe = RecipeLoader.match("com.tencent.xinWeChat")
    assert recipe is not None
    assert recipe.bundle_id == "com.tencent.xinWeChat"
    assert recipe.app_name == "微信"
    assert recipe.strategy == "hard_clone"
    assert not recipe.strip_sandbox
    assert "HOME" in recipe.environment_injection
    assert "TMPDIR" in recipe.environment_injection
    assert "Library/Keychains" in recipe.symlink_whitelist
    assert ".ssh" in recipe.symlink_whitelist


def test_load_builtin_chrome():
    recipe = RecipeLoader.match("com.google.Chrome")
    assert recipe is not None
    assert recipe.bundle_id == "com.google.Chrome"
    assert recipe.strategy == "soft_clone"
    assert any("--user-data-dir" in arg for arg in recipe.launch_args)


def test_load_fallback_unknown():
    recipe = RecipeLoader.match("com.unknown.app")
    assert recipe is not None
    assert recipe.bundle_id == "com.unknown.app"
    assert recipe.app_name == "Unknown"
    assert recipe.strategy == "hard_clone"


def test_local_recipe_priority(tmp_path, monkeypatch):
    local_dir = tmp_path / "recipes"
    local_dir.mkdir(parents=True)
    custom_yaml = local_dir / "com.tencent.xinWeChat.yaml"
    custom_yaml.write_text(
        """
bundle_id: com.tencent.xinWeChat
app_name: 微信-自定义
strategy: hard_clone
strip_sandbox: true
""",
        encoding="utf-8",
    )

    monkeypatch.setattr(RecipeLoader, "LOCAL_DIR", local_dir)
    recipe = RecipeLoader.match("com.tencent.xinWeChat")
    assert recipe.app_name == "微信-自定义"
    assert recipe.strip_sandbox is True


def test_recipe_loader_get_local_dir_default():
    assert RecipeLoader.LOCAL_DIR is None
    expected = Path.home() / ".AIToBox" / "recipes"
    assert RecipeLoader.get_local_dir() == expected


def test_recipe_loader_load_file_direct(tmp_path):
    custom_file = tmp_path / "custom.yaml"
    custom_file.write_text(
        """
bundle_id: com.custom.tool
app_name: CustomTool
strategy: soft_clone
strip_sandbox: false
launch_args:
  - "--debug"
""",
        encoding="utf-8",
    )
    recipe = RecipeLoader._load_file(custom_file)
    assert recipe.bundle_id == "com.custom.tool"
    assert recipe.app_name == "CustomTool"
    assert recipe.strategy == "soft_clone"
    assert recipe.launch_args == ["--debug"]
