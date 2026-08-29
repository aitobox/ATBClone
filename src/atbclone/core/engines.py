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

    @staticmethod
    def _build_codex_init_cmd(effective_env: dict[str, str], data_dir: Path) -> str:
        """Return shell snippet to initialize CODEX_HOME from ~/.codex at clone creation time."""
        if "CODEX_HOME" not in effective_env:
            return ""
        raw_val = effective_env["CODEX_HOME"]
        target_path = raw_val.replace("{{ATB_DATA_DIR}}", str(data_dir))
        target_quoted = shlex.quote(target_path)
        return textwrap.dedent(f"""\
            if [ -d "$HOME/.codex" ] && [ ! -d {target_quoted} ]; then
                mkdir -p {target_quoted}
                cp -R "$HOME/.codex/." {target_quoted}/ 2>/dev/null || true
            fi
        """).strip() + "\n"

    @staticmethod
    def _build_gemini_init_cmd(effective_env: dict[str, str], data_dir: Path) -> str:
        """Return shell snippet to initialize GEMINI_HOME from ~/.gemini at clone creation time."""
        target_val = (
            effective_env.get("GEMINI_HOME")
            or effective_env.get("ANTIGRAVITY_HOME")
            or effective_env.get("GEMINI_CONFIG_DIR")
        )
        if not target_val:
            return ""
        target_path = target_val.replace("{{ATB_DATA_DIR}}", str(data_dir))
        target_quoted = shlex.quote(target_path)
        return textwrap.dedent(f"""\
            if [ -d "$HOME/.gemini" ] && [ ! -d {target_quoted} ]; then
                mkdir -p {target_quoted}
                cp -R "$HOME/.gemini/." {target_quoted}/ 2>/dev/null || true
            fi
        """).strip() + "\n"

    @staticmethod
    def _build_claude_init_cmd(effective_env: dict[str, str], data_dir: Path) -> str:
        """Return shell snippet to initialize CLAUDE_CONFIG_DIR from ~/.claude at clone creation time."""
        if "CLAUDE_CONFIG_DIR" not in effective_env:
            return ""
        raw_val = effective_env["CLAUDE_CONFIG_DIR"]
        target_path = raw_val.replace("{{ATB_DATA_DIR}}", str(data_dir))
        target_quoted = shlex.quote(target_path)
        return textwrap.dedent(f"""\
            if [ -d "$HOME/.claude" ] && [ ! -d {target_quoted} ]; then
                mkdir -p {target_quoted}
                cp -R "$HOME/.claude/." {target_quoted}/ 2>/dev/null || true
            fi
        """).strip() + "\n"

    @staticmethod
    def _build_symlink_whitelist_snippet(task: CloneTask) -> str:
        """Return a shell snippet that creates symlinks for items in symlink_whitelist."""
        whitelist = getattr(task.recipe, "symlink_whitelist", [])
        if not whitelist:
            return ""
        lines = []
        for item in whitelist:
            item_clean = item.strip().strip("/")
            if not item_clean:
                continue
            item_quoted = shlex.quote(item_clean)
            lines.append(
                f'    if [ ! -e "$HOME"/{item_quoted} ] && [ -e "$REAL_USER_HOME"/{item_quoted} ]; then\n'
                f'        mkdir -p "$(dirname "$HOME"/{item_quoted})"\n'
                f'        ln -s "$REAL_USER_HOME"/{item_quoted} "$HOME"/{item_quoted} 2>/dev/null || true\n'
                f'    fi'
            )
        return "\n".join(lines)


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

        effective_env = dict(task.recipe.environment_injection)
        env_vars = "\n".join([
            f"export {k}={shlex.quote(v.replace('{{ATB_DATA_DIR}}', str(task.data_dir)))}"
            for k, v in effective_env.items()
        ])
        codex_init_cmd = cls._build_codex_init_cmd(effective_env, task.data_dir)
        gemini_init_cmd = cls._build_gemini_init_cmd(effective_env, task.data_dir)
        claude_init_cmd = cls._build_claude_init_cmd(effective_env, task.data_dir)

        args_list = cls._combine_launch_args(valid_launch_args, lang_args, task.data_dir)

        args_str = f" {' '.join(args_list)}" if args_list else ""
        exec_cmd = f'exec {src_bin}{args_str} "$@"'

        symlink_snippet = cls._build_symlink_whitelist_snippet(task)
        if symlink_snippet:
            symlink_snippet_block = f"\n{symlink_snippet}"
        else:
            symlink_snippet_block = ""

        proxy_env = cls._build_proxy_env(task)
        wrapper_lines = ["#!/bin/bash", 'REAL_USER_HOME="$HOME"']
        if env_vars:
            wrapper_lines.append(env_vars)
        if lang_env:
            wrapper_lines.append(lang_env)
        if proxy_env:
            wrapper_lines.append(proxy_env)
        wrapper_lines.extend([
            'REAL_USER_HOME="${REAL_USER_HOME:-$HOME}"',
            'if [ -n "$HOME" ] && [ "$HOME" != "$REAL_USER_HOME" ]; then',
            '    mkdir -p "$HOME/Library/Preferences"',
            '    if [ ! -f "$HOME/Library/Preferences/.GlobalPreferences.plist" ] && [ -f "$REAL_USER_HOME/Library/Preferences/.GlobalPreferences.plist" ]; then',
            '        cp "$REAL_USER_HOME/Library/Preferences/.GlobalPreferences.plist" "$HOME/Library/Preferences/.GlobalPreferences.plist" 2>/dev/null || true',
            '    fi',
            '    if [ ! -f "$HOME/.CFUserTextEncoding" ] && [ -f "$REAL_USER_HOME/.CFUserTextEncoding" ]; then',
            '        cp "$REAL_USER_HOME/.CFUserTextEncoding" "$HOME/.CFUserTextEncoding" 2>/dev/null || true',
            '    fi',
            '    if [ ! -e "$HOME/Library/Keychains" ] && [ -e "$REAL_USER_HOME/Library/Keychains" ]; then',
            '        mkdir -p "$HOME/Library"',
            '        ln -s "$REAL_USER_HOME/Library/Keychains" "$HOME/Library/Keychains" 2>/dev/null || true',
            '    fi' + symlink_snippet_block,
            'fi',
            'if [ -n "$CODEX_HOME" ] && [ "$CODEX_HOME" != "$REAL_USER_HOME/.codex" ]; then',
            '    mkdir -p "$CODEX_HOME" 2>/dev/null || true',
            '    if [ -d "$REAL_USER_HOME/.codex" ] && [ -z "$(ls -A "$CODEX_HOME" 2>/dev/null)" ]; then',
            '        cp -R "$REAL_USER_HOME/.codex/." "$CODEX_HOME/" 2>/dev/null || true',
            '    fi',
            'fi',
            '_TARGET_GEMINI_DIR="${GEMINI_HOME:-${ANTIGRAVITY_HOME:-$GEMINI_CONFIG_DIR}}"',
            'if [ -n "$_TARGET_GEMINI_DIR" ] && [ "$_TARGET_GEMINI_DIR" != "$REAL_USER_HOME/.gemini" ]; then',
            '    mkdir -p "$_TARGET_GEMINI_DIR" 2>/dev/null || true',
            '    if [ -d "$REAL_USER_HOME/.gemini" ] && [ -z "$(ls -A "$_TARGET_GEMINI_DIR" 2>/dev/null)" ]; then',
            '        cp -R "$REAL_USER_HOME/.gemini/." "$_TARGET_GEMINI_DIR/" 2>/dev/null || true',
            '    fi',
            'fi',
            'if [ -n "$CLAUDE_CONFIG_DIR" ] && [ "$CLAUDE_CONFIG_DIR" != "$REAL_USER_HOME/.claude" ]; then',
            '    mkdir -p "$CLAUDE_CONFIG_DIR" 2>/dev/null || true',
            '    if [ -d "$REAL_USER_HOME/.claude" ] && [ -z "$(ls -A "$CLAUDE_CONFIG_DIR" 2>/dev/null)" ]; then',
            '        cp -R "$REAL_USER_HOME/.claude/." "$CLAUDE_CONFIG_DIR/" 2>/dev/null || true',
            '    fi',
            'fi',
            'mkdir -p "$HOME" "$TMPDIR" 2>/dev/null || true',
            exec_cmd,
        ])
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
{codex_init_cmd}{gemini_init_cmd}{claude_init_cmd}# Copy Resources dir so the app icon (.icns) and other assets are available

if [ -d {src_resources} ]; then
    cp -R {src_resources} {dst_resources}
fi
cp {src_plist} {dst_plist}
chmod -R u+w {dst_app} 2>/dev/null || true
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
            # Patch ProcessSingleton in embedded frameworks if present (e.g. Feishu/Lark, ChatGPT)
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
                for pos in range(found_pc - 4, max(0, found_pc - 300), -4):
                    w, = struct.unpack_from("<I", data, pos)
                    if (w & 0xFFE0001F) == 0x7100001F:
                        cmp_pos = pos
                        break
                if cmp_pos is None:
                    continue
                for pos in range(cmp_pos - 4, max(0, cmp_pos - 40), -4):
                    w_bl, = struct.unpack_from("<I", data, pos)
                    if (w_bl & 0xFC000000) == 0x94000000:
                        imm26 = w_bl & 0x03FFFFFF
                        if imm26 & (1 << 25): imm26 -= (1 << 26)
                        bl_target = pos + (imm26 << 2)
                        if 0 <= bl_target < len(data) - 8:
                            struct.pack_into("<II", data, bl_target, 0x52800000, 0xD65F03C0)
                        struct.pack_into("<II", data, pos, 0x52800000, 0xD503201F)
                        with open(fpath, "wb") as f:
                            f.write(data)
                        break
            except Exception:
                pass
' 2>/dev/null || true
        """)

    @classmethod
    def _build_cef_patch_cmd(cls, dest_path: Path) -> str:
        """Patch Chromium Embedded Framework to disable Seatbelt sandbox and set no_sandbox=1."""
        dest_quoted = shlex.quote(str(dest_path))
        return textwrap.dedent(f"""\
            # Patch CEF framework no_sandbox and bypass child process Seatbelt sandbox if present
            python3 -c '
import os
dst = {dest_quoted}
cef_path = os.path.join(dst, "Contents", "Frameworks", "Chromium Embedded Framework.framework", "Versions", "A", "Chromium Embedded Framework")
if not os.path.exists(cef_path):
    cef_path = os.path.join(dst, "Contents", "Frameworks", "Chromium Embedded Framework.framework", "Chromium Embedded Framework")
if os.path.exists(cef_path) and not os.path.islink(cef_path):
    try:
        with open(cef_path, "rb") as f:
            data = bytearray(f.read())
        # 1. Patch cef_initialize settings copy to force no_sandbox = 1
        needle1 = bytes.fromhex("f50302aaf30301aaf40300aa080840b9280800b9")
        pos1 = data.find(needle1)
        if pos1 != -1:
            patch_off1 = pos1 + 12
            if data[patch_off1:patch_off1+4] == bytes.fromhex("080840b9"):
                data[patch_off1:patch_off1+4] = bytes.fromhex("28008052")
        # 2. Patch ChildProcessLauncherHelper to bypass Seatbelt sandbox branches
        needle2 = bytes.fromhex("010a005448260035e8c343391f05007180250054")
        pos2 = data.find(needle2)
        if pos2 != -1:
            data[pos2+4:pos2+8] = bytes.fromhex("1f2003d5")
            data[pos2+16:pos2+20] = bytes.fromhex("1f2003d5")
        # 3. Patch ChildProcessLauncherHelper Seatbelt compile entry to directly branch to launch
        needle3 = bytes.fromhex("e00315aae4010094f80300aa40e5054f")
        pos3 = data.find(needle3)
        if pos3 != -1:
            data[pos3:pos3+4] = bytes.fromhex("34000014")
        # 4. Patch FallBackToNextGpuMode FATAL abort ("GPU process isn'\''t usable. Goodbye.") to safe return
        needle4 = bytes.fromhex("ff4305d1f44f13a9fd7b14a9fd030591")
        pos4 = data.find(needle4)
        if pos4 != -1:
            data[pos4:pos4+4] = bytes.fromhex("d0ffff17")
        with open(cef_path, "wb") as f:
            f.write(data)
    except Exception:
        pass
' 2>/dev/null || true
        """)

    @staticmethod
    def _build_symlink_whitelist_snippet(task: CloneTask) -> str:
        """Return a shell snippet that creates symlinks for items in symlink_whitelist."""
        whitelist = getattr(task.recipe, "symlink_whitelist", [])
        if not whitelist:
            return ""
        lines = []
        for item in whitelist:
            item_clean = item.strip().strip("/")
            if not item_clean:
                continue
            item_quoted = shlex.quote(item_clean)
            lines.append(
                f'    if [ ! -e "$HOME"/{item_quoted} ] && [ -e "$REAL_USER_HOME"/{item_quoted} ]; then\n'
                f'        mkdir -p "$(dirname "$HOME"/{item_quoted})"\n'
                f'        ln -s "$REAL_USER_HOME"/{item_quoted} "$HOME"/{item_quoted} 2>/dev/null || true\n'
                f'    fi'
            )
        return "\n".join(lines)

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
                    for pos in range(found_pc - 4, max(0, found_pc - 300), -4):
                        (w,) = struct.unpack_from("<I", data, pos)
                        if (w & 0xFFE0001F) == 0x7100001F:
                            cmp_pos = pos
                            break

                    if cmp_pos is None:
                        continue

                    for pos in range(cmp_pos - 4, max(0, cmp_pos - 40), -4):
                        (w_bl,) = struct.unpack_from("<I", data, pos)
                        if (w_bl & 0xFC000000) == 0x94000000:
                            imm26 = w_bl & 0x03FFFFFF
                            if imm26 & (1 << 25):
                                imm26 -= 1 << 26
                            bl_target = pos + (imm26 << 2)
                            if 0 <= bl_target < len(data) - 8:
                                struct.pack_into("<II", data, bl_target, 0x52800000, 0xD65F03C0)
                            struct.pack_into("<II", data, pos, 0x52800000, 0xD503201F)
                            with open(fpath, "wb") as f:
                                f.write(data)
                            patched_any = True
                            break
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

        codex_init_cmd = cls._build_codex_init_cmd(effective_env, task.data_dir)
        gemini_init_cmd = cls._build_gemini_init_cmd(effective_env, task.data_dir)
        claude_init_cmd = cls._build_claude_init_cmd(effective_env, task.data_dir)

        # Inject launch_args (e.g. --user-data-dir=... for Chromium apps)
        args_list = cls._combine_launch_args(valid_launch_args, lang_args, task.data_dir)

        args_str = f" {' '.join(args_list)}" if args_list else ""

        symlink_snippet = cls._build_symlink_whitelist_snippet(task)
        if symlink_snippet:
            symlink_snippet_block = f"\n{symlink_snippet}"
        else:
            symlink_snippet_block = ""

        wrapper_lines = [
            "#!/bin/bash",
            'REAL_USER_HOME="$HOME"',
        ]
        if env_vars:
            wrapper_lines.append(env_vars)
        if lang_env:
            wrapper_lines.append(lang_env)
        if proxy_env:
            wrapper_lines.append(proxy_env)

        wrapper_lines.extend([
            'REAL_USER_HOME="${REAL_USER_HOME:-$HOME}"',
            'mkdir -p "$HOME" "$TMPDIR" 2>/dev/null || true',
            'if [ -n "$HOME" ] && [ "$HOME" != "$REAL_USER_HOME" ]; then',
            '    mkdir -p "$HOME/Library/Preferences"',
            '    if [ ! -f "$HOME/Library/Preferences/.GlobalPreferences.plist" ] && [ -f "$REAL_USER_HOME/Library/Preferences/.GlobalPreferences.plist" ]; then',
            '        cp "$REAL_USER_HOME/Library/Preferences/.GlobalPreferences.plist" "$HOME/Library/Preferences/.GlobalPreferences.plist" 2>/dev/null || true',
            '    fi',
            '    if [ ! -f "$HOME/.CFUserTextEncoding" ] && [ -f "$REAL_USER_HOME/.CFUserTextEncoding" ]; then',
            '        cp "$REAL_USER_HOME/.CFUserTextEncoding" "$HOME/.CFUserTextEncoding" 2>/dev/null || true',
            '    fi',
            '    if [ ! -e "$HOME/Library/Keychains" ] && [ -e "$REAL_USER_HOME/Library/Keychains" ]; then',
            '        mkdir -p "$HOME/Library"',
            '        ln -s "$REAL_USER_HOME/Library/Keychains" "$HOME/Library/Keychains" 2>/dev/null || true',
            '    fi' + symlink_snippet_block,
            'fi',
            'if [ -n "$CODEX_HOME" ] && [ "$CODEX_HOME" != "$REAL_USER_HOME/.codex" ]; then',
            '    mkdir -p "$CODEX_HOME" 2>/dev/null || true',
            '    if [ -d "$REAL_USER_HOME/.codex" ] && [ -z "$(ls -A "$CODEX_HOME" 2>/dev/null)" ]; then',
            '        cp -R "$REAL_USER_HOME/.codex/." "$CODEX_HOME/" 2>/dev/null || true',
            '    fi',
            'fi',
            '_TARGET_GEMINI_DIR="${GEMINI_HOME:-${ANTIGRAVITY_HOME:-$GEMINI_CONFIG_DIR}}"',
            'if [ -n "$_TARGET_GEMINI_DIR" ] && [ "$_TARGET_GEMINI_DIR" != "$REAL_USER_HOME/.gemini" ]; then',
            '    mkdir -p "$_TARGET_GEMINI_DIR" 2>/dev/null || true',
            '    if [ -d "$REAL_USER_HOME/.gemini" ] && [ -z "$(ls -A "$_TARGET_GEMINI_DIR" 2>/dev/null)" ]; then',
            '        cp -R "$REAL_USER_HOME/.gemini/." "$_TARGET_GEMINI_DIR/" 2>/dev/null || true',
            '    fi',
            'fi',
            'if [ -n "$CLAUDE_CONFIG_DIR" ] && [ "$CLAUDE_CONFIG_DIR" != "$REAL_USER_HOME/.claude" ]; then',
            '    mkdir -p "$CLAUDE_CONFIG_DIR" 2>/dev/null || true',
            '    if [ -d "$REAL_USER_HOME/.claude" ] && [ -z "$(ls -A "$CLAUDE_CONFIG_DIR" 2>/dev/null)" ]; then',
            '        cp -R "$REAL_USER_HOME/.claude/." "$CLAUDE_CONFIG_DIR/" 2>/dev/null || true',
            '    fi',
            'fi',
            f'exec "$(dirname "$0")/{orig_bin_name}.bin"{args_str} "$@"',
        ])
        wrapper_body = "\n".join(wrapper_lines)

        # Build framework singleton patcher command ONLY when explicitly enabled by recipe
        # or when cloning Feishu/Lark which requires custom ProcessSingleton handling.
        needs_singleton_patch = (
            getattr(task.recipe, "patch_framework_singleton", False)
            or getattr(task.source, "bundle_id", "") == "com.electron.lark"
        )
        singleton_patch_cmd = (
            cls._build_singleton_patch_cmd(task.dest_path)
            if needs_singleton_patch
            else ""
        )

        # Build CEF patcher command ONLY when explicitly enabled by recipe
        needs_cef_patch = bool(getattr(task.recipe, "patch_cef", False))
        cef_patch_cmd = (
            cls._build_cef_patch_cmd(task.dest_path)
            if needs_cef_patch
            else ""
        )

        if needs_cef_patch:
            helper_bundle_id_cmd = f"""if [ -d {dst}/Contents/Frameworks ]; then
    find {dst}/Contents/Frameworks -name "*.app" -type d 2>/dev/null | while read -r helper_app; do
        h_plist="$helper_app/Contents/Info.plist"
        if [ -f "$h_plist" ]; then
            cur_id=$(/usr/libexec/PlistBuddy -c "Print :CFBundleIdentifier" "$h_plist" 2>/dev/null || true)
            if [[ "$cur_id" =~ ^[A-Z0-9]{{10}}\\. ]]; then
                new_id=$(echo "$cur_id" | sed -E 's/^[A-Z0-9]{{10}}\\.//')
                /usr/libexec/PlistBuddy -c "Set :CFBundleIdentifier $new_id.{task.new_bundle_id}" "$h_plist" 2>/dev/null || true
            fi
        fi
    done
fi
"""
        else:
            helper_bundle_id_cmd = ""

        if task.recipe.strip_sandbox:
            strip_sandbox_snippet = (
                '/usr/libexec/PlistBuddy -c "Delete :com.apple.security.app-sandbox" "$ent_plist" 2>/dev/null || true\n'
                '    /usr/libexec/PlistBuddy -c "Delete :com.apple.security.application-groups" "$ent_plist" 2>/dev/null || true\n'
                '    /usr/libexec/PlistBuddy -c "Delete :com.apple.developer.team-identifier" "$ent_plist" 2>/dev/null || true\n'
                '    /usr/libexec/PlistBuddy -c "Delete :com.apple.developer.aps-environment" "$ent_plist" 2>/dev/null || true\n'
                '    /usr/libexec/PlistBuddy -c "Delete :com.apple.application-identifier" "$ent_plist" 2>/dev/null || true\n'
                '    /usr/libexec/PlistBuddy -c "Delete :keychain-access-groups" "$ent_plist" 2>/dev/null || true\n'
                '    /usr/libexec/PlistBuddy -c "Delete :com.apple.developer.associated-domains" "$ent_plist" 2>/dev/null || true\n'
                '    /usr/libexec/PlistBuddy -c "Delete :com.apple.developer.icloud-container-identifiers" "$ent_plist" 2>/dev/null || true\n'
                '    /usr/libexec/PlistBuddy -c "Delete :com.apple.developer.ubiquity-container-identifiers" "$ent_plist" 2>/dev/null || true\n'
            )
        else:
            strip_sandbox_snippet = ""

        codesign_cmds = (
            f"ent_plist=$(mktemp /tmp/atb_ent_XXXXXX.plist)\n"
            f"codesign -d --entitlements - --xml {src} > \"$ent_plist\" 2>/dev/null || true\n"
            f"if [ -s \"$ent_plist\" ]; then\n"
            f"    {strip_sandbox_snippet}"
            f"    find {dst} -type f \\( -name '*.dylib' -o -name '*.so' \\) -exec codesign --force --sign - {{}} + 2>/dev/null || true\n"
            f"    find {dst}/Contents -name '*.app' -type d -exec codesign --force --deep --sign - --entitlements \"$ent_plist\" {{}} + 2>/dev/null || true\n"
            f"    find {dst}/Contents -name '*.framework' -type d -exec codesign --force --deep --sign - {{}} + 2>/dev/null || true\n"
            f"    find {dst}/Contents -type f -perm +111 | while read -r bin_file; do if file \"$bin_file\" 2>/dev/null | grep -q 'Mach-O'; then codesign --force --sign - --entitlements \"$ent_plist\" \"$bin_file\" 2>/dev/null || true; fi; done\n"
            f"    codesign --force --deep --sign - --entitlements \"$ent_plist\" {dst}\n"
            f"else\n"
            f"    codesign --force --deep --sign - {dst}\n"
            f"fi\n"
            f'rm -f "$ent_plist"\n'
        )

        script = f"""set -e
mkdir -p {dst_parent}
mkdir -p {data_dir}
rm -rf {dst}
{codex_init_cmd}{gemini_init_cmd}{claude_init_cmd}cp -R {src} {dst}

chmod -R u+w {dst} 2>/dev/null || true
/usr/libexec/PlistBuddy -c "Set :CFBundleIdentifier {task.new_bundle_id}" {dst_plist}
{helper_bundle_id_cmd}{display_name_cmd}
{icon_cmd}mv {bin_orig} {bin_bak}
cat << 'WRAPPER_EOF' > {wrapper}
{wrapper_body}
WRAPPER_EOF
chmod +x {wrapper}
{singleton_patch_cmd}{cef_patch_cmd}xattr -cr {dst} 2>/dev/null || true
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

