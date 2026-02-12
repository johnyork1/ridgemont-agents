#!/usr/bin/env python3
"""
Preflight Validation Module — Ridgemont Studio
Step 1.5: Verify all asset paths exist before rendering begins.

A single missing PNG will crash the batch hours into processing.
This module runs AFTER mood mapping, BEFORE passing manifest to batch_produce.py.

Usage:
    from preflight_validator import preflight_validate, preflight_batch
    missing = preflight_validate(manifest)
    if missing:
        log.error(f"PREFLIGHT_FAIL: {song} — missing: {missing}")
"""

import os
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def preflight_validate(manifest):
    """
    Verify all referenced assets exist on disk.
    Returns list of missing paths. Empty list = all clear.
    """
    paths_to_check = [
        manifest.get("weeter_pose"),
        manifest.get("blubby_pose"),
        manifest.get("together_pose"),
        manifest.get("meme_sign_template"),
        manifest.get("audio_source"),
        manifest.get("background_image"),
    ]
    missing = [p for p in paths_to_check if p and not os.path.exists(p)]
    return missing


def preflight_batch(manifests):
    """
    Run preflight on an entire batch for fail-fast behavior.
    Returns dict: { song_id: [missing_paths] } for failures only.
    Songs with no missing paths are omitted.
    """
    failures = {}
    for song_id, manifest in manifests.items():
        missing = preflight_validate(manifest)
        if missing:
            failures[song_id] = missing
            manifest["status"] = "ABORTED_PREFLIGHT"
            manifest["missing_assets"] = missing
            logger.error(f"PREFLIGHT_FAIL: {song_id} — missing: {missing}")
        else:
            manifest["status"] = "READY_FOR_ASSEMBLY"
            logger.info(f"PREFLIGHT_OK: {song_id}")
    return failures


def update_progress_preflight(progress_file, song_id, passed, missing=None):
    """Update progress log with preflight results."""
    try:
        if os.path.exists(progress_file):
            with open(progress_file, 'r') as f:
                progress_data = json.load(f)
        else:
            progress_data = {'song_id': song_id, 'stages': {}}

        progress_data['stages']['preflight'] = {
            'completed': datetime.now().isoformat(),
            'passed': passed,
            'missing_assets': missing or []
        }

        with open(progress_file, 'w') as f:
            json.dump(progress_data, f, indent=2)
    except Exception as e:
        logger.warning(f"Could not update progress log: {e}")
