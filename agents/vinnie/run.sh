#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "[vinnie] Generating financial report..."
echo "  Working directory: $SCRIPT_DIR"
echo ""

VENV_PYTHON="../../.venv/bin/python3"

if [[ ! -x "$VENV_PYTHON" ]]; then
  echo "ERROR: Shared venv not found at $VENV_PYTHON"
  echo "  Run: python3 -m venv ../../.venv && ../../.venv/bin/pip install -r requirements.txt"
  exit 1
fi

exec "$VENV_PYTHON" src/generate_report.py "$@"
