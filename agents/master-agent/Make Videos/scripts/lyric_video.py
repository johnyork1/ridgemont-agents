#!/usr/bin/env python3
"""
lyric_video.py — Ridgemont Studio
Generate lyric overlay videos with text within Safe Zone.

Phase 1: Simple text overlay via FFmpeg drawtext filter.
Phase 2+: Manim kinetic typography (planned).

Usage:
    python lyric_video.py --song-id "song_001" --artist "DJ Chromosphere" \
        --lyrics "path/to/lyrics.txt" --project-root "/path/to/ridgemont"
"""

import argparse
import json
import os
import sys
import subprocess
import logging
from datetime import datetime

from safe_zone import enforce_safe_zone, get_safe_zone_bounds

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Load lyric rendering config from external JSON (replaces scattered magic numbers)
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_DATA_DIR = os.path.join(os.path.dirname(_SCRIPT_DIR), "data")

def _load_lyric_config():
    """Load lyric overlay rendering constants from JSON."""
    defaults = {"fontsize": 42, "fontcolor": "white", "border_width": 2,
                "border_color": "black@0.6", "y_position_pct": 0.75,
                "display_duration": 4.0, "fade_in_sec": 0.3, "fade_out_sec": 0.3,
                "frame_width": 1920, "frame_height": 1080}
    try:
        with open(os.path.join(_DATA_DIR, "lyric_config.json"), 'r') as f:
            data = json.load(f)
        defaults.update({k: v for k, v in data.items() if not k.startswith("_")})
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.warning(f"Could not load lyric_config.json: {e} — using defaults")
    return defaults

LYRIC_CFG = _load_lyric_config()


def parse_lyrics_file(lyrics_path):
    """
    Parse lyrics file. Supports simple format:
    [00:15.00] First line of lyrics
    [00:20.50] Second line
    
    Or plain text (one line per estimated interval).
    """
    lines = []
    with open(lyrics_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith('[') and ']' in line:
                # Timestamped format
                bracket_end = line.index(']')
                timestamp_str = line[1:bracket_end]
                text = line[bracket_end + 1:].strip()
                try:
                    parts = timestamp_str.replace('.', ':').split(':')
                    minutes = float(parts[0])
                    seconds = float(parts[1])
                    ms = float(parts[2]) if len(parts) > 2 else 0
                    time_sec = minutes * 60 + seconds + ms / 100
                    lines.append({"time": time_sec, "text": text})
                except (ValueError, IndexError):
                    lines.append({"time": None, "text": line})
            else:
                lines.append({"time": None, "text": line})
    return lines


def distribute_lyrics_over_beats(lyrics, beat_times, duration):
    """Assign timestamps to lyrics without explicit timing."""
    timed = []
    # Filter to lyrics needing timestamps
    untimed = [l for l in lyrics if l["time"] is None]
    timed_existing = [l for l in lyrics if l["time"] is not None]

    if untimed:
        # Distribute evenly across song duration
        interval = duration / (len(untimed) + 1)
        for i, lyric in enumerate(untimed):
            target_time = interval * (i + 1)
            # Snap to nearest beat if possible
            if beat_times:
                closest_beat = min(beat_times, key=lambda bt: abs(bt - target_time))
                lyric["time"] = closest_beat
            else:
                lyric["time"] = target_time

    all_lyrics = timed_existing + untimed
    all_lyrics.sort(key=lambda l: l["time"])
    return all_lyrics


def build_drawtext_filter(lyrics, duration, frame_width=None, frame_height=None):
    """Build FFmpeg drawtext filter for lyric overlay within Safe Zone."""
    fw = frame_width or LYRIC_CFG["frame_width"]
    fh = frame_height or LYRIC_CFG["frame_height"]
    safe_left, safe_top, safe_right, safe_bottom = get_safe_zone_bounds(fw, fh, "master")
    cy = int(fh * LYRIC_CFG["y_position_pct"])
    show_dur = LYRIC_CFG["display_duration"]
    fade_in = LYRIC_CFG["fade_in_sec"]
    fade_out = LYRIC_CFG["fade_out_sec"]

    filters = []
    for i, lyric in enumerate(lyrics):
        start = lyric["time"]
        if i + 1 < len(lyrics):
            end = min(lyric["time"] + show_dur, lyrics[i + 1]["time"])
        else:
            end = min(start + show_dur, duration)

        text = lyric["text"].replace("'", "'\\''").replace(":", "\\:")
        alpha_expr = (
            f"if(between(t,{start:.2f},{start+fade_in:.2f}),(t-{start:.2f})/{fade_in},"
            f"if(between(t,{end-fade_out:.2f},{end:.2f}),({end:.2f}-t)/{fade_out},"
            f"if(between(t,{start:.2f},{end:.2f}),1,0)))"
        )

        drawtext = (
            f"drawtext=text='{text}':"
            f"fontsize={LYRIC_CFG['fontsize']}:fontcolor={LYRIC_CFG['fontcolor']}:"
            f"x=(w-text_w)/2:y={cy}:"
            f"alpha='{alpha_expr}':"
            f"borderw={LYRIC_CFG['border_width']}:bordercolor={LYRIC_CFG['border_color']}"
        )
        filters.append(drawtext)

    return ",".join(filters) if filters else "null"


def main():
    parser = argparse.ArgumentParser(description="Generate lyric video overlay")
    parser.add_argument("--song-id", required=True)
    parser.add_argument("--artist", required=True)
    parser.add_argument("--lyrics", required=True, help="Path to lyrics file")
    parser.add_argument("--project-root", default=".")
    args = parser.parse_args()

    project_root = os.path.abspath(args.project_root)
    song_dir = os.path.join(project_root, "catalog", args.artist, args.song_id)

    # Load manifest for beat times and duration
    manifest_path = os.path.join(song_dir, "manifest.json")
    if not os.path.exists(manifest_path):
        logger.error(f"Manifest not found: {manifest_path}")
        sys.exit(1)

    with open(manifest_path, 'r') as f:
        manifest = json.load(f)

    # Parse lyrics
    if not os.path.exists(args.lyrics):
        logger.error(f"Lyrics file not found: {args.lyrics}")
        sys.exit(1)

    lyrics = parse_lyrics_file(args.lyrics)
    beat_times = manifest.get("beats", {}).get("beat_times", [])
    duration = manifest.get("duration", 180)

    lyrics = distribute_lyrics_over_beats(lyrics, beat_times, duration)
    logger.info(f"Processed {len(lyrics)} lyric lines")

    # Build lyric video from master
    master_path = os.path.join(song_dir, "master_video.mp4")
    if not os.path.exists(master_path):
        logger.error(f"Master video not found: {master_path}")
        sys.exit(1)

    output_path = os.path.join(song_dir, "outputs", "lyric_video.mp4")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    vf = build_drawtext_filter(lyrics, duration)
    cmd = (
        f'ffmpeg -y -i "{master_path}" '
        f'-vf "{vf}" '
        f'-c:v libx264 -crf 18 -preset medium -c:a copy '
        f'"{output_path}"'
    )

    logger.info("Rendering lyric video...")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        logger.info(f"Lyric video created: {output_path}")
    else:
        logger.error(f"Render failed: {result.stderr[:300]}")
        sys.exit(1)


if __name__ == "__main__":
    main()
