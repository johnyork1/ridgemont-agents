#!/usr/bin/env python3
"""
meme_sign_render.py — Ridgemont Studio
Render the Meme Sign end card with Song Title + Artist Name.

Template: assets/characters/together/meme_sign/blank_sign.png
Output: Rendered sign with text, ready for video compositing.

Usage:
    python meme_sign_render.py --title "Neon Dreams" --artist "DJ Chromosphere" \
        --template "assets/characters/together/meme_sign/blank_sign.png" \
        --output "catalog/artist/song/meme_sign_rendered.png"
"""

import argparse
import os
import sys
import logging

from PIL import Image, ImageDraw, ImageFont

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Default font paths (fallback chain)
FONT_PATHS = [
    "fonts/bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
]

FONT_PATHS_REGULAR = [
    "fonts/regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
]


def find_font(paths, size):
    """Find first available font from path list."""
    for path in paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def generate_meme_sign(song_title, artist_name, sign_template_path, output_path):
    """
    Render Meme Sign with song title and artist name.
    Positions text centered on the sign template.
    """
    if not os.path.exists(sign_template_path):
        logger.error(f"Sign template not found: {sign_template_path}")
        return False

    sign = Image.open(sign_template_path).convert("RGBA")
    draw = ImageDraw.Draw(sign)

    font_title = find_font(FONT_PATHS, 48)
    font_artist = find_font(FONT_PATHS_REGULAR, 36)

    cx, cy = sign.width // 2, sign.height // 2

    draw.text((cx, cy - 30), song_title, font=font_title,
              anchor="mm", fill="black")

    draw.text((cx, cy + 30), f"by {artist_name}", font=font_artist,
              anchor="mm", fill="#333333")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    sign.save(output_path)
    logger.info(f"Meme Sign rendered: {output_path}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Render Meme Sign end card")
    parser.add_argument("--title", required=True, help="Song title")
    parser.add_argument("--artist", required=True, help="Artist name")
    parser.add_argument("--template", required=True, help="Path to blank_sign.png")
    parser.add_argument("--output", required=True, help="Output path for rendered sign")
    args = parser.parse_args()

    success = generate_meme_sign(args.title, args.artist, args.template, args.output)
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
