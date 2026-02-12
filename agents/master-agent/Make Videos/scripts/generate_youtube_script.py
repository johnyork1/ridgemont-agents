#!/usr/bin/env python3
"""
generate_youtube_script.py — YouTube Video Script & Metadata Generator
Skill: /youtube-script
Version: 1.0

Generates a complete YouTube publishing package:
  - SEO-optimized title
  - Description with timestamps, links, hashtags
  - Discovery tags (up to 30)
  - Video script with intro narration, scene breakdown, outro CTA

Usage:
  python generate_youtube_script.py <song_id> <artist_slug> [--project-root PATH]
                                    [--video-type master] [--output-dir PATH]
"""
import argparse
import json
import math
import os
import re
import sys
import textwrap
from pathlib import Path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_json(path: Path) -> dict:
    """Load a JSON file, return empty dict on failure."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"  [WARN] Could not load {path}: {e}")
        return {}


def fmt_timestamp(seconds: float) -> str:
    """Convert seconds to M:SS format."""
    m = int(seconds) // 60
    s = int(seconds) % 60
    return f"{m}:{s:02d}"


def truncate(text: str, max_len: int) -> str:
    """Truncate text to max_len, adding ellipsis if needed."""
    if len(text) <= max_len:
        return text
    return text[: max_len - 3].rstrip() + "..."


def parse_lrc_lines(lrc_path: Path) -> list[dict]:
    """Parse an LRC file into [{time_sec, text}, ...]."""
    lines = []
    if not lrc_path.exists():
        return lines
    pattern = re.compile(r"\[(\d+):(\d+(?:\.\d+)?)\](.+)")
    with open(lrc_path, "r", encoding="utf-8") as f:
        for raw in f:
            m = pattern.match(raw.strip())
            if m:
                mins, secs, text = int(m.group(1)), float(m.group(2)), m.group(3).strip()
                lines.append({"time_sec": mins * 60 + secs, "text": text})
    return lines


def pick_quotable(lyrics: list[dict], max_lines: int = 2) -> str:
    """Pick the most interesting lyric lines for the description hook."""
    if not lyrics:
        return ""
    # Prefer lines from the first third of the song (usually the hook)
    cutoff = len(lyrics) // 3 if len(lyrics) > 6 else len(lyrics)
    candidates = [l["text"] for l in lyrics[:cutoff] if len(l["text"]) > 15]
    if not candidates:
        candidates = [l["text"] for l in lyrics if len(l["text"]) > 10]
    return " / ".join(candidates[:max_lines])


# ---------------------------------------------------------------------------
# Generators
# ---------------------------------------------------------------------------

def generate_title(
    artist_name: str,
    song_title: str,
    genre: str,
    video_type: str,
    config: dict,
) -> str:
    """Generate an SEO-optimized YouTube title."""
    tc = config.get("title", {})
    max_len = tc.get("max_length", 70)
    emoji_map = tc.get("genre_emoji", {})
    suffix_map = tc.get("suffix_patterns", {})

    emoji = emoji_map.get(genre, "🎵")
    suffix = suffix_map.get(video_type, "(Official Music Video)")

    # Try full format first
    title = f'{emoji} {artist_name} - "{song_title}" {suffix}'
    if len(title) <= max_len:
        return title

    # Drop emoji
    title = f'{artist_name} - "{song_title}" {suffix}'
    if len(title) <= max_len:
        return title

    # Drop quotes
    title = f"{artist_name} - {song_title} {suffix}"
    return truncate(title, max_len)


def generate_description(
    artist_name: str,
    song_title: str,
    genre: str,
    mood: str,
    duration_sec: float,
    segments: list[dict],
    lyrics: list[dict],
    artist_profile: dict,
    config: dict,
) -> str:
    """Generate full YouTube description with timestamps, links, hashtags."""
    dc = config.get("description", {})
    parts = []

    # --- Hook (first 2 lines visible in search) ---
    quotable = pick_quotable(lyrics)
    if quotable:
        parts.append(f'"{quotable}"')
    parts.append(
        f"{song_title} by {artist_name} — a {mood} {genre} track "
        f"that runs {fmt_timestamp(duration_sec)}. "
        f"Featuring Weeter & Blubby!"
    )
    parts.append("")

    # --- Timestamps from segments ---
    if dc.get("include_timestamps", True) and segments:
        parts.append("⏱️ Timestamps:")
        for seg in segments:
            label = seg.get("label", seg.get("name", "section"))
            label = label.replace("_", " ").title()
            start = seg.get("start", 0)
            parts.append(f"  {fmt_timestamp(start)} — {label}")
        parts.append("")

    # --- Artist bio ---
    if dc.get("include_artist_bio", True):
        bio = artist_profile.get("creative_brief", {}).get("visual_identity", "")
        if not bio:
            bio = f"{artist_name} is a {genre} artist on Frozen Cloud Music."
        parts.append(f"🎤 About {artist_name}:")
        parts.append(bio)
        parts.append("")

    # --- Links ---
    if dc.get("include_links", True):
        lt = dc.get("links_template", {})
        label_name = dc.get("label_name", "Frozen Cloud Music")
        label_url = dc.get("label_url", "https://frozencloudmusic.com")
        parts.append("🔗 Links:")
        # Artist website from profile
        website = artist_profile.get("website", "")
        if website:
            parts.append(f"  🌐 {artist_name}: {website}")
        parts.append(f"  🏷️ {label_name}: {label_url}")
        parts.append("")

    # --- CTA ---
    cta = dc.get("default_cta", "Like & Subscribe!")
    parts.append(cta)
    parts.append("")

    # --- Hashtags ---
    if dc.get("include_hashtags", True):
        max_h = dc.get("max_hashtags", 10)
        tags = [f"#{genre.replace('-', '').replace(' ', '')}", f"#{mood}",
                f"#{artist_name.replace(' ', '')}", "#WeetAndBlubby",
                "#FrozenCloudMusic", "#RidgemontRecords", "#OfficialMusicVideo",
                "#NewMusic"]
        parts.append(" ".join(tags[:max_h]))

    return "\n".join(parts)


def generate_tags(
    artist_name: str,
    song_title: str,
    genre: str,
    mood: str,
    config: dict,
) -> list[str]:
    """Generate up to 30 discovery tags."""
    tc = config.get("tags", {})
    max_count = tc.get("max_count", 30)
    always = list(tc.get("always_include", []))
    genre_specific = tc.get("genre_tags", {}).get(genre, [])

    tags = always + genre_specific
    # Add song-specific
    tags += [
        artist_name,
        song_title,
        f"{artist_name} {song_title}",
        f"{artist_name} official",
        f"{genre} music {mood}",
        f"new {genre}",
        f"{mood} music",
    ]
    # Deduplicate preserving order
    seen = set()
    unique = []
    for t in tags:
        low = t.lower()
        if low not in seen:
            seen.add(low)
            unique.append(t)
    return unique[:max_count]


def generate_script(
    artist_name: str,
    song_title: str,
    genre: str,
    mood: str,
    duration_sec: float,
    segments: list[dict],
    lyrics: list[dict],
    config: dict,
) -> dict:
    """Generate a structured video script with intro, scenes, and outro."""
    sc = config.get("script", {})
    intro_dur = sc.get("intro_duration_seconds", 8)
    outro_dur = sc.get("outro_duration_seconds", 10)
    intro_style = sc.get("intro_style", {}).get(mood, "energetic tone")
    cta_opts = sc.get("cta_options", ["Subscribe!"])

    script = {
        "version": "1.0",
        "total_duration_sec": duration_sec,
        "intro": {
            "duration_sec": intro_dur,
            "tone": intro_style,
            "narration": (
                f"Get ready for \"{song_title}\" by {artist_name} — "
                f"a {mood} {genre} experience brought to you by "
                f"Weeter and Blubby on Frozen Cloud Music."
            ),
            "visual_direction": (
                f"Open with a slow zoom on the background. "
                f"Weeter enters from left with bounce-in (0.5s). "
                f"Blubby enters from right. Title card fades in: "
                f"\"{song_title}\" — {artist_name}."
            ),
        },
        "scenes": [],
        "outro": {
            "duration_sec": outro_dur,
            "narration": (
                f"That was \"{song_title}\" by {artist_name}. "
                f"Hit subscribe and the bell icon so you never miss a drop!"
            ),
            "cta": cta_opts[0] if cta_opts else "Subscribe!",
            "visual_direction": (
                "Slow zoom out. Weeter and Blubby wave. "
                "End card with subscribe button overlay and playlist link."
            ),
        },
    }

    # Build scenes from segments
    for i, seg in enumerate(segments):
        label = seg.get("label", seg.get("name", f"section_{i}"))
        start = seg.get("start", 0)
        end = seg.get("end", start + 30)
        dur = end - start

        # Find lyrics in this segment's time range
        seg_lyrics = [l["text"] for l in lyrics if start <= l["time_sec"] < end]

        scene = {
            "scene_number": i + 1,
            "label": label.replace("_", " ").title(),
            "time_range": f"{fmt_timestamp(start)} - {fmt_timestamp(end)}",
            "duration_sec": round(dur, 1),
            "visual_direction": _scene_direction(label, genre, mood, i, len(segments)),
            "lyrics_in_segment": seg_lyrics[:5],  # Cap at 5 for readability
        }
        script["scenes"].append(scene)

    return script


def _scene_direction(label: str, genre: str, mood: str, idx: int, total: int) -> str:
    """Generate visual direction for a scene based on its position and mood."""
    label_l = label.lower()

    if "intro" in label_l or idx == 0:
        return (
            "Slow Ken Burns zoom-in on background. Characters enter with bounce. "
            "Low energy — let the scene breathe."
        )
    elif idx == total - 1:
        return (
            "Slow zoom-out. Characters do their exit animation (0.3s fade). "
            "Transition to end card."
        )
    elif "chorus" in label_l or "hook" in label_l:
        return (
            "Maximum energy: fast zoompan oscillation, strong beat bounce on characters. "
            "Lyric text appears larger with glow effect. "
            "Character poses shift to hype/excited."
        )
    elif "verse" in label_l:
        return (
            "Moderate Ken Burns with gentle XY drift. "
            "Characters in neutral/happy poses with standard breathing. "
            "Lyrics flow in with subtle fade-in."
        )
    elif "bridge" in label_l:
        return (
            "Shift color grading slightly cooler. Slow zoom. "
            "Characters shift to thoughtful/neutral poses. "
            "Lyric text has longer fade timing."
        )
    else:
        energy_word = "high" if mood in ("hype", "explosive", "happy") else "moderate"
        return (
            f"{energy_word.title()} energy Ken Burns movement. "
            f"Standard {genre} color grading. "
            f"Characters in genre-default poses with beat-synced bounce."
        )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Generate YouTube script & metadata")
    parser.add_argument("song_id", help="Song identifier (e.g., crazy)")
    parser.add_argument("artist_slug", help="Artist slug (e.g., the_ridgemonts)")
    parser.add_argument("--project-root", default=".", help="Project root path")
    parser.add_argument("--video-type", default="master",
                        choices=["master", "lyric_video", "visualizer", "short", "sync_reel"])
    parser.add_argument("--output-dir", default=None, help="Override output directory")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    catalog_dir = root / "catalog" / args.artist_slug / args.song_id

    print(f"=== YouTube Script Generator v1.0 ===")
    print(f"Song: {args.song_id} | Artist: {args.artist_slug}")
    print(f"Video type: {args.video_type}")
    print(f"Catalog dir: {catalog_dir}")
    print()

    # --- Load data ---
    manifest = load_json(catalog_dir / "manifest.json")
    if not manifest:
        print("[FATAL] No manifest.json found. Run analyze_catalog.py first.")
        sys.exit(1)

    artist_profile = load_json(catalog_dir / "artist_profile.json")
    if not artist_profile:
        artist_profile = load_json(root / "profiles" / f"{args.artist_slug}.json")

    creative_brief = load_json(catalog_dir / "creative_brief.json")
    config = load_json(root / "data" / "youtube_script_config.json")
    if not config:
        print("[WARN] No youtube_script_config.json found, using defaults.")
        config = {}

    # --- Extract manifest data ---
    analysis = manifest.get("analysis", manifest)
    artist_name = manifest.get("artist", args.artist_slug.replace("_", " ").title())
    song_title = manifest.get("title", args.song_id.replace("_", " ").title())
    genre = analysis.get("genre", "pop")
    mood = analysis.get("mood", "happy")
    bpm = analysis.get("bpm", 120)
    key = analysis.get("key", "C major")
    duration_sec = analysis.get("duration_sec", 180)
    segments = analysis.get("segments", [])

    print(f"Artist: {artist_name}")
    print(f"Title: {song_title}")
    print(f"Genre: {genre} | Mood: {mood} | BPM: {bpm} | Key: {key}")
    print(f"Duration: {fmt_timestamp(duration_sec)} | Segments: {len(segments)}")
    print()

    # --- Parse lyrics ---
    lrc_path = catalog_dir / "lyrics.lrc"
    if not lrc_path.exists():
        # Check common alternate locations
        alt = catalog_dir / f"{args.song_id}.lrc"
        if alt.exists():
            lrc_path = alt
    lyrics = parse_lrc_lines(lrc_path)
    print(f"Lyrics: {len(lyrics)} lines loaded" if lyrics else "Lyrics: none found")

    # --- Generate outputs ---
    print("\n--- Generating Title ---")
    title = generate_title(artist_name, song_title, genre, args.video_type, config)
    print(f"  {title}")

    print("\n--- Generating Description ---")
    description = generate_description(
        artist_name, song_title, genre, mood, duration_sec,
        segments, lyrics, artist_profile, config,
    )
    print(f"  ({len(description)} chars)")

    print("\n--- Generating Tags ---")
    tags = generate_tags(artist_name, song_title, genre, mood, config)
    print(f"  {len(tags)} tags")

    print("\n--- Generating Video Script ---")
    script = generate_script(
        artist_name, song_title, genre, mood, duration_sec,
        segments, lyrics, config,
    )
    print(f"  {len(script['scenes'])} scenes")

    # --- Save outputs ---
    out_dir = Path(args.output_dir) if args.output_dir else catalog_dir / "youtube"
    out_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / "youtube_title.txt").write_text(title, encoding="utf-8")
    (out_dir / "youtube_description.txt").write_text(description, encoding="utf-8")
    (out_dir / "youtube_tags.txt").write_text(", ".join(tags), encoding="utf-8")
    with open(out_dir / "youtube_script.json", "w", encoding="utf-8") as f:
        json.dump(script, f, indent=2, ensure_ascii=False)

    print(f"\n=== Outputs saved to {out_dir} ===")
    for fname in ["youtube_title.txt", "youtube_description.txt",
                   "youtube_tags.txt", "youtube_script.json"]:
        fpath = out_dir / fname
        print(f"  ✓ {fname} ({fpath.stat().st_size:,} bytes)")

    print("\nDone!")


if __name__ == "__main__":
    main()
