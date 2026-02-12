#!/usr/bin/env python3
"""lyric_video.py - Step 6a of the Make Videos pipeline.

Renders a lyric overlay video (1920x1080) from an analyzed manifest:
  1. Loads manifest.json (requires pipeline_stage in ['analyzed', 'rendered'])
  2. Reads lyric_config.json for font, position, animation, and timing params
  3. Parses LRC file (if present) or generates word-timed placeholders
  4. Builds FFmpeg filter graph:
     - Base: Ken Burns background (reuses baseline_master approach)
     - Character overlays (Weeter + Blubby)
     - Lyric drawtext with fade in/out per line
     - Bottom-third overlay bar for readability
  5. Composites audio + video into lyric MP4
  6. Updates manifest.json with outputs.lyric_video path

Usage:
    python lyric_video.py --song-id crazy --artist the_ridgemonts
    python lyric_video.py --song-id crazy --artist the_ridgemonts --lrc lyrics.lrc
"""
import argparse
import json
import math
import os
import re
import subprocess
import sys
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
PROJECT_ROOT_DEFAULT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

from render_signature import generate_signature


# ── Config Loaders ───────────────────────────────────────────

def load_lyric_config(project_root):
    """Load lyric_config.json."""
    path = os.path.join(project_root, "data", "lyric_config.json")
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def load_recipe(project_root):
    """Load baseline_recipe.json for shared timing/composition constants."""
    path = os.path.join(project_root, "data", "baseline_recipe.json")
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def load_manifest(catalog_dir):
    """Load manifest.json from catalog song directory."""
    path = os.path.join(catalog_dir, "manifest.json")
    if not os.path.isfile(path):
        print(f"[lyric] ERROR: manifest.json not found at {path}")
        return None, path
    with open(path, "r", encoding="utf-8") as fh:
        manifest = json.load(fh)
    stage = manifest.get("pipeline_stage", "")
    if stage not in ("analyzed", "rendered"):
        print(f"[lyric] ERROR: pipeline_stage is '{stage}', need 'analyzed' or 'rendered'")
        return None, path
    return manifest, path


# ── LRC Parser ───────────────────────────────────────────────

def parse_lrc(lrc_path):
    """Parse an LRC file into a list of {start_sec, text} entries."""
    lines = []
    pattern = re.compile(r"\[(\d+):(\d+)\.(\d+)\](.*)")
    with open(lrc_path, "r", encoding="utf-8") as fh:
        for raw in fh:
            m = pattern.match(raw.strip())
            if m:
                mins, secs, hundredths, text = m.groups()
                start = int(mins) * 60 + int(secs) + int(hundredths) / 100.0
                text = text.strip()
                if text:
                    lines.append({"start_sec": start, "text": text})
    return lines


def generate_placeholder_lyrics(duration, config):
    """Generate evenly spaced placeholder lyric lines when no LRC is available."""
    wpm = config.get("timing", {}).get("fallback_words_per_minute", 150)
    min_display = config.get("timing", {}).get("min_display_seconds", 1.0)
    max_display = config.get("timing", {}).get("max_display_seconds", 6.0)
    interval = max(min_display, min(max_display, 60.0 / (wpm / 8.0)))
    lines = []
    t = 1.0  # skip first second
    line_num = 1
    while t < duration - 2.0:
        lines.append({"start_sec": round(t, 2), "text": f"[Line {line_num}]"})
        t += interval
        line_num += 1
    return lines


# ── FFmpeg Lyric Filter Builder ──────────────────────────────

def build_lyric_drawtext_chain(lyric_lines, config, duration, fps=30):
    """Build a chain of drawtext filters for each lyric line with fade in/out."""
    font_cfg = config.get("font", {})
    pos_cfg = config.get("position", {})
    anim_cfg = config.get("animation", {})

    font_family = font_cfg.get("family", "Arial")
    font_size = font_cfg.get("size_primary", 56)
    font_color = font_cfg.get("color", "#FFFFFF").replace("#", "")
    shadow_color = font_cfg.get("shadow_color", "#000000").replace("#", "")
    shadow_x = font_cfg.get("shadow_offset_px", 3)
    stroke_color = font_cfg.get("stroke_color", "#000000").replace("#", "")
    stroke_width = font_cfg.get("stroke_width_px", 2)

    y_offset_pct = pos_cfg.get("y_offset_pct", 0.20)
    max_width_pct = pos_cfg.get("max_width_pct", 0.80)

    fade_in = anim_cfg.get("fade_in_seconds", 0.25)
    fade_out = anim_cfg.get("fade_out_seconds", 0.25)
    hold_after = anim_cfg.get("hold_after_seconds", 0.5)

    filters = []
    for i, line in enumerate(lyric_lines):
        start = line["start_sec"]
        # Determine end time: next line start or +max_display
        if i + 1 < len(lyric_lines):
            end = lyric_lines[i + 1]["start_sec"]
        else:
            end = min(start + 6.0, duration - 1.0)
        end = max(end, start + 0.5)

        text_escaped = line["text"].replace("'", "\\'").replace(":", "\\:")
        y_pos = f"h-h*{y_offset_pct}-th"

        alpha_expr = (
            f"if(lt(t,{start}),0,"
            f"if(lt(t,{start + fade_in}),(t-{start})/{fade_in},"
            f"if(lt(t,{end - fade_out}),1,"
            f"if(lt(t,{end}),({end}-t)/{fade_out},0))))"
        )

        dt = (
            f"drawtext=text='{text_escaped}'"
            f":fontsize={font_size}:fontcolor=0x{font_color}"
            f":borderw={stroke_width}:bordercolor=0x{stroke_color}"
            f":shadowx={shadow_x}:shadowy={shadow_x}:shadowcolor=0x{shadow_color}"
            f":x=(w-tw)/2:y={y_pos}"
            f":alpha='{alpha_expr}'"
        )
        filters.append(dt)

    return filters


def build_overlay_bar_filter(config, duration, intro_dur=3.0):
    """Build a semi-transparent overlay bar on the bottom third for readability."""
    bg_cfg = config.get("background", {})
    if not bg_cfg.get("overlay_enabled", True):
        return None
    color = bg_cfg.get("overlay_color", "#000000").replace("#", "")
    opacity = bg_cfg.get("overlay_opacity", 0.35)
    return (
        f"drawbox=x=0:y=ih*0.65:w=iw:h=ih*0.35"
        f":color=0x{color}@{opacity}:t=fill"
        f":enable='between(t,{intro_dur},{duration - 1.0})'"
    )


# ── Main Render ──────────────────────────────────────────────

def render_lyric_video(manifest, manifest_path, catalog_dir, project_root,
                       lrc_path=None, force=False):
    """Render a full lyric overlay video."""
    config = load_lyric_config(project_root)
    recipe = load_recipe(project_root)

    audio_path = manifest.get("source_audio", "")
    if not os.path.isfile(audio_path):
        print(f"[lyric] ERROR: audio not found: {audio_path}")
        return False

    analysis = manifest.get("analysis", {})
    duration = analysis.get("duration_seconds", 30.0)
    bpm = analysis.get("bpm", 120)
    fps = recipe.get("video", {}).get("fps", 30)
    intro_dur = recipe.get("timing", {}).get("intro_duration_seconds", 3.0)
    endcard_dur = recipe.get("timing", {}).get("endcard_duration_seconds", 5.0)
    total_dur = intro_dur + duration + endcard_dur

    # Parse lyrics
    if lrc_path and os.path.isfile(lrc_path):
        lyric_lines = parse_lrc(lrc_path)
        print(f"[lyric] Loaded {len(lyric_lines)} lines from LRC: {lrc_path}")
    else:
        lyric_lines = generate_placeholder_lyrics(duration, config)
        print(f"[lyric] Generated {len(lyric_lines)} placeholder lines (no LRC)")

    # Offset lyrics by intro duration
    for line in lyric_lines:
        line["start_sec"] += intro_dur

    # Build FFmpeg command
    output_path = os.path.join(catalog_dir, "lyric.mp4")
    artist = manifest.get("artist", "Unknown")
    title = manifest.get("title", "Untitled")
    fmt = recipe.get("video", {})

    # Character overlays
    chars = manifest.get("characters", {})
    weeter_path = chars.get("weeter", {}).get("pose_path", "")
    blubby_path = chars.get("blubby", {}).get("pose_path", "")

    # Build filter complex
    filter_parts = []

    # Background: solid color gradient
    bg_c1 = "1a1a2e"
    bg_c2 = "16213e"
    filter_parts.append(
        f"color=c=0x{bg_c1}:s=1920x1080:d={total_dur}:r={fps}[bg0]"
    )

    # Ken Burns zoom on background
    zoom_min, zoom_max = recipe.get("ken_burns", {}).get("zoom_range", [1.0, 1.15])
    cycle = recipe.get("ken_burns", {}).get("cycle_seconds", 8.0)
    z_mid = (zoom_min + zoom_max) / 2
    z_amp = (zoom_max - zoom_min) / 2
    filter_parts.append(
        f"[bg0]zoompan=z='{z_mid}+{z_amp}*sin(2*PI*on/({fps}*{cycle}))'"
        f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
        f":d={int(total_dur * fps)}:s=1920x1080:fps={fps}[bg]"
    )

    # Overlay bar for lyric readability
    bar_filter = build_overlay_bar_filter(config, total_dur, intro_dur)
    if bar_filter:
        filter_parts.append(f"[bg]{bar_filter}[bg_bar]")
        current_label = "bg_bar"
    else:
        current_label = "bg"

    # Character overlays (if available)
    input_idx = 1  # 0 = audio
    input_args = ["-i", audio_path]
    char_height = int(1080 * recipe.get("composition", {}).get("character_max_height_pct", 0.45))

    if weeter_path and os.path.isfile(weeter_path):
        input_args.extend(["-i", weeter_path])
        weeter_idx = input_idx
        input_idx += 1
        filter_parts.append(
            f"[{weeter_idx}:v]scale=-1:{char_height}[weeter]"
        )
        filter_parts.append(
            f"[{current_label}][weeter]overlay=x=W*0.18-w/2:y=H*0.87-h:shortest=1[v_w]"
        )
        current_label = "v_w"

    if blubby_path and os.path.isfile(blubby_path):
        input_args.extend(["-i", blubby_path])
        blubby_idx = input_idx
        input_idx += 1
        filter_parts.append(
            f"[{blubby_idx}:v]scale=-1:{char_height}[blubby]"
        )
        filter_parts.append(
            f"[{current_label}][blubby]overlay=x=W*0.62-w/2:y=H*0.87-h:shortest=1[v_b]"
        )
        current_label = "v_b"

    # Title drawtext
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

    # Lyric drawtext chain
    dt_filters = build_lyric_drawtext_chain(lyric_lines, config, total_dur, fps)
    for i, dt in enumerate(dt_filters):
        out_label = f"v_lyr{i}"
        filter_parts.append(f"[{current_label}]{dt}[{out_label}]")
        current_label = out_label

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
        "-f", "lavfi", "-i",
        f"color=c=0x{bg_c1}:s=1920x1080:d={total_dur}:r={fps}",
    ] + input_args + [
        "-filter_complex", filter_complex,
        "-map", "[vout]", "-map", "1:a",
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

    print(f"[lyric] Rendering lyric video: {title} ({total_dur:.1f}s)")
    t0 = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    elapsed = time.time() - t0

    if result.returncode != 0:
        print(f"[lyric] FFmpeg FAILED ({elapsed:.1f}s)")
        stderr_tail = result.stderr[-500:] if result.stderr else "no stderr"
        print(f"[lyric] stderr: {stderr_tail}")
        return False

    size = os.path.getsize(output_path) if os.path.isfile(output_path) else 0
    print(f"[lyric] SUCCESS: {output_path} ({size:,} bytes, {elapsed:.1f}s)")

    # Update manifest
    manifest.setdefault("outputs", {})["lyric_video"] = {
        "path": output_path,
        "size_bytes": size,
        "render_time_seconds": round(elapsed, 2),
        "lyric_lines": len(lyric_lines),
        "lrc_source": lrc_path or "placeholder",
    }
    try:
        with open(manifest_path, "w", encoding="utf-8") as fh:
            json.dump(manifest, fh, indent=2, ensure_ascii=False)
    except OSError as e:
        print(f"[lyric] WARNING: could not update manifest: {e}")

    return True


# ── CLI ──────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Render lyric overlay video.")
    parser.add_argument("--song-id", required=True)
    parser.add_argument("--artist", required=True)
    parser.add_argument("--project-root", default=PROJECT_ROOT_DEFAULT)
    parser.add_argument("--lrc", default=None, help="Path to .lrc lyric file")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    catalog_dir = os.path.join(args.project_root, "catalog", args.artist, args.song_id)
    manifest, manifest_path = load_manifest(catalog_dir)
    if manifest is None:
        sys.exit(1)

    ok = render_lyric_video(
        manifest, manifest_path, catalog_dir, args.project_root,
        lrc_path=args.lrc, force=args.force,
    )
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
