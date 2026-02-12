#!/bin/bash
#──────────────────────────────────────────────────────────
# ingest_vinnie.sh — Local launcher for Dr. Vinnie Boombatz
#
# Usage:
#   ./ingest_vinnie.sh                     # Interactive Python REPL
#   ./ingest_vinnie.sh --script myscript.py # Run a specific script
#──────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OUTPUT_DIR="$SCRIPT_DIR/output"
PYTHON="$SCRIPT_DIR/.venv/bin/python3"

# Ensure output directory exists
mkdir -p "$OUTPUT_DIR"

# Parse arguments
MODE="interactive"
SCRIPT_FILE=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --script)
      MODE="script"
      SCRIPT_FILE="$2"
      shift 2
      ;;
    *)
      echo "Usage: $0 [--script <file.py>]"
      exit 1
      ;;
  esac
done

# Verify venv exists
if [ ! -x "$PYTHON" ]; then
  echo "Python venv not found at $PYTHON"
  echo "  Run: python3 -m venv $SCRIPT_DIR/.venv && $SCRIPT_DIR/.venv/bin/pip install -r $SCRIPT_DIR/requirements.txt"
  exit 1
fi

echo "╔═══════════════════════════════════════════╗"
echo "║  Dr. Vinnie Boombatz — Local Launch        ║"
echo "╠═══════════════════════════════════════════╣"
echo "║  Catalog : $SCRIPT_DIR/catalog             ║"
echo "║  Output  : $OUTPUT_DIR                     ║"
echo "║  Python  : $PYTHON                         ║"
echo "╚═══════════════════════════════════════════╝"

export PYTHONPATH="$SCRIPT_DIR/scripts:${PYTHONPATH:-}"

case $MODE in
  interactive)
    echo "Launching interactive Python..."
    "$PYTHON" -i
    ;;
  script)
    if [ ! -f "$SCRIPT_DIR/$SCRIPT_FILE" ]; then
      echo "Script not found: $SCRIPT_FILE"
      exit 1
    fi
    echo "Running: $SCRIPT_FILE"
    "$PYTHON" "$SCRIPT_DIR/$SCRIPT_FILE"
    ;;
esac
