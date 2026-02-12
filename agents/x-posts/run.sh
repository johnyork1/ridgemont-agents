#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "[x-posts] X/Twitter post drafting agent"
echo "  Working directory: $SCRIPT_DIR"
echo ""
echo "This agent is a Claude Desktop project for drafting X posts."
echo ""
echo "  Open this directory as a project in Claude Desktop."
