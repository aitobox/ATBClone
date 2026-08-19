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
PYTHON_BIN="${PYTHON:-$(which python || which python3)}"
if [[ -z "${PYTHON_BIN}" ]]; then
    echo "[-] Error: Python is not found in PATH." >&2
    exit 1
fi
echo "[+] Using Python: ${PYTHON_BIN}"

# Verify Python version is 3.12+
PY_VERSION=$("${PYTHON_BIN}" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PY_MAJOR=$(echo "${PY_VERSION}" | cut -d. -f1)
PY_MINOR=$(echo "${PY_VERSION}" | cut -d. -f2)
if [[ "${PY_MAJOR}" -lt 3 ]] || [[ "${PY_MAJOR}" -eq 3 && "${PY_MINOR}" -lt 12 ]]; then
    echo "[-] Error: Python 3.12+ required, found ${PY_VERSION}." >&2
    echo "    Tip: Run: conda activate ATBClone" >&2
    exit 1
fi
echo "[+] Python version: ${PY_VERSION}"

# 2. Check / Install Nuitka
if ! "${PYTHON_BIN}" -c "import nuitka" 2>/dev/null; then
    echo "[*] Nuitka not found. Installing nuitka..."
    "${PYTHON_BIN}" -m pip install "nuitka>=2.0"
fi
echo "[+] Nuitka is available."

# 3. Clean previous build artifacts
echo "[*] Cleaning previous build outputs..."
rm -rf dist/
mkdir -p dist/

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
    --python-flag=no_site \
    --assume-yes-for-downloads \
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
