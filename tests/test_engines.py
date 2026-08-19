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
            assert '/usr/libexec/PlistBuddy -c "Set :CFBundleIdentifier com.example.testapp.clone2" /Applications/TestApp2.app/Contents/Info.plist' in script
            assert '/usr/libexec/PlistBuddy -c "Set :CFBundleName TestApp 2" /Applications/TestApp2.app/Contents/Info.plist' in script
            assert "cat << 'WRAPPER_EOF' > /Applications/TestApp2.app/Contents/MacOS/TestApp" in script
            assert 'exec /Applications/TestApp.app/Contents/MacOS/TestApp "$@"' in script
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
            assert "exec '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' \"$@\"" in script

    def test_soft_clone_with_launch_args_and_proxy(self, sample_task):
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
            assert "exec /Applications/TestApp.app/Contents/MacOS/TestApp '--user-data-dir=/Users/test/Library/Application Support/TestApp2' --no-first-run \"$@\"" in script

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
            assert '/usr/libexec/PlistBuddy -c "Set :CFBundleIdentifier com.example.testapp.clone2" /Applications/TestApp2.app/Contents/Info.plist' in script
            assert '/usr/libexec/PlistBuddy -c "Set :CFBundleName TestApp 2" /Applications/TestApp2.app/Contents/Info.plist' in script
            assert "mv /Applications/TestApp2.app/Contents/MacOS/TestApp /Applications/TestApp2.app/Contents/MacOS/TestApp.bin" in script
            assert "cat << 'WRAPPER_EOF' > /Applications/TestApp2.app/Contents/MacOS/TestApp" in script
            assert 'exec "$(dirname "$0")/TestApp.bin" "$@"' in script
            assert "chmod +x /Applications/TestApp2.app/Contents/MacOS/TestApp" in script
            assert "xattr -cr /Applications/TestApp2.app" in script
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
            assert 'exec "$(dirname "$0")/Google Chrome.bin" "$@"' in script


    def test_hard_clone_with_strip_sandbox(self, sample_task):
        sample_task.recipe.strip_sandbox = True
        with patch("atbclone.executor.runner.Runner.run") as mock_run:
            HardCloneEngine.execute(sample_task, needs_admin=False)
            mock_run.assert_called_once()
            script, _ = mock_run.call_args[0]
            assert "codesign -d --entitlements :- /Applications/TestApp2.app > /Applications/TestApp2.app/Contents/atb_entitlements.plist 2>/dev/null || true" in script
            assert '/usr/libexec/PlistBuddy -c "Delete :com.apple.security.app-sandbox" /Applications/TestApp2.app/Contents/atb_entitlements.plist || true' in script
            assert "codesign --force --deep --sign - --entitlements /Applications/TestApp2.app/Contents/atb_entitlements.plist /Applications/TestApp2.app" in script
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

    def test_hard_clone_with_launch_args(self, sample_task):
        sample_task.recipe.launch_args = ["--user-data-dir={{ATB_DATA_DIR}}", "--no-first-run"]
        with patch("atbclone.executor.runner.Runner.run") as mock_run:
            HardCloneEngine.execute(sample_task, needs_admin=False)
            mock_run.assert_called_once()
            script, _ = mock_run.call_args[0]
            assert "exec \"$(dirname \"$0\")/TestApp.bin\" '--user-data-dir=/Users/test/Library/Application Support/TestApp2' --no-first-run \"$@\"" in script

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

    def test_custom_display_name_overrides_clone_name(self, sample_task):
        """When display_name is set, CFBundleDisplayName should use it instead."""
        sample_task.display_name = "我的测试App"
        with patch("atbclone.executor.runner.Runner.run") as mock_run:
            SoftCloneEngine.execute(sample_task, needs_admin=False)
            script, _ = mock_run.call_args[0]
            assert "Set :CFBundleDisplayName 我的测试App" in script
            # clone_name should NOT appear in the DisplayName line
            assert "Set :CFBundleDisplayName TestApp 2" not in script

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

    def test_lshaslocalizedname_deleted(self, sample_task):
        """LSHasLocalizedDisplayName delete command must always be present."""
        with patch("atbclone.executor.runner.Runner.run") as mock_run:
            SoftCloneEngine.execute(sample_task, needs_admin=False)
            script, _ = mock_run.call_args[0]
            assert "Delete :LSHasLocalizedDisplayName" in script


class TestHardCloneEngineCustomisation:
    """Tests for display_name and icon_path in HardCloneEngine."""

    def test_default_display_name_uses_clone_name(self, sample_task):
        sample_task.display_name = None
        with patch("atbclone.executor.runner.Runner.run") as mock_run:
            HardCloneEngine.execute(sample_task, needs_admin=False)
            script, _ = mock_run.call_args[0]
            assert "Set :CFBundleDisplayName TestApp 2" in script

    def test_custom_display_name_overrides_clone_name(self, sample_task):
        sample_task.display_name = "硬克隆App"
        with patch("atbclone.executor.runner.Runner.run") as mock_run:
            HardCloneEngine.execute(sample_task, needs_admin=False)
            script, _ = mock_run.call_args[0]
            assert "Set :CFBundleDisplayName 硬克隆App" in script
            assert "Set :CFBundleDisplayName TestApp 2" not in script

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

    def test_lshaslocalizedname_deleted(self, sample_task):
        with patch("atbclone.executor.runner.Runner.run") as mock_run:
            HardCloneEngine.execute(sample_task, needs_admin=False)
            script, _ = mock_run.call_args[0]
            assert "Delete :LSHasLocalizedDisplayName" in script

