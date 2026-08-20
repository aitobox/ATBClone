#!/usr/bin/env bash
# ==============================================================================
# ATBCloneCli Build Script (Nuitka macOS arm64 onefile + Apple Code Signing)
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${PROJECT_ROOT}"

# Default parameters
TEAM_ID="WC7C59Q92T"

# Code signing certificate for Direct Distribution (Developer ID Application)
DEFAULT_DEV_ID_CERT="Developer ID Application: Shanghai Tianzhi Cloud Information Technology Co., LTD (${TEAM_ID})"
DEV_ID_CERT="${DEV_ID_CERT:-$DEFAULT_DEV_ID_CERT}"

SIGN_IDENTITY="${APPLE_SIGN_IDENTITY:-$DEV_ID_CERT}"
SKIP_SIGN="${SKIP_SIGN:-0}"
DO_NOTARIZE=0
NOTARIZE_PROFILE="${APPLE_NOTARIZE_PROFILE:-}"
ENTITLEMENTS_FILE="${SCRIPT_DIR}/entitlements.plist"

show_help() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS]

Build ATBCloneCli standalone binary for macOS with Nuitka and Apple code signing.

Options:
  -s, --sign <identity>       Code signing identity (e.g. "Developer ID Application: Name (TEAMID)" or "-")
  --skip-sign                 Skip macOS code signing step
  -n, --notarize              Run Apple Notarization after successful build and sign
  -p, --profile <name>        Keychain profile for Apple Notarization (used with --notarize)
  -h, --help                  Show this help message

Environment Variables:
  APPLE_SIGN_IDENTITY         Default signing identity
  SKIP_SIGN                   Set to 1 to skip signing
  APPLE_NOTARIZE_PROFILE      Default notarization keychain profile

Examples:
  # Build and auto-detect Apple Developer certificate (or fallback to ad-hoc)
  bash scripts/build_cli.sh

  # Build and sign with specific Developer ID
  bash scripts/build_cli.sh --sign "Developer ID Application: My Company (AB12CD34EF)"

  # Build and sign ad-hoc (local use only)
  bash scripts/build_cli.sh --sign -

  # Build, sign, and submit for Apple Notarization
  bash scripts/build_cli.sh --notarize --profile "notary-profile"
EOF
}

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help)
            show_help
            exit 0
            ;;
        -s|--sign)
            SIGN_IDENTITY="$2"
            shift 2
            ;;
        --skip-sign)
            SKIP_SIGN=1
            shift
            ;;
        -n|--notarize)
            DO_NOTARIZE=1
            shift
            ;;
        -p|--profile|--keychain-profile)
            NOTARIZE_PROFILE="$2"
            DO_NOTARIZE=1
            shift 2
            ;;
        -*)
            echo "[-] Unknown option: $1" >&2
            show_help
            exit 1
            ;;
        *)
            echo "[-] Unexpected argument: $1" >&2
            show_help
            exit 1
            ;;
    esac
done

echo "======================================================"
echo "  🚀 Building ATBCloneCli Standalone Executable"
echo "======================================================"

# 1. Check Python environment
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

if [[ -z "${PYTHON_BIN}" || ! -x "${PYTHON_BIN}" ]]; then
    echo "[-] Error: Python is not found in PATH or active conda environment." >&2
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
echo "[+] Target version: v${VERSION}"

# 5. Run Nuitka Build
echo "==> Compiling with Nuitka..."
PYTHONNOUSERSITE=1 PYTHONPATH=src "${PYTHON_BIN}" -m nuitka \
    --onefile \
    --output-filename=ATBCloneCli \
    --output-dir=dist \
    --macos-app-icon=resource/images/logo.icns \
    --include-data-dir=resource=resource \
    --include-package=atbclone \
    --include-package-data=atbclone \
    --include-package=click \
    --include-package=rich \
    --include-package=pydantic \
    --include-package=pydantic_core \
    --include-package=yaml \
    --product-version="${VERSION}" \
    --python-flag=no_site \
    --assume-yes-for-downloads \
    src/atbclone_entry.py

# 6. Ensure executable permissions
chmod +x dist/ATBCloneCli

# 7. Apple Code Signing
if [[ "${SKIP_SIGN}" -eq 1 ]]; then
    echo "[*] Code signing skipped as requested (--skip-sign)."
else
    echo "==> Performing macOS Code Signing..."

    # Verify if specified or default SIGN_IDENTITY exists in Keychain
    if [[ "${SIGN_IDENTITY}" != "-" ]]; then
        echo "[*] Checking code signing identity: ${SIGN_IDENTITY}..."
        CERT_FOUND=0
        if security find-identity -v -p codesigning 2>/dev/null | grep -F -q "${SIGN_IDENTITY}"; then
            CERT_FOUND=1
        elif security find-identity -v -p codesigning 2>/dev/null | grep -F -q "${TEAM_ID}"; then
            # Match by TEAM_ID if exact name is slightly different
            MATCHED_CERT=$(security find-identity -v -p codesigning 2>/dev/null | awk -F'"' "/${TEAM_ID}/ {print \$2; exit}")
            if [[ -n "${MATCHED_CERT}" ]]; then
                SIGN_IDENTITY="${MATCHED_CERT}"
                CERT_FOUND=1
            fi
        fi

        if [[ "${CERT_FOUND}" -eq 1 ]]; then
            echo "[+] Found valid certificate in Keychain: ${SIGN_IDENTITY}"
        else
            echo "[!] Certificate '${SIGN_IDENTITY}' not found in Keychain."
            # Check if any other developer certificate is available
            AUTO_DEV=$(security find-identity -v -p codesigning 2>/dev/null | awk -F'"' '/(Developer ID Application:|Apple Development:|Mac Developer:)/ {print $2; exit}' || true)
            if [[ -n "${AUTO_DEV}" ]]; then
                echo "[*] Using alternative certificate found in Keychain: ${AUTO_DEV}"
                SIGN_IDENTITY="${AUTO_DEV}"
            else
                echo "[!] Falling back to ad-hoc signature (-)."
                echo "    Tip: To sign for distribution, ensure '${DEFAULT_DEV_ID_CERT}' is installed in Keychain."
                SIGN_IDENTITY="-"
            fi
        fi
    fi

    if [[ "${SIGN_IDENTITY}" == "-" ]]; then
        echo "[*] Signing with ad-hoc identity (-)..."
        codesign --force --sign - dist/ATBCloneCli
    else
        echo "[*] Signing with identity: ${SIGN_IDENTITY}"
        echo "[*] Applying Hardened Runtime (--options runtime) and Entitlements (${ENTITLEMENTS_FILE})..."
        codesign --force \
                 --options runtime \
                 --timestamp \
                 --entitlements "${ENTITLEMENTS_FILE}" \
                 --sign "${SIGN_IDENTITY}" \
                 dist/ATBCloneCli
    fi

    # Verify signature
    echo "[*] Verifying code signature..."
    codesign --verify --deep --strict --verbose=2 dist/ATBCloneCli
    echo "[✔] Code signature verified."
    echo ""
    echo "--- Code Signature Details ---"
    codesign -dv --verbose=4 dist/ATBCloneCli 2>&1 | grep -E "(Identifier|Authority|Timestamp|TeamIdentifier|flags)" || true
    echo "------------------------------"

    # Check Gatekeeper assessment
    if [[ "${SIGN_IDENTITY}" != "-" ]]; then
        echo "[*] Checking Gatekeeper assessment..."
        spctl --assess --type execute --verbose dist/ATBCloneCli 2>&1 || true
    fi
fi

# 8. Post-build validation
echo ""
echo "==> Validating build artifact..."
if [[ -f "dist/ATBCloneCli" ]]; then
    FILE_SIZE=$(ls -lh dist/ATBCloneCli | awk '{print $5}')
    echo "[✔] Build successful: dist/ATBCloneCli (${FILE_SIZE})"
    echo "[*] Testing execution (--help)..."
    ./dist/ATBCloneCli --help | head -n 10
    echo ""
    echo "[✔] ATBCloneCli is ready!"
else
    echo "[-] Error: dist/ATBCloneCli was not created." >&2
    exit 1
fi

# 9. Apple Notarization (optional)
if [[ "${DO_NOTARIZE}" -eq 1 ]]; then
    echo ""
    echo "==> Running Apple Notarization workflow..."
    NOTARIZE_ARGS=()
    if [[ -n "${NOTARIZE_PROFILE}" ]]; then
        NOTARIZE_ARGS+=("--profile" "${NOTARIZE_PROFILE}")
    fi
    bash scripts/notarize.sh "${NOTARIZE_ARGS[@]}" dist/ATBCloneCli
fi
