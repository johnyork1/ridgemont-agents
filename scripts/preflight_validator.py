#!/usr/bin/env python3
"""preflight_validator.py - Fail-fast validation for the Make Videos pipeline.

Checks that required directories, configs, and character assets exist
on disk before any rendering step begins. Exits non-zero on first failure.

Usage:
    python preflight_validator.py [--project-root /path/to/root]
    python preflight_validator.py --manifest catalog/artist/song/manifest.json
"""
import argparse, json, os, sys

REQUIRED_DIRS = [
    "scripts", "data", "assets/characters", "catalog", "ingestion",
]
REQUIRED_CONFIGS = [
    "data/mood_map.json", "data/baseline_recipe.json",
    "data/genre_defaults.json", "data/output_formats.json",
    "data/beat_sync_strategies.json", "data/genre_visual_identity.json",
    "data/lyric_config.json",
]
REQUIRED_CHARACTER_DIRS = [
    "assets/characters/weeter",
    "assets/characters/blubby",
    "assets/characters/together",
]


def check_directories(root):
    errors = []
    for d in REQUIRED_DIRS:
        if not os.path.isdir(os.path.join(root, d)):
            errors.append(f"Missing directory: {d}/")
    return errors


def check_configs(root):
    errors = []
    for cfg in REQUIRED_CONFIGS:
        path = os.path.join(root, cfg)
        if not os.path.isfile(path):
            errors.append(f"Missing config: {cfg}")
            continue
        try:
            with open(path, "r", encoding="utf-8") as fh:
                json.load(fh)
        except (json.JSONDecodeError, OSError) as exc:
            errors.append(f"Invalid config {cfg}: {exc}")
    return errors


def check_characters(root):
    errors = []
    for d in REQUIRED_CHARACTER_DIRS:
        path = os.path.join(root, d)
        if not os.path.isdir(path):
            errors.append(f"Missing character dir: {d}/")
            continue
        has_png = False
        for dirpath, _, filenames in os.walk(path):
            if any(f.lower().endswith(".png") for f in filenames):
                has_png = True
                break
        if not has_png:
            errors.append(f"No PNGs found in {d}/")
    return errors


def check_manifest(manifest_path):
    errors = []
    if not os.path.isfile(manifest_path):
        return [f"Manifest not found: {manifest_path}"]
    try:
        with open(manifest_path, "r", encoding="utf-8") as fh:
            manifest = json.load(fh)
    except (json.JSONDecodeError, OSError) as exc:
        return [f"Invalid manifest: {exc}"]
    audio = manifest.get("source_audio")
    if audio and not os.path.isfile(audio):
        errors.append(f"Missing audio: {audio}")
    for key in ("weeter_pose", "blubby_pose", "together_pose"):
        pose = manifest.get(key)
        if pose and not os.path.isfile(pose):
            errors.append(f"Missing {key}: {pose}")
    chars = manifest.get("characters", {})
    for char_name, char_data in chars.items():
        pose_path = char_data.get("pose_path")
        if pose_path and not os.path.isfile(pose_path):
            errors.append(f"Missing pose for {char_name}: {pose_path}")
    return errors


def run_preflight(root, manifest_path=None):
    all_errors = []
    print(f"[preflight] Checking project root: {root}")
    all_errors.extend(check_directories(root))
    all_errors.extend(check_configs(root))
    all_errors.extend(check_characters(root))
    if manifest_path:
        print(f"[preflight] Checking manifest: {manifest_path}")
        all_errors.extend(check_manifest(manifest_path))
    if all_errors:
        print(f"\n[preflight] FAILED - {len(all_errors)} issue(s):")
        for err in all_errors:
            print(f"  x {err}")
        return False, all_errors
    else:
        print("[preflight] PASSED - all checks OK.")
        return True, []


def main():
    parser = argparse.ArgumentParser(description="Preflight validation for Make Videos.")
    parser.add_argument("--project-root", default=os.getcwd())
    parser.add_argument("--manifest", default=None)
    args = parser.parse_args()
    passed, _ = run_preflight(args.project_root, args.manifest)
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
