#!/usr/bin/env python3
"""meme_sign_render.py - Step 6c of the Make Videos pipeline.

Renders a static or animated meme image with Weeter/Blubby holding a sign:
  1. Loads manifest.json for character pose paths and genre identity
  2. Uses genre_visual_identity.json for color theming
  3. Composites characters + text-on-sign via FFmpeg drawtext + overlay
  4. Outputs a PNG (static) or short MP4 (animated) meme card

Usage:
    python meme_sign_render.py --song-id crazy --artist the_ridgemonts --text "Stream now!"
    python meme_sign_render.py --text "New album dropping!" --genre reggae --animated
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
    """Load genre_defaults.json for character pose fallbacks."""
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


# ── Sign Renderer ────────────────────────────────────────────

def resolve_character_paths(manifest, genre, project_root):
    """Get Weeter and Blubby pose paths from manifest or genre defaults."""
    chars_dir = os.path.join(project_root, "assets", "characters")

    if manifest:
        chars = manifest.get("characters", {})
        weeter = chars.get("weeter", {}).get("pose_path", "")
        blubby = chars.get("blubby", {}).get("pose_path", "")
        if weeter and os.path.isfile(weeter) and blubby and os.path.isfile(blubby):
            return weeter, blubby

    defaults = load_genre_defaults(project_root)
    genre_data = defaults.get("genres", {}).get(genre, defaults.get("fallback", {}))
    weeter_rel = genre_data.get("weeter_pose", "neutral/weeter_0.png")
    blubby_rel = genre_data.get("blubby_pose", "neutral/blubby_0.png")
    weeter = os.path.join(chars_dir, "weeter", weeter_rel)
    blubby = os.path.join(chars_dir, "blubby", blubby_rel)
    return weeter, blubby


def render_meme_sign(text, genre, project_root, output_path,
                     manifest=None, animated=False, duration=5):
    """Render a meme sign image/video with characters and custom text."""
    identity = load_visual_identity(project_root)
    genre_style = identity.get("genres", {}).get(genre, identity.get("fallback", {}))

    primary = genre_style.get("primary_color", "#37474F").replace("#", "")
    secondary = genre_style.get("secondary_color", "#26C6DA").replace("#", "")
    accent = genre_style.get("accent_color", "#FFAB40").replace("#", "")

    weeter_path, blubby_path = resolve_character_paths(manifest, genre, project_root)

    width, height = 1280, 720
    sign_w, sign_h = 700, 200
    sign_x = (width - sign_w) // 2
    sign_y = int(height * 0.35)
    char_h = int(height * 0.55)

    text_escaped = text.replace("'", "\\'").replace(":", "\\:")

    filter_parts = []

    if animated:
        fps = 30
        filter_parts.append(
            f"color=c=0x{primary}:s={width}x{height}:d={duration}:r={fps}[bg]"
        )
    else:
        filter_parts.append(
            f"color=c=0x{primary}:s={width}x{height}:d=1:r=1[bg]"
        )

    # Sign background (rounded rect approximation)
    filter_parts.append(
        f"[bg]drawbox=x={sign_x}:y={sign_y}:w={sign_w}:h={sign_h}"
        f":color=0x{secondary}@0.9:t=fill[bg_sign]"
    )
    # Sign border
    filter_parts.append(
        f"[bg_sign]drawbox=x={sign_x}:y={sign_y}:w={sign_w}:h={sign_h}"
        f":color=0x{accent}:t=4[bg_border]"
    )
    current = "bg_border"

    # Sign text
    font_size = min(48, max(24, int(640 / max(len(text), 1) * 1.8)))
    filter_parts.append(
        f"[{current}]drawtext=text='{text_escaped}'"
        f":fontsize={font_size}:fontcolor=white"
        f":borderw=2:bordercolor=0x{primary}"
        f":x=(w-tw)/2:y={sign_y + sign_h // 2}-th/2[v_text]"
    )
    current = "v_text"

    # Character overlays
    input_args = []
    input_idx = 0

    if weeter_path and os.path.isfile(weeter_path):
        input_args.extend(["-i", weeter_path])
        filter_parts.append(f"[{input_idx}:v]scale=-1:{char_h}[weeter]")
        filter_parts.append(
            f"[{current}][weeter]overlay=x=W*0.12-w/2:y=H*0.95-h"
            f":shortest=1[v_w]"
        )
        current = "v_w"
        input_idx += 1

    if blubby_path and os.path.isfile(blubby_path):
        input_args.extend(["-i", blubby_path])
        filter_parts.append(f"[{input_idx}:v]scale=-1:{char_h}[blubby]")
        filter_parts.append(
            f"[{current}][blubby]overlay=x=W*0.68-w/2:y=H*0.95-h"
            f":shortest=1[v_b]"
        )
        current = "v_b"
        input_idx += 1

    # Credit text
    filter_parts.append(
        f"[{current}]drawtext=text='The Ridgemonts'"
        f":fontsize=20:fontcolor=0xCCCCCC:x=(w-tw)/2:y=h-30[vout]"
    )

    filter_complex = ";".join(filter_parts)

    if animated:
        cmd = [
            "ffmpeg", "-y",
        ] + input_args + [
            "-f", "lavfi", "-i",
            f"color=c=0x{primary}:s={width}x{height}:d={duration}:r=30",
            "-filter_complex", filter_complex,
            "-map", "[vout]",
            "-c:v", "libx264", "-crf", "23", "-pix_fmt", "yuv420p",
            "-t", str(duration),
            output_path,
        ]
    else:
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

    print(f"[meme] Rendering {'animated' if animated else 'static'} sign: \"{text}\"")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"[meme] FFmpeg FAILED")
        stderr_tail = result.stderr[-500:] if result.stderr else "no stderr"
        print(f"[meme] stderr: {stderr_tail}")
        return False

    size = os.path.getsize(output_path) if os.path.isfile(output_path) else 0
    print(f"[meme] SUCCESS: {output_path} ({size:,} bytes)")
    return True


# ── CLI ──────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Render meme sign with characters.")
    parser.add_argument("--text", required=True, help="Text to display on sign")
    parser.add_argument("--song-id", default=None)
    parser.add_argument("--artist", default=None)
    parser.add_argument("--genre", default="pop", help="Genre for styling fallback")
    parser.add_argument("--project-root", default=PROJECT_ROOT_DEFAULT)
    parser.add_argument("--output", default=None, help="Output path (auto if omitted)")
    parser.add_argument("--animated", action="store_true", help="Render as short MP4")
    parser.add_argument("--duration", type=int, default=5, help="Duration if animated")
    args = parser.parse_args()

    manifest = None
    if args.song_id and args.artist:
        catalog_dir = os.path.join(args.project_root, "catalog", args.artist, args.song_id)
        manifest, _ = load_manifest(catalog_dir)
        if manifest:
            args.genre = manifest.get("genre", args.genre)

    ext = ".mp4" if args.animated else ".png"
    if args.output:
        output_path = args.output
    elif args.song_id:
        catalog_dir = os.path.join(args.project_root, "catalog",
                                   args.artist or "the_ridgemonts", args.song_id)
        os.makedirs(catalog_dir, exist_ok=True)
        output_path = os.path.join(catalog_dir, f"meme_sign{ext}")
    else:
        output_path = os.path.join(args.project_root, f"meme_sign{ext}")

    ok = render_meme_sign(
        text=args.text, genre=args.genre, project_root=args.project_root,
        output_path=output_path, manifest=manifest,
        animated=args.animated, duration=args.duration,
    )
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
