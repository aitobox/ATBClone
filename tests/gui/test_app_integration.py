import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
import toga

from atbclone.gui.app import ATBCloneApp


def test_app_creation_and_routing():
    app = ATBCloneApp("ATBClone", "com.atbclone.app")
    app.startup()

    assert app.main_window is not None
    assert app.clone_view is not None
    assert app.recipe_view is not None
    assert app.probe_view is not None
    assert app.doctor_view is not None

    # Test route switching
    app.switch_view("recipes")
    assert app.current_view_name == "recipes"

    app.switch_view("probe")
    assert app.current_view_name == "probe"

    app.switch_view("doctor")
    assert app.current_view_name == "doctor"

    app.switch_view("logs")
    assert app.current_view_name == "logs"

    app.switch_view("settings")
    assert app.current_view_name == "settings"

    app.switch_view("clones")
    assert app.current_view_name == "clones"

