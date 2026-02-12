#!/usr/bin/env python3
"""
beat_sync_cuts.py — Ridgemont Studio
Generate beat-synchronized cut points for video editing.

Uses librosa beat detection to create edit decision lists (EDL)
for hook-first openings, highlight segments, and beat-synced transitions.

Usage:
    python beat_sync_cuts.py --manifest "catalog/artist/song/manifest.json" \
        --format "tiktok" --output "catalog/artist/song/edl_tiktok.json"
"""

import argparse
import json
import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Load format strategies from external JSON (replaces 24-line hardcoded dict)
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_DATA_DIR = os.path.join(os.path.dirname(_SCRIPT_DIR), "data")

def _load_format_strategies():
    """Load beat sync cut strategies from JSON."""
    try:
        with open(os.path.join(_DATA_DIR, "beat_sync_strategies.json"), 'r') as f:
            data = json.load(f).get("strategies", {})
        # Convert hook_window lists back to tuples for compatibility
        for k, v in data.items():
            if "hook_window" in v:
                v["hook_window"] = tuple(v["hook_window"])
        return data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.warning(f"Could not load beat_sync_strategies.json: {e}")
        return {}

FORMAT_STRATEGIES = _load_format_strategies()


def find_nearest_beat(target_time, beat_times):
    """Find the beat time closest to target_time."""
    if not beat_times:
        return target_time
    closest = min(beat_times, key=lambda bt: abs(bt - target_time))
    return closest


def find_hook_segment(beat_times, onset_times, duration, max_length, hook_window):
    """
    Find the best hook-first opening segment.
    Looks for high onset density (energy) in the hook window.
    """
    start_pct, end_pct = hook_window
    window_start = duration * start_pct
    window_end = duration * end_pct

    best_start = window_start
    best_density = 0

    step = 2.0
    check_length = min(max_length, 30)

    t = window_start
    while t < window_end:
        onsets_in_range = [o for o in onset_times if t <= o < t + check_length]
        density = len(onsets_in_range)
        if density > best_density:
            best_density = density
            best_start = t
        t += step

    segment_start = find_nearest_beat(best_start, beat_times)
    segment_end = find_nearest_beat(segment_start + max_length, beat_times)

    return segment_start, min(segment_end, segment_start + max_length)


def find_energy_peak(beat_times, onset_times, duration, max_length):
    """Find the highest energy segment for sync reels."""
    best_start = 0
    best_density = 0
    step = 5.0

    t = 0
    while t < duration - max_length:
        onsets = [o for o in onset_times if t <= o < t + max_length]
        if len(onsets) > best_density:
            best_density = len(onsets)
            best_start = t
        t += step

    start = find_nearest_beat(best_start, beat_times)
    end = find_nearest_beat(start + max_length, beat_times)
    return start, min(end, start + max_length)


def generate_edl(manifest, format_name):
    """Generate an Edit Decision List for the given format."""
    strategy = FORMAT_STRATEGIES.get(format_name, FORMAT_STRATEGIES["short"])
    duration = manifest.get("duration", 180)
    beat_times = manifest.get("beats", {}).get("beat_times", [])
    onset_times = manifest.get("beats", {}).get("onset_times", [])
    max_dur = strategy["max_duration"]

    if strategy["strategy"] == "hook_first":
        start, end = find_hook_segment(
            beat_times, onset_times, duration, max_dur,
            strategy["hook_window"]
        )
    elif strategy["strategy"] == "energy_peak":
        start, end = find_energy_peak(beat_times, onset_times, duration, max_dur)
    else:
        start = find_nearest_beat(duration * 0.20, beat_times)
        end = find_nearest_beat(start + max_dur, beat_times)

    edl = {
        "format": format_name,
        "strategy": strategy["strategy"],
        "segment": {
            "start": round(start, 3),
            "end": round(min(end, start + max_dur), 3),
            "duration": round(min(end - start, max_dur), 3)
        },
        "fade_out": strategy["fade_out"],
        "beat_aligned": True,
        "generated_at": __import__('datetime').datetime.now().isoformat()
    }

    return edl


def main():
    parser = argparse.ArgumentParser(description="Generate beat-synced cut points")
    parser.add_argument("--manifest", required=True, help="Path to manifest.json")
    parser.add_argument("--format", required=True, choices=list(FORMAT_STRATEGIES.keys()))
    parser.add_argument("--output", required=True, help="Output EDL path")
    args = parser.parse_args()

    with open(args.manifest, 'r') as f:
        manifest = json.load(f)

    edl = generate_edl(manifest, args.format)

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, 'w') as f:
        json.dump(edl, f, indent=2)

    logger.info(f"EDL generated: {args.output}")
    logger.info(f"  Segment: {edl['segment']['start']:.1f}s → {edl['segment']['end']:.1f}s "
                f"({edl['segment']['duration']:.1f}s)")


if __name__ == "__main__":
    main()
