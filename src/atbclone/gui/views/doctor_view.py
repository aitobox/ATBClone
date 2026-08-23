"""Doctor Environment Check View with modern TopHeaderBar."""

import asyncio
from typing import Optional
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER

from atbclone.core.i18n import t
from atbclone.core.logger import get_logger
from atbclone.gui.services.doctor_service import DoctorService
from atbclone.gui.components.top_bar import TopHeaderBar
from atbclone.gui.theme import Theme

logger = get_logger("gui.doctor_view")


class DoctorView(toga.Box):
    """View presenting system prerequisites, toolchain availability, and diagnostic advice."""

    def __init__(self, doctor_service: Optional[DoctorService] = None, app: Optional[toga.App] = None):
        super().__init__(style=Pack(direction=COLUMN, flex=1, background_color=Theme.BG_WINDOW))
        self.doctor_service = doctor_service or DoctorService()
        self.app_instance = app

        # Top Header Bar
        self.top_bar = TopHeaderBar(
            title=t("nav_doctor"),
            action_label=t("doctor_btn_recheck"),
            on_action=lambda w: asyncio.create_task(self.run_checks()),
        )
        self.add(self.top_bar)

        content_box = toga.Box(style=Pack(direction=COLUMN, margin=(0, 24, 20, 24), flex=1))
        self.add(content_box)

        # Summary badge card
        self.card_summary = toga.Box(style=Pack(direction=COLUMN, margin_bottom=14, background_color=Theme.BG_CARD))
        inner_summary = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin=(14, 18, 14, 18), flex=1))
        self.label_summary = toga.Label(t("doctor_summary_initial"), style=Pack(font_weight="bold", font_size=15, flex=1, color=Theme.TEXT_PRIMARY))
        inner_summary.add(self.label_summary)

        # One-click install Xcode Command Line Tools button
        self.btn_install_xcode = toga.Button(
            t("doctor_btn_install_xcode"),
            on_press=lambda w: asyncio.create_task(self.action_install_xcode(w)),
            style=Pack(
                height=32,
                font_size=13,
                font_weight="bold",
                margin_left=12,
                visibility="hidden",
            ),
        )
        inner_summary.add(self.btn_install_xcode)

        self.card_summary.add(inner_summary)
        content_box.add(self.card_summary)

        # Diagnostics Table
        self.table = toga.Table(
            columns=[
                t("doctor_col_status"),
                t("doctor_col_item"),
                t("doctor_col_details"),
                t("doctor_col_hint"),
            ],
            style=Pack(flex=1),
        )
        content_box.add(self.table)

    async def action_install_xcode(self, widget: Optional[toga.Button] = None):
        """Invoke macOS native Xcode Command Line Tools installer dialog with user guidance."""
        if self.btn_install_xcode:
            self.btn_install_xcode.enabled = False
        try:
            success, status = await self.doctor_service.trigger_xcode_install()
            title = t("doctor_dialog_install_title")
            if success:
                if status == "already_installed":
                    msg = t("doctor_dialog_install_already_msg")
                else:
                    msg = t("doctor_dialog_install_msg")
            else:
                msg = t("doctor_dialog_install_error_msg", error=status)

            if self.app_instance and hasattr(self.app_instance, "main_window") and self.app_instance.main_window:
                await self.app_instance.main_window.info_dialog(title, msg)
        except Exception as e:
            logger.error(f"Error executing action_install_xcode: {e}")
            if self.app_instance and hasattr(self.app_instance, "main_window") and self.app_instance.main_window:
                await self.app_instance.main_window.info_dialog(
                    t("doctor_dialog_install_title"),
                    t("doctor_dialog_install_error_msg", error=str(e)),
                )
        finally:
            if self.btn_install_xcode:
                self.btn_install_xcode.enabled = True

    async def run_checks(self):
        items = await self.doctor_service.check_environment()
        table_data = []
        passed_count = 0
        total_count = len(items)
        xcode_select_passed = True

        for item in items:
            if item.passed:
                passed_count += 1
                status_icon = t("doctor_status_ok")
            else:
                status_icon = t("doctor_status_missing")
                if item.name == "xcode-select":
                    xcode_select_passed = False

            table_data.append((
                status_icon,
                item.name,
                item.details,
                item.hint or "—",
            ))

        self.table.data = table_data
        if passed_count == total_count:
            self.label_summary.text = t("doctor_summary_all_passed", passed=passed_count, total=total_count)
            self.btn_install_xcode.style.visibility = "hidden"
        else:
            self.label_summary.text = t("doctor_summary_issues_found", count=total_count - passed_count)
            if not xcode_select_passed:
                self.btn_install_xcode.style.visibility = "visible"
            else:
                self.btn_install_xcode.style.visibility = "hidden"


