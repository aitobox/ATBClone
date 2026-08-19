#!/usr/bin/env bash
# ==============================================================================
# ATBClone Standalone Binary Notarization Script (macOS notarytool)
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${PROJECT_ROOT}"

TARGET_FILE=""
TEAM_ID="WC7C59Q92T"
KEYCHAIN_PROFILE="${APPLE_NOTARIZE_PROFILE:-}"
APPLE_ID="${APPLE_ID:-}"
APPLE_TEAM_ID="${APPLE_TEAM_ID:-$TEAM_ID}"
APPLE_PASSWORD="${APPLE_APP_SPECIFIC_PASSWORD:-}"
ZIP_ONLY=0

show_help() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS] [TARGET_BINARY]

Package and notarize macOS standalone binary with Apple Notary Service.

Arguments:
  TARGET_BINARY               Path to executable (default: dist/ATBCloneCli)

Options:
  -p, --profile <name>        Keychain profile name created via notarytool
  --apple-id <email>          Apple ID email for notarization
  --team-id <team_id>         Apple Developer Team ID (10 alphanumeric characters)
  --password <app_password>   Apple App-Specific Password
  -z, --zip-only              Create notarization ZIP archive without submitting
  -h, --help                  Show this help message

Environment Variables:
  APPLE_NOTARIZE_PROFILE       Keychain profile name (recommended)
  APPLE_ID                     Apple ID email
  APPLE_TEAM_ID                Apple Team ID
  APPLE_APP_SPECIFIC_PASSWORD  Apple App-Specific Password

How to setup Keychain Profile (Recommended by Apple):
  xcrun notarytool store-credentials "notary-profile" \\
      --apple-id "developer@example.com" \\
      --team-id "TEAMID1234" \\
      --password "xxxx-xxxx-xxxx-xxxx"

Then notarize simply with:
  $(basename "$0") --profile "notary-profile"
EOF
}

# Parse flags
while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help)
            show_help
            exit 0
            ;;
        -p|--profile|--keychain-profile)
            KEYCHAIN_PROFILE="$2"
            shift 2
            ;;
        --apple-id)
            APPLE_ID="$2"
            shift 2
            ;;
        --team-id)
            APPLE_TEAM_ID="$2"
            shift 2
            ;;
        --password)
            APPLE_PASSWORD="$2"
            shift 2
            ;;
        -z|--zip-only)
            ZIP_ONLY=1
            shift
            ;;
        -*)
            echo "[-] Unknown option: $1" >&2
            show_help
            exit 1
            ;;
        *)
            TARGET_FILE="$1"
            shift
            ;;
    esac
done

TARGET_FILE="${TARGET_FILE:-dist/ATBCloneCli}"

if [[ ! -f "${TARGET_FILE}" ]]; then
    echo "[-] Error: Target binary not found: ${TARGET_FILE}" >&2
    exit 1
fi

# Extract version from pyproject.toml
VERSION=$(grep -m 1 '^version =' pyproject.toml | cut -d '"' -f 2 || echo "0.1.0")
ARCH="$(uname -m)"
ZIP_OUTPUT="dist/ATBCloneCli-v${VERSION}-darwin-${ARCH}.zip"

echo "======================================================"
echo "  📦 Packaging ATBCloneCli for Notarization"
echo "======================================================"
echo "[+] Target Binary: ${TARGET_FILE}"
echo "[+] Version:       v${VERSION}"
echo "[+] Architecture:  ${ARCH}"

# Verify binary signature before archiving
echo "[*] Checking signature on ${TARGET_FILE}..."
if ! codesign -dv "${TARGET_FILE}" 2>&1 | grep -q "Authority=Developer ID Application"; then
    echo "[!] Warning: Binary is not signed with 'Developer ID Application'."
    echo "    Apple Notarization will reject binaries signed with ad-hoc or development certificates."
    if [[ "${ZIP_ONLY}" -eq 0 && -z "${KEYCHAIN_PROFILE}" && -z "${APPLE_ID}" ]]; then
        echo "[-] Aborting notarization submission. Use --zip-only if you just want the archive." >&2
        exit 1
    fi
fi

# Create ZIP archive (ditto preserves file permissions, symlinks, and code signature metadata)
echo "[*] Creating notarization ZIP archive: ${ZIP_OUTPUT}..."
rm -f "${ZIP_OUTPUT}"
ditto -c -k --keepParent "${TARGET_FILE}" "${ZIP_OUTPUT}"
echo "[✔] Archive created successfully (${ZIP_OUTPUT})"

if [[ "${ZIP_ONLY}" -eq 1 ]]; then
    echo "[✔] --zip-only specified. Done."
    exit 0
fi

# Submit to Apple Notary Service
if [[ -n "${KEYCHAIN_PROFILE}" ]]; then
    echo "==> Submitting to Apple Notary Service using keychain profile: ${KEYCHAIN_PROFILE}..."
    xcrun notarytool submit "${ZIP_OUTPUT}" --keychain-profile "${KEYCHAIN_PROFILE}" --wait
    echo "[✔] Notarization submission completed!"
elif [[ -n "${APPLE_ID}" && -n "${APPLE_TEAM_ID}" && -n "${APPLE_PASSWORD}" ]]; then
    echo "==> Submitting to Apple Notary Service using provided credentials..."
    xcrun notarytool submit "${ZIP_OUTPUT}" \
        --apple-id "${APPLE_ID}" \
        --team-id "${APPLE_TEAM_ID}" \
        --password "${APPLE_PASSWORD}" \
        --wait
    echo "[✔] Notarization submission completed!"
else
    echo ""
    echo "[*] No notarization credentials provided. Skipping submission."
    echo "    Archive is ready at: ${ZIP_OUTPUT}"
    echo "    To submit manually:"
    echo "      xcrun notarytool submit ${ZIP_OUTPUT} --keychain-profile <profile> --wait"
fi
