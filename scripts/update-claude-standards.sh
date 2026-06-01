#!/bin/bash
# Update Claude standards from the main repository
#
# This script pulls the latest Claude Code standards from the upstream
# repository using git subtree. The standards are maintained separately
# and shared across all projects.

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
SUBTREE_PREFIX=".claude/standard"
CLAUDE_REPO="https://github.com/ByronWilliamsCPA/.claude.git"
BRANCH="main"

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo -e "${RED}Error: Not in a git repository${NC}"
    echo "Please run this script from the root of your project"
    exit 1
fi

# Check if the subtree exists
if [ ! -d "$SUBTREE_PREFIX" ]; then
    echo -e "${YELLOW}Warning: Claude standards subtree not found at $SUBTREE_PREFIX${NC}"
    echo ""
    read -p "Do you want to add it now? (Y/n): " -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
        echo -e "${GREEN}Adding Claude standards subtree...${NC}"
        git subtree add --prefix "$SUBTREE_PREFIX" "$CLAUDE_REPO" "$BRANCH" --squash
        echo -e "${GREEN}✓ Claude standards added successfully${NC}"
        exit 0
    else
        echo "Cancelled."
        exit 1
    fi
fi

# Pull the latest changes
echo -e "${GREEN}Pulling latest Claude standards from $CLAUDE_REPO...${NC}"
echo ""

git subtree pull --prefix "$SUBTREE_PREFIX" "$CLAUDE_REPO" "$BRANCH" --squash

echo ""
echo -e "${GREEN}✓ Claude standards updated successfully${NC}"
echo ""
echo "Updated files in $SUBTREE_PREFIX/"
echo ""
echo "Note: If there were conflicts, resolve them and commit the merge."
