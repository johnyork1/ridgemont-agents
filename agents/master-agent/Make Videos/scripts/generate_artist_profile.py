#!/usr/bin/env python3
"""
generate_artist_profile.py — Ridgemont Studio
Auto-generate artist_profile.json files from genre defaults.

Creates a starter visual identity profile for artists who don't yet have one.
Profiles are flagged auto_generated: true, human_reviewed: false.

Usage:
    python generate_artist_profile.py --artist "DJ Chromosphere" --genre "Electronic" \
        --project-root "/path/to/ridgemont"
"""

import argparse
import json
import os
import sys
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Load genre visual identity from external JSON (replaces 115-line hardcoded dict)
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_DATA_DIR = os.path.join(os.path.dirname(_SCRIPT_DIR), "data")
_VISUAL_ID_PATH = os.path.join(_DATA_DIR, "genre_visual_identity.json")

def _load_genre_data():
    """Load genre visual identity data from JSON file."""
    try:
        with open(_VISUAL_ID_PATH, 'r') as f:
            data = json.load(f)
        return data.get("genres", {}), data.get("_default", {})
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.warning(f"Could not load {_VISUAL_ID_PATH}: {e} — using minimal fallback")
        return {}, {
            "primary_colors": ["#333333", "#FFFFFF", "#0077CC"],
            "secondary_colors": ["#666666", "#00AAFF"],
            "typography": {"heading_font": "Roboto", "body_font": "Open Sans", "style": "clean, modern"},
            "visual_motifs": ["abstract shapes", "gradient backgrounds"],
            "color_grading": "balanced, neutral tones",
            "camera_style": "smooth pan, centered framing",
            "comfyui_workflow": "",
            "sd_prompt_prefix": "abstract music visualization, clean modern aesthetic"
        }

GENRE_DEFAULTS, DEFAULT_VISUAL = _load_genre_data()


def get_genre_visual(genre):
    """Look up visual defaults for a genre."""
    genre_lower = genre.lower().strip()
    # Try exact match first
    if genre_lower in GENRE_DEFAULTS:
        return GENRE_DEFAULTS[genre_lower]
    # Try partial match
    for key in GENRE_DEFAULTS:
        if key in genre_lower or genre_lower in key:
            return GENRE_DEFAULTS[key]
    return DEFAULT_VISUAL


def generate_profile(artist_name, genre, publishing_entity=None):
    """Generate a complete artist profile from genre defaults."""
    visual = get_genre_visual(genre)

    profile = {
        "artist_name": artist_name,
        "genre": genre,
        "publishing_entity": publishing_entity or "Ridgemont Studio",
        "visual_identity": visual,
        "vertical_style": "blur_fill",
        "weeter_blubby_default": "end_card_meme_sign",
        "weeter_blubby_frequency": "every_video",
        "created": datetime.now().strftime("%Y-%m-%d"),
        "auto_generated": True,
        "human_reviewed": False
    }
    return profile


def main():
    parser = argparse.ArgumentParser(description="Generate artist visual profile")
    parser.add_argument("--artist", required=True, help="Artist name")
    parser.add_argument("--genre", required=True, help="Primary genre")
    parser.add_argument("--publisher", default=None, help="Publishing entity")
    parser.add_argument("--project-root", default=".", help="Project root")
    parser.add_argument("--force", action="store_true", help="Overwrite existing profile")
    args = parser.parse_args()

    project_root = os.path.abspath(args.project_root)
    artist_dir = os.path.join(project_root, "catalog", args.artist)
    profile_path = os.path.join(artist_dir, "artist_profile.json")

    # Check for existing profile
    if os.path.exists(profile_path) and not args.force:
        logger.info(f"Profile already exists: {profile_path}")
        logger.info("Use --force to overwrite")
        return

    os.makedirs(artist_dir, exist_ok=True)

    profile = generate_profile(args.artist, args.genre, args.publisher)

    with open(profile_path, 'w') as f:
        json.dump(profile, f, indent=2)

    logger.info(f"Profile generated: {profile_path}")
    logger.info(f"  Genre: {args.genre} | Style: {profile['visual_identity'].get('color_grading', 'default')}")
    logger.info(f"  REMINDER: Set human_reviewed: true after review")


if __name__ == "__main__":
    main()
