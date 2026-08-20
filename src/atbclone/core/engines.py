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

    @staticmethod
    def _build_icon_cmd(task: CloneTask, dst_resources: str, dst_plist: str) -> str:
        """Return a shell snippet that applies icon customisation after Resources are in place.

        When task.icon_path is set, the custom .icns is copied over the file named by
        CFBundleIconFile in the destination plist.  Falls back silently if the plist key
        is missing (uncommon but possible).  Returns empty string when icon_path is None.
        """
        if task.icon_path is None:
            return ""
        custom_icon = shlex.quote(str(task.icon_path))
        return (
            f"ICON_FILE=$(/usr/libexec/PlistBuddy -c \"Print :CFBundleIconFile\" {dst_plist} 2>/dev/null || true)\n"
            f"[ -n \"$ICON_FILE\" ] && cp {custom_icon} {dst_resources}/\"$ICON_FILE\" || true\n"
        )


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
            shlex.quote(arg.replace("{{ATB_DATA_DIR}}", str(task.data_dir)))
            for arg in task.recipe.launch_args
        ]
        args_str = f" {' '.join(args_list)}" if args_list else ""
        exec_cmd = f'exec {src_bin}{args_str} "$@"'


        proxy_env = cls._build_proxy_env(task)
        wrapper_lines = ["#!/bin/bash"]
        if proxy_env:
            wrapper_lines.append(proxy_env)
        wrapper_lines.append(exec_cmd)
        wrapper_body = "\n".join(wrapper_lines)

        src_resources = shlex.quote(str(task.source.path / "Contents" / "Resources"))
        dst_resources = shlex.quote(str(task.dest_path / "Contents" / "Resources"))
        dst_parent = shlex.quote(str(task.dest_path.parent))
        data_dir = shlex.quote(str(task.data_dir))

        # Effective display name: explicit override > clone_name
        effective_display_name = task.display_name if task.display_name else task.clone_name
        icon_cmd = cls._build_icon_cmd(task, dst_resources, dst_plist)

        script = f"""set -e
mkdir -p {dst_parent}
mkdir -p {data_dir}
mkdir -p {dst_mac}
# Copy Resources dir so the app icon (.icns) and other assets are available
if [ -d {src_resources} ]; then
    cp -R {src_resources} {dst_resources}
fi
cp {src_plist} {dst_plist}
/usr/libexec/PlistBuddy -c "Set :CFBundleIdentifier {task.new_bundle_id}" {dst_plist}
/usr/libexec/PlistBuddy -c "Set :CFBundleName {task.clone_name}" {dst_plist}
/usr/libexec/PlistBuddy -c "Set :CFBundleDisplayName {effective_display_name}" {dst_plist} 2>/dev/null || /usr/libexec/PlistBuddy -c "Add :CFBundleDisplayName string {effective_display_name}" {dst_plist}
/usr/libexec/PlistBuddy -c "Delete :LSHasLocalizedDisplayName" {dst_plist} 2>/dev/null || true
{icon_cmd}cat << 'WRAPPER_EOF' > {wrapper}
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
        dst_resources = shlex.quote(str(task.dest_path / "Contents" / "Resources"))

        orig_bin_name = (
            task.source.executable.name
            if task.source.executable and task.source.executable.name
            else task.source.app_name
        )
        bin_orig = shlex.quote(str(task.dest_path / "Contents" / "MacOS" / orig_bin_name))
        bin_bak = shlex.quote(str(task.dest_path / "Contents" / "MacOS" / f"{orig_bin_name}.bin"))
        wrapper = bin_orig

        env_vars = "\n".join([
            f"export {k}={shlex.quote(v.replace('{{ATB_DATA_DIR}}', str(task.data_dir)))}"
            for k, v in task.recipe.environment_injection.items()
        ])
        proxy_env = cls._build_proxy_env(task)

        # Inject launch_args (e.g. --user-data-dir=... for Chromium apps)
        args_list = [
            shlex.quote(arg.replace("{{ATB_DATA_DIR}}", str(task.data_dir)))
            for arg in task.recipe.launch_args
        ]
        args_str = f" {' '.join(args_list)}" if args_list else ""

        wrapper_lines = ["#!/bin/bash"]
        if env_vars:
            wrapper_lines.append(env_vars)
        if proxy_env:
            wrapper_lines.append(proxy_env)
        wrapper_lines.append(f'exec "$(dirname "$0")/{orig_bin_name}.bin"{args_str} "$@"')
        wrapper_body = "\n".join(wrapper_lines)


        if task.recipe.strip_sandbox:
            ent_plist = shlex.quote(str(task.dest_path / "Contents" / "atb_entitlements.plist"))
            codesign_cmds = (
                f"codesign -d --entitlements :- {dst} > {ent_plist} 2>/dev/null || true\n"
                f'/usr/libexec/PlistBuddy -c "Delete :com.apple.security.app-sandbox" {ent_plist} || true\n'
                f"codesign --force --deep --sign - --entitlements {ent_plist} {dst}\n"
            )
        else:
            codesign_cmds = f"codesign --force --deep --sign - {dst}\n"

        # Effective display name: explicit override > clone_name
        effective_display_name = task.display_name if task.display_name else task.clone_name
        icon_cmd = cls._build_icon_cmd(task, dst_resources, dst_plist)
        dst_parent = shlex.quote(str(task.dest_path.parent))
        data_dir = shlex.quote(str(task.data_dir))

        script = f"""set -e
mkdir -p {dst_parent}
mkdir -p {data_dir}
cp -R {src} {dst}
/usr/libexec/PlistBuddy -c "Set :CFBundleIdentifier {task.new_bundle_id}" {dst_plist}
/usr/libexec/PlistBuddy -c "Set :CFBundleName {task.clone_name}" {dst_plist}
/usr/libexec/PlistBuddy -c "Set :CFBundleDisplayName {effective_display_name}" {dst_plist} 2>/dev/null || /usr/libexec/PlistBuddy -c "Add :CFBundleDisplayName string {effective_display_name}" {dst_plist}
/usr/libexec/PlistBuddy -c "Delete :LSHasLocalizedDisplayName" {dst_plist} 2>/dev/null || true
{icon_cmd}mv {bin_orig} {bin_bak}
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
