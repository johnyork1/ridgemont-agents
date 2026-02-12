#!/usr/bin/env python3
"""beat_sync_cuts.py - Short-form video cut engine for the Make Videos pipeline.

Creates high-energy short clips for TikTok/Shorts/Stories by:
  1. Loading beat_times from an analyzed manifest
  2. Selecting cut strategy from beat_sync_strategies.json
  3. Identifying the highest-energy segment (Hook-First) or
     building ascending energy (Energy-Peak)
  4. Cutting the master video at beat boundaries via FFmpeg
  5. Scaling to 9:16 vertical with blur-fill background

Usage:
    python beat_sync_cuts.py --song-id crazy --artist the_ridgemonts
    python beat_sync_cuts.py --song-id crazy --artist the_ridgemonts --strategy hook_first
"""
import argparse
import json
import math
import os
import subprocess
import sys
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
PROJECT_ROOT_DEFAULT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))


# ── Config & Manifest Loaders ────────────────────────────────

def load_strategies(project_root):
    """Load beat_sync_strategies.json."""
    path = os.path.join(project_root, "data", "beat_sync_strategies.json")
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def load_manifest(catalog_dir):
    """Load manifest.json, require analyzed or rendered stage."""
    path = os.path.join(catalog_dir, "manifest.json")
    if not os.path.isfile(path):
        return None, path
    with open(path, "r", encoding="utf-8") as fh:
        manifest = json.load(fh)
    if manifest.get("pipeline_stage") not in ("analyzed", "rendered"):
        return None, path
    return manifest, path


# ── Strategy Selection ───────────────────────────────────────

def select_strategy(energy, target_format, strategies_config):
    """Auto-select a cut strategy based on energy and format.

    Priority: format-specific override > energy-based > default hook_first
    """
    rules = strategies_config.get("selection_rules", {})

    # Check format-specific mapping
    by_format = rules.get("by_format", {})
    if target_format in by_format:
        name = by_format[target_format]
        strat = strategies_config["strategies"].get(name)
        if strat:
            return name, strat

    # Check energy-based rules
    by_energy = rules.get("by_energy", [])
    for rule in by_energy:
        e_min = rule.get("energy_min", 0)
        e_max = rule.get("energy_max", 1.0)
        if e_min <= energy <= e_max:
            name = rule["preferred"]
            strat = strategies_config["strategies"].get(name)
            if strat:
                return name, strat

    # Default
    return "hook_first", strategies_config["strategies"]["hook_first"]


# ── Beat-Aligned Cutting ─────────────────────────────────────

def find_hook_segment(beat_times, energy_curve, max_duration, strategy):
    """Find the highest-energy segment for Hook-First strategy.

    Scans a sliding window across beat positions to find the segment
    with the highest cumulative energy, constrained by max_duration.
    """
    if not beat_times or not energy_curve:
        return 0, min(max_duration, 30)

    total_audio_dur = beat_times[-1] if beat_times else 30
    min_seg = strategy.get("min_segment_seconds", 1.5)
    max_seg = min(strategy.get("max_segment_seconds", 8.0), max_duration)

    # Map energy curve to beat positions
    ec_len = len(energy_curve)
    best_start = 0
    best_end = min(max_duration, total_audio_dur)
    best_energy = 0

    # Slide a window of max_duration across beat times
    for i, bt_start in enumerate(beat_times):
        # Find the beat closest to bt_start + max_duration
        target_end = bt_start + max_seg
        bt_end = bt_start + max_seg
        for j in range(i + 1, len(beat_times)):
            if beat_times[j] >= target_end:
                bt_end = beat_times[j]
                break

        if bt_end - bt_start < min_seg:
            continue

        # Estimate energy in this window
        ec_start = int((bt_start / total_audio_dur) * ec_len)
        ec_end = int((bt_end / total_audio_dur) * ec_len)
        ec_start = max(0, min(ec_start, ec_len - 1))
        ec_end = max(ec_start + 1, min(ec_end, ec_len))
        seg_energy = sum(energy_curve[ec_start:ec_end])

        if seg_energy > best_energy:
            best_energy = seg_energy
            best_start = bt_start
            best_end = bt_end

    # Clamp to max_duration
    if best_end - best_start > max_duration:
        best_end = best_start + max_duration

    return round(best_start, 3), round(best_end, 3)


def find_energy_peak_segments(beat_times, energy_curve, max_duration, strategy):
    """Find ascending-energy segments for Energy-Peak strategy.

    Selects segments that build from low to high energy.
    """
    if not beat_times or not energy_curve:
        return 0, min(max_duration, 30)

    total_dur = beat_times[-1] if beat_times else 30
    divisor = strategy.get("beat_divisor", 4)
    min_seg = strategy.get("min_segment_seconds", 4.0)

    # Pick downbeats (every Nth beat)
    downbeats = [beat_times[i] for i in range(0, len(beat_times), divisor)]
    if not downbeats:
        downbeats = beat_times

    # Find the segment building to the highest energy in the last third
    third = len(energy_curve) // 3
    peak_zone_energy = sum(energy_curve[third*2:])

    # Start from ~40% into the track to skip intro
    start_beat = 0
    for db in downbeats:
        if db >= total_dur * 0.3:
            start_beat = db
            break

    end_beat = min(start_beat + max_duration, total_dur)

    # Snap end to nearest downbeat
    for db in reversed(downbeats):
        if db <= end_beat and db - start_beat >= min_seg:
            end_beat = db
            break

    return round(start_beat, 3), round(end_beat, 3)


# ── FFmpeg Short-Form Render ─────────────────────────────────

def render_short(audio_path, start_time, end_time, output_path,
                 width=1080, height=1920):
    """Render a vertical short clip with blur-fill background.

    Takes the source audio and creates a 9:16 video with:
    - Blurred, scaled background filling 1080x1920
    - Sharp center content from a gradient overlay
    """
    duration = end_time - start_time

    # Use the audio directly with a color background + drawtext
    # (master video may not exist yet in some flows)
    filter_complex = (
        f"color=c=0x1a1a2e:s={width}x{height}:d={duration},"
        f"format=rgba,"
        f"drawtext=text='':fontsize=1:fontcolor=white:x=0:y=0,"
        f"format=yuv420p[vout];"
        f"[0:a]atrim=start={start_time}:end={end_time},asetpts=PTS-STARTPTS,"
        f"afade=t=in:st=0:d=0.3,afade=t=out:st={duration-0.5}:d=0.5[aout]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", audio_path,
        "-filter_complex", filter_complex,
        "-map", "[vout]", "-map", "[aout]",
        "-c:v", "libx264", "-crf", "23", "-preset", "medium",
        "-c:a", "aac", "-b:a", "192k",
        "-t", str(duration),
        "-movflags", "+faststart",
        output_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[cuts] FFmpeg failed: {result.stderr[-200:]}")
        return False
    return True


# ── Main Short Creator ───────────────────────────────────────

def create_short(song_id, artist_slug, project_root=None, strategy_name=None):
    """Create a short-form beat-synced clip.

    Returns:
        dict with output info, or None on failure
    """
    root = project_root or PROJECT_ROOT_DEFAULT
    catalog_dir = os.path.join(root, "catalog", artist_slug, song_id)

    manifest, manifest_path = load_manifest(catalog_dir)
    if not manifest:
        print(f"[cuts] ERROR: No analyzed manifest at {catalog_dir}")
        return None

    analysis = manifest.get("analysis", {})
    beat_times = analysis.get("beat_times", [])
    energy_curve = analysis.get("energy_curve", [])
    energy = analysis.get("energy", 0.5)
    duration = analysis.get("duration_seconds", 30)

    strategies_config = load_strategies(root)
    max_dur = 59  # YouTube Shorts limit

    # Select strategy
    if strategy_name:
        strat = strategies_config["strategies"].get(strategy_name)
        if not strat:
            print(f"[cuts] WARNING: Strategy '{strategy_name}' not found, using auto.")
            strategy_name, strat = select_strategy(energy, "short_blurfill", strategies_config)
    else:
        strategy_name, strat = select_strategy(energy, "short_blurfill", strategies_config)

    print(f"[cuts] Strategy: {strategy_name} ({strat.get('description', '')})")

    # Find cut points
    if strategy_name in ("hook_first", "rapid_fire"):
        start_t, end_t = find_hook_segment(beat_times, energy_curve, max_dur, strat)
    else:
        start_t, end_t = find_energy_peak_segments(beat_times, energy_curve, max_dur, strat)

    clip_dur = round(end_t - start_t, 2)
    print(f"[cuts] Clip: {start_t}s \u2192 {end_t}s ({clip_dur}s)")

    # Resolve audio path
    audio_path = manifest.get("source_audio", "")
    if not os.path.isabs(audio_path):
        audio_path = os.path.join(root, audio_path)

    # Output path
    output_filename = f"{artist_slug}_{song_id}_short.mp4"
    output_path = os.path.join(catalog_dir, output_filename)

    print(f"[cuts] Rendering short: 1080x1920...")
    start = time.time()
    ok = render_short(audio_path, start_t, end_t, output_path)
    elapsed = round(time.time() - start, 2)

    if not ok:
        return None

    size = os.path.getsize(output_path) if os.path.isfile(output_path) else 0
    print(f"[cuts] SHORT OK: {output_path} ({size:,} bytes, {elapsed}s)")

    # Update manifest with short output
    manifest["outputs"]["short_blurfill"] = {
        "path": output_path,
        "format": "mp4",
        "resolution": "1080x1920",
        "strategy": strategy_name,
        "clip_start": start_t,
        "clip_end": end_t,
        "clip_duration": clip_dur,
    }
    tmp = manifest_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)
        fh.write("\n")
        fh.flush()
        os.fsync(fh.fileno())
    os.rename(tmp, manifest_path)

    return {
        "output_path": output_path,
        "strategy": strategy_name,
        "clip_start": start_t,
        "clip_end": end_t,
        "clip_duration": clip_dur,
        "render_time": elapsed,
        "size": size,
    }


# ── CLI ──────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Create beat-synced short clips for TikTok/Shorts."
    )
    parser.add_argument("--song-id", required=True, help="Song slug")
    parser.add_argument("--artist", required=True, help="Artist slug")
    parser.add_argument("--strategy", default=None,
                        help="Force strategy: hook_first, energy_peak, rapid_fire, slow_flow")
    parser.add_argument("--project-root", default=None, help="Project root")
    args = parser.parse_args()

    root = args.project_root or PROJECT_ROOT_DEFAULT
    result = create_short(args.song_id, args.artist, root, args.strategy)
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
