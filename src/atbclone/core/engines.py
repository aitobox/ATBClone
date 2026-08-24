"""Clone engines for creating soft (wrapper) and hard (physical) app clones."""

from pathlib import Path
import os
import shlex
import struct
import textwrap

from atbclone.core.clone_task import CloneTask
from atbclone.core.locale import build_language_wrapper_snippet
from atbclone.executor.runner import CloneError, Runner


class CloneEngine:
    """Base class providing shared helper methods for clone engines."""

    @staticmethod
    def _build_language_env_and_args(task: CloneTask) -> tuple[str, list[str]]:
        """Generate shell exports and launch arguments for language/locale configuration."""
        lang = getattr(task, "language", None) or getattr(task.recipe, "language", "system")
        app_type = getattr(task.recipe, "app_type", None)
        if not app_type and hasattr(task, "source") and task.source and getattr(task.source, "path", None):
            from atbclone.core.app_prober import AppProber
            app_type = AppProber.detect_app_type(
                task.source.path,
                bundle_id=getattr(task.source, "bundle_id", ""),
            )
        return build_language_wrapper_snippet(lang, app_type=app_type or "cocoa")

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

    @classmethod
    def _get_validated_launch_args(cls, task: CloneTask) -> list[str]:
        """Validate launch_args against app_type and executable binary strings, pruning unsupported args."""
        from atbclone.core.argument_prober import LaunchArgumentValidator
        app_type = getattr(task.recipe, "app_type", None)
        if not app_type and hasattr(task, "source") and task.source and getattr(task.source, "path", None):
            from atbclone.core.app_prober import AppProber
            app_type = AppProber.detect_app_type(
                task.source.path,
                bundle_id=getattr(task.source, "bundle_id", ""),
            )
        exe_path = getattr(task.source, "executable", None) or task.source.path
        valid_args, _ = LaunchArgumentValidator.validate_and_filter(
            exe_path,
            task.recipe.launch_args,
            app_type=app_type or "generic",
        )
        return valid_args

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

    @staticmethod
    def _build_display_name_cmd(effective_display_name: str, dst_plist: str, dst_resources: str) -> str:
        """Return a shell snippet that applies display name to Info.plist and removes localized overrides."""
        name_escaped = effective_display_name.replace('\\', '\\\\').replace('"', '\\"')
        return textwrap.dedent(f"""
            /usr/libexec/PlistBuddy -c "Set :CFBundleName {name_escaped}" {dst_plist} 2>/dev/null || /usr/libexec/PlistBuddy -c "Add :CFBundleName string {name_escaped}" {dst_plist}
            /usr/libexec/PlistBuddy -c "Set :CFBundleDisplayName {name_escaped}" {dst_plist} 2>/dev/null || /usr/libexec/PlistBuddy -c "Add :CFBundleDisplayName string {name_escaped}" {dst_plist}
            /usr/libexec/PlistBuddy -c "Delete :LSHasLocalizedDisplayName" {dst_plist} 2>/dev/null || true
            if [ -d {dst_resources} ]; then
                find {dst_resources} -name "InfoPlist.strings" -type f -print0 2>/dev/null | while IFS= read -r -d '' str_file; do
                    /usr/libexec/PlistBuddy -c "Delete :CFBundleDisplayName" "$str_file" 2>/dev/null || true
                    /usr/libexec/PlistBuddy -c "Delete :CFBundleName" "$str_file" 2>/dev/null || true
                    /usr/libexec/PlistBuddy -c "Delete :CFBundleGetInfoString" "$str_file" 2>/dev/null || true
                done
            fi
        """).strip()

    @staticmethod
    def _combine_launch_args(valid_launch_args: list[str], lang_args: list[str], data_dir: Path) -> list[str]:
        """Combine recipe launch args with language args, deduplicating conflicting language flags."""
        args_list: list[str] = []
        lang_prefixes: set[str] = set()
        for larg in lang_args:
            if larg.startswith("--lang="):
                lang_prefixes.add("--lang=")
            elif larg in ("-AppleLanguages", "-AppleLocale"):
                lang_prefixes.add(larg)

        for arg in valid_launch_args:
            if any(arg.startswith(k) for k in lang_prefixes if k.startswith("--")):
                continue
            if arg in ("-AppleLanguages", "-AppleLocale"):
                continue
            args_list.append(shlex.quote(arg.replace("{{ATB_DATA_DIR}}", str(data_dir))))

        for larg in lang_args:
            args_list.append(shlex.quote(larg))

        return args_list

    @staticmethod
    def _build_lsregister_cmd(dst_app: str) -> str:
        """Return shell snippet to register the app bundle with LaunchServices."""
        return f"/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -f {dst_app} 2>/dev/null || true"


class SoftCloneEngine(CloneEngine):
    """Creates a lightweight wrapper app that launches the original binary with custom args and environment."""

    @classmethod
    def execute(cls, task: CloneTask, needs_admin: bool = False) -> None:
        """Execute soft clone script.

        Args:
            task: The clone task parameters.
            needs_admin: Whether administrator elevation is required.
        """
        if getattr(task.source, "is_ios_app", False):
            from atbclone.core.i18n import t
            raise CloneError(t("clone_err_ios_wrapper_unsupported"))

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

        lang_env, lang_args = cls._build_language_env_and_args(task)
        valid_launch_args = cls._get_validated_launch_args(task)

        args_list = cls._combine_launch_args(valid_launch_args, lang_args, task.data_dir)

        args_str = f" {' '.join(args_list)}" if args_list else ""
        exec_cmd = f'exec {src_bin}{args_str} "$@"'

        proxy_env = cls._build_proxy_env(task)
        wrapper_lines = ["#!/bin/bash", 'REAL_USER_HOME="$HOME"']
        if lang_env:
            wrapper_lines.append(lang_env)
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
        display_name_cmd = cls._build_display_name_cmd(effective_display_name, dst_plist, dst_resources)
        icon_cmd = cls._build_icon_cmd(task, dst_resources, dst_plist)
        lsregister_cmd = cls._build_lsregister_cmd(dst_app)

        script = f"""set -e
mkdir -p {dst_parent}
mkdir -p {data_dir}
rm -rf {dst_app}
mkdir -p {dst_mac}
# Copy Resources dir so the app icon (.icns) and other assets are available
if [ -d {src_resources} ]; then
    cp -R {src_resources} {dst_resources}
fi
cp {src_plist} {dst_plist}
/usr/libexec/PlistBuddy -c "Set :CFBundleIdentifier {task.new_bundle_id}" {dst_plist}
{display_name_cmd}
{icon_cmd}cat << 'WRAPPER_EOF' > {wrapper}
{wrapper_body}
WRAPPER_EOF
chmod +x {wrapper}
{lsregister_cmd}
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
    def _build_singleton_patch_cmd(cls, dest_path: Path) -> str:
        """Return a shell snippet that patches ProcessSingleton in embedded frameworks if present.

        Some Electron/Chromium apps (e.g. Feishu/Lark) contain custom ProcessSingleton logic
        in embedded framework binaries (like Lark Framework.framework). When launched as a second
        instance, they call ProcessSingleton::NotifyOtherProcessOrCreate() which immediately signals
        the first instance and exits (exit code 34). This command scans embedded Mach-O binaries in
        Contents/Frameworks/ and patches the bl NotifyOtherProcessOrCreate call with `mov w0, #0; nop`
        so every clone runs concurrently as an independent primary instance.
        """
        dest_quoted = shlex.quote(str(dest_path))
        return textwrap.dedent(f"""\
            # Patch ProcessSingleton in embedded frameworks if present (e.g. Feishu/Lark)
            python3 -c '
import os, glob, struct
frameworks_dir = os.path.join({dest_quoted}, "Contents", "Frameworks")
target_str = b"Failed to create a ProcessSingleton for your profile directory."
if os.path.isdir(frameworks_dir):
    for root, _, files in os.walk(frameworks_dir):
        for fname in files:
            fpath = os.path.join(root, fname)
            if os.path.islink(fpath) or not os.path.isfile(fpath):
                continue
            try:
                if os.path.getsize(fpath) < 1000000:
                    continue
                with open(fpath, "rb") as f:
                    header = f.read(4)
                    if header not in (b"\\xcf\\xfa\\xed\\xfe", b"\\xfe\\xed\\xfa\\xcf"):
                        continue
                    f.seek(0)
                    data = bytearray(f.read())
                str_idx = data.find(target_str)
                if str_idx == -1:
                    continue
                page = str_idx & ~0xFFF
                page_offset = str_idx & 0xFFF
                found_pc = None
                for i in range(0, len(data) - 8, 4):
                    w1, w2 = struct.unpack_from("<II", data, i)
                    if (w1 & 0x9F000000) == 0x90000000:
                        immlo = (w1 >> 29) & 3
                        immhi = (w1 >> 5) & 0x7FFFF
                        imm = (immhi << 2) | immlo
                        if imm & (1 << 20): imm -= (1 << 21)
                        if (i & ~0xFFF) + (imm << 12) == page:
                            if (w2 & 0xFFC00000) == 0x91000000 and ((w2 >> 10) & 0xFFF) == page_offset:
                                found_pc = i
                                break
                if found_pc is None:
                    continue
                cmp_pos = None
                for pos in range(found_pc - 4, max(0, found_pc - 200), -4):
                    w, = struct.unpack_from("<I", data, pos)
                    if w == 0x7100001F:
                        cmp_pos = pos
                        break
                if cmp_pos is None:
                    continue
                bl_pos = cmp_pos - 4
                w_bl, = struct.unpack_from("<I", data, bl_pos)
                if (w_bl & 0xFC000000) == 0x94000000:
                    struct.pack_into("<II", data, bl_pos, 0x52800000, 0xD503201F)
                    with open(fpath, "wb") as f:
                        f.write(data)
            except Exception:
                pass
' 2>/dev/null || true
        """)

    @staticmethod
    def patch_framework_singletons(dest_path: Path) -> bool:
        """Python helper to patch ProcessSingleton in embedded frameworks for testing and tools."""
        import struct
        patched_any = False
        target_str = b"Failed to create a ProcessSingleton for your profile directory."

        frameworks_dir = dest_path / "Contents" / "Frameworks"
        if not frameworks_dir.is_dir():
            return False

        for root, _, files in os.walk(frameworks_dir):
            for fname in files:
                fpath = Path(root) / fname
                if fpath.is_symlink() or not fpath.is_file():
                    continue
                try:
                    if fpath.stat().st_size < 1_000_000:
                        continue
                    with open(fpath, "rb") as f:
                        header = f.read(4)
                        if header not in (b"\xcf\xfa\xed\xfe", b"\xfe\xed\xfa\xcf"):
                            continue
                        f.seek(0)
                        data = bytearray(f.read())

                    str_idx = data.find(target_str)
                    if str_idx == -1:
                        continue

                    page = str_idx & ~0xFFF
                    page_offset = str_idx & 0xFFF

                    found_pc = None
                    for i in range(0, len(data) - 8, 4):
                        w1, w2 = struct.unpack_from("<II", data, i)
                        if (w1 & 0x9F000000) == 0x90000000:
                            immlo = (w1 >> 29) & 3
                            immhi = (w1 >> 5) & 0x7FFFF
                            imm = (immhi << 2) | immlo
                            if imm & (1 << 20):
                                imm -= 1 << 21
                            if (i & ~0xFFF) + (imm << 12) == page:
                                if (w2 & 0xFFC00000) == 0x91000000 and ((w2 >> 10) & 0xFFF) == page_offset:
                                    found_pc = i
                                    break

                    if found_pc is None:
                        continue

                    cmp_pos = None
                    for pos in range(found_pc - 4, max(0, found_pc - 200), -4):
                        (w,) = struct.unpack_from("<I", data, pos)
                        if w == 0x7100001F:
                            cmp_pos = pos
                            break

                    if cmp_pos is None:
                        continue

                    bl_pos = cmp_pos - 4
                    (w_bl,) = struct.unpack_from("<I", data, bl_pos)
                    if (w_bl & 0xFC000000) == 0x94000000:
                        struct.pack_into("<II", data, bl_pos, 0x52800000, 0xD503201F)
                        with open(fpath, "wb") as f:
                            f.write(data)
                        patched_any = True
                except Exception:
                    continue

        return patched_any

    @classmethod
    def execute(cls, task: CloneTask, needs_admin: bool = False) -> None:
        """Execute hard clone script.

        Args:
            task: The clone task parameters.
            needs_admin: Whether administrator elevation is required.
        """
        if getattr(task.source, "is_ios_app", False):
            from atbclone.core.i18n import t
            raise CloneError(t("clone_err_ios_wrapper_unsupported"))

        src = shlex.quote(str(task.source.path))
        dst = shlex.quote(str(task.dest_path))

        rel_plist = getattr(task.source, "relative_plist_path", Path("Contents/Info.plist"))
        rel_resources = getattr(task.source, "relative_resources_path", Path("Contents/Resources"))

        dst_plist = shlex.quote(str(task.dest_path / rel_plist))
        dst_resources = shlex.quote(str(task.dest_path / rel_resources))

        # Effective display name: explicit override > clone_name
        effective_display_name = task.display_name if task.display_name else task.clone_name
        display_name_cmd = cls._build_display_name_cmd(effective_display_name, dst_plist, dst_resources)
        icon_cmd = cls._build_icon_cmd(task, dst_resources, dst_plist)
        lsregister_cmd = cls._build_lsregister_cmd(dst)
        dst_parent = shlex.quote(str(task.dest_path.parent))
        data_dir = shlex.quote(str(task.data_dir))
        orig_bin_name = (
            task.source.executable.name
            if task.source.executable and task.source.executable.name
            else task.source.app_name
        )
        bin_orig = shlex.quote(str(task.dest_path / "Contents" / "MacOS" / orig_bin_name))
        bin_bak = shlex.quote(str(task.dest_path / "Contents" / "MacOS" / f"{orig_bin_name}.bin"))
        wrapper = bin_orig

        lang_env, lang_args = cls._build_language_env_and_args(task)
        valid_launch_args = cls._get_validated_launch_args(task)

        # Fallback environment isolation if no valid launch args isolate data dir and no env vars are set
        effective_env = dict(task.recipe.environment_injection)
        has_data_in_args = any("{{ATB_DATA_DIR}}" in a for a in valid_launch_args)
        has_data_in_env = any("{{ATB_DATA_DIR}}" in v for v in effective_env.values())
        if not has_data_in_args and not has_data_in_env:
            effective_env["HOME"] = "{{ATB_DATA_DIR}}/Home"
            effective_env["TMPDIR"] = "{{ATB_DATA_DIR}}/Tmp"

        env_vars = "\n".join([
            f"export {k}={shlex.quote(v.replace('{{ATB_DATA_DIR}}', str(task.data_dir)))}"
            for k, v in effective_env.items()
        ])
        proxy_env = cls._build_proxy_env(task)

        # Inject launch_args (e.g. --user-data-dir=... for Chromium apps)
        args_list = cls._combine_launch_args(valid_launch_args, lang_args, task.data_dir)

        args_str = f" {' '.join(args_list)}" if args_list else ""

        wrapper_lines = ["#!/bin/bash", 'REAL_USER_HOME="$HOME"']
        if env_vars:
            wrapper_lines.append(env_vars)
        if lang_env:
            wrapper_lines.append(lang_env)
        if proxy_env:
            wrapper_lines.append(proxy_env)

        wrapper_lines.append(f'exec "$(dirname "$0")/{orig_bin_name}.bin"{args_str} "$@"')
        wrapper_body = "\n".join(wrapper_lines)

        # Build framework singleton patcher command for Electron/Chromium apps
        singleton_patch_cmd = cls._build_singleton_patch_cmd(task.dest_path)


        if task.recipe.strip_sandbox:
            ent_plist = shlex.quote(str(task.dest_path / "Contents" / "atb_entitlements.plist"))
            codesign_cmds = (
                f"codesign -d --entitlements :- {src} > {ent_plist} 2>/dev/null || true\n"
                f"if [ -s {ent_plist} ]; then\n"
                f'    /usr/libexec/PlistBuddy -c "Delete :com.apple.security.app-sandbox" {ent_plist} 2>/dev/null || true\n'
                f"    codesign --force --deep --sign - --entitlements {ent_plist} {dst}\n"
                f"else\n"
                f"    rm -f {ent_plist}\n"
                f"    codesign --force --deep --sign - {dst}\n"
                f"fi\n"
            )
        else:
            codesign_cmds = f"codesign --force --deep --sign - {dst}\n"

        script = f"""set -e
mkdir -p {dst_parent}
mkdir -p {data_dir}
rm -rf {dst}
cp -R {src} {dst}
/usr/libexec/PlistBuddy -c "Set :CFBundleIdentifier {task.new_bundle_id}" {dst_plist}
{display_name_cmd}
{icon_cmd}mv {bin_orig} {bin_bak}
cat << 'WRAPPER_EOF' > {wrapper}
{wrapper_body}
WRAPPER_EOF
chmod +x {wrapper}
{singleton_patch_cmd}xattr -cr {dst}
{codesign_cmds}codesign -vv --deep --strict {dst}
{lsregister_cmd}
"""

        try:
            Runner.run(script, needs_admin)
        except Exception:
            try:
                Runner.run(f"rm -rf {dst}", needs_admin)
            except (CloneError, OSError):
                pass
            raise

