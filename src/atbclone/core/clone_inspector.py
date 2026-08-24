"""Clone inspector for resolving injected launch parameters and environment variables."""

from dataclasses import dataclass, field
from pathlib import Path
import plistlib
import re
import shlex

from atbclone.core.locale import build_language_wrapper_snippet, resolve_language_config
from atbclone.core.logger import get_logger
from atbclone.core.state import CloneRecord
from atbclone.recipes.loader import RecipeLoader

logger = get_logger("core.clone_inspector")


@dataclass
class InjectedDetails:
    launch_args: list[str] = field(default_factory=list)
    env_vars: dict[str, str] = field(default_factory=dict)
    exec_command: str = ""
    source_type: str = "recipe_fallback"  # "wrapper_script" | "recipe_fallback"


class CloneInspector:
    """Extracts and resolves runtime injected launch arguments, environment variables, and exec commands."""

    @classmethod
    def inspect(cls, record: CloneRecord) -> InjectedDetails:
        """Inspect a clone record, trying on-disk wrapper script first and falling back to recipe reconstruction."""
        dest_path = Path(record.dest_path)
        macos_dir = dest_path / "Contents" / "MacOS"

        if macos_dir.exists() and macos_dir.is_dir():
            candidates: list[Path] = []

            # 1. Try resolving main executable name from Info.plist first
            plist_path = dest_path / "Contents" / "Info.plist"
            if plist_path.is_file():
                try:
                    with plist_path.open("rb") as f:
                        plist_data = plistlib.load(f)
                    exe_name = plist_data.get("CFBundleExecutable")
                    if exe_name:
                        candidate = macos_dir / exe_name
                        if candidate.is_file():
                            candidates.append(candidate)
                except Exception as e:
                    logger.debug(f"Failed to read Info.plist for '{dest_path}': {e}")

            # 2. Add other candidate scripts in MacOS directory
            for child in macos_dir.iterdir():
                if (
                    child not in candidates
                    and child.is_file()
                    and not child.name.startswith(".")
                    and not child.name.endswith(".bin")
                ):
                    candidates.append(child)

            for target_file in candidates:
                if target_file.exists() and target_file.is_file():
                    try:
                        content = target_file.read_text(encoding="utf-8", errors="ignore")
                        if content.startswith("#!/bin/bash") or "exec " in content:
                            details = cls.parse_wrapper_script(content)
                            if details.exec_command or details.env_vars or details.launch_args:
                                return details
                    except Exception as e:
                        logger.debug(f"Failed to read wrapper script {target_file}: {e}")

        return cls.reconstruct_from_recipe(record)

    @classmethod
    def parse_wrapper_script(cls, script_content: str) -> InjectedDetails:
        """Parse bash wrapper script content to extract exports and exec command."""
        env_vars: dict[str, str] = {}
        launch_args: list[str] = []
        exec_command = ""

        for line in script_content.splitlines():
            line_str = line.strip()
            if line_str.startswith("export "):
                export_match = re.match(r"^export\s+([A-Za-z_][A-Za-z0-9_]*)=(.*)$", line_str)
                if export_match:
                    k, v = export_match.group(1), export_match.group(2).strip()
                    if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                        v = v[1:-1]
                    # Dereference simple variable reference like $HTTP_PROXY
                    if v.startswith("$") and v[1:] in env_vars:
                        v = env_vars[v[1:]]
                    env_vars[k] = v

            elif line_str.startswith("exec "):
                exec_command = line_str[5:].strip()
                try:
                    cleaned_cmd = re.sub(r'\s+"?\$@"?\s*$', "", exec_command).strip()
                    tokens = shlex.split(cleaned_cmd)
                    if tokens:
                        launch_args = tokens[1:]
                except Exception as e:
                    logger.debug(f"Failed to split exec command tokens: {e}")

        return InjectedDetails(
            launch_args=launch_args,
            env_vars=env_vars,
            exec_command=exec_command,
            source_type="wrapper_script",
        )

    @classmethod
    def reconstruct_from_recipe(cls, record: CloneRecord) -> InjectedDetails:
        """Fallback reconstruction using Recipe and CloneRecord properties."""
        recipe = RecipeLoader.match(record.bundle_id)
        env_vars: dict[str, str] = {}
        launch_args: list[str] = []

        # 1. Environment injection from recipe
        for k, v in recipe.environment_injection.items():
            env_vars[k] = v.replace("{{ATB_DATA_DIR}}", record.data_dir)

        # 2. Language settings
        app_type = recipe.app_type or "cocoa"
        _, lang_args = build_language_wrapper_snippet(record.language, app_type=app_type)
        cfg = resolve_language_config(record.language)
        env_vars["LANG"] = cfg.posix_lang
        env_vars["LC_ALL"] = cfg.posix_lang

        # 3. Proxy
        if record.proxy_enabled and record.proxy_summary:
            env_vars["HTTP_PROXY"] = record.proxy_summary
            env_vars["HTTPS_PROXY"] = record.proxy_summary
            env_vars["http_proxy"] = record.proxy_summary
            env_vars["https_proxy"] = record.proxy_summary

        # 4. Launch args from recipe + lang args
        for arg in recipe.launch_args:
            launch_args.append(arg.replace("{{ATB_DATA_DIR}}", record.data_dir))
        launch_args.extend(lang_args)

        # 5. Exec command estimate
        src_bin = f"{record.source_path}/Contents/MacOS/{record.source_app}"
        args_str = f" {' '.join(shlex.quote(a) for a in launch_args)}" if launch_args else ""
        exec_command = f'exec "{src_bin}"{args_str} "$@"'

        return InjectedDetails(
            launch_args=launch_args,
            env_vars=env_vars,
            exec_command=exec_command,
            source_type="recipe_fallback",
        )
