#!/usr/bin/env python3
"""visualizer.py - Step 6b of the Make Videos pipeline.

Renders an audio waveform/spectrum visualizer video (1920x1080):
  1. Loads manifest.json (requires pipeline_stage in ['analyzed', 'rendered'])
  2. Uses FFmpeg showwaves/showspectrum filters for audio visualization
  3. Composites waveform over Ken Burns background with character overlays
  4. Outputs visualizer MP4 (suffix: _viz)

Usage:
    python visualizer.py --song-id crazy --artist the_ridgemonts
    python visualizer.py --song-id crazy --artist the_ridgemonts --style spectrum
"""
import argparse
import json
import os
import subprocess
import sys
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
PROJECT_ROOT_DEFAULT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))


# ── Config Loaders ───────────────────────────────────────────

def load_recipe(project_root):
    """Load baseline_recipe.json."""
    path = os.path.join(project_root, "data", "baseline_recipe.json")
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def load_output_formats(project_root):
    """Load output_formats.json."""
    path = os.path.join(project_root, "data", "output_formats.json")
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def load_manifest(catalog_dir):
    """Load and validate manifest.json."""
    path = os.path.join(catalog_dir, "manifest.json")
    if not os.path.isfile(path):
        print(f"[viz] ERROR: manifest.json not found at {path}")
        return None, path
    with open(path, "r", encoding="utf-8") as fh:
        manifest = json.load(fh)
    stage = manifest.get("pipeline_stage", "")
    if stage not in ("analyzed", "rendered"):
        print(f"[viz] ERROR: pipeline_stage is '{stage}', need 'analyzed' or 'rendered'")
        return None, path
    return manifest, path


# ── Visualizer Styles ────────────────────────────────────────

def get_wave_filter(style, width, height, viz_height):
    """Return FFmpeg filter for audio visualization."""
    if style == "spectrum":
        return (
            f"showspectrum=s={width}x{viz_height}:mode=combined"
            f":color=intensity:scale=cbrt:fscale=log"
            f":overlap=0.8:slide=scroll"
        )
    elif style == "frequency":
        return (
            f"avectorscope=s={width}x{viz_height}:mode=lissajous_xy"
            f":draw=line:scale=cbrt"
        )
    else:  # default: waveform
        return (
            f"showwaves=s={width}x{viz_height}:mode=cline"
            f":colors=0x00E5FF|0x7C4DFF"
            f":rate=30:scale=cbrt"
        )


# ── Main Render ──────────────────────────────────────────────

def render_visualizer(manifest, manifest_path, catalog_dir, project_root,
                      style="waveform", force=False):
    """Render an audio visualizer video."""
    recipe = load_recipe(project_root)

    audio_path = manifest.get("source_audio", "")
    if not os.path.isfile(audio_path):
        print(f"[viz] ERROR: audio not found: {audio_path}")
        return False

    analysis = manifest.get("analysis", {})
    duration = analysis.get("duration_seconds", 30.0)
    fps = recipe.get("video", {}).get("fps", 30)
    intro_dur = recipe.get("timing", {}).get("intro_duration_seconds", 3.0)
    endcard_dur = recipe.get("timing", {}).get("endcard_duration_seconds", 5.0)
    total_dur = intro_dur + duration + endcard_dur

    width, height = 1920, 1080
    viz_height = 300  # height of the waveform band

    output_path = os.path.join(catalog_dir, "viz.mp4")
    artist = manifest.get("artist", "Unknown")
    title = manifest.get("title", "Untitled")

    # Characters
    chars = manifest.get("characters", {})
    weeter_path = chars.get("weeter", {}).get("pose_path", "")
    blubby_path = chars.get("blubby", {}).get("pose_path", "")

    fmt = recipe.get("video", {})
    char_height = int(height * recipe.get("composition", {}).get("character_max_height_pct", 0.45))

    # Build filter complex
    filter_parts = []
    input_args = []
    input_count = 0

    # Input 0: audio
    input_args.extend(["-i", audio_path])
    input_count += 1

    # Background generation
    bg_c1 = "0f0c29"
    bg_c2 = "302b63"
    filter_parts.append(
        f"color=c=0x{bg_c1}:s={width}x{height}:d={total_dur}:r={fps}[bg]"
    )

    # Audio visualization from input 0
    wave_filter = get_wave_filter(style, width, viz_height)
    filter_parts.append(
        f"[0:a]{wave_filter}[wave_raw]"
    )
    # Pad waveform to full frame with transparency
    filter_parts.append(
        f"[wave_raw]format=rgba,pad=w={width}:h={height}"
        f":x=0:y={height - viz_height - 80}:color=0x00000000[wave]"
    )

    # Overlay waveform on background
    filter_parts.append(
        f"[bg][wave]overlay=0:0:shortest=1:format=auto[v_wave]"
    )
    current_label = "v_wave"

    # Character overlays
    if weeter_path and os.path.isfile(weeter_path):
        input_args.extend(["-i", weeter_path])
        w_idx = input_count
        input_count += 1
        filter_parts.append(f"[{w_idx}:v]scale=-1:{char_height}[weeter]")
        filter_parts.append(
            f"[{current_label}][weeter]overlay=x=W*0.18-w/2:y=H*0.50-h/2"
            f":shortest=1[v_w]"
        )
        current_label = "v_w"

    if blubby_path and os.path.isfile(blubby_path):
        input_args.extend(["-i", blubby_path])
        b_idx = input_count
        input_count += 1
        filter_parts.append(f"[{b_idx}:v]scale=-1:{char_height}[blubby]")
        filter_parts.append(
            f"[{current_label}][blubby]overlay=x=W*0.62-w/2:y=H*0.50-h/2"
            f":shortest=1[v_b]"
        )
        current_label = "v_b"

    # Title
    title_safe = title.replace("'", "\\'").replace(":", "\\:")
    artist_safe = artist.replace("'", "\\'").replace(":", "\\:").replace("_", " ").title()
    filter_parts.append(
        f"[{current_label}]drawtext=text='{artist_safe} - {title_safe}'"
        f":fontsize=42:fontcolor=white:borderw=2:bordercolor=black"
        f":x=(w-tw)/2:y=40"
        f":alpha='if(lt(t,0.5),t/0.5,if(lt(t,{total_dur - 1}),1,({total_dur}-t)/1))'"
        f"[v_titled]"
    )
    current_label = "v_titled"

    # Style label
    style_label = style.replace("_", " ").title()
    filter_parts.append(
        f"[{current_label}]drawtext=text='Audio {style_label}'"
        f":fontsize=24:fontcolor=0xCCCCCC:x=20:y=h-40[v_labeled]"
    )
    current_label = "v_labeled"

    # Fade in/out
    fade_in = recipe.get("timing", {}).get("fade_in_seconds", 0.5)
    fade_out = recipe.get("timing", {}).get("fade_out_seconds", 1.0)
    filter_parts.append(
        f"[{current_label}]fade=in:st=0:d={fade_in},"
        f"fade=out:st={total_dur - fade_out}:d={fade_out}[vout]"
    )

    filter_complex = ";".join(filter_parts)

    cmd = [
        "ffmpeg", "-y",
    ] + input_args + [
        "-filter_complex", filter_complex,
        "-map", "[vout]", "-map", "0:a",
        "-c:v", fmt.get("codec", "libx264"),
        "-preset", fmt.get("preset", "medium"),
        "-crf", str(fmt.get("crf", 23)),
        "-pix_fmt", fmt.get("pixel_format", "yuv420p"),
        "-c:a", recipe.get("audio", {}).get("codec", "aac"),
        "-b:a", recipe.get("audio", {}).get("bitrate", "192k"),
        "-t", str(total_dur),
        "-shortest",
        output_path,
    ]

    print(f"[viz] Rendering {style} visualizer: {title} ({total_dur:.1f}s)")
    t0 = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    elapsed = time.time() - t0

    if result.returncode != 0:
        print(f"[viz] FFmpeg FAILED ({elapsed:.1f}s)")
        stderr_tail = result.stderr[-500:] if result.stderr else "no stderr"
        print(f"[viz] stderr: {stderr_tail}")
        return False

    size = os.path.getsize(output_path) if os.path.isfile(output_path) else 0
    print(f"[viz] SUCCESS: {output_path} ({size:,} bytes, {elapsed:.1f}s)")

    # Update manifest
    manifest.setdefault("outputs", {})["visualizer"] = {
        "path": output_path,
        "size_bytes": size,
        "render_time_seconds": round(elapsed, 2),
        "style": style,
    }
    try:
        with open(manifest_path, "w", encoding="utf-8") as fh:
            json.dump(manifest, fh, indent=2, ensure_ascii=False)
    except OSError as e:
        print(f"[viz] WARNING: could not update manifest: {e}")

    return True


# ── CLI ──────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Render audio visualizer video.")
    parser.add_argument("--song-id", required=True)
    parser.add_argument("--artist", required=True)
    parser.add_argument("--project-root", default=PROJECT_ROOT_DEFAULT)
    parser.add_argument("--style", default="waveform",
                        choices=["waveform", "spectrum", "frequency"],
                        help="Visualization style")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    catalog_dir = os.path.join(args.project_root, "catalog", args.artist, args.song_id)
    manifest, manifest_path = load_manifest(catalog_dir)
    if manifest is None:
        sys.exit(1)

    ok = render_visualizer(
        manifest, manifest_path, catalog_dir, args.project_root,
        style=args.style, force=args.force,
    )
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
