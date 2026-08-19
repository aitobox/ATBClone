# ATBClone CLI Phase 2 — Implementation Plan

## 目标

在现有 CLI MVP 基础上，补全状态管理、生命周期命令、代理配置入口、向导模式和 Recipe 管理命令。

## 设计决策（来自访谈）

| 问题 | 决策 |
|------|------|
| 状态存储格式 | YAML（`~/.atbclone/clones.yaml`） |
| 代理配置入口 | `clone` 命令增加 `--proxy-host/port/type` 选项 |
| 新命令 | `list` + `remove` + `update` |
| `update` 策略 | 删除 .app → 重新 clone → 保留 data_dir |
| `list` 字段 | 名称、原APP、bundle_id、策略、创建时间、代理开关 |
| Wizard | `atbclone wizard` 交互引导模式 |
| Recipe 子命令 | `recipe list` + `recipe show <bundle_id>` |
| GUI | 第一期不加，后期 PySide6 封装 |

---

## Global Constraints

- Python 3.10+, `conda run -n ATBClone` for Python env
- Test command: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/ -v`
- 状态文件: `~/.atbclone/clones.yaml`
- 不破坏现有 61 个测试

---

## 文件全景

### 新建
- `src/atbclone/core/state.py` — 状态模型 + 读写 YAML
- `src/atbclone/cli/cmd_list.py`
- `src/atbclone/cli/cmd_remove.py`
- `src/atbclone/cli/cmd_update.py`
- `src/atbclone/cli/cmd_wizard.py`
- `src/atbclone/cli/cmd_recipe.py`
- `tests/test_state.py`
- `tests/test_cmd_list.py`
- `tests/test_cmd_remove.py`
- `tests/test_cmd_update.py`
- `tests/test_cmd_recipe.py`

### 修改
- `src/atbclone/cli/cmd_clone.py` — 添加 proxy 选项，clone 成功后写状态
- `src/atbclone/cli/main.py` — 注册新命令

---

### Task 1: 状态管理模块

**Files:**
- Create: `src/atbclone/core/state.py`
- Create: `tests/test_state.py`

**CloneRecord 模型:**
```python
@dataclass
class CloneRecord:
    clone_name: str       # e.g. "微信2"
    source_app: str       # e.g. "微信"
    bundle_id: str        # e.g. "com.tencent.xinWeChat"
    strategy: str         # "hard_clone" | "soft_clone"
    dest_path: str        # e.g. "/Users/.../Applications/微信2.app"
    data_dir: str         # e.g. "/Users/.../.atbclone/Data/微信2"
    created_at: str       # ISO 8601
    proxy_enabled: bool
    proxy_summary: str    # e.g. "" or "http://127.0.0.1:1080"
```

**StateManager 接口:**
- `StateManager.load() -> list[CloneRecord]`
- `StateManager.save(records: list[CloneRecord])`
- `StateManager.add(record: CloneRecord)`
- `StateManager.remove(clone_name: str) -> bool`
- `StateManager.get(clone_name: str) -> CloneRecord | None`

- [ ] 写失败测试 → 实现 → 验证通过
- [ ] `git commit -m "feat: add state management module (YAML)"`

---

### Task 2: clone 命令增加 proxy 选项 + 写状态

**修改 `cmd_clone.py`:**
```
--proxy-host TEXT     代理地址（覆盖 recipe 默认值）
--proxy-port INTEGER  代理端口
--proxy-type [http|socks5]
```

- 若提供 `--proxy-host`，则在 task.recipe.proxy 上设置 enabled=True, host=..., port=...
- clone 成功后调用 `StateManager.add(record)` 写入状态

- [ ] 更新 `tests/test_cmd_clone.py` 新增 proxy option 测试
- [ ] `git commit -m "feat(clone): add proxy CLI options and state persistence"`

---

### Task 3: list 命令

**`atbclone list`** — 用 Rich Table 展示所有分身

列：名称 | 原APP | bundle_id | 策略 | 创建时间 | 代理
无分身时打印友好提示。

- [ ] `tests/test_cmd_list.py`
- [ ] `git commit -m "feat: add list command"`

---

### Task 4: remove 命令

**`atbclone remove <CLONE_NAME>`**

流程：
1. 从状态文件找到记录
2. `rm -rf <dest_path>`（需要 admin 时用 osascript）
3. 可选：`--with-data` 同时删除 data_dir
4. 从状态文件移除记录

选项：`--with-data / --no-with-data`（默认不删数据，只删 .app）

- [ ] `tests/test_cmd_remove.py`
- [ ] `git commit -m "feat: add remove command"`

---

### Task 5: update 命令

**`atbclone update <CLONE_NAME>`**

流程：
1. 从状态文件读取原始克隆参数
2. `rm -rf <dest_path>`（保留 data_dir）
3. 用相同参数重新 clone（source 原始 .app 路径）
4. 更新状态文件的 created_at

- [ ] `tests/test_cmd_update.py`
- [ ] `git commit -m "feat: add update command"`

---

### Task 6: recipe 子命令组

**`atbclone recipe list`** — Rich Table 展示所有内置配方
列：bundle_id | 名称 | 策略 | strip_sandbox

**`atbclone recipe show <bundle_id>`** — YAML 格式完整输出

- [ ] `tests/test_cmd_recipe.py`
- [ ] `git commit -m "feat: add recipe list/show subcommands"`

---

### Task 7: wizard 交互引导

**`atbclone wizard`**

流程（用 Click.prompt / inquirer 风格）：
1. 请输入 .app 路径（或拖入）
2. 自动检测 bundle_id，显示匹配的 recipe
3. 询问分身名称（默认自动编号）
4. 询问输出目录（默认 ~/Applications）
5. 是否配置代理？若是，询问地址/端口/类型
6. 确认信息 → 执行 clone

只使用 `click.prompt()` 和 `click.confirm()`，无需额外依赖。

- [ ] `git commit -m "feat: add wizard interactive command"`

---

## Verification Plan

```bash
# 全量测试
PYTHONPATH=src conda run -n ATBClone python -m pytest tests/ -v

# 手动验证
atbclone clone /Applications/WeChat.app
atbclone list
atbclone remove 微信2
atbclone update 微信2
atbclone recipe list
atbclone recipe show com.tencent.xinWeChat
atbclone wizard
```

## 说明

> [!NOTE]
> `update` 命令需要记录 source_app 的**原始路径**（`/Applications/WeChat.app`），因此 `CloneRecord` 需要包含 `source_path: str` 字段。Task 1 实现时需要包含该字段。

> [!IMPORTANT]
> `remove --with-data` 是不可逆操作，必须有确认提示（`click.confirm`）。
