"""Clone Detail Window."""

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER

from atbclone.core.i18n import t
from atbclone.core.state import CloneRecord
from atbclone.gui.patch_cocoa import configure_cocoa_window
from atbclone.gui.theme import Theme


class CloneDetailWindow(toga.Window):
    def __init__(self, record: CloneRecord):
        super().__init__(title=t("win_detail_title", name=record.clone_name), size=(500, 440))
        configure_cocoa_window(self, floating=True)
        self.record = record

        proxy_str = record.proxy_summary if record.proxy_enabled else t("list_proxy_disabled")
        strat_badge = t("card_strategy_soft") if record.strategy == "soft_clone" else t("card_strategy_hard")

        self.label_clone_name = toga.Label(record.clone_name, style=Pack(font_weight="bold", font_size=16, margin_bottom=10, color=Theme.TEXT_PRIMARY))
        self.label_source_app = toga.Label(t("win_detail_source_app", source_app=record.source_app), style=Pack(font_size=12.5, color=Theme.TEXT_MUTED, margin_bottom=5))
        self.label_source_path = toga.Label(t("win_detail_source_path", path=record.source_path), style=Pack(font_size=12.5, color=Theme.TEXT_MUTED, margin_bottom=5))
        self.label_bundle_id = toga.Label(t("win_detail_bundle_id", bundle_id=record.bundle_id), style=Pack(font_size=12.5, color=Theme.TEXT_MUTED, margin_bottom=5))
        self.label_new_bundle_id = toga.Label(t("win_detail_new_bundle_id", new_bundle_id=record.new_bundle_id or "—"), style=Pack(font_size=12.5, color=Theme.TEXT_MUTED, margin_bottom=5))
        self.label_strategy = toga.Label(t("win_detail_strategy", strategy=strat_badge), style=Pack(font_size=12.5, color=Theme.TEXT_MUTED, margin_bottom=5))
        self.label_dest_path = toga.Label(t("win_detail_dest_path", dest_path=record.dest_path), style=Pack(font_size=12.5, color=Theme.TEXT_MUTED, margin_bottom=5))
        self.label_data_dir = toga.Label(t("win_detail_data_dir", data_dir=record.data_dir), style=Pack(font_size=12.5, color=Theme.TEXT_MUTED, margin_bottom=5))
        self.label_created_at = toga.Label(t("win_detail_created_at", created_at=record.created_at), style=Pack(font_size=12.5, color=Theme.TEXT_MUTED, margin_bottom=5))
        self.label_proxy = toga.Label(t("win_detail_proxy", proxy=proxy_str), style=Pack(font_size=12.5, color=Theme.TEXT_MUTED, margin_bottom=5))

        self.btn_close = toga.Button(t("btn_close"), on_press=lambda w: self.close(), style=Pack(margin_top=14, width=100, height=30, font_size=13))

        self.content = self._build_content()

    def _build_content(self) -> toga.Box:
        root = toga.Box(style=Pack(direction=COLUMN, margin=(18, 20, 18, 20), background_color=Theme.BG_WINDOW))
        
        card = toga.Box(style=Pack(direction=COLUMN, background_color=Theme.BG_CARD, margin_bottom=10))
        inner_card = toga.Box(style=Pack(direction=COLUMN, margin=(14, 18, 14, 18)))
        inner_card.add(self.label_clone_name)
        inner_card.add(self.label_source_app)
        inner_card.add(self.label_source_path)
        inner_card.add(self.label_bundle_id)
        inner_card.add(self.label_new_bundle_id)
        inner_card.add(self.label_strategy)
        inner_card.add(self.label_dest_path)
        inner_card.add(self.label_data_dir)
        inner_card.add(self.label_created_at)
        inner_card.add(self.label_proxy)
        card.add(inner_card)
        root.add(card)

        btn_row = toga.Box(style=Pack(direction=ROW, align_items=CENTER))
        btn_row.add(toga.Box(style=Pack(flex=1)))
        btn_row.add(self.btn_close)
        root.add(btn_row)
        return root
