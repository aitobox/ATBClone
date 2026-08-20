# ATBClone GUI Modern Redesign Spec

## 1. Overview & Objectives

Redesign the ATBClone BeeWare/Toga macOS desktop GUI to match modern desktop layout standards (inspired by the provided Cockpit Tools reference design). The new interface replaces cramped button bars with a spacious, ice-blue themed sidebar, unified top action bars, dynamic card/grid and table views, direct 1-click clone app launching, dedicated Logs and Settings views, and cohesive visual aesthetics.

---

## 2. Navigation Architecture

### Left Sidebar (`SidebarBox`)
- **Header**: `🚀 ATBClone` branding with formal title and version tag.
- **Primary Section**:
  1. `📱 我的分身 (Clone Apps)` — Active clones manager.
  2. `📖 预设配方 (Recipes)` — Built-in & custom clone recipes library.
  3. `🔍 应用探测 (Probe)` — Application inspector & strategy recommender.
  4. `🩺 环境自检 (Doctor)` — System dependencies & toolchain diagnostics.
- **Bottom Fixed Section**:
  1. `📋 运行日志 (Logs)` — Real-time execution logs & clone task outputs.
  2. `⚙️ 全局设置 (Settings)` — Preferences, default paths, and "Open Data Directory" action.
- **Styling**:
  - Width: ~200px fixed width, compact layout with proper padding.
  - Background: Modern ice-blue/light-gray `#EEF4FB`.
  - Selection: Active item highlighted with soft blue pill background `#E0ECFD`, dark blue text `#1D4ED8`, and left accent indicator.

---

## 3. Right Content Area & Unified Top Toolbar

Every functional view shares a unified top toolbar layout (`TopHeaderBar`):
- **Breadcrumb / Title**: e.g., `📁 全部应用 > 分身管理 (3)`
- **Search & Filter Input**: Real-time filtering by app name, clone name, bundle ID, or strategy.
- **View Mode Switcher**:
  - 🔲 **Card/Grid View** (Default for Clones and Recipes)
  - 📋 **Table/List View** (Compact data-dense view)
- **Primary Actions**:
  - `+ 新建分身 (New Clone)`: High-visibility primary action button (accent blue `#2563EB`).
  - `🔄 刷新 (Refresh)`: Instant reload of current dataset.

---

## 4. View-Specific Designs

### A. Clone Apps View (`CloneListView`)
- **Card View (`CloneCardGrid`)**:
  - Rendered as responsive 2-column or 3-column card grid in a scrollable container.
  - **Card Header**: App icon/emoji, clone name (bold), strategy badge (`[Hard Clone]` in sky-blue, `[Soft Clone]` in emerald-green), proxy indicator tag.
  - **Card Body**:
    - Source: Source app name & bundle ID.
    - App Path: Target `.app` location.
    - Data Dir: Isolated data directory path.
    - Status: Ready / Created timestamp.
  - **Card Footer (Actions)**:
    - **`▶️ 启动 (Launch)`**: 1-click direct app launch using background `asyncio` execution (`open <path>`).
    - **`🔄 更新 (Update)`**: Synchronize source app binary changes.
    - **`✏️ 编辑 (Edit)`**: Open edit window for display name / proxy settings.
    - **`ℹ️ 详情 (Detail)`**: Open inspect window.
    - **`🗑️ 删除 (Delete)`**: Confirmation dialog with optional data wipe.
- **Table View**:
  - Dense `toga.Table` with columns: Clone Name, Source, Strategy, Path, Proxy, Actions.

### B. Recipes View (`RecipeListView`)
- Card & Table support for recipes.
- Tagged with strategy support (Hard / Soft), custom data dir support, and launch args preview.
- Direct "+ New Recipe", "Edit", "Duplicate", and "Export".

### C. Application Probe View (`ProbeView`)
- Clean drag-or-browse target card at the top.
- Detailed analysis cards displaying: Architecture (arm64/x86_64), Frameworks (Electron/Chromium/Native), Sandbox status, and one-click "Clone with this Recipe" button.

### D. System Diagnostics View (`DoctorView`)
- Checklist cards for Xcode CLI tools, codesign permissions, Python runtime, and SIP status.
- One-click "Fix All" and individual repair actions.

### E. Logs View (`LogsView`)
- Clean monospace log stream viewer with auto-scroll.
- Controls: Filter logs by level (INFO/WARN/ERROR), "Clear Logs", and "Copy to Clipboard".

### F. Settings View (`SettingsView`)
- General preferences:
  - Default Destination Directory (with Browse button).
  - Default Data Directory.
  - Default Proxy host and port.
  - **"📂 查看数据目录 (Open Data Directory)"** button (opens `~/.atbclone` in macOS Finder).

---

## 5. Visual Styling & Color Palette

- **Window Background**: Clean neutral `#F8FAFC`
- **Sidebar Background**: Soft ice-blue `#EEF4FB`
- **Card Background**: Pure white `#FFFFFF` with `#E2E8F0` border and rounded corners (8px)
- **Accent / Primary Buttons**: Royal Blue `#2563EB`
- **Badges**:
  - Hard Clone: Light blue `#DBEAFE` text `#1E40AF`
  - Soft Clone: Light green `#D1FAE5` text `#065F46`
  - Proxy Active: Light orange `#FFEDD5` text `#9A3412`

---

## 6. Implementation Architecture

- **`src/atbclone/gui/components/`**:
  - `sidebar.py`: Modern custom sidebar navigation box with state tracking.
  - `top_bar.py`: Shared breadcrumb, search bar, and action bar component.
  - `clone_card.py`: Standalone clone app card widget with direct launch & action buttons.
  - `recipe_card.py`: Standalone recipe card widget.
- **`src/atbclone/gui/views/`**:
  - `clone_list.py`: Refactored to support dual Card/Table views.
  - `recipe_list.py`: Refactored to support dual Card/Table views.
  - `probe_view.py`: Refactored with card-based analysis panels.
  - `doctor_view.py`: Refactored with status cards.
  - `logs_view.py`: New real-time log viewer.
  - `settings_view.py`: New settings view with Finder directory opener.
- **`src/atbclone/gui/app.py`**:
  - Updated layout coordinator managing Sidebar + Main Content view container.
