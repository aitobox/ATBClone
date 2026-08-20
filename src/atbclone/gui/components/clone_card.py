"""CloneCard widget for presenting application clone instances."""

import asyncio
from typing import Callable, Optional
from pathlib import Path
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER
from atbclone.core.i18n import t
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
        super().__init__(style=Pack(direction=COLUMN, margin=(6, 8, 6, 8), width=340, background_color=Theme.BG_CARD))
        self.record = record

        # Card Header: Icon + Name + Strategy Tag
        header = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin=(14, 16, 8, 16)))
        self.label_name = toga.Label(
            f"📱 {record.clone_name}",
            style=Pack(font_weight="bold", font_size=16, flex=1, color=Theme.TEXT_PRIMARY),
        )
        strat_badge = t("card_strategy_soft") if record.strategy == "soft_clone" else t("card_strategy_hard")
        self.label_strategy = toga.Label(
            strat_badge,
            style=Pack(font_size=13, font_weight="bold", color=Theme.ACCENT_BLUE),
        )
        header.add(self.label_name)
        header.add(self.label_strategy)
        self.add(header)

        # Card Body: Metadata info
        body = toga.Box(style=Pack(direction=COLUMN, margin=(0, 16, 12, 16)))
        body.add(toga.Label(t("card_label_source", source_app=record.source_app), style=Pack(font_size=14, color=Theme.TEXT_MUTED, margin_bottom=4)))
        body.add(toga.Label(t("card_label_path", path=Path(record.dest_path).name), style=Pack(font_size=13, color=Theme.TEXT_MUTED, margin_bottom=4)))
        proxy_info = record.proxy_summary if record.proxy_enabled else t("card_proxy_disabled")
        body.add(toga.Label(t("card_label_proxy", proxy_info=proxy_info), style=Pack(font_size=13, color=Theme.TEXT_MUTED)))
        self.add(body)

        # Card Footer: Action buttons
        actions = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin=(0, 16, 14, 16)))

        # 1-Click Direct Launch Button
        btn_launch = toga.Button(
            t("btn_launch"),
            on_press=lambda w: on_launch(record) if on_launch else None,
            style=Pack(font_weight="bold", font_size=14, height=32, margin_right=6, flex=1),
        )
        btn_update = toga.Button("🔄", on_press=lambda w: on_update(record) if on_update else None, style=Pack(margin_right=4, width=36, height=32))
        btn_edit = toga.Button("✏️", on_press=lambda w: on_edit(record) if on_edit else None, style=Pack(margin_right=4, width=36, height=32))
        btn_detail = toga.Button("ℹ️", on_press=lambda w: on_detail(record) if on_detail else None, style=Pack(margin_right=4, width=36, height=32))
        btn_delete = toga.Button("🗑️", on_press=lambda w: on_delete(record) if on_delete else None, style=Pack(width=36, height=32))

        actions.add(btn_launch)
        actions.add(btn_update)
        actions.add(btn_edit)
        actions.add(btn_detail)
        actions.add(btn_delete)
        self.add(actions)

