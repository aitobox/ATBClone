# ATBCloneCli Packaging Script Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Provide an automated packaging script (`scripts/build_cli.sh`) using Nuitka to compile the ATBClone CLI into a single standalone binary `dist/ATBCloneCli` for macOS arm64.

**Architecture:** A shell script `scripts/build_cli.sh` wraps the Nuitka compiler invocation with appropriate module inclusions (`atbclone`, `click`, `rich`, `pydantic`, `yaml`) and package data (`recipes/builtin/*.yaml`). It handles dependency pre-checks, build artifact cleanup, and post-build executable validation.

**Tech Stack:** Bash, Nuitka (>=2.0), Python 3.12+, Pytest, macOS arm64.

## Global Constraints

- Target macOS arm64 single-file executable (`--onefile`).
- Output executable named `ATBCloneCli` in `dist/` directory.
- Must bundle all builtin recipe YAML definitions inside `atbclone.recipes.builtin`.
- Clean error reporting if Python or Nuitka environment is incomplete.

---

### Task 1: Update `.gitignore` for Build Artifacts

**Files:**
- Modify: `.gitignore:48-61`

**Interfaces:**
- Consumes: Existing `.gitignore`
- Produces: Updated `.gitignore` with `dist/`, `*.build/`, `*.dist/`, `*.onefile-build/`

- [ ] **Step 1: Check existing .gitignore content**

Run: `grep "dist/" .gitignore || true`

- [ ] **Step 2: Add packaging build patterns to .gitignore**

Add:
```
# Nuitka / Python packaging outputs
dist/
*.build/
*.dist/
*.onefile-build/
```

- [ ] **Step 3: Verify .gitignore syntax**

Run: `git check-ignore -v dist/ATBCloneCli || true`
Expected: shows `.gitignore` match for `dist/`

- [ ] **Step 4: Commit**

```bash
git add .gitignore
git commit -m "build: add dist and nuitka build artifacts to gitignore"
```

---

### Task 2: Add Packaging Script Unit & Syntax Tests

**Files:**
- Create: `tests/test_build_script.py`

**Interfaces:**
- Consumes: `scripts/build_cli.sh`
- Produces: Automated pytest test validating script permissions, bash syntax correctness, and key Nuitka flags

- [ ] **Step 1: Write the failing test**

```python
"""Tests for build_cli.sh script integrity and syntax."""

import os
import subprocess
from pathlib import Path


def test_build_script_exists_and_executable():
    root = Path(__file__).parent.parent
    script = root / "scripts" / "build_cli.sh"
    assert script.exists(), "scripts/build_cli.sh does not exist"
    assert os.access(script, os.X_OK), "scripts/build_cli.sh is not executable"


def test_build_script_bash_syntax():
    root = Path(__file__).parent.parent
    script = root / "scripts" / "build_cli.sh"
    result = subprocess.run(
        ["bash", "-n", str(script)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Bash syntax error: {result.stderr}"


def test_build_script_contains_required_flags():
    root = Path(__file__).parent.parent
    script = root / "scripts" / "build_cli.sh"
    content = script.read_text(encoding="utf-8")
    assert "--onefile" in content
    assert "ATBCloneCli" in content
    assert "--include-package=atbclone" in content
    assert "--include-package-data=atbclone" in content
    assert "src/atbclone/cli/main.py" in content
```

- [ ] **Step 2: Run test to verify it fails**

Run: `conda run -n ATBClone python -m pytest tests/test_build_script.py -v`
Expected: FAIL with "scripts/build_cli.sh does not exist"

- [ ] **Step 3: Commit test file**

```bash
git add tests/test_build_script.py
git commit -m "test: add test_build_script for packaging verification"
```

---

### Task 3: Implement `scripts/build_cli.sh`

**Files:**
- Create: `scripts/build_cli.sh`

**Interfaces:**
- Consumes: `src/atbclone/cli/main.py`, `src/atbclone/recipes/builtin/*.yaml`, `pyproject.toml`
- Produces: `dist/ATBCloneCli` standalone executable

- [ ] **Step 1: Write `scripts/build_cli.sh`**

```bash
#!/usr/bin/env bash
# ==============================================================================
# ATBCloneCli Build Script (Nuitka macOS arm64 onefile)
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${PROJECT_ROOT}"

echo "==> Building ATBCloneCli standalone executable..."

# 1. Check Python environment
PYTHON_BIN="$(which python || which python3)"
if [[ -z "${PYTHON_BIN}" ]]; then
    echo "[-] Error: Python is not found in PATH." >&2
    exit 1
fi
echo "[+] Using Python: ${PYTHON_BIN}"

# 2. Check / Install Nuitka
if ! "${PYTHON_BIN}" -c "import nuitka" 2>/dev/null; then
    echo "[*] Nuitka not found. Installing nuitka..."
    "${PYTHON_BIN}" -m pip install "nuitka>=2.0"
fi
echo "[+] Nuitka is available."

# 3. Clean previous build artifacts
echo "[*] Cleaning previous build outputs..."
rm -rf dist/ATBCloneCli dist/ATBCloneCli.build dist/ATBCloneCli.dist dist/ATBCloneCli.onefile-build

# 4. Extract version from pyproject.toml
VERSION=$(grep -m 1 '^version =' pyproject.toml | cut -d '"' -f 2 || echo "0.1.0")
echo "[+] Building ATBCloneCli v${VERSION}..."

# 5. Run Nuitka Build
echo "[*] Running Nuitka compiler..."
PYTHONPATH=src "${PYTHON_BIN}" -m nuitka \
    --onefile \
    --output-filename=ATBCloneCli \
    --output-dir=dist \
    --include-package=atbclone \
    --include-package-data=atbclone \
    --include-package=click \
    --include-package=rich \
    --include-package=pydantic \
    --include-package=pydantic_core \
    --include-package=yaml \
    --assume-yes-for-downloads \
    --remove-output \
    src/atbclone/cli/main.py

# 6. Ensure executable permissions
chmod +x dist/ATBCloneCli

# 7. Post-build validation
echo "==> Validating build artifact..."
if [[ -f "dist/ATBCloneCli" ]]; then
    FILE_SIZE=$(ls -lh dist/ATBCloneCli | awk '{print $5}')
    echo "[✔] Build successful: dist/ATBCloneCli (${FILE_SIZE})"
    echo "[*] Testing execution (--help)..."
    ./dist/ATBCloneCli --help | head -n 10
    echo ""
    echo "[✔] ATBCloneCli is ready to distribute!"
else
    echo "[-] Error: dist/ATBCloneCli was not created." >&2
    exit 1
fi
```

- [ ] **Step 2: Set executable bit**

Run: `chmod +x scripts/build_cli.sh`

- [ ] **Step 3: Run unit tests to verify script integrity**

Run: `conda run -n ATBClone python -m pytest tests/test_build_script.py -v`
Expected: PASS (all 3 tests pass)

- [ ] **Step 4: Commit**

```bash
git add scripts/build_cli.sh
git commit -m "feat: add build_cli.sh Nuitka packaging script"
```

---

### Task 4: Full Test Suite Verification

**Files:**
- Test: `tests/`

**Interfaces:**
- Consumes: All tests in `tests/`
- Produces: Test suite verification report

- [ ] **Step 1: Run full pytest suite**

Run: `PYTHONPATH=src conda run -n ATBClone python -m pytest tests/ -v`
Expected: All tests PASS

- [ ] **Step 2: Commit any final cleanup**

```bash
git status
```
