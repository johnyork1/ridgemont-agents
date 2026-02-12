#!/usr/bin/env python3
"""
generate_thumbnails.py — Ridgemont Studio
Generate branded thumbnails for all video formats.

Uses Pillow for local generation, with Canva Bulk Create integration
for Brand Kit thumbnails at scale.

Usage:
    python generate_thumbnails.py --song-id "song_001" --artist "DJ Chromosphere" \
        --title "Neon Dreams" --project-root "/path/to/ridgemont"
"""

import argparse
import json
import os
import sys
import logging
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont

from safe_zone import enforce_safe_zone

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

THUMBNAIL_SIZES = {
    "youtube": (1280, 720),
    "youtube_short": (1080, 1920),
    "tiktok": (1080, 1920),
    "instagram": (1080, 1080),
    "spotify": (640, 640),
}

FONT_PATHS = [
    "fonts/bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]

FONT_PATHS_REGULAR = [
    "fonts/regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def find_font(paths, size):
    for path in paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def load_artist_colors(project_root, artist):
    """Load artist profile for branded colors."""
    profile_path = os.path.join(project_root, "catalog", artist, "artist_profile.json")
    if os.path.exists(profile_path):
        with open(profile_path, 'r') as f:
            profile = json.load(f)
        vi = profile.get("visual_identity", {})
        colors = vi.get("primary_colors", ["#1a1a2e", "#FFFFFF", "#0077CC"])
        return colors
    return ["#1a1a2e", "#FFFFFF", "#0077CC"]


def create_thumbnail(title, artist_name, size, bg_color, text_color,
                     accent_color, output_path, character_overlay=None):
    """Create a single branded thumbnail."""
    w, h = size
    img = Image.new("RGBA", (w, h), bg_color)
    draw = ImageDraw.Draw(img)

    # Title text
    title_size = max(24, min(72, w // 15))
    artist_size = max(18, min(48, w // 20))
    font_title = find_font(FONT_PATHS, title_size)
    font_artist = find_font(FONT_PATHS_REGULAR, artist_size)

    cx, cy = w // 2, h // 2

    # Draw accent bar
    bar_height = int(h * 0.08)
    draw.rectangle([(0, cy - bar_height * 2), (w, cy + bar_height * 2)],
                   fill=accent_color + "40")  # Semi-transparent

    # Draw text
    draw.text((cx, cy - 20), title, font=font_title,
              anchor="mm", fill=text_color)
    draw.text((cx, cy + title_size), f"by {artist_name}", font=font_artist,
              anchor="mm", fill=text_color + "CC")

    # Add W&B character overlay if provided
    if character_overlay and os.path.exists(character_overlay):
        try:
            char_img = Image.open(character_overlay).convert("RGBA")
            char_w = int(w * 0.25)
            char_h = int(char_img.height * (char_w / char_img.width))
            char_img = char_img.resize((char_w, char_h), Image.LANCZOS)
            # Position in bottom-right safe zone
            pos_x = w - char_w - int(w * 0.05)
            pos_y = h - char_h - int(h * 0.05)
            img.paste(char_img, (pos_x, pos_y), char_img)
        except Exception as e:
            logger.warning(f"Could not add character overlay: {e}")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path)
    logger.info(f"Thumbnail created: {output_path} ({w}x{h})")
    return True


def main():
    parser = argparse.ArgumentParser(description="Generate video thumbnails")
    parser.add_argument("--song-id", required=True)
    parser.add_argument("--artist", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--formats", nargs="*", default=list(THUMBNAIL_SIZES.keys()))
    args = parser.parse_args()

    project_root = os.path.abspath(args.project_root)
    colors = load_artist_colors(project_root, args.artist)
    bg_color = colors[0] if len(colors) > 0 else "#1a1a2e"
    text_color = colors[1] if len(colors) > 1 else "#FFFFFF"
    accent_color = colors[2] if len(colors) > 2 else "#0077CC"

    output_dir = os.path.join(project_root, "catalog", args.artist, args.song_id, "thumbnails")
    os.makedirs(output_dir, exist_ok=True)

    # Load manifest for character pose
    manifest_path = os.path.join(project_root, "catalog", args.artist, args.song_id, "manifest.json")
    together_pose = None
    if os.path.exists(manifest_path):
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        together_pose = manifest.get("together_pose")
        if together_pose:
            together_pose = os.path.join(project_root, together_pose)

    created = 0
    for fmt in args.formats:
        if fmt not in THUMBNAIL_SIZES:
            logger.warning(f"Unknown format: {fmt}")
            continue
        output_path = os.path.join(output_dir, f"thumb_{fmt}.png")
        if create_thumbnail(args.title, args.artist, THUMBNAIL_SIZES[fmt],
                           bg_color, text_color, accent_color, output_path,
                           together_pose):
            created += 1

    logger.info(f"Generated {created}/{len(args.formats)} thumbnails")


if __name__ == "__main__":
    main()
