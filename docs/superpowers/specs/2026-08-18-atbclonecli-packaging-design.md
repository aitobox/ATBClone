# ATBCloneCli 打包脚本设计

## 背景与目标

ATBClone 是一个 Python CLI 工具（基于 Click 框架），当前通过 conda 环境运行。
目标是提供一个打包脚本，将整个项目编译为单一可执行文件 `ATBCloneCli`，
分发给其他 macOS 用户使用——无需目标机器安装 Python 或 conda 环境。

## 技术选型

| 维度 | 决策 |
|------|------|
| 打包工具 | **Nuitka**（编译为原生 C，启动速度快） |
| 输出格式 | **单文件可执行**（`--onefile`） |
| 目标平台 | **macOS arm64**（Apple Silicon） |
| 触发方式 | 手动运行 shell 脚本 |

> **为何不选 universal2？** Nuitka 无法在单台 arm64 Mac 上交叉编译 x86_64，
> 生成 universal2 需要两台机器 + lipo 合并，超出当前需求范围。

## 文件结构

```
scripts/
  build_cli.sh              <- 主打包脚本
dist/
  ATBCloneCli               <- 输出可执行文件（gitignored）
```

dist/ 目录将加入 .gitignore。

## 打包脚本设计（scripts/build_cli.sh）

### 执行流程

```
1. 检查环境（nuitka 是否可用）
2. 若 nuitka 未安装，自动 pip install nuitka
3. 清理上次构建产物（dist/ 目录）
4. 从 pyproject.toml 读取版本号
5. 执行 nuitka 编译
6. chmod +x dist/ATBCloneCli
7. 验证：运行 dist/ATBCloneCli --help
8. 打印成功信息与文件大小
```

### 关键 Nuitka 参数

```bash
python -m nuitka \
  --onefile \
  --output-filename=ATBCloneCli \
  --output-dir=dist \
  --include-package=atbclone \
  --include-package-data=atbclone \
  --include-package=click \
  --include-package=rich \
  --include-package=pydantic \
  --include-package=yaml \
  --python-flag=no_site \
  --assume-yes-for-downloads \
  src/atbclone/cli/main.py
```

### 设计原则

- **幂等性**：每次执行前清理 dist/，确保结果一致
- **明确报错**：环境不满足时打印明确提示并退出
- **版本注入**：通过 grep 从 pyproject.toml 提取版本号，打印在输出信息中
- **一键运行**：bash scripts/build_cli.sh，无需额外参数

## 入口点确认

pyproject.toml 中已定义：

```toml
[project.scripts]
atbclone = "atbclone.cli.main:cli"
```

Nuitka 将直接编译 src/atbclone/cli/main.py 中的 cli 函数作为入口。

## 验证计划

脚本末尾自动执行：

```bash
dist/ATBCloneCli --help    # 验证可执行且命令解析正常
ls -lh dist/ATBCloneCli    # 显示文件大小
```

## 不在此次范围内

- CI/CD 自动打包（可后续集成 GitHub Actions）
- universal2 / x86_64 交叉编译
- macOS 代码签名（codesign / notarize）
- Homebrew tap 分发
