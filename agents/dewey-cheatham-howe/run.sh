#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "[dewey-cheatham-howe] Claude Desktop plugin agent"
echo "  Working directory: $SCRIPT_DIR"
echo ""
echo "This agent is a Claude Desktop plugin with no standalone entry point."
echo ""
echo "  Open this directory as a project in Claude Desktop."
