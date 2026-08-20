"""Doctor Environment Check View with modern TopHeaderBar."""

import asyncio
from typing import Optional
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER

from atbclone.core.i18n import t
from atbclone.gui.services.doctor_service import DoctorService
from atbclone.gui.components.top_bar import TopHeaderBar
from atbclone.gui.theme import Theme


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

        content_box = toga.Box(style=Pack(direction=COLUMN, margin=(0, 20, 20, 20), flex=1))
        self.add(content_box)

        # Summary badge card
        self.card_summary = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin_bottom=10, margin=10, background_color=Theme.BG_CARD))
        self.label_summary = toga.Label(t("doctor_summary_initial"), style=Pack(font_weight="bold", font_size=13, flex=1, color=Theme.TEXT_PRIMARY))
        self.card_summary.add(self.label_summary)
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

    async def run_checks(self):
        items = await self.doctor_service.check_environment()
        table_data = []
        passed_count = 0
        total_count = len(items)

        for item in items:
            if item.passed:
                passed_count += 1
                status_icon = t("doctor_status_ok")
            else:
                status_icon = t("doctor_status_missing")

            table_data.append((
                status_icon,
                item.name,
                item.details,
                item.hint or "—",
            ))

        self.table.data = table_data
        if passed_count == total_count:
            self.label_summary.text = t("doctor_summary_all_passed", passed=passed_count, total=total_count)
        else:
            self.label_summary.text = t("doctor_summary_issues_found", count=total_count - passed_count)

