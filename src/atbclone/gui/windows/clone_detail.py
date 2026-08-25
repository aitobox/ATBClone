"""Clone Detail Window."""

import subprocess
import sys
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER

from atbclone.core.clone_inspector import CloneInspector, InjectedDetails
from atbclone.core.i18n import t
from atbclone.core.state import CloneRecord
from atbclone.gui.components.wrapping_label import WrappingLabel
from atbclone.gui.patch_cocoa import configure_cocoa_multiline_text_view, configure_cocoa_window
from atbclone.gui.theme import Theme


def copy_to_clipboard(text: str) -> bool:
    """Copy text to macOS clipboard using native NSPasteboard and pbcopy fallback."""
    if not text:
        return False

    # 1. Cocoa NSPasteboard via Rubicon ObjC (native & 100% reliable)
    if sys.platform == "darwin":
        try:
            import toga_cocoa.libs.appkit  # noqa: F401
            from rubicon.objc import ObjCClass
            NSPasteboard = ObjCClass("NSPasteboard")
            pb = NSPasteboard.generalPasteboard
            pb.clearContents()
            pb.setString_forType_(text, "public.utf8-plain-text")
            return True
        except Exception:
            pass

    # 2. Fallback to /usr/bin/pbcopy or pbcopy subprocess
    for cmd in (["/usr/bin/pbcopy"], ["pbcopy"]):
        try:
            p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
            p.communicate(text.encode("utf-8"))
            if p.returncode == 0:
                return True
        except Exception:
            continue

    return False


class CloneDetailWindow(toga.Window):
    def __init__(self, record: CloneRecord):
        super().__init__(title=t("win_detail_title", name=record.clone_name), size=(580, 580))
        configure_cocoa_window(self, floating=True)
        self.record = record
        self.details: InjectedDetails = CloneInspector.inspect(record)

        proxy_str = record.proxy_summary if record.proxy_enabled else t("list_proxy_disabled")
        strat_badge = t("card_strategy_soft") if record.strategy == "soft_clone" else t("card_strategy_hard")

        from atbclone.core.locale import SUPPORTED_LANGUAGES
        lang_key = SUPPORTED_LANGUAGES.get(record.language, {}).get("label_key", "lang_system")
        lang_str = t(lang_key)

        # Basic Info Labels (kept for symbol reference and test compatibility)
        self.label_clone_name = WrappingLabel(
            record.clone_name,
            style=Pack(font_weight="bold", font_size=15, color=Theme.TEXT_PRIMARY),
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

        # Full selectable multiline text view for all clone details
        summary_text = self.get_summary_text()
        self.text_content = toga.MultilineTextInput(
            value=summary_text,
            readonly=True,
            style=Pack(
                flex=1,
                font_family="monospace",
                font_size=12,
                background_color=Theme.BG_CARD,
                margin_bottom=10,
            ),
        )

        # Action Buttons
        self.btn_copy_cmd = toga.Button(
            t("win_detail_btn_copy_cmd"),
            on_press=self._on_copy_cmd,
            style=Pack(height=30, font_size=12, margin_right=8),
        )
        self.btn_copy_all = toga.Button(
            t("win_detail_btn_copy_all"),
            on_press=self._on_copy_all,
            style=Pack(height=30, font_size=12, margin_right=8),
        )
        self.btn_close = toga.Button(
            t("btn_close"),
            on_press=lambda w: self.close(),
            style=Pack(height=30, font_size=12),
        )

        self.content = self._build_content()
        self._configure_native_view(summary_text)

    def _configure_native_view(self, summary_text: str) -> None:
        """Apply native Cocoa styling and readonly properties to the MultilineTextInput."""
        self.text_content.readonly = True
        self.text_content.value = summary_text
        if sys.platform == "darwin":
            try:
                native = getattr(getattr(self.text_content, "_impl", None), "native", None)
                configure_cocoa_multiline_text_view(native, font_size=12.0, readonly=True)
            except Exception:
                pass

    def get_summary_text(self) -> str:
        """Generate a complete formatted text report of clone details for easy copying/reporting."""
        proxy_str = self.record.proxy_summary if self.record.proxy_enabled else t("list_proxy_disabled")
        strat_badge = t("card_strategy_soft") if self.record.strategy == "soft_clone" else t("card_strategy_hard")

        from atbclone.core.locale import SUPPORTED_LANGUAGES
        lang_key = SUPPORTED_LANGUAGES.get(self.record.language, {}).get("label_key", "lang_system")
        lang_str = t(lang_key)

        lines = [
            f"=== {self.record.clone_name} ({t('win_detail_section_basic')}) ===",
            t("win_detail_source_app", source_app=self.record.source_app),
            t("win_detail_source_path", path=self.record.source_path),
            t("win_detail_bundle_id", bundle_id=self.record.bundle_id),
            t("win_detail_new_bundle_id", new_bundle_id=self.record.new_bundle_id or "—"),
            t("win_detail_strategy", strategy=strat_badge),
            f"{t('detail_label_language')}: {lang_str}",
            t("win_detail_dest_path", dest_path=self.record.dest_path),
            t("win_detail_data_dir", data_dir=self.record.data_dir),
            t("win_detail_created_at", created_at=self.record.created_at),
            t("win_detail_proxy", proxy=proxy_str),
            "",
            f"=== {t('win_detail_section_injected')} ===",
            f"[{t('win_detail_launch_args')}]",
        ]
        if self.details.launch_args:
            for arg in self.details.launch_args:
                lines.append(f"  • {arg}")
        else:
            lines.append(f"  {t('win_detail_none')}")

        lines.append("")
        lines.append(f"[{t('win_detail_env_vars')}]")
        if self.details.env_vars:
            for k, v in self.details.env_vars.items():
                lines.append(f"  • {k}={v}")
        else:
            lines.append(f"  {t('win_detail_none')}")

        lines.append("")
        lines.append(f"[{t('win_detail_exec_cmd')}]")
        lines.append(f"  {self.details.exec_command or t('win_detail_none')}")

        return "\n".join(lines)

    def _on_copy_all(self, widget: toga.Button) -> None:
        summary = self.get_summary_text()
        if summary and copy_to_clipboard(summary):
            self.btn_copy_all.text = t("win_detail_all_copied")

            import asyncio

            try:
                loop = asyncio.get_running_loop()

                async def _reset_text():
                    await asyncio.sleep(2)
                    self.btn_copy_all.text = t("win_detail_btn_copy_all")

                loop.create_task(_reset_text())
            except RuntimeError:
                pass

    def _on_copy_cmd(self, widget: toga.Button) -> None:
        cmd = self.details.exec_command
        if cmd and copy_to_clipboard(cmd):
            self.btn_copy_cmd.text = t("win_detail_cmd_copied")

            import asyncio

            try:
                loop = asyncio.get_running_loop()

                async def _reset_text():
                    await asyncio.sleep(2)
                    self.btn_copy_cmd.text = t("win_detail_btn_copy_cmd")

                loop.create_task(_reset_text())
            except RuntimeError:
                pass

    def _build_content(self) -> toga.Box:
        root = toga.Box(style=Pack(direction=COLUMN, margin=(14, 16, 14, 16), background_color=Theme.BG_WINDOW))

        # Header Box with Title
        header_box = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin_bottom=10))
        header_box.add(self.label_clone_name)
        root.add(header_box)

        # Multiline text view for all clone details
        root.add(self.text_content)

        # Bottom Button Row
        btn_row = toga.Box(style=Pack(direction=ROW, align_items=CENTER))
        if self.details.exec_command:
            btn_row.add(self.btn_copy_cmd)
        btn_row.add(toga.Box(style=Pack(flex=1)))
        btn_row.add(self.btn_copy_all)
        btn_row.add(self.btn_close)
        root.add(btn_row)

        return root

