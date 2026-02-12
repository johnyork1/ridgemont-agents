#!/usr/bin/env python3
"""baseline_master.py - Step 3 of the Make Videos pipeline (v2: Audio-Reactive).

Renders an audio-reactive Ken Burns master video (1920x1080) from a fully analyzed manifest.

v2 UPGRADES (Audio-Reactive "Awesome Protocol"):
  1. Energy-Driven Bounce: Character bounce amplitude scales 3-18px with energy_curve
  2. Energy-Driven Zoom: Ken Burns zoom range pulses wider during high-energy sections
  3. Beat-Triggered Bloom: Background brightness pulses on each beat via eq filter

The energy_curve (100 samples) is encoded as a piecewise-linear FFmpeg expression
function, giving per-second interpolation of the song's loudness envelope.

Usage:
    python baseline_master.py --song-id crazy --artist the_ridgemonts
    python baseline_master.py --song-id crazy --artist the_ridgemonts --project-root /path
"""
import argparse
import json
import math
import os
import subprocess
import sys
import time

# Local imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
PROJECT_ROOT_DEFAULT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

from cache_utils import load_cache, save_cache, get_default_cache_path
from render_signature import generate_signature


# ── Config Loaders ───────────────────────────────────────────

def load_recipe(project_root):
    """Load baseline_recipe.json."""
    path = os.path.join(project_root, "data", "baseline_recipe.json")
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def load_animation_constants(project_root):
    """Load animation_constants from mood_map.json."""
    path = os.path.join(project_root, "data", "mood_map.json")
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    return data.get("animation_constants", {})


def load_manifest(catalog_dir):
    """Load and validate manifest.json from a catalog song directory."""
    path = os.path.join(catalog_dir, "manifest.json")
    if not os.path.isfile(path):
        print(f"[render] ERROR: manifest.json not found at {path}")
        return None, path
    with open(path, "r", encoding="utf-8") as fh:
        manifest = json.load(fh)
    if manifest.get("pipeline_stage") not in ("analyzed", "rendered"):
        print(f"[render] ERROR: pipeline_stage is '{manifest.get('pipeline_stage')}', expected 'analyzed'.")
        print(f"[render]        Run analyze_catalog.py first.")
        return None, path
    return manifest, path


# ── Energy Curve → FFmpeg Expression ─────────────────────────

def _smooth_and_normalize(energy_curve):
    """Normalize to 0-1 and apply 3-point moving average."""
    n = len(energy_curve)
    e_max = max(energy_curve) if max(energy_curve) > 0 else 1.0
    normed = [e / e_max for e in energy_curve]
    smoothed = []
    for i in range(n):
        lo = max(0, i - 1)
        hi = min(n - 1, i + 1)
        smoothed.append(sum(normed[lo:hi + 1]) / (hi - lo + 1))
    return smoothed


# Maximum number of piecewise conditions to keep under FFmpeg nesting limit
_MAX_ENERGY_SEGMENTS = 40


def build_energy_expr(energy_curve, duration, intro_dur, var_name="t"):
    """Convert a 100-sample energy_curve into a piecewise-linear FFmpeg expression.

    Returns an expression string that, given time variable `var_name`,
    evaluates to the interpolated energy value (0.0-1.0) at that time.

    Adaptively downsamples so the total number of segments never exceeds
    _MAX_ENERGY_SEGMENTS (~40), keeping well under FFmpeg's ~100-level
    nesting limit for expressions.
    """
    if not energy_curve or duration <= 0:
        return "0.5"  # Fallback: constant mid-energy

    n_samples = len(energy_curve)
    smoothed = _smooth_and_normalize(energy_curve)

    # Adaptive interval: pick seconds_per_step so total segments <= _MAX_ENERGY_SEGMENTS
    total_seconds = max(1, int(math.ceil(duration)))
    step = max(1, math.ceil(total_seconds / _MAX_ENERGY_SEGMENTS))
    n_steps = math.ceil(total_seconds / step)

    # Sample one value per step
    per_step = []
    for i in range(n_steps):
        mid_sec = i * step + step / 2.0  # sample at midpoint of each bucket
        frac = min(mid_sec / max(1, duration), 1.0)
        idx = min(int(frac * (n_samples - 1)), n_samples - 1)
        per_step.append(round(smoothed[idx], 3))

    # Build piecewise expression: if(between(t, start, end), lerp, fallback)
    expr = str(per_step[-1])
    for i in range(len(per_step) - 1, -1, -1):
        t_start = round(i * step + intro_dur, 2)
        t_end = round(min((i + 1) * step, total_seconds) + intro_dur, 2)
        val = per_step[i]
        if i + 1 < len(per_step):
            next_val = per_step[i + 1]
            delta = round(next_val - val, 4)
            span = round(t_end - t_start, 2)
            lerp = f"{val}+{delta}*({var_name}-{t_start})/{span}"
            expr = f"if(between({var_name},{t_start},{t_end}),{lerp},{expr})"
        else:
            expr = f"if(between({var_name},{t_start},{t_end}),{val},{expr})"

    return expr


def build_energy_expr_frame(energy_curve, duration, intro_dur, fps, var_name="n"):
    """Build energy expression using frame number instead of time.

    For use in overlay/zoompan where 'n' (frame number) is available but 't' is not.
    Adaptively downsamples so segments never exceed _MAX_ENERGY_SEGMENTS.
    """
    if not energy_curve or duration <= 0:
        return "0.5"

    n_samples = len(energy_curve)
    smoothed = _smooth_and_normalize(energy_curve)

    # Adaptive interval
    total_seconds = max(1, int(math.ceil(duration)))
    step = max(1, math.ceil(total_seconds / _MAX_ENERGY_SEGMENTS))
    n_steps = math.ceil(total_seconds / step)

    per_step = []
    for i in range(n_steps):
        mid_sec = i * step + step / 2.0
        frac = min(mid_sec / max(1, duration), 1.0)
        idx = min(int(frac * (n_samples - 1)), n_samples - 1)
        per_step.append(round(smoothed[idx], 3))

    # Build piecewise expression using frame ranges
    intro_frames = int(intro_dur * fps)
    step_frames = step * fps
    expr = str(per_step[-1])
    for i in range(len(per_step) - 1, -1, -1):
        f_start = intro_frames + i * step_frames
        f_end = intro_frames + min((i + 1) * step, total_seconds) * fps
        val = per_step[i]
        if i + 1 < len(per_step):
            next_val = per_step[i + 1]
            delta = round(next_val - val, 4)
            span_frames = f_end - f_start
            lerp = f"{val}+{delta}*({var_name}-{f_start})/{span_frames}"
            expr = f"if(between({var_name},{f_start},{f_end}),{lerp},{expr})"
        else:
            expr = f"if(between({var_name},{f_start},{f_end}),{val},{expr})"

    return expr


# Maximum beat terms in bloom expression to avoid FFmpeg expression size limits
_MAX_BLOOM_BEATS = 50


def build_beat_bloom_expr(beat_times, intro_dur, bloom_strength=0.12, decay_frames=6,
                          fps=30, var_name="n"):
    """Build an expression for beat-triggered brightness bloom.

    Returns an FFmpeg expression evaluating to a brightness boost (0.0-bloom_strength)
    that spikes on selected beats and decays over decay_frames frames.

    Adaptively thins beats so the total number of terms never exceeds
    _MAX_BLOOM_BEATS (~50), preventing enormous FFmpeg expressions.
    """
    if not beat_times:
        return "0"

    # Thin beats: keep every Nth so total <= _MAX_BLOOM_BEATS
    n_beats = len(beat_times)
    thin_step = max(1, math.ceil(n_beats / _MAX_BLOOM_BEATS))
    thinned = beat_times[::thin_step]

    # Convert thinned beat times to frame numbers (offset by intro)
    beat_frames = [int((bt + intro_dur) * fps) for bt in thinned]

    parts = []
    for bf in beat_frames:
        part = f"{bloom_strength}*max(0,1-({var_name}-{bf})/{decay_frames})*gte({var_name},{bf})"
        parts.append(part)

    if len(parts) <= 1:
        return parts[0] if parts else "0"

    # Sum all contributions, clamped to bloom_strength
    combined = "+".join(parts)
    return f"min({bloom_strength},{combined})"


# ── Background Generator ─────────────────────────────────────

def generate_background(audio_path, width, height, duration, blur_radius,
                        darken, output_path):
    """Generate a background frame."""
    print("[render] Generating background frame...")
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i",
        f"color=c=0x1a1a2e:s={width}x{height}:d=1,format=rgb24",
        "-frames:v", "1",
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[render] WARNING: Background generation failed: {result.stderr[:200]}")
        return False
    print(f"[render] Background: {output_path}")
    return True


# ── FFmpeg Filter Graph Builder (v2: Audio-Reactive) ─────────

def build_filter_graph(manifest, recipe, anim_constants, project_root, bg_path):
    """Build the FFmpeg filter graph string for the master video.

    v2 Audio-Reactive upgrades:
      - Character bounce amplitude driven by energy_curve (3-18px range)
      - Ken Burns zoom range modulated by energy (wider zoom at high energy)
      - Background brightness bloom on each beat

    Returns:
        tuple (filter_complex: str, input_files: list, total_dur: float)
    """
    v = recipe["video"]
    w, h = v["width"], v["height"]
    fps = v["fps"]
    comp = recipe["composition"]
    kb = recipe["ken_burns"]
    timing = recipe["timing"]
    analysis = manifest["analysis"]
    duration = analysis["duration_seconds"]
    intro_dur = timing["intro_duration_seconds"]
    endcard_dur = timing["endcard_duration_seconds"]
    total_dur = duration + intro_dur + endcard_dur

    # Energy data
    energy_curve = analysis.get("energy_curve", [])
    beat_times = analysis.get("beat_times", [])

    # Ken Burns parameters
    zoom_start, zoom_end = kb["zoom_range"]
    cycle_s = kb["cycle_seconds"]
    total_frames = int(total_dur * fps)

    # Animation constants
    breathe_cycle = anim_constants.get("breathe_cycle_seconds", 2.0)
    breathe_lo, breathe_hi = anim_constants.get("breathe_scale_range", [0.98, 1.02])
    bounce_lo, bounce_hi = anim_constants.get("beat_bounce_px", [5, 10])

    # v2: Dynamic bounce range driven by energy
    bounce_min = 3    # quiet sections
    bounce_max = 18   # peak energy sections

    # Character positioning
    char_max_h = comp["character_max_height_pct"]
    char_bottom_margin = comp["character_bottom_margin_pct"]
    char_h_px = int(h * char_max_h)
    char_y_base = int(h * (1.0 - char_bottom_margin) - char_h_px)

    weeter_x = int(w * 0.18)
    blubby_x = int(w * 0.62)

    # Character paths
    chars_base = os.path.join(project_root, "assets", "characters")
    weeter_pose = os.path.join(chars_base, manifest["characters"]["weeter"]["pose_path"])
    blubby_pose = os.path.join(chars_base, manifest["characters"]["blubby"]["pose_path"])

    # Audio path
    audio_path = manifest.get("source_audio", "")
    if not os.path.isabs(audio_path):
        audio_path = os.path.join(project_root, audio_path)

    input_files = [bg_path, weeter_pose, blubby_pose, audio_path]

    # ── Build energy expressions ──
    energy_frame_expr = build_energy_expr_frame(
        energy_curve, duration, intro_dur, fps, var_name="n"
    )
    energy_time_expr = build_energy_expr(
        energy_curve, duration, intro_dur, var_name="t"
    )

    # ── Build beat bloom expression ──
    bloom_expr = build_beat_bloom_expr(
        beat_times, intro_dur,
        bloom_strength=0.12, decay_frames=6, fps=fps, var_name="n"
    )

    # Zoom parameters
    zoom_amp = (zoom_end - zoom_start) / 2.0
    zoom_mid = zoom_start + zoom_amp
    zp_period = int(fps * cycle_s)

    # v2: Energy-modulated zoom: base zoom cycle + energy boost (0-0.05 extra)
    # zoom = base_cycle + energy * 0.05
    energy_zoom_boost = 0.05

    bpm = analysis.get("bpm", 100)
    beat_period_frames = max(1, int(fps * 60.0 / bpm))

    filters = []

    # ── [0] Background → zoompan with energy-modulated zoom ──
    # v2: zoom = base_sinusoidal + energy * boost
    # The energy expression uses 'on' (output frame number) in zoompan
    energy_zoom_expr = build_energy_expr_frame(
        energy_curve, duration, intro_dur, fps, var_name="on"
    )
    zoom_expr = (
        f"({zoom_mid}+{zoom_amp}*sin(2*PI*on/{zp_period})"
        f"+{energy_zoom_boost}*({energy_zoom_expr}))"
    )
    filters.append(
        f"[0:v]loop=loop={total_frames}:size=1:start=0,"
        f"zoompan=z='{zoom_expr}':"
        f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
        f"d={total_frames}:s={w}x{h}:fps={fps},"
        f"setpts=PTS-STARTPTS,"
        f"format=rgba[bg_raw]"
    )

    # v2: Beat bloom — brightness pulse on each beat
    # eq filter: brightness is baseline + bloom_expr
    if beat_times:
        bloom_time_expr = build_beat_bloom_expr(
            beat_times, intro_dur,
            bloom_strength=0.12, decay_frames=6, fps=fps, var_name="n"
        )
        # Use eq filter for brightness modulation
        # brightness range: -1.0 to 1.0, we add a small bloom
        filters.append(
            f"[bg_raw]eq=brightness='{bloom_time_expr}'[bg]"
        )
    else:
        filters.append("[bg_raw]null[bg]")

    # ── [1] Weeter: scale to character height ──
    filters.append(
        f"[1:v]scale=-1:{char_h_px},"
        f"loop=loop={total_frames}:size=1:start=0,"
        f"setpts=PTS-STARTPTS,"
        f"format=rgba[weeter_raw]"
    )

    # ── [2] Blubby: same treatment ──
    filters.append(
        f"[2:v]scale=-1:{char_h_px},"
        f"loop=loop={total_frames}:size=1:start=0,"
        f"setpts=PTS-STARTPTS,"
        f"format=rgba[blubby_raw]"
    )

    # ── Overlay Weeter with energy-driven bounce ──
    # v2: bounce_amplitude = bounce_min + (bounce_max - bounce_min) * energy(n)
    bounce_range = bounce_max - bounce_min
    weeter_bounce = (
        f"({bounce_min}+{bounce_range}*({energy_frame_expr}))"
        f"*abs(sin(2*PI*n/{beat_period_frames}))"
    )
    filters.append(
        f"[bg][weeter_raw]overlay="
        f"x={weeter_x}:"
        f"y='{char_y_base}-({weeter_bounce})':"
        f"format=auto:shortest=0[with_weeter]"
    )

    # Blubby: same energy-driven bounce with PI/4 phase offset
    blubby_bounce = (
        f"({bounce_min}+{bounce_range}*({energy_frame_expr}))"
        f"*abs(sin(2*PI*n/{beat_period_frames}+PI/4))"
    )
    filters.append(
        f"[with_weeter][blubby_raw]overlay="
        f"x={blubby_x}:"
        f"y='{char_y_base}-({blubby_bounce})':"
        f"format=auto:shortest=0[with_chars]"
    )

    # ── Title drawtext ──
    artist = manifest.get("artist", "Unknown Artist")
    title = manifest.get("title", "Unknown Song")
    artist_esc = artist.replace("'", "\\'").replace(":", "\\:")
    title_esc = title.replace("'", "\\'").replace(":", "\\:")

    title_fs = comp.get("title_font_size", 48)
    sub_fs = comp.get("subtitle_font_size", 32)
    fade_in = timing["fade_in_seconds"]

    filters.append(
        f"[with_chars]drawtext="
        f"text='{title_esc}':"
        f"fontsize={title_fs}:fontcolor=white:"
        f"x=(w-text_w)/2:y=(h*0.12):"
        f"enable='between(t,0,{intro_dur + duration})',"
        f"drawtext="
        f"text='{artist_esc}':"
        f"fontsize={sub_fs}:fontcolor=0xCCCCCC:"
        f"x=(w-text_w)/2:y=(h*0.12+{title_fs}+10):"
        f"enable='between(t,0,{intro_dur + duration})'[titled]"
    )

    # ── Fade in/out ──
    fade_out_start = total_dur - timing["fade_out_seconds"]
    filters.append(
        f"[titled]fade=t=in:st=0:d={fade_in},"
        f"fade=t=out:st={fade_out_start}:d={timing['fade_out_seconds']},"
        f"format={v['pixel_format']}[vout]"
    )

    # ── Audio: pad with silence for intro, add fade ──
    filters.append(
        f"[3:a]adelay={int(intro_dur * 1000)}|{int(intro_dur * 1000)},"
        f"afade=t=in:st={intro_dur}:d={fade_in},"
        f"afade=t=out:st={intro_dur + duration - timing['fade_out_seconds']}:"
        f"d={timing['fade_out_seconds']}[aout]"
    )

    filter_complex = ";\n".join(filters)

    # Log reactive stats
    total_secs = max(1, int(math.ceil(duration)))
    e_step = max(1, math.ceil(total_secs / _MAX_ENERGY_SEGMENTS))
    b_thin = max(1, math.ceil(len(beat_times) / _MAX_BLOOM_BEATS))
    print(f"[render] v2.1 AUDIO-REACTIVE mode enabled:")
    print(f"[render]   Energy curve: {len(energy_curve)} samples → {math.ceil(total_secs/e_step)} segments ({e_step}s intervals)")
    print(f"[render]   Bounce range: {bounce_min}-{bounce_max}px (energy-scaled)")
    print(f"[render]   Zoom boost: +{energy_zoom_boost} at peak energy")
    print(f"[render]   Beat bloom: {len(beat_times)} beats → {len(beat_times[::b_thin])} used (every {b_thin}), 0.12 brightness, 6-frame decay")

    return filter_complex, input_files, total_dur


# ── Render Execution ─────────────────────────────────────────

def render_master(manifest, recipe, anim_constants, project_root,
                  catalog_dir, output_path, bg_path):
    """Execute the FFmpeg render for the master video."""
    v = recipe["video"]

    filter_complex, input_files, total_dur = build_filter_graph(
        manifest, recipe, anim_constants, project_root, bg_path
    )

    print(f"[render] Building master video: {v['width']}x{v['height']} @ {v['fps']}fps")
    print(f"[render] Total duration: {total_dur:.1f}s (intro + audio + endcard)")
    print(f"[render] Ken Burns: {recipe['ken_burns']['zoom_range']} over {recipe['ken_burns']['cycle_seconds']}s cycles")
    print(f"[render] Characters: Weeter + Blubby with energy-reactive bounce @ {manifest['analysis']['bpm']} BPM")

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", input_files[0],
        "-i", input_files[1],
        "-i", input_files[2],
        "-i", input_files[3],
        "-filter_complex", filter_complex,
        "-map", "[vout]", "-map", "[aout]",
        "-c:v", v["codec"],
        "-preset", v.get("preset", "medium"),
        "-crf", str(v["crf"]),
        "-pix_fmt", v["pixel_format"],
        "-c:a", recipe["audio"]["codec"],
        "-b:a", recipe["audio"]["bitrate"],
        "-ar", str(recipe["audio"]["sample_rate"]),
        "-t", str(total_dur),
        "-movflags", "+faststart",
        output_path
    ]

    print(f"[render] Executing FFmpeg (v2 audio-reactive)...")
    start = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    elapsed = round(time.time() - start, 2)

    if result.returncode != 0:
        print(f"[render] FFmpeg FAILED (exit {result.returncode})")
        err_lines = result.stderr.strip().split("\n")
        for line in err_lines[-15:]:
            print(f"  {line}")
        return False, output_path, elapsed

    size = os.path.getsize(output_path) if os.path.isfile(output_path) else 0
    print(f"[render] SUCCESS: {output_path}")
    print(f"[render] Size: {size:,} bytes  |  Elapsed: {elapsed}s")
    return True, output_path, elapsed


# ── Manifest & Cache Update ──────────────────────────────────

def update_manifest_rendered(manifest_path, manifest, output_path,
                             render_elapsed, project_root):
    """Update manifest.json with render output info."""
    audio_path = manifest.get("source_audio", "")
    if not os.path.isabs(audio_path):
        audio_path = os.path.join(project_root, audio_path)

    sig = generate_signature(audio_path, manifest_path)

    manifest["pipeline_stage"] = "rendered"
    manifest["render_signature"] = sig
    manifest["rendered_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    manifest.setdefault("outputs", {})["master"] = {
        "path": output_path,
        "format": "mp4",
        "resolution": "1920x1080",
        "render_time_seconds": render_elapsed,
        "render_version": "v2-audio-reactive",
    }

    tmp = manifest_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)
        fh.write("\n")
        fh.flush()
        os.fsync(fh.fileno())
    os.rename(tmp, manifest_path)
    print(f"[render] Manifest updated: pipeline_stage → rendered, signature: {sig}")


def update_cache_rendered(project_root, artist_slug, song_id):
    """Update catalog cache with rendered status."""
    cache_path = get_default_cache_path(project_root)
    cache = load_cache(cache_path)
    key = f"{artist_slug}::{song_id}"
    if key in cache:
        cache[key]["pipeline_stage"] = "rendered"
        cache[key]["rendered_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        save_cache(cache_path, cache)
        print(f"[render] Cache updated: {key} → rendered")


# ── Main Pipeline ────────────────────────────────────────────

def render_song(song_id, artist_slug, project_root=None):
    """Render the master video for an analyzed song."""
    root = project_root or PROJECT_ROOT_DEFAULT
    catalog_dir = os.path.join(root, "catalog", artist_slug, song_id)

    manifest, manifest_path = load_manifest(catalog_dir)
    if not manifest:
        return None

    recipe = load_recipe(root)
    anim_constants = load_animation_constants(root)

    artist = manifest.get("artist", artist_slug)
    title = manifest.get("title", song_id)

    print(f"\n{'='*60}")
    print(f"[render] RENDERING (v2 AUDIO-REACTIVE): \"{title}\" by {artist}")
    print(f"[render] Format: master (1920x1080)")
    print(f"{'='*60}\n")

    # Generate background
    bg_path = os.path.join(catalog_dir, "_bg_frame.png")
    if not generate_background(
        manifest.get("source_audio", ""),
        recipe["video"]["width"], recipe["video"]["height"],
        manifest["analysis"]["duration_seconds"],
        recipe["composition"]["background_blur_radius"],
        recipe["composition"]["background_darken_factor"],
        bg_path
    ):
        print("[render] FATAL: Could not generate background.")
        return None

    output_filename = f"{artist_slug}_{song_id}_master.mp4"
    output_path = os.path.join(catalog_dir, output_filename)

    success, final_path, elapsed = render_master(
        manifest, recipe, anim_constants, root,
        catalog_dir, output_path, bg_path
    )

    if not success:
        return None

    update_manifest_rendered(manifest_path, manifest, output_path, elapsed, root)
    update_cache_rendered(root, artist_slug, song_id)

    try:
        os.remove(bg_path)
    except OSError:
        pass

    result = {
        "output_path": final_path,
        "render_time": elapsed,
        "resolution": f"{recipe['video']['width']}x{recipe['video']['height']}",
        "duration": manifest["analysis"]["duration_seconds"],
        "render_version": "v2-audio-reactive",
    }

    print(f"\n{'='*60}")
    print(f"[render] RENDER COMPLETE (v2): \"{title}\" by {artist}")
    print(f"{'='*60}")
    print(f"  Output:     {final_path}")
    print(f"  Resolution: {result['resolution']}")
    print(f"  Duration:   {result['duration']:.1f}s")
    print(f"  Render:     {elapsed}s")
    print(f"  Version:    v2-audio-reactive")
    print(f"{'='*60}\n")

    return result


# ── CLI ──────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Render a Ken Burns master video (Step 3 - v2 Audio-Reactive)."
    )
    parser.add_argument("--song-id", required=True,
                        help="Song slug (catalog directory name)")
    parser.add_argument("--artist", required=True,
                        help="Artist slug (catalog directory name)")
    parser.add_argument("--project-root", default=None,
                        help="Project root directory (default: parent of scripts/)")
    args = parser.parse_args()

    root = args.project_root or PROJECT_ROOT_DEFAULT
    result = render_song(args.song_id, args.artist, root)
    if result is None:
        print("[render] FAILED: Render did not complete.")
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
