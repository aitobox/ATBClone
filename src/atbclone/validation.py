"""Central input validation and shell-escaping helpers.

Every string that ATBClone interpolates into a generated shell script, an
AppleScript `do shell script` payload, or generated C source must pass through
this module (or be wrapped with ``shlex.quote``) before it reaches the engine.
The rules are deliberately strict: values that cannot be represented safely are
rejected with a clear error instead of being escaped aggressively.
"""

import re

# Reverse-DNS style bundle identifier: letters, digits, dots, hyphens, underscores.
# Anything else (quotes, spaces, "$", backticks, slashes...) can smuggle shell
# payloads through PlistBuddy / codesign command strings.
BUNDLE_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")

# Environment variable names accepted by setenv(3) / POSIX export.
ENV_KEY_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

# Proxy hostnames, IPv4 and bracketed IPv6 literals.
HOST_PATTERN = re.compile(r"^[A-Za-z0-9._:\[\]-]+$")

# Characters that never legitimately appear in names or paths we interpolate.
_FORBIDDEN_CTRL_PATTERN = re.compile(r"[\x00-\x1f\x7f]")

# Characters rejected in proxy credentials / no_proxy: they break the generated
# shell `export` lines, the embedded URL, or the generated C launcher source.
_PROXY_FORBIDDEN_PATTERN = re.compile(r"""["'`$\\\s\x00-\x1f\x7f]""")


def validate_bundle_id(value: str, *, field: str = "bundle_id") -> str:
    """Validate a bundle identifier; return it unchanged or raise ValueError.

    Applied to both source app identifiers read from Info.plist and generated
    clone identifiers, because both end up inside PlistBuddy command strings.
    """
    if not value or not BUNDLE_ID_PATTERN.match(value):
        raise ValueError(
            f"Invalid {field}: {value!r}. Expected a reverse-DNS identifier "
            f"(letters, digits, dots, hyphens, underscores only)."
        )
    return value


def validate_env_key(key: str) -> str:
    """Validate an environment variable name used in environment_injection."""
    if not ENV_KEY_PATTERN.match(key):
        raise ValueError(
            f"Invalid environment variable name: {key!r}. "
            f"Expected letters, digits and underscores, starting with a letter or underscore."
        )
    return key


def validate_clone_name(name: str) -> str:
    """Validate a clone name used to build destination paths.

    Path separators would let a name escape the output directory (path
    traversal), and NUL/control characters break the generated scripts.
    """
    if not name or not name.strip():
        raise ValueError("Clone name must not be empty.")
    if _FORBIDDEN_CTRL_PATTERN.search(name):
        raise ValueError(f"Clone name contains control characters: {name!r}.")
    if "/" in name or "\\" in name:
        raise ValueError(
            f"Clone name must not contain path separators: {name!r}."
        )
    if name in (".", ".."):
        raise ValueError(f"Clone name must not be {name!r}.")
    return name


def sanitize_name_component(name: str) -> str:
    """Sanitize an untrusted app/name string (e.g. CFBundleDisplayName from a
    cloned app's Info.plist) so it is safe to use as a single path component.

    Replaces path separators and control characters instead of raising, because
    app metadata is attacker-controlled and a hard failure here would block
    cloning entirely; the sanitized name keeps the clone functional.
    """
    cleaned = _FORBIDDEN_CTRL_PATTERN.sub("-", name.replace("\\", "-").replace("/", "-"))
    cleaned = cleaned.strip()
    if cleaned in ("", ".", ".."):
        cleaned = "-"
    return cleaned


def validate_display_name(name: str) -> str:
    """Validate a display name destined for CFBundleDisplayName.

    Arbitrary Unicode is allowed (it is escaped before reaching the shell), but
    control characters would break the single-line PlistBuddy commands.
    """
    if _FORBIDDEN_CTRL_PATTERN.search(name):
        raise ValueError(f"Display name contains control characters: {name!r}.")
    if not name.strip():
        raise ValueError("Display name must not be empty.")
    return name


def validate_path_component(path: str, *, field: str = "path") -> str:
    """Validate a filesystem path supplied by the user (data dir, output dir...).

    Such paths are shlex-quoted when interpolated, so most characters are safe;
    only control characters (which break the generated scripts themselves) are
    rejected.
    """
    if not path:
        raise ValueError(f"{field} must not be empty.")
    if _FORBIDDEN_CTRL_PATTERN.search(path):
        raise ValueError(f"{field} contains control characters: {path!r}.")
    return path


def escape_double_quoted(value: str) -> str:
    """Escape a value for interpolation inside a double-quoted shell string.

    Covers the full set of characters with special meaning inside double
    quotes: backslash, double quote, dollar and backtick. Suitable for values
    embedded into e.g. ``PlistBuddy -c "Set :Key {value}"`` commands.
    """
    return (
        value.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("$", "\\$")
        .replace("`", "\\`")
    )


def validate_host(host: str) -> str:
    """Validate a proxy host name or IP literal."""
    if not host or not HOST_PATTERN.match(host):
        raise ValueError(
            f"Invalid proxy host: {host!r}. Expected a hostname or IP literal "
            f"(letters, digits, dots, colons, hyphens, brackets only)."
        )
    return host


def validate_proxy_port(port: int) -> int:
    """Validate a proxy TCP port."""
    if not 1 <= port <= 65535:
        raise ValueError(f"Invalid proxy port: {port}. Expected 1-65535.")
    return port


def validate_proxy_credential(value: str, *, field: str = "credential") -> str:
    """Validate proxy username/password/no_proxy values.

    These values are embedded verbatim into generated `export` lines, the proxy
    URL persisted to clones.yaml, and the generated C launcher source; shell or
    C metacharacters are rejected outright.
    """
    if _PROXY_FORBIDDEN_PATTERN.search(value):
        raise ValueError(
            f"Invalid proxy {field}: {value!r}. Quotes, backslashes, dollar signs, "
            f"backticks and whitespace are not supported."
        )
    return value
