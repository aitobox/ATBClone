#!/usr/bin/env bash
# ==============================================================================
# ATBClone Release Packaging Script (arm64 CLI tar.gz + GUI dmg)
# ==============================================================================
# Builds and packages:
#   1. ATBCloneCli-${VERSION}-arm64.tar.gz (standalone arm64 CLI executable)
#   2. ATBClone-${VERSION}-arm64.dmg       (macOS arm64 GUI installer disk image)
#
# Designed for both local packaging and GitHub Actions Release workflow.
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${PROJECT_ROOT}"

TARGET_VERSION=""
SIGN_IDENTITY="${APPLE_SIGN_IDENTITY:-}"
SKIP_SIGN="${SKIP_SIGN:-0}"
DO_NOTARIZE=0
NOTARIZE_PROFILE="${APPLE_NOTARIZE_PROFILE:-}"
CLEAN_BUILD=0

show_help() {
    cat << 'HELP'
Usage: build_release_packages.sh [OPTIONS]

Build and package ATBClone release distribution packages for arm64:
  - dist/ATBCloneCli-<VERSION>-arm64.tar.gz
  - dist/ATBClone-<VERSION>-arm64.dmg

Options:
  -v, --version <x.y.z>    Explicit release version (e.g. 1.1.0 or v1.1.0)
  -s, --sign <identity>    Apple code signing identity (passed to build scripts)
  --skip-sign              Skip code signing or use ad-hoc signing
  -n, --notarize           Submit packages to Apple Notarization Service
  -p, --profile <name>     Keychain profile for Apple notarytool
  -c, --clean              Clean build/ and dist/ directories before building
  -h, --help               Show this help message

Environment Variables:
  VERSION / TARGET_VERSION Override version string
  APPLE_SIGN_IDENTITY      Signing identity
  APPLE_ID                 Apple ID email for notarization
  APPLE_PASSWORD           Apple app-specific password
  APPLE_APP_SPECIFIC_PASSWORD Alternative for APPLE_PASSWORD
  APPLE_TEAM_ID            Apple Team ID (default: WC7C59Q92T)
HELP
}

# Parse command line options
while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help)
            show_help
            exit 0
            ;;
        -v|--version)
            TARGET_VERSION="$2"
            shift 2
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
        -c|--clean)
            CLEAN_BUILD=1
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

# Resolve version
if [[ -z "${TARGET_VERSION}" ]]; then
    TARGET_VERSION="${VERSION:-}"
fi
if [[ -z "${TARGET_VERSION}" ]]; then
    TARGET_VERSION=$(grep -m 1 '^version =' pyproject.toml | cut -d '"' -f 2 || echo "")
fi
if [[ -z "${TARGET_VERSION}" ]]; then
    echo "[-] Error: Unable to determine target version." >&2
    exit 1
fi

# Strip optional leading 'v'
TARGET_VERSION="${TARGET_VERSION#v}"

# AppKit Sandbox Anti-Crash Linker Parameters & Deployment Target
export LDFLAGS="${LDFLAGS:--Wl,-needed_framework,AppKit}"
export MACOSX_DEPLOYMENT_TARGET="${MACOSX_DEPLOYMENT_TARGET:-12.0}"

# Propagate notary credentials
if [[ -n "${APPLE_PASSWORD:-}" && -z "${APPLE_APP_SPECIFIC_PASSWORD:-}" ]]; then
    export APPLE_APP_SPECIFIC_PASSWORD="${APPLE_PASSWORD}"
fi

echo "======================================================"
echo "  🚀 Packaging ATBClone Release v${TARGET_VERSION} (arm64)"
echo "======================================================"
echo "[+] Architecture: $(uname -m)"
echo "[+] Target Version: ${TARGET_VERSION}"
echo "[+] Deployment Target: ${MACOSX_DEPLOYMENT_TARGET}"
echo "[+] LDFLAGS: ${LDFLAGS}"

if [[ "${CLEAN_BUILD}" -eq 1 ]]; then
    echo "[*] Cleaning previous dist/ and build/ directories..."
    rm -rf dist/ build/
fi
mkdir -p dist/

# Common build arguments
CLI_ARGS=()
GUI_ARGS=()

if [[ -n "${SIGN_IDENTITY}" ]]; then
    CLI_ARGS+=("--sign" "${SIGN_IDENTITY}")
    GUI_ARGS+=("--sign" "${SIGN_IDENTITY}")
elif [[ "${SKIP_SIGN}" -eq 1 ]]; then
    CLI_ARGS+=("--skip-sign")
    GUI_ARGS+=("--skip-sign")
fi

if [[ "${DO_NOTARIZE}" -eq 1 ]]; then
    CLI_ARGS+=("--notarize")
    GUI_ARGS+=("--notarize")
    if [[ -n "${NOTARIZE_PROFILE}" ]]; then
        CLI_ARGS+=("--profile" "${NOTARIZE_PROFILE}")
        GUI_ARGS+=("--profile" "${NOTARIZE_PROFILE}")
    fi
fi

# ------------------------------------------------------------------------------
# 1. Build CLI Standalone Executable
# ------------------------------------------------------------------------------
echo ""
echo "======================================================"
echo "  [1/2] Building ATBCloneCli Binary..."
echo "======================================================"
bash scripts/build_cli.sh "${CLI_ARGS[@]}"

CLI_BIN="dist/ATBCloneCli"
if [[ ! -f "${CLI_BIN}" || ! -x "${CLI_BIN}" ]]; then
    echo "[-] Error: Expected CLI binary at ${CLI_BIN} not found or not executable." >&2
    exit 1
fi

CLI_TAR="dist/ATBCloneCli-${TARGET_VERSION}-arm64.tar.gz"
echo "[*] Creating CLI archive: ${CLI_TAR}..."
rm -f "${CLI_TAR}"
tar -czvf "${CLI_TAR}" -C dist ATBCloneCli

if [[ ! -f "${CLI_TAR}" ]]; then
    echo "[-] Error: Failed to create ${CLI_TAR}." >&2
    exit 1
fi
CLI_TAR_SIZE=$(du -sh "${CLI_TAR}" | cut -f1)
echo "[✔] Created CLI archive: ${CLI_TAR} (${CLI_TAR_SIZE})"

# ------------------------------------------------------------------------------
# 2. Build GUI macOS App & DMG
# ------------------------------------------------------------------------------
echo ""
echo "======================================================"
echo "  [2/2] Building ATBClone GUI DMG..."
echo "======================================================"
bash scripts/build_gui.sh "${GUI_ARGS[@]}"

# Locate produced DMG
PRODUCED_DMG=""
for candidate in "dist/ATBClone-${TARGET_VERSION}.dmg" "dist/ATBClone.dmg" dist/*.dmg; do
    # Skip already formatted release target or non-dmg files
    if [[ "${candidate}" == *"ATBClone-${TARGET_VERSION}-arm64.dmg"* ]]; then
        PRODUCED_DMG="${candidate}"
        break
    fi
    if [[ -f "${candidate}" ]]; then
        PRODUCED_DMG="${candidate}"
        break
    fi
done

if [[ -z "${PRODUCED_DMG}" ]]; then
    PRODUCED_DMG=$(find build/ -name "*.dmg" 2>/dev/null | head -1 || true)
fi

if [[ -z "${PRODUCED_DMG}" || ! -f "${PRODUCED_DMG}" ]]; then
    echo "[-] Error: No GUI .dmg found after running build_gui.sh." >&2
    exit 1
fi

FINAL_DMG="dist/ATBClone-${TARGET_VERSION}-arm64.dmg"
if [[ "${PRODUCED_DMG}" != "${FINAL_DMG}" ]]; then
    echo "[*] Normalizing DMG release artifact name to ${FINAL_DMG}..."
    cp -f "${PRODUCED_DMG}" "${FINAL_DMG}"
fi

FINAL_DMG_SIZE=$(du -sh "${FINAL_DMG}" | cut -f1)
echo "[✔] GUI installer ready: ${FINAL_DMG} (${FINAL_DMG_SIZE})"

# ------------------------------------------------------------------------------
# 3. Generate SHA256 Checksums
# ------------------------------------------------------------------------------
CHECKSUM_FILE="dist/checksums.txt"
echo ""
echo "==> Generating SHA256 checksums..."
(
    cd dist
    shasum -a 256 "ATBCloneCli-${TARGET_VERSION}-arm64.tar.gz" "ATBClone-${TARGET_VERSION}-arm64.dmg" > "checksums.txt"
)
cat "${CHECKSUM_FILE}"

echo ""
echo "======================================================"
echo "  🎉 Release Packages Successfully Built!"
echo "======================================================"
printf "  1. CLI Package: %s (%s)\n" "${CLI_TAR}" "${CLI_TAR_SIZE}"
printf "  2. GUI DMG:     %s (%s)\n" "${FINAL_DMG}" "${FINAL_DMG_SIZE}"
printf "  3. Checksums:   %s\n" "${CHECKSUM_FILE}"
echo "======================================================"
