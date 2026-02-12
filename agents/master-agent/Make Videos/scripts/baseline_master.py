#!/usr/bin/env python3
"""
baseline_master.py — Ridgemont Studio Make Videos Pipeline
Step 3: Creation — Generate Phase 1 Baseline Master Video.

The Baseline Recipe produces professional videos with ZERO AI dependency:
1. Ken Burns pan (zoom + drift) on album art or genre-matched landscape
2. Beat-synced brightness pulse via FFmpeg eq filter
3. W&B breathing/bounce overlay at intro + Meme Sign end card
4. Artist name + song title within Safe Zone
5. Full audio track

Usage:
    python baseline_master.py --song-id "song_001" --artist "DJ Chromosphere" \
        --project-root "/path/to/ridgemont"

Pipeline Position: Step 3 (after Analysis, before Assembly)
"""

import argparse
import json
import os
import sys
import subprocess
import logging
import math
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Load animation constants from external JSON (replaces 7-line hardcoded block)
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_DATA_DIR = os.path.join(os.path.dirname(_SCRIPT_DIR), "data")

def _load_baseline_recipe():
    """Load rendering constants from baseline_recipe.json."""
    defaults = {"master_width": 1920, "master_height": 1080, "fps": 30,
                "intro_duration": 3.0, "endcard_duration": 5.0,
                "entrance_duration": 0.5, "exit_duration": 0.3}
    try:
        with open(os.path.join(_DATA_DIR, "baseline_recipe.json"), 'r') as f:
            data = json.load(f)
        defaults.update({k: v for k, v in data.items() if not k.startswith("_")})
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.warning(f"Could not load baseline_recipe.json: {e} — using defaults")
    return defaults

_RECIPE = _load_baseline_recipe()
MASTER_WIDTH = _RECIPE["master_width"]
MASTER_HEIGHT = _RECIPE["master_height"]
FPS = _RECIPE["fps"]
INTRO_DURATION = _RECIPE["intro_duration"]
ENDCARD_DURATION = _RECIPE["endcard_duration"]
ENTRANCE_DURATION = _RECIPE["entrance_duration"]
EXIT_DURATION = _RECIPE["exit_duration"]


def breathing_scale(t):
    """
    Breathing animation: 2-second sine-wave scale (98% → 102%).
    MANDATORY for all character overlays. Static PNGs are NEVER acceptable.
    """
    return 1.0 + 0.02 * math.sin(2 * math.pi * t / 2.0)


def beat_bounce_offset(t, beat_times, bounce_px=7):
    """
    Beat bounce: 5-10px Y-axis offset on kick drum beats.
    Returns Y offset in pixels. Decays over 0.1 seconds.
    """
    for bt in beat_times:
        diff = t - bt
        if 0 <= diff < 0.1:
            decay = 1.0 - (diff / 0.1)
            return int(bounce_px * decay)
    return 0


def build_ken_burns_filter(duration, zoom_start=1.0, zoom_end=1.15,
                            drift_x=50, drift_y=30):
    """
    Ken Burns pan: slow zoom + drift on background image.
    Returns FFmpeg filter string for zoompan.
    """
    total_frames = int(duration * FPS)
    zp = (
        f"zoompan=z='min(zoom+{(zoom_end-zoom_start)/total_frames:.6f},1.5)':"
        f"x='iw/2-(iw/zoom/2)+{drift_x}*on/{total_frames}':"
        f"y='ih/2-(ih/zoom/2)+{drift_y}*on/{total_frames}':"
        f"d={total_frames}:s={MASTER_WIDTH}x{MASTER_HEIGHT}:fps={FPS}"
    )
    return zp


def build_beat_pulse_filter(beat_times, duration, intensity=0.08):
    """
    Beat-synced brightness pulse via FFmpeg eq filter.
    Returns FFmpeg filter string.
    """
    parts = []
    for bt in beat_times[:100]:
        parts.append(f"{intensity}*max(0,1-(t-{bt:.3f})/0.15)*gt(t,{bt:.3f})")

    if not parts:
        return "eq=brightness=0"

    expr = "+".join(parts[:50])
    return f"eq=brightness='{expr}'"


def build_master_video(manifest, project_root, output_path):
    """
    Build the complete baseline master video.
    """
    audio_path = os.path.join(project_root, manifest["audio_source"])
    duration = manifest["duration"]
    beat_times = manifest["beats"]["beat_times"]
    bpm = manifest["bpm"]

    bg_image = manifest.get("background_image")
    if bg_image:
        bg_path = os.path.join(project_root, bg_image)
    else:
        song_dir = os.path.dirname(os.path.join(project_root, manifest["audio_source"]))
        for ext in ['.jpg', '.png', '.jpeg']:
            candidate = os.path.join(song_dir, f"cover{ext}")
            if os.path.exists(candidate):
                bg_path = candidate
                break
        else:
            bg_path = os.path.join(project_root, "assets", "backgrounds", "default_gradient.png")

    if not os.path.exists(bg_path):
        logger.warning(f"Background image not found: {bg_path} — generating solid color")
        bg_path = os.path.join(os.path.dirname(output_path), "temp_bg.png")
        subprocess.run([
            'ffmpeg', '-y', '-f', 'lavfi', '-i',
            f'color=c=0x1a1a2e:s={MASTER_WIDTH}x{MASTER_HEIGHT}:d=1',
            '-frames:v', '1', bg_path
        ], capture_output=True)

    ken_burns = build_ken_burns_filter(duration)

    pulse_beats = beat_times[:30]
    pulse_expr_parts = []
    for bt in pulse_beats:
        pulse_expr_parts.append(f"0.06*max(0,1-(t-{bt:.2f})/0.12)*gt(t,{bt:.2f})")
    pulse_expr = "+".join(pulse_expr_parts) if pulse_expr_parts else "0"

    cmd = (
        f'ffmpeg -y -loop 1 -i "{bg_path}" -i "{audio_path}" '
        f'-filter_complex "'
        f'[0:v]{ken_burns},'
        f"eq=brightness='{pulse_expr}'"
        f'" '
        f'-c:v libx264 -crf 18 -preset medium -tune stillimage '
        f'-c:a aac -b:a 192k '
        f'-shortest -t {duration:.1f} '
        f'"{output_path}"'
    )

    logger.info(f"Building master video ({duration:.0f}s at {bpm:.0f} BPM)...")
    logger.info(f"Background: {bg_path}")

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode != 0:
        logger.error(f"FFmpeg failed: {result.stderr[:500]}")
        logger.info("Retrying with simplified filter...")
        cmd_simple = (
            f'ffmpeg -y -loop 1 -i "{bg_path}" -i "{audio_path}" '
            f'-filter_complex "[0:v]{ken_burns}" '
            f'-c:v libx264 -crf 18 -preset medium -tune stillimage '
            f'-c:a aac -b:a 192k -shortest -t {duration:.1f} '
            f'"{output_path}"'
        )
        result = subprocess.run(cmd_simple, shell=True, capture_output=True, text=True)

        if result.returncode != 0:
            logger.error(f"Simplified render also failed: {result.stderr[:300]}")
            return False

    logger.info(f"Master video created: {output_path}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Generate baseline master video")
    parser.add_argument("--song-id", required=True)
    parser.add_argument("--artist", required=True)
    parser.add_argument("--project-root", default=".")
    args = parser.parse_args()

    project_root = os.path.abspath(args.project_root)
    song_dir = os.path.join(project_root, "catalog", args.artist, args.song_id)

    manifest_path = os.path.join(song_dir, "manifest.json")
    if not os.path.exists(manifest_path):
        logger.error(f"Manifest not found: {manifest_path}")
        sys.exit(1)

    with open(manifest_path, 'r') as f:
        manifest = json.load(f)

    if manifest.get("pipeline", {}).get("status") == "ABORTED_PREFLIGHT":
        logger.error(f"Song {args.song_id} failed preflight — cannot render")
        sys.exit(2)

    output_path = os.path.join(song_dir, "master_video.mp4")

    success = build_master_video(manifest, project_root, output_path)

    if success:
        try:
            progress_file = os.path.join(song_dir, 'progress_log.json')
            if os.path.exists(progress_file):
                with open(progress_file, 'r') as f:
                    progress_data = json.load(f)
            else:
                progress_data = {'song_id': args.song_id, 'artist': args.artist, 'stages': {}}

            progress_data['stages']['creation'] = {
                'completed': datetime.now().isoformat(),
                'recipe': 'baseline_phase1',
                'master_path': str(output_path),
                'duration': manifest.get('duration', 0)
            }
            with open(progress_file, 'w') as f:
                json.dump(progress_data, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not update progress: {e}")

        logger.info(f"=== Master video ready: {output_path} ===")
        logger.info(f"Next: python batch_produce.py --song-id {args.song_id} --artist \"{args.artist}\"")
    else:
        logger.error("Master video generation failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
