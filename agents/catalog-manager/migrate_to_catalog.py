#!/usr/bin/env python3
"""
migrate_to_catalog.py — Ridgemont Studio Catalog Migration
Reads catalog.json + artists.json and builds the catalog/ directory structure
in the target Ridgemont_Studio folder.

Usage:
  python3 migrate_to_catalog.py \
    --source "/Users/johnyork/My Drive/Ridgemont Studio/Claude Cowork/Ridgemont Catalog Manager/data" \
    --target "/Users/johnyork/Ridgemont_Studio/catalog"

Creates:
  catalog/<artist_slug>/<song_slug>/manifest.json
"""

import argparse
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime


def slugify(text):
    """Convert text to lowercase slug: spaces/special -> underscores."""
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = text.strip("_")
    return text


def load_catalog(source_dir):
    """Load catalog.json and artists.json from source directory."""
    catalog_path = os.path.join(source_dir, "catalog.json")
    artists_path = os.path.join(source_dir, "artists.json")

    if not os.path.isfile(catalog_path):
        print(f"[ERROR] catalog.json not found at: {catalog_path}")
        sys.exit(1)

    with open(catalog_path, "r") as f:
        catalog = json.load(f)

    artist_lookup = {}
    if os.path.isfile(artists_path):
        with open(artists_path, "r") as f:
            artists_data = json.load(f)
        artist_list = artists_data.get("artists", artists_data) if isinstance(artists_data, dict) else artists_data
        if isinstance(artist_list, list):
            for a in artist_list:
                if isinstance(a, dict):
                    bid = a.get("band_id", "")
                    artist_lookup[bid] = {
                        "name": a.get("name", ""),
                        "type": a.get("type", ""),
                        "publishers": a.get("publishers", []),
                    }

    return catalog.get("songs", []), artist_lookup


def resolve_artist_slug(act_id):
    """Map act_id to a filesystem-safe artist slug."""
    return slugify(act_id.replace("_", " "))


def build_manifest(song, artist_info):
    """Build a manifest.json dict from a catalog song entry."""
    manifest = {
        "song_id": song.get("song_id", ""),
        "title": song.get("title", ""),
        "artist_id": song.get("act_id", ""),
        "artist_name": artist_info.get("name", song.get("act_id", "")),
        "genre": song.get("musical_info", {}).get("genre", ""),
        "subgenre": song.get("musical_info", {}).get("subgenre", ""),
        "bpm": song.get("musical_info", {}).get("bpm"),
        "key": song.get("musical_info", {}).get("key"),
        "time_signature": song.get("musical_info", {}).get("time_signature", "4/4"),
        "duration_seconds": song.get("musical_info", {}).get("duration_seconds"),
        "instrumental": song.get("musical_info", {}).get("instrumental", False),
        "moods": song.get("sync_metadata", {}).get("moods", []),
        "themes": song.get("sync_metadata", {}).get("themes", []),
        "keywords": song.get("sync_metadata", {}).get("keywords", []),
        "explicit": song.get("sync_metadata", {}).get("explicit", False),
        "one_stop": song.get("sync_metadata", {}).get("one_stop", True),
        "status": song.get("status", ""),
        "legacy_code": song.get("legacy_code", ""),
        "dates": song.get("dates", {}),
        "registration": song.get("registration", {}),
        "rights": song.get("rights", {}),
        "links": song.get("links", {}),
        "audio_file": None,  # Populated when audio is added
        "analyzed": False,   # Set True after analyze_catalog.py runs
        "migrated_at": datetime.now().isoformat(),
    }
    return manifest


def migrate(source_dir, target_dir, dry_run=False):
    """Run the full migration."""
    songs, artist_lookup = load_catalog(source_dir)

    print(f"{'=' * 60}")
    print(f"  RIDGEMONT STUDIO — CATALOG MIGRATION")
    print(f"{'=' * 60}")
    print(f"  Source:  {source_dir}")
    print(f"  Target:  {target_dir}")
    print(f"  Songs:   {len(songs)}")
    print(f"  Mode:    {'DRY RUN' if dry_run else 'LIVE'}")
    print(f"{'=' * 60}\n")

    if not dry_run:
        os.makedirs(target_dir, exist_ok=True)

    # Track slug usage for deduplication
    slug_counter = Counter()
    created = 0
    skipped = 0
    errors = 0
    with_audio = 0

    # Stats by artist
    artist_stats = Counter()

    for song in songs:
        act_id = song.get("act_id", "UNKNOWN")
        title = song.get("title", "untitled")
        artist_slug = resolve_artist_slug(act_id)
        song_slug = slugify(title)

        # Deduplicate: if same artist/song slug seen before, append _v2, _v3, etc.
        combo_key = f"{artist_slug}/{song_slug}"
        slug_counter[combo_key] += 1
        count = slug_counter[combo_key]
        if count > 1:
            song_slug = f"{song_slug}_v{count}"

        song_dir = os.path.join(target_dir, artist_slug, song_slug)
        artist_info = artist_lookup.get(act_id, {"name": act_id})

        # Check for R2 audio link
        r2_path = song.get("links", {}).get("r2_path", "")
        has_audio = bool(r2_path)
        if has_audio:
            with_audio += 1

        if dry_run:
            marker = " [AUDIO]" if has_audio else ""
            print(f"  [DRY] {artist_slug}/{song_slug}/{marker}")
            artist_stats[artist_slug] += 1
            created += 1
            continue

        # Create directory
        try:
            os.makedirs(song_dir, exist_ok=True)

            # Build and write manifest
            manifest = build_manifest(song, artist_info)
            manifest_path = os.path.join(song_dir, "manifest.json")

            # Don't overwrite existing manifest (preserves analysis data)
            if os.path.isfile(manifest_path):
                print(f"  [SKIP] {artist_slug}/{song_slug} (manifest exists)")
                skipped += 1
            else:
                with open(manifest_path, "w") as f:
                    json.dump(manifest, f, indent=2, default=str)
                marker = " [AUDIO: " + r2_path + "]" if has_audio else ""
                print(f"  [OK]   {artist_slug}/{song_slug}{marker}")
                created += 1

            artist_stats[artist_slug] += 1

        except Exception as e:
            print(f"  [FAIL] {artist_slug}/{song_slug}: {e}")
            errors += 1

    # Summary
    print(f"\n{'=' * 60}")
    print(f"  MIGRATION SUMMARY")
    print(f"{'=' * 60}")
    print(f"  Created:    {created}")
    print(f"  Skipped:    {skipped} (already existed)")
    print(f"  Errors:     {errors}")
    print(f"  With Audio: {with_audio} (R2 links)")
    print(f"\n  By Artist:")
    for artist, count in sorted(artist_stats.items()):
        print(f"    {artist}: {count} songs")
    print(f"{'=' * 60}")

    if errors > 0:
        return 1
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Migrate Ridgemont catalog metadata into catalog/ directory structure"
    )
    parser.add_argument(
        "--source",
        default="/Users/johnyork/My Drive/Ridgemont Studio/Claude Cowork/Ridgemont Catalog Manager/data",
        help="Path to data/ directory containing catalog.json and artists.json",
    )
    parser.add_argument(
        "--target",
        default="/Users/johnyork/Ridgemont_Studio/catalog",
        help="Path to target catalog/ directory in Ridgemont_Studio",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview migration without creating files",
    )
    args = parser.parse_args()
    sys.exit(migrate(args.source, args.target, args.dry_run))


if __name__ == "__main__":
    main()
