#!/usr/bin/env bash
# ==============================================================================
# ATBClone Release Automation Script
# Steps:
#   1. Validate semantic version x.y.z
#   2. Run pytest test suite
#   3. Update version in pyproject.toml & src/atbclone/__init__.py
#   4. Verify multilingual ReleaseNotes in docs/release/
#   5. Commit release to git and create annotated tag v<version>
#   6. Compile standalone binary via scripts/build_cli.sh
#   7. Verify binary execution and version output
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${PROJECT_ROOT}"

TARGET_VERSION="${1:-}"

if [[ -z "${TARGET_VERSION}" ]]; then
    echo "[-] Usage: $0 <x.y.z> (e.g. $0 0.2.0)" >&2
    exit 1
fi

# Strip optional leading 'v'
TARGET_VERSION="${TARGET_VERSION#v}"

# Validate x.y.z format
if ! [[ "${TARGET_VERSION}" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "[-] Error: Version '${TARGET_VERSION}' must be in x.y.z format (e.g. 0.2.0)." >&2
    exit 1
fi

TAG_NAME="v${TARGET_VERSION}"

# Check if tag already exists
if git rev-parse -q --verify "refs/tags/${TAG_NAME}" >/dev/null; then
    echo "[-] Error: Git tag '${TAG_NAME}' already exists!" >&2
    exit 1
fi

echo "======================================================"
echo "  🚀 Starting ATBClone Release Workflow: ${TAG_NAME}"
echo "======================================================"

PYTHON_BIN="$(which python || which python3)"

# 1. Run Tests
echo "==> [Step 1/6] Running test suite..."
PYTHONPATH=src "${PYTHON_BIN}" -m pytest tests/ -q
echo "[✔] All tests passed."

# 2. Update Version
echo "==> [Step 2/6] Updating version to ${TARGET_VERSION}..."
PYTHONPATH=src "${PYTHON_BIN}" scripts/manage_version.py "${TARGET_VERSION}"
echo "[✔] Version files updated."

# 3. Check Multilingual ReleaseNotes
echo "==> [Step 3/6] Verifying multilingual ReleaseNotes in docs/release/..."
if ! PYTHONPATH=src "${PYTHON_BIN}" scripts/manage_version.py --check-notes "${TARGET_VERSION}"; then
    echo "[-] Error: Please update all 9 ReleaseNotes in docs/release/ for ${TAG_NAME} before releasing." >&2
    exit 1
fi
echo "[✔] All 9 ReleaseNotes contain entries for ${TAG_NAME}."

# 4. Git Commit & Tag
echo "==> [Step 4/6] Committing release and creating tag ${TAG_NAME}..."
git add pyproject.toml src/atbclone/__init__.py Readme.md Readme_zh.md docs/release/*.md
# Commit only if there are staged changes
if ! git diff --cached --quiet; then
    git commit -m "release: ${TAG_NAME}"
else
    echo "[*] No file diffs to commit."
fi

git tag -a "${TAG_NAME}" -m "Release ${TAG_NAME}"
echo "[✔] Tag ${TAG_NAME} created."

# 5. Build Standalone Executable
echo "==> [Step 5/6] Building standalone binary..."
bash scripts/build_cli.sh

# 6. Verify Build
echo "==> [Step 6/6] Verifying built binary..."
if [[ -f "dist/ATBCloneCli" ]]; then
    echo "[*] Running ./dist/ATBCloneCli version..."
    ./dist/ATBCloneCli version
    echo ""
    echo "======================================================"
    echo "  🎉 Successfully released ATBClone ${TAG_NAME}!"
    echo "  Executable: ${PROJECT_ROOT}/dist/ATBCloneCli"
    echo "======================================================"
else
    echo "[-] Error: dist/ATBCloneCli was not created." >&2
    exit 1
fi
