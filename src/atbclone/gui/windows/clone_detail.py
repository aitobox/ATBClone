"""Clone Detail Window."""

import subprocess
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER

from atbclone.core.clone_inspector import CloneInspector, InjectedDetails
from atbclone.core.i18n import t
from atbclone.core.state import CloneRecord
from atbclone.gui.components.wrapping_label import WrappingLabel
from atbclone.gui.patch_cocoa import configure_cocoa_window
from atbclone.gui.theme import Theme


def copy_to_clipboard(text: str) -> bool:
    """Copy text to macOS clipboard using pbcopy."""
    try:
        p = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
        p.communicate(text.encode("utf-8"))
        return p.returncode == 0
    except Exception:
        return False


class CloneDetailWindow(toga.Window):
    def __init__(self, record: CloneRecord):
        super().__init__(title=t("win_detail_title", name=record.clone_name), size=(560, 580))
        configure_cocoa_window(self, floating=True)
        self.record = record
        self.details: InjectedDetails = CloneInspector.inspect(record)

        proxy_str = record.proxy_summary if record.proxy_enabled else t("list_proxy_disabled")
        strat_badge = t("card_strategy_soft") if record.strategy == "soft_clone" else t("card_strategy_hard")

        from atbclone.core.locale import SUPPORTED_LANGUAGES
        lang_key = SUPPORTED_LANGUAGES.get(record.language, {}).get("label_key", "lang_system")
        lang_str = t(lang_key)

        # Basic Info Labels
        self.label_clone_name = WrappingLabel(
            record.clone_name,
            style=Pack(font_weight="bold", font_size=16, margin_bottom=10, color=Theme.TEXT_PRIMARY),
        )
        self.label_source_app = WrappingLabel(
            t("win_detail_source_app", source_app=record.source_app),
            style=Pack(font_size=12.5, color=Theme.TEXT_MUTED, margin_bottom=5),
        )
        self.label_source_path = WrappingLabel(
            t("win_detail_source_path", path=record.source_path),
            style=Pack(font_size=12.5, color=Theme.TEXT_MUTED, margin_bottom=5),
        )
        self.label_bundle_id = WrappingLabel(
            t("win_detail_bundle_id", bundle_id=record.bundle_id),
            style=Pack(font_size=12.5, color=Theme.TEXT_MUTED, margin_bottom=5),
        )
        self.label_new_bundle_id = WrappingLabel(
            t("win_detail_new_bundle_id", new_bundle_id=record.new_bundle_id or "—"),
            style=Pack(font_size=12.5, color=Theme.TEXT_MUTED, margin_bottom=5),
        )
        self.label_strategy = WrappingLabel(
            t("win_detail_strategy", strategy=strat_badge),
            style=Pack(font_size=12.5, color=Theme.TEXT_MUTED, margin_bottom=5),
        )
        self.label_language = WrappingLabel(
            f"{t('detail_label_language')}: {lang_str}",
            style=Pack(font_size=12.5, color=Theme.TEXT_MUTED, margin_bottom=5),
        )
        self.label_dest_path = WrappingLabel(
            t("win_detail_dest_path", dest_path=record.dest_path),
            style=Pack(font_size=12.5, color=Theme.TEXT_MUTED, margin_bottom=5),
        )
        self.label_data_dir = WrappingLabel(
            t("win_detail_data_dir", data_dir=record.data_dir),
            style=Pack(font_size=12.5, color=Theme.TEXT_MUTED, margin_bottom=5),
        )
        self.label_created_at = WrappingLabel(
            t("win_detail_created_at", created_at=record.created_at),
            style=Pack(font_size=12.5, color=Theme.TEXT_MUTED, margin_bottom=5),
        )
        self.label_proxy = WrappingLabel(
            t("win_detail_proxy", proxy=proxy_str),
            style=Pack(font_size=12.5, color=Theme.TEXT_MUTED, margin_bottom=5),
        )

        # Action Buttons
        self.btn_copy_cmd = toga.Button(
            t("win_detail_btn_copy_cmd"),
            on_press=self._on_copy_cmd,
            style=Pack(width=90, height=24, font_size=11),
        )
        self.btn_close = toga.Button(
            t("btn_close"),
            on_press=lambda w: self.close(),
            style=Pack(width=100, height=30, font_size=13),
        )

        self.content = self._build_content()

    def _on_copy_cmd(self, widget: toga.Button) -> None:
        cmd = self.details.exec_command
        if cmd and copy_to_clipboard(cmd):
            self.btn_copy_cmd.text = t("win_detail_cmd_copied")

    def _build_content(self) -> toga.Box:
        root = toga.Box(style=Pack(direction=COLUMN, margin=(14, 16, 14, 16), background_color=Theme.BG_WINDOW))

        scroll_content = toga.Box(style=Pack(direction=COLUMN))
        scroll_content.add(self.label_clone_name)

        # Card 1: Basic Information
        card_basic = toga.Box(style=Pack(direction=COLUMN, background_color=Theme.BG_CARD, margin_bottom=12))
        inner_basic = toga.Box(style=Pack(direction=COLUMN, margin=(12, 14, 12, 14)))
        inner_basic.add(
            WrappingLabel(
                t("win_detail_section_basic"),
                style=Pack(font_weight="bold", font_size=13.5, color=Theme.TEXT_PRIMARY, margin_bottom=8),
            )
        )
        inner_basic.add(self.label_source_app)
        inner_basic.add(self.label_source_path)
        inner_basic.add(self.label_bundle_id)
        inner_basic.add(self.label_new_bundle_id)
        inner_basic.add(self.label_strategy)
        inner_basic.add(self.label_language)
        inner_basic.add(self.label_dest_path)
        inner_basic.add(self.label_data_dir)
        inner_basic.add(self.label_created_at)
        inner_basic.add(self.label_proxy)
        card_basic.add(inner_basic)
        scroll_content.add(card_basic)

        # Card 2: Injected Parameters & Environment
        card_injected = toga.Box(style=Pack(direction=COLUMN, background_color=Theme.BG_CARD, margin_bottom=12))
        inner_injected = toga.Box(style=Pack(direction=COLUMN, margin=(12, 14, 12, 14)))
        inner_injected.add(
            WrappingLabel(
                t("win_detail_section_injected"),
                style=Pack(font_weight="bold", font_size=13.5, color=Theme.TEXT_PRIMARY, margin_bottom=8),
            )
        )

        # 1. Launch args
        inner_injected.add(
            WrappingLabel(
                t("win_detail_launch_args"),
                style=Pack(font_weight="bold", font_size=12.5, color=Theme.TEXT_PRIMARY, margin_bottom=4),
            )
        )
        if self.details.launch_args:
            for arg in self.details.launch_args:
                inner_injected.add(
                    WrappingLabel(
                        f"• {arg}",
                        style=Pack(font_size=12, color=Theme.TEXT_MUTED, margin_left=8, margin_bottom=3),
                    )
                )
        else:
            inner_injected.add(
                WrappingLabel(
                    t("win_detail_none"),
                    style=Pack(font_size=12, color=Theme.TEXT_MUTED, margin_left=8, margin_bottom=3),
                )
            )

        # 2. Environment variables
        inner_injected.add(
            WrappingLabel(
                t("win_detail_env_vars"),
                style=Pack(font_weight="bold", font_size=12.5, color=Theme.TEXT_PRIMARY, margin_top=8, margin_bottom=4),
            )
        )
        if self.details.env_vars:
            for k, v in self.details.env_vars.items():
                inner_injected.add(
                    WrappingLabel(
                        f"• {k}={v}",
                        style=Pack(font_size=12, color=Theme.TEXT_MUTED, margin_left=8, margin_bottom=3),
                    )
                )
        else:
            inner_injected.add(
                WrappingLabel(
                    t("win_detail_none"),
                    style=Pack(font_size=12, color=Theme.TEXT_MUTED, margin_left=8, margin_bottom=3),
                )
            )

        # 3. Exec Command
        cmd_header_row = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin_top=8, margin_bottom=4))
        cmd_header_row.add(
            WrappingLabel(
                t("win_detail_exec_cmd"),
                style=Pack(font_weight="bold", font_size=12.5, color=Theme.TEXT_PRIMARY),
            )
        )
        cmd_header_row.add(toga.Box(style=Pack(flex=1)))
        if self.details.exec_command:
            cmd_header_row.add(self.btn_copy_cmd)
        inner_injected.add(cmd_header_row)

        inner_injected.add(
            WrappingLabel(
                self.details.exec_command or t("win_detail_none"),
                style=Pack(font_size=11.5, color=Theme.TEXT_MUTED, margin_left=8, margin_bottom=4),
            )
        )

        card_injected.add(inner_injected)
        scroll_content.add(card_injected)

        scroll_container = toga.ScrollContainer(content=scroll_content, horizontal=False, style=Pack(flex=1))
        root.add(scroll_container)

        btn_row = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin_top=8))
        btn_row.add(toga.Box(style=Pack(flex=1)))
        btn_row.add(self.btn_close)
        root.add(btn_row)
        return root
