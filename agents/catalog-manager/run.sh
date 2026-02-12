#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "[catalog-manager] Running catalog manager..."
echo "  Working directory: $SCRIPT_DIR"
echo ""

exec python3 scripts/catalog_manager.py "$@"
