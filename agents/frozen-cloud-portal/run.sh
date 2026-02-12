#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "[frozen-cloud-portal] Launching Streamlit app..."
echo "  Working directory: $SCRIPT_DIR"
echo ""

if ! command -v streamlit &>/dev/null; then
  echo "ERROR: streamlit not found. Install with: pip install streamlit"
  exit 1
fi

exec streamlit run app.py "$@"
