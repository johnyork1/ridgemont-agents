#!/usr/bin/env python3
"""
Suno v5.0 Prompt Generator — Deterministic Style Prompt Engine

Generates structured Suno.com prompts from genre + mood + instrumentation
parameters. Follows the Authoritative Consolidated Guidebook (Final).

Deterministic output: same inputs always produce same prompt.
Slot ordering: Era → Rhythm → Genre → Subgenre → Instruments → Vocals → Mood → Mix

Usage:
    python generate_prompt.py --genre reggae --mood chill --bpm 136
    python generate_prompt.py --genre hip-hop --mood aggressive --vocals "male rap"
    python generate_prompt.py --genre electronic --subgenre "deep house" --mood dreamy
"""

import argparse
import json
import logging
import os
import sys
import hashlib

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "assets")

SUBGENRES_PATH = os.path.join(ASSETS_DIR, "subgenres.json")
TAGS_PATH = os.path.join(ASSETS_DIR, "subgenre_tags.json")
INSTRUMENTS_PATH = os.path.join(ASSETS_DIR, "instruments.json")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("suno_prompt")

# ---------------------------------------------------------------------------
# Data loaders
# ---------------------------------------------------------------------------

def load_json(path: str) -> dict:
    """Load a JSON asset file. Abort on failure."""
    if not os.path.isfile(path):
        log.error("Asset not found: %s", path)
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def load_assets():
    """Load all three asset files and return them."""
    subgenres = load_json(SUBGENRES_PATH)
    tags = load_json(TAGS_PATH)
    instruments = load_json(INSTRUMENTS_PATH)
    return subgenres, tags, instruments

# ---------------------------------------------------------------------------
# Deterministic helpers
# ---------------------------------------------------------------------------

def deterministic_pick(items: list, seed_str: str, count: int = 1) -> list:
    """
    Deterministically select *count* items from *items* using a hash-based
    seed so that the same inputs always produce the same selection.
    """
    if not items:
        return []
    h = int(hashlib.sha256(seed_str.encode()).hexdigest(), 16)
    picked = []
    for i in range(min(count, len(items))):
        idx = (h + i * 7919) % len(items)  # prime step for spread
        picked.append(items[idx])
    return picked


def resolve_subgenre(subgenres: dict, genre: str, subgenre: str | None) -> dict:
    """
    Resolve a subgenre entry. If subgenre is explicitly provided, look it up.
    Otherwise return the first entry for the genre as default.
    """
    genre_key = genre.lower().replace(" ", "-")
    genre_data = subgenres.get("genres", {}).get(genre_key, {})
    sub_list = genre_data.get("subgenres", [])

    if subgenre:
        sub_lower = subgenre.lower()
        for entry in sub_list:
            if entry.get("name", "").lower() == sub_lower:
                return entry
        log.warning("Subgenre '%s' not found for genre '%s'; using default.", subgenre, genre)

    if sub_list:
        return sub_list[0]
    return {"name": genre_key, "rhythm": "standard", "era": "contemporary"}


def resolve_instruments(instruments_db: dict, genre: str, requested: list[str] | None, seed: str) -> list[str]:
    """
    Build an instrument list. If the user specified instruments, validate them.
    Otherwise pick genre-appropriate defaults deterministically.
    """
    all_instruments = instruments_db.get("instruments", [])
    inst_names = [i["name"] if isinstance(i, dict) else i for i in all_instruments]

    if requested:
        validated = []
        for r in requested:
            r_lower = r.lower().strip()
            for name in inst_names:
                if r_lower in name.lower():
                    validated.append(name)
                    break
            else:
                validated.append(r)  # pass through user text
        return validated

    # Genre-default instrument selection
    genre_defaults = instruments_db.get("genre_defaults", {}).get(genre.lower(), [])
    if genre_defaults:
        return genre_defaults[:5]

    # Fallback: deterministic pick from full list
    return deterministic_pick(inst_names, f"inst-{genre}-{seed}", count=4)


def resolve_tags(tags_db: dict, genre: str, mood: str, seed: str) -> list[str]:
    """
    Pick descriptive tags for the prompt from the tag database.
    """
    genre_tags = tags_db.get("genres", {}).get(genre.lower(), [])
    mood_tags = tags_db.get("moods", {}).get(mood.lower(), [])

    combined = list(set(genre_tags + mood_tags))
    if not combined:
        combined = tags_db.get("universal", ["polished", "professional", "studio-quality"])

    return deterministic_pick(combined, f"tags-{genre}-{mood}-{seed}", count=5)

# ---------------------------------------------------------------------------
# Prompt builder — Deterministic Slot Order
# ---------------------------------------------------------------------------

# Slot order from guidebook §4.1:
# Era → Rhythm → Primary Genre → Subgenre/Influences → Instruments → Vocals → Mood → Mix

def build_style_prompt(
    genre: str,
    mood: str,
    bpm: int | None,
    subgenre_entry: dict,
    instruments: list[str],
    vocals: str | None,
    tags: list[str],
    mix_intent: str | None,
) -> str:
    """
    Assemble the Style Prompt in strict deterministic slot order.
    Returns a single prose string (no tags, no lyrics).
    """
    parts = []

    # 1. Era
    era = subgenre_entry.get("era", "contemporary")
    parts.append(era.capitalize())

    # 2. Rhythm
    rhythm = subgenre_entry.get("rhythm", "")
    if bpm:
        rhythm_str = f"{rhythm}, {bpm} BPM" if rhythm else f"{bpm} BPM"
    else:
        rhythm_str = rhythm
    if rhythm_str:
        parts.append(rhythm_str)

    # 3. Primary Genre
    parts.append(genre.lower())

    # 4. Subgenre / Influences
    sub_name = subgenre_entry.get("name", "")
    if sub_name and sub_name.lower() != genre.lower():
        influences = subgenre_entry.get("influences", [])
        if influences:
            parts.append(f"{sub_name} with {', '.join(influences[:2])} influences")
        else:
            parts.append(sub_name)

    # 5. Instruments (at least one specific type — guidebook §4.2)
    if instruments:
        parts.append(", ".join(instruments))

    # 6. Vocals (always present — guidebook §4.2)
    if vocals:
        parts.append(vocals)
    else:
        parts.append("clear male vocals")  # safe default

    # 7. Mood + descriptive tags
    mood_section = mood.lower()
    if tags:
        mood_section += f", {', '.join(tags)}"
    parts.append(mood_section)

    # 8. Mix / Production Intent
    if mix_intent:
        parts.append(mix_intent)
    else:
        parts.append("polished studio mix")

    return ", ".join(parts)

# ---------------------------------------------------------------------------
# Output model (canonical JSON — guidebook §8)
# ---------------------------------------------------------------------------

def build_output_model(
    genre: str,
    mood: str,
    bpm: int | None,
    subgenre_entry: dict,
    instruments: list[str],
    vocals: str | None,
    tags: list[str],
    mix_intent: str | None,
    style_prompt: str,
) -> dict:
    """Build the canonical internal data model from guidebook §8."""
    return {
        "modelPreset": "Suno_v5",
        "era": subgenre_entry.get("era", "contemporary"),
        "rhythm": subgenre_entry.get("rhythm", ""),
        "genrePrimary": genre,
        "genreInfluences": [
            {"name": inf, "weight": round(0.3 + i * 0.1, 2)}
            for i, inf in enumerate(subgenre_entry.get("influences", [])[:3])
        ],
        "instruments": [
            {"type": inst, "model": "", "articulation": "", "fx": []}
            for inst in instruments
        ],
        "vocals": {
            "gender": "",
            "range": "",
            "delivery": vocals or "clear male vocals",
            "fx": [],
        },
        "moods": [mood] + tags,
        "mixIntent": mix_intent or "polished studio mix",
        "bpm": bpm,
        "stylePrompt": style_prompt,
        "sections": [],
        "sequence": [],
        "exclusions": [],
    }

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Suno v5.0 Deterministic Prompt Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --genre reggae --mood chill --bpm 136
  %(prog)s --genre hip-hop --mood aggressive --vocals "male rap, deep voice"
  %(prog)s --genre electronic --subgenre "deep house" --mood dreamy --instruments "303 bass,Roland TR-808"
        """,
    )
    p.add_argument("--genre", required=True, help="Primary genre (e.g. reggae, hip-hop, pop)")
    p.add_argument("--subgenre", default=None, help="Specific subgenre (optional)")
    p.add_argument("--mood", default="neutral", help="Mood descriptor (e.g. chill, aggressive, dreamy)")
    p.add_argument("--bpm", type=int, default=None, help="Tempo in BPM (optional)")
    p.add_argument("--vocals", default=None, help="Vocal description (e.g. 'female soprano, airy')")
    p.add_argument("--instruments", default=None, help="Comma-separated instruments (optional)")
    p.add_argument("--mix", default=None, help="Mix/production intent (e.g. 'lo-fi bedroom production')")
    p.add_argument("--seed", default="default", help="Determinism seed for reproducible selections")
    p.add_argument("--json", action="store_true", help="Output full canonical JSON model")
    p.add_argument("--quiet", action="store_true", help="Suppress log output")
    return p.parse_args()


def main():
    args = parse_args()

    if args.quiet:
        logging.disable(logging.CRITICAL)

    log.info("Loading asset databases...")
    subgenres, tags_db, instruments_db = load_assets()

    log.info("Genre: %s | Mood: %s | BPM: %s", args.genre, args.mood, args.bpm)

    # Resolve subgenre
    sub_entry = resolve_subgenre(subgenres, args.genre, args.subgenre)
    log.info("Resolved subgenre: %s", sub_entry.get("name", "default"))

    # Resolve instruments
    requested_inst = [i.strip() for i in args.instruments.split(",")] if args.instruments else None
    inst_list = resolve_instruments(instruments_db, args.genre, requested_inst, args.seed)
    log.info("Instruments: %s", inst_list)

    # Resolve tags
    tag_list = resolve_tags(tags_db, args.genre, args.mood, args.seed)
    log.info("Tags: %s", tag_list)

    # Build style prompt
    style_prompt = build_style_prompt(
        genre=args.genre,
        mood=args.mood,
        bpm=args.bpm,
        subgenre_entry=sub_entry,
        instruments=inst_list,
        vocals=args.vocals,
        tags=tag_list,
        mix_intent=args.mix,
    )

    if args.json:
        model = build_output_model(
            genre=args.genre,
            mood=args.mood,
            bpm=args.bpm,
            subgenre_entry=sub_entry,
            instruments=inst_list,
            vocals=args.vocals,
            tags=tag_list,
            mix_intent=args.mix,
            style_prompt=style_prompt,
        )
        print(json.dumps(model, indent=2))
    else:
        print("\n=== SUNO v5.0 STYLE PROMPT ===")
        print(style_prompt)
        print("==============================\n")


if __name__ == "__main__":
    main()
