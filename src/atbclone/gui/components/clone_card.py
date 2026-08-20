"""CloneCard widget for presenting application clone instances."""

import asyncio
from typing import Callable, Optional
from pathlib import Path
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER
from atbclone.core.state import CloneRecord
from atbclone.gui.theme import Theme


class CloneCard(toga.Box):
    """Card widget rendering single clone instance metadata and action controls."""

    def __init__(
        self,
        record: CloneRecord,
        on_launch: Optional[Callable[[CloneRecord], None]] = None,
        on_update: Optional[Callable[[CloneRecord], None]] = None,
        on_edit: Optional[Callable[[CloneRecord], None]] = None,
        on_detail: Optional[Callable[[CloneRecord], None]] = None,
        on_delete: Optional[Callable[[CloneRecord], None]] = None,
    ):
        super().__init__(style=Pack(direction=COLUMN, margin=8, width=300, background_color=Theme.BG_CARD))
        self.record = record

        # Card Header: Icon + Name + Strategy Tag
        header = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin_bottom=6))
        self.label_name = toga.Label(
            f"📱 {record.clone_name}",
            style=Pack(font_weight="bold", font_size=14, flex=1, color=Theme.TEXT_PRIMARY),
        )
        strat_badge = "[Soft Clone]" if record.strategy == "soft_clone" else "[Hard Clone]"
        self.label_strategy = toga.Label(
            strat_badge,
            style=Pack(font_size=11, color=Theme.ACCENT_BLUE),
        )
        header.add(self.label_name)
        header.add(self.label_strategy)
        self.add(header)

        # Card Body: Metadata info
        body = toga.Box(style=Pack(direction=COLUMN, margin_bottom=8))
        body.add(toga.Label(f"源应用: {record.source_app}", style=Pack(font_size=11, color=Theme.TEXT_MUTED, margin_bottom=2)))
        body.add(toga.Label(f"路径: {Path(record.dest_path).name}", style=Pack(font_size=11, color=Theme.TEXT_MUTED, margin_bottom=2)))
        proxy_info = record.proxy_summary if record.proxy_enabled else "未启用代理"
        body.add(toga.Label(f"代理: {proxy_info}", style=Pack(font_size=11, color=Theme.TEXT_MUTED)))
        self.add(body)

        # Card Footer: Action buttons
        actions = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin_top=4))

        # 1-Click Direct Launch Button
        btn_launch = toga.Button(
            "▶️ 启动",
            on_press=lambda w: on_launch(record) if on_launch else None,
            style=Pack(font_weight="bold", margin_right=4, flex=1),
        )
        btn_update = toga.Button("🔄", on_press=lambda w: on_update(record) if on_update else None, style=Pack(margin_right=4, width=34))
        btn_edit = toga.Button("✏️", on_press=lambda w: on_edit(record) if on_edit else None, style=Pack(margin_right=4, width=34))
        btn_detail = toga.Button("ℹ️", on_press=lambda w: on_detail(record) if on_detail else None, style=Pack(margin_right=4, width=34))
        btn_delete = toga.Button("🗑️", on_press=lambda w: on_delete(record) if on_delete else None, style=Pack(width=34))

        actions.add(btn_launch)
        actions.add(btn_update)
        actions.add(btn_edit)
        actions.add(btn_detail)
        actions.add(btn_delete)
        self.add(actions)
