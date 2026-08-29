"""Unit tests for CloneEngines (SoftCloneEngine and HardCloneEngine) and CloneTask."""

from pathlib import Path
from unittest.mock import patch

import pytest

from atbclone.core.clone_task import CloneTask
from atbclone.core.engines import CloneEngine, HardCloneEngine, SoftCloneEngine
from atbclone.core.models import AppInfo
from atbclone.executor.runner import CloneError
from atbclone.recipes.models import ProxyConfig, Recipe


@pytest.fixture
def mock_app_info():
    return AppInfo(
        path=Path("/Applications/TestApp.app"),
        bundle_id="com.example.testapp",
        app_name="TestApp",
        executable=Path("/Applications/TestApp.app/Contents/MacOS/TestApp"),
        has_sandbox=True,
    )


@pytest.fixture
def mock_app_info_with_spaces():
    return AppInfo(
        path=Path("/Applications/Google Chrome.app"),
        bundle_id="com.google.Chrome",
        app_name="Google Chrome",
        executable=Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
        has_sandbox=True,
    )


@pytest.fixture
def base_recipe():
    return Recipe(
        bundle_id="com.example.testapp",
        app_name="TestApp",
        strategy="soft_clone",
        strip_sandbox=False,
        proxy=ProxyConfig(enabled=False),
        environment_injection={},
        symlink_whitelist=[],
        launch_args=[],
    )


@pytest.fixture
def sample_task(mock_app_info, base_recipe):
    return CloneTask(
        source=mock_app_info,
        dest_path=Path("/Applications/TestApp2.app"),
        data_dir=Path("/Users/test/Library/Application Support/TestApp2"),
        recipe=base_recipe,
        clone_name="TestApp 2",
        new_bundle_id="com.example.testapp.clone2",
    )


class TestCloneTask:
    def test_clone_task_fields(self, mock_app_info, base_recipe):
        task = CloneTask(
            source=mock_app_info,
            dest_path=Path("/Applications/TestApp2.app"),
            data_dir=Path("/Users/test/data"),
            recipe=base_recipe,
            clone_name="TestApp2",
            new_bundle_id="com.example.testapp2",
        )
        assert task.source == mock_app_info
        assert task.dest_path == Path("/Applications/TestApp2.app")
        assert task.data_dir == Path("/Users/test/data")
        assert task.recipe == base_recipe
        assert task.clone_name == "TestApp2"
        assert task.new_bundle_id == "com.example.testapp2"


class TestCloneEngineProxyHelper:
    def test_proxy_env_disabled(self, sample_task):
        sample_task.recipe.proxy.enabled = False
        assert CloneEngine._build_proxy_env(sample_task) == ""

    def test_proxy_env_enabled_default(self, sample_task):
        sample_task.recipe.proxy = ProxyConfig(
            enabled=True,
            type="http",
            host="127.0.0.1",
            port=7890,
            no_proxy="localhost,127.0.0.1",
        )
        env = CloneEngine._build_proxy_env(sample_task)
        assert 'export HTTP_PROXY="http://127.0.0.1:7890"' in env
        assert 'export HTTPS_PROXY="http://127.0.0.1:7890"' in env
        assert 'export http_proxy="$HTTP_PROXY"' in env
        assert 'export https_proxy="$HTTPS_PROXY"' in env
        assert 'export NO_PROXY="localhost,127.0.0.1"' in env
        assert 'export no_proxy="$NO_PROXY"' in env

    def test_proxy_env_with_auth(self, sample_task):
        sample_task.recipe.proxy = ProxyConfig(
            enabled=True,
            type="socks5",
            host="proxy.corp.internal",
            port=1080,
            username="alice",
            password="secretpassword",
        )
        env = CloneEngine._build_proxy_env(sample_task)
        assert 'export HTTP_PROXY="socks5://alice:secretpassword@proxy.corp.internal:1080"' in env
        assert 'export HTTPS_PROXY="socks5://alice:secretpassword@proxy.corp.internal:1080"' in env


class TestSoftCloneEngine:
    def test_soft_clone_basic_script(self, sample_task):
        with patch("atbclone.executor.runner.Runner.run") as mock_run:
            SoftCloneEngine.execute(sample_task, needs_admin=False)
            mock_run.assert_called_once()
            script, needs_admin = mock_run.call_args[0]
            assert needs_admin is False
            assert "set -e" in script
            assert "mkdir -p /Applications/TestApp2.app/Contents/MacOS" in script
            assert "cp /Applications/TestApp.app/Contents/Info.plist /Applications/TestApp2.app/Contents/Info.plist" in script
            assert "chmod -R u+w /Applications/TestApp2.app 2>/dev/null || true" in script
            assert '/usr/libexec/PlistBuddy -c "Set :CFBundleIdentifier com.example.testapp.clone2" /Applications/TestApp2.app/Contents/Info.plist' in script
            assert '/usr/libexec/PlistBuddy -c "Set :CFBundleName TestApp 2" /Applications/TestApp2.app/Contents/Info.plist' in script
            assert "cat << 'WRAPPER_EOF' > /Applications/TestApp2.app/Contents/MacOS/TestApp" in script
            assert 'export LANG=' in script
            assert 'export LC_ALL=' in script
            assert 'exec /Applications/TestApp.app/Contents/MacOS/TestApp' in script
            assert '-AppleLanguages' in script
            assert '-AppleLocale' in script
            assert "chmod +x /Applications/TestApp2.app/Contents/MacOS/TestApp" in script

    def test_soft_clone_with_spaces_in_path(self, mock_app_info_with_spaces, base_recipe):
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
            mock_run.assert_called_once()
            script, _ = mock_run.call_args[0]
            assert "mkdir -p '/Applications/Google Chrome 2.app/Contents/MacOS'" in script
            assert "cp '/Applications/Google Chrome.app/Contents/Info.plist' '/Applications/Google Chrome 2.app/Contents/Info.plist'" in script
            assert "exec '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'" in script
            assert "--lang=" in script
            assert "-AppleLanguages" not in script
            assert "-AppleLocale" not in script

    def test_soft_clone_with_launch_args_and_proxy(self, sample_task):
        sample_task.recipe.app_type = "chromium"
        sample_task.recipe.launch_args = [
            "--user-data-dir={{ATB_DATA_DIR}}",
            "--no-first-run",
        ]
        sample_task.recipe.proxy = ProxyConfig(
            enabled=True,
            host="127.0.0.1",
            port=8080,
        )
        with patch("atbclone.executor.runner.Runner.run") as mock_run:
            SoftCloneEngine.execute(sample_task, needs_admin=True)
            mock_run.assert_called_once()
            script, needs_admin = mock_run.call_args[0]
            assert needs_admin is True
            assert 'export HTTP_PROXY="http://127.0.0.1:8080"' in script
            assert '--user-data-dir=/Users/test/Library/Application Support/TestApp2' in script
            assert "exec /Applications/TestApp.app/Contents/MacOS/TestApp '--user-data-dir=/Users/test/Library/Application Support/TestApp2' --no-first-run" in script

    def test_soft_clone_failure_cleans_up_and_reraises(self, sample_task):
        with patch("atbclone.executor.runner.Runner.run", side_effect=[CloneError("Permission denied"), None]) as mock_run:
            with pytest.raises(CloneError) as exc_info:
                SoftCloneEngine.execute(sample_task, needs_admin=False)
            assert "Permission denied" in str(exc_info.value)
            assert mock_run.call_count == 2
            cleanup_call = mock_run.call_args_list[1]
            assert "rm -rf /Applications/TestApp2.app" in cleanup_call[0][0]


class TestHardCloneEngine:
    def test_hard_clone_basic_no_strip_sandbox(self, sample_task):
        with patch("atbclone.executor.runner.Runner.run") as mock_run:
            HardCloneEngine.execute(sample_task, needs_admin=False)
            mock_run.assert_called_once()
            script, needs_admin = mock_run.call_args[0]
            assert needs_admin is False
            assert "set -e" in script
            assert "cp -R /Applications/TestApp.app /Applications/TestApp2.app" in script
            assert "chmod -R u+w /Applications/TestApp2.app 2>/dev/null || true" in script
            assert '/usr/libexec/PlistBuddy -c "Set :CFBundleIdentifier com.example.testapp.clone2" /Applications/TestApp2.app/Contents/Info.plist' in script
            assert '/usr/libexec/PlistBuddy -c "Set :CFBundleName TestApp 2" /Applications/TestApp2.app/Contents/Info.plist' in script
            assert "mv /Applications/TestApp2.app/Contents/MacOS/TestApp /Applications/TestApp2.app/Contents/MacOS/TestApp.bin" in script
            assert "cat << 'WRAPPER_EOF' > /Applications/TestApp2.app/Contents/MacOS/TestApp" in script
            assert 'export LANG=' in script
            assert 'export LC_ALL=' in script
            assert 'exec "$(dirname "$0")/TestApp.bin"' in script
            assert "-AppleLanguages" in script
            assert "-AppleLocale" in script
            assert "chmod +x /Applications/TestApp2.app/Contents/MacOS/TestApp" in script
            assert "xattr -cr /Applications/TestApp2.app 2>/dev/null || true" in script
            assert "codesign --force --deep --sign - /Applications/TestApp2.app" in script
            assert "codesign -vv --deep --strict /Applications/TestApp2.app" in script

    def test_hard_clone_with_spaces_in_path(self, mock_app_info_with_spaces, base_recipe):
        task = CloneTask(
            source=mock_app_info_with_spaces,
            dest_path=Path("/Applications/Google Chrome 2.app"),
            data_dir=Path("/Users/test/Library/Application Support/Google Chrome 2"),
            recipe=base_recipe,
            clone_name="Google Chrome 2",
            new_bundle_id="com.google.Chrome.clone2",
        )
        with patch("atbclone.executor.runner.Runner.run") as mock_run:
            HardCloneEngine.execute(task, needs_admin=False)
            mock_run.assert_called_once()
            script, _ = mock_run.call_args[0]
            assert "cp -R '/Applications/Google Chrome.app' '/Applications/Google Chrome 2.app'" in script
            assert "mv '/Applications/Google Chrome 2.app/Contents/MacOS/Google Chrome' '/Applications/Google Chrome 2.app/Contents/MacOS/Google Chrome.bin'" in script
            assert 'exec "$(dirname "$0")/Google Chrome.bin"' in script
            assert "--lang=" in script
            assert "-AppleLanguages" not in script
            assert "-AppleLocale" not in script


    def test_hard_clone_with_strip_sandbox(self, sample_task):
        sample_task.recipe.strip_sandbox = True
        with patch("atbclone.executor.runner.Runner.run") as mock_run:
            HardCloneEngine.execute(sample_task, needs_admin=False)
            mock_run.assert_called_once()
            script, _ = mock_run.call_args[0]
            assert 'ent_plist=$(mktemp /tmp/atb_ent_XXXXXX.plist)' in script
            assert 'codesign -d --entitlements - --xml /Applications/TestApp.app > "$ent_plist" 2>/dev/null || true' in script
            assert 'if [ -s "$ent_plist" ]; then' in script
            assert '/usr/libexec/PlistBuddy -c "Delete :com.apple.security.app-sandbox" "$ent_plist" 2>/dev/null || true' in script
            assert 'codesign --force --deep --sign - --entitlements "$ent_plist" /Applications/TestApp2.app' in script
            assert "codesign --force --deep --sign - /Applications/TestApp2.app" in script
            assert "codesign -vv --deep --strict /Applications/TestApp2.app" in script

    def test_hard_clone_with_env_injection_and_proxy(self, sample_task):
        sample_task.recipe.environment_injection = {
            "APP_DATA_DIR": "{{ATB_DATA_DIR}}",
            "CUSTOM_FLAG": "1",
            "UNSAFE_VAL": 'foo"; rm -rf /; echo "$bar`whoami`',
        }
        sample_task.recipe.proxy = ProxyConfig(
            enabled=True,
            host="127.0.0.1",
            port=1080,
        )
        with patch("atbclone.executor.runner.Runner.run") as mock_run:
            HardCloneEngine.execute(sample_task, needs_admin=True)
            mock_run.assert_called_once()
            script, needs_admin = mock_run.call_args[0]
            assert needs_admin is True
            assert "export APP_DATA_DIR='/Users/test/Library/Application Support/TestApp2'" in script
            assert "export CUSTOM_FLAG=1" in script
            assert "export UNSAFE_VAL='foo\"; rm -rf /; echo \"$bar`whoami`'" in script
            assert 'export HTTP_PROXY="http://127.0.0.1:1080"' in script
            assert 'export LANG=' in script

    def test_hard_clone_with_launch_args(self, sample_task):
        sample_task.recipe.app_type = "chromium"
        sample_task.recipe.launch_args = ["--user-data-dir={{ATB_DATA_DIR}}", "--no-first-run"]
        with patch("atbclone.executor.runner.Runner.run") as mock_run:
            HardCloneEngine.execute(sample_task, needs_admin=False)
            mock_run.assert_called_once()
            script, _ = mock_run.call_args[0]
            assert 'exec "$(dirname "$0")/TestApp.bin" \'--user-data-dir=/Users/test/Library/Application Support/TestApp2\' --no-first-run' in script
            assert "--lang=" in script

    def test_hard_clone_failure_cleans_up_and_reraises(self, sample_task):

        with patch("atbclone.executor.runner.Runner.run", side_effect=[CloneError("Disk full"), None]) as mock_run:
            with pytest.raises(CloneError) as exc_info:
                HardCloneEngine.execute(sample_task, needs_admin=False)
            assert "Disk full" in str(exc_info.value)
            assert mock_run.call_count == 2
            cleanup_call = mock_run.call_args_list[1]
            assert "rm -rf /Applications/TestApp2.app" in cleanup_call[0][0]


class TestBuildIconCmd:
    """Unit tests for CloneEngine._build_icon_cmd helper."""

    def test_returns_empty_when_no_icon_path(self, sample_task):
        sample_task.icon_path = None
        result = CloneEngine._build_icon_cmd(sample_task, "/dst/Resources", "/dst/Info.plist")
        assert result == ""

    def test_returns_shell_snippet_when_icon_path_set(self, sample_task):
        sample_task.icon_path = Path("/custom/MyIcon.icns")
        result = CloneEngine._build_icon_cmd(sample_task, "/dst/Resources", "/dst/Info.plist")
        assert "PlistBuddy" in result
        assert "CFBundleIconFile" in result
        assert "/custom/MyIcon.icns" in result
        assert "/dst/Resources" in result

    def test_icon_path_with_spaces_is_quoted(self, sample_task):
        sample_task.icon_path = Path("/path with spaces/My Icon.icns")
        result = CloneEngine._build_icon_cmd(sample_task, "/dst/Resources", "/dst/Info.plist")
        assert "'/path with spaces/My Icon.icns'" in result


class TestSoftCloneEngineCustomisation:
    """Tests for display_name and icon_path in SoftCloneEngine."""

    def test_default_display_name_uses_clone_name(self, sample_task):
        """When display_name is None, CFBundleDisplayName should be set to clone_name."""
        sample_task.display_name = None
        with patch("atbclone.executor.runner.Runner.run") as mock_run:
            SoftCloneEngine.execute(sample_task, needs_admin=False)
            script, _ = mock_run.call_args[0]
            assert 'Set :CFBundleDisplayName TestApp 2' in script
            assert 'Set :CFBundleName TestApp 2' in script

    def test_custom_display_name_overrides_clone_name(self, sample_task):
        """When display_name is set, CFBundleDisplayName and CFBundleName should use it instead."""
        sample_task.display_name = "我的测试App"
        with patch("atbclone.executor.runner.Runner.run") as mock_run:
            SoftCloneEngine.execute(sample_task, needs_admin=False)
            script, _ = mock_run.call_args[0]
            assert "Set :CFBundleDisplayName 我的测试App" in script
            assert "Set :CFBundleName 我的测试App" in script
            # clone_name should NOT appear in the DisplayName or Name lines
            assert "Set :CFBundleDisplayName TestApp 2" not in script
            assert "Set :CFBundleName TestApp 2" not in script

    def test_custom_icon_injects_copy_command(self, sample_task):
        """When icon_path is set, shell script should contain the icon copy snippet."""
        sample_task.icon_path = Path("/Users/test/custom.icns")
        with patch("atbclone.executor.runner.Runner.run") as mock_run:
            SoftCloneEngine.execute(sample_task, needs_admin=False)
            script, _ = mock_run.call_args[0]
            assert "CFBundleIconFile" in script
            assert "/Users/test/custom.icns" in script

    def test_no_icon_path_no_icon_snippet(self, sample_task):
        """When icon_path is None, no icon-copy snippet should appear."""
        sample_task.icon_path = None
        with patch("atbclone.executor.runner.Runner.run") as mock_run:
            SoftCloneEngine.execute(sample_task, needs_admin=False)
            script, _ = mock_run.call_args[0]
            assert "CFBundleIconFile" not in script

    def test_lshaslocalizedname_deleted_and_strings_cleaned(self, sample_task):
        """LSHasLocalizedDisplayName and localized InfoPlist.strings overrides must be cleaned."""
        with patch("atbclone.executor.runner.Runner.run") as mock_run:
            SoftCloneEngine.execute(sample_task, needs_admin=False)
            script, _ = mock_run.call_args[0]
            assert "Delete :LSHasLocalizedDisplayName" in script
            assert 'find /Applications/TestApp2.app/Contents/Resources -name "InfoPlist.strings"' in script
            assert "Delete :CFBundleDisplayName" in script
            assert "Delete :CFBundleName" in script
            assert "lsregister -f /Applications/TestApp2.app" in script


class TestHardCloneEngineCustomisation:
    """Tests for display_name and icon_path in HardCloneEngine."""

    def test_default_display_name_uses_clone_name(self, sample_task):
        sample_task.display_name = None
        with patch("atbclone.executor.runner.Runner.run") as mock_run:
            HardCloneEngine.execute(sample_task, needs_admin=False)
            script, _ = mock_run.call_args[0]
            assert "Set :CFBundleDisplayName TestApp 2" in script
            assert "Set :CFBundleName TestApp 2" in script

    def test_custom_display_name_overrides_clone_name(self, sample_task):
        sample_task.display_name = "硬克隆App"
        with patch("atbclone.executor.runner.Runner.run") as mock_run:
            HardCloneEngine.execute(sample_task, needs_admin=False)
            script, _ = mock_run.call_args[0]
            assert "Set :CFBundleDisplayName 硬克隆App" in script
            assert "Set :CFBundleName 硬克隆App" in script
            assert "Set :CFBundleDisplayName TestApp 2" not in script
            assert "Set :CFBundleName TestApp 2" not in script

    def test_custom_icon_injects_copy_command(self, sample_task):
        sample_task.icon_path = Path("/icons/hard_custom.icns")
        with patch("atbclone.executor.runner.Runner.run") as mock_run:
            HardCloneEngine.execute(sample_task, needs_admin=False)
            script, _ = mock_run.call_args[0]
            assert "CFBundleIconFile" in script
            assert "/icons/hard_custom.icns" in script

    def test_no_icon_path_no_icon_snippet(self, sample_task):
        sample_task.icon_path = None
        with patch("atbclone.executor.runner.Runner.run") as mock_run:
            HardCloneEngine.execute(sample_task, needs_admin=False)
            script, _ = mock_run.call_args[0]
            assert "CFBundleIconFile" not in script

    def test_lshaslocalizedname_deleted_and_strings_cleaned(self, sample_task):
        with patch("atbclone.executor.runner.Runner.run") as mock_run:
            HardCloneEngine.execute(sample_task, needs_admin=False)
            script, _ = mock_run.call_args[0]
            assert "Delete :LSHasLocalizedDisplayName" in script
            assert 'find /Applications/TestApp2.app/Contents/Resources -name "InfoPlist.strings"' in script
            assert "Delete :CFBundleDisplayName" in script
            assert "Delete :CFBundleName" in script
            assert "lsregister -f /Applications/TestApp2.app" in script


class TestIOSEngines:
    """Tests for iOS on Mac app support in Clone Engines."""

    @pytest.fixture
    def ios_app_info(self):
        return AppInfo(
            path=Path("/Applications/小宇宙.app"),
            bundle_id="app.podcast.cosmos",
            app_name="小宇宙",
            executable=Path("/Applications/小宇宙.app/Wrapper/Podcast.app/Podcast"),
            has_sandbox=True,
            is_ios_app=True,
            relative_plist_path=Path("Wrapper/Podcast.app/Info.plist"),
            relative_executable_path=Path("Wrapper/Podcast.app/Podcast"),
            relative_resources_path=Path("Wrapper/Podcast.app"),
        )

    @pytest.fixture
    def ios_task(self, ios_app_info):
        recipe = Recipe(
            bundle_id="app.podcast.cosmos",
            app_name="小宇宙",
            strategy="hard_clone",
            strip_sandbox=False,
        )
        return CloneTask(
            source=ios_app_info,
            dest_path=Path("/Users/test/Applications/小宇宙 Brain.app"),
            data_dir=Path("/Users/test/Data/小宇宙 Brain"),
            recipe=recipe,
            clone_name="小宇宙 Brain",
            new_bundle_id="app.podcast.cosmos.atbclone.1",
        )

    def test_hard_clone_ios_app_raises_clone_error(self, ios_task):
        with pytest.raises(CloneError) as exc_info:
            HardCloneEngine.execute(ios_task, needs_admin=False)
        assert "iOS on Mac Wrapper" in str(exc_info.value)

    def test_soft_clone_ios_app_raises_clone_error(self, ios_task):
        ios_task.recipe.strategy = "soft_clone"
        with pytest.raises(CloneError) as exc_info:
            SoftCloneEngine.execute(ios_task, needs_admin=False)
        assert "iOS on Mac Wrapper" in str(exc_info.value)


class TestAdaptiveLanguageArgs:
    """Verify that CloneEngine adaptively injects framework-appropriate language args."""

    def test_chrome_soft_clone_emits_lang_flag_without_apple_languages(self, mock_app_info_with_spaces, base_recipe):
        base_recipe.app_type = "chromium"
        task = CloneTask(
            source=mock_app_info_with_spaces,
            dest_path=Path("/Applications/Google Chrome 2.app"),
            data_dir=Path("/Users/test/Library/Application Support/Google Chrome 2"),
            recipe=base_recipe,
            clone_name="Google Chrome 2",
            new_bundle_id="com.google.Chrome.clone2",
            language="zh-Hans",
        )
        with patch("atbclone.executor.runner.Runner.run") as mock_run:
            SoftCloneEngine.execute(task, needs_admin=False)
            script, _ = mock_run.call_args[0]
            assert "--lang=zh-CN" in script
            assert "-AppleLanguages" not in script
            assert "-AppleLocale" not in script

    def test_chrome_hard_clone_emits_lang_flag_without_apple_languages(self, mock_app_info_with_spaces, base_recipe):
        base_recipe.app_type = "chromium"
        task = CloneTask(
            source=mock_app_info_with_spaces,
            dest_path=Path("/Applications/Google Chrome 2.app"),
            data_dir=Path("/Users/test/Library/Application Support/Google Chrome 2"),
            recipe=base_recipe,
            clone_name="Google Chrome 2",
            new_bundle_id="com.google.Chrome.clone2",
            language="en",
        )
        with patch("atbclone.executor.runner.Runner.run") as mock_run:
            HardCloneEngine.execute(task, needs_admin=False)
            script, _ = mock_run.call_args[0]
            assert "--lang=en-US" in script
            assert "-AppleLanguages" not in script
            assert "-AppleLocale" not in script

    def test_native_cocoa_emits_apple_languages(self, mock_app_info, base_recipe):
        base_recipe.app_type = "cocoa"
        task = CloneTask(
            source=mock_app_info,
            dest_path=Path("/Applications/TestApp2.app"),
            data_dir=Path("/Users/test/Library/Application Support/TestApp2"),
            recipe=base_recipe,
            clone_name="TestApp 2",
            new_bundle_id="com.example.testapp.clone2",
            language="zh-Hans",
        )
        with patch("atbclone.executor.runner.Runner.run") as mock_run:
            SoftCloneEngine.execute(task, needs_admin=False)
            script, _ = mock_run.call_args[0]
            assert "-AppleLanguages" in script
            assert "-AppleLocale" in script
            assert "--lang=" not in script

    def test_soft_clone_engine_prunes_unsupported_args(self, tmp_path, base_recipe):
        app_dir = tmp_path / "MyNative.app"
        (app_dir / "Contents" / "MacOS").mkdir(parents=True)
        exe = app_dir / "Contents" / "MacOS" / "MyNative"
        exe.write_bytes(b"MachO_HEADER\x00--supported-flag\x00")

        app_info = AppInfo(
            path=app_dir,
            bundle_id="com.example.mynative",
            app_name="MyNative",
            executable=exe,
            has_sandbox=False,
        )

        base_recipe.app_type = "cocoa"
        base_recipe.launch_args = [
            "--supported-flag=foo",
            "--unsupported-flag=bar",
            "--user-data-dir={{ATB_DATA_DIR}}",
        ]

        task = CloneTask(
            source=app_info,
            dest_path=tmp_path / "MyNative2.app",
            data_dir=tmp_path / "Data",
            recipe=base_recipe,
            clone_name="MyNative2",
            new_bundle_id="com.example.mynative.clone2",
        )

        with patch("atbclone.executor.runner.Runner.run") as mock_run:
            SoftCloneEngine.execute(task, needs_admin=False)
            script, _ = mock_run.call_args[0]
            assert "--supported-flag=foo" in script
            assert "--unsupported-flag=bar" not in script
            assert "--user-data-dir=" not in script

    def test_hard_clone_engine_prunes_unsupported_args_and_falls_back_to_env(self, tmp_path, base_recipe):
        app_dir = tmp_path / "MyNative.app"
        (app_dir / "Contents" / "MacOS").mkdir(parents=True)
        exe = app_dir / "Contents" / "MacOS" / "MyNative"
        exe.write_bytes(b"MachO_HEADER\x00CocoaApp\x00")

        app_info = AppInfo(
            path=app_dir,
            bundle_id="com.example.mynative",
            app_name="MyNative",
            executable=exe,
            has_sandbox=False,
        )

        base_recipe.app_type = "cocoa"
        base_recipe.strategy = "hard_clone"
        # Faulty recipe specified --user-data-dir for Cocoa app that doesn't support it
        base_recipe.launch_args = ["--user-data-dir={{ATB_DATA_DIR}}"]
        base_recipe.environment_injection = {}

        task = CloneTask(
            source=app_info,
            dest_path=tmp_path / "MyNative2.app",
            data_dir=tmp_path / "Data",
            recipe=base_recipe,
            clone_name="MyNative2",
            new_bundle_id="com.example.mynative.clone2",
        )

        with patch("atbclone.executor.runner.Runner.run") as mock_run:
            HardCloneEngine.execute(task, needs_admin=False)
            script, _ = mock_run.call_args[0]
            # Argument must be pruned
            assert "--user-data-dir=" not in script
            # Must fall back to HOME & TMPDIR
            assert f"{tmp_path}/Data/Home" in script
            assert f"{tmp_path}/Data/Tmp" in script

    def test_launch_args_deduplication_removes_duplicate_lang_flags(self, mock_app_info_with_spaces, base_recipe):
        base_recipe.app_type = "chromium"
        base_recipe.launch_args = [
            "--user-data-dir={{ATB_DATA_DIR}}",
            "--lang=en-US",
            "-AppleLanguages",
        ]
        task = CloneTask(
            source=mock_app_info_with_spaces,
            dest_path=Path("/Applications/Google Chrome 2.app"),
            data_dir=Path("/Users/test/Library/Application Support/Google Chrome 2"),
            recipe=base_recipe,
            clone_name="Google Chrome 2",
            new_bundle_id="com.google.Chrome.clone2",
            language="zh-Hans",
        )
        with patch("atbclone.executor.runner.Runner.run") as mock_run:
            SoftCloneEngine.execute(task, needs_admin=False)
            script, _ = mock_run.call_args[0]
            # Should have the new --lang=zh-CN, and not have duplicate --lang=en-US or -AppleLanguages
class TestProcessSingletonFrameworkPatching:
    """Tests for ProcessSingleton framework patching in HardCloneEngine."""

    def test_patch_framework_singletons_no_frameworks_dir(self, tmp_path):
        app_dir = tmp_path / "MyApp.app"
        app_dir.mkdir()
        assert not HardCloneEngine.patch_framework_singletons(app_dir)

    def test_patch_framework_singletons_success(self, tmp_path):
        import struct

        app_dir = tmp_path / "LarkClone.app"
        frameworks_dir = app_dir / "Contents" / "Frameworks" / "Lark Framework.framework"
        frameworks_dir.mkdir(parents=True)
        macho_file = frameworks_dir / "Lark Framework"

        target_str = b"Failed to create a ProcessSingleton for your profile directory.\x00"

        # Construct a synthetic Mach-O binary (> 1MB with arm64 magic)
        data = bytearray(b"\xcf\xfa\xed\xfe" + b"\x00" * (1_050_000))
        str_offset = 0x100000
        data[str_offset : str_offset + len(target_str)] = target_str

        page = str_offset & ~0xFFF
        page_offset = str_offset & 0xFFF

        pc = 0x50000
        pc_page = pc & ~0xFFF
        imm = (page - pc_page) >> 12
        immlo = imm & 3
        immhi = (imm >> 2) & 0x7FFFF
        adrp_w = 0x90000000 | (immlo << 29) | (immhi << 5)
        add_w = 0x91000000 | (page_offset << 10)

        # Write bl (0x94000010), cmp w0, #0 (0x7100001f), adrp, add
        struct.pack_into("<IIII", data, pc - 8, 0x94000010, 0x7100001F, adrp_w, add_w)

        macho_file.write_bytes(data)

        assert HardCloneEngine.patch_framework_singletons(app_dir) is True

        patched_data = macho_file.read_bytes()
        bl_patched, nop_patched = struct.unpack_from("<II", patched_data, pc - 8)
        assert bl_patched == 0x52800000  # mov w0, #0
        assert nop_patched == 0xD503201F  # nop

    def test_patch_framework_singletons_with_custom_register(self, tmp_path):
        import struct

        app_dir = tmp_path / "ChatGPT2.app"
        fw_dir = app_dir / "Contents" / "Frameworks" / "Codex Framework.framework"
        fw_dir.mkdir(parents=True)
        macho_file = fw_dir / "Codex Framework"

        data = bytearray(b"\x00" * 0x100000)
        data[0:4] = b"\xcf\xfa\xed\xfe"

        target_str = b"Failed to create a ProcessSingleton for your profile directory."
        str_offset = 0x80000
        data[str_offset : str_offset + len(target_str)] = target_str

        page = str_offset & ~0xFFF
        page_offset = str_offset & 0xFFF

        pc = 0x50000
        pc_page = pc & ~0xFFF
        imm = (page - pc_page) >> 12
        immlo = imm & 3
        immhi = (imm >> 2) & 0x7FFFF
        adrp_w = 0x90000000 | (immlo << 29) | (immhi << 5)
        add_w = 0x91000000 | (page_offset << 10)

        # Write bl targeting 0x60000, cmp w8, #0 (0x7100011f), adrp, add
        # bl offset = (0x60000 - (pc - 8)) >> 2 = (0x10008) >> 2 = 0x4002
        bl_inst = 0x94000000 | 0x4002
        cmp_w8 = 0x7100011F
        struct.pack_into("<IIII", data, pc - 8, bl_inst, cmp_w8, adrp_w, add_w)

        macho_file.write_bytes(data)

        assert HardCloneEngine.patch_framework_singletons(app_dir) is True

        patched_data = macho_file.read_bytes()
        bl_patched, _ = struct.unpack_from("<II", patched_data, pc - 8)
        assert bl_patched == 0x52800000  # mov w0, #0
        target_fn_patched, target_fn_ret = struct.unpack_from("<II", patched_data, 0x60000)
        assert target_fn_patched == 0x52800000  # mov w0, #0
        assert target_fn_ret == 0xD65F03C0  # ret

    def test_hard_clone_script_omits_singleton_patch_by_default(self, sample_task):
        sample_task.source.bundle_id = "com.example.normalapp"
        sample_task.recipe.patch_framework_singleton = False
        with patch("atbclone.executor.runner.Runner.run") as mock_run:
            HardCloneEngine.execute(sample_task, needs_admin=False)
            script, _ = mock_run.call_args[0]
            assert "Patch ProcessSingleton in embedded frameworks" not in script

    def test_hard_clone_script_includes_singleton_patch_for_lark(self, sample_task):
        sample_task.source.bundle_id = "com.electron.lark"
        with patch("atbclone.executor.runner.Runner.run") as mock_run:
            HardCloneEngine.execute(sample_task, needs_admin=False)
            script, _ = mock_run.call_args[0]
            assert "Patch ProcessSingleton in embedded frameworks" in script

    def test_hard_clone_script_includes_singleton_patch_when_recipe_flag_true(self, sample_task):
        sample_task.source.bundle_id = "com.other.electronapp"
        sample_task.recipe.patch_framework_singleton = True
        with patch("atbclone.executor.runner.Runner.run") as mock_run:
            HardCloneEngine.execute(sample_task, needs_admin=False)
            script, _ = mock_run.call_args[0]
            assert "Patch ProcessSingleton in embedded frameworks" in script


class TestCefFrameworkPatchingAndSymlinks:
    """Tests for Chromium Embedded Framework (CEF) patch gating and symlink whitelist generation."""

    def test_hard_clone_script_omits_cef_patch_by_default(self, sample_task):
        sample_task.source.bundle_id = "com.google.Chrome"
        sample_task.recipe.patch_cef = False
        with patch("atbclone.executor.runner.Runner.run") as mock_run:
            HardCloneEngine.execute(sample_task, needs_admin=False)
            script, _ = mock_run.call_args[0]
            assert "Patch CEF framework no_sandbox" not in script
            assert "CFBundleIdentifier $new_id." not in script

    def test_hard_clone_script_includes_cef_patch_when_recipe_flag_true(self, sample_task):
        sample_task.source.bundle_id = "com.custom.cefapp"
        sample_task.recipe.patch_cef = True
        with patch("atbclone.executor.runner.Runner.run") as mock_run:
            HardCloneEngine.execute(sample_task, needs_admin=False)
            script, _ = mock_run.call_args[0]
            assert "Patch CEF framework no_sandbox" in script
            assert "CFBundleIdentifier $new_id." in script

    def test_symlink_whitelist_snippet_generation_empty(self, sample_task):
        sample_task.recipe.symlink_whitelist = []
        snippet = HardCloneEngine._build_symlink_whitelist_snippet(sample_task)
        assert snippet == ""

    def test_symlink_whitelist_snippet_generation_populated(self, sample_task):
        sample_task.recipe.symlink_whitelist = ["Library/Keychains", ".ssh", "/Library/Preferences/foo.plist"]
        snippet = HardCloneEngine._build_symlink_whitelist_snippet(sample_task)
        assert "Library/Keychains" in snippet
        assert ".ssh" in snippet
        assert "Library/Preferences/foo.plist" in snippet
        assert "ln -s" in snippet


class TestEnginePermissionsAndXattrTolerance:
    """Tests to ensure read-only files in source apps don't fail clone creation due to xattr or PlistBuddy."""

    def test_hard_clone_ensures_writable_and_tolerant_xattr(self, sample_task):
        with patch("atbclone.executor.runner.Runner.run") as mock_run:
            HardCloneEngine.execute(sample_task, needs_admin=False)
            script, _ = mock_run.call_args[0]
            # Must ensure user write permission on destination
            assert f"chmod -R u+w {sample_task.dest_path} 2>/dev/null || true" in script
            # Must tolerate errors from xattr -cr
            assert f"xattr -cr {sample_task.dest_path} 2>/dev/null || true" in script

    def test_wrapper_guarantees_home_and_tmpdir_directories(self, sample_task):
        with patch("atbclone.executor.runner.Runner.run") as mock_run:
            HardCloneEngine.execute(sample_task, needs_admin=False)
            script, _ = mock_run.call_args[0]
            assert 'mkdir -p "$HOME" "$TMPDIR" 2>/dev/null || true' in script

        with patch("atbclone.executor.runner.Runner.run") as mock_run_soft:
            SoftCloneEngine.execute(sample_task, needs_admin=False)
            script_soft, _ = mock_run_soft.call_args[0]
            assert 'mkdir -p "$HOME" "$TMPDIR" 2>/dev/null || true' in script_soft

    def test_strip_sandbox_cleans_team_and_group_entitlements(self, sample_task):
        sample_task.recipe.strip_sandbox = True
        with patch("atbclone.executor.runner.Runner.run") as mock_run:
            HardCloneEngine.execute(sample_task, needs_admin=False)
            script, _ = mock_run.call_args[0]
            assert '/usr/libexec/PlistBuddy -c "Delete :com.apple.security.app-sandbox" "$ent_plist" 2>/dev/null || true' in script
            assert '/usr/libexec/PlistBuddy -c "Delete :com.apple.security.application-groups" "$ent_plist" 2>/dev/null || true' in script
            assert '/usr/libexec/PlistBuddy -c "Delete :com.apple.developer.team-identifier" "$ent_plist" 2>/dev/null || true' in script
            assert '/usr/libexec/PlistBuddy -c "Delete :com.apple.application-identifier" "$ent_plist" 2>/dev/null || true' in script

    def test_hard_clone_codex_home_script(self, mock_app_info, base_recipe):
        base_recipe.environment_injection = {
            "HOME": "{{ATB_DATA_DIR}}/Home",
            "TMPDIR": "{{ATB_DATA_DIR}}/Tmp",
            "CODEX_HOME": "{{ATB_DATA_DIR}}/Codex",
        }
        task = CloneTask(
            source=mock_app_info,
            dest_path=Path("/Applications/TestApp2.app"),
            data_dir=Path("/Users/test/data"),
            recipe=base_recipe,
            clone_name="TestApp2",
            new_bundle_id="com.example.testapp2",
        )
        with patch("atbclone.executor.runner.Runner.run") as mock_run:
            HardCloneEngine.execute(task, needs_admin=False)
            mock_run.assert_called_once()
            script, _ = mock_run.call_args[0]
            assert "export CODEX_HOME=/Users/test/data/Codex" in script
            assert 'if [ -d "$HOME/.codex" ] && [ ! -d /Users/test/data/Codex ]; then' in script
            assert 'cp -R "$HOME/.codex/." /Users/test/data/Codex/' in script
            assert 'if [ -n "$CODEX_HOME" ] && [ "$CODEX_HOME" != "$REAL_USER_HOME/.codex" ]; then' in script
            assert 'cp -R "$REAL_USER_HOME/.codex/." "$CODEX_HOME/"' in script

    def test_soft_clone_codex_home_script(self, mock_app_info, base_recipe):
        base_recipe.environment_injection = {
            "HOME": "{{ATB_DATA_DIR}}/Home",
            "TMPDIR": "{{ATB_DATA_DIR}}/Tmp",
            "CODEX_HOME": "{{ATB_DATA_DIR}}/Codex",
        }
        task = CloneTask(
            source=mock_app_info,
            dest_path=Path("/Applications/TestApp2.app"),
            data_dir=Path("/Users/test/data"),
            recipe=base_recipe,
            clone_name="TestApp2",
            new_bundle_id="com.example.testapp2",
        )
        with patch("atbclone.executor.runner.Runner.run") as mock_run:
            SoftCloneEngine.execute(task, needs_admin=False)
            mock_run.assert_called_once()
            script, _ = mock_run.call_args[0]
            assert "export CODEX_HOME=/Users/test/data/Codex" in script
            assert 'if [ -d "$HOME/.codex" ] && [ ! -d /Users/test/data/Codex ]; then' in script
            assert 'cp -R "$HOME/.codex/." /Users/test/data/Codex/' in script
            assert 'if [ -n "$CODEX_HOME" ] && [ "$CODEX_HOME" != "$REAL_USER_HOME/.codex" ]; then' in script
            assert 'cp -R "$REAL_USER_HOME/.codex/." "$CODEX_HOME/"' in script

    def test_hard_clone_gemini_home_script(self, mock_app_info, base_recipe):
        base_recipe.environment_injection = {
            "HOME": "{{ATB_DATA_DIR}}/Home",
            "TMPDIR": "{{ATB_DATA_DIR}}/Tmp",
            "GEMINI_HOME": "{{ATB_DATA_DIR}}/Gemini",
            "GEMINI_CONFIG_DIR": "{{ATB_DATA_DIR}}/Gemini",
            "ANTIGRAVITY_HOME": "{{ATB_DATA_DIR}}/Gemini",
        }
        task = CloneTask(
            source=mock_app_info,
            dest_path=Path("/Applications/TestApp2.app"),
            data_dir=Path("/Users/test/data"),
            recipe=base_recipe,
            clone_name="TestApp2",
            new_bundle_id="com.example.testapp2",
        )
        with patch("atbclone.executor.runner.Runner.run") as mock_run:
            HardCloneEngine.execute(task, needs_admin=False)
            mock_run.assert_called_once()
            script, _ = mock_run.call_args[0]
            assert "export GEMINI_HOME=/Users/test/data/Gemini" in script
            assert "export GEMINI_CONFIG_DIR=/Users/test/data/Gemini" in script
            assert "export ANTIGRAVITY_HOME=/Users/test/data/Gemini" in script
            assert 'if [ -d "$HOME/.gemini" ] && [ ! -d /Users/test/data/Gemini ]; then' in script
            assert 'cp -R "$HOME/.gemini/." /Users/test/data/Gemini/' in script
            assert 'cp -R "$REAL_USER_HOME/.gemini/." "$_TARGET_GEMINI_DIR/"' in script

    def test_soft_clone_gemini_home_script(self, mock_app_info, base_recipe):
        base_recipe.environment_injection = {
            "HOME": "{{ATB_DATA_DIR}}/Home",
            "TMPDIR": "{{ATB_DATA_DIR}}/Tmp",
            "GEMINI_HOME": "{{ATB_DATA_DIR}}/Gemini",
            "GEMINI_CONFIG_DIR": "{{ATB_DATA_DIR}}/Gemini",
            "ANTIGRAVITY_HOME": "{{ATB_DATA_DIR}}/Gemini",
        }
        task = CloneTask(
            source=mock_app_info,
            dest_path=Path("/Applications/TestApp2.app"),
            data_dir=Path("/Users/test/data"),
            recipe=base_recipe,
            clone_name="TestApp2",
            new_bundle_id="com.example.testapp2",
        )
        with patch("atbclone.executor.runner.Runner.run") as mock_run:
            SoftCloneEngine.execute(task, needs_admin=False)
            mock_run.assert_called_once()
            script, _ = mock_run.call_args[0]
            assert "export GEMINI_HOME=/Users/test/data/Gemini" in script
            assert "export GEMINI_CONFIG_DIR=/Users/test/data/Gemini" in script
            assert "export ANTIGRAVITY_HOME=/Users/test/data/Gemini" in script
            assert 'if [ -d "$HOME/.gemini" ] && [ ! -d /Users/test/data/Gemini ]; then' in script
            assert 'cp -R "$HOME/.gemini/." /Users/test/data/Gemini/' in script
            assert 'cp -R "$REAL_USER_HOME/.gemini/." "$_TARGET_GEMINI_DIR/"' in script

    def test_hard_clone_claude_script(self, mock_app_info, base_recipe):
        base_recipe.environment_injection = {
            "HOME": "{{ATB_DATA_DIR}}/Home",
            "TMPDIR": "{{ATB_DATA_DIR}}/Tmp",
            "CLAUDE_CONFIG_DIR": "{{ATB_DATA_DIR}}/Claude",
        }
        task = CloneTask(
            source=mock_app_info,
            dest_path=Path("/Applications/TestApp2.app"),
            data_dir=Path("/Users/test/data"),
            recipe=base_recipe,
            clone_name="TestApp2",
            new_bundle_id="com.example.testapp2",
        )
        with patch("atbclone.executor.runner.Runner.run") as mock_run:
            HardCloneEngine.execute(task, needs_admin=False)
            mock_run.assert_called_once()
            script, _ = mock_run.call_args[0]
            assert "export CLAUDE_CONFIG_DIR=/Users/test/data/Claude" in script
            assert 'if [ -d "$HOME/.claude" ] && [ ! -d /Users/test/data/Claude ]; then' in script
            assert 'cp -R "$HOME/.claude/." /Users/test/data/Claude/' in script
            assert 'if [ -n "$CLAUDE_CONFIG_DIR" ] && [ "$CLAUDE_CONFIG_DIR" != "$REAL_USER_HOME/.claude" ]; then' in script
            assert 'cp -R "$REAL_USER_HOME/.claude/." "$CLAUDE_CONFIG_DIR/"' in script

    def test_soft_clone_claude_script(self, mock_app_info, base_recipe):
        base_recipe.environment_injection = {
            "HOME": "{{ATB_DATA_DIR}}/Home",
            "TMPDIR": "{{ATB_DATA_DIR}}/Tmp",
            "CLAUDE_CONFIG_DIR": "{{ATB_DATA_DIR}}/Claude",
        }
        task = CloneTask(
            source=mock_app_info,
            dest_path=Path("/Applications/TestApp2.app"),
            data_dir=Path("/Users/test/data"),
            recipe=base_recipe,
            clone_name="TestApp2",
            new_bundle_id="com.example.testapp2",
        )
        with patch("atbclone.executor.runner.Runner.run") as mock_run:
            SoftCloneEngine.execute(task, needs_admin=False)
            mock_run.assert_called_once()
            script, _ = mock_run.call_args[0]
            assert "export CLAUDE_CONFIG_DIR=/Users/test/data/Claude" in script
            assert 'if [ -d "$HOME/.claude" ] && [ ! -d /Users/test/data/Claude ]; then' in script
            assert 'cp -R "$HOME/.claude/." /Users/test/data/Claude/' in script
            assert 'if [ -n "$CLAUDE_CONFIG_DIR" ] && [ "$CLAUDE_CONFIG_DIR" != "$REAL_USER_HOME/.claude" ]; then' in script
            assert 'cp -R "$REAL_USER_HOME/.claude/." "$CLAUDE_CONFIG_DIR/"' in script









