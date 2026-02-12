#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "[make-videos] Video pipeline wrapper agent"
echo "  Working directory: $SCRIPT_DIR"
echo ""
echo "This agent is designed to run as a Claude Desktop project."
echo ""
echo "  Open this directory as a project in Claude Desktop."
echo "  Pipeline scripts are in ../../scripts/"
echo ""
echo "Available pipeline scripts:"
ls -1 ../../scripts/*.py 2>/dev/null || echo "  (none found)"
