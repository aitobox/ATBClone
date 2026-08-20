"""Logs View for displaying persistent runtime logs and live execution output."""

from pathlib import Path
from typing import Optional
import toga
from toga.style import Pack
from toga.style.pack import COLUMN
from atbclone.core.i18n import t
from atbclone.core.logger import (
    add_log_listener,
    clear_logs,
    get_logger,
    read_logs,
    remove_log_listener,
)
from atbclone.gui.components.top_bar import TopHeaderBar
from atbclone.gui.theme import Theme

logger = get_logger("gui.logs_view")


class LogsView(toga.Box):
    """View presenting persistent application logs and real-time task output."""

    def __init__(self, app: Optional[toga.App] = None):
        super().__init__(style=Pack(direction=COLUMN, flex=1, background_color=Theme.BG_WINDOW))
        self.app_instance = app
        self._raw_log_lines: list[str] = []
        self._current_filter: str = ""

        # Top Header Bar
        self.top_bar = TopHeaderBar(
            title=t("nav_logs"),
            search_placeholder=t("logs_search_placeholder"),
            on_search=self.on_filter_logs,
            action_label=t("logs_btn_clear"),
            on_action=self.on_clear_logs,
            on_refresh=self.on_refresh_logs,
        )
        self.add(self.top_bar)

        # Monospace Log Text Area
        self.log_text = toga.MultilineTextInput(
            readonly=True,
            style=Pack(flex=1, margin=(0, 24, 20, 24), font_family="monospace", font_size=12, background_color=Theme.BG_CARD),
        )
        self.add(self.log_text)

        # Load persisted disk logs
        self.reload_from_disk()

        # Register live broadcast listener
        add_log_listener(self._on_live_log_entry)

    def reload_from_disk(self):
        """Read all log entries from the persistent log file on disk."""
        content = read_logs()
        if content:
            self._raw_log_lines = [line for line in content.strip().split("\n") if line.strip()]
        else:
            self._raw_log_lines = []
        self._update_log_display()

    def _on_live_log_entry(self, entry: str):
        """Listener callback for new log messages emitted anywhere in the app."""
        if entry.strip():
            self._raw_log_lines.append(entry.strip())
            self._update_log_display()

    def _update_log_display(self):
        query = self._current_filter.strip().lower()
        if not query:
            filtered = self._raw_log_lines
        else:
            filtered = [line for line in self._raw_log_lines if query in line.lower()]

        self.log_text.value = "\n".join(filtered)
        count = len(filtered)
        total = len(self._raw_log_lines)
        if query:
            self.top_bar.update_title(t("logs_title_filtered", count=count, total=total))
        else:
            self.top_bar.update_title(t("logs_title", total=total))


    def on_filter_logs(self, query: str):
        self._current_filter = query
        self._update_log_display()

    def on_clear_logs(self, widget: toga.Button):
        clear_logs()
        self.reload_from_disk()

    def on_refresh_logs(self, widget: toga.Button):
        self.reload_from_disk()

    def log_info(self, message: str):
        get_logger("gui").info(message)

    def log_error(self, message: str):
        get_logger("gui").error(message)
