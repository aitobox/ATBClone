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
        on_open_dir: Optional[Callable[[CloneRecord], None]] = None,
        on_update: Optional[Callable[[CloneRecord], None]] = None,
        on_edit: Optional[Callable[[CloneRecord], None]] = None,
        on_detail: Optional[Callable[[CloneRecord], None]] = None,
        on_delete: Optional[Callable[[CloneRecord], None]] = None,
    ):
        super().__init__(style=Pack(direction=COLUMN, margin=(6, 8, 8, 8), width=340, background_color=Theme.BG_CARD))
        self.record = record

        # Card Header: Icon + Name + Strategy Tag
        header = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin=(12, 14, 6, 14)))
        self.label_name = toga.Label(
            record.clone_name,
            style=Pack(font_weight="bold", font_size=15, flex=1, color=Theme.TEXT_PRIMARY),
        )
        is_soft = record.strategy == "soft_clone"
        strat_badge = t("card_strategy_soft") if is_soft else t("card_strategy_hard")
        strat_color = Theme.BTN_SUCCESS if is_soft else Theme.ACCENT_BLUE
        self.label_strategy = toga.Label(
            strat_badge,
            style=Pack(font_size=12, font_weight="bold", color=strat_color),
        )
        header.add(self.label_name)
        header.add(self.label_strategy)
        self.add(header)

        # Card Body: Metadata info
        body = toga.Box(style=Pack(direction=COLUMN, margin=(0, 14, 10, 14)))
        body.add(toga.Label(t("card_label_source", source_app=record.source_app), style=Pack(font_size=12.5, color=Theme.TEXT_MUTED, margin_bottom=3)))
        body.add(toga.Label(t("card_label_path", path=Path(record.dest_path).name), style=Pack(font_size=12, color=Theme.TEXT_TERTIARY, margin_bottom=3)))
        proxy_info = record.proxy_summary if record.proxy_enabled else t("card_proxy_disabled")
        body.add(toga.Label(t("card_label_proxy", proxy_info=proxy_info), style=Pack(font_size=12, color=Theme.TEXT_TERTIARY)))
        self.add(body)

        # Card Footer: Action buttons
        actions = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin=(0, 14, 12, 14)))

        # 1-Click Direct Launch Button
        btn_launch = toga.Button(
            t("btn_launch"),
            on_press=lambda w: on_launch(record) if on_launch else None,
            style=Pack(font_weight="bold", font_size=13, height=30, margin_right=6, flex=1),
        )
        btn_open_dir = toga.Button(t("btn_open_dir_short"), on_press=lambda w: on_open_dir(record) if on_open_dir else None, style=Pack(margin_right=4, width=50, height=30, font_size=12))
        btn_update = toga.Button(t("btn_update_short"), on_press=lambda w: on_update(record) if on_update else None, style=Pack(margin_right=4, width=50, height=30, font_size=12))
        btn_edit = toga.Button(t("btn_edit_short"), on_press=lambda w: on_edit(record) if on_edit else None, style=Pack(margin_right=4, width=50, height=30, font_size=12))
        btn_detail = toga.Button(t("btn_detail_short"), on_press=lambda w: on_detail(record) if on_detail else None, style=Pack(margin_right=4, width=50, height=30, font_size=12))
        btn_delete = toga.Button(t("btn_delete_short"), on_press=lambda w: on_delete(record) if on_delete else None, style=Pack(width=50, height=30, font_size=12))

        actions.add(btn_launch)
        actions.add(btn_open_dir)
        actions.add(btn_update)
        actions.add(btn_edit)
        actions.add(btn_detail)
        actions.add(btn_delete)
        self.add(actions)


