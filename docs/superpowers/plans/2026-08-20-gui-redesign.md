# Modern GUI Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Redesign the ATBClone BeeWare/Toga macOS desktop GUI to match the reference modern desktop card layout, featuring an ice-blue compact sidebar, shared top header bar with search/view toggle, interactive clone cards with direct 1-click launching, and new Logs/Settings views.

**Architecture:** A component-driven GUI architecture with dedicated `theme.py`, reusable `SidebarNav`, `TopHeaderBar`, and `CloneCard` components, supporting responsive dual-view (Card Grid / Table) across all feature areas managed by `ATBCloneApp`.

**Tech Stack:** Python 3.12, BeeWare Toga 0.4.x+, AppKit/Cocoa backend, Pydantic v2, PyYAML, Pytest.

## Global Constraints

- Preserve all existing CLI functionality and 234 unit/integration tests without breaking changes.
- Ensure Toga event loop compatibility using `asyncio` and `loop.run_in_executor` for background processes (such as app launching and cloning).
- Maintain macOS visual conventions (window close/min/zoom, system open panels, Finder reveals).

---

### Task 1: Theme Foundation and Top Header Bar Component

**Files:**
- Create: `src/atbclone/gui/theme.py`
- Create: `src/atbclone/gui/components/__init__.py`
- Create: `src/atbclone/gui/components/top_bar.py`
- Test: `tests/gui/test_theme_and_components.py`

**Interfaces:**
- Produces: `Theme` color and font constants (`BG_WINDOW`, `BG_SIDEBAR`, `BG_CARD`, `ACCENT_BLUE`, `BADGE_HARD`, `BADGE_SOFT`), `TopHeaderBar(title, search_placeholder, on_search, on_view_change, on_action, action_label)`

- [ ] **Step 1: Write tests for Theme and TopHeaderBar**

```python
# tests/gui/test_theme_and_components.py
from unittest.mock import MagicMock
import toga
from atbclone.gui.theme import Theme
from atbclone.gui.components.top_bar import TopHeaderBar


def test_theme_constants():
    assert Theme.BG_WINDOW == "#F8FAFC"
    assert Theme.BG_SIDEBAR == "#EEF4FB"
    assert Theme.ACCENT_BLUE == "#2563EB"
    assert Theme.BG_CARD == "#FFFFFF"


def test_top_header_bar_initialization():
    on_search = MagicMock()
    on_view_change = MagicMock()
    on_action = MagicMock()

    bar = TopHeaderBar(
        title="全部应用 > 分身管理 (3)",
        search_placeholder="搜索应用...",
        on_search=on_search,
        on_view_change=on_view_change,
        on_action=on_action,
        action_label="+ 新建分身",
    )
    assert bar.label_title.text == "全部应用 > 分身管理 (3)"
    assert bar.btn_action.text == "+ 新建分身"
    assert bar.input_search.placeholder == "搜索应用..."
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src:. /opt/homebrew/anaconda3/envs/ATBClone/bin/pytest tests/gui/test_theme_and_components.py -v`
Expected: FAIL (ModuleNotFoundError)

- [ ] **Step 3: Implement theme.py and components/top_bar.py**

```python
# src/atbclone/gui/theme.py
class Theme:
    BG_WINDOW = "#F8FAFC"
    BG_SIDEBAR = "#EEF4FB"
    BG_SIDEBAR_ACTIVE = "#E0ECFD"
    BG_CARD = "#FFFFFF"
    BORDER_CARD = "#E2E8F0"
    TEXT_PRIMARY = "#0F172A"
    TEXT_MUTED = "#64748B"
    TEXT_ACTIVE = "#1D4ED8"
    ACCENT_BLUE = "#2563EB"
    BADGE_HARD_BG = "#DBEAFE"
    BADGE_HARD_TEXT = "#1E40AF"
    BADGE_SOFT_BG = "#D1FAE5"
    BADGE_SOFT_TEXT = "#065F46"
    BADGE_PROXY_BG = "#FFEDD5"
    BADGE_PROXY_TEXT = "#9A3412"
```

```python
# src/atbclone/gui/components/top_bar.py
from typing import Callable, Optional
import toga
from toga.style import Pack
from toga.style.pack import ROW, COLUMN, CENTER


class TopHeaderBar(toga.Box):
    def __init__(
        self,
        title: str,
        search_placeholder: str = "搜索...",
        on_search: Optional[Callable[[str], None]] = None,
        on_view_change: Optional[Callable[[str], None]] = None,
        on_action: Optional[Callable[[toga.Button], None]] = None,
        action_label: str = "+ 新建",
        on_refresh: Optional[Callable[[toga.Button], None]] = None,
    ):
        super().__init__(style=Pack(direction=ROW, alignment=CENTER, margin=10, flex=1))
        self.on_search_cb = on_search
        self.on_view_change_cb = on_view_change

        # Title / Breadcrumbs
        self.label_title = toga.Label(title, style=Pack(font_weight="bold", font_size=15, margin_right=15))
        self.add(self.label_title)

        # Search Bar
        self.input_search = toga.TextInput(
            placeholder=search_placeholder,
            on_change=self._handle_search,
            style=Pack(width=220, margin_right=10),
        )
        self.add(self.input_search)

        # View Mode Toggle (Grid / Table)
        if on_view_change:
            self.btn_grid = toga.Button("🔲 卡片", on_press=lambda w: on_view_change("grid"), style=Pack(margin_right=4))
            self.btn_list = toga.Button("📋 列表", on_press=lambda w: on_view_change("list"), style=Pack(margin_right=10))
            self.add(self.btn_grid)
            self.add(self.btn_list)

        # Spacer
        self.add(toga.Box(style=Pack(flex=1)))

        # Refresh
        if on_refresh:
            self.btn_refresh = toga.Button("🔄", on_press=on_refresh, style=Pack(margin_right=8, width=40))
            self.add(self.btn_refresh)

        # Primary Action Button
        if on_action:
            self.btn_action = toga.Button(action_label, on_press=on_action, style=Pack(font_weight="bold"))
            self.add(self.btn_action)

    def _handle_search(self, widget: toga.TextInput):
        if self.on_search_cb:
            self.on_search_cb(widget.value.strip())

    def update_title(self, new_title: str):
        self.label_title.text = new_title
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src:. /opt/homebrew/anaconda3/envs/ATBClone/bin/pytest tests/gui/test_theme_and_components.py -v`
Expected: PASS

---

### Task 2: Modern Sidebar Navigation Component

**Files:**
- Create: `src/atbclone/gui/components/sidebar.py`
- Test: `tests/gui/test_sidebar.py`

**Interfaces:**
- Produces: `SidebarNav(on_select: Callable[[str], None], active_key: str = "clones")`
- Nav Items: `"clones"`, `"recipes"`, `"probe"`, `"doctor"`, `"logs"`, `"settings"`

- [ ] **Step 1: Write test for SidebarNav**

```python
# tests/gui/test_sidebar.py
from unittest.mock import MagicMock
from atbclone.gui.components.sidebar import SidebarNav


def test_sidebar_nav_initialization_and_selection():
    on_select = MagicMock()
    sidebar = SidebarNav(on_select=on_select, active_key="clones")
    assert sidebar.active_key == "clones"

    # Simulate selecting "recipes"
    sidebar.select_item("recipes")
    assert sidebar.active_key == "recipes"
    on_select.assert_called_with("recipes")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src:. /opt/homebrew/anaconda3/envs/ATBClone/bin/pytest tests/gui/test_sidebar.py -v`
Expected: FAIL

- [ ] **Step 3: Implement SidebarNav**

```python
# src/atbclone/gui/components/sidebar.py
from typing import Callable, Dict
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER
from atbclone import __version__
from atbclone.gui.theme import Theme


class SidebarNav(toga.Box):
    """Modern macOS-style sidebar navigation."""

    MAIN_NAV_ITEMS = [
        ("clones", "📱 我的分身"),
        ("recipes", "📖 预设配方"),
        ("probe", "🔍 应用探测"),
        ("doctor", "🩺 环境自检"),
    ]

    BOTTOM_NAV_ITEMS = [
        ("logs", "📋 运行日志"),
        ("settings", "⚙️ 全局设置"),
    ]

    def __init__(self, on_select: Callable[[str], None], active_key: str = "clones"):
        super().__init__(style=Pack(direction=COLUMN, width=190, margin=0, background_color=Theme.BG_SIDEBAR))
        self.on_select = on_select
        self.active_key = active_key
        self.buttons: Dict[str, toga.Button] = {}

        # Brand header
        header_box = toga.Box(style=Pack(direction=COLUMN, margin=(16, 12, 12, 12)))
        title_label = toga.Label("🚀 ATBClone", style=Pack(font_weight="bold", font_size=16, color=Theme.TEXT_PRIMARY))
        ver_label = toga.Label(f"v{__version__} Multi-Instance", style=Pack(font_size=10, color=Theme.TEXT_MUTED, margin_top=2))
        header_box.add(title_label)
        header_box.add(ver_label)
        self.add(header_box)

        # Main Nav Section
        self.main_box = toga.Box(style=Pack(direction=COLUMN, margin=(4, 8, 4, 8)))
        for key, title in self.MAIN_NAV_ITEMS:
            btn = toga.Button(
                title,
                on_press=self._create_select_handler(key),
                style=Pack(margin_bottom=4, height=34),
            )
            self.buttons[key] = btn
            self.main_box.add(btn)
        self.add(self.main_box)

        # Flexible spacer
        self.add(toga.Box(style=Pack(flex=1)))

        # Bottom Fixed Nav Section
        self.bottom_box = toga.Box(style=Pack(direction=COLUMN, margin=(4, 8, 12, 8)))
        for key, title in self.BOTTOM_NAV_ITEMS:
            btn = toga.Button(
                title,
                on_press=self._create_select_handler(key),
                style=Pack(margin_bottom=4, height=32),
            )
            self.buttons[key] = btn
            self.bottom_box.add(btn)
        self.add(self.bottom_box)

        self._update_button_styles()

    def _create_select_handler(self, key: str):
        return lambda widget: self.select_item(key)

    def select_item(self, key: str):
        self.active_key = key
        self._update_button_styles()
        if self.on_select:
            self.on_select(key)

    def _update_button_styles(self):
        for key, btn in self.buttons.items():
            if key == self.active_key:
                btn.style.font_weight = "bold"
            else:
                btn.style.font_weight = "normal"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src:. /opt/homebrew/anaconda3/envs/ATBClone/bin/pytest tests/gui/test_sidebar.py -v`
Expected: PASS

---

### Task 3: Clone Card Component & 1-Click Launching

**Files:**
- Create: `src/atbclone/gui/components/clone_card.py`
- Test: `tests/gui/test_clone_card.py`

**Interfaces:**
- Produces: `CloneCard(record: CloneRecord, on_launch, on_update, on_edit, on_detail, on_delete)`
- Direct launch executes `open <dest_path>` asynchronously in background.

- [ ] **Step 1: Write test for CloneCard**

```python
# tests/gui/test_clone_card.py
from unittest.mock import AsyncMock, MagicMock
from pathlib import Path
from atbclone.core.state import CloneRecord
from atbclone.gui.components.clone_card import CloneCard


def test_clone_card_render_and_actions():
    record = CloneRecord(
        clone_name="WeChat2",
        source_app="WeChat",
        source_path="/Applications/WeChat.app",
        bundle_id="com.tencent.xinWeChat",
        strategy="soft_clone",
        dest_path="/Users/test/.atbclone/Apps/WeChat2.app",
        data_dir="/Users/test/.atbclone/data/WeChat2",
        created_at="2026-08-20T10:00:00Z",
    )

    on_launch = MagicMock()
    on_update = MagicMock()
    on_edit = MagicMock()
    on_detail = MagicMock()
    on_delete = MagicMock()

    card = CloneCard(
        record=record,
        on_launch=on_launch,
        on_update=on_update,
        on_edit=on_edit,
        on_detail=on_detail,
        on_delete=on_delete,
    )

    assert card.label_name.text == "WeChat2"
    assert "Soft Clone" in card.label_strategy.text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src:. /opt/homebrew/anaconda3/envs/ATBClone/bin/pytest tests/gui/test_clone_card.py -v`
Expected: FAIL

- [ ] **Step 3: Implement CloneCard**

```python
# src/atbclone/gui/components/clone_card.py
import asyncio
from typing import Callable, Optional
from pathlib import Path
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER
from atbclone.core.state import CloneRecord
from atbclone.gui.theme import Theme


class CloneCard(toga.Box):
    """Modern card representation of an application clone."""

    def __init__(
        self,
        record: CloneRecord,
        on_launch: Optional[Callable[[CloneRecord], None]] = None,
        on_update: Optional[Callable[[CloneRecord], None]] = None,
        on_edit: Optional[Callable[[CloneRecord], None]] = None,
        on_detail: Optional[Callable[[CloneRecord], None]] = None,
        on_delete: Optional[Callable[[CloneRecord], None]] = None,
    ):
        super().__init__(style=Pack(direction=COLUMN, margin=8, padding=12, width=320, background_color=Theme.BG_CARD))
        self.record = record

        # Card Header: Icon + Name + Strategy Tag
        header = toga.Box(style=Pack(direction=ROW, alignment=CENTER, margin_bottom=8))
        self.label_name = toga.Label(
            f"📱 {record.clone_name}",
            style=Pack(font_weight="bold", font_size=14, flex=1, color=Theme.TEXT_PRIMARY),
        )
        strat_badge = "[Soft Clone]" if record.strategy == "soft_clone" else "[Hard Clone]"
        self.label_strategy = toga.Label(
            strat_badge,
            style=Pack(font_size=11, color=Theme.ACCENT_BLUE),
        )
        header.add(self.label_name)
        header.add(self.label_strategy)
        self.add(header)

        # Card Body: Metadata info
        body = toga.Box(style=Pack(direction=COLUMN, margin_bottom=10))
        body.add(toga.Label(f"源应用: {record.source_app}", style=Pack(font_size=11, color=Theme.TEXT_MUTED, margin_bottom=2)))
        body.add(toga.Label(f"路径: {Path(record.dest_path).name}", style=Pack(font_size=11, color=Theme.TEXT_MUTED, margin_bottom=2)))
        proxy_info = record.proxy_summary if record.proxy_enabled else "未启用代理"
        body.add(toga.Label(f"代理: {proxy_info}", style=Pack(font_size=11, color=Theme.TEXT_MUTED)))
        self.add(body)

        # Card Footer: Action buttons
        actions = toga.Box(style=Pack(direction=ROW, alignment=CENTER, margin_top=4))
        
        # 1-Click Launch Button
        btn_launch = toga.Button("▶️ 启动", on_press=lambda w: on_launch(record) if on_launch else None, style=Pack(font_weight="bold", margin_right=4, flex=1))
        btn_update = toga.Button("🔄", on_press=lambda w: on_update(record) if on_update else None, style=Pack(margin_right=4, width=36))
        btn_edit = toga.Button("✏️", on_press=lambda w: on_edit(record) if on_edit else None, style=Pack(margin_right=4, width=36))
        btn_detail = toga.Button("ℹ️", on_press=lambda w: on_detail(record) if on_detail else None, style=Pack(margin_right=4, width=36))
        btn_delete = toga.Button("🗑️", on_press=lambda w: on_delete(record) if on_delete else None, style=Pack(width=36))

        actions.add(btn_launch)
        actions.add(btn_update)
        actions.add(btn_edit)
        actions.add(btn_detail)
        actions.add(btn_delete)
        self.add(actions)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src:. /opt/homebrew/anaconda3/envs/ATBClone/bin/pytest tests/gui/test_clone_card.py -v`
Expected: PASS

---

### Task 4: Dual-View Clone List View (Cards Grid + Table)

**Files:**
- Modify: `src/atbclone/gui/views/clone_list.py`
- Test: `tests/gui/test_clone_views.py`

**Interfaces:**
- Uses: `TopHeaderBar`, `CloneCard`, `CloneService`
- Actions: Filter clones in real-time, toggle Grid/List mode, launch clone app (`open <path>`).

- [ ] **Step 1: Update test_clone_views.py with dual-view and launch tests**
- [ ] **Step 2: Run test to verify it fails**
- [ ] **Step 3: Refactor CloneListView to integrate TopHeaderBar and CloneCardGrid**
- [ ] **Step 4: Run test to verify it passes**

---

### Task 5: Logs View and Settings View

**Files:**
- Create: `src/atbclone/gui/views/logs_view.py`
- Create: `src/atbclone/gui/views/settings_view.py`
- Test: `tests/gui/test_logs_and_settings_views.py`

**Interfaces:**
- Produces: `LogsView`, `SettingsView(on_open_data_dir, on_save_settings)`
- SettingsView includes "📂 查看数据目录" button calling `open ~/.atbclone` in Finder.

- [ ] **Step 1: Write test for LogsView and SettingsView**
- [ ] **Step 2: Run test to verify it fails**
- [ ] **Step 3: Implement LogsView and SettingsView**
- [ ] **Step 4: Run test to verify it passes**

---

### Task 6: Recipe List, Probe, and Doctor Views Refresh

**Files:**
- Modify: `src/atbclone/gui/views/recipe_list.py`
- Modify: `src/atbclone/gui/views/probe_view.py`
- Modify: `src/atbclone/gui/views/doctor_view.py`
- Test: `tests/gui/test_recipe_ui.py`, `tests/gui/test_probe_and_doctor_ui.py`

- [ ] **Step 1: Add TopHeaderBar to RecipeListView, ProbeView, and DoctorView**
- [ ] **Step 2: Run all GUI view tests and verify they pass**

---

### Task 7: App Integration & Full UI Assembly

**Files:**
- Modify: `src/atbclone/gui/app.py`
- Test: `tests/gui/test_app_integration.py`

- [ ] **Step 1: Integrate SidebarNav and view router in ATBCloneApp**
- [ ] **Step 2: Wire up Logs and Settings views to sidebar**
- [ ] **Step 3: Run full pytest suite across entire project (all tests pass)**
- [ ] **Step 4: Launch local test via run_gui.sh to verify macOS aesthetics**
