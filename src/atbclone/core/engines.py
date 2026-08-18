"""Clone engines for creating soft (wrapper) and hard (physical) app clones."""

import shlex
import textwrap

from atbclone.core.clone_task import CloneTask
from atbclone.executor.runner import CloneError, Runner


class CloneEngine:
    """Base class providing shared helper methods for clone engines."""

    @staticmethod
    def _build_proxy_env(task: CloneTask) -> str:
        """Generate shell export statements for proxy environment variables if enabled."""
        proxy = task.recipe.proxy
        if not proxy.enabled:
            return ""
        return textwrap.dedent(f"""
            export HTTP_PROXY="{proxy.url}"
            export HTTPS_PROXY="{proxy.url}"
            export http_proxy="$HTTP_PROXY"
            export https_proxy="$HTTPS_PROXY"
            export NO_PROXY="{proxy.no_proxy}"
            export no_proxy="$NO_PROXY"
        """).strip()


class SoftCloneEngine(CloneEngine):
    """Creates a lightweight wrapper app that launches the original binary with custom args and environment."""

    @classmethod
    def execute(cls, task: CloneTask, needs_admin: bool = False) -> None:
        """Execute soft clone script.

        Args:
            task: The clone task parameters.
            needs_admin: Whether administrator elevation is required.
        """
        src_bin = shlex.quote(str(task.source.executable))
        src_plist = shlex.quote(str(task.source.path / "Contents" / "Info.plist"))
        dst_app = shlex.quote(str(task.dest_path))
        dst_mac = shlex.quote(str(task.dest_path / "Contents" / "MacOS"))
        dst_plist = shlex.quote(str(task.dest_path / "Contents" / "Info.plist"))

        bin_name = (
            task.source.executable.name
            if task.source.executable and task.source.executable.name
            else task.source.app_name
        )
        wrapper = shlex.quote(str(task.dest_path / "Contents" / "MacOS" / bin_name))

        args_list = [
            arg.replace("{{ATB_DATA_DIR}}", str(task.data_dir))
            for arg in task.recipe.launch_args
        ]
        args_str = f" {' '.join(args_list)}" if args_list else ""
        exec_cmd = f"exec {src_bin}{args_str} >/dev/null 2>&1 &"

        proxy_env = cls._build_proxy_env(task)
        wrapper_lines = ["#!/bin/bash"]
        if proxy_env:
            wrapper_lines.append(proxy_env)
        wrapper_lines.append(exec_cmd)
        wrapper_body = "\n".join(wrapper_lines)

        script = f"""set -e
mkdir -p {dst_mac}
cp {src_plist} {dst_plist}
/usr/libexec/PlistBuddy -c "Set :CFBundleIdentifier {task.new_bundle_id}" {dst_plist}
/usr/libexec/PlistBuddy -c "Set :CFBundleName {task.clone_name}" {dst_plist}
cat << 'WRAPPER_EOF' > {wrapper}
{wrapper_body}
WRAPPER_EOF
chmod +x {wrapper}
"""
        try:
            Runner.run(script, needs_admin)
        except Exception:
            try:
                Runner.run(f"rm -rf {dst_app}", needs_admin)
            except (CloneError, OSError):
                pass
            raise


class HardCloneEngine(CloneEngine):
    """Creates a full physical clone of the app bundle with binary renaming, wrapper, and re-signing."""

    @classmethod
    def execute(cls, task: CloneTask, needs_admin: bool = False) -> None:
        """Execute hard clone script.

        Args:
            task: The clone task parameters.
            needs_admin: Whether administrator elevation is required.
        """
        src = shlex.quote(str(task.source.path))
        dst = shlex.quote(str(task.dest_path))
        dst_plist = shlex.quote(str(task.dest_path / "Contents" / "Info.plist"))

        orig_bin_name = (
            task.source.executable.name
            if task.source.executable and task.source.executable.name
            else task.source.app_name
        )
        bin_orig = shlex.quote(str(task.dest_path / "Contents" / "MacOS" / orig_bin_name))
        bin_bak = shlex.quote(str(task.dest_path / "Contents" / "MacOS" / f"{orig_bin_name}.bin"))
        wrapper = bin_orig

        env_vars = "\n".join([
            f'export {k}="{v.replace("{{ATB_DATA_DIR}}", str(task.data_dir))}"'
            for k, v in task.recipe.environment_injection.items()
        ])
        proxy_env = cls._build_proxy_env(task)

        wrapper_lines = ["#!/bin/bash"]
        if env_vars:
            wrapper_lines.append(env_vars)
        if proxy_env:
            wrapper_lines.append(proxy_env)
        wrapper_lines.append(f'exec "$(dirname "$0")/{orig_bin_name}.bin" "$@"')
        wrapper_body = "\n".join(wrapper_lines)

        if task.recipe.strip_sandbox:
            codesign_cmds = (
                f"codesign -d --entitlements :- {dst} > /tmp/atb_entitlements.plist 2>/dev/null || true\n"
                f'/usr/libexec/PlistBuddy -c "Delete :com.apple.security.app-sandbox" /tmp/atb_entitlements.plist || true\n'
                f"codesign --force --deep --sign - --entitlements /tmp/atb_entitlements.plist {dst}\n"
            )
        else:
            codesign_cmds = f"codesign --force --deep --sign - {dst}\n"

        script = f"""set -e
cp -R {src} {dst}
/usr/libexec/PlistBuddy -c "Set :CFBundleIdentifier {task.new_bundle_id}" {dst_plist}
/usr/libexec/PlistBuddy -c "Set :CFBundleName {task.clone_name}" {dst_plist}
mv {bin_orig} {bin_bak}
cat << 'WRAPPER_EOF' > {wrapper}
{wrapper_body}
WRAPPER_EOF
chmod +x {wrapper}
xattr -cr {dst}
{codesign_cmds}codesign -vv --deep --strict {dst}
"""
        try:
            Runner.run(script, needs_admin)
        except Exception:
            try:
                Runner.run(f"rm -rf {dst}", needs_admin)
            except (CloneError, OSError):
                pass
            raise
