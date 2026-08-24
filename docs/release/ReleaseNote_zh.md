[English](ReleaseNote.md) | [简体中文](ReleaseNote_zh.md) | [繁體中文](ReleaseNote_zh_TW.md) | [日本語](ReleaseNote_ja.md) | [한국어](ReleaseNote_ko.md) | [Deutsch](ReleaseNote_de.md) | [Français](ReleaseNote_fr.md) | [Русский](ReleaseNote_ru.md) | [Español](ReleaseNote_es.md)

# ATBClone 更新日志 (Release Notes)

本文档记录了 **ATBClone** 的所有重要更新、新功能、性能优化及问题修复。

---

## [v0.9.9] - 2026-08-24

### 📋 分身详情窗口文字可选与“复制全部信息”
- **全字段文本高亮选择与一键导出**：
  - 在 `CloneDetailWindow` 详情窗口中开启 Cocoa 原生文本可选模式（`setSelectable_`），支持鼠标高亮选择并复制任意路径、Bundle ID 与运行参数。
  - 底部新增“复制全部信息”按钮，一键将分身的完整诊断摘要格式化导出至剪贴板，并提供即时复制反馈。

### 🎨 macOS 原生 UI 视觉与组件间距优化
- **主题色彩与卡片排版打磨**：
  - 优化 `Theme` 中的明暗模式色彩 Token（`BG_APP`、`BG_CARD`、`BG_HOVER`、`BORDER`、`TEXT_PRIMARY`、`TEXT_MUTED`、`ACCENT`）。
  - 规范卡片边框圆角、内边距与组件间距，大幅提升 `CloneListView`、`RecipeListView`、`ProbeView`、`DoctorView`、`SettingsView` 及各弹窗的视觉质感与原生体验。

### 📖 全新多语言完整用户使用手册 (`docs/guide/`)
- **全方位使用与进阶指南**：
  - 发布中英文双语完整用户手册（`docs/guide/zh-cn/` 与 `docs/guide/en/`）。
  - 涵盖第一章（基础操作与生命周期）、第二章（高级自定义规则）、第三章（底层架构与框架原理）与第四章（常见问题、环境诊断与排错指南）。

### 🧪 自动化测试与质量保障
- **测试套件扩充**：
  - 自动化测试用例扩充至 431 项，覆盖详情导出、原生可选文本及主题样式验证。

---

## [v0.9.8] - 2026-08-24

### 🔒 沙盒权限精准提取与硬分身引擎稳定性提升
- **源应用 Entitlements 签名权限继承**：
  - 增强 `HardCloneEngine` 硬分身引擎，通过 `codesign -d --entitlements :-` 精准提取并保留源 Mach-O 可执行文件的原生权限配置。
  - 增加了对空权限及损坏权限文件的安全防护，杜绝重新签名时因权限缺失导致的权限异常与闪退。
- **内置规则沙盒容器绝对隔离**：
  - 规范并修正全部硬分身内置规则（包括微信、QQ、企业微信、WPS Office、LINE、Skype、剪映/CapCut 等），显式保留沙盒约束（`strip_sandbox: false`）。
  - 确保硬分身应用在独立沙盒容器目录（`~/Library/Containers/<new_bundle_id>`）中运行，杜绝分身间数据与凭证交叉串号。

### 📚 项目文档与规则规范同步
- **中英文技术文档更新**：
  - 同步更新英文 `README.md` 与中文 `README_zh.md`，全面补充 `app_type`、`strip_sandbox`、架构分类规则及 CLI/GUI 使用示例。

### 🧪 自动化测试与质量保障
- **测试套件全绿通过**：
  - 428 项单元测试、核心克隆引擎与 GUI 集成测试全部验证通过。

---

## [v0.9.7] - 2026-08-24

### 🔍 智能应用架构探测与框架自适应多语言注入
- **应用运行时框架识别 (`app_type`)**：
  - 在 Recipe 规则模型中引入 `app_type` 字段（`electron`、`chromium`、`qt`、`flutter`、`native_cocoa`、`java`、`unknown`）。
  - `AppProber.detect_app_type` 通过解析 Frameworks、动态链接库和 JVM 结构自动识别应用底层架构。
  - 标准化全部 34 个内置规则文件，补充声明 `app_type` 与 `strip_sandbox` 属性。
- **框架自适应多语言参数注入**：
  - 依据应用架构动态注入匹配的语言启动参数（Chromium/Electron 使用 `--lang=`、原生 Cocoa 使用 `-AppleLanguages`、Java 使用 `-user.language` 等）。

### 🧬 Mach-O 二进制参数智能探测与校验
- **未知应用数据目录参数探测**：
  - 实现 `BinaryArgumentProber` 扫描 Mach-O 可执行文件字符串表，自动探测支持的用户数据目录启动参数（`--user-data-dir`、`--profile-directory`、`--datadir` 等）。
- **启动参数合规性校验**：
  - 新增 `LaunchArgumentValidator`，在分身构建时过滤不支持或冲突的启动参数，保障分身稳定运行。

### 📋 分身注入参数深度解析与一键复制
- **分身注入参数详情 (`CloneInspector`)**：
  - 实现 `CloneInspector` 解析分身应用包中的运行时注入环境变量、代理规则、多语言重写及启动参数。
  - 在 `CloneDetailWindow` 中新增“注入参数”卡片，提供一键复制到剪贴板与状态反馈。

### ⚙️ 规则编辑窗口高级参数配置
- **可视化规则编辑升级 (`RecipeEditWindow`)**：
  - 支持应用框架类型选择、自定义启动参数编辑、代理配置、环境变量注入及软链接白名单设置。

### 🧪 测试套件扩充
- **全面质量保障**：
  - 自动化测试用例扩充至 428 项，覆盖架构识别、二进制参数探测、参数校验与分身详情解析。

---

## [v0.9.6] - 2026-08-24

### 🖱️ 原生 Cocoa 表格表头点击排序
- **列表表头交互式升降序排序**：
  - 针对分身列表 (`CloneListView`) 与规则列表 (`RecipeListView`) 实现原生 Cocoa `NSTableViewHeaderView` 点击排序补丁。
  - 支持点击表头列进行升序/降序切换，表头实时显示排序箭头指示器，并与工具栏排序下拉框双向同步。
  - 排序后自动保持当前选中的行项，杜绝视图抖动与焦点丢失。

### 📦 列表多选与批量管理操作
- **分身批量管理 (`CloneListView`)**：
  - 支持多行选中 (`multiple_select=True`)，工具栏操作按钮根据选中数量动态激活或禁用。
  - 支持批量更新分身与批量删除分身（联动数据清理确认弹窗）。
- **规则批量删除与场景化保护 (`RecipeListView`)**：
  - 支持多选批量删除自定义规则。
  - 智能场景化提示：内置只读规则受保护提示、混合选中（自定义+内置规则）过滤删除确认、纯自定义规则批量删除确认。
  - 引入并发 Busy 互斥锁，确保批量操作执行期间界面安全锁定。

### 🛠️ Xcode 命令行工具环境诊断与健康检查升级
- **启动环境就绪检查**：
  - 增强 `DoctorService` 与健康检查页面，新增针对 Xcode 命令行工具 (`xcode-select -p`, `codesign`, `lipo`, `otool`, `install_name_tool`) 的诊断检查与引导指引。

### ℹ️ macOS 原生“关于”弹窗元数据优化
- **标准关于弹窗信息修复**：
  - 规范 Cocoa `orderFrontStandardAboutPanelWithOptions:` 调用，准确呈现应用版本号、版权与技术栈元数据。

### 🧪 测试套件扩充
- **全面覆盖**：
  - 自动化测试用例扩充至 369 项，覆盖表头排序、批量分身/规则操作及健康诊断。

---

## [v0.9.5] - 2026-08-23

### 📝 全新多行自动折行 `WrappingLabel` 组件与排版优化
- **长文本自适应自动折行**：
  - 针对 macOS Cocoa 下 Toga Label 单行计算导致长文本横向撑大父容器和窗口的缺陷，实现 `WrappingLabel` 原生多行自适应组件。
  - 基于 `NSTextField` 和 `cellSizeForBounds_` 动态依据容器宽度重算高度，宽度保持弹性无约束，杜绝长路径、长参数导致的文字截断与窗口形变。
- **探测分析报告与详情页体验打磨**：
  - 在 `ProbeView`（应用探测报告、兼容性评估、沙盒状态）、`CloneDetailWindow`（运行参数、Bundle ID、数据目录）与 `WizardWindow`（策略建议）中全面应用 `WrappingLabel`。

### 🧪 测试密闭性与状态隔离
- **动态配置求值与测试解耦**：
  - 优化 `StateManager` 与 `RecipeLoader`，将默认存储路径从模块导入期求值改为运行时动态求值，彻底隔离测试用例与用户本地状态及自定义规则文件。
- **测试套件扩充**：
  - 自动化测试用例扩充至 347 项，新增 `WrappingLabel` 宽度自适应与高度重算专项测试。

---

## [v0.9.4] - 2026-08-23

### 📁 默认根数据目录迁移至用户可见目录 (`~/ATBClone`)
- **直观便捷的数据与配置管理**：
  - 将 ATBClone 默认根目录从隐藏的 `~/.atbclone` 迁移至用户主目录下的可见文件夹 `~/ATBClone`（包括 `~/ATBClone/Data/` 数据目录、`~/ATBClone/clones.yaml` 状态文件与日志）。
  - 用户在 Finder 或终端中查找分身数据、备份与管理存储空间更加直观便捷。

### 🏷️ 应用显示名称精确覆盖与多语言本地化清理
- **彻底消除系统语言默认名称干扰**：
  - 增强 `SoftCloneEngine` 与 `HardCloneEngine`，在生成分身时自动移除 `Info.plist` 中的 `LSHasLocalizedDisplayName`，并清理资源包中各语言的 `InfoPlist.strings`（如 `CFBundleDisplayName`、`CFBundleName`）。
  - 确保 Finder、Dock 栏、Spotlight 聚焦搜索和活动监视器中严格显示用户自定义的分身名称，杜绝被原应用多语言覆盖。

### 🔄 LaunchServices 服务自动注册与即时刷新
- **图标与元数据即时生效**：
  - 在分身创建与更新流程最后自动执行 `lsregister -f` 强制注册，确保 macOS 立即刷新分身图标与 Bundle 信息，无需重启系统或重启 Finder。

### 📦 文档与测试套件同步
- **全局路径更新**：
  - 同步更新 CLI 帮助信息、GUI 设置页面说明、README 及全套 341 项自动化测试。

---

## [v0.9.3] - 2026-08-21

### 🛡️ 应用检查增强与向导 iOS 移植应用友好拦截
- **向导前置检查与错误弹窗**：
  - 增强 `AppInspector.inspect_app` 逻辑，在用户选择或拖拽应用时直接分析 `UIDeviceFamily` / `LSRequiresIPhoneOS` 及 `Wrapper/` 结构并标记 `is_ios_wrapper`。
  - 在 GUI 创建向导 (`WizardWindow`) 中，一旦选入 iOS 移植应用，立即弹出多语言警告弹窗并清空输入框，将不兼容拦截前置至第一步，提供更明确的引导。

### 🍏 macOS 退出流程优化与 Cocoa 内存解绑
- **修复退出时偶发崩溃 (Crash on Exit)**：
  - 优化 `TrayService.disable()` 与 `ATBCloneApp.exit_app()`，在退出前安全解绑并重置 Cocoa 状态栏菜单与图标 target/action，消除野指针与悬挂选择器。
  - 采用标准的 Cocoa 事件循环终止流程 (`NSApp.terminate_` / `os._exit(0)`)，彻底解决通过托盘“退出”或 `Cmd+Q` 退出程序时偶发的崩溃问题。

### 📦 测试套件扩充
- **自动化测试增强**：
  - 自动化测试用例扩充至 341 项，全面覆盖 iOS 移植应用向导弹窗拦截与安全退出流程。

---

## [v0.9.2] - 2026-08-21

### 🍏 macOS Dock 栏图标动态隐藏与托盘体验增强
- **Dock 栏图标动态显示/隐藏**：
  - 基于 Cocoa AppKit 运行策略 (`NSApplicationActivationPolicy`) 实现 Dock 栏图标动态显隐控制。
  - 开启“最小化到托盘”后，当窗口最小化或关闭至系统托盘时，自动将 App 切换为后台配件模式 (`NSApplicationActivationPolicyAccessory`)，完全隐藏 Dock 栏图标。
  - 从顶部菜单栏托盘还原窗口时，自动无缝恢复为标准模式 (`NSApplicationActivationPolicyRegular`)，重新显现 Dock 图标并置顶聚焦。
- **Dock 点击恢复窗口响应 (Reopen Handler)**：
  - 注入原生 `AppDelegate` 的 `applicationShouldHandleReopen:hasVisibleWindows:` 方法，支持在 Dock 栏点击应用图标时平滑拉起并激活主窗口。

### 📦 资源体积优化与测试扩充
- **图标资源瘦身**：
  - 对应用图标资源 (`logo.icns`, `logo.png`) 进行无损压缩与优化，显著降低打包体积与内存占用。
- **测试套件扩充**：
  - 自动化测试用例扩充至 338 项，全面覆盖 Dock 栏策略切换与生命周期恢复。

---

## [v0.9.1] - 2026-08-21

### 🛡️ iOS-on-Mac (Designed for iPad/iPhone) 兼容应用检测与拦截
- **优雅识别与安全拦截**：
  - 增强 `AppProber` 探测引擎及克隆引擎 (`SoftCloneEngine` / `HardCloneEngine`)，精准识别基于 Apple Silicon 运行的 iOS/iPadOS 移植包装应用（如包含 `Wrapper/` 目录或 `UIDeviceFamily` / `LSRequiresIPhoneOS=True` 的应用）。
  - 在 CLI 命令行 (`atbclone clone`, `atbclone wizard`) 及 GUI 交互向导中友好拦截并提示不支持克隆此类 iOS 移植应用 (`error_ios_wrapper_unsupported`)，避免生成损坏的分身及启动崩溃。

### 🎨 打包脚本自动化图标资源生成
- **动态 `.icns` 图标编译**：
  - 优化 `scripts/build_gui.sh`，在生成 macOS DMG 安装包时自动调用 `sips` 和 `iconutil` 将 PNG 图标动态编译为多分辨率 `.icns` 资源。
  - 增强 CLI 与 GUI 构建脚本中的资源打包与完整性校验。

### 🌐 多语言本地化完善
- **新增错误提示多语言支持**：
  - 9 种语言全面补全针对 iOS 移植应用的拦截提示文案。
- **测试套件扩充**：
  - 自动化测试用例扩充至 336 项，全面覆盖 iOS 移植应用探测与拦截分支。

---

## [v0.9.0] - 2026-08-21

### 🌐 分身独立语言与区域 (Locale) 隔离支持
- **分身专属运行语言配置 (`--language` / `--locale`)**：
  - 支持为每个分身独立指定界面显示语言与区域设置，完全独立于 macOS 系统语言及原应用的语言偏好。
  - `atbclone clone` 与 `atbclone wizard` 命令行新增 `--language` / `--locale` 参数，GUI 创建向导与编辑弹窗同步提供可视化语言选择下拉框。
  - 自动向软克隆启动脚本及硬克隆二进制注入 `AppleLanguages` 与 `AppleLocale` 系统偏好与环境变量。
  - 引入 `atbclone.core.locale` 模块，全面支持 BCP-47 语言代码与地区标签解析。

### 🆔 多分身 Bundle ID 自动递增与冲突消解
- **确定性唯一标识解析**：
  - 引入 `AppInspector.find_next_bundle_id` 算法，动态扫描状态记录与文件系统，确保连续克隆同一应用时生成严格唯一且无冲突的 Bundle ID (`com.vendor.app.atb1`, `atb2`, `atb3` 等)。

### 🍏 系统菜单栏托盘唤醒与窗口生命周期优化
- **无缝托盘窗口恢复与激活**：
  - 彻底修复从系统菜单栏图标 (`TrayService`) 还原主窗口时的 Cocoa 激活、取消最小化及置顶聚焦逻辑。
  - 支持在开启“最小化到托盘”时拦截窗口关闭事件（`Cmd+W` 或红绿灯关闭按钮），平滑隐藏至菜单栏而不退出程序。
  - 完善托盘图标的左键、右键及 Ctrl+点击响应。

### ⚡ 分身更新并发竞争修复与目标路径清理
- **原子化更新流程**：
  - 修复 `clone update` 时的并发竞争问题，在重新生成分身前强制对目标路径进行彻底清理，确保数据和代码更新的原子性与稳定性。
  - 优化 GUI 中分身卡片与列表的实时刷新同步。

### 🎨 GUI 排版字号优化与文档完善
- **视觉体验打磨**：
  - 调整 Cocoa 原生表格行高至 34px，优化下拉选择框文本字号，杜绝文字截断与溢出。
  - README 新增桌面端安装指引、GUI 操作图文教程及高清截图。
- **测试套件扩充**：
  - 自动化测试用例扩充至 329 项，全面覆盖语言隔离、Bundle ID 递增与托盘生命周期。

---

## [v0.8.0] - 2026-08-20

### 🎨 深度适配苹果 macOS HIG 原生视觉与交互规范
- **原生设计语言与无障碍体验升级**：
  - 全面重构 GUI 视觉设计，严格遵循 Apple Human Interface Guidelines (HIG)：统一色彩体系、系统字体阶梯（11pt–22pt）与呼吸感间距。
  - 通过运行时注入 (`patch_cocoa`) 优化 Cocoa 原生表格渲染：行高扩增至 40px，重构表头样式并放大单元格字号，大幅提升大屏阅读体验。
  - 全面放大向导窗口、全局设置与编辑弹窗中的输入框、下拉框、开关、按钮及标签控件尺寸。
  - 表格底部操作栏优化为紧凑优雅的 macOS 原生工具栏风格。
  - 全面默认启用 **列表视图 (List View)**，提供更清晰、高效的分身与配方浏览体验。

### 💾 存储设置整合与子目录动态联动
- **存储管理体验优化**：
  - 重组全局设置 (`SettingsView`)，将根存储目录整合进存储管理专区。修改根目录时，自动动态联动更新所有衍生子路径 (`clones.yaml`、`Data/`、`logs/`、`recipes/`)。
  - 提供实时的路径有效性与目录状态提示。

### 🌐 全面支持 HTTPS 代理协议
- **代理支持拓展**：
  - Recipe 模型、CLI (`atbclone clone`, `atbclone wizard`) 与 GUI 网络配置全面支持 `https://` 代理协议（支持带用户名与密码认证）。

### 📦 打包体系优化与测试扩充
- **模块执行入口与 DMG 打包增强**：
  - 新增 `src/atbclone/__main__.py` 入口，支持通过 `python -m atbclone` 直接运行。
  - 增强 `scripts/build_gui.sh` 打包脚本，加入严格的 Bundle 完整性校验、图标资源检查与签名验证。
- **测试套件扩充**：
  - 自动化测试用例扩充至 304 项，全面覆盖 GUI 补丁、视觉组件与代理模型。

---

## [v0.7.0] - 2026-08-20

### 🖥️ 原生 BeeWare Toga 图形桌面客户端
- **全新冰蓝 (Ice-Blue) 现代桌面界面**：
  - 正式发布基于 BeeWare Toga 构建的 macOS 原生桌面客户端 (`atbclone-gui`)。
  - 采用流体侧边栏导航与卡片网格布局，内置分身管理 (`ClonesView`)、应用深度探测 (`ProbeView`)、配方管理 (`RecipesView`)、实时日志 (`LogsView`) 与全局设置 (`SettingsView`)。
  - 支持拖拽 `.app` 的图形化分身创建向导，提供实时创建状态与动画反馈。

### 🍏 原生 macOS 状态栏托盘与最小化支持
- **菜单栏系统托盘服务 (TrayService)**：
  - 深度集成原生 `NSStatusBar` 与 `NSStatusItem` 状态栏图标，提供快捷菜单（打开主窗口、新建分身、快捷启动、首选项、退出）。
  - 支持“最小化到系统托盘”偏好设置，通过 Cocoa Selector 与 `NSWindowDelegate` 实现平滑的窗口隐藏与托盘恢复。

### 📖 GUI 专属多语言更新日志查看器
- **内嵌 Release Notes 窗口**：
  - 全局设置界面新增“查看更新日志”按钮，可独立打开 `ReleaseNotesWindow`。
  - 内置 9 种语言动态切换下拉框，实时渲染多语言 Markdown 更新日志。

### 📝 统一操作日志系统 (Unified Logger)
- **文件持久化与实时广播流**：
  - 引入 `atbclone.core.logger`，统一 CLI 与 GUI 日志输出，支持文件持久化 (`~/.atbclone/logs/atbclone.log`) 与内存广播流 (`LogBroadcastHandler`)。
  - GUI 日志视图支持实时流式刷新、级别筛选、关键字搜索、日志导出与磁盘日志清空。

### 📦 配方库扩充与测试套件升级
- **新增主流应用配方**：新增 **Claude Desktop** (`com.anthropic.claudefordesktop`)、修正 **Telegram** (`ru.keepcoder.Telegram`)、**Cursor** 等热门工具配方。
- **自动化测试扩充**：测试套件用例大幅扩展至 299 项，全面覆盖 GUI 视图、托盘服务与核心逻辑。

---

## [v0.6.0] - 2026-08-19

### 📂 自定义数据存储目录支持
- **克隆数据存储位置自定义 (`--data-dir`)**：
  - `atbclone clone` 命令新增 `--data-dir` 参数，支持为分身指定自定义数据存储路径（例如外接移动固态硬盘或特定工作目录）。
  - `atbclone wizard` 交互式向导全面支持自定义数据目录的提示与配置。
  - Recipe 模型与克隆引擎全面适配动态数据目录变量解析。

### 🗑️ 增强的分身卸载与数据清理 (`atbclone remove`)
- **安全数据清理选项与确认机制**：
  - `atbclone remove` 新增 `--purge-data` 参数，支持非交互式一键彻底清理分身应用本体及对应的数据目录。
  - 新增 `--keep-data` 参数，仅卸载应用本体并保留用户聊天记录与配置文件。
  - 交互式卸载向导增加多语言确认提示，支持用户自主选择是否清理数据，并提供安全提示。
  - 完善孤立残留数据目录与权限异常的安全诊断处理。

### 🆔 Bundle ID 生成规范化与多语言更新
- **规范化 Bundle ID 生成逻辑**：
  - 引入 `AppInspector.generate_bundle_id` 统一生成规则，确保 `clone`、`wizard` 和 `update` 指令间 Bundle ID 格式严格一致。
- **多语言本地化完善**：
  - 9 种语言全面接入数据目录配置、卸载确认与清理状态提示。
- **测试套件扩充**：
  - 自动化测试用例扩充至 213 项，全面覆盖自定义目录与卸载清理逻辑。

---

## [v0.5.0] - 2026-08-19

### 🔐 苹果官方代码签名与公证支持 (Code Signing & Notarization)
- **强化运行时 (Hardened Runtime) 与代码签名**：
  - 深度集成 Apple Developer ID Application 开发者证书签名机制，启用 `--options runtime` 强化运行时、时间戳及自定义 JIT / 二进制执行授权文件 (`scripts/entitlements.plist`)。
  - 新增 `scripts/notarize.sh` 自动化公证脚本，支持通过钥匙串凭证 (`--keychain-profile`) 调用 `xcrun notarytool` 一键完成苹果官方公证与门禁安全验证。
  - `scripts/build_cli.sh` 与 `scripts/release.sh` 全面支持 `--sign-identity`、`--skip-sign` 及 `--notarize` 编译与发布选项，未配置证书时自动降级至 ad-hoc 本地签名。

### 🚀 Chromium 浏览器硬克隆与启动参数注入
- **硬克隆引擎支持 `launch_args` 注入**：
  - 增强 `HardCloneEngine`，使其在环境变量隔离之外，同时支持向二进制启动器动态注入 `--user-data-dir={{ATB_DATA_DIR}}` 等启动参数。
  - 将 **Google Chrome**、**Microsoft Edge**、**Arc Browser** 预置规则升级为 `hard_clone` 策略，实现完整的 App Bundle 独立复制与 Dock/Finder 专属身份。
- **CLI 支持策略覆盖**：
  - `atbclone clone` 命令行新增 `--strategy` 参数（可选 `hard_clone` 或 `soft_clone`），允许用户手动覆盖预设策略。

### ⚡ 进程管理与测试套件扩充
- **进程转发优化**：优化 `SoftCloneEngine` 启动包装脚本，使用标准 `exec "$@"` 进行参数转发与进程接管。
- **自动化测试扩充**：测试套件用例扩展至 199 项，全面覆盖代码签名流程、公证脚本语法与硬克隆参数注入。

---

## [v0.4.0] - 2026-08-19

### 🌐 9 国语言全面本地化与文档体系
- **CLI 全指令 9 语言多语言支持**：
  - 扩展 `atbclone.core.i18n` 多语言模块，全面支持英语、简体中文、繁体中文、日语、韩语、德语、法语、俄语、西班牙语 9 种语言。
  - 所有终端命令（`wizard`、`clone`、`probe`、`list`、`recipe`、`doctor`、`update`、`remove`、`version`）均已实现多语言提示、Rich 表格与错误日志输出。
- **多语言 Release Notes 标准化**：
  - 规范化 `docs/release/` 目录下的 9 国语言更新日志管理与语言导航体系。

### 🔄 自动化发布与版本同步流水线
- **9 语言 ReleaseNotes 自动校验机制**：
  - 升级 `scripts/manage_version.py` 与 `scripts/release.sh`，在发布时自动校验并同步 `docs/release/` 下全部 9 份 ReleaseNotes。
  - 增加 `--check-notes` 版本完整性检查指令，杜绝遗漏多语言发布文档。
- **测试套件扩充**：
  - 自动化测试用例扩充至 191 项，全面覆盖多语言字典渲染与发布流程校验。

---

## [v0.3.0] - 2026-08-19

### 🌐 国际化与多语言支持 (i18n)
- **macOS 系统语言自动探测**：
  - 内置 `atbclone.core.i18n` 多语言引擎，通过 `AppleLanguages` 与 `AppleLocale` 自动探测 macOS 系统偏好语言。
  - CLI 交互式向导、终端提示、表格表头及状态日志自动在中文与英文间智能切换。
  - 支持通过环境变量 `ATBCLONE_LANG`（如 `ATBCLONE_LANG=zh` 或 `ATBCLONE_LANG=en`）强制指定运行语言。
- **多语言文档体系**：
  - 默认采用英文版 `Readme.md`，中文完整文档重命名为 `Readme_zh.md`。
  - 发布涵盖 9 种语言的 Release Notes：英文、简体中文、繁體中文、日语、韩语、德语、法语、俄语、西班牙语。

### 🛠️ CLI 与构建打包优化
- **向导国际化全面接入**：`atbclone wizard` 交互提示、自定义显示名称、自定义 `.icns` 图标选择及代理设置全部支持双语。
- **独立二进制构建升级**：使用 Nuitka 重新打包 `./dist/ATBCloneCli`，内嵌多语言字典并增强沙盒构建兼容性（`PYTHONNOUSERSITE=1`）。
- **自动化测试套件**：新增 `test_i18n.py` 测试用例，全部 186 项自动化测试均支持双语环境验证并通过。

---

## [v0.2.0] - 2026-08-18

### 🚀 重大新功能
- **交互式克隆向导 (`atbclone wizard`)**：
  - 终端交互式操作流，支持直接拖拽 `.app` 应用路径到终端。
  - 分身名称自动自增探测（如 `WeChat2`、`WeChat3`）。
  - 支持配置自定义应用显示名称及自定义 `.icns` 应用图标。
  - 交互式配置专属网络代理（HTTP / SOCKS5），支持账号密码鉴权。
- **智能深度应用探测器 (`atbclone probe`)**：
  - 自动分析任意 macOS 应用的 Mach-O 架构（arm64、x86_64、Universal）、开发框架（Electron、Flutter、Chromium、Qt、Cocoa）及沙盒权限（`com.apple.security.app-sandbox`）。
  - 为未预置规则的应用动态推荐最佳分身策略（`hard_clone` / `soft_clone`）并生成标准 Recipe YAML。
  - `atbclone clone` 支持自动触发探测引擎，无需手动指定分身规则即可一键分身未知应用。
- **独立二进制打包构建**：
  - 增加 `scripts/build_cli.sh` 构建脚本，基于 Nuitka 编译零外部依赖的 macOS 原生 arm64 单文件可执行文件（`dist/ATBCloneCli`）。

### ⚡ 优化与修复
- 优化 `/Applications` 目标路径的提权逻辑，采用原生 macOS `osascript` 授权弹窗，单次输入密码即可完成提权操作。
- 全面采用 `shlex.quote` 对执行路径进行转义保护，杜绝空格与特殊字符引发的路径异常。

---

## [v0.1.0] - 2026-08-17

### 🌟 初始版本发布
- **双引擎克隆架构**：
  - **硬克隆引擎 (Hard Clone)**：完整复制 App Bundle，修改 `Info.plist`，劫持二进制启动脚本注入独立 `HOME` / `TMPDIR`，按需解除沙盒，重新执行 ad-hoc 签名。
  - **软克隆引擎 (Soft Clone)**：针对 Chromium 浏览器和现代编辑器生成轻量级启动器，注入独立 `--user-data-dir` 与代理环境变量。
- **18+ 款主流应用预置分身规则**：
  - 即时通讯：微信 (WeChat)、QQ、Telegram、LINE、Slack、Discord、Skype。
  - AI 客户端：ChatGPT (Codex)、Gemini、Antigravity、Antigravity IDE。
  - 浏览器与开发工具：Google Chrome、Microsoft Edge、Firefox、Arc、Cursor、VS Code、Zed。
- **完整 CLI 命令集**：
  - `clone`：创建应用分身，支持自定义名称、输出目录及网络代理。
  - `list`：Rich 表格查看已创建分身、策略类型、创建时间及代理状态。
  - `update`：主应用升级后一键同步分身，保留全部聊天记录与配置数据。
  - `remove`：安全卸载分身，支持可选清理数据目录。
  - `recipe`：查看内置规则列表及本地自定义规则覆盖。
  - `doctor`：自动化环境自检（检查 `codesign`、`xcode-select`、`PlistBuddy` 等工具链）。
