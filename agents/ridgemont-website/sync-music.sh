#!/bin/bash
#
# Ridgemont Studio Music Sync
# Syncs your local music folder to Cloudflare R2
#
# Usage: ./sync-music.sh
#
# Prerequisites:
#   1. Install Wrangler: npm install -g wrangler
#   2. Set your API token: export CLOUDFLARE_API_TOKEN="your-token-here"
#

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MUSIC_DIR="$SCRIPT_DIR"
R2_BUCKET="ridgemont-studio"
ACCOUNT_ID="68f7ce5b85fc559091ec522f2b7b5aeb"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🎵 Ridgemont Studio Music Sync${NC}"
echo "================================"

# Check for API token
if [ -z "$CLOUDFLARE_API_TOKEN" ]; then
    echo -e "${YELLOW}⚠️  CLOUDFLARE_API_TOKEN not set${NC}"
    echo ""
    echo "Set it with:"
    echo "  export CLOUDFLARE_API_TOKEN=\"xEaS4ZIjcyKtGTxN8sm5oSHW1AwFU9-C0vxP9-ZS\""
    echo ""
    exit 1
fi

# Check for wrangler
if ! command -v wrangler &> /dev/null; then
    echo -e "${YELLOW}⚠️  Wrangler not found. Installing...${NC}"
    npm install -g wrangler
fi

# Upload tracks.json
echo -e "\n${BLUE}📋 Uploading tracks.json...${NC}"
if [ -f "$MUSIC_DIR/tracks.json" ]; then
    wrangler r2 object put "$R2_BUCKET/tracks.json" \
        --file="$MUSIC_DIR/tracks.json" \
        --content-type="application/json"
    echo -e "${GREEN}✓ tracks.json uploaded${NC}"
else
    echo -e "${YELLOW}⚠️  tracks.json not found in $MUSIC_DIR${NC}"
fi

# Upload all MP3 files
echo -e "\n${BLUE}🎶 Uploading music files...${NC}"
MP3_COUNT=0
for file in "$MUSIC_DIR"/*.mp3; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        echo "  Uploading: $filename"
        wrangler r2 object put "$R2_BUCKET/$filename" \
            --file="$file" \
            --content-type="audio/mpeg"
        ((MP3_COUNT++))
    fi
done

if [ $MP3_COUNT -eq 0 ]; then
    echo -e "${YELLOW}  No MP3 files found${NC}"
else
    echo -e "${GREEN}✓ Uploaded $MP3_COUNT music file(s)${NC}"
fi

# Upload all WAV files (if any)
WAV_COUNT=0
for file in "$MUSIC_DIR"/*.wav; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        echo "  Uploading: $filename"
        wrangler r2 object put "$R2_BUCKET/$filename" \
            --file="$file" \
            --content-type="audio/wav"
        ((WAV_COUNT++))
    fi
done

if [ $WAV_COUNT -gt 0 ]; then
    echo -e "${GREEN}✓ Uploaded $WAV_COUNT WAV file(s)${NC}"
fi

echo -e "\n${GREEN}🎉 Sync complete!${NC}"
echo ""
echo "Your music is now available at:"
echo "  https://ridgemont-studio.pages.dev"
