"""Pytest configuration and global fixtures for ATBClone test suite."""

import os
import pytest
from atbclone.core.i18n import set_language


@pytest.fixture(autouse=True)
def default_test_language(monkeypatch):
    """Default test environment to English unless explicitly overridden by a test."""
    if "ATBCLONE_LANG" not in os.environ:
        monkeypatch.setenv("ATBCLONE_LANG", "en")
    set_language(None)
    yield
    set_language(None)
