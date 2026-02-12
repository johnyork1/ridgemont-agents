#!/usr/bin/env python3
"""analyze_catalog.py - Step 2 of the Make Videos pipeline.

Performs audio analysis on an ingested song using librosa and numpy:
  1. Loads audio from the catalog
  2. Detects BPM and beat positions
  3. Estimates musical key with confidence scores
  4. Computes energy profile (RMS + spectral)
  5. Applies mood_map.json rules to determine mood
  6. Implements the Librosa Confidence Safety Valve
  7. Assigns character poses via mood → character_dynamics
  8. Writes analysis results to the song's manifest.json
  9. Updates the catalog cache

Usage:
    python analyze_catalog.py --song-id "crazy" --artist "the-ridgemonts"
    python analyze_catalog.py --song-id "crazy" --artist "the-ridgemonts" --project-root /path
"""
import argparse
import json
import os
import sys
import time

# Add scripts directory to path for local imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

# Add .pip_packages to path for librosa/numpy if installed there
PROJECT_ROOT_DEFAULT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
PIP_PKG_DIR = os.path.join(PROJECT_ROOT_DEFAULT, ".pip_packages")
if os.path.isdir(PIP_PKG_DIR):
    sys.path.insert(0, PIP_PKG_DIR)

# Lazy imports: numpy/librosa loaded only when analysis runs (not for --list)
np = None
librosa = None

def _ensure_audio_deps():
    """Load heavy audio dependencies on first use."""
    global np, librosa
    if np is None:
        import numpy as _np
        np = _np
    if librosa is None:
        try:
            import librosa as _librosa
            librosa = _librosa
        except ImportError:
            print("[analyze] FATAL: librosa not installed.")
            print("         Install with: pip install librosa soundfile")
            sys.exit(1)

from cache_utils import load_cache, save_cache, get_default_cache_path


# ── Krumhansl-Kessler key profiles ────────────────────────────
# Correlation weights for major and minor keys (12 pitch classes: C, C#, D, ...)
# Lazy-initialized after numpy is loaded
MAJOR_PROFILE = None
MINOR_PROFILE = None
PITCH_NAMES = ["C", "C#", "D", "D#", "E", "F",
               "F#", "G", "G#", "A", "A#", "B"]

def _init_key_profiles():
    global MAJOR_PROFILE, MINOR_PROFILE
    if MAJOR_PROFILE is None:
        MAJOR_PROFILE = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09,
                                  2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
        MINOR_PROFILE = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53,
                                  2.54, 4.75, 3.98, 2.69, 3.34, 3.17])


# ── Audio Loading ─────────────────────────────────────────────

def load_audio(audio_path, sr=22050):
    """Load audio file and return (signal, sample_rate)."""
    print(f"[analyze] Loading audio: {os.path.basename(audio_path)}")
    y, loaded_sr = librosa.load(audio_path, sr=sr, mono=True)
    duration = librosa.get_duration(y=y, sr=loaded_sr)
    print(f"[analyze] Duration: {duration:.1f}s  |  SR: {loaded_sr} Hz  |  Samples: {len(y)}")
    return y, loaded_sr, duration


# ── BPM & Beat Detection ─────────────────────────────────────

def detect_bpm_and_beats(y, sr):
    """Detect tempo (BPM) and beat frame positions.

    Returns:
        dict with bpm, beat_count, beat_times (list), beats_per_second
    """
    print("[analyze] Detecting BPM and beats...")
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)

    # librosa may return tempo as array in newer versions
    bpm = float(np.atleast_1d(tempo)[0])

    beat_times = librosa.frames_to_time(beat_frames, sr=sr).tolist()
    bps = len(beat_times) / max(librosa.get_duration(y=y, sr=sr), 0.1)

    result = {
        "bpm": round(bpm, 1),
        "beat_count": len(beat_times),
        "beat_times": [round(t, 3) for t in beat_times],
        "beats_per_second": round(bps, 2),
    }
    print(f"[analyze] BPM: {result['bpm']}  |  Beats: {result['beat_count']}  |  BPS: {result['beats_per_second']}")
    return result


# ── Key Detection (Krumhansl-Schmuckler) ─────────────────────

def detect_key(y, sr):
    """Estimate musical key using chroma features and Krumhansl-Kessler profiles.

    Returns:
        dict with key, mode, key_confidence, mode_confidence,
        all_correlations (for debugging)
    """
    print("[analyze] Estimating musical key...")

    # Compute CQT chromagram and average across time
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    chroma_mean = np.mean(chroma, axis=1)  # shape: (12,)

    # Normalize chroma vector
    chroma_norm = chroma_mean - np.mean(chroma_mean)
    norm_mag = np.linalg.norm(chroma_norm)
    if norm_mag < 1e-8:
        print("[analyze] WARNING: Near-silent audio, key detection unreliable.")
        return _low_confidence_key_result()

    # Correlate with all 12 major and 12 minor key profiles
    major_corrs = np.zeros(12)
    minor_corrs = np.zeros(12)

    for shift in range(12):
        shifted_chroma = np.roll(chroma_norm, -shift)
        major_ref = MAJOR_PROFILE - np.mean(MAJOR_PROFILE)
        minor_ref = MINOR_PROFILE - np.mean(MINOR_PROFILE)
        major_corrs[shift] = np.corrcoef(shifted_chroma, major_ref)[0, 1]
        minor_corrs[shift] = np.corrcoef(shifted_chroma, minor_ref)[0, 1]

    # Find best key
    best_major_idx = int(np.argmax(major_corrs))
    best_minor_idx = int(np.argmax(minor_corrs))
    best_major_corr = float(major_corrs[best_major_idx])
    best_minor_corr = float(minor_corrs[best_minor_idx])

    if best_major_corr >= best_minor_corr:
        key_name = PITCH_NAMES[best_major_idx]
        mode = "major"
        key_corr = best_major_corr
        mode_corr = best_major_corr - best_minor_corr
    else:
        key_name = PITCH_NAMES[best_minor_idx]
        mode = "minor"
        key_corr = best_minor_corr
        mode_corr = best_minor_corr - best_major_corr

    # Confidence: how much the best key stands out from the average
    all_corrs = np.concatenate([major_corrs, minor_corrs])
    corr_range = float(np.max(all_corrs) - np.mean(all_corrs))
    key_confidence = max(0.0, min(1.0, corr_range))
    mode_confidence = max(0.0, min(1.0, abs(mode_corr)))

    result = {
        "key": key_name,
        "mode": mode,
        "key_confidence": round(key_confidence, 4),
        "mode_confidence": round(mode_confidence, 4),
        "key_full": f"{key_name} {mode}",
    }
    print(f"[analyze] Key: {result['key_full']}  |  Key conf: {result['key_confidence']}  |  Mode conf: {result['mode_confidence']}")
    return result


def _low_confidence_key_result():
    """Return a default key result for near-silent or unanalyzable audio."""
    return {
        "key": "C",
        "mode": "major",
        "key_confidence": 0.0,
        "mode_confidence": 0.0,
        "key_full": "C major",
    }


# ── Energy Analysis ──────────────────────────────────────────

def analyze_energy(y, sr):
    """Compute energy metrics: overall energy level (0-1), RMS curve, spectral centroid.

    Returns:
        dict with energy (0-1 float), rms_mean, rms_max,
        spectral_centroid_mean, energy_curve (downsampled list)
    """
    print("[analyze] Computing energy profile...")

    # RMS energy per frame
    rms = librosa.feature.rms(y=y)[0]
    rms_mean = float(np.mean(rms))
    rms_max = float(np.max(rms))

    # Normalize energy to 0-1 range using a reference scale
    # Typical pop/rock RMS ranges from 0.01 (quiet) to 0.3 (loud)
    # We use a sigmoid-like mapping for robustness
    energy_raw = rms_mean / max(rms_max, 1e-8)
    energy_normalized = float(np.clip(rms_mean / 0.15, 0.0, 1.0))

    # Spectral centroid (brightness indicator)
    spec_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
    centroid_mean = float(np.mean(spec_centroid))

    # Downsample RMS curve to ~100 points for storage
    n_points = min(100, len(rms))
    if len(rms) > n_points:
        indices = np.linspace(0, len(rms) - 1, n_points, dtype=int)
        rms_curve = [round(float(rms[i]), 4) for i in indices]
    else:
        rms_curve = [round(float(v), 4) for v in rms]

    result = {
        "energy": round(energy_normalized, 4),
        "rms_mean": round(rms_mean, 6),
        "rms_max": round(rms_max, 6),
        "spectral_centroid_mean": round(centroid_mean, 1),
        "energy_curve": rms_curve,
    }
    print(f"[analyze] Energy: {result['energy']}  |  RMS mean: {result['rms_mean']:.4f}  |  Centroid: {result['spectral_centroid_mean']:.0f} Hz")
    return result


# ── Segment Analysis ─────────────────────────────────────────

def analyze_segments(y, sr):
    """Detect structural segments (intro, verse, chorus, etc.) using spectral changes.

    Returns:
        list of segment dicts with start_time, end_time, label
    """
    print("[analyze] Detecting segments...")
    try:
        # Use spectral clustering for segment boundaries
        boundaries = librosa.segment.agglomerative(
            librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13),
            k=min(8, max(2, int(librosa.get_duration(y=y, sr=sr) / 15)))
        )
        boundary_times = librosa.frames_to_time(boundaries, sr=sr)

        labels = ["intro"] + [f"section_{i+1}" for i in range(len(boundary_times) - 1)]
        segments = []
        for i, bt in enumerate(boundary_times):
            end_time = boundary_times[i + 1] if i + 1 < len(boundary_times) else librosa.get_duration(y=y, sr=sr)
            segments.append({
                "start_time": round(float(bt), 2),
                "end_time": round(float(end_time), 2),
                "label": labels[i] if i < len(labels) else f"section_{i+1}",
            })
        print(f"[analyze] Segments detected: {len(segments)}")
        return segments
    except Exception as exc:
        print(f"[analyze] WARNING: Segment detection failed ({exc}), skipping.")
        return []


# ── Mood Mapping ─────────────────────────────────────────────

def load_mood_map(project_root):
    """Load mood_map.json from the data directory."""
    path = os.path.join(project_root, "data", "mood_map.json")
    if not os.path.isfile(path):
        print(f"[analyze] WARNING: mood_map.json not found at {path}")
        return None
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def load_genre_defaults(project_root):
    """Load genre_defaults.json from the data directory."""
    path = os.path.join(project_root, "data", "genre_defaults.json")
    if not os.path.isfile(path):
        print(f"[analyze] WARNING: genre_defaults.json not found at {path}")
        return None
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def determine_mood(bpm_data, key_data, energy_data, mood_map):
    """Apply mood_map.json rules in priority order to determine the song's mood.

    Args:
        bpm_data: dict from detect_bpm_and_beats()
        key_data: dict from detect_key()
        energy_data: dict from analyze_energy()
        mood_map: parsed mood_map.json

    Returns:
        tuple (mood_name: str, matched_rule: dict or None, fallback_used: bool)
    """
    if not mood_map:
        return "chill", None, True

    bpm = bpm_data["bpm"]
    energy = energy_data["energy"]
    mode = key_data["mode"]
    priority = mood_map.get("priority_order", [])
    rules = mood_map.get("rules", [])

    # Build lookup: mood_name → rule
    rule_map = {r["mood"]: r for r in rules}

    print(f"[analyze] Mood mapping: BPM={bpm}, energy={energy}, mode={mode}")

    # Evaluate rules in priority order
    for mood_name in priority:
        rule = rule_map.get(mood_name)
        if not rule:
            continue
        conds = rule.get("conditions", {})

        # Check BPM range
        if bpm < conds.get("bpm_min", 0):
            continue
        if bpm > conds.get("bpm_max", 999):
            continue

        # Check energy range
        if energy < conds.get("energy_min", 0):
            continue
        if "energy_max" in conds and energy > conds["energy_max"]:
            continue

        # Check key mode (if specified)
        if "key_mode" in conds and mode != conds["key_mode"]:
            continue

        # All conditions met
        print(f"[analyze] Mood matched: {mood_name} (rule: {rule.get('description', '')})")
        return mood_name, rule, False

    # No rule matched — fallback
    print("[analyze] No mood rule matched, using fallback: chill")
    return "chill", None, True


# ── Safety Valve ─────────────────────────────────────────────

def apply_safety_valve(key_data, mood_name, genre, mood_map, genre_defaults):
    """Implement the Librosa Confidence Safety Valve.

    If key_confidence < threshold or mode_confidence < threshold,
    fall back to genre_defaults.json poses instead of mood-derived poses.

    Args:
        key_data: dict from detect_key()
        mood_name: determined mood string
        genre: song genre string
        mood_map: parsed mood_map.json
        genre_defaults: parsed genre_defaults.json

    Returns:
        tuple (use_genre_fallback: bool, reason: str or None)
    """
    if not mood_map or not genre_defaults:
        return False, None

    valve = mood_map.get("safety_valve", {})
    key_thresh = valve.get("key_confidence_threshold", 0.15)
    mode_thresh = valve.get("mode_confidence_threshold", 0.10)

    key_conf = key_data.get("key_confidence", 0)
    mode_conf = key_data.get("mode_confidence", 0)

    if key_conf < key_thresh:
        reason = f"key_confidence ({key_conf:.4f}) < threshold ({key_thresh})"
        print(f"[analyze] SAFETY VALVE: {reason}")
        return True, reason

    if mode_conf < mode_thresh:
        reason = f"mode_confidence ({mode_conf:.4f}) < threshold ({mode_thresh})"
        print(f"[analyze] SAFETY VALVE: {reason}")
        return True, reason

    return False, None


# ── Character Assignment ─────────────────────────────────────

def assign_characters(mood_name, genre, mood_map, genre_defaults,
                      use_genre_fallback, project_root):
    """Assign Weeter, Blubby, and Together poses based on mood or genre fallback.

    Returns:
        dict with weeter, blubby, together sub-dicts (pose_path, animation, scale)
    """
    characters_base = os.path.join(project_root, "assets", "characters")

    if use_genre_fallback and genre_defaults:
        # Use genre_defaults.json
        genres = genre_defaults.get("genres", {})
        genre_entry = genres.get(genre, genre_defaults.get("fallback", {}))
        default_mood = genre_entry.get("default_mood", "chill")

        print(f"[analyze] Characters: genre fallback ({genre} → {default_mood})")
        result = {
            "weeter": {
                "pose_path": os.path.join(characters_base, "weeter", genre_entry.get("weeter_pose", "neutral/weeter_0.png")),
                "pose_relative": os.path.join("weeter", genre_entry.get("weeter_pose", "neutral/weeter_0.png")),
                "animation": "gentle_breathe",
                "scale": 1.0,
            },
            "blubby": {
                "pose_path": os.path.join(characters_base, "blubby", genre_entry.get("blubby_pose", "neutral/blubby_0.png")),
                "pose_relative": os.path.join("blubby", genre_entry.get("blubby_pose", "neutral/blubby_0.png")),
                "animation": "gentle_breathe",
                "scale": 1.0,
            },
            "together": {
                "pose_path": os.path.join(characters_base, "together", genre_entry.get("together_pose", "chill/weeter_blubby_together.png")),
                "pose_relative": os.path.join("together", genre_entry.get("together_pose", "chill/weeter_blubby_together.png")),
                "animation": "gentle_breathe",
                "scale": 0.95,
            },
            "source": "genre_defaults",
            "mood_used": default_mood,
        }
        return result

    # Use mood_map character_dynamics
    dynamics = {}
    if mood_map:
        dynamics = mood_map.get("character_dynamics", {}).get(mood_name, {})

    if not dynamics:
        # Final fallback
        dynamics = {
            "weeter": {"pose_folder": "neutral", "animation": "gentle_breathe", "scale": 1.0},
            "blubby": {"pose_folder": "neutral", "animation": "gentle_breathe", "scale": 1.0},
            "together": {"pose_folder": "chill", "animation": "gentle_breathe", "scale": 0.95},
        }

    print(f"[analyze] Characters: mood-mapped ({mood_name})")

    result = {}
    for char_name in ["weeter", "blubby", "together"]:
        char_dyn = dynamics.get(char_name, {})
        pose_folder = char_dyn.get("pose_folder", "neutral")
        animation = char_dyn.get("animation", "gentle_breathe")
        scale = char_dyn.get("scale", 1.0)

        # Find the first available PNG in the pose folder
        char_dir = os.path.join(characters_base, char_name, pose_folder)
        pose_file = _find_first_png(char_dir)

        if pose_file:
            pose_path = os.path.join(char_dir, pose_file)
            pose_relative = os.path.join(char_name, pose_folder, pose_file)
        else:
            # Fallback to neutral
            neutral_dir = os.path.join(characters_base, char_name, "neutral")
            nf = _find_first_png(neutral_dir)
            pose_file = nf or f"{char_name}_0.png"
            pose_path = os.path.join(neutral_dir, pose_file)
            pose_relative = os.path.join(char_name, "neutral", pose_file)
            print(f"[analyze] WARNING: No PNGs in {char_dir}, using neutral/{pose_file}")

        result[char_name] = {
            "pose_path": pose_path,
            "pose_relative": pose_relative,
            "animation": animation,
            "scale": scale,
        }

    result["source"] = "mood_map"
    result["mood_used"] = mood_name
    return result


def _find_first_png(directory):
    """Return the first .png file found in directory, or None."""
    if not os.path.isdir(directory):
        return None
    for fname in sorted(os.listdir(directory)):
        if fname.lower().endswith(".png"):
            return fname
    return None


# ── Manifest Update ──────────────────────────────────────────

def update_manifest(manifest_path, analysis_result):
    """Update the song's manifest.json with analysis results.

    Reads the existing manifest, merges analysis data, writes atomically.
    """
    print(f"[analyze] Updating manifest: {manifest_path}")

    if not os.path.isfile(manifest_path):
        print(f"[analyze] ERROR: Manifest not found: {manifest_path}")
        return False

    with open(manifest_path, "r", encoding="utf-8") as fh:
        manifest = json.load(fh)

    # Merge analysis data
    manifest["analysis"] = analysis_result["analysis"]
    manifest["mood"] = analysis_result["mood"]
    manifest["characters"] = {
        "weeter": {
            "pose_path": analysis_result["characters"]["weeter"]["pose_relative"],
            "animation": analysis_result["characters"]["weeter"]["animation"],
            "scale": analysis_result["characters"]["weeter"].get("scale", 1.0),
        },
        "blubby": {
            "pose_path": analysis_result["characters"]["blubby"]["pose_relative"],
            "animation": analysis_result["characters"]["blubby"]["animation"],
            "scale": analysis_result["characters"]["blubby"].get("scale", 1.0),
        },
        "together": {
            "pose_path": analysis_result["characters"]["together"]["pose_relative"],
            "animation": analysis_result["characters"]["together"]["animation"],
            "scale": analysis_result["characters"]["together"].get("scale", 1.0),
        },
    }
    manifest["pipeline_stage"] = "analyzed"
    manifest["analyzed"] = True
    manifest["is_analyzed"] = True
    manifest["analyzed_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    # Atomic write
    tmp_path = manifest_path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)
        fh.write("\n")
        fh.flush()
        os.fsync(fh.fileno())
    os.rename(tmp_path, manifest_path)

    print(f"[analyze] Manifest updated: pipeline_stage → analyzed")
    return True


# ── Cache Update ─────────────────────────────────────────────

def update_cache(project_root, artist_slug, title_slug, analysis_summary):
    """Update the catalog cache with analysis metadata."""
    cache_path = get_default_cache_path(project_root)
    cache = load_cache(cache_path)

    cache_key = f"{artist_slug}::{title_slug}"
    if cache_key in cache:
        cache[cache_key]["analysis"] = analysis_summary
        cache[cache_key]["pipeline_stage"] = "analyzed"
        cache[cache_key]["analyzed_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        save_cache(cache_path, cache)
        print(f"[analyze] Cache updated: {cache_key} → analyzed")
    else:
        print(f"[analyze] WARNING: Cache key '{cache_key}' not found, skipping cache update.")


# ── Main Analysis Pipeline ───────────────────────────────────

def analyze_song(song_id, artist_slug, project_root=None):
    """Run the full analysis pipeline for an ingested song.

    Args:
        song_id: Song slug (directory name in catalog)
        artist_slug: Artist slug (directory name in catalog)
        project_root: Project root directory

    Returns:
        dict with full analysis results, or None on failure
    """
    _ensure_audio_deps()
    _init_key_profiles()
    root = project_root or os.getcwd()

    # Locate the manifest
    catalog_dir = os.path.join(root, "catalog", artist_slug, song_id)
    manifest_path = os.path.join(catalog_dir, "manifest.json")

    if not os.path.isfile(manifest_path):
        print(f"[analyze] ERROR: Manifest not found at {manifest_path}")
        print(f"[analyze]        Has this song been ingested? Run ingest_song.py first.")
        return None

    # Load manifest to get audio path and genre
    with open(manifest_path, "r", encoding="utf-8") as fh:
        manifest = json.load(fh)

    # Find audio file in catalog dir
    audio_path = None
    for fname in os.listdir(catalog_dir):
        if fname.lower().endswith((".mp3", ".wav", ".flac", ".m4a", ".ogg")):
            audio_path = os.path.join(catalog_dir, fname)
            break

    if not audio_path:
        source = manifest.get("source_audio", "")
        if os.path.isfile(source):
            audio_path = source
        else:
            print(f"[analyze] ERROR: No audio file found in {catalog_dir}")
            return None

    genre = manifest.get("genre", "pop")
    artist_name = manifest.get("artist", artist_slug)
    title_name = manifest.get("title", song_id)

    print(f"\n{'='*60}")
    print(f"[analyze] ANALYZING: \"{title_name}\" by {artist_name}")
    print(f"[analyze] Genre: {genre}")
    print(f"[analyze] Audio: {os.path.basename(audio_path)}")
    print(f"{'='*60}\n")

    start_time = time.time()

    # ── Step 1: Load audio ──
    y, sr, duration = load_audio(audio_path)

    # ── Step 2: BPM & Beats ──
    bpm_data = detect_bpm_and_beats(y, sr)

    # ── Step 3: Key Detection ──
    key_data = detect_key(y, sr)

    # ── Step 4: Energy Analysis ──
    energy_data = analyze_energy(y, sr)

    # ── Step 5: Segment Detection ──
    segments = analyze_segments(y, sr)

    # ── Step 6: Load configs ──
    mood_map = load_mood_map(root)
    genre_defaults = load_genre_defaults(root)

    # ── Step 7: Determine Mood ──
    mood_name, matched_rule, mood_fallback = determine_mood(
        bpm_data, key_data, energy_data, mood_map
    )

    # ── Step 8: Safety Valve ──
    use_genre_fallback, safety_reason = apply_safety_valve(
        key_data, mood_name, genre, mood_map, genre_defaults
    )

    # If safety valve triggers, override mood with genre default
    if use_genre_fallback and genre_defaults:
        genres_map = genre_defaults.get("genres", {})
        genre_entry = genres_map.get(genre, genre_defaults.get("fallback", {}))
        mood_name = genre_entry.get("default_mood", "chill")
        print(f"[analyze] Safety valve overrode mood to: {mood_name}")

    # ── Step 9: Assign Characters ──
    characters = assign_characters(
        mood_name, genre, mood_map, genre_defaults,
        use_genre_fallback, root
    )

    # ── Build analysis result ──
    elapsed = round(time.time() - start_time, 2)

    analysis_result = {
        "analysis": {
            "bpm": bpm_data["bpm"],
            "beat_count": bpm_data["beat_count"],
            "beat_times": bpm_data["beat_times"],
            "beats_per_second": bpm_data["beats_per_second"],
            "key": key_data["key"],
            "mode": key_data["mode"],
            "key_full": key_data["key_full"],
            "key_confidence": key_data["key_confidence"],
            "mode_confidence": key_data["mode_confidence"],
            "energy": energy_data["energy"],
            "rms_mean": energy_data["rms_mean"],
            "rms_max": energy_data["rms_max"],
            "spectral_centroid_mean": energy_data["spectral_centroid_mean"],
            "energy_curve": energy_data["energy_curve"],
            "duration_seconds": round(duration, 2),
            "segments": segments,
            "analysis_time_seconds": elapsed,
            "analyzer_version": "1.0.0",
        },
        "mood": {
            "name": mood_name,
            "rule_matched": matched_rule.get("description", None) if matched_rule else None,
            "fallback_used": mood_fallback,
            "safety_valve_triggered": use_genre_fallback,
            "safety_valve_reason": safety_reason,
        },
        "characters": characters,
    }

    # ── Step 10: Update manifest ──
    manifest_ok = update_manifest(manifest_path, analysis_result)

    # ── Step 11: Update cache ──
    cache_summary = {
        "bpm": bpm_data["bpm"],
        "key": key_data["key_full"],
        "energy": energy_data["energy"],
        "mood": mood_name,
    }
    update_cache(root, artist_slug, song_id, cache_summary)

    # ── Print summary ──
    print(f"\n{'='*60}")
    print(f"[analyze] ANALYSIS COMPLETE: \"{title_name}\" by {artist_name}")
    print(f"{'='*60}")
    print(f"  BPM:        {bpm_data['bpm']}")
    print(f"  Key:        {key_data['key_full']}")
    print(f"  Key Conf:   {key_data['key_confidence']}")
    print(f"  Mode Conf:  {key_data['mode_confidence']}")
    print(f"  Energy:     {energy_data['energy']}")
    print(f"  Mood:       {mood_name}")
    print(f"  Safety:     {'TRIGGERED - ' + (safety_reason or '') if use_genre_fallback else 'OK'}")
    print(f"  Weeter:     {characters['weeter']['pose_relative']}")
    print(f"  Blubby:     {characters['blubby']['pose_relative']}")
    print(f"  Together:   {characters['together']['pose_relative']}")
    print(f"  Segments:   {len(segments)}")
    print(f"  Duration:   {duration:.1f}s")
    print(f"  Elapsed:    {elapsed}s")
    print(f"  Manifest:   {'OK' if manifest_ok else 'FAILED'}")
    print(f"{'='*60}\n")

    return analysis_result


# ── CLI ──────────────────────────────────────────────────────

def list_catalog(root):
    """List all songs in the catalog directory."""
    catalog_dir = os.path.join(root, "catalog")
    if not os.path.isdir(catalog_dir):
        print(f"[catalog] ERROR: catalog directory not found at {catalog_dir}")
        return 1

    total = 0
    artists = sorted(d for d in os.listdir(catalog_dir)
                     if os.path.isdir(os.path.join(catalog_dir, d)) and not d.startswith("."))

    print(f"{'='*60}")
    print(f"  CATALOG LISTING — {catalog_dir}")
    print(f"{'='*60}")

    for artist in artists:
        artist_path = os.path.join(catalog_dir, artist)
        songs = sorted(d for d in os.listdir(artist_path)
                       if os.path.isdir(os.path.join(artist_path, d)) and not d.startswith("."))
        print(f"\n  Artist: {artist} ({len(songs)} songs)")
        for song in songs:
            song_path = os.path.join(artist_path, song)
            manifest = os.path.join(song_path, "manifest.json")
            status = "analyzed" if os.path.isfile(manifest) else "ingested"
            audio_files = [f for f in os.listdir(song_path)
                           if f.endswith((".mp3", ".wav", ".flac", ".ogg", ".m4a"))]
            audio_tag = audio_files[0] if audio_files else "no audio"
            print(f"    {song:<30} [{status}]  ({audio_tag})")
            total += 1

    print(f"\n{'='*60}")
    print(f"  TOTAL: {len(artists)} artist(s), {total} song(s)")
    print(f"{'='*60}")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Analyze an ingested song (Step 2 of Make Videos pipeline)."
    )
    parser.add_argument("--song-id", default=None,
                        help="Song slug (catalog directory name)")
    parser.add_argument("--artist", default=None,
                        help="Artist slug (catalog directory name)")
    parser.add_argument("--project-root", default=None,
                        help="Project root directory (default: parent of scripts/)")
    parser.add_argument("--list", action="store_true",
                        help="List all songs in the catalog and exit")
    args = parser.parse_args()

    root = args.project_root or PROJECT_ROOT_DEFAULT

    if args.list:
        sys.exit(list_catalog(root))

    if not args.song_id or not args.artist:
        parser.error("--song-id and --artist are required (unless using --list)")

    result = analyze_song(args.song_id, args.artist, root)
    if result is None:
        print("[analyze] FAILED: Analysis did not complete.")
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
