"""Doctor Environment Check View with modern TopHeaderBar."""

import asyncio
from typing import Optional
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER

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
            title="环境自检",
            action_label="🔄 重新检测",
            on_action=lambda w: asyncio.create_task(self.run_checks()),
        )
        self.add(self.top_bar)

        content_box = toga.Box(style=Pack(direction=COLUMN, margin=(0, 20, 20, 20), flex=1))
        self.add(content_box)

        # Summary badge card
        self.card_summary = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin_bottom=10, margin=10, background_color=Theme.BG_CARD))
        self.label_summary = toga.Label("诊断状态: 点击右上角「🔄 重新检测」获取最新环境状态", style=Pack(font_weight="bold", font_size=13, flex=1, color=Theme.TEXT_PRIMARY))
        self.card_summary.add(self.label_summary)
        content_box.add(self.card_summary)

        # Diagnostics Table
        self.table = toga.Table(
            columns=["状态", "检测项", "当前环境详情", "修复建议 / 说明"],
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
                status_icon = "✅ 正常"
            else:
                status_icon = "❌ 缺失"

            table_data.append((
                status_icon,
                item.name,
                item.details,
                item.hint or "—",
            ))

        self.table.data = table_data
        if passed_count == total_count:
            self.label_summary.text = f"✅ 所有环境检测项全部通过 ({passed_count}/{total_count})"
        else:
            self.label_summary.text = f"⚠️ 发现 {total_count - passed_count} 项未就绪环境组件，请参考列表修复建议"
