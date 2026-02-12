#!/usr/bin/env python3
"""cache_utils.py - Atomic catalog cache for the Make Videos pipeline.

Provides thread-safe, corruption-resistant read/write of the catalog
cache via a .tmp-then-rename pattern. Also exposes SHA256 hashing
for MP3 idempotency checks.

Usage (library):  from cache_utils import load_cache, save_cache, file_hash, is_stale
Usage (CLI):      python cache_utils.py <cache_path>
"""
import hashlib, json, os, sys, time

CACHE_FILENAME = ".catalog_cache.json"
HASH_BLOCK_SIZE = 65536


def load_cache(cache_path):
    """Load and return the catalog cache dict. Returns {} if missing/corrupt."""
    if not os.path.isfile(cache_path):
        return {}
    try:
        with open(cache_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError) as exc:
        print(f"[cache_utils] WARNING: corrupt cache ({exc}), resetting.")
        return {}


def save_cache(cache_path, data):
    """Atomically write data dict to cache_path via .tmp + rename."""
    if not isinstance(data, dict):
        raise TypeError("cache data must be a dict")
    tmp_path = cache_path + ".tmp"
    parent = os.path.dirname(cache_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    try:
        with open(tmp_path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, sort_keys=True)
            fh.write("\n")
            fh.flush()
            os.fsync(fh.fileno())
        os.rename(tmp_path, cache_path)
    except OSError:
        if os.path.exists(tmp_path):
            try: os.remove(tmp_path)
            except OSError: pass
        raise


def file_hash(filepath):
    """Return the SHA256 hex digest of a file."""
    sha = hashlib.sha256()
    with open(filepath, "rb") as fh:
        while True:
            block = fh.read(HASH_BLOCK_SIZE)
            if not block: break
            sha.update(block)
    return sha.hexdigest()


def composite_hash(*parts):
    """SHA256 hex digest of multiple string parts concatenated."""
    sha = hashlib.sha256()
    for part in parts:
        sha.update(str(part).encode("utf-8"))
    return sha.hexdigest()


def is_stale(cache_entry, mp3_path):
    """Return True if the cache entry is stale (MP3 changed on disk)."""
    if not os.path.isfile(mp3_path):
        return True
    stored = cache_entry.get("source_hash")
    if not stored:
        return True
    return stored != file_hash(mp3_path)


def make_entry(mp3_path, analysis_data=None):
    """Create a new cache entry dict for a song."""
    entry = {
        "source_hash": file_hash(mp3_path),
        "source_path": os.path.abspath(mp3_path),
        "cached_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    if analysis_data and isinstance(analysis_data, dict):
        entry["analysis"] = analysis_data
    return entry


def resolve_path(path, project_root):
    """Resolve a path: return as-is if absolute, otherwise join to project_root."""
    if os.path.isabs(path):
        return path
    return os.path.join(project_root, path)


def get_default_cache_path(project_root=None):
    """Return the default cache file path for a project root."""
    root = project_root or os.getcwd()
    return os.path.join(root, "catalog", CACHE_FILENAME)


def main():
    if len(sys.argv) < 2:
        print(f"Usage: python {os.path.basename(__file__)} <cache_path>")
        sys.exit(1)
    cache_path = sys.argv[1]
    if not os.path.isfile(cache_path):
        print(f"Cache file not found: {cache_path}")
        sys.exit(1)
    data = load_cache(cache_path)
    print(json.dumps(data, indent=2))
    print(f"\n--- {len(data)} entries ---")


if __name__ == "__main__":
    main()
