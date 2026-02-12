#!/usr/bin/env python3
"""render_pro_video.py — Pro-quality music video renderer.

Renders a cinematic music video with:
  - Real background image (upscaled, Ken Burns with direction changes)
  - Character overlays with energy-driven bounce
  - Beat-synced lyric overlay with fade-in/out per line
  - Warm color grading (golden reggae tones)
  - Cinematic vignette
  - Beat-triggered brightness bloom

Usage:
    python render_pro_video.py --song-id crazy --artist the_ridgemonts \
        --lrc /path/to/lyrics.lrc --bg /path/to/background.jpg
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
PROJECT_ROOT_DEFAULT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
sys.path.insert(0, SCRIPT_DIR)
from cache_utils import resolve_path

# ── Constants ──
MAX_ENERGY_SEGMENTS = 40
MAX_BLOOM_BEATS = 50


# ── LRC Parser ──
def parse_lrc(lrc_path, beat_times=None):
    """Parse an LRC file and optionally snap to beat grid."""
    lines = []
    with open(lrc_path, "r", encoding="utf-8") as f:
        for raw in f:
            m = re.match(r'\[(\d+):(\d+(?:\.\d+)?)\](.*)', raw.strip())
            if m:
                mm, ss, text = m.groups()
                t = int(mm) * 60 + float(ss)
                text = text.strip()
                if text:
                    # Snap to nearest beat if grid provided
                    if beat_times:
                        nearest = min(beat_times, key=lambda b: abs(b - t))
                        if abs(nearest - t) < 0.5:
                            t = nearest
                    lines.append((round(t, 2), text))
    return lines


# ── Energy Expression Builders (same adaptive approach as v2.1) ──
def _smooth_and_normalize(energy_curve):
    n = len(energy_curve)
    e_max = max(energy_curve) if max(energy_curve) > 0 else 1.0
    normed = [e / e_max for e in energy_curve]
    smoothed = []
    for i in range(n):
        lo, hi = max(0, i-1), min(n-1, i+1)
        smoothed.append(sum(normed[lo:hi+1]) / (hi - lo + 1))
    return smoothed


def build_energy_expr_frame(energy_curve, duration, intro_dur, fps, var_name="n"):
    if not energy_curve or duration <= 0:
        return "0.5"
    smoothed = _smooth_and_normalize(energy_curve)
    n_samples = len(energy_curve)
    total_seconds = max(1, int(math.ceil(duration)))
    step = max(1, math.ceil(total_seconds / MAX_ENERGY_SEGMENTS))
    n_steps = math.ceil(total_seconds / step)
    per_step = []
    for i in range(n_steps):
        mid_sec = i * step + step / 2.0
        frac = min(mid_sec / max(1, duration), 1.0)
        idx = min(int(frac * (n_samples - 1)), n_samples - 1)
        per_step.append(round(smoothed[idx], 3))
    intro_frames = int(intro_dur * fps)
    step_frames = step * fps
    expr = str(per_step[-1])
    for i in range(len(per_step) - 1, -1, -1):
        f_start = intro_frames + i * step_frames
        f_end = intro_frames + min((i + 1) * step, total_seconds) * fps
        val = per_step[i]
        if i + 1 < len(per_step):
            nv = per_step[i + 1]
            delta = round(nv - val, 4)
            span = f_end - f_start
            lerp = f"{val}+{delta}*({var_name}-{f_start})/{span}"
            expr = f"if(between({var_name},{f_start},{f_end}),{lerp},{expr})"
        else:
            expr = f"if(between({var_name},{f_start},{f_end}),{val},{expr})"
    return expr


def build_beat_bloom_expr(beat_times, intro_dur, bloom_strength=0.10,
                          decay_frames=6, fps=30, var_name="n"):
    if not beat_times:
        return "0"
    n_beats = len(beat_times)
    thin_step = max(1, math.ceil(n_beats / MAX_BLOOM_BEATS))
    thinned = beat_times[::thin_step]
    beat_frames = [int((bt + intro_dur) * fps) for bt in thinned]
    parts = [f"{bloom_strength}*max(0,1-({var_name}-{bf})/{decay_frames})*gte({var_name},{bf})"
             for bf in beat_frames]
    if len(parts) <= 1:
        return parts[0] if parts else "0"
    return f"min({bloom_strength},{'+'.join(parts)})"


# ── Lyric Drawtext Builder ──
def build_lyric_filters(lyric_lines, input_label, output_label,
                        font_size=42, fade_dur=0.4, line_gap=3.0):
    """Build drawtext filter chain for synced lyrics.

    Each lyric line fades in at its timestamp and fades out before the next line.
    Lyrics appear centered in the lower third with a semi-transparent backdrop.
    """
    if not lyric_lines:
        return f"[{input_label}]null[{output_label}]"

    filters = []
    n = len(lyric_lines)

    for i, (start_t, text) in enumerate(lyric_lines):
        # End time: either next line start or start + line_gap
        if i + 1 < n:
            end_t = lyric_lines[i + 1][0] - 0.1
        else:
            end_t = start_t + line_gap

        # Duration this line is visible
        visible_dur = end_t - start_t
        if visible_dur < 0.5:
            visible_dur = line_gap
            end_t = start_t + visible_dur

        # Escape text for FFmpeg drawtext
        esc = text.replace("\\", "\\\\").replace("'", "\u2019")
        esc = esc.replace(":", "\\:").replace("%", "%%")

        # Alpha fade: ramp up over fade_dur, hold, ramp down over fade_dur
        fade_in_end = start_t + fade_dur
        fade_out_start = end_t - fade_dur
        alpha_expr = (
            f"if(lt(t,{start_t}),0,"
            f"if(lt(t,{fade_in_end}),(t-{start_t})/{fade_dur},"
            f"if(lt(t,{fade_out_start}),1,"
            f"if(lt(t,{end_t}),({end_t}-t)/{fade_dur},"
            f"0))))"
        )

        # Build label chain
        in_lbl = input_label if i == 0 else f"_lyr{i-1}"
        out_lbl = output_label if i == n - 1 else f"_lyr{i}"

        # Shadow text (offset +2,+2, dark)
        shadow_filter = (
            f"[{in_lbl}]drawtext="
            f"text='{esc}':"
            f"fontsize={font_size}:fontcolor=0x000000:"
            f"alpha='{alpha_expr}'*0.6:"
            f"x=(w-text_w)/2+2:y=h*0.78+2:"
            f"enable='between(t,{start_t-0.1},{end_t+0.1})'[_shd{i}]"
        )
        # Main text (white with slight yellow tint)
        main_filter = (
            f"[_shd{i}]drawtext="
            f"text='{esc}':"
            f"fontsize={font_size}:fontcolor=0xFFF8E1:"
            f"alpha='{alpha_expr}':"
            f"x=(w-text_w)/2:y=h*0.78:"
            f"enable='between(t,{start_t-0.1},{end_t+0.1})'[{out_lbl}]"
        )
        filters.append(shadow_filter)
        filters.append(main_filter)

    return ";\n".join(filters)


# ── Main Render ──
def render_pro(song_id, artist_slug, lrc_path, bg_path, project_root):
    root = project_root
    catalog_dir = os.path.join(root, "catalog", artist_slug, song_id)
    manifest_path = os.path.join(catalog_dir, "manifest.json")

    with open(manifest_path, "r") as f:
        manifest = json.load(f)

    with open(os.path.join(root, "data", "baseline_recipe.json"), "r") as f:
        recipe = json.load(f)

    analysis = manifest["analysis"]
    duration = analysis["duration_seconds"]
    bpm = analysis["bpm"]
    energy_curve = analysis.get("energy_curve", [])
    beat_times = analysis.get("beat_times", [])

    v = recipe["video"]
    W, H, FPS = v["width"], v["height"], v["fps"]
    timing = recipe["timing"]
    intro_dur = timing["intro_duration_seconds"]
    endcard_dur = timing["endcard_duration_seconds"]
    total_dur = duration + intro_dur + endcard_dur
    total_frames = int(total_dur * FPS)
    beat_period_frames = max(1, int(FPS * 60.0 / bpm))

    # Audio path
    audio_path = manifest.get("source_audio", "")
    if not os.path.isabs(audio_path):
        audio_path = os.path.join(root, audio_path)

    # Character paths
    chars_base = os.path.join(root, "assets", "characters")
    weeter_pose = os.path.join(chars_base, manifest["characters"]["weeter"]["pose_path"])
    blubby_pose = os.path.join(chars_base, manifest["characters"]["blubby"]["pose_path"])

    # Parse lyrics
    lyric_lines = parse_lrc(lrc_path, beat_times)
    print(f"[pro] Parsed {len(lyric_lines)} synced lyric lines")

    # ── Step 1: Upscale background ──
    # Upscale just enough for zoompan headroom (1.5x output res)
    up_w = int(W * 1.5)
    up_h = int(H * 1.5)
    bg_upscaled = os.path.join(catalog_dir, "_bg_upscaled.png")
    print(f"[pro] Upscaling background to {up_w}x{up_h} ...")
    subprocess.run([
        "ffmpeg", "-y", "-i", bg_path,
        "-vf", f"scale={up_w}:{up_h}:flags=lanczos",
        "-frames:v", "1", bg_upscaled
    ], capture_output=True, text=True)

    # ── Build energy expressions ──
    energy_frame_expr = build_energy_expr_frame(
        energy_curve, duration, intro_dur, FPS, var_name="n")
    energy_zoom_expr = build_energy_expr_frame(
        energy_curve, duration, intro_dur, FPS, var_name="on")

    # ── Build beat bloom ──
    bloom_expr = build_beat_bloom_expr(
        beat_times, intro_dur, bloom_strength=0.10, decay_frames=6, fps=FPS, var_name="n")

    # ── Character dimensions ──
    char_h_px = int(H * 0.35)
    char_y_base = int(H * 0.55)
    weeter_x = int(W * 0.15)
    blubby_x = int(W * 0.62)
    bounce_min, bounce_max = 3, 18
    bounce_range = bounce_max - bounce_min

    # ── Ken Burns with direction changes ──
    # Split into 4 phases: pan right, zoom in, pan left, zoom out
    cycle_s = 6.0  # Faster cycle for more motion
    zp_period = int(FPS * cycle_s)
    zoom_mid = 1.05
    zoom_amp = 0.08  # More dramatic zoom range
    energy_zoom_boost = 0.06

    zoom_expr = (
        f"({zoom_mid}+{zoom_amp}*sin(2*PI*on/{zp_period})"
        f"+{energy_zoom_boost}*({energy_zoom_expr}))"
    )
    # Pan X: slow drift left-right synced to zoom cycle (phase offset)
    pan_amp_x = 40  # pixels of pan range (conservative for 1.5x upscale)
    pan_x_expr = f"(iw/2-iw/zoom/2+{pan_amp_x}*sin(2*PI*on/{zp_period}+PI/3))"
    # Pan Y: gentle vertical drift
    pan_amp_y = 25
    pan_y_expr = f"(ih/2-ih/zoom/2+{pan_amp_y}*sin(2*PI*on/{int(zp_period*1.7)}))"

    filters = []

    # ── [0] Background: zoompan with dynamic pan ──
    filters.append(
        f"[0:v]loop=loop={total_frames}:size=1:start=0,"
        f"zoompan=z='{zoom_expr}':"
        f"x='{pan_x_expr}':y='{pan_y_expr}':"
        f"d={total_frames}:s={W}x{H}:fps={FPS},"
        f"setpts=PTS-STARTPTS,"
        f"format=rgba[bg_raw]"
    )

    # ── Beat bloom on background ──
    if beat_times:
        filters.append(f"[bg_raw]eq=brightness='{bloom_expr}'[bg_bloom]")
    else:
        filters.append("[bg_raw]null[bg_bloom]")

    # ── Color grading: warm golden reggae tones ──
    # Boost reds/yellows in midtones, lift shadows, add warmth
    filters.append(
        "[bg_bloom]colorbalance="
        "rs=0.08:gs=-0.02:bs=-0.10:"    # shadows: warm
        "rm=0.10:gm=0.02:bm=-0.08:"     # midtones: golden
        "rh=0.05:gh=0.03:bh=-0.05,"     # highlights: warm
        "eq=saturation=1.15:contrast=1.05:brightness=0.02,"
        "vignette=PI/4:0.4[bg]"          # cinematic vignette
    )

    # ── [1] Weeter ──
    filters.append(
        f"[1:v]scale=-1:{char_h_px},"
        f"loop=loop={total_frames}:size=1:start=0,"
        f"setpts=PTS-STARTPTS,"
        f"format=rgba[weeter_raw]"
    )

    # ── [2] Blubby ──
    filters.append(
        f"[2:v]scale=-1:{char_h_px},"
        f"loop=loop={total_frames}:size=1:start=0,"
        f"setpts=PTS-STARTPTS,"
        f"format=rgba[blubby_raw]"
    )

    # ── Overlay Weeter with energy bounce ──
    weeter_bounce = (
        f"({bounce_min}+{bounce_range}*({energy_frame_expr}))"
        f"*abs(sin(2*PI*n/{beat_period_frames}))"
    )
    # Add gentle horizontal sway
    weeter_sway = f"{int(W*0.01)}*sin(2*PI*n/{FPS*3})"
    filters.append(
        f"[bg][weeter_raw]overlay="
        f"x='{weeter_x}+{weeter_sway}':"
        f"y='{char_y_base}-({weeter_bounce})':"
        f"format=auto:shortest=0[with_weeter]"
    )

    # ── Overlay Blubby with energy bounce (phase offset) ──
    blubby_bounce = (
        f"({bounce_min}+{bounce_range}*({energy_frame_expr}))"
        f"*abs(sin(2*PI*n/{beat_period_frames}+PI/4))"
    )
    blubby_sway = f"{int(W*0.01)}*sin(2*PI*n/{FPS*4}+PI/2)"
    filters.append(
        f"[with_weeter][blubby_raw]overlay="
        f"x='{blubby_x}+{blubby_sway}':"
        f"y='{char_y_base}-({blubby_bounce})':"
        f"format=auto:shortest=0[with_chars]"
    )

    # ── Title text ──
    artist = manifest.get("artist", "Unknown")
    title = manifest.get("title", "Unknown")
    artist_esc = artist.replace("'", "\u2019").replace(":", "\\:")
    title_esc = title.replace("'", "\u2019").replace(":", "\\:")
    title_fs = 52
    sub_fs = 34
    # Title fades out after intro
    title_fade_end = intro_dur + 8
    title_alpha = (
        f"if(lt(t,{intro_dur}),t/{intro_dur},"
        f"if(lt(t,{title_fade_end}),1,"
        f"if(lt(t,{title_fade_end+2}),({title_fade_end+2}-t)/2,0)))"
    )
    filters.append(
        f"[with_chars]drawtext="
        f"text='{title_esc}':"
        f"fontsize={title_fs}:fontcolor=0xFFFFFF:"
        f"alpha='{title_alpha}':"
        f"x=(w-text_w)/2:y=h*0.10,"
        f"drawtext="
        f"text='{artist_esc}':"
        f"fontsize={sub_fs}:fontcolor=0xFFD700:"
        f"alpha='{title_alpha}':"
        f"x=(w-text_w)/2:y=h*0.10+{title_fs}+8"
        f"[titled]"
    )

    # ── Lyric overlay ──
    lyric_filter = build_lyric_filters(
        lyric_lines, "titled", "with_lyrics",
        font_size=44, fade_dur=0.35
    )
    filters.append(lyric_filter)

    # ── Lower-third gradient bar behind lyrics (semi-transparent) ──
    # Draw a dark gradient bar at 70-90% height for readability
    bar_y = int(H * 0.72)
    bar_h = int(H * 0.18)
    # Only show when lyrics are active
    first_lyric_t = lyric_lines[0][0] if lyric_lines else 5
    last_lyric_t = lyric_lines[-1][0] + 4 if lyric_lines else 120
    filters.append(
        f"[with_lyrics]drawbox="
        f"x=0:y={bar_y}:w={W}:h={bar_h}:"
        f"color=0x000000@0.35:t=fill:"
        f"enable='between(t,{first_lyric_t-0.5},{last_lyric_t})'[with_bar]"
    )

    # ── Fade in/out + final format ──
    fade_in = timing["fade_in_seconds"]
    fade_out_start = total_dur - timing["fade_out_seconds"]
    filters.append(
        f"[with_bar]fade=t=in:st=0:d={fade_in},"
        f"fade=t=out:st={fade_out_start}:d={timing['fade_out_seconds']},"
        f"format={v['pixel_format']}[vout]"
    )

    # ── Audio ──
    filters.append(
        f"[3:a]adelay={int(intro_dur*1000)}|{int(intro_dur*1000)},"
        f"afade=t=in:st={intro_dur}:d={fade_in},"
        f"afade=t=out:st={intro_dur+duration-timing['fade_out_seconds']}:"
        f"d={timing['fade_out_seconds']}[aout]"
    )

    filter_complex = ";\n".join(filters)

    # ── Output ──
    output_path = os.path.join(catalog_dir, f"{artist_slug}_{song_id}_pro.mp4")

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", bg_upscaled,    # [0] background
        "-i", weeter_pose,                    # [1] weeter
        "-i", blubby_pose,                    # [2] blubby
        "-i", audio_path,                     # [3] audio
        "-filter_complex", filter_complex,
        "-map", "[vout]", "-map", "[aout]",
        "-c:v", v["codec"],
        "-preset", "ultrafast",
        "-crf", "28",
        "-pix_fmt", v["pixel_format"],
        "-c:a", recipe["audio"]["codec"],
        "-b:a", recipe["audio"]["bitrate"],
        "-ar", str(recipe["audio"]["sample_rate"]),
        "-t", str(total_dur),
        "-movflags", "+faststart",
        output_path
    ]

    total_secs = max(1, int(math.ceil(duration)))
    e_step = max(1, math.ceil(total_secs / MAX_ENERGY_SEGMENTS))
    b_thin = max(1, math.ceil(len(beat_times) / MAX_BLOOM_BEATS))

    print(f"\n{'='*65}")
    print(f"[pro] PRO RENDER: \"{title}\" by {artist}")
    print(f"{'='*65}")
    print(f"[pro] Resolution: {W}x{H} @ {FPS}fps")
    print(f"[pro] Duration: {total_dur:.1f}s  |  BPM: {bpm}")
    print(f"[pro] Background: {bg_path} (upscaled to {W*2}x{H*2})")
    print(f"[pro] Ken Burns: zoom {zoom_mid}±{zoom_amp}, {cycle_s}s cycles, xy-pan")
    print(f"[pro] Energy: {len(energy_curve)} samples → {math.ceil(total_secs/e_step)} segments")
    print(f"[pro] Beat bloom: {len(beat_times)} → {len(beat_times[::b_thin])} beats")
    print(f"[pro] Lyrics: {len(lyric_lines)} lines synced to beat grid")
    print(f"[pro] Color grading: warm golden + vignette")
    print(f"[pro] Characters: energy bounce + horizontal sway")
    print(f"{'='*65}\n")

    print("[pro] Executing FFmpeg (this will take several minutes)...")
    start = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    elapsed = round(time.time() - start, 2)

    if result.returncode != 0:
        print(f"[pro] FFmpeg FAILED (exit {result.returncode})")
        err_lines = result.stderr.strip().split("\n")
        for line in err_lines[-20:]:
            print(f"  {line}")
        return None

    size = os.path.getsize(output_path) if os.path.isfile(output_path) else 0
    print(f"\n{'='*65}")
    print(f"[pro] RENDER COMPLETE")
    print(f"{'='*65}")
    print(f"  Output:  {output_path}")
    print(f"  Size:    {size:,} bytes ({size/1048576:.1f} MB)")
    print(f"  Render:  {elapsed}s ({elapsed/60:.1f} min)")
    print(f"{'='*65}\n")

    # Cleanup
    try:
        os.remove(bg_upscaled)
    except OSError:
        pass

    return output_path


def main():
    parser = argparse.ArgumentParser(description="Pro music video renderer")
    parser.add_argument("--song-id", required=True)
    parser.add_argument("--artist", required=True)
    parser.add_argument("--lrc", required=True, help="Path to LRC lyrics file")
    parser.add_argument("--bg", required=True, help="Path to background image")
    parser.add_argument("--project-root", default=None)
    args = parser.parse_args()

    root = args.project_root or PROJECT_ROOT_DEFAULT
    lrc_path = resolve_path(args.lrc, root)
    bg_path = resolve_path(args.bg, root)
    result = render_pro(args.song_id, args.artist, lrc_path, bg_path, root)
    if not result:
        print("[pro] FAILED")
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
