#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Byron Williams
# SPDX-License-Identifier: MIT
#
# Generate requirements.txt files from uv.lock for pip-based deployments
#
# This script exports dependencies from uv.lock to requirements.txt format,
# enabling compatibility with pip-based deployment environments and tools
# that don't support uv directly (e.g., some CI systems, Docker builds).
#
# Usage:
#   ./scripts/generate_requirements.sh [options]
#
# Options:
#   --no-hashes    Exclude package hashes (smaller files, less secure)
#   --help         Show this help message
#
# Generated files:
#   requirements.txt      - Production dependencies only
#   requirements-dev.txt  - All dependencies including dev tools

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Parse arguments
INCLUDE_HASHES=true
while [[ $# -gt 0 ]]; do
    case $1 in
        --no-hashes)
            INCLUDE_HASHES=false
            shift
            ;;
        --help)
            head -25 "$0" | tail -20
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

echo -e "${GREEN}Generating requirements files from uv.lock...${NC}"

# Check if uv is available
if ! command -v uv &> /dev/null; then
    echo -e "${RED}Error: uv is not installed or not in PATH${NC}"
    echo "Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Check if uv.lock exists
if [[ ! -f "uv.lock" ]]; then
    echo -e "${RED}Error: uv.lock not found${NC}"
    echo "Run 'uv sync' to create the lock file first"
    exit 1
fi

# Build export arguments
EXPORT_ARGS=(--format requirements-txt)
if [[ "$INCLUDE_HASHES" == "false" ]]; then
    EXPORT_ARGS+=(--no-hashes)
    echo -e "${YELLOW}Note: Generating without hashes (--no-hashes)${NC}"
fi

# Generate production requirements (no dev dependencies)
echo "Generating requirements.txt (production only)..."
uv export "${EXPORT_ARGS[@]}" --no-dev --output-file requirements.txt

# Count packages
PROD_COUNT=$(grep -c "^[a-zA-Z]" requirements.txt 2>/dev/null || echo "0")
echo -e "  ${GREEN}Created requirements.txt with ${PROD_COUNT} packages${NC}"

# Generate dev requirements (all dependencies)
echo "Generating requirements-dev.txt (all dependencies)..."
uv export "${EXPORT_ARGS[@]}" --output-file requirements-dev.txt

# Count packages
DEV_COUNT=$(grep -c "^[a-zA-Z]" requirements-dev.txt 2>/dev/null || echo "0")
echo -e "  ${GREEN}Created requirements-dev.txt with ${DEV_COUNT} packages${NC}"

# Show summary
echo ""
echo -e "${GREEN}Requirements generation complete!${NC}"
echo ""
echo "Generated files:"
echo "  - requirements.txt      (${PROD_COUNT} production packages)"
echo "  - requirements-dev.txt  (${DEV_COUNT} total packages)"
echo ""
echo "Usage:"
echo "  pip install -r requirements.txt      # Production only"
echo "  pip install -r requirements-dev.txt  # Development"

# Verify files are different from uv.lock (sanity check)
if [[ ! -s "requirements.txt" ]]; then
    echo -e "${YELLOW}Warning: requirements.txt is empty${NC}"
    echo "This may indicate no production dependencies are defined"
fi
