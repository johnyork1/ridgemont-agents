#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "[ridgemont-website] Static site with Cloudflare Worker"
echo "  Working directory: $SCRIPT_DIR"
echo ""
echo "  To preview: open index.html in a browser"
echo "  To deploy:  wrangler deploy"
echo ""

if [[ "${1:-}" == "deploy" ]]; then
  if ! command -v wrangler &>/dev/null; then
    echo "ERROR: wrangler not found. Install with: npm install -g wrangler"
    exit 1
  fi
  echo "Deploying with wrangler..."
  exec wrangler deploy
elif [[ "${1:-}" == "preview" ]] || [[ $# -eq 0 ]]; then
  if command -v open &>/dev/null; then
    echo "Opening index.html..."
    open index.html
  else
    echo "Open index.html in your browser to preview."
  fi
fi
