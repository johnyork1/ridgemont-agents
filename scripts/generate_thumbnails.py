#!/usr/bin/env python3
"""generate_thumbnails.py - Step 6d of the Make Videos pipeline.

Generates 1280x720 PNG thumbnails for YouTube from catalog manifests:
  1. Loads manifest.json for song metadata, character poses, genre
  2. Uses genre_visual_identity.json for color theming
  3. Composites: gradient background + characters + title text + genre badge
  4. Outputs thumb.png in the song's catalog directory

Usage:
    python generate_thumbnails.py --song-id crazy --artist the_ridgemonts
    python generate_thumbnails.py --batch --project-root /path
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
    """Load manifest.json."""
    path = os.path.join(catalog_dir, "manifest.json")
    if not os.path.isfile(path):
        return None, path
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh), path


# ── Character Resolution ─────────────────────────────────────

def resolve_characters(manifest, genre, project_root):
    """Get character pose paths from manifest or genre defaults."""
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


# ── Thumbnail Renderer ───────────────────────────────────────

def render_thumbnail(manifest, genre, title, artist, project_root, output_path):
    """Render a single 1280x720 PNG thumbnail."""
    identity = load_visual_identity(project_root)
    style = identity.get("genres", {}).get(genre, identity.get("fallback", {}))

    primary = style.get("primary_color", "#37474F").replace("#", "")
    secondary = style.get("secondary_color", "#26C6DA").replace("#", "")
    accent = style.get("accent_color", "#FFAB40").replace("#", "")

    weeter_path, blubby_path = resolve_characters(manifest, genre, project_root)

    width, height = 1280, 720
    char_h = int(height * 0.60)

    title_escaped = title.replace("'", "\\'").replace(":", "\\:")
    artist_escaped = artist.replace("'", "\\'").replace(":", "\\:").replace("_", " ").title()
    genre_escaped = genre.replace("'", "\\'").replace("_", " ").title()

    filter_parts = []

    # Background
    filter_parts.append(
        f"color=c=0x{primary}:s={width}x{height}:d=1:r=1[bg]"
    )

    # Decorative stripe
    filter_parts.append(
        f"[bg]drawbox=x=0:y=0:w={width}:h=8:color=0x{accent}:t=fill[bg1]"
    )
    filter_parts.append(
        f"[bg1]drawbox=x=0:y={height-8}:w={width}:h=8:color=0x{accent}:t=fill[bg2]"
    )
    current = "bg2"

    # Character overlays
    input_args = []
    input_idx = 0

    if weeter_path and os.path.isfile(weeter_path):
        input_args.extend(["-i", weeter_path])
        filter_parts.append(f"[{input_idx}:v]scale=-1:{char_h}[weeter]")
        filter_parts.append(
            f"[{current}][weeter]overlay=x=W*0.05:y=H*0.95-h"
            f":shortest=1[v_w]"
        )
        current = "v_w"
        input_idx += 1

    if blubby_path and os.path.isfile(blubby_path):
        input_args.extend(["-i", blubby_path])
        filter_parts.append(f"[{input_idx}:v]scale=-1:{char_h}[blubby]")
        filter_parts.append(
            f"[{current}][blubby]overlay=x=W*0.72:y=H*0.95-h"
            f":shortest=1[v_b]"
        )
        current = "v_b"
        input_idx += 1

    # Title text (large, centered)
    title_size = min(64, max(32, int(900 / max(len(title), 1) * 2.5)))
    filter_parts.append(
        f"[{current}]drawtext=text='{title_escaped}'"
        f":fontsize={title_size}:fontcolor=white"
        f":borderw=3:bordercolor=0x{primary}"
        f":shadowx=2:shadowy=2:shadowcolor=black"
        f":x=(w-tw)/2:y=h*0.15[v_title]"
    )
    current = "v_title"

    # Artist name
    filter_parts.append(
        f"[{current}]drawtext=text='{artist_escaped}'"
        f":fontsize=36:fontcolor=0x{secondary}"
        f":borderw=1:bordercolor=black"
        f":x=(w-tw)/2:y=h*0.15+{title_size + 15}[v_artist]"
    )
    current = "v_artist"

    # Genre badge
    filter_parts.append(
        f"[{current}]drawbox=x=w-180:y=20:w=160:h=40"
        f":color=0x{accent}@0.85:t=fill[v_badge_bg]"
    )
    filter_parts.append(
        f"[v_badge_bg]drawtext=text='{genre_escaped}'"
        f":fontsize=22:fontcolor=white:borderw=1:bordercolor=0x{primary}"
        f":x=w-180+(160-tw)/2:y=30[vout]"
    )

    filter_complex = ";".join(filter_parts)

    cmd = [
        "ffmpeg", "-y",
    ] + input_args + [
        "-f", "lavfi", "-i",
        f"color=c=0x{primary}:s={width}x{height}:d=1:r=1",
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        "-frames:v", "1",
        output_path,
    ]

    print(f"[thumb] Rendering thumbnail: {artist} - {title} ({genre})")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"[thumb] FFmpeg FAILED")
        stderr_tail = result.stderr[-300:] if result.stderr else "no stderr"
        print(f"[thumb] stderr: {stderr_tail}")
        return False

    size = os.path.getsize(output_path) if os.path.isfile(output_path) else 0
    print(f"[thumb] SUCCESS: {output_path} ({size:,} bytes)")
    return True


# ── Batch Mode ───────────────────────────────────────────────

def batch_thumbnails(project_root):
    """Generate thumbnails for all songs in the catalog."""
    catalog_root = os.path.join(project_root, "catalog")
    count = 0
    errors = 0
    for artist_dir in sorted(os.listdir(catalog_root)):
        artist_path = os.path.join(catalog_root, artist_dir)
        if not os.path.isdir(artist_path):
            continue
        for song_dir in sorted(os.listdir(artist_path)):
            song_path = os.path.join(artist_path, song_dir)
            manifest, manifest_path = load_manifest(song_path)
            if manifest is None:
                continue
            genre = manifest.get("genre", "pop")
            title = manifest.get("title", song_dir)
            artist = manifest.get("artist", artist_dir)
            output = os.path.join(song_path, "thumb.png")
            ok = render_thumbnail(manifest, genre, title, artist, project_root, output)
            if ok:
                manifest.setdefault("outputs", {})["thumbnail"] = {
                    "path": output,
                    "size_bytes": os.path.getsize(output),
                }
                try:
                    with open(manifest_path, "w", encoding="utf-8") as fh:
                        json.dump(manifest, fh, indent=2, ensure_ascii=False)
                except OSError:
                    pass
                count += 1
            else:
                errors += 1
    print(f"[thumb] Batch complete: {count} thumbnails, {errors} errors")
    return errors == 0


# ── CLI ──────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Generate YouTube thumbnails.")
    parser.add_argument("--song-id", default=None)
    parser.add_argument("--artist", default=None)
    parser.add_argument("--genre", default="pop")
    parser.add_argument("--project-root", default=PROJECT_ROOT_DEFAULT)
    parser.add_argument("--output", default=None)
    parser.add_argument("--batch", action="store_true", help="Generate for all catalog songs")
    args = parser.parse_args()

    if args.batch:
        ok = batch_thumbnails(args.project_root)
        sys.exit(0 if ok else 1)

    if not args.song_id or not args.artist:
        print("[thumb] ERROR: --song-id and --artist required (or use --batch)")
        sys.exit(1)

    catalog_dir = os.path.join(args.project_root, "catalog", args.artist, args.song_id)
    manifest, manifest_path = load_manifest(catalog_dir)

    genre = args.genre
    title = args.song_id.replace("_", " ").title()
    artist = args.artist.replace("_", " ").title()
    if manifest:
        genre = manifest.get("genre", genre)
        title = manifest.get("title", title)
        artist = manifest.get("artist", artist)

    output_path = args.output or os.path.join(catalog_dir, "thumb.png")
    ok = render_thumbnail(manifest, genre, title, artist, args.project_root, output_path)

    if ok and manifest:
        manifest.setdefault("outputs", {})["thumbnail"] = {
            "path": output_path,
            "size_bytes": os.path.getsize(output_path),
        }
        try:
            with open(manifest_path, "w", encoding="utf-8") as fh:
                json.dump(manifest, fh, indent=2, ensure_ascii=False)
        except OSError:
            pass

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
