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
from atbclone.validation import validate_host, validate_proxy_port, validate_proxy_credential


class CloneEditWindow(toga.Window):
    def __init__(
        self,
        record: CloneRecord,
        on_save: Callable[[CloneRecord], Coroutine[Any, Any, None]] | None = None,
    ):
        super().__init__(title=t("win_edit_title", name=record.clone_name), size=(520, 440))
        configure_cocoa_window(self, floating=True)
        self.record = record
        self.on_save_callback = on_save

        # Proxy parsing
        proxy_type = "http"
        proxy_host = "127.0.0.1"
        proxy_port = "7890"
        proxy_user = ""
        proxy_pass = ""
        has_auth = False
        if record.proxy_summary:
            parsed = urlparse(record.proxy_summary)
            if parsed.scheme:
                proxy_type = parsed.scheme
            if parsed.hostname:
                proxy_host = parsed.hostname
            if parsed.port:
                proxy_port = str(parsed.port)
            if parsed.username:
                proxy_user = parsed.username
                has_auth = True
            if parsed.password:
                proxy_pass = parsed.password
                has_auth = True

        if not proxy_pass and (has_auth or proxy_user):
            try:
                from atbclone.core.keychain import get_clone_proxy_password
                keychain_pass = get_clone_proxy_password(record.clone_name)
                if keychain_pass:
                    proxy_pass = keychain_pass
                    has_auth = True
            except Exception:
                pass

        self._initial_auth = has_auth
        self._initial_password = proxy_pass
        self.credential_changed: bool = False

        self.switch_proxy = toga.Switch(
            text=t("win_edit_switch_proxy"),
            value=record.proxy_enabled,
            on_change=self._on_proxy_toggle,
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

        # Proxy Authentication switch and inputs
        self.switch_proxy_auth = toga.Switch(
            text=t("proxy_auth_enable"),
            value=has_auth,
            on_change=self._on_auth_toggle,
            style=Pack(margin_top=8, margin_bottom=6, font_size=13),
        )
        self.input_proxy_user = toga.TextInput(
            value=proxy_user,
            placeholder=t("proxy_auth_username"),
            style=Pack(flex=1, margin_right=8, font_size=13),
        )
        self.input_proxy_pass = toga.PasswordInput(
            value=proxy_pass,
            placeholder=t("proxy_auth_password"),
            style=Pack(flex=1, font_size=13),
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
        self._on_proxy_toggle(self.switch_proxy)

    def _on_proxy_toggle(self, widget: toga.Switch) -> None:
        enabled = bool(widget.value)
        self.select_proxy_type.enabled = enabled
        self.input_proxy_host.enabled = enabled
        self.input_proxy_port.enabled = enabled
        self.switch_proxy_auth.enabled = enabled
        auth_enabled = enabled and bool(self.switch_proxy_auth.value)
        self.input_proxy_user.enabled = auth_enabled
        self.input_proxy_pass.enabled = auth_enabled

    def _on_auth_toggle(self, widget: toga.Switch) -> None:
        auth_enabled = bool(self.switch_proxy.value) and bool(widget.value)
        self.input_proxy_user.enabled = auth_enabled
        self.input_proxy_pass.enabled = auth_enabled

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

        # Proxy Auth Section
        box_auth = toga.Box(style=Pack(direction=COLUMN, margin_top=8, margin_left=12))
        box_auth.add(self.switch_proxy_auth)

        row_auth = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin_top=4))
        row_auth.add(toga.Label(t("proxy_auth_username"), style=Pack(width=80, font_size=12.5, color=Theme.TEXT_PRIMARY)))
        row_auth.add(self.input_proxy_user)
        row_auth.add(toga.Label(t("proxy_auth_password"), style=Pack(margin_left=8, margin_right=6, font_size=12.5, color=Theme.TEXT_PRIMARY)))
        row_auth.add(self.input_proxy_pass)
        box_auth.add(row_auth)

        box_auth.add(toga.Label(t("proxy_auth_password_hint"), style=Pack(font_size=11, color=Theme.TEXT_MUTED, margin_top=4, margin_left=80)))
        box.add(box_auth)

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
        proxy_enabled = bool(self.switch_proxy.value)
        proxy_type = str(self.select_proxy_type.value)
        proxy_host = self.input_proxy_host.value.strip() or "127.0.0.1"

        port = 1080
        if proxy_enabled:
            validate_host(proxy_host)
            try:
                port = int(self.input_proxy_port.value)
            except ValueError:
                raise ValueError(f"Invalid proxy port: {self.input_proxy_port.value!r}. Expected an integer 1-65535.")
            validate_proxy_port(port)

        auth_enabled = proxy_enabled and bool(self.switch_proxy_auth.value)
        if auth_enabled:
            username = self.input_proxy_user.value.strip()
            password = self.input_proxy_pass.value or ""
            validate_proxy_credential(username, field="username")
            validate_proxy_credential(password, field="password")

            self.credential_changed = (
                not self._initial_auth
                or password != self._initial_password
            )

            try:
                from atbclone.core.keychain import save_clone_proxy_password, delete_clone_proxy_password
                if password:
                    save_clone_proxy_password(self.record.clone_name, password)
                else:
                    delete_clone_proxy_password(self.record.clone_name)
            except Exception:
                pass
            user_part = f"{username}@" if username else ""
            proxy_summary = f"{proxy_type}://{user_part}{proxy_host}:{port}"
        elif proxy_enabled:
            self.credential_changed = self._initial_auth
            try:
                from atbclone.core.keychain import delete_clone_proxy_password
                delete_clone_proxy_password(self.record.clone_name)
            except Exception:
                pass
            proxy_summary = f"{proxy_type}://{proxy_host}:{port}"
        else:
            self.credential_changed = self._initial_auth
            try:
                from atbclone.core.keychain import delete_clone_proxy_password
                delete_clone_proxy_password(self.record.clone_name)
            except Exception:
                pass
            proxy_summary = ""

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
            display_name=getattr(self.record, "display_name", None),
            injection_strategy=getattr(self.record, "injection_strategy", "auto"),
        )
        return updated

    async def on_save_press(self, widget: toga.Button):
        try:
            updated = self.get_updated_record()
        except ValueError as err:
            await self.error_dialog(t("dialog_validation_error_title"), str(err))
            return

        if self.on_save_callback:
            await self.on_save_callback(updated)
        self.close()
