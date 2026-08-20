"""Logs View for displaying runtime logs and execution histories."""

import asyncio
from datetime import datetime, timezone
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER
from atbclone.gui.components.top_bar import TopHeaderBar
from atbclone.gui.theme import Theme


class LogsView(toga.Box):
    """View presenting live application logs and task output."""

    def __init__(self, app: toga.App | None = None):
        super().__init__(style=Pack(direction=COLUMN, flex=1, background_color=Theme.BG_WINDOW))
        self.app_instance = app
        self._log_entries: list[str] = []

        # Top Header Bar
        self.top_bar = TopHeaderBar(
            title="运行日志",
            search_placeholder="🔍 搜索日志关键字...",
            on_search=self.on_filter_logs,
            action_label="🗑️ 清空日志",
            on_action=self.on_clear_logs,
            on_refresh=self.on_refresh_logs,
        )
        self.add(self.top_bar)

        # Monospace Log Text Area
        self.log_text = toga.MultilineTextInput(
            readonly=True,
            style=Pack(flex=1, margin=(0, 15, 15, 15), font_family="monospace", font_size=12),
        )
        self.add(self.log_text)

        # Initial bootstrap log
        self.log_info("ATBClone GUI runtime initialized.")

    def log_info(self, message: str):
        self._append_log("INFO", message)

    def log_error(self, message: str):
        self._append_log("ERROR", message)

    def _append_log(self, level: str, message: str):
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{now_str}] [{level}] {message}"
        self._log_entries.append(entry)
        self._update_log_display()

    def _update_log_display(self, filter_query: str = ""):
        if not filter_query:
            self.log_text.value = "\n".join(self._log_entries)
        else:
            filtered = [e for e in self._log_entries if filter_query.lower() in e.lower()]
            self.log_text.value = "\n".join(filtered)

    def on_filter_logs(self, query: str):
        self._update_log_display(query)

    def on_clear_logs(self, widget: toga.Button):
        self._log_entries.clear()
        self.log_text.value = ""

    def on_refresh_logs(self, widget: toga.Button):
        self._update_log_display()
