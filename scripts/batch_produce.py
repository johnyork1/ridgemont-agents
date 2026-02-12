#!/usr/bin/env python3
"""batch_produce.py - Step 4 of the Make Videos pipeline.

Orchestrates the full production pipeline for multiple songs:
  1. Scans an input directory for audio files (MP3/WAV/FLAC)
  2. For each file: ingest -> analyze -> render master -> short cuts
  3. Uses render_signature to skip songs that haven't changed
  4. Generates a CSV Production Log of all results

Usage:
    python batch_produce.py --input-dir ../ingestion/
    python batch_produce.py --input-dir ../ingestion/ --limit 3
    python batch_produce.py --input-dir ../ingestion/ --genre reggae --force
"""
import argparse
import csv
import json
import os
import re
import sys
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
PROJECT_ROOT_DEFAULT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
PIP_PKG_DIR = os.path.join(PROJECT_ROOT_DEFAULT, ".pip_packages")
if os.path.isdir(PIP_PKG_DIR):
    sys.path.insert(0, PIP_PKG_DIR)

from cache_utils import load_cache, get_default_cache_path
from render_signature import generate_signature

# Lazy-import pipeline scripts to avoid heavy librosa load on --help
_ingest_mod = None
_analyze_mod = None
_master_mod = None
_cuts_mod = None


def _get_ingest():
    global _ingest_mod
    if not _ingest_mod:
        import importlib.util
        spec = importlib.util.spec_from_file_location("ingest_song", os.path.join(SCRIPT_DIR, "ingest_song.py"))
        _ingest_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_ingest_mod)
    return _ingest_mod


def _get_analyze():
    global _analyze_mod
    if not _analyze_mod:
        import importlib.util
        spec = importlib.util.spec_from_file_location("analyze_catalog", os.path.join(SCRIPT_DIR, "analyze_catalog.py"))
        _analyze_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_analyze_mod)
    return _analyze_mod


def _get_master():
    global _master_mod
    if not _master_mod:
        import importlib.util
        spec = importlib.util.spec_from_file_location("baseline_master", os.path.join(SCRIPT_DIR, "baseline_master.py"))
        _master_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_master_mod)
    return _master_mod


def _get_cuts():
    global _cuts_mod
    if not _cuts_mod:
        path = os.path.join(SCRIPT_DIR, "beat_sync_cuts.py")
        if os.path.isfile(path):
            import importlib.util
            spec = importlib.util.spec_from_file_location("beat_sync_cuts", path)
            _cuts_mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(_cuts_mod)
    return _cuts_mod


# ── File Discovery ───────────────────────────────────────────

AUDIO_EXTS = {".mp3", ".wav", ".flac", ".m4a", ".ogg"}

def discover_audio_files(input_dir):
    """Find all audio files in the input directory (non-recursive)."""
    if not os.path.isdir(input_dir):
        print(f"[batch] ERROR: Input directory not found: {input_dir}")
        return []
    files = []
    for fname in sorted(os.listdir(input_dir)):
        ext = os.path.splitext(fname)[1].lower()
        if ext in AUDIO_EXTS:
            files.append(os.path.join(input_dir, fname))
    return files


def parse_filename(filepath):
    """Extract artist, title, and genre from filename.

    Expected formats:
        'Title (Genre).mp3'          -> artist=Unknown, title=Title, genre=Genre
        'Artist - Title (Genre).mp3' -> artist=Artist, title=Title, genre=Genre
        'Title.mp3'                  -> artist=Unknown, title=Title, genre=pop
    """
    basename = os.path.splitext(os.path.basename(filepath))[0]

    # Extract genre from parentheses
    genre_match = re.search(r'\(([^)]+)\)', basename)
    genre = genre_match.group(1).lower().strip() if genre_match else "pop"
    name_part = re.sub(r'\s*\([^)]+\)\s*', '', basename).strip()

    # Split on ' - ' for artist/title
    if ' - ' in name_part:
        parts = name_part.split(' - ', 1)
        artist = parts[0].strip()
        title = parts[1].strip()
    else:
        artist = "The Ridgemonts"
        title = name_part.strip()

    return artist, title, genre


# ── Deduplication ────────────────────────────────────────────

def should_skip(audio_path, manifest_path, project_root):
    """Check if a song can be skipped (already rendered, unchanged).

    Returns:
        tuple (skip: bool, reason: str)
    """
    if not os.path.isfile(manifest_path):
        return False, "no manifest"

    with open(manifest_path, "r", encoding="utf-8") as fh:
        manifest = json.load(fh)

    stage = manifest.get("pipeline_stage", "")
    if stage != "rendered":
        return False, f"stage={stage}, not rendered"

    old_sig = manifest.get("render_signature")
    if not old_sig:
        return False, "no render signature"

    new_sig = generate_signature(audio_path, manifest_path)
    if old_sig == new_sig:
        return True, f"signature match ({old_sig})"
    return False, f"signature mismatch ({old_sig} vs {new_sig})"


# ── Single Song Pipeline ─────────────────────────────────────

def process_song(audio_path, artist, title, genre, project_root, force=False):
    """Run the full pipeline for a single song: ingest -> analyze -> render -> cuts.

    Returns:
        dict with status, timings, and output info
    """
    result = {
        "audio_file": os.path.basename(audio_path),
        "artist": artist,
        "title": title,
        "genre": genre,
        "status": "pending",
        "ingest_ok": False,
        "analyze_ok": False,
        "render_ok": False,
        "cuts_ok": False,
        "skipped": False,
        "skip_reason": "",
        "bpm": "",
        "key": "",
        "mood": "",
        "render_time": "",
        "output_path": "",
        "short_path": "",
        "error": "",
        "total_time": "",
    }

    start = time.time()
    slugify = _get_ingest().slugify
    artist_slug = slugify(artist)
    title_slug = slugify(title)
    catalog_dir = os.path.join(project_root, "catalog", artist_slug, title_slug)
    manifest_path = os.path.join(catalog_dir, "manifest.json")

    # ── Dedup check ──
    if not force:
        skip, reason = should_skip(audio_path, manifest_path, project_root)
        if skip:
            result["status"] = "skipped"
            result["skipped"] = True
            result["skip_reason"] = reason
            result["total_time"] = round(time.time() - start, 2)
            print(f"[batch] SKIP: \"{title}\" by {artist} ({reason})")
            return result

    # ── Step 1: Ingest ──
    try:
        ingest = _get_ingest()
        ok, mpath = ingest.ingest(audio_path, artist, title, genre, project_root, force=True)
        result["ingest_ok"] = ok
        if not ok:
            result["status"] = "failed"
            result["error"] = "ingest failed"
            result["total_time"] = round(time.time() - start, 2)
            return result
    except Exception as exc:
        result["status"] = "failed"
        result["error"] = f"ingest exception: {exc}"
        result["total_time"] = round(time.time() - start, 2)
        return result

    # ── Step 2: Analyze ──
    try:
        analyze = _get_analyze()
        analysis_result = analyze.analyze_song(title_slug, artist_slug, project_root)
        result["analyze_ok"] = analysis_result is not None
        if not analysis_result:
            result["status"] = "failed"
            result["error"] = "analysis failed"
            result["total_time"] = round(time.time() - start, 2)
            return result
        result["bpm"] = analysis_result["analysis"]["bpm"]
        result["key"] = analysis_result["analysis"].get("key_full", "")
        result["mood"] = analysis_result["mood"]["name"]
    except Exception as exc:
        result["status"] = "failed"
        result["error"] = f"analyze exception: {exc}"
        result["total_time"] = round(time.time() - start, 2)
        return result

    # ── Step 3: Render Master ──
    try:
        master = _get_master()
        render_result = master.render_song(title_slug, artist_slug, project_root)
        result["render_ok"] = render_result is not None
        if not render_result:
            result["status"] = "failed"
            result["error"] = "render failed"
            result["total_time"] = round(time.time() - start, 2)
            return result
        result["render_time"] = render_result["render_time"]
        result["output_path"] = render_result["output_path"]
    except Exception as exc:
        result["status"] = "failed"
        result["error"] = f"render exception: {exc}"
        result["total_time"] = round(time.time() - start, 2)
        return result

    # ── Step 4: Beat-Sync Short Cuts (optional) ──
    try:
        cuts = _get_cuts()
        if cuts:
            short_result = cuts.create_short(title_slug, artist_slug, project_root)
            result["cuts_ok"] = short_result is not None
            if short_result:
                result["short_path"] = short_result.get("output_path", "")
        else:
            result["cuts_ok"] = False
    except Exception as exc:
        print(f"[batch] WARNING: Short cuts failed for {title}: {exc}")
        result["cuts_ok"] = False

    result["status"] = "success"
    result["total_time"] = round(time.time() - start, 2)
    return result


# ── CSV Production Log ───────────────────────────────────────

CSV_HEADERS = [
    "audio_file", "artist", "title", "genre", "status",
    "skipped", "skip_reason", "bpm", "key", "mood",
    "ingest_ok", "analyze_ok", "render_ok", "cuts_ok",
    "render_time", "total_time", "output_path", "short_path", "error"
]

def write_production_log(results, project_root):
    """Write the Production Log CSV to the project root."""
    log_path = os.path.join(project_root, "output", "production_log.csv")
    with open(log_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_HEADERS, extrasaction="ignore")
        writer.writeheader()
        for r in results:
            writer.writerow(r)
    print(f"\n[batch] Production log: {log_path} ({len(results)} entries)")
    return log_path


# ── Batch Summary ────────────────────────────────────────────

def print_summary(results, batch_start):
    """Print a formatted summary table."""
    total = len(results)
    ok = sum(1 for r in results if r["status"] == "success")
    skipped = sum(1 for r in results if r["status"] == "skipped")
    failed = sum(1 for r in results if r["status"] == "failed")
    elapsed = round(time.time() - batch_start, 2)

    print(f"\n{'='*70}")
    print(f"[batch] BATCH PRODUCTION SUMMARY")
    print(f"{'='*70}")
    print(f"  Total:    {total}")
    print(f"  Success:  {ok}")
    print(f"  Skipped:  {skipped}")
    print(f"  Failed:   {failed}")
    print(f"  Elapsed:  {elapsed}s")
    print(f"{'='*70}")

    for r in results:
        status_icon = {"success": "OK", "skipped": "SKIP", "failed": "FAIL"}.get(r["status"], "?")
        line = f"  [{status_icon:4s}] {r['title']:20s} by {r['artist']:20s}"
        if r["status"] == "success":
            line += f"  BPM={r['bpm']}  mood={r['mood']}  render={r['render_time']}s"
        elif r["status"] == "skipped":
            line += f"  ({r['skip_reason']})"
        elif r["status"] == "failed":
            line += f"  ERROR: {r['error'][:40]}"
        print(line)

    print(f"{'='*70}\n")
    return {"total": total, "success": ok, "skipped": skipped, "failed": failed, "elapsed": elapsed}


# ── Main Orchestrator ────────────────────────────────────────

def batch_produce(input_dir, project_root=None, genre_override=None,
                  limit=None, force=False):
    """Run the full batch production pipeline.

    Args:
        input_dir: Directory containing audio files
        project_root: Project root (default: parent of scripts/)
        genre_override: Override genre for all songs
        limit: Max number of songs to process
        force: Skip dedup checks, re-render everything

    Returns:
        list of result dicts
    """
    root = project_root or PROJECT_ROOT_DEFAULT
    batch_start = time.time()

    print(f"\n{'='*70}")
    print(f"[batch] BATCH PRODUCTION START")
    print(f"[batch] Input:  {input_dir}")
    print(f"[batch] Root:   {root}")
    print(f"[batch] Force:  {force}")
    if limit:
        print(f"[batch] Limit:  {limit}")
    print(f"{'='*70}\n")

    # Discover files
    audio_files = discover_audio_files(input_dir)
    if not audio_files:
        print("[batch] No audio files found.")
        return []

    if limit:
        audio_files = audio_files[:limit]

    print(f"[batch] Found {len(audio_files)} audio file(s) to process.\n")

    results = []
    for i, audio_path in enumerate(audio_files, 1):
        artist, title, genre = parse_filename(audio_path)
        if genre_override:
            genre = genre_override

        print(f"\n{'─'*70}")
        print(f"[batch] [{i}/{len(audio_files)}] \"{title}\" by {artist} ({genre})")
        print(f"{'─'*70}")

        result = process_song(audio_path, artist, title, genre, root, force)
        results.append(result)

    # Write production log
    log_path = write_production_log(results, root)

    # Print summary
    summary = print_summary(results, batch_start)

    return results


# ── CLI ──────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Batch production pipeline (Step 4 of Make Videos)."
    )
    parser.add_argument("--input-dir", required=True,
                        help="Directory containing audio files")
    parser.add_argument("--project-root", default=None,
                        help="Project root (default: parent of scripts/)")
    parser.add_argument("--genre", default=None,
                        help="Override genre for all songs")
    parser.add_argument("--limit", type=int, default=None,
                        help="Max number of songs to process")
    parser.add_argument("--force", action="store_true",
                        help="Skip dedup, re-render everything")
    args = parser.parse_args()

    root = args.project_root or PROJECT_ROOT_DEFAULT
    results = batch_produce(
        args.input_dir, root, args.genre, args.limit, args.force
    )

    # Exit code: 0 if all succeed/skip, 1 if any failed
    if any(r["status"] == "failed" for r in results):
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
