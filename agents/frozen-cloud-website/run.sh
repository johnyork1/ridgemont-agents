#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "[frozen-cloud-website] Static website"
echo "  Working directory: $SCRIPT_DIR"
echo ""
echo "This is a static site with no build step."
echo ""
echo "  To preview: open index.html in a browser"
echo "  To deploy:  push to GitHub Pages or your preferred host"
echo ""

if command -v open &>/dev/null; then
  echo "Opening index.html..."
  open index.html
else
  echo "Open index.html in your browser to preview."
fi
