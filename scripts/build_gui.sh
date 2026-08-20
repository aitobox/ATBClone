#!/usr/bin/env bash
# ==============================================================================
# ATBClone GUI Build Script — Briefcase macOS DMG Packaging
#
# Workflow:
#   1. briefcase create macOS   — scaffold the .app bundle structure
#   2. briefcase build  macOS   — compile/assemble the native .app
#   3. briefcase package macOS  — produce the signed .dmg installer
#   4. (optional) Notarize      — submit .dmg to Apple Notary Service
#
# Quick start:
#   bash scripts/build_gui.sh                       # auto-detect best cert / ad-hoc
#   bash scripts/build_gui.sh --skip-sign           # unsigned dev build
#   bash scripts/build_gui.sh --notarize -p <prof>  # full release build with notarization
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${PROJECT_ROOT}"

# ── Defaults ──────────────────────────────────────────────────────────────── #
TEAM_ID="WC7C59Q92T"
DEFAULT_CERT="Developer ID Application: Shanghai Tianzhi Cloud Information Technology Co., LTD (${TEAM_ID})"
SIGN_IDENTITY="${APPLE_SIGN_IDENTITY:-${DEFAULT_CERT}}"
SKIP_SIGN="${SKIP_SIGN:-0}"
DO_NOTARIZE=0
NOTARIZE_PROFILE="${APPLE_NOTARIZE_PROFILE:-}"
CLEAN_BUILD=0

# ── Help ──────────────────────────────────────────────────────────────────── #
show_help() {
    cat << 'HELP'
Usage: build_gui.sh [OPTIONS]

Build ATBClone GUI as a macOS .dmg installer via BeeWare Briefcase.

Options:
  -s, --sign <identity>    Code-signing identity (e.g. "Developer ID Application: ...")
                           Pass "-" for ad-hoc signing (local machine only).
  --adhoc                  Ad-hoc sign (fastest, requires no network/Apple timestamp server)
  --skip-sign              Skip all code signing (uses --adhoc-sign as fallback for macOS)
  -n, --notarize           Notarize the .dmg after packaging
  -p, --profile <name>     Keychain profile for notarytool (implies -n)
  -c, --clean              Remove previous Briefcase build/ directory first
  -h, --help               Show this help message

Environment Variables:
  APPLE_SIGN_IDENTITY         Override default signing identity
  SKIP_SIGN=1                 Skip signing
  APPLE_NOTARIZE_PROFILE      Default notarization keychain profile
  PYTHON                      Override Python executable path

Examples:
  # Fast local build (ad-hoc signing, no Apple timestamp network dependency):
  bash scripts/build_gui.sh --adhoc
  # Or:
  bash scripts/build_gui.sh --sign -

  # Production release: Developer ID sign + notarize
  bash scripts/build_gui.sh --sign "Developer ID Application: Shanghai Tianzhi Cloud Information Technology Co., LTD (WC7C59Q92T)" \
                            --notarize --profile "notary-profile"

  # Auto-detect Developer ID certificate from Keychain:
  bash scripts/build_gui.sh
HELP
}

# ── Argument Parsing ──────────────────────────────────────────────────────── #
while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help)     show_help; exit 0 ;;
        -s|--sign)     SIGN_IDENTITY="$2"; shift 2 ;;
        --adhoc)       SIGN_IDENTITY="-"; shift ;;
        --skip-sign)   SKIP_SIGN=1; SIGN_IDENTITY="-"; shift ;;
        -n|--notarize) DO_NOTARIZE=1; shift ;;
        -p|--profile|--keychain-profile)
                       NOTARIZE_PROFILE="$2"; DO_NOTARIZE=1; shift 2 ;;
        -c|--clean)    CLEAN_BUILD=1; shift ;;
        -*)  echo "[-] Unknown option: $1" >&2; show_help; exit 1 ;;
        *)   echo "[-] Unexpected argument: $1" >&2; show_help; exit 1 ;;
    esac
done

echo "======================================================"
echo "  🖥️  ATBClone GUI — macOS DMG Build"
echo "======================================================"

# ── 1. Locate Python ──────────────────────────────────────────────────────── #
if [[ -n "${PYTHON:-}" ]]; then
    PYTHON_BIN="${PYTHON}"
elif [[ -n "${CONDA_PREFIX:-}" && "${CONDA_PREFIX}" == *ATBClone* && -x "${CONDA_PREFIX}/bin/python" ]]; then
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
    PYTHON_BIN="$(command -v python3 || command -v python)"
fi

if [[ -z "${PYTHON_BIN:-}" || ! -x "${PYTHON_BIN}" ]]; then
    echo "[-] Error: Python not found. Run: conda activate ATBClone" >&2
    exit 1
fi

PY_VERSION=$("${PYTHON_BIN}" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PY_MAJOR=$(echo "${PY_VERSION}" | cut -d. -f1)
PY_MINOR=$(echo "${PY_VERSION}" | cut -d. -f2)
if [[ "${PY_MAJOR}" -lt 3 ]] || [[ "${PY_MAJOR}" -eq 3 && "${PY_MINOR}" -lt 12 ]]; then
    echo "[-] Error: Python 3.12+ required, found ${PY_VERSION}." >&2
    exit 1
fi
echo "[+] Python: ${PYTHON_BIN} (${PY_VERSION})"

# ── 2. Verify Briefcase ───────────────────────────────────────────────────── #
if ! "${PYTHON_BIN}" -m briefcase --version &>/dev/null; then
    echo "[*] Briefcase not found — installing..."
    "${PYTHON_BIN}" -m pip install "briefcase>=0.3.17"
fi
BRIEFCASE_VER=$("${PYTHON_BIN}" -m briefcase --version 2>&1 | head -1)
echo "[+] Briefcase: ${BRIEFCASE_VER}"

# ── 3. Version + arch ────────────────────────────────────────────────────── #
VERSION=$(grep -m 1 '^version = ' pyproject.toml | cut -d '"' -f2 || echo "0.1.0")
ARCH="$(uname -m)"
echo "[+] Version: v${VERSION}  Arch: ${ARCH}"

# ── 4. Optional clean ────────────────────────────────────────────────────── #
if [[ "${CLEAN_BUILD}" -eq 1 ]]; then
    echo "[*] Removing previous Briefcase build/ ..."
    rm -rf build/
fi

# ── 5. Resolve signing identity ───────────────────────────────────────────── #
resolve_identity() {
    # Exact match
    if security find-identity -v -p codesigning 2>/dev/null | grep -F -q "${SIGN_IDENTITY}"; then
        echo "${SIGN_IDENTITY}"; return 0
    fi
    # Match by Team ID
    local by_team
    by_team=$(security find-identity -v -p codesigning 2>/dev/null \
        | awk -F'"' "/${TEAM_ID}/ {print \$2; exit}" || true)
    if [[ -n "${by_team}" ]]; then echo "${by_team}"; return 0; fi
    # Any Developer cert
    local any_dev
    any_dev=$(security find-identity -v -p codesigning 2>/dev/null \
        | awk -F'"' '/(Developer ID Application:|Apple Development:|Mac Developer:)/ {print $2; exit}' || true)
    if [[ -n "${any_dev}" ]]; then echo "${any_dev}"; return 0; fi
    echo "-"
}

if [[ "${SKIP_SIGN}" -eq 0 && "${SIGN_IDENTITY}" != "-" ]]; then
    SIGN_IDENTITY=$(resolve_identity)
    if [[ "${SIGN_IDENTITY}" == "-" ]]; then
        echo "[!] No Developer ID certificate found. Using ad-hoc signing (local only)."
    else
        echo "[+] Signing identity: ${SIGN_IDENTITY}"
    fi
else
    echo "[+] Signing: ad-hoc (local machine only, no network timestamp required)"
    SIGN_IDENTITY="-"
fi

# ── 6. briefcase create ───────────────────────────────────────────────────── #
echo ""
echo "==> [1/3] briefcase create macOS ..."
PYTHONPATH="src" "${PYTHON_BIN}" -m briefcase create macOS

# ── 7. briefcase build ────────────────────────────────────────────────────── #
echo ""
echo "==> [2/3] briefcase build macOS ..."
PYTHONPATH="src" "${PYTHON_BIN}" -m briefcase build macOS

# Verify application icon in built app bundle
APP_BUNDLE=$(find build/ -name "ATBClone.app" -type d 2>/dev/null | head -1 || true)
if [[ -n "${APP_BUNDLE}" && -d "${APP_BUNDLE}" ]]; then
    if [[ -f "${APP_BUNDLE}/Contents/Resources/ATBClone.icns" || -f "${APP_BUNDLE}/Contents/Resources/logo.icns" || -f "${APP_BUNDLE}/Contents/Resources/icon.icns" ]]; then
        echo "[+] App bundle icon verified in: ${APP_BUNDLE}/Contents/Resources/"
    fi
fi

# ── 8. briefcase package  (produces .dmg) ────────────────────────────────── #
echo ""
echo "==> [3/3] briefcase package macOS (DMG) ..."

# Set up codesign retry wrapper shim so timestamp server timeouts automatically backoff and retry (2s..60s)
WRAPPER_BIN_DIR="$(mktemp -d -t codesign_shim_XXXXXX)"
ln -sf "${SCRIPT_DIR}/codesign_wrapper.py" "${WRAPPER_BIN_DIR}/codesign"
export PATH="${WRAPPER_BIN_DIR}:${PATH}"
trap 'rm -rf "${WRAPPER_BIN_DIR}"' EXIT

if [[ "${SKIP_SIGN}" -eq 1 || "${SIGN_IDENTITY}" == "-" ]]; then
    PYTHONPATH="src" "${PYTHON_BIN}" -m briefcase package macOS -p dmg --adhoc-sign --no-notarize
else
    PYTHONPATH="src" "${PYTHON_BIN}" -m briefcase package macOS -p dmg \
        --identity "${SIGN_IDENTITY}" \
        --no-notarize
fi

# ── 9. Locate produced .dmg ───────────────────────────────────────────────── #
DMG_PATH=""
for candidate in "dist/ATBClone-${VERSION}.dmg" "dist/ATBClone.dmg" dist/*.dmg; do
    if [[ -f "${candidate}" ]]; then
        DMG_PATH="${candidate}"; break
    fi
done
# Briefcase sometimes places it inside the build tree
if [[ -z "${DMG_PATH}" ]]; then
    DMG_PATH=$(find build/ -name "*.dmg" 2>/dev/null | head -1 || true)
fi
if [[ -z "${DMG_PATH}" || ! -f "${DMG_PATH}" ]]; then
    echo "[-] Error: .dmg not found after briefcase package." >&2
    exit 1
fi

DMG_SIZE=$(du -sh "${DMG_PATH}" | cut -f1)
echo ""
echo "======================================================"
echo "  DMG ready: ${DMG_PATH}  (${DMG_SIZE})"
echo "======================================================"

# ── 10. Verify signature ──────────────────────────────────────────────────── #
if [[ "${SKIP_SIGN}" -eq 0 ]]; then
    echo ""
    echo "==> Verifying DMG signature..."
    codesign --verify --deep --strict --verbose=2 "${DMG_PATH}" 2>&1 || true
    echo ""
    echo "--- Signature Summary ---"
    codesign -dv --verbose=4 "${DMG_PATH}" 2>&1 \
        | grep -E "(Identifier|Authority|Timestamp|TeamIdentifier|flags)" || true
    echo "-------------------------"
    if [[ "${SIGN_IDENTITY}" != "-" ]]; then
        echo "[*] Gatekeeper assessment..."
        spctl --assess --type install --verbose "${DMG_PATH}" 2>&1 || true
    fi
fi

# ── 11. Notarize (optional) ───────────────────────────────────────────────── #
if [[ "${DO_NOTARIZE}" -eq 1 ]]; then
    if [[ "${SKIP_SIGN}" -eq 1 || "${SIGN_IDENTITY}" == "-" ]]; then
        echo "[!] Notarization requires a Developer ID signature. Skipping." >&2
    else
        echo ""
        echo "==> Notarizing ${DMG_PATH} ..."
        if [[ -n "${NOTARIZE_PROFILE}" ]]; then
            xcrun notarytool submit "${DMG_PATH}" \
                --keychain-profile "${NOTARIZE_PROFILE}" --wait
        elif [[ -n "${APPLE_ID:-}" && -n "${APPLE_TEAM_ID:-}" && -n "${APPLE_APP_SPECIFIC_PASSWORD:-}" ]]; then
            xcrun notarytool submit "${DMG_PATH}" \
                --apple-id "${APPLE_ID}" \
                --team-id "${APPLE_TEAM_ID}" \
                --password "${APPLE_APP_SPECIFIC_PASSWORD}" \
                --wait
        else
            echo "[-] No notarization credentials provided." >&2
            echo "    Set up a keychain profile first:" >&2
            echo "      xcrun notarytool store-credentials \"notary-profile\" \\" >&2
            echo "          --apple-id developer@example.com \\" >&2
            echo "          --team-id ${TEAM_ID} \\" >&2
            echo "          --password <app-specific-password>" >&2
            echo "    Then re-run: bash scripts/build_gui.sh --notarize -p notary-profile" >&2
            exit 1
        fi

        echo "[*] Stapling notarization ticket..."
        xcrun stapler staple "${DMG_PATH}"
        echo "[+] Notarization stapled successfully."

        echo ""
        echo "--- Post-notarization Gatekeeper ---"
        spctl --assess --type install --verbose "${DMG_PATH}" 2>&1 || true
        echo "------------------------------------"
    fi
fi

# ── 12. Final Summary ─────────────────────────────────────────────────────── #
echo ""
echo "======================================================"
echo "  🎉  Build Complete"
echo "------------------------------------------------------"
printf "  DMG:     %s\n"  "${DMG_PATH}"
printf "  Size:    %s\n"  "${DMG_SIZE}"
printf "  Version: v%s\n" "${VERSION}"
printf "  Arch:    %s\n"  "${ARCH}"
if [[ "${SKIP_SIGN}" -eq 1 ]]; then
    echo "  Signed:  (unsigned)"
elif [[ "${SIGN_IDENTITY}" == "-" ]]; then
    echo "  Signed:  ad-hoc (local only)"
else
    printf "  Signed:  %s\n" "${SIGN_IDENTITY}"
    [[ "${DO_NOTARIZE}" -eq 1 ]] && echo "  Status:  Notarized"
fi
echo "======================================================"
echo ""
printf "  Install: open %s\n" "${DMG_PATH}"
echo ""
