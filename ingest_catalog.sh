#!/usr/bin/env bash
# ============================================================
#  Master Studio Ingestor — ingest_catalog.sh
#  Loops through every artist/song in catalog/ and runs the
#  analyze_catalog pipeline for each.
# ============================================================
set -euo pipefail

STUDIO_DIR="$(cd "$(dirname "$0")" && pwd)"
CATALOG_DIR="$STUDIO_DIR/catalog"
LOG_FILE="$STUDIO_DIR/output/production_log.csv"
PYTHON="$STUDIO_DIR/.venv/bin/python3"

# Counters
total=0
success=0
failed=0
skipped=0

# Colors (disabled if not a terminal)
if [ -t 1 ]; then
    GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
else
    GREEN=''; RED=''; YELLOW=''; CYAN=''; NC=''
fi

log()  { echo -e "${CYAN}[ingestor]${NC} $*"; }
pass() { echo -e "${GREEN}[  OK  ]${NC} $*"; }
fail() { echo -e "${RED}[ FAIL ]${NC} $*"; }
skip() { echo -e "${YELLOW}[ SKIP ]${NC} $*"; }

# ── Preflight checks ───────────────────────────────────────
if [ ! -x "$PYTHON" ]; then
    echo "ERROR: Python venv not found at $PYTHON" >&2
    echo "  Run: python3 -m venv $STUDIO_DIR/.venv && $STUDIO_DIR/.venv/bin/pip install -r $STUDIO_DIR/requirements.txt" >&2
    exit 1
fi

if [ ! -d "$CATALOG_DIR" ]; then
    echo "ERROR: catalog/ directory not found at $CATALOG_DIR" >&2
    exit 1
fi

# Ensure production log exists with header
if [ ! -f "$LOG_FILE" ]; then
    echo "audio_file,artist,title,genre,status,skipped,skip_reason,bpm,key,mood,ingest_ok,analyze_ok,render_ok,cuts_ok,render_time,total_time,output_path,short_path,error" > "$LOG_FILE"
    log "Created new production_log.csv"
fi

# ── Main loop ──────────────────────────────────────────────
echo ""
echo "============================================================"
echo "  MASTER STUDIO INGESTOR"
echo "  Catalog : $CATALOG_DIR"
echo "  Python  : $PYTHON"
echo "  Log     : $LOG_FILE"
echo "============================================================"
echo ""

for artist_dir in "$CATALOG_DIR"/*/; do
    [ -d "$artist_dir" ] || continue
    artist_slug=$(basename "$artist_dir")

    # Skip hidden directories
    [[ "$artist_slug" == .* ]] && continue

    log "Artist: $artist_slug"

    for song_dir in "$artist_dir"*/; do
        [ -d "$song_dir" ] || continue
        song_slug=$(basename "$song_dir")
        [[ "$song_slug" == .* ]] && continue

        total=$((total + 1))

        # Check if audio file exists
        audio_file=$(find "$song_dir" -maxdepth 1 -type f \( -name "*.mp3" -o -name "*.wav" -o -name "*.flac" -o -name "*.m4a" -o -name "*.ogg" \) | head -1)
        if [ -z "$audio_file" ]; then
            skip "$artist_slug / $song_slug — no audio file found"
            skipped=$((skipped + 1))
            continue
        fi

        log "  Processing: $artist_slug / $song_slug"

        if "$PYTHON" "$STUDIO_DIR/scripts/analyze_catalog.py" \
                --song-id "$song_slug" \
                --artist "$artist_slug" \
                --project-root "$STUDIO_DIR"; then
            pass "  $artist_slug / $song_slug"
            success=$((success + 1))
        else
            fail "  $artist_slug / $song_slug (exit code: $?)"
            failed=$((failed + 1))
        fi

        echo ""
    done
done

# ── Summary ────────────────────────────────────────────────
echo "============================================================"
echo "  INGEST COMPLETE"
echo "  Total : $total"
echo "  OK    : $success"
echo "  Failed: $failed"
echo "  Skipped: $skipped"
echo "============================================================"

# Exit with failure if any song failed
[ "$failed" -eq 0 ] || exit 1
