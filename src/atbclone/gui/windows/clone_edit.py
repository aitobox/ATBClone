"""Clone Edit Window."""

from typing import Callable, Coroutine, Any
from urllib.parse import urlparse
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER

from atbclone.core.i18n import t
from atbclone.core.locale import SUPPORTED_LANGUAGES
from atbclone.core.state import CloneRecord
from atbclone.recipes.models import ProxyConfig
from atbclone.gui.patch_cocoa import configure_cocoa_window
from atbclone.gui.theme import Theme


class CloneEditWindow(toga.Window):
    def __init__(
        self,
        record: CloneRecord,
        on_save: Callable[[CloneRecord], Coroutine[Any, Any, None]] | None = None,
    ):
        super().__init__(title=t("win_edit_title", name=record.clone_name), size=(500, 390))
        configure_cocoa_window(self, floating=True)
        self.record = record
        self.on_save_callback = on_save

        # Proxy parsing
        proxy_type = "http"
        proxy_host = "127.0.0.1"
        proxy_port = "7890"
        if record.proxy_summary:
            parsed = urlparse(record.proxy_summary)
            if parsed.scheme:
                proxy_type = parsed.scheme
            if parsed.hostname:
                proxy_host = parsed.hostname
            if parsed.port:
                proxy_port = str(parsed.port)

        self.switch_proxy = toga.Switch(
            text=t("win_edit_switch_proxy"),
            value=record.proxy_enabled,
            style=Pack(margin_bottom=8, font_size=13.5),
        )
        self.select_proxy_type = toga.Selection(
            items=["http", "https", "socks5"],
            value=proxy_type,
            style=Pack(width=105, margin_right=8, font_size=12.0),
        )
        self.input_proxy_host = toga.TextInput(
            value=proxy_host,
            style=Pack(flex=1, margin_right=8, font_size=13.5),
        )
        self.input_proxy_port = toga.TextInput(
            value=proxy_port,
            style=Pack(width=90, font_size=13.5),
        )

        # Language selection
        self._lang_keys = list(SUPPORTED_LANGUAGES.keys())
        self._lang_display_items = [
            t(SUPPORTED_LANGUAGES[k]["label_key"]) for k in self._lang_keys
        ]
        curr_lang = record.language if record.language in self._lang_keys else "system"
        curr_lang_idx = self._lang_keys.index(curr_lang)
        self.select_language = toga.Selection(
            items=self._lang_display_items,
            value=self._lang_display_items[curr_lang_idx],
            style=Pack(flex=1, font_size=12.0),
        )

        self.btn_save = toga.Button(t("btn_save_changes"), on_press=self.on_save_press, style=Pack(flex=1, margin_left=8, height=30, font_weight="bold", font_size=13))
        self.btn_cancel = toga.Button(t("btn_cancel"), on_press=lambda w: self.close(), style=Pack(flex=1, height=30, font_size=13))

        self.content = self._build_content()

    def _build_content(self) -> toga.Box:
        box = toga.Box(style=Pack(direction=COLUMN, margin=(18, 20, 18, 20)))

        title_label = toga.Label(t("win_edit_title", name=self.record.clone_name), style=Pack(font_weight="bold", font_size=15, margin_bottom=12, color=Theme.TEXT_PRIMARY))
        box.add(title_label)

        # Language Settings
        row_lang = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin_bottom=12))
        row_lang.add(toga.Label(t("win_edit_language"), style=Pack(width=120, font_size=13, color=Theme.TEXT_PRIMARY)))
        row_lang.add(self.select_language)
        box.add(row_lang)

        # Proxy Settings
        box.add(self.switch_proxy)

        row_proxy = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin_top=6))
        row_proxy.add(toga.Label(t("win_edit_type_host_port"), style=Pack(width=120, font_size=13, color=Theme.TEXT_PRIMARY)))
        row_proxy.add(self.select_proxy_type)
        row_proxy.add(self.input_proxy_host)
        row_proxy.add(self.input_proxy_port)
        box.add(row_proxy)

        # Action Buttons
        btn_box = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin_top=20))
        btn_box.add(self.btn_cancel)
        btn_box.add(self.btn_save)
        box.add(btn_box)

        return box

    def _get_selected_language(self) -> str:
        if self.select_language.value:
            try:
                idx = self._lang_display_items.index(str(self.select_language.value))
                return self._lang_keys[idx]
            except ValueError:
                pass
        return "system"

    def get_updated_record(self) -> CloneRecord:
        port = 1080
        try:
            port = int(self.input_proxy_port.value)
        except ValueError:
            pass

        proxy_enabled = self.switch_proxy.value
        proxy_type = str(self.select_proxy_type.value)
        proxy_host = self.input_proxy_host.value.strip() or "127.0.0.1"
        proxy_summary = f"{proxy_type}://{proxy_host}:{port}" if proxy_enabled else ""
        lang = self._get_selected_language()

        # Clone current record with updated proxy and language info
        updated = CloneRecord(
            clone_name=self.record.clone_name,
            source_app=self.record.source_app,
            source_path=self.record.source_path,
            bundle_id=self.record.bundle_id,
            strategy=self.record.strategy,
            dest_path=self.record.dest_path,
            data_dir=self.record.data_dir,
            created_at=self.record.created_at,
            proxy_enabled=proxy_enabled,
            proxy_summary=proxy_summary,
            new_bundle_id=self.record.new_bundle_id,
            language=lang,
        )
        return updated

    async def on_save_press(self, widget: toga.Button):
        updated = self.get_updated_record()
        if self.on_save_callback:
            await self.on_save_callback(updated)
        self.close()
