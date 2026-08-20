"""Clone Detail Window."""

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

from atbclone.core.i18n import t
from atbclone.core.state import CloneRecord
from atbclone.gui.patch_cocoa import configure_cocoa_window


class CloneDetailWindow(toga.Window):
    def __init__(self, record: CloneRecord):
        super().__init__(title=t("win_detail_title", name=record.clone_name), size=(480, 420))
        configure_cocoa_window(self, floating=True)
        self.record = record


        proxy_str = record.proxy_summary if record.proxy_enabled else t("list_proxy_disabled")
        strat_badge = t("card_strategy_soft") if record.strategy == "soft_clone" else t("card_strategy_hard")

        self.label_clone_name = toga.Label(record.clone_name, style=Pack(font_weight="bold", font_size=16, margin_bottom=10))
        self.label_source_app = toga.Label(f"{t('win_detail_source_app')}: {record.source_app}", style=Pack(margin=4))
        self.label_source_path = toga.Label(f"{t('win_detail_source_path')}: {record.source_path}", style=Pack(margin=4))
        self.label_bundle_id = toga.Label(f"{t('win_detail_bundle_id')}: {record.bundle_id}", style=Pack(margin=4))
        self.label_new_bundle_id = toga.Label(f"{t('win_detail_new_bundle_id')}: {record.new_bundle_id or '—'}", style=Pack(margin=4))
        self.label_strategy = toga.Label(f"{t('win_detail_strategy')}: {strat_badge}", style=Pack(margin=4))
        self.label_dest_path = toga.Label(f"{t('win_detail_dest_path')}: {record.dest_path}", style=Pack(margin=4))
        self.label_data_dir = toga.Label(f"{t('win_detail_data_dir')}: {record.data_dir}", style=Pack(margin=4))
        self.label_created_at = toga.Label(f"{t('win_detail_created_at')}: {record.created_at}", style=Pack(margin=4))
        self.label_proxy = toga.Label(f"{t('win_detail_proxy')}: {proxy_str}", style=Pack(margin=4))

        self.btn_close = toga.Button(t("btn_close"), on_press=lambda w: self.close(), style=Pack(margin_top=15, width=100))

        self.content = self._build_content()

    def _build_content(self) -> toga.Box:
        box = toga.Box(style=Pack(direction=COLUMN, margin=15))
        box.add(self.label_clone_name)
        box.add(self.label_source_app)
        box.add(self.label_source_path)
        box.add(self.label_bundle_id)
        box.add(self.label_new_bundle_id)
        box.add(self.label_strategy)
        box.add(self.label_dest_path)
        box.add(self.label_data_dir)
        box.add(self.label_created_at)
        box.add(self.label_proxy)
        box.add(self.btn_close)
        return box
