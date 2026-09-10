"""macOS Keychain Services integration for secure proxy credential storage."""

import os
import subprocess
import sys
from atbclone.core.logger import get_logger

logger = get_logger("core.keychain")

DEFAULT_SERVICE = "atbclone.proxy"
DEFAULT_ACCOUNT = "default"

_MOCK_STORAGE: dict[tuple[str, str], str] = {}
_FORCE_MOCK: bool | None = None


def is_mock_mode() -> bool:
    """Check whether keychain operations should use in-memory mock storage."""
    if _FORCE_MOCK is not None:
        return _FORCE_MOCK
    return (
        sys.platform != "darwin"
        or "PYTEST_CURRENT_TEST" in os.environ
        or os.environ.get("ATBCLONE_MOCK_KEYCHAIN") == "1"
    )


def set_mock_mode(enabled: bool | None) -> None:
    """Explicitly enable or disable mock mode (primarily for testing)."""
    global _FORCE_MOCK
    _FORCE_MOCK = enabled


def clear_mock_storage() -> None:
    """Clear all in-memory mock credentials."""
    _MOCK_STORAGE.clear()


def get_clone_account(clone_name: str) -> str:
    """Generate standardized keychain account name for a clone."""
    return f"clone:{clone_name}"


def set_proxy_password(account: str, password: str, service: str = DEFAULT_SERVICE) -> bool:
    """Store or update a proxy password in macOS Keychain."""
    if not password:
        return delete_proxy_password(account, service)

    if is_mock_mode():
        _MOCK_STORAGE[(service, account)] = password
        return True

    cmd = [
        "/usr/bin/security",
        "add-generic-password",
        "-a",
        account,
        "-s",
        service,
        "-w",
        password,
        "-U",
    ]
    try:
        res = subprocess.run(cmd, check=False, capture_output=True, text=True)
        if res.returncode != 0:
            logger.warning(
                f"Failed to save password in Keychain for '{account}' (code {res.returncode}): {res.stderr.strip()}"
            )
            return False
        return True
    except Exception as e:
        logger.error(f"Error executing security command for '{account}': {e}")
        return False


def get_proxy_password(account: str, service: str = DEFAULT_SERVICE) -> str | None:
    """Retrieve a proxy password from macOS Keychain."""
    if is_mock_mode():
        return _MOCK_STORAGE.get((service, account))

    cmd = [
        "/usr/bin/security",
        "find-generic-password",
        "-a",
        account,
        "-s",
        service,
        "-w",
    ]
    try:
        res = subprocess.run(cmd, check=False, capture_output=True, text=True)
        if res.returncode == 0:
            return res.stdout.rstrip("\r\n")
        elif res.returncode == 44:
            # Item not found in keychain
            return None
        else:
            logger.debug(
                f"Keychain lookup for '{account}' returned code {res.returncode}: {res.stderr.strip()}"
            )
            return None
    except Exception as e:
        logger.error(f"Error reading password from Keychain for '{account}': {e}")
        return None


def delete_proxy_password(account: str, service: str = DEFAULT_SERVICE) -> bool:
    """Delete a proxy password from macOS Keychain."""
    if is_mock_mode():
        _MOCK_STORAGE.pop((service, account), None)
        return True

    cmd = [
        "/usr/bin/security",
        "delete-generic-password",
        "-a",
        account,
        "-s",
        service,
    ]
    try:
        res = subprocess.run(cmd, check=False, capture_output=True, text=True)
        # 0 = deleted successfully, 44 = item not found (already absent)
        if res.returncode in (0, 44):
            return True
        logger.warning(
            f"Failed to delete password from Keychain for '{account}' (code {res.returncode}): {res.stderr.strip()}"
        )
        return False
    except Exception as e:
        logger.error(f"Error deleting password from Keychain for '{account}': {e}")
        return False


def save_clone_proxy_password(clone_name: str, password: str) -> bool:
    """Save proxy password for a specific clone."""
    return set_proxy_password(get_clone_account(clone_name), password)


def get_clone_proxy_password(clone_name: str) -> str | None:
    """Get proxy password for a specific clone."""
    return get_proxy_password(get_clone_account(clone_name))


def delete_clone_proxy_password(clone_name: str) -> bool:
    """Delete proxy password for a specific clone."""
    return delete_proxy_password(get_clone_account(clone_name))


def save_default_proxy_password(password: str) -> bool:
    """Save global default proxy password."""
    return set_proxy_password(DEFAULT_ACCOUNT, password)


def get_default_proxy_password() -> str | None:
    """Get global default proxy password."""
    return get_proxy_password(DEFAULT_ACCOUNT)


def delete_default_proxy_password() -> bool:
    """Delete global default proxy password."""
    return delete_proxy_password(DEFAULT_ACCOUNT)
