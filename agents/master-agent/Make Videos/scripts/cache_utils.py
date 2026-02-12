#!/usr/bin/env python3
"""
cache_utils.py — Shared catalog cache read/write utilities.
Atomic writes via .tmp + os.rename(). No file locking (pipeline is sequential).
"""

import hashlib
import json
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SCRIPT_DIR)
CACHE_PATH = os.path.join(_PROJECT_ROOT, "catalog_cache.json")
CACHE_TMP = CACHE_PATH + ".tmp"


def _empty_cache():
    """Return a minimal empty cache structure."""
    return {
        "version": "1.0",
        "last_updated": datetime.now().isoformat(),
        "stats": {"total_songs": 0, "analyzed": 0, "pending_analysis": 0,
                  "failed": 0, "fully_rendered": 0},
        "songs": {}
    }


def load_cache():
    """Load the catalog cache. Returns empty cache if missing or corrupt."""
    try:
        with open(CACHE_PATH, 'r') as f:
            data = json.load(f)
        if "songs" not in data:
            data["songs"] = {}
        return data
    except (FileNotFoundError, json.JSONDecodeError):
        return _empty_cache()


def save_cache(cache):
    """Atomic write: dump to .tmp, then rename."""
    cache["last_updated"] = datetime.now().isoformat()
    _rebuild_stats(cache)
    with open(CACHE_TMP, 'w') as f:
        json.dump(cache, f, indent=2)
    os.rename(CACHE_TMP, CACHE_PATH)


def _rebuild_stats(cache):
    """Recompute stats from song entries."""
    songs = cache.get("songs", {})
    total = len(songs)
    analyzed = sum(1 for s in songs.values() if s.get("status") in ("analyzed", "complete"))
    pending = sum(1 for s in songs.values() if s.get("status") == "pending_analysis")
    failed = sum(1 for s in songs.values() if s.get("status") == "failed")
    complete = sum(1 for s in songs.values() if s.get("status") == "complete")
    cache["stats"] = {
        "total_songs": total,
        "analyzed": analyzed,
        "pending_analysis": pending,
        "failed": failed,
        "fully_rendered": complete
    }


def song_key(artist, song_id):
    """Canonical cache key: 'artist/song_id'."""
    return f"{artist}/{song_id}"


def sha256_file(filepath):
    """Compute SHA256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def cache_add_song(cache, artist, song_id, title, genre, audio_path):
    """Add or update a song entry at ingestion time."""
    key = song_key(artist, song_id)
    audio_hash = sha256_file(audio_path) if os.path.exists(audio_path) else None
    now = datetime.now().isoformat()

    existing = cache["songs"].get(key, {})
    old_hash = existing.get("audio_hash")

    # If hash matches, song hasn't changed — preserve existing data
    if old_hash and old_hash == audio_hash and existing.get("status") != "failed":
        logger.info(f"Cache: {key} unchanged (hash match)")
        return False  # No update needed

    cache["songs"][key] = {
        "artist": artist,
        "title": title,
        "genre": genre,
        "song_id": song_id,
        "audio_hash": audio_hash,
        "status": "pending_analysis",
        "ingested_at": now,
        "analysis": None,
        "outputs": {}
    }
    logger.info(f"Cache: {key} added/updated → pending_analysis")
    return True


def cache_update_analysis(cache, artist, song_id, analysis_data):
    """Update a song's analysis results after analyze_catalog.py completes."""
    key = song_key(artist, song_id)
    entry = cache["songs"].get(key)
    if not entry:
        logger.warning(f"Cache: {key} not found — creating stub entry")
        entry = {"artist": artist, "song_id": song_id, "status": "pending_analysis",
                 "audio_hash": None, "outputs": {}}
        cache["songs"][key] = entry

    entry["status"] = "analyzed"
    entry["analysis"] = {
        "completed_at": datetime.now().isoformat(),
        "bpm": analysis_data.get("bpm"),
        "key": f"{analysis_data.get('key_name', '?')} {analysis_data.get('mode', '?')}",
        "energy": analysis_data.get("energy_category"),
        "duration": analysis_data.get("duration"),
        "reliable": analysis_data.get("analysis_reliable", False)
    }
    logger.info(f"Cache: {key} → analyzed")


def cache_update_render(cache, artist, song_id, format_name, success, size_mb=None):
    """Record a render result for a specific output format."""
    key = song_key(artist, song_id)
    entry = cache["songs"].get(key)
    if not entry:
        return

    entry["outputs"][format_name] = {
        "exists": success,
        "size_mb": round(size_mb, 1) if size_mb else None,
        "rendered_at": datetime.now().isoformat()
    }

    # Check if all 7 formats are rendered successfully
    successful = sum(1 for v in entry["outputs"].values() if v.get("exists"))
    if successful >= 7:
        entry["status"] = "complete"
        logger.info(f"Cache: {key} → complete (all 7 formats)")
