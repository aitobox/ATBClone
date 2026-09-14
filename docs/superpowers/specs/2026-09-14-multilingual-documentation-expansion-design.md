# Design Spec: ATBClone 帮助手册多语言矩阵扩展 (9 种语言体系)

- **Date**: 2026-09-14
- **Status**: Draft (Under Review)
- **Author**: Antigravity & aitobox
- **Target Repository**: `aitobox/ATBClone`

---

## 1. 背景与目标

### 1.1 背景
ATBClone（艾特智能分身）是一款面向全球 macOS 用户的高性能应用多开与沙盒隔离工具。其客户端 GUI（`src/atbclone/core/locale.py`）已完整支持 9 国语言。为提供一致的全球化用户体验，官方独立文档站点 **`https://clone.aitobox.com`** 需要由现有的中英双语扩展至全套 9 国语言。

### 1.2 目标语言支持矩阵
1. **English (英语)**: `/en/` (`docs/guide/en/`) - 已就绪
2. **简体中文**: `/zh/` (`docs/guide/zh-cn/`) - 已就绪
3. **繁體中文**: `/zh-hant/` (`docs/guide/zh-hant/`) - 新增
4. **日本語**: `/ja/` (`docs/guide/ja/`) - 新增
5. **Deutsch (德语)**: `/de/` (`docs/guide/de/`) - 新增
6. **Français (法语)**: `/fr/` (`docs/guide/fr/`) - 新增
7. **Русский (俄语)**: `/ru/` (`docs/guide/ru/`) - 新增
8. **Español (西班牙语)**: `/es/` (`docs/guide/es/`) - 新增
9. **한국어 (韩语)**: `/ko/` (`docs/guide/ko/`) - 新增

---

## 2. 架构与目录规范

### 2.1 目录组织
所有文档源码、静态资产与配置文件继续统一收敛在 `docs/guide/` 目录下，彻底保持项目根目录干净：

```
docs/guide/
├── CNAME                                  # 绑定 clone.aitobox.com
├── root_index.html                        # 9 语种智能探测分流路由
├── overrides/                             # Apple Glassmorphism UI 覆写模版
├── en/                                    # 英语源码 (5 篇)
├── zh-cn/                                 # 简体中文源码 (5 篇)
├── zh-hant/                               # 繁體中文源码 (5 篇)
│   ├── assets/images/logo.png
│   ├── javascripts/{language-detector.js,ascii-diagram.js}
│   ├── stylesheets/extra.css
│   ├── README.md                          # 手冊總覽
│   ├── 01-basic-operations.md             # 基礎操作
│   ├── 02-advanced-custom-recipes.md      # 高級規則配置
│   ├── 03-under-the-hood-and-internals.md # 底層原理與沙盒隔離
│   └── 04-faq-and-troubleshooting.md      # 常見問題與故障排查
├── ja/                                    # 日本語源码 (同等 5 篇)
├── de/                                    # Deutsch 源码 (同等 5 篇)
├── fr/                                    # Français 源码 (同等 5 篇)
├── ru/                                    # Русский 源码 (同等 5 篇)
├── es/                                    # Español 源码 (同等 5 篇)
└── ko/                                    # 한국어 源码 (同等 5 篇)
```

### 2.2 Zensical 配置文件矩阵
在 `docs/guide/` 下共维护 9 套独立的 TOML 配置文件：
- `zensical.en.toml` (`site_dir = "site/en"`, `docs_dir = "en"`)
- `zensical.zh.toml` (`site_dir = "site/zh"`, `docs_dir = "zh-cn"`)
- `zensical.zh-hant.toml` (`site_dir = "site/zh-hant"`, `docs_dir = "zh-hant"`)
- `zensical.ja.toml` (`site_dir = "site/ja"`, `docs_dir = "ja"`)
- `zensical.de.toml` (`site_dir = "site/de"`, `docs_dir = "de"`)
- `zensical.fr.toml` (`site_dir = "site/fr"`, `docs_dir = "fr"`)
- `zensical.ru.toml` (`site_dir = "site/ru"`, `docs_dir = "ru"`)
- `zensical.es.toml` (`site_dir = "site/es"`, `docs_dir = "es"`)
- `zensical.ko.toml` (`site_dir = "site/ko"`, `docs_dir = "ko"`)

每个配置文件均明确定义：
- `site_url`: `https://clone.aitobox.com/<lang>/`
- `theme.language`: 对应的 ISO 语言标识（如 `zh-Hant`, `ja`, `de`, `fr`, `ru`, `es`, `ko`）
- `project.extra.alternate`: 包含全部 9 种语言的导航切换菜单元数据
- `nav`: 本地化后的各章节标题

---

## 3. 本地化翻译规范与术语标准

### 3.1 核心术语对照表

| 概念 | 简体中文 (zh-Hans) | 繁體中文 (zh-Hant) | 日本語 (ja) | Deutsch (de) | Français (fr) | Español (es) | Русский (ru) | 한국어 (ko) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **应用分身** | 应用分身 / 实例 | 應用分身 / 實例 | アプリクローン / インスタンス | App-Klon / Instanz | Clone d'application / Instance | Clon de aplicación / Instancia | Клон приложения / Экземпляр | 앱 클론 / 인스턴스 |
| **沙盒隔离** | 沙盒隔离 | 沙盒隔離 | サンドボックス分離 | Sandbox-Isolation | Isolation en bac à sable | Aislamiento en sandbox | Изоляция в песочнице | 샌드박스 격리 |
| **软链接/替身** | 符号链接 / 替身 | 符號連結 / 替身 | シンボリックリンク / エイリアス | Symbolischer Link / Alias | Lien symbolique / Alias | Enlace simbólico / Alias | Символическая ссылка / Псевдоним | 심볼릭 링크 / 가상본 |
| **钥匙串** | 钥匙串访问 | 鑰匙圈存取 | キーチェーンアクセス | Schlüsselbundverwaltung | Trousseau d'accès | Acceso a Llaveros | Связка ключей | 키체인 접근 |
| **偏好设置** | 设置 / 偏好设置 | 設定 / 偏好設定 | 設定 / 環境設定 | Einstellungen | Réglages / Préférences | Ajustes / Preferencias | Настройки | 설정 / 환경설정 |
| **分身配方** | 分身配方 (Recipe) | 分身配方 (Recipe) | クローンレシピ (Recipe) | Klon-Rezept (Recipe) | Recette de clone (Recipe) | Receta de clon (Recipe) | Рецепт клона (Recipe) | 클론 레시피 (Recipe) |

### 3.2 技术格式约束
1. **代码与命令行**：所有 CLI 命令（如 `atbclone clone ...`）、配置键（如 `data_dir`, `plist_overrides`）、环境变量及系统路径（`~/Library/Containers/...`）保持原生英文字符串。
2. **列表语法与空行**：严禁 MD032 违规，列表项与前后段落之间强制保留空行。
3. **ASCII 架构图对齐**：CJK 语言保持由 `ascii-diagram.js` 执行等宽字符对齐补正。
4. **GFM Admonitions**：统一使用标准 Blockquote 标记（`> [!NOTE]`, `> [!TIP]`, `> [!WARNING]`, `> [!IMPORTANT]`）。

---

## 4. 全站导航联动与多语言路由

### 4.1 下拉菜单联动 (`docs/guide/overrides/partials/source.html`)
所有站点的 `alternate` 属性统一声明 9 种语言。点击任一语言选项时，保持当前相对路径跳转（如 `/zh/02-advanced-custom-recipes/` ➔ `/de/02-advanced-custom-recipes/`）。

### 4.2 根路由自动分流 (`docs/guide/root_index.html`)
根目录路由按以下优先级解析并跳转：
1. URL 查询参数 `?lang=<code>`（最高优先级，支持调试与强行指定）。
2. `localStorage.getItem('preferred_language')`（用户之前主动选择过的语言）。
3. 浏览器语言匹配：
   - 繁体字系（`zh-tw`, `zh-hk`, `zh-mo`, `zh-hant`）➔ `/zh-hant/`
   - 简体字系（`zh-cn`, `zh-sg`, `zh-hans`, `zh`）➔ `/zh/`
   - 日语（`ja`, `ja-jp`）➔ `/ja/`
   - 韩语（`ko`, `ko-kr`）➔ `/ko/`
   - 德语（`de`, `de-de`, `de-at`, `de-ch`）➔ `/de/`
   - 法语（`fr`, `fr-fr`, `fr-ca`, etc.）➔ `/fr/`
   - 西班牙语（`es`, `es-es`, `es-mx`, etc.）➔ `/es/`
   - 俄语（`ru`, `ru-ru`, etc.）➔ `/ru/`
4. 兜底回退：`/en/`（英文站点）。

---

## 5. 构建与自动化发布管线

### 5.1 本地编译与校验工具 (`scripts/test_deploy_doc.sh`)
- 循环编译 `docs/guide/zensical*.toml`，自动生成 `docs/guide/site/{en,zh,zh-hant,ja,de,fr,ru,es,ko}/`。
- 自动部署 `CNAME`、`root_index.html` (作为 `site/index.html`) 以及 `.nojekyll`。
- 支持 `./scripts/test_deploy_doc.sh -l` 全局 Markdown 格式与列表规范静态检查。

### 5.2 GitHub Actions 工作流 (`.github/workflows/deploy-docs.yml`)
1. 编译全部 9 个 `zensical*.toml`。
2. 安装根路由、CNAME 与 `.nojekyll`。
3. 借助 `peaceiris/actions-gh-pages@v4` 将静态产物推送到 `gh-pages` 分支。
4. 借助 `actions/deploy-pages@v4` 发布到 GitHub Pages 线上环境。

---

## 6. 验证计划

1. **静态语法检查**：
   - 运行 `./scripts/test_deploy_doc.sh -l`，35 篇 Markdown 全部 PASS。
2. **完整本地编译**：
   - 运行 `./scripts/test_deploy_doc.sh -b`，确认 9 个语言目录均成功输出，且每个语种的 5 篇 HTML 均正确生成。
3. **单元测试回归**：
   - 运行 `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/`，保证核心功能不受任何负面影响（588 测试全过）。
4. **CI/CD 与线上验证**：
   - 提交 PR 合并入 `main`，确认 GitHub Actions 执行成功。
   - 验证 `https://clone.aitobox.com` 9 个语言页面在线访问通畅，语言切换正常。
