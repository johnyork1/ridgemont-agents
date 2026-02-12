#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "[make-music] Running music generation script..."
echo "  Working directory: $SCRIPT_DIR"
echo ""

exec python3 generate_getting_old.py "$@"
