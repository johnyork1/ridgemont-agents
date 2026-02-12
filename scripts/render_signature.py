#!/usr/bin/env python3
"""render_signature.py - Deterministic render signatures for the pipeline.

Generates a SHA256-based signature from the combination of:
  1. Source audio file hash
  2. Artist/song profile data
  3. Manifest analysis results

Two renders with identical inputs produce the same signature,
enabling idempotent re-renders and cache-hit detection.

Usage (library):  from render_signature import generate_signature
Usage (CLI):      python render_signature.py <audio_path> [manifest_path]
"""
import hashlib, json, os, sys

HASH_BLOCK_SIZE = 65536
SIGNATURE_PREFIX = "rv1"


def _file_sha256(filepath):
    """Return the SHA256 hex digest of a file."""
    sha = hashlib.sha256()
    with open(filepath, "rb") as fh:
        while True:
            block = fh.read(HASH_BLOCK_SIZE)
            if not block: break
            sha.update(block)
    return sha.hexdigest()


def _stable_json(data):
    """Return a deterministic JSON string for hashing."""
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def generate_signature(audio_path, manifest_data=None, profile_data=None):
    """Generate a deterministic render signature.

    Returns string in format 'rv1-<first12chars>' of the SHA256 digest.
    """
    sha = hashlib.sha256()
    audio_hash = _file_sha256(audio_path)
    sha.update(f"audio:{audio_hash}".encode("utf-8"))
    if manifest_data:
        relevant_keys = [
            "bpm", "key", "mode", "energy", "mood",
            "key_confidence", "mode_confidence",
            "duration_seconds", "beat_count",
        ]
        filtered = {k: manifest_data[k] for k in relevant_keys if k in manifest_data}
        sha.update(f"manifest:{_stable_json(filtered)}".encode("utf-8"))
    if profile_data:
        sha.update(f"profile:{_stable_json(profile_data)}".encode("utf-8"))
    digest = sha.hexdigest()
    return f"{SIGNATURE_PREFIX}-{digest[:12]}"


def is_same_render(sig_a, sig_b):
    """Return True if two render signatures match."""
    return sig_a == sig_b


def load_manifest(manifest_path):
    with open(manifest_path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def main():
    if len(sys.argv) < 2:
        print(f"Usage: python {os.path.basename(__file__)} <audio_path> [manifest_path]")
        sys.exit(1)
    audio_path = sys.argv[1]
    if not os.path.isfile(audio_path):
        print(f"Audio file not found: {audio_path}")
        sys.exit(1)
    manifest_data = None
    if len(sys.argv) >= 3:
        mpath = sys.argv[2]
        if os.path.isfile(mpath):
            manifest_data = load_manifest(mpath)
        else:
            print(f"Manifest not found: {mpath}")
            sys.exit(1)
    sig = generate_signature(audio_path, manifest_data)
    print(f"Render Signature: {sig}")
    print(f"Audio:            {audio_path}")
    if manifest_data:
        print(f"Mood:             {manifest_data.get('mood', 'N/A')}")
        print(f"BPM:              {manifest_data.get('bpm', 'N/A')}")


if __name__ == "__main__":
    main()
