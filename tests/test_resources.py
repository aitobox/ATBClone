from pathlib import Path
import pytest
from atbclone.core.resources import get_resource_dir, get_resource_path, get_app_icon_path


def test_get_resource_dir_exists():
    res_dir = get_resource_dir()
    assert res_dir.exists()
    assert res_dir.is_dir()


def test_get_resource_path_resolves_logo():
    png_path = get_resource_path("images/logo.png")
    assert png_path.exists()
    assert png_path.name == "logo.png"


def test_get_app_icon_path_png():
    icon_path = get_app_icon_path("png")
    assert icon_path is not None
    assert icon_path.exists()
    assert icon_path.suffix == ".png"


def test_get_app_icon_path_icns():
    icon_path = get_app_icon_path("icns")
    assert icon_path is not None
    assert icon_path.exists()
    assert icon_path.suffix == ".icns"


def test_get_app_icon_path_invalid_format():
    icon_path = get_app_icon_path("invalid_format")
    # Falls back to png or icns if exists
    assert icon_path is not None
    assert icon_path.exists()
