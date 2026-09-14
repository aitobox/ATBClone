# ATBClone 帮助手册多语言矩阵扩展 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 ATBClone 官方静态帮助文档站点扩展至 9 种语言（英文、简体中文、繁体中文、日语、韩语、德语、法语、西班牙语、俄语），包含完整的高质量本地化内容、全站语言路由联动与 CI/CD 自动化构建发布。

**Architecture:** 基于现有的 Zensical 多配置独立编译模型，为 7 种新语言分别建立独立源码目录与配置文件 `zensical.<lang>.toml`；在所有配置文件中同步声明 9 语种 `alternate` 下拉菜单元数据；升级根路由重定向器与 CI/CD 构建流，实现 9 语种全自动静态构建、多分支同步发布与就地无缝语言切换。

**Tech Stack:** Zensical 0.0.62, Markdown (GFM Admonitions, MD032), Jinja2 HTML Templates, JavaScript, Bash, GitHub Actions (`peaceiris/actions-gh-pages@v4`, `actions/deploy-pages@v4`).

**Spec:** `docs/superpowers/specs/2026-09-14-multilingual-documentation-expansion-design.md`

## Global Constraints

- 所有配置文件、模板和资产必须严格收敛在 `docs/guide/` 目录内，不得污染项目根目录。
- 遵循统一的语言代码规范：`en`（英文）、`zh`（简体中文，源码在 `zh-cn`）、`zh-hant`（繁体中文）、`ja`（日语）、`ko`（韩语）、`de`（德语）、`fr`（法语）、`es`（西班牙语）、`ru`（俄语）。
- 代码块、CLI 命令、YAML 键名和 macOS 容器系统路径（`~/Library/Containers/...`）在所有语种中保持英文字符不变，以保证复用性和可执行性。
- 严禁 MD032 列表与段落黏连语法错误，列表前后强制空行。
- 所有 CJK 语种（中文、日文、韩文）在 ASCII 架构图绘制时须兼容 `ascii-diagram.js` 补正。
- 根路由智能探测必须支持优先级：1. `?lang=<code>` -> 2. `localStorage` -> 3. `navigator.languages` -> 4. 兜底回退 `/en/`。
- CI/CD 必须同步部署至 GitHub Pages 托管环境并推送到 `gh-pages` 分支。
- 必须通过全量单元测试套件：`PYTHONPATH=src conda run -n ATBClone python -m pytest tests/`。

---

### Task 1: 目录骨架与 7 种语言配置文件矩阵构建

**Files:**
- Create: `docs/guide/zensical.{zh-hant,ja,ko,de,fr,es,ru}.toml`
- Create Scaffolding: `docs/guide/{zh-hant,ja,ko,de,fr,es,ru}/`
- Modify: `docs/guide/zensical.en.toml:45-50`
- Modify: `docs/guide/zensical.zh.toml:45-50`

**Interfaces:**
- Consumes: `docs/guide/zensical.en.toml`, `docs/guide/zensical.zh.toml`
- Produces: 7 套完整 Zensical 配置文件，并使所有 9 份配置文件的 `[project.extra.alternate]` 拥有相同的 9 语言矩阵。

- [ ] **Step 1: 创建 7 个语言源码子目录及必要静态资产**
  - 为 `zh-hant`, `ja`, `ko`, `de`, `fr`, `es`, `ru` 分别创建 `assets/images/`, `javascripts/`, `stylesheets/` 目录。
  - 同步拷贝 `logo.png`, `extra.css`, `language-detector.js`, `ascii-diagram.js`。

- [ ] **Step 2: 生成 7 份全新 `zensical.<lang>.toml` 配置文件**
  - 严格配置各语言的 `site_name`, `site_description`, `site_url`, `theme.language`, `docs_dir`, `site_dir`。
  - 在每个配置文件中配置本地化后的 `nav` 章节标题（README、基础操作、高级规则配置、底层原理、常见问题与故障排查）。

- [ ] **Step 3: 更新现有 `zensical.en.toml` 与 `zensical.zh.toml` 的 `alternate` 列表**
  - 将 9 语种全部录入 `alternate` 数组。

- [ ] **Step 4: 校验配置文件语法与引用有效性**
  - 运行 `python3 -c "import tomllib; [tomllib.load(open(f, 'rb')) for f in glob.glob('docs/guide/zensical*.toml')]"`。

- [ ] **Step 5: 提交 Task 1 成果**
  - `git add docs/guide/zensical*.toml docs/guide/*/{assets,javascripts,stylesheets}`
  - `git commit -m "docs(i18n): scaffold 7 new language configs and asset directories"`

---

### Task 2: CJK 语言内容本地化与翻译 (繁体中文、日本語、한국어)

**Files:**
- Create: `docs/guide/zh-hant/{README,01-basic-operations,02-advanced-custom-recipes,03-under-the-hood-and-internals,04-faq-and-troubleshooting}.md`
- Create: `docs/guide/ja/{README,01-basic-operations,02-advanced-custom-recipes,03-under-the-hood-and-internals,04-faq-and-troubleshooting}.md`
- Create: `docs/guide/ko/{README,01-basic-operations,02-advanced-custom-recipes,03-under-the-hood-and-internals,04-faq-and-troubleshooting}.md`

**Interfaces:**
- Consumes: `docs/guide/zh-cn/*.md`, `docs/guide/en/*.md`
- Produces: 15 篇高质量 CJK 帮助文档。

- [ ] **Step 1: 编写繁體中文 (zh-hant) 全部 5 篇文档**
  - 对齐台湾/香港常用 macOS 术语（偏好設定、替身、沙盒、鑰匙圈存取、應用分身）。
  - 保留所有代码块与 YAML 示例的规范性。

- [ ] **Step 2: 编写日本語 (ja) 全部 5 篇文档**
  - 对齐 Apple 日本官方指南术语（環境設定、クローン/インスタンス、シンボリックリンク、キーチェーン、サンドボックス）。
  - 自然流畅的敬体（です/ます）表达。

- [ ] **Step 3: 编写한국어 (ko) 全部 5 篇文档**
  - 对齐 Apple 韩国官方指南术语（환경설정, 앱 클론/인스턴스, 심볼릭 링크, 키체인, 샌드박스 격리）。
  - 严谨清晰的 기술 문서 한국어 风格。

- [ ] **Step 4: 运行 MD032 列表与格式合规性检查**
  - 运行 `./scripts/test_deploy_doc.sh -l`，修复可能的空行与格式警告。

- [ ] **Step 5: 提交 Task 2 成果**
  - `git add docs/guide/{zh-hant,ja,ko}/*.md`
  - `git commit -m "docs(i18n): add localized user guides for Traditional Chinese, Japanese, and Korean"`

---

### Task 3: 欧洲语言内容本地化与翻译 (德语、法语、西班牙语、俄语)

**Files:**
- Create: `docs/guide/de/{README,01-basic-operations,02-advanced-custom-recipes,03-under-the-hood-and-internals,04-faq-and-troubleshooting}.md`
- Create: `docs/guide/fr/{README,01-basic-operations,02-advanced-custom-recipes,03-under-the-hood-and-internals,04-faq-and-troubleshooting}.md`
- Create: `docs/guide/es/{README,01-basic-operations,02-advanced-custom-recipes,03-under-the-hood-and-internals,04-faq-and-troubleshooting}.md`
- Create: `docs/guide/ru/{README,01-basic-operations,02-advanced-custom-recipes,03-under-the-hood-and-internals,04-faq-and-troubleshooting}.md`

**Interfaces:**
- Consumes: `docs/guide/en/*.md`, `docs/guide/zh-cn/*.md`
- Produces: 20 篇高质量欧洲语言帮助文档。

- [ ] **Step 1: 编写 Deutsch (de) 全部 5 篇文档**
  - 对齐 Apple 德语标准术语（Einstellungen, App-Klon/Instanz, Symbolischer Link, Schlüsselbund, Sandbox-Isolation）。

- [ ] **Step 2: 编写 Français (fr) 全部 5 篇文档**
  - 对齐 Apple 法语标准术语（Réglages, Clone d'application, Lien symbolique, Trousseau d'accès, Bac à sable）。

- [ ] **Step 3: 编写 Español (es) 全部 5 篇文档**
  - 对齐 Apple 西班牙语标准术语（Ajustes, Clon de aplicación, Enlace simbólico, Acceso a Llaveros, Aislamiento en sandbox）。

- [ ] **Step 4: 编写 Русский (ru) 全部 5 篇文档**
  - 对齐 Apple 俄语标准术语（Настройки, Клон приложения, Символическая ссылка, Связка ключей, Песочница）。

- [ ] **Step 5: 运行全量 Markdown 格式校验**
  - 运行 `./scripts/test_deploy_doc.sh -l`，确保全部 35 篇文档 100% PASS。

- [ ] **Step 6: 提交 Task 3 成果**
  - `git add docs/guide/{de,fr,es,ru}/*.md`
  - `git commit -m "docs(i18n): add localized user guides for German, French, Spanish, and Russian"`

---

### Task 4: 根路由重定向与前端语言切换器联动升级

**Files:**
- Modify: `docs/guide/root_index.html`
- Modify: `docs/guide/*/javascripts/language-detector.js`

**Interfaces:**
- Consumes: 9 种语言的代码映射列表
- Produces: 能够无缝根据浏览器环境及手动选择进行精准路由跳转的前端逻辑。

- [ ] **Step 1: 升级 `docs/guide/root_index.html` 路由探测脚本**
  - 补充对 `zh-hant`, `ja`, `ko`, `de`, `fr`, `es`, `ru` 的语言前缀识别。
  - 严格按照：繁体 -> 简体 -> 日 -> 韩 -> 德 -> 法 -> 西 -> 俄 -> 英文回退 的顺序执行。

- [ ] **Step 2: 验证多语言前端切换联动与路径保留机制**
  - 检查各语种静态页面中的语言选择下拉菜单与当前路径拼接逻辑。

- [ ] **Step 3: 提交 Task 4 成果**
  - `git add docs/guide/root_index.html docs/guide/*/javascripts/language-detector.js`
  - `git commit -m "feat(i18n): update root language router and detector for 9-language matrix"`

---

### Task 5: 自动化构建管线升级与本地全量编译验收

**Files:**
- Modify: `.github/workflows/deploy-docs.yml`
- Test: `./scripts/test_deploy_doc.sh -b`
- Test: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/`

**Interfaces:**
- Consumes: 9 份 `zensical*.toml` 及全部 Markdown 源码
- Produces: 完整的 `docs/guide/site/` 编译产物，涵盖 9 个语言子目录及 HTML 文件。

- [ ] **Step 1: 更新 `.github/workflows/deploy-docs.yml` 编译步骤**
  - 改用动态通配构建或完整的 9 语种构建序列。

- [ ] **Step 2: 本地执行编译验收测试**
  - 执行 `./scripts/test_deploy_doc.sh -b`。
  - 验证 `docs/guide/site/` 目录下 `en/`, `zh/`, `zh-hant/`, `ja/`, `ko/`, `de/`, `fr/`, `es/`, `ru/` 均完整生成。
  - 验证 `docs/guide/site/index.html`、`CNAME` 与 `.nojekyll` 存在。

- [ ] **Step 3: 执行 Python 核心测试套件回归**
  - 运行 `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/`，确认 588 测试全过。

- [ ] **Step 4: 提交 Task 5 成果**
  - `git add .github/workflows/deploy-docs.yml`
  - `git commit -m "ci(docs): update deploy-docs workflow for 9-language matrix compilation"`

---

### Task 6: GitHub PR 合入与线上多语言部署验证

**Files:**
- Target Branch: `main`
- PR Branch: `docs/multilingual-expansion`

**Interfaces:**
- Consumes: 所有前置 Task 的提交
- Produces: 线上 `https://clone.aitobox.com` 9 语种就绪，GitHub Pages 与 `gh-pages` 分支同步更新。

- [ ] **Step 1: 推送分支至远端仓库**
  - `git push -u origin docs/multilingual-expansion`

- [ ] **Step 2: 创建 GitHub Pull Request**
  - 使用 `gh pr create` 提交 PR 至 `main`。

- [ ] **Step 3: 等待 CI 检查并合入**
  - 监控 `Run Pytest` 及安全分析检查通过。
  - 使用 `gh pr merge --squash` 合入主分支。

- [ ] **Step 4: 监控 GitHub Pages 部署并验证全语言在线访问**
  - 监控 `Deploy Documentation to GitHub Pages` 工作流执行成功。
  - 采用 `curl` 针对 9 种语言路径进行在线 HTTP 200 响应验证。
