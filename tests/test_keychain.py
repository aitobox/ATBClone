import os
import subprocess
from unittest.mock import patch, MagicMock
import pytest

from atbclone.core.keychain import (
    DEFAULT_SERVICE,
    DEFAULT_ACCOUNT,
    get_clone_account,
    set_proxy_password,
    get_proxy_password,
    delete_proxy_password,
    save_clone_proxy_password,
    get_clone_proxy_password,
    delete_clone_proxy_password,
    save_default_proxy_password,
    get_default_proxy_password,
    delete_default_proxy_password,
    set_mock_mode,
    clear_mock_storage,
    is_mock_mode,
)


@pytest.fixture(autouse=True)
def setup_mock_keychain():
    set_mock_mode(True)
    clear_mock_storage()
    yield
    set_mock_mode(True)
    clear_mock_storage()


def test_clone_account_format():
    assert get_clone_account("test_clone") == "clone:test_clone"


def test_mock_keychain_crud():
    # Test setting and getting
    assert set_proxy_password("account1", "pass123") is True
    assert get_proxy_password("account1") == "pass123"

    # Test updating
    assert set_proxy_password("account1", "pass456") is True
    assert get_proxy_password("account1") == "pass456"

    # Test non-existent
    assert get_proxy_password("unknown") is None

    # Test setting empty password deletes it
    assert set_proxy_password("account1", "") is True
    assert get_proxy_password("account1") is None


def test_mock_keychain_delete():
    set_proxy_password("account_del", "secret")
    assert get_proxy_password("account_del") == "secret"
    assert delete_proxy_password("account_del") is True
    assert get_proxy_password("account_del") is None
    # Deleting non-existent returns True
    assert delete_proxy_password("account_del") is True


def test_clone_helpers():
    clone_name = "MyDiscord"
    assert save_clone_proxy_password(clone_name, "p@ssword!") is True
    assert get_clone_proxy_password(clone_name) == "p@ssword!"
    assert delete_clone_proxy_password(clone_name) is True
    assert get_clone_proxy_password(clone_name) is None


def test_default_helpers():
    assert save_default_proxy_password("global_secret") is True
    assert get_default_proxy_password() == "global_secret"
    assert delete_default_proxy_password() is True
    assert get_default_proxy_password() is None


@patch("subprocess.run")
def test_real_keychain_subprocess_calls(mock_run):
    set_mock_mode(False)
    try:
        # Mock add-generic-password
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        assert set_proxy_password("real_user", "real_pass") is True
        mock_run.assert_called_with(
            [
                "/usr/bin/security",
                "add-generic-password",
                "-a",
                "real_user",
                "-s",
                DEFAULT_SERVICE,
                "-w",
                "real_pass",
                "-U",
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        # Mock find-generic-password success
        mock_run.return_value = MagicMock(returncode=0, stdout="real_pass\n", stderr="")
        assert get_proxy_password("real_user") == "real_pass"

        # Mock find-generic-password not found (code 44)
        mock_run.return_value = MagicMock(returncode=44, stdout="", stderr="Item not found")
        assert get_proxy_password("missing_user") is None

        # Mock delete-generic-password
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        assert delete_proxy_password("real_user") is True
    finally:
        set_mock_mode(True)
