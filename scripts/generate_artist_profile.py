#!/usr/bin/env python3
"""generate_artist_profile.py - Step 6e of the Make Videos pipeline.

Generates square artist profile cards (1080x1080 PNG) using genre_visual_identity.json:
  1. Loads genre_visual_identity.json for colors, font style, motif hints
  2. Loads genre_defaults.json for character pose selection
  3. Composites: themed gradient + characters + artist name + genre badge + motif text
  4. Outputs profile.png in the artist's catalog directory or custom path

Usage:
    python generate_artist_profile.py --artist the_ridgemonts --genre reggae
    python generate_artist_profile.py --artist the_ridgemonts --song-id crazy
    python generate_artist_profile.py --batch --project-root /path
"""
import argparse
import json
import os
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
PROJECT_ROOT_DEFAULT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))


# ── Config Loaders ───────────────────────────────────────────

def load_visual_identity(project_root):
    """Load genre_visual_identity.json."""
    path = os.path.join(project_root, "data", "genre_visual_identity.json")
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def load_genre_defaults(project_root):
    """Load genre_defaults.json."""
    path = os.path.join(project_root, "data", "genre_defaults.json")
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def load_manifest(catalog_dir):
    """Load manifest.json if available."""
    path = os.path.join(catalog_dir, "manifest.json")
    if not os.path.isfile(path):
        return None, path
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh), path


# ── Character Resolution ─────────────────────────────────────

def resolve_together_pose(genre, project_root, manifest=None):
    """Get together pose path from manifest or genre defaults."""
    chars_dir = os.path.join(project_root, "assets", "characters")

    if manifest:
        chars = manifest.get("characters", {})
        together = chars.get("together", {}).get("pose_path", "")
        if together and os.path.isfile(together):
            return together

    defaults = load_genre_defaults(project_root)
    gd = defaults.get("genres", {}).get(genre, defaults.get("fallback", {}))
    together_rel = gd.get("together_pose", "chill/weeter_blubby_together.png")
    return os.path.join(chars_dir, "together", together_rel)


def resolve_solo_characters(genre, project_root, manifest=None):
    """Get individual character paths."""
    chars_dir = os.path.join(project_root, "assets", "characters")

    if manifest:
        chars = manifest.get("characters", {})
        w = chars.get("weeter", {}).get("pose_path", "")
        b = chars.get("blubby", {}).get("pose_path", "")
        if w and os.path.isfile(w) and b and os.path.isfile(b):
            return w, b

    defaults = load_genre_defaults(project_root)
    gd = defaults.get("genres", {}).get(genre, defaults.get("fallback", {}))
    w = os.path.join(chars_dir, "weeter", gd.get("weeter_pose", "neutral/weeter_0.png"))
    b = os.path.join(chars_dir, "blubby", gd.get("blubby_pose", "neutral/blubby_0.png"))
    return w, b


# ── Profile Card Renderer ────────────────────────────────────

def render_profile_card(artist_name, genre, project_root, output_path,
                        manifest=None, use_together=True):
    """Render a square 1080x1080 artist profile card."""
    identity = load_visual_identity(project_root)
    style = identity.get("genres", {}).get(genre, identity.get("fallback", {}))

    primary = style.get("primary_color", "#37474F").replace("#", "")
    secondary = style.get("secondary_color", "#26C6DA").replace("#", "")
    accent = style.get("accent_color", "#FFAB40").replace("#", "")
    motifs = style.get("motifs", [])

    size = 1080
    char_h = int(size * 0.55)

    artist_display = artist_name.replace("_", " ").title()
    artist_escaped = artist_display.replace("'", "\\'").replace(":", "\\:")
    genre_escaped = genre.replace("_", " ").title().replace("'", "\\'")

    filter_parts = []

    # Background
    filter_parts.append(
        f"color=c=0x{primary}:s={size}x{size}:d=1:r=1[bg]"
    )

    # Decorative elements
    filter_parts.append(
        f"[bg]drawbox=x=0:y=0:w={size}:h=6:color=0x{accent}:t=fill[bg1]"
    )
    filter_parts.append(
        f"[bg1]drawbox=x=0:y={size-6}:w={size}:h=6:color=0x{accent}:t=fill[bg2]"
    )
    filter_parts.append(
        f"[bg2]drawbox=x=0:y=0:w=6:h={size}:color=0x{accent}:t=fill[bg3]"
    )
    filter_parts.append(
        f"[bg3]drawbox=x={size-6}:y=0:w=6:h={size}:color=0x{accent}:t=fill[bg4]"
    )
    current = "bg4"

    # Character overlay
    input_args = []
    input_idx = 0

    if use_together:
        together_path = resolve_together_pose(genre, project_root, manifest)
        if together_path and os.path.isfile(together_path):
            input_args.extend(["-i", together_path])
            filter_parts.append(f"[{input_idx}:v]scale=-1:{char_h}[chars]")
            filter_parts.append(
                f"[{current}][chars]overlay=x=(W-w)/2:y=H*0.58-h/2"
                f":shortest=1[v_chars]"
            )
            current = "v_chars"
            input_idx += 1
    else:
        weeter_path, blubby_path = resolve_solo_characters(genre, project_root, manifest)
        solo_h = int(size * 0.45)
        if weeter_path and os.path.isfile(weeter_path):
            input_args.extend(["-i", weeter_path])
            filter_parts.append(f"[{input_idx}:v]scale=-1:{solo_h}[weeter]")
            filter_parts.append(
                f"[{current}][weeter]overlay=x=W*0.18-w/2:y=H*0.70-h/2"
                f":shortest=1[v_w]"
            )
            current = "v_w"
            input_idx += 1
        if blubby_path and os.path.isfile(blubby_path):
            input_args.extend(["-i", blubby_path])
            filter_parts.append(f"[{input_idx}:v]scale=-1:{solo_h}[blubby]")
            filter_parts.append(
                f"[{current}][blubby]overlay=x=W*0.62-w/2:y=H*0.70-h/2"
                f":shortest=1[v_b]"
            )
            current = "v_b"
            input_idx += 1

    # Artist name (top area)
    name_size = min(72, max(36, int(800 / max(len(artist_display), 1) * 2.5)))
    filter_parts.append(
        f"[{current}]drawtext=text='{artist_escaped}'"
        f":fontsize={name_size}:fontcolor=white"
        f":borderw=3:bordercolor=0x{primary}"
        f":shadowx=2:shadowy=2:shadowcolor=black"
        f":x=(w-tw)/2:y=h*0.08[v_name]"
    )
    current = "v_name"

    # Genre badge
    filter_parts.append(
        f"[{current}]drawbox=x=(w-200)/2:y=h*0.08+{name_size + 15}:w=200:h=36"
        f":color=0x{accent}@0.85:t=fill[v_badge_bg]"
    )
    filter_parts.append(
        f"[v_badge_bg]drawtext=text='{genre_escaped}'"
        f":fontsize=22:fontcolor=white:borderw=1:bordercolor=0x{primary}"
        f":x=(w-tw)/2:y=h*0.08+{name_size + 22}[v_badge]"
    )
    current = "v_badge"

    # Motif text (subtle, bottom area)
    if motifs:
        motif_text = " • ".join(m.replace("_", " ").title() for m in motifs[:4])
        motif_escaped = motif_text.replace("'", "\\'").replace(":", "\\:")
        filter_parts.append(
            f"[{current}]drawtext=text='{motif_escaped}'"
            f":fontsize=18:fontcolor=0xAAAAAA"
            f":x=(w-tw)/2:y=h-40[vout]"
        )
    else:
        filter_parts.append(f"[{current}]null[vout]")

    filter_complex = ";".join(filter_parts)

    cmd = [
        "ffmpeg", "-y",
    ] + input_args + [
        "-f", "lavfi", "-i",
        f"color=c=0x{primary}:s={size}x{size}:d=1:r=1",
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        "-frames:v", "1",
        output_path,
    ]

    print(f"[profile] Rendering profile card: {artist_display} ({genre})")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"[profile] FFmpeg FAILED")
        stderr_tail = result.stderr[-300:] if result.stderr else "no stderr"
        print(f"[profile] stderr: {stderr_tail}")
        return False

    file_size = os.path.getsize(output_path) if os.path.isfile(output_path) else 0
    print(f"[profile] SUCCESS: {output_path} ({file_size:,} bytes)")
    return True


# ── Batch Mode ───────────────────────────────────────────────

def batch_profiles(project_root):
    """Generate profile cards for all artists in the catalog."""
    catalog_root = os.path.join(project_root, "catalog")
    count = 0
    errors = 0
    seen_artists = set()

    for artist_dir in sorted(os.listdir(catalog_root)):
        artist_path = os.path.join(catalog_root, artist_dir)
        if not os.path.isdir(artist_path):
            continue
        if artist_dir in seen_artists:
            continue
        seen_artists.add(artist_dir)

        # Find first song manifest for genre info
        genre = "pop"
        manifest = None
        for song_dir in sorted(os.listdir(artist_path)):
            song_path = os.path.join(artist_path, song_dir)
            m, _ = load_manifest(song_path)
            if m:
                genre = m.get("genre", genre)
                manifest = m
                break

        output = os.path.join(artist_path, "profile.png")
        ok = render_profile_card(artist_dir, genre, project_root, output, manifest)
        if ok:
            count += 1
        else:
            errors += 1

    print(f"[profile] Batch complete: {count} profiles, {errors} errors")
    return errors == 0


# ── CLI ──────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Generate artist profile cards.")
    parser.add_argument("--artist", default=None)
    parser.add_argument("--song-id", default=None, help="Song to derive genre from")
    parser.add_argument("--genre", default="pop")
    parser.add_argument("--project-root", default=PROJECT_ROOT_DEFAULT)
    parser.add_argument("--output", default=None)
    parser.add_argument("--solo", action="store_true",
                        help="Use solo character poses instead of together")
    parser.add_argument("--batch", action="store_true",
                        help="Generate for all catalog artists")
    args = parser.parse_args()

    if args.batch:
        ok = batch_profiles(args.project_root)
        sys.exit(0 if ok else 1)

    if not args.artist:
        print("[profile] ERROR: --artist required (or use --batch)")
        sys.exit(1)

    manifest = None
    if args.song_id:
        catalog_dir = os.path.join(args.project_root, "catalog", args.artist, args.song_id)
        manifest, _ = load_manifest(catalog_dir)
        if manifest:
            args.genre = manifest.get("genre", args.genre)

    if args.output:
        output_path = args.output
    else:
        artist_dir = os.path.join(args.project_root, "catalog", args.artist)
        os.makedirs(artist_dir, exist_ok=True)
        output_path = os.path.join(artist_dir, "profile.png")

    ok = render_profile_card(
        args.artist, args.genre, args.project_root, output_path,
        manifest=manifest, use_together=not args.solo,
    )
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
