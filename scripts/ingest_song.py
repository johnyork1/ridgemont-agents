#!/usr/bin/env python3
"""ingest_song.py - Step 1 of the Make Videos pipeline.

Imports an MP3 file into the pipeline by:
  1. Computing its SHA256 fingerprint
  2. Checking the catalog cache for duplicates
  3. Creating the artist/song directory structure in catalog/
  4. Copying the MP3 into the catalog
  5. Writing an initial ingestion manifest (manifest.json)
  6. Updating the catalog cache

Usage:
    python ingest_song.py <mp3_path> --artist "Artist Name" --title "Song Title" --genre reggae
    python ingest_song.py <mp3_path> --artist "Artist" --title "Song" --project-root /path/to/root
"""
import argparse
import json
import os
import shutil
import sys
import time

# Add scripts directory to path for local imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cache_utils import load_cache, save_cache, file_hash, get_default_cache_path, make_entry, resolve_path


def slugify(text):
    """Convert text to a filesystem-safe slug."""
    slug = text.lower().strip()
    slug = slug.replace("'", "").replace('"', "")
    for ch in " _/\\:*?\"<>|&!@#$%^()+=[]{}":
        slug = slug.replace(ch, "_")
    while "__" in slug:
        slug = slug.replace("__", "_")
    return slug.strip("_")


def validate_mp3(mp3_path):
    """Verify the input file exists and looks like an MP3."""
    if not os.path.isfile(mp3_path):
        print(f"[ingest] ERROR: File not found: {mp3_path}")
        return False
    ext = os.path.splitext(mp3_path)[1].lower()
    if ext not in (".mp3", ".wav", ".flac", ".m4a", ".ogg"):
        print(f"[ingest] WARNING: Unexpected extension '{ext}', proceeding anyway.")
    size = os.path.getsize(mp3_path)
    if size < 1024:
        print(f"[ingest] ERROR: File too small ({size} bytes), likely corrupt.")
        return False
    return True


def build_catalog_path(project_root, artist, title):
    """Build the catalog directory path for this song."""
    artist_slug = slugify(artist)
    title_slug = slugify(title)
    return os.path.join(project_root, "catalog", artist_slug, title_slug)


def check_duplicate(cache_path, source_hash):
    """Check if this audio file has already been ingested."""
    cache = load_cache(cache_path)
    for key, entry in cache.items():
        if entry.get("source_hash") == source_hash:
            return key, entry
    return None, None


def create_manifest(mp3_path, artist, title, genre, catalog_dir, source_hash):
    """Create the initial ingestion manifest."""
    audio_filename = os.path.basename(mp3_path)
    catalog_audio_path = os.path.join(catalog_dir, audio_filename)

    manifest = {
        "artist": artist,
        "title": title,
        "genre": genre,
        "source_audio": catalog_audio_path,
        "source_hash": source_hash,
        "ingested_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "pipeline_stage": "ingested",
        "analysis": None,
        "mood": None,
        "characters": {
            "weeter": {"pose_path": None, "animation": None},
            "blubby": {"pose_path": None, "animation": None},
            "together": {"pose_path": None, "animation": None},
        },
        "outputs": {},
        "render_signature": None,
    }
    return manifest


def ingest(mp3_path, artist, title, genre, project_root=None, force=False):
    """Run the full ingestion pipeline for a single song.

    Args:
        mp3_path: Path to the source audio file.
        artist: Artist name.
        title: Song title.
        genre: Genre tag (should match genre_defaults.json keys).
        project_root: Project root directory (default: cwd).
        force: If True, re-ingest even if duplicate found.

    Returns:
        Tuple (success: bool, manifest_path: str or None)
    """
    root = project_root or os.getcwd()
    cache_path = get_default_cache_path(root)

    # Step 1: Validate input
    print(f"[ingest] Validating: {mp3_path}")
    if not validate_mp3(mp3_path):
        return False, None

    # Step 2: Compute SHA256
    print("[ingest] Computing SHA256 fingerprint...")
    source_hash = file_hash(mp3_path)
    print(f"[ingest] Hash: {source_hash[:16]}...")

    # Step 3: Check for duplicates
    if not force:
        dup_key, dup_entry = check_duplicate(cache_path, source_hash)
        if dup_key:
            print(f"[ingest] SKIP: Already ingested as '{dup_key}'.")
            print(f"[ingest]       Cached at: {dup_entry.get('cached_at', 'unknown')}")
            print(f"[ingest]       Use --force to re-ingest.")
            existing_manifest = os.path.join(
                root, "catalog",
                dup_key.replace("::", os.sep),
                "manifest.json"
            )
            return True, existing_manifest

    # Step 4: Create catalog directory
    catalog_dir = build_catalog_path(root, artist, title)
    os.makedirs(catalog_dir, exist_ok=True)
    print(f"[ingest] Catalog dir: {catalog_dir}")

    # Step 5: Copy audio file
    audio_filename = os.path.basename(mp3_path)
    dest_audio = os.path.join(catalog_dir, audio_filename)
    if os.path.abspath(mp3_path) != os.path.abspath(dest_audio):
        shutil.copy2(mp3_path, dest_audio)
        print(f"[ingest] Copied audio: {audio_filename}")
    else:
        print(f"[ingest] Audio already in place: {audio_filename}")

    # Step 6: Write manifest
    manifest = create_manifest(mp3_path, artist, title, genre,
                               catalog_dir, source_hash)
    manifest_path = os.path.join(catalog_dir, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)
        fh.write("\n")
    print(f"[ingest] Manifest written: {manifest_path}")

    # Step 7: Update catalog cache
    cache = load_cache(cache_path)
    cache_key = f"{slugify(artist)}::{slugify(title)}"
    cache[cache_key] = make_entry(dest_audio, {
        "artist": artist,
        "title": title,
        "genre": genre,
        "pipeline_stage": "ingested",
    })
    save_cache(cache_path, cache)
    print(f"[ingest] Cache updated: {cache_key}")

    # Summary
    print(f"\n[ingest] SUCCESS: '{title}' by {artist}")
    print(f"         Genre:    {genre}")
    print(f"         Hash:     {source_hash[:16]}...")
    print(f"         Catalog:  {catalog_dir}")
    print(f"         Manifest: {manifest_path}")

    return True, manifest_path


def main():
    parser = argparse.ArgumentParser(
        description="Ingest an MP3 into the Make Videos pipeline (Step 1)."
    )
    parser.add_argument("mp3_path", help="Path to the source MP3 file")
    parser.add_argument("--artist", required=True, help="Artist name")
    parser.add_argument("--title", required=True, help="Song title")
    parser.add_argument("--genre", default="pop",
                        help="Genre tag (default: pop)")
    parser.add_argument("--project-root", default=os.getcwd(),
                        help="Project root directory (default: cwd)")
    parser.add_argument("--force", action="store_true",
                        help="Re-ingest even if duplicate found in cache")
    args = parser.parse_args()

    mp3_path = resolve_path(args.mp3_path, args.project_root)

    success, manifest = ingest(
        mp3_path,
        args.artist,
        args.title,
        args.genre,
        args.project_root,
        args.force,
    )
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
