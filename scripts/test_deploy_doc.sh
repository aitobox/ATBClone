#!/usr/bin/env bash

# test_deploy_doc.sh - Local build and preview script for Zensical Documentation
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DOCS_GUIDE_DIR="$PROJECT_ROOT/docs/guide"

cd "$DOCS_GUIDE_DIR"

BOLD='\033[1m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

if [ -n "$NO_COLOR" ] || [ ! -t 1 ]; then
    BOLD=''
    GREEN=''
    BLUE=''
    YELLOW=''
    CYAN=''
    RED=''
    NC=''
fi

PORT=8000
BUILD_ONLY=false
AUTO_OPEN=true
SERVE_MODE=""

print_usage() {
    cat << USAGE_EOF
${BOLD}Usage:${NC} ./scripts/test_deploy_doc.sh [OPTIONS]

${BOLD}Options:${NC}
  -b, --build-only        Only compile the static site to site/, do not start preview server
  -p, --port <PORT>       Specify preview server port (default: 8000)
      --no-open           Do not automatically open default web browser
  -s, --serve             Run zensical live dev server (hot reload)
  -l, --lint              Check Markdown lists blank spacing across docs/guide/
      --fix-lists         Auto-format Markdown lists blank spacing in place
  -h, --help              Show this help message and exit

${BOLD}Examples:${NC}
  ./scripts/test_deploy_doc.sh               # Compile documentation and start local preview server
  ./scripts/test_deploy_doc.sh -b            # Only compile static files to site/
  ./scripts/test_deploy_doc.sh -l            # Check Markdown list blank spacing
  ./scripts/test_deploy_doc.sh --fix-lists   # Auto-fix Markdown list blank spacing
  ./scripts/test_deploy_doc.sh -s            # Live edit mode with Zensical hot reload
  ./scripts/test_deploy_doc.sh -p 8080       # Preview on port 8080
USAGE_EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        -b|--build-only)
            BUILD_ONLY=true
            shift
            ;;
        -l|--lint)
            if [ -f "$PROJECT_ROOT/scripts/format_markdown_lists.py" ]; then
                python3 "$PROJECT_ROOT/scripts/format_markdown_lists.py" --check "$DOCS_GUIDE_DIR"
            else
                echo -e "${YELLOW}Warning:${NC} scripts/format_markdown_lists.py not found."
            fi
            exit $?
            ;;
        --fix-lists)
            if [ -f "$PROJECT_ROOT/scripts/format_markdown_lists.py" ]; then
                python3 "$PROJECT_ROOT/scripts/format_markdown_lists.py" --fix "$DOCS_GUIDE_DIR"
            else
                echo -e "${YELLOW}Warning:${NC} scripts/format_markdown_lists.py not found."
            fi
            exit $?
            ;;
        -s|--serve)
            SERVE_MODE="true"
            shift
            ;;
        -p|--port)
            if [ -n "$2" ] && [[ "$2" =~ ^[0-9]+$ ]]; then
                PORT="$2"
                shift 2
            else
                echo -e "${RED}Error:${NC} --port requires a numeric argument."
                exit 1
            fi
            ;;
        --no-open)
            AUTO_OPEN=false
            shift
            ;;
        -h|--help)
            print_usage
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option:${NC} $1"
            print_usage
            exit 1
            ;;
    esac
done

# Detect zensical command
ZENSICAL_CMD=""
if [ -n "$CONDA_PREFIX" ] && [ -x "$CONDA_PREFIX/bin/zensical" ]; then
    ZENSICAL_CMD="$CONDA_PREFIX/bin/zensical"
elif command -v zensical &> /dev/null; then
    ZENSICAL_CMD="zensical"
elif [ -x "/opt/homebrew/anaconda3/envs/ATBClone/bin/zensical" ]; then
    ZENSICAL_CMD="/opt/homebrew/anaconda3/envs/ATBClone/bin/zensical"
fi

if [ -z "$ZENSICAL_CMD" ]; then
    echo -e "${RED}Error:${NC} 'zensical' command not found."
    echo -e "Please activate your environment or install dependencies:"
    echo -e "  conda activate ATBClone"
    echo -e "  pip install zensical>=0.0.46 pymdown-extensions>=10.0 Pygments>=2.16.0 markdown-gfm-admonition>=0.3.0"
    exit 1
fi

# Live dev server mode
if [ "$SERVE_MODE" = "true" ]; then
    echo -e "${BLUE}==>${NC} ${BOLD}Starting Zensical live development server...${NC}"
    CONFIG_FLAG=""
    if [ -f "zensical.zh.toml" ]; then
        CONFIG_FLAG="-f zensical.zh.toml"
    elif [ -f "zensical.toml" ]; then
        CONFIG_FLAG="-f zensical.toml"
    fi
    $ZENSICAL_CMD serve $CONFIG_FLAG
    exit 0
fi

# Multi-config or single config build
CONFIG_FILES=()
for f in zensical*.toml; do
    if [ -f "$f" ]; then
        CONFIG_FILES+=("$f")
    fi
done

if [ ${#CONFIG_FILES[@]} -eq 0 ]; then
    echo -e "${RED}Error:${NC} No zensical*.toml found in $DOCS_GUIDE_DIR."
    exit 1
fi

echo -e "${BLUE}==>${NC} ${BOLD}Building documentation with Zensical...${NC}"
for cfg in "${CONFIG_FILES[@]}"; do
    echo -e "  ${CYAN}->${NC} Compiling with config: ${BOLD}$cfg${NC}"
    $ZENSICAL_CMD build -f "$cfg"
done

# Copy root_index.html and CNAME to site/ if present and site/ exists
if [ -f "root_index.html" ] && [ -d "site" ]; then
    cp root_index.html site/index.html
fi
if [ -f "CNAME" ] && [ -d "site" ]; then
    cp CNAME site/CNAME
fi
if [ -d "site" ]; then
    touch site/.nojekyll
fi

echo -e "${GREEN}==>${NC} ${BOLD}Build completed successfully!${NC}"

if [ "$BUILD_ONLY" = true ]; then
    exit 0
fi

SITE_DIR="site"
if [ ! -d "$SITE_DIR" ]; then
    echo -e "${RED}Error:${NC} Directory '$SITE_DIR' does not exist."
    exit 1
fi

echo -e "\n${BLUE}======================================================${NC}"
echo -e "${GREEN}${BOLD}  Local Documentation Preview Server Running${NC}"
echo -e "${BLUE}======================================================${NC}"
echo -e "  Local URL: ${CYAN}http://localhost:${PORT}/${NC}"
echo -e "  Serving:   ${BOLD}$DOCS_GUIDE_DIR/${SITE_DIR}/${NC}"
echo -e "  Press ${YELLOW}Ctrl+C${NC} to stop the server.\n"

if [ "$AUTO_OPEN" = true ]; then
    (sleep 0.8 && {
        if command -v open &> /dev/null; then
            open "http://localhost:${PORT}/"
        elif command -v xdg-open &> /dev/null; then
            xdg-open "http://localhost:${PORT}/"
        fi
    }) &
fi

exec python3 -m http.server "$PORT" --directory "$SITE_DIR"
