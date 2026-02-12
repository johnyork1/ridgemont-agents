#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "[suno] Running Suno prompt generator..."
echo "  Working directory: $SCRIPT_DIR"
echo ""

exec python3 scripts/generate_prompt.py "$@"
