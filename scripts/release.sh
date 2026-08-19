#!/usr/bin/env bash
# ==============================================================================
# ATBClone Release Automation Script
# Steps:
#   1. Validate semantic version x.y.z
#   2. Run pytest test suite
#   3. Update version in pyproject.toml & src/atbclone/__init__.py
#   4. Verify multilingual ReleaseNotes in docs/release/
#   5. Commit release to git and create annotated tag v<version>
#   6. Compile standalone binary via scripts/build_cli.sh (+ Apple Code Signing)
#   7. Verify binary execution, version output, and signature
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${PROJECT_ROOT}"

TARGET_VERSION=""
BUILD_ARGS=()

show_help() {
    cat << EOF
Usage: $(basename "$0") <x.y.z> [BUILD_OPTIONS]

Automate complete release workflow for ATBClone.

Arguments:
  <x.y.z>                     Semantic version number (e.g. 0.2.0 or v0.2.0)

Build & Signing Options (passed to build_cli.sh):
  -s, --sign <identity>       Apple Code Signing Identity (e.g. "Developer ID Application: ...")
  --skip-sign                 Skip code signing during binary build
  -n, --notarize              Run Apple Notarization after build
  -p, --profile <name>        Keychain profile for notarization
  -h, --help                  Show this help message

Examples:
  bash scripts/release.sh 0.2.0
  bash scripts/release.sh 0.2.0 --sign "Developer ID Application: Shanghai Tianzhi Cloud Information Technology Co., LTD (WC7C59Q92T)"
  bash scripts/release.sh 0.2.0 --notarize --profile "notary-profile"
EOF
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help)
            show_help
            exit 0
            ;;
        -s|--sign|-p|--profile|--keychain-profile)
            BUILD_ARGS+=("$1" "$2")
            shift 2
            ;;
        --skip-sign|-n|--notarize)
            BUILD_ARGS+=("$1")
            shift
            ;;
        -*)
            echo "[-] Unknown option: $1" >&2
            show_help
            exit 1
            ;;
        *)
            if [[ -z "${TARGET_VERSION}" ]]; then
                TARGET_VERSION="$1"
            else
                echo "[-] Unexpected extra argument: $1" >&2
                show_help
                exit 1
            fi
            shift
            ;;
    esac
done

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

if [[ -n "${PYTHON:-}" ]]; then
    PYTHON_BIN="${PYTHON}"
elif [[ -n "${CONDA_PREFIX:-}" && "${CONDA_PREFIX}" == *"ATBClone"* && -x "${CONDA_PREFIX}/bin/python" ]]; then
    PYTHON_BIN="${CONDA_PREFIX}/bin/python"
elif [[ -x "/opt/homebrew/anaconda3/envs/ATBClone/bin/python" ]]; then
    PYTHON_BIN="/opt/homebrew/anaconda3/envs/ATBClone/bin/python"
elif [[ -x "${HOME}/anaconda3/envs/ATBClone/bin/python" ]]; then
    PYTHON_BIN="${HOME}/anaconda3/envs/ATBClone/bin/python"
elif [[ -x "${HOME}/miniconda3/envs/ATBClone/bin/python" ]]; then
    PYTHON_BIN="${HOME}/miniconda3/envs/ATBClone/bin/python"
elif [[ -x "${HOME}/miniforge3/envs/ATBClone/bin/python" ]]; then
    PYTHON_BIN="${HOME}/miniforge3/envs/ATBClone/bin/python"
elif [[ -n "${CONDA_PREFIX:-}" && -x "${CONDA_PREFIX}/bin/python" ]]; then
    PYTHON_BIN="${CONDA_PREFIX}/bin/python"
else
    PYTHON_BIN="$(which python || which python3)"
fi

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

# 5. Build Standalone Executable with Code Signing
echo "==> [Step 5/6] Building standalone binary..."
if [[ ${#BUILD_ARGS[@]} -gt 0 ]]; then
    bash scripts/build_cli.sh "${BUILD_ARGS[@]}"
else
    bash scripts/build_cli.sh
fi

# 6. Verify Build & Signature
echo "==> [Step 6/6] Verifying built binary & signature..."
if [[ -f "dist/ATBCloneCli" ]]; then
    echo "[*] Running ./dist/ATBCloneCli version..."
    ./dist/ATBCloneCli version
    echo ""
    echo "[*] Verifying binary signature status..."
    codesign -dv --verbose=2 dist/ATBCloneCli 2>&1 | grep -E "(Identifier|Authority|Timestamp|TeamIdentifier)" || true
    echo ""
    echo "======================================================"
    echo "  🎉 Successfully released ATBClone ${TAG_NAME}!"
    echo "  Executable: ${PROJECT_ROOT}/dist/ATBCloneCli"
    echo "======================================================"
else
    echo "[-] Error: dist/ATBCloneCli was not created." >&2
    exit 1
fi
