#!/usr/bin/env python3
"""
Hash-Based Idempotency Module — Ridgemont Studio
Prevents re-rendering unchanged content using SHA256 signatures.

Signature = SHA256(audio_bytes + artist_profile_JSON + manifest_JSON)

Usage:
    from render_signature import should_render, save_render_signature
    if should_render(audio, profile, manifest, output_dir) or args.force:
        # render...
        save_render_signature(audio, profile, manifest, output_dir)
"""

import hashlib
import json
import os
import logging

logger = logging.getLogger(__name__)

EXPECTED_OUTPUTS = [
    "full_video.mp4",
    "short_916.mp4",
    "tiktok.mp4",
    "reel_4x5.mp4",
    "lyric_video.mp4",
    "visualizer.mp4",
    "sync_reel.mp4"
]


def compute_render_signature(song_audio_path, artist_profile_path, manifest_entry):
    """Compute SHA256 hash of all render inputs."""
    hasher = hashlib.sha256()
    with open(song_audio_path, 'rb') as f:
        hasher.update(f.read())
    if os.path.exists(artist_profile_path):
        with open(artist_profile_path, 'rb') as f:
            hasher.update(f.read())
    hasher.update(json.dumps(manifest_entry, sort_keys=True).encode())
    return hasher.hexdigest()[:16]


def should_render(song_audio_path, artist_profile_path, manifest_entry, output_dir):
    """
    Check if rendering is needed by comparing hash signatures.
    Returns True if render needed, False if skip.
    """
    sig_path = os.path.join(output_dir, "render_signature.txt")
    current_sig = compute_render_signature(song_audio_path, artist_profile_path, manifest_entry)

    if not os.path.exists(sig_path):
        logger.info(f"No existing signature — render needed")
        return True

    with open(sig_path, 'r') as f:
        stored_sig = f.read().strip()

    if current_sig != stored_sig:
        logger.info(f"Signature mismatch (stored={stored_sig}, current={current_sig}) — re-render")
        return True

    # Check all 7 output files exist
    for fname in EXPECTED_OUTPUTS:
        if not os.path.exists(os.path.join(output_dir, fname)):
            logger.info(f"Missing output file: {fname} — render needed")
            return True

    logger.info(f"Hash match + all outputs exist — SKIP render")
    return False


def save_render_signature(song_audio_path, artist_profile_path, manifest_entry, output_dir):
    """Save render signature after successful render."""
    os.makedirs(output_dir, exist_ok=True)
    sig = compute_render_signature(song_audio_path, artist_profile_path, manifest_entry)
    sig_path = os.path.join(output_dir, "render_signature.txt")
    with open(sig_path, 'w') as f:
        f.write(sig)
    logger.info(f"Saved render signature: {sig}")
    return sig
