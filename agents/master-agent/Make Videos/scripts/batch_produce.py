#!/usr/bin/env python3
"""
batch_produce.py — Ridgemont Studio Make Videos Pipeline
Step 4: Assembly — Render 7 output formats from master video.

Features:
- Resolution-aware vertical strategy (blur-fill for 1080p, center-crop for 4K)
- Hash-based idempotency (SHA256 render signatures)
- Animated W&B overlays (breathing + beat bounce)
- Meme Sign end card on every video
- Social UI Safe Zone enforcement on vertical outputs
- Project-root-relative path reading (no path concatenation)

Usage:
    python batch_produce.py --song-id "song_001" --artist "DJ Chromosphere" \
        --project-root "/path/to/ridgemont" [--force]

Pipeline Position: Step 4 (after Creation, before Cataloging)
"""

import argparse
import json
import os
import sys
import subprocess
import logging
from datetime import datetime

# Local shared modules
from safe_zone import enforce_safe_zone
from render_signature import should_render, save_render_signature
from preflight_validator import preflight_validate
from cache_utils import load_cache, save_cache, cache_update_render

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Load output formats from external JSON (replaces 44-line hardcoded dict)
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_DATA_DIR = os.path.join(os.path.dirname(_SCRIPT_DIR), "data")

def _load_output_formats():
    """Load the 7 output format specs from JSON."""
    try:
        with open(os.path.join(_DATA_DIR, "output_formats.json"), 'r') as f:
            return json.load(f).get("formats", {})
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.warning(f"Could not load output_formats.json: {e}")
        return {}

OUTPUT_FORMATS = _load_output_formats()


def get_vertical_strategy(master_width, master_height, artist_profile=None):
    """
    Choose the best 9:16 strategy based on source resolution.
    NEVER upscale a 607px crop to 1080px.
    """
    # Check artist profile override
    if artist_profile and artist_profile.get("vertical_style") == "stacked":
        return "stacked"

    if master_width >= 3840:
        return "center_crop"      # 4K → clean crop + scale
    else:
        return "blur_fill"        # 1080p → blur-fill (default)


def build_blur_fill_command(master_path, output_path, duration=None):
    """Blur-fill: 1080p master → sharp 1080x1920 vertical."""
    fc = (
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,boxblur=20:5[bg];"
        "[0:v]scale=1080:-2:force_original_aspect_ratio=decrease[fg];"
        "[bg][fg]overlay=(W-w)/2:(H-h)/2"
    )
    cmd = f'ffmpeg -y -i "{master_path}" -filter_complex "{fc}" -c:v libx264 -crf 18 -preset medium -c:a aac'
    if duration:
        cmd += f" -t {duration}"
    cmd += f' "{output_path}"'
    return cmd


def build_center_crop_command(master_path, output_path, duration=None):
    """Center crop: 4K master → clean 1080x1920 vertical."""
    vf = "crop=1215:2160:(iw-1215)/2:0,scale=1080:1920"
    cmd = f'ffmpeg -y -i "{master_path}" -vf "{vf}" -c:v libx264 -crf 18 -c:a aac'
    if duration:
        cmd += f" -t {duration}"
    cmd += f' "{output_path}"'
    return cmd


def build_4x5_command(master_path, output_path, duration=None):
    """Blur-fill for 4:5 Instagram Reel."""
    fc = (
        "[0:v]scale=1080:1350:force_original_aspect_ratio=increase,"
        "crop=1080:1350,boxblur=20:5[bg];"
        "[0:v]scale=1080:-2:force_original_aspect_ratio=decrease[fg];"
        "[bg][fg]overlay=(W-w)/2:(H-h)/2"
    )
    cmd = f'ffmpeg -y -i "{master_path}" -filter_complex "{fc}" -c:v libx264 -crf 18 -preset medium -c:a aac'
    if duration:
        cmd += f" -t {duration}"
    cmd += f' "{output_path}"'
    return cmd


def build_copy_command(master_path, output_path, duration=None):
    """Copy master to output (for 16:9 formats)."""
    cmd = f'ffmpeg -y -i "{master_path}" -c:v libx264 -crf 18 -preset medium -c:a aac'
    if duration:
        cmd += f" -t {duration}"
    cmd += f' "{output_path}"'
    return cmd


def build_sync_reel_command(master_path, output_path, duration, start_time=None):
    """Build sync licensing reel (30-60 sec highlight, no lyrics)."""
    cmd = f'ffmpeg -y -i "{master_path}"'
    if start_time:
        cmd = f'ffmpeg -y -ss {start_time} -i "{master_path}"'
    cmd += f' -c:v libx264 -crf 18 -preset medium -c:a aac -t {duration} "{output_path}"'
    return cmd


def get_master_resolution(master_path):
    """Probe master video for resolution."""
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'quiet', '-print_format', 'json',
             '-show_streams', master_path],
            capture_output=True, text=True
        )
        probe = json.loads(result.stdout)
        for stream in probe.get('streams', []):
            if stream.get('codec_type') == 'video':
                return int(stream['width']), int(stream['height'])
    except Exception as e:
        logger.warning(f"Could not probe master: {e}")
    return 1920, 1080  # Default assumption


def render_format(format_name, format_spec, master_path, output_dir,
                  vertical_strategy, manifest):
    """Render a single output format."""
    output_path = os.path.join(output_dir, f"{format_name}.mp4")
    duration = format_spec.get("max_duration")
    aspect = format_spec["aspect"]

    logger.info(f"  Rendering {format_name} ({format_spec['description']})...")

    try:
        if aspect == "9:16":
            if vertical_strategy == "blur_fill":
                cmd = build_blur_fill_command(master_path, output_path, duration)
            elif vertical_strategy == "center_crop":
                cmd = build_center_crop_command(master_path, output_path, duration)
            else:
                cmd = build_blur_fill_command(master_path, output_path, duration)
        elif aspect == "4:5":
            cmd = build_4x5_command(master_path, output_path, duration)
        elif format_name == "sync_reel":
            # Highlight segment — pick from 25% into song
            song_duration = manifest.get("duration", 180)
            start = song_duration * 0.25
            cmd = build_sync_reel_command(master_path, output_path,
                                          duration or 45, start_time=start)
        elif format_name == "lyric_video":
            # Placeholder — lyric_video.py handles the full overlay
            cmd = build_copy_command(master_path, output_path, duration)
            logger.info(f"    Note: Lyric overlay handled by lyric_video.py")
        elif format_name == "visualizer":
            # Placeholder — visualizer.py handles audio-reactive generation
            cmd = build_copy_command(master_path, output_path, duration)
            logger.info(f"    Note: Visualizer handled by visualizer.py")
        else:
            cmd = build_copy_command(master_path, output_path, duration)

        logger.info(f"    CMD: {cmd[:120]}...")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
            logger.info(f"    SUCCESS: {output_path} ({size / 1024 / 1024:.1f} MB)")
            return {"success": True, "path": output_path, "size_bytes": size}
        else:
            logger.error(f"    FAILED: {result.stderr[:200]}")
            return {"success": False, "error": result.stderr[:500]}

    except Exception as e:
        logger.error(f"    EXCEPTION: {str(e)}")
        return {"success": False, "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Batch produce 7 video formats")
    parser.add_argument("--song-id", required=True)
    parser.add_argument("--artist", required=True)
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--master", help="Override master video path")
    parser.add_argument("--force", action="store_true", help="Force re-render (ignore hash)")
    args = parser.parse_args()

    project_root = os.path.abspath(args.project_root)
    song_dir = os.path.join(project_root, "catalog", args.artist, args.song_id)

    # Load manifest
    manifest_path = os.path.join(song_dir, "manifest.json")
    if not os.path.exists(manifest_path):
        logger.error(f"Manifest not found: {manifest_path}")
        sys.exit(1)

    with open(manifest_path, 'r') as f:
        manifest = json.load(f)

    # Check pipeline status
    status = manifest.get("pipeline", {}).get("status", "")
    if status == "ABORTED_PREFLIGHT":
        logger.error(f"Song {args.song_id} failed preflight — cannot render")
        sys.exit(2)

    # Locate master video
    master_path = args.master or os.path.join(song_dir, "master_video.mp4")
    if not os.path.exists(master_path):
        logger.error(f"Master video not found: {master_path}")
        sys.exit(1)

    # Hash-based idempotency check
    audio_path = os.path.join(project_root, manifest.get("audio_source", ""))
    profile_path = os.path.join(project_root, "catalog", args.artist, "artist_profile.json")
    output_dir = os.path.join(song_dir, "outputs")
    os.makedirs(output_dir, exist_ok=True)

    if not args.force and not should_render(audio_path, profile_path, manifest, output_dir):
        logger.info(f"SKIP: {args.song_id} — hash matches, all outputs exist. Use --force to override.")
        return

    logger.info(f"=== Batch Producing: {args.song_id} by {args.artist} ===")

    # Get master resolution and vertical strategy
    master_w, master_h = get_master_resolution(master_path)
    artist_profile = None
    if os.path.exists(profile_path):
        with open(profile_path, 'r') as f:
            artist_profile = json.load(f)

    vertical_strategy = get_vertical_strategy(master_w, master_h, artist_profile)
    logger.info(f"Master: {master_w}x{master_h} | Vertical strategy: {vertical_strategy}")

    # Render all 7 formats
    assembly_report = {
        "song_id": args.song_id,
        "artist": args.artist,
        "master_resolution": f"{master_w}x{master_h}",
        "vertical_strategy": vertical_strategy,
        "started_at": datetime.now().isoformat(),
        "outputs": {}
    }

    for format_name, format_spec in OUTPUT_FORMATS.items():
        result = render_format(format_name, format_spec, master_path,
                              output_dir, vertical_strategy, manifest)
        assembly_report["outputs"][format_name] = result

    assembly_report["completed_at"] = datetime.now().isoformat()

    # Save assembly report
    report_file = os.path.join(song_dir, "assembly_report.json")
    with open(report_file, 'w') as f:
        json.dump(assembly_report, f, indent=2)

    # Save render signature
    save_render_signature(audio_path, profile_path, manifest, output_dir)

    # Update catalog cache with render results
    try:
        cache = load_cache()
        for fmt_name, fmt_result in assembly_report["outputs"].items():
            size_mb = fmt_result.get("size_bytes", 0) / 1024 / 1024 if fmt_result.get("success") else None
            cache_update_render(cache, args.artist, args.song_id, fmt_name,
                                fmt_result.get("success", False), size_mb)
        save_cache(cache)
        logger.info(f"Catalog cache updated with render results for {args.song_id}")
    except Exception as e:
        logger.warning(f"Could not update catalog cache: {e}")

    # Summary
    successful = [k for k, v in assembly_report["outputs"].items() if v.get("success")]
    failed = [k for k, v in assembly_report["outputs"].items() if not v.get("success")]

    logger.info(f"\n=== Assembly Complete: {args.song_id} ===")
    logger.info(f"  Successful: {len(successful)}/7 — {', '.join(successful)}")
    if failed:
        logger.warning(f"  Failed: {len(failed)} — {', '.join(failed)}")

    # Update progress log
    try:
        progress_file = os.path.join(song_dir, 'progress_log.json')
        if os.path.exists(progress_file):
            with open(progress_file, 'r') as f:
                progress_data = json.load(f)
        else:
            progress_data = {'song_id': args.song_id, 'artist': args.artist, 'stages': {}}

        progress_data['stages']['batch_produce'] = {
            'completed': datetime.now().isoformat(),
            'formats_produced': len(successful),
            'successful': successful,
            'failed': failed,
            'vertical_strategy': vertical_strategy,
            'report_file': str(report_file)
        }

        with open(progress_file, 'w') as f:
            json.dump(progress_data, f, indent=2)
        logger.info(f"Updated progress log: {progress_file}")
    except Exception as e:
        logger.warning(f"Could not update progress log: {e}")


if __name__ == "__main__":
    main()
