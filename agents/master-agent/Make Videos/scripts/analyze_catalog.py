#!/usr/bin/env python3
"""
analyze_catalog.py — Ridgemont Studio Make Videos Pipeline
Step 2: Audio Analysis + Mood Mapping + Manifest Generation

Analyzes audio files using librosa for BPM, beats, key estimation (with confidence),
energy level, and duration. Maps results to Weeter & Blubby poses via mood_map.json.
Writes project-root-relative paths to song manifest. Runs preflight validation.

Usage:
    python analyze_catalog.py --song-id "song_001" --audio "catalog/artist/song/audio.wav" \
        --artist "DJ Chromosphere" --genre "Electronic" \
        --project-root "/path/to/ridgemont"

Pipeline Position: Step 2 (after Ingestion, before Creation)
"""

import argparse
import json
import os
import sys
import logging
from datetime import datetime

import librosa
import numpy as np

# Local shared modules
from preflight_validator import preflight_validate, update_progress_preflight
from cache_utils import load_cache, save_cache, cache_update_analysis

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Key name mapping (chroma index → note name)
KEY_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']


def analyze_song(audio_path):
    """
    Full audio analysis with confidence scoring.
    Returns dict with BPM, beats, key, confidence, energy, duration.
    
    SAFETY VALVE: If key_confidence < 0.15 or mode_confidence < 0.10,
    analysis_reliable = False → mood mapping must fall back to genre defaults.
    BPM and beat timestamps are ALWAYS reliable regardless.
    """
    logger.info(f"Loading audio: {audio_path}")
    y, sr = librosa.load(audio_path)

    # BPM and beat tracking (always reliable)
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)

    # Onset detection
    onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
    onset_times = librosa.frames_to_time(onset_frames, sr=sr)

    # Chroma analysis for key estimation
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    key_strengths = chroma.mean(axis=1)
    estimated_key = int(key_strengths.argmax())

    # Energy (RMS)
    rms = librosa.feature.rms(y=y)[0].mean()

    # KEY CONFIDENCE SCORING
    sorted_strengths = np.sort(key_strengths)[::-1]
    key_confidence = float((sorted_strengths[0] - sorted_strengths[1]) / sorted_strengths[0])

    # MAJOR/MINOR ESTIMATION
    major_third = key_strengths[(estimated_key + 4) % 12]
    minor_third = key_strengths[(estimated_key + 3) % 12]
    is_major = bool(major_third > minor_third)
    mode_confidence = float(abs(major_third - minor_third) / max(major_third, minor_third))

    # Handle numpy types for JSON serialization
    bpm_value = float(tempo) if not isinstance(tempo, np.ndarray) else float(tempo[0])

    return {
        "bpm": bpm_value,
        "beat_times": beat_times.tolist(),
        "beat_count": len(beat_times),
        "onset_times": onset_times.tolist(),
        "estimated_key": estimated_key,
        "key_name": KEY_NAMES[estimated_key],
        "is_major_key": is_major,
        "mode": "major" if is_major else "minor",
        "key_confidence": round(key_confidence, 4),
        "mode_confidence": round(mode_confidence, 4),
        "energy_level": float(rms),
        "energy_category": categorize_energy(float(rms)),
        "duration": float(librosa.get_duration(y=y, sr=sr)),
        "analysis_reliable": key_confidence > 0.15 and mode_confidence > 0.10
    }


def categorize_energy(rms):
    """Classify energy level for mood mapping."""
    if rms > 0.15:
        return "high"
    elif rms > 0.08:
        return "medium"
    else:
        return "low"


def load_mood_map(mood_map_path):
    """Load mood_map.json for pose selection."""
    with open(mood_map_path, 'r') as f:
        return json.load(f)


def select_mood_and_poses(analysis, mood_map, genre=None):
    """
    Select W&B poses based on audio analysis and mood_map.json rules.
    Returns mood name and pose paths (project-root-relative).
    
    If analysis_reliable is False, returns None — caller must use genre defaults.
    """
    if not analysis["analysis_reliable"]:
        logger.warning("Low confidence analysis — skipping mood mapping, use genre defaults")
        return None, None, None, None

    bpm = analysis["bpm"]
    is_major = analysis["is_major_key"]
    energy = analysis["energy_category"]

    # Evaluate rules in order (first match wins)
    for rule in mood_map.get("rules", []):
        condition = rule["condition"]
        if evaluate_condition(condition, bpm, is_major, energy, genre):
            logger.info(f"Mood matched: {rule['mood']} (condition: {condition})")
            return (
                rule["mood"],
                rule.get("weeter_pose"),
                rule.get("blubby_pose"),
                rule.get("together_pose")
            )

    # Fall through to default
    default = mood_map.get("default", {})
    logger.info(f"Using default mood: {default.get('mood', 'neutral')}")
    return (
        default.get("mood", "neutral"),
        default.get("weeter_pose"),
        default.get("blubby_pose"),
        default.get("together_pose")
    )


def evaluate_condition(condition, bpm, is_major, energy, genre):
    """
    Evaluate a mood_map condition string.
    Supports: bpm comparisons, major_key, minor_key, energy_high, genre checks.
    """
    parts = [p.strip() for p in condition.replace(" AND ", " AND ").replace(" OR ", " OR ").split(" AND ")]

    for part in parts:
        part = part.strip()

        if part == "major_key":
            if not is_major:
                return False
        elif part == "minor_key":
            if is_major:
                return False
        elif part.startswith("bpm >"):
            threshold = float(part.split(">")[1].strip())
            if bpm <= threshold:
                return False
        elif part.startswith("bpm <"):
            threshold = float(part.split("<")[1].strip())
            if bpm >= threshold:
                return False
        elif part.startswith("bpm "):
            # Range: "bpm 90-120"
            try:
                range_str = part.replace("bpm ", "").strip()
                low, high = range_str.split("-")
                if not (float(low) <= bpm <= float(high)):
                    return False
            except (ValueError, IndexError):
                return False
        elif part == "energy_high":
            if energy != "high":
                return False
        elif part.startswith("genre =="):
            # genre == 'jazz' OR genre == 'classical'
            if " OR " in part:
                or_parts = part.split(" OR ")
                matched = False
                for op in or_parts:
                    g = op.split("'")[1] if "'" in op else ""
                    if genre and genre.lower() == g.lower():
                        matched = True
                        break
                if not matched:
                    return False
            else:
                g = part.split("'")[1] if "'" in part else ""
                if not genre or genre.lower() != g.lower():
                    return False

    return True


def load_creative_brief(song_dir):
    """Check for creative_brief.json (highest priority override)."""
    brief_path = os.path.join(song_dir, "creative_brief.json")
    if os.path.exists(brief_path):
        with open(brief_path, 'r') as f:
            return json.load(f)
    return None


def load_artist_profile(artist_dir):
    """Load artist_profile.json for visual identity overrides."""
    profile_path = os.path.join(artist_dir, "artist_profile.json")
    if os.path.exists(profile_path):
        with open(profile_path, 'r') as f:
            return json.load(f)
    return None


def apply_priority_chain(creative_brief, artist_profile, mood_result, genre_defaults):
    """
    Apply the priority chain for visual decisions:
    1. Creative Brief (highest)
    2. Artist Profile
    3. Mood Map (if analysis reliable)
    4. Genre Defaults
    5. System Default (happy/thumbs_up)
    """
    result = {
        "weeter_pose": "assets/characters/weeter/happy/thumbs_up.png",
        "blubby_pose": "assets/characters/blubby/happy/excited_stars.png",
        "together_pose": "assets/characters/together/happy/thumbs_up_duo.png",
        "meme_sign_template": "assets/characters/together/meme_sign/blank_sign.png"
    }

    # Layer 4: Genre defaults
    if genre_defaults:
        for key in result:
            if key in genre_defaults:
                result[key] = genre_defaults[key]

    # Layer 3: Mood map
    if mood_result and mood_result[0]:
        _, w_pose, b_pose, t_pose = mood_result
        if w_pose:
            result["weeter_pose"] = w_pose
        if b_pose:
            result["blubby_pose"] = b_pose
        if t_pose:
            result["together_pose"] = t_pose

    # Layer 2: Artist profile
    if artist_profile:
        wb = artist_profile.get("weeter_blubby_override", {})
        for key in ["weeter_pose", "blubby_pose", "together_pose"]:
            if key in wb:
                result[key] = wb[key]

    # Layer 1: Creative brief (highest priority)
    if creative_brief:
        wb = creative_brief.get("character_override", {})
        for key in ["weeter_pose", "blubby_pose", "together_pose"]:
            if key in wb:
                result[key] = wb[key]

    return result


def build_manifest(song_id, artist_name, genre, audio_path, analysis,
                   poses, mood_name, project_root):
    """Build the complete song manifest with project-root-relative paths."""
    manifest = {
        "song_id": song_id,
        "artist": artist_name,
        "genre": genre,
        "audio_source": audio_path,
        "bpm": analysis["bpm"],
        "beats": {
            "beat_times": analysis["beat_times"],
            "beat_count": analysis["beat_count"],
            "onset_times": analysis["onset_times"]
        },
        "key": {
            "estimated_key": analysis["estimated_key"],
            "key_name": analysis["key_name"],
            "is_major": analysis["is_major_key"],
            "mode": analysis["mode"],
            "key_confidence": analysis["key_confidence"],
            "mode_confidence": analysis["mode_confidence"]
        },
        "energy": {
            "level": analysis["energy_level"],
            "category": analysis["energy_category"]
        },
        "duration": analysis["duration"],
        "analysis_reliable": analysis["analysis_reliable"],
        "mood_estimate": {
            "predicted_mood": mood_name or "genre_default",
            "source": "mood_map" if mood_name else "genre_default"
        },
        # Project-root-relative paths — batch_produce.py reads as-is
        "weeter_pose": poses["weeter_pose"],
        "blubby_pose": poses["blubby_pose"],
        "together_pose": poses["together_pose"],
        "meme_sign_template": poses["meme_sign_template"],
        "pipeline": {
            "analyzed_at": datetime.now().isoformat(),
            "analyzer_version": "3.0",
            "status": "pending_preflight"
        }
    }
    return manifest


def main():
    parser = argparse.ArgumentParser(description="Analyze song and generate manifest")
    parser.add_argument("--song-id", required=True, help="Unique song identifier")
    parser.add_argument("--audio", required=True, help="Path to audio file (project-root-relative)")
    parser.add_argument("--artist", required=True, help="Artist name")
    parser.add_argument("--genre", default="Pop", help="Primary genre")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--output-dir", help="Override manifest output directory")
    args = parser.parse_args()

    project_root = os.path.abspath(args.project_root)
    audio_full_path = os.path.join(project_root, args.audio)

    if not os.path.exists(audio_full_path):
        logger.error(f"Audio file not found: {audio_full_path}")
        sys.exit(1)

    # Step 2a: Audio analysis
    logger.info(f"=== Analyzing: {args.song_id} by {args.artist} ===")
    analysis = analyze_song(audio_full_path)
    logger.info(f"BPM: {analysis['bpm']:.1f} | Key: {analysis['key_name']} {analysis['mode']} | "
                f"Energy: {analysis['energy_category']} | Reliable: {analysis['analysis_reliable']}")

    # Step 2b: Load mood map
    mood_map_path = os.path.join(project_root, "data", "mood_map.json")
    if os.path.exists(mood_map_path):
        mood_map = load_mood_map(mood_map_path)
    else:
        logger.warning("mood_map.json not found — using defaults")
        mood_map = {"rules": [], "default": {
            "mood": "neutral",
            "weeter_pose": "assets/characters/weeter/happy/thumbs_up.png",
            "blubby_pose": "assets/characters/blubby/happy/excited_stars.png",
            "together_pose": "assets/characters/together/happy/thumbs_up_duo.png"
        }}

    # Step 2c: Select mood and poses
    mood_result = select_mood_and_poses(analysis, mood_map, args.genre)

    # Step 2d: Load higher-priority overrides
    artist_dir = os.path.join(project_root, "catalog", args.artist)
    song_dir = os.path.join(artist_dir, args.song_id) if args.output_dir is None else args.output_dir
    creative_brief = load_creative_brief(song_dir)
    artist_profile = load_artist_profile(artist_dir)

    # Step 2e: Apply priority chain
    poses = apply_priority_chain(creative_brief, artist_profile, mood_result, None)

    mood_name = mood_result[0] if mood_result and mood_result[0] else "genre_default"

    # Step 2f: Build manifest
    manifest = build_manifest(
        args.song_id, args.artist, args.genre, args.audio,
        analysis, poses, mood_name, project_root
    )

    # Step 1.5: Preflight validation
    logger.info("Running preflight validation...")
    # Resolve paths against project root for existence check
    preflight_manifest = {}
    for key in ["weeter_pose", "blubby_pose", "together_pose", "meme_sign_template"]:
        full_path = os.path.join(project_root, manifest[key])
        preflight_manifest[key] = full_path
    preflight_manifest["audio_source"] = audio_full_path

    missing = preflight_validate(preflight_manifest)
    if missing:
        manifest["pipeline"]["status"] = "ABORTED_PREFLIGHT"
        manifest["pipeline"]["missing_assets"] = missing
        logger.error(f"PREFLIGHT_FAIL: {args.song_id} — missing: {missing}")
    else:
        manifest["pipeline"]["status"] = "READY_FOR_ASSEMBLY"
        logger.info("Preflight passed — all assets verified")

    # Save manifest
    manifest_dir = args.output_dir or os.path.join(project_root, "catalog", args.artist, args.song_id)
    os.makedirs(manifest_dir, exist_ok=True)
    manifest_path = os.path.join(manifest_dir, "manifest.json")
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    logger.info(f"Manifest saved: {manifest_path}")

    # Update catalog cache
    try:
        cache = load_cache()
        cache_update_analysis(cache, args.artist, args.song_id, analysis)
        save_cache(cache)
        logger.info(f"Catalog cache updated for {args.song_id}")
    except Exception as e:
        logger.warning(f"Could not update catalog cache: {e}")

    # Update progress log
    try:
        progress_file = os.path.join(manifest_dir, 'progress_log.json')
        if os.path.exists(progress_file):
            with open(progress_file, 'r') as f:
                progress_data = json.load(f)
        else:
            progress_data = {'song_id': args.song_id, 'artist': args.artist, 'stages': {}}

        progress_data['stages']['analysis'] = {
            'completed': datetime.now().isoformat(),
            'bpm': manifest['bpm'],
            'key': f"{analysis['key_name']} {analysis['mode']}",
            'mood': mood_name,
            'beat_count': analysis['beat_count'],
            'analysis_reliable': analysis['analysis_reliable'],
            'status': manifest['pipeline']['status']
        }

        with open(progress_file, 'w') as f:
            json.dump(progress_data, f, indent=2)
        logger.info(f"Updated progress log: {progress_file}")
    except Exception as e:
        logger.warning(f"Could not update progress log: {e}")

    # Report
    if manifest["pipeline"]["status"] == "ABORTED_PREFLIGHT":
        logger.error(f"Song {args.song_id} ABORTED — fix missing assets and re-run")
        sys.exit(2)
    else:
        logger.info(f"Song {args.song_id} ready for assembly (mood: {mood_name})")


if __name__ == "__main__":
    main()
