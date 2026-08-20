"""Clone Detail Window."""

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

from atbclone.core.state import CloneRecord


class CloneDetailWindow(toga.Window):
    def __init__(self, record: CloneRecord):
        super().__init__(title=f"Clone Details: {record.clone_name}", size=(480, 420))
        self.record = record

        self.label_clone_name = toga.Label(record.clone_name, style=Pack(font_weight="bold", font_size=16, margin_bottom=10))
        self.label_source_app = toga.Label(f"Source App: {record.source_app}", style=Pack(margin=4))
        self.label_source_path = toga.Label(f"Source Path: {record.source_path}", style=Pack(margin=4))
        self.label_bundle_id = toga.Label(f"Bundle ID: {record.bundle_id}", style=Pack(margin=4))
        self.label_new_bundle_id = toga.Label(f"New Bundle ID: {record.new_bundle_id or '—'}", style=Pack(margin=4))
        self.label_strategy = toga.Label(f"Strategy: {record.strategy}", style=Pack(margin=4))
        self.label_dest_path = toga.Label(f"Destination: {record.dest_path}", style=Pack(margin=4))
        self.label_data_dir = toga.Label(f"Data Dir: {record.data_dir}", style=Pack(margin=4))
        self.label_created_at = toga.Label(f"Created: {record.created_at}", style=Pack(margin=4))
        self.label_proxy = toga.Label(f"Proxy: {record.proxy_summary if record.proxy_enabled else 'Disabled'}", style=Pack(margin=4))

        self.btn_close = toga.Button("Close", on_press=lambda w: self.close(), style=Pack(margin_top=15, width=100))

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
