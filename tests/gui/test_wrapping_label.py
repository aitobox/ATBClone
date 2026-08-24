"""Unit tests for WrappingLabel component and ProbeView auto-wrapping behavior."""

import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch
import pytest
import toga
from toga.style import Pack
from toga.style.pack import COLUMN

from atbclone.core.app_prober import ProbeResult
from atbclone.core.models import AppInfo
from atbclone.recipes.models import Recipe
from atbclone.gui.components.wrapping_label import WrappingLabel
from atbclone.gui.patch_cocoa import configure_cocoa_wrapping_label
from atbclone.gui.services.probe_service import ProbeService
from atbclone.gui.services.recipe_service import RecipeService
from atbclone.gui.views.probe_view import ProbeView


def test_wrapping_label_init():
    label = WrappingLabel("Test label text", style=Pack(font_size=13))
    assert label.text == "Test label text"
    assert label.intrinsic.width is None


def test_wrapping_label_cocoa_configuration():
    label = WrappingLabel("Test Wrapping Cocoa Label")
    assert label.selectable is True
    if sys.platform == "darwin":
        native = getattr(getattr(label, "_impl", None), "native", None)
        if native is not None:
            cell = getattr(native, "cell", None)
            if cell is not None:
                assert cell.wraps is True
                assert cell.lineBreakMode == 0  # NSLineBreakByWordWrapping
                assert cell.isScrollable() is False
                assert cell.isSelectable() is True
            assert native.usesSingleLineMode is False
            assert native.maximumNumberOfLines == 0
            assert native.isSelectable() is True


def test_wrapping_label_non_selectable():
    label = WrappingLabel("Non selectable", selectable=False)
    assert label.selectable is False
    if sys.platform == "darwin":
        native = getattr(getattr(label, "_impl", None), "native", None)
        if native is not None:
            assert native.isSelectable() is False


def test_wrapping_label_dynamic_rehint():
    long_text = "ConfSDKdyn.framework, libwxocr.dylib, ilink2.framework, libEGL.dylib, roam_migration.framework, libmmmojo.dylib, libvlccore.dylib, usb.framework, roam_server.framework, WCDY.framework"
    label = WrappingLabel(f"Frameworks: {long_text}")
    assert label.intrinsic.width is None
    assert label.intrinsic.height is not None

    # Text update
    label.text = "Short text"
    assert label.intrinsic.width is None


def test_wrapping_label_target_width_calculation():
    label = WrappingLabel("Sample text")
    target_w = label._get_target_width()
    assert target_w >= 200.0


def test_configure_cocoa_wrapping_label_null_safe():
    # Should safely no-op on None or invalid objects
    configure_cocoa_wrapping_label(None)
    configure_cocoa_wrapping_label(object())


def test_probe_view_with_long_frameworks_and_notes(tmp_path):
    async def _test():
        probe_service = ProbeService()
        recipe_service = RecipeService(custom_recipes_dir=tmp_path / "recipes")
        view = ProbeView(probe_service=probe_service, recipe_service=recipe_service)

        long_fw_list = [
            "ConfSDKdyn.framework", "libwxocr.dylib", "ilink2.framework",
            "libEGL.dylib", "roam_migration.framework", "libmmmojo.dylib",
            "libvlccore.dylib", "usb.framework", "roam_server.framework",
            "WCDY.framework", "ilink_stream_channel.framework", "libwechatocr.dylib",
        ]
        long_reason = "Native macOS application (Sandboxed); requires binary wrapper hijack with HOME/TMPDIR isolation."

        mock_probe_result = ProbeResult(
            app_info=AppInfo(
                path=Path("/Applications/WeChat.app"),
                bundle_id="com.tencent.xinWeChat",
                app_name="WeChat",
                executable=Path("/Applications/WeChat.app/Contents/MacOS/WeChat"),
                has_sandbox=True,
            ),
            has_sandbox=True,
            frameworks=long_fw_list,
            strategy="hard_clone",
            reason=long_reason,
            recipe=Recipe(
                bundle_id="com.tencent.xinWeChat",
                app_name="WeChat",
                strategy="hard_clone",
                strip_sandbox=True,
            ),
        )

        with patch.object(probe_service, "probe_app", new=AsyncMock(return_value=mock_probe_result)):
            view.input_path.value = "/Applications/WeChat.app"
            await view.do_probe()

            # Verify that labels are WrappingLabel instances
            assert isinstance(view.label_frameworks, WrappingLabel)
            assert isinstance(view.label_reason, WrappingLabel)
            assert isinstance(view.label_app_name, WrappingLabel)
            assert isinstance(view.label_bundle_id, WrappingLabel)

            # Check that content was populated properly
            assert "ConfSDKdyn.framework" in view.label_frameworks.text
            assert "Native macOS application" in view.label_reason.text

            # Verify intrinsic width is unconstrained (None) so layout width is not stretched
            assert view.label_frameworks.intrinsic.width is None
            assert view.label_reason.intrinsic.width is None

    asyncio.run(_test())
