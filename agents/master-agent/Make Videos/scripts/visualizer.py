#!/usr/bin/env python3
"""
visualizer.py — Ridgemont Studio
Generate audio-reactive visualizer videos.

Phase 1: FFmpeg-based waveform/spectrum visualization.
Phase 2+: Deforum or custom Python audio-reactive generation.

Usage:
    python visualizer.py --song-id "song_001" --artist "DJ Chromosphere" \
        --project-root "/path/to/ridgemont"
"""

import argparse
import json
import os
import sys
import subprocess
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


def load_artist_colors(project_root, artist):
    """Load artist profile for branded visualization colors."""
    profile_path = os.path.join(project_root, "catalog", artist, "artist_profile.json")
    if os.path.exists(profile_path):
        with open(profile_path, 'r') as f:
            profile = json.load(f)
        vi = profile.get("visual_identity", {})
        colors = vi.get("primary_colors", ["#00E5FF", "#FF00FF", "#0D0D0D"])
        return colors
    return ["#00E5FF", "#FF00FF", "#0D0D0D"]


def build_showwaves_command(audio_path, output_path, duration, colors):
    """Build FFmpeg showwaves visualization."""
    fg_color = colors[0].replace("#", "0x") if colors else "0x00E5FF"
    bg_color = colors[2].replace("#", "0x") if len(colors) > 2 else "0x0D0D0D"

    cmd = (
        f'ffmpeg -y -i "{audio_path}" '
        f'-filter_complex "'
        f'[0:a]showwaves=s=1920x1080:mode=cline:rate=30:'
        f'colors={fg_color}[v]'
        f'" -map "[v]" -map 0:a '
        f'-c:v libx264 -crf 18 -preset medium -c:a aac '
        f'-t {duration:.1f} '
        f'"{output_path}"'
    )
    return cmd


def build_showspectrum_command(audio_path, output_path, duration, colors):
    """Build FFmpeg showspectrum visualization."""
    cmd = (
        f'ffmpeg -y -i "{audio_path}" '
        f'-filter_complex "'
        f'[0:a]showspectrum=s=1920x1080:mode=combined:'
        f'color=fire:scale=cbrt:fscale=log[v]'
        f'" -map "[v]" -map 0:a '
        f'-c:v libx264 -crf 18 -preset medium -c:a aac '
        f'-t {duration:.1f} '
        f'"{output_path}"'
    )
    return cmd


def build_avectorscope_command(audio_path, output_path, duration, colors):
    """Build FFmpeg audio vectorscope visualization."""
    cmd = (
        f'ffmpeg -y -i "{audio_path}" '
        f'-filter_complex "'
        f'[0:a]avectorscope=s=1920x1080:draw=line:mode=lissajous:'
        f'rate=30[v]'
        f'" -map "[v]" -map 0:a '
        f'-c:v libx264 -crf 18 -preset medium -c:a aac '
        f'-t {duration:.1f} '
        f'"{output_path}"'
    )
    return cmd


VISUALIZER_TYPES = {
    "waveform": build_showwaves_command,
    "spectrum": build_showspectrum_command,
    "vectorscope": build_avectorscope_command,
}


def select_visualizer_type(genre):
    """Select best visualizer type based on genre."""
    genre_lower = (genre or "").lower()
    if any(g in genre_lower for g in ["electronic", "edm", "techno", "house"]):
        return "spectrum"
    elif any(g in genre_lower for g in ["jazz", "classical", "ambient"]):
        return "vectorscope"
    return "waveform"


def main():
    parser = argparse.ArgumentParser(description="Generate audio-reactive visualizer")
    parser.add_argument("--song-id", required=True)
    parser.add_argument("--artist", required=True)
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--type", choices=list(VISUALIZER_TYPES.keys()),
                        help="Override visualizer type")
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

    audio_path = os.path.join(project_root, manifest.get("audio_source", ""))
    if not os.path.exists(audio_path):
        logger.error(f"Audio not found: {audio_path}")
        sys.exit(1)

    duration = manifest.get("duration", 180)
    genre = manifest.get("genre", "Pop")
    colors = load_artist_colors(project_root, args.artist)

    # Select visualizer type
    viz_type = args.type or select_visualizer_type(genre)
    logger.info(f"Visualizer type: {viz_type} (genre: {genre})")

    output_path = os.path.join(song_dir, "outputs", "visualizer.mp4")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Build and run command
    build_fn = VISUALIZER_TYPES[viz_type]
    cmd = build_fn(audio_path, output_path, duration, colors)

    logger.info("Rendering visualizer...")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        size = os.path.getsize(output_path) / 1024 / 1024
        logger.info(f"Visualizer created: {output_path} ({size:.1f} MB)")
    else:
        logger.error(f"Render failed: {result.stderr[:300]}")
        sys.exit(1)


if __name__ == "__main__":
    main()
