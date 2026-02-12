#!/usr/bin/env python3
"""
ingest_song.py — Ridgemont Studio Make Videos Pipeline
Step 1: Ingestion — Pull audio + metadata from Make-Music agent.

Handles:
- Audio file (WAV/MP3) ingestion and validation
- Metadata extraction and organization
- Creative Brief detection (creative_brief.json)
- Artist profile linkage
- Project-root-relative path setup

Usage:
    python ingest_song.py --song-id "song_001" --audio "/path/to/audio.wav" \
        --artist "DJ Chromosphere" --title "Neon Dreams" --genre "Electronic" \
        --project-root "/path/to/ridgemont"

Pipeline Position: Step 1 (first step, before Preflight + Analysis)
"""

import argparse
import json
import os
import sys
import shutil
import logging
from datetime import datetime

from cache_utils import load_cache, save_cache, cache_add_song

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

SUPPORTED_FORMATS = ['.wav', '.mp3', '.flac', '.aac', '.ogg', '.m4a']


def validate_audio(audio_path):
    """Validate audio file exists and is a supported format."""
    if not os.path.exists(audio_path):
        logger.error(f"Audio file not found: {audio_path}")
        return False
    ext = os.path.splitext(audio_path)[1].lower()
    if ext not in SUPPORTED_FORMATS:
        logger.error(f"Unsupported audio format: {ext} (supported: {SUPPORTED_FORMATS})")
        return False
    size = os.path.getsize(audio_path)
    if size < 1000:
        logger.warning(f"Audio file suspiciously small: {size} bytes")
    logger.info(f"Audio validated: {audio_path} ({size / 1024 / 1024:.1f} MB)")
    return True


def setup_song_directory(project_root, artist, song_id):
    """Create catalog directory structure for the song."""
    song_dir = os.path.join(project_root, "catalog", artist, song_id)
    os.makedirs(song_dir, exist_ok=True)
    os.makedirs(os.path.join(song_dir, "outputs"), exist_ok=True)
    logger.info(f"Song directory ready: {song_dir}")
    return song_dir


def ingest_audio(audio_source, song_dir, song_id):
    """Copy audio to catalog and return project-root-relative path."""
    ext = os.path.splitext(audio_source)[1].lower()
    dest_filename = f"audio{ext}"
    dest_path = os.path.join(song_dir, dest_filename)

    if os.path.abspath(audio_source) != os.path.abspath(dest_path):
        shutil.copy2(audio_source, dest_path)
        logger.info(f"Audio ingested: {dest_path}")
    else:
        logger.info(f"Audio already in place: {dest_path}")

    return dest_path


def get_root_relative_path(full_path, project_root):
    """Convert absolute path to project-root-relative."""
    return os.path.relpath(full_path, project_root)


def check_creative_brief(song_dir):
    """Check for creative_brief.json (highest priority in visual chain)."""
    brief_path = os.path.join(song_dir, "creative_brief.json")
    if os.path.exists(brief_path):
        with open(brief_path, 'r') as f:
            brief = json.load(f)
        logger.info(f"Creative Brief found: {brief_path}")
        return brief
    logger.info("No creative brief found — will use standard priority chain")
    return None


def check_artist_profile(project_root, artist):
    """Check for existing artist_profile.json."""
    profile_path = os.path.join(project_root, "catalog", artist, "artist_profile.json")
    if os.path.exists(profile_path):
        with open(profile_path, 'r') as f:
            profile = json.load(f)
        logger.info(f"Artist profile found: {profile_path}")
        return profile
    logger.info(f"No artist profile for {artist} — will auto-generate during analysis")
    return None


def create_ingestion_record(song_id, artist, title, genre, audio_rel_path,
                            creative_brief, artist_profile):
    """Create the ingestion record for the pipeline."""
    return {
        "song_id": song_id,
        "artist": artist,
        "title": title,
        "genre": genre,
        "audio_source": audio_rel_path,
        "has_creative_brief": creative_brief is not None,
        "has_artist_profile": artist_profile is not None,
        "ingested_at": datetime.now().isoformat(),
        "pipeline": {
            "status": "ingested",
            "next_step": "analysis"
        }
    }


def main():
    parser = argparse.ArgumentParser(description="Ingest song into Make Videos pipeline")
    parser.add_argument("--song-id", required=True, help="Unique song identifier")
    parser.add_argument("--audio", required=True, help="Path to source audio file")
    parser.add_argument("--artist", required=True, help="Artist name")
    parser.add_argument("--title", default="", help="Song title")
    parser.add_argument("--genre", default="Pop", help="Primary genre")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    args = parser.parse_args()

    project_root = os.path.abspath(args.project_root)
    logger.info(f"=== Ingesting: {args.song_id} — '{args.title}' by {args.artist} ===")

    if not validate_audio(args.audio):
        sys.exit(1)

    song_dir = setup_song_directory(project_root, args.artist, args.song_id)

    audio_dest = ingest_audio(args.audio, song_dir, args.song_id)
    audio_rel_path = get_root_relative_path(audio_dest, project_root)

    creative_brief = check_creative_brief(song_dir)
    artist_profile = check_artist_profile(project_root, args.artist)

    record = create_ingestion_record(
        args.song_id, args.artist, args.title, args.genre,
        audio_rel_path, creative_brief, artist_profile
    )

    record_path = os.path.join(song_dir, "ingestion_record.json")
    with open(record_path, 'w') as f:
        json.dump(record, f, indent=2)
    logger.info(f"Ingestion record saved: {record_path}")

    # Update catalog cache
    try:
        cache = load_cache()
        cache_add_song(cache, args.artist, args.song_id, args.title, args.genre, audio_dest)
        save_cache(cache)
        logger.info(f"Catalog cache updated for {args.song_id}")
    except Exception as e:
        logger.warning(f"Could not update catalog cache: {e}")

    try:
        progress_file = os.path.join(song_dir, 'progress_log.json')
        progress_data = {
            'song_id': args.song_id,
            'artist': args.artist,
            'title': args.title,
            'stages': {
                'ingestion': {
                    'completed': datetime.now().isoformat(),
                    'audio_format': os.path.splitext(args.audio)[1],
                    'has_creative_brief': creative_brief is not None,
                    'has_artist_profile': artist_profile is not None
                }
            }
        }
        with open(progress_file, 'w') as f:
            json.dump(progress_data, f, indent=2)
        logger.info(f"Progress log initialized: {progress_file}")
    except Exception as e:
        logger.warning(f"Could not write progress log: {e}")

    logger.info(f"=== Ingestion complete. Next: python analyze_catalog.py --song-id {args.song_id} --audio {audio_rel_path} --artist \"{args.artist}\" --genre \"{args.genre}\" ===")


if __name__ == "__main__":
    main()
