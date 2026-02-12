#!/usr/bin/env python3
"""
Suno v5.0 Prompt Generator
Deterministic engine for generating Style and Exclude prompts from minimal input.

Usage:
    python generate_prompt.py --subgenre "Synth Pop" --bpm 120 --instrumental
    python generate_prompt.py --subgenre "Modern Trap" --vocals --vocal-mode "Rap" --seed 3
    python generate_prompt.py --preset "80s Synth Pop"
"""

import json
import argparse
import os
import re
from pathlib import Path
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

# ----------------------------
# Errors
# ----------------------------
class ValidationError(Exception):
    """Validation error with optional rule_id for debugging."""
    def __init__(self, message, rule_id=None):
        super().__init__(message)
        self.rule_id = rule_id

# ----------------------------
# Utility
# ----------------------------
def _norm_token(s: str) -> str:
    """Normalize user tokens for alias matching & comparisons."""
    s = s.strip().lower()
    s = re.sub(r"\s+", " ", s)
    return s

@dataclass
class VocalIntent:
    """Tri-state vocal intent: vocals | instrumental | unspecified"""
    value: str

def get_vocal_intent(args: argparse.Namespace) -> VocalIntent:
    """Determine vocal intent from CLI args (tri-state)."""
    if getattr(args, "instrumental", False):
        return VocalIntent("instrumental")
    if getattr(args, "vocals", False):
        return VocalIntent("vocals")
    return VocalIntent("unspecified")

# Resolve asset paths relative to script location
SCRIPT_DIR = Path(__file__).parent.parent
ASSETS_DIR = SCRIPT_DIR / "assets"

def load_json(filename):
    filepath = ASSETS_DIR / filename
    if not filepath.exists():
        return None
    with open(filepath, 'r') as f:
        return json.load(f)

def load_data():
    """Load all data files and build indexes."""
    data = {
        'genres': load_json('genres.json') or [],
        'subgenres': load_json('subgenres.json') or [],
        'tags': load_json('subgenre_tags.json') or [],
        'instruments': load_json('instruments.json') or [],
        'presets': load_json('presets.json') or [],
        'aliases': load_json('aliases.json') or [],
        'constraints': load_json('constraints.json'),
        'modifiers': load_json('modifiers.json') or []
    }

    # Build indexes
    data['idx'] = build_indexes(data)
    return data

def build_indexes(data: Dict[str, Any]) -> Dict[str, Any]:
    """Build lookup indexes for fast access."""
    idx = {}

    # Genre indexes
    idx['genres_by_id'] = {g['genre_id']: g for g in data['genres']}
    idx['genres_by_name_norm'] = {_norm_token(g['name']): g for g in data['genres']}

    # Subgenre indexes
    idx['subgenres_by_id'] = {sg['subgenre_id']: sg for sg in data['subgenres']}
    idx['subgenres_by_name_norm'] = {_norm_token(sg['name']): sg for sg in data['subgenres']}

    # Tags indexes: by subgenre_id and globals
    idx['tags_by_subgenre'] = {}
    idx['global_tags'] = []

    for t in data['tags']:
        if t.get('global') is True:
            idx['global_tags'].append(t)
            continue
        sid = t.get('subgenre_id')
        if sid:
            idx['tags_by_subgenre'].setdefault(sid, []).append(t)

    # Alias map: alias_norm -> canonical string
    idx['alias_map'] = {}
    for entry in data['aliases']:
        canonical = entry['canonical']
        for a in entry.get('aliases', []):
            idx['alias_map'][_norm_token(a)] = canonical
        # Include canonical itself
        idx['alias_map'][_norm_token(canonical)] = canonical

    # Modifier tokens for constraint checking
    idx['modifier_tokens_norm'] = set()
    for m in data['modifiers']:
        idx['modifier_tokens_norm'].add(_norm_token(m['name']))

    return idx

# ----------------------------
# Lookups
# ----------------------------
def find_genre_by_id(data: Dict[str, Any], genre_id: str) -> Optional[Dict[str, Any]]:
    """Find genre by ID."""
    return data['idx']['genres_by_id'].get(genre_id)

def find_genre_by_name(data: Dict[str, Any], name: str) -> Optional[Dict[str, Any]]:
    """Find genre by name (case-insensitive)."""
    return data['idx']['genres_by_name_norm'].get(_norm_token(name))

def find_subgenre(data, name):
    """Find subgenre by name (case-insensitive)."""
    return data['idx']['subgenres_by_name_norm'].get(_norm_token(name))

def find_preset(data, name):
    """Find preset by name."""
    name_lower = name.lower()
    for p in data['presets']:
        if p['name'].lower() == name_lower:
            return p
    return None

def resolve_alias(data: Dict[str, Any], token: str) -> str:
    """Resolve alias to canonical (case-insensitive)."""
    tnorm = _norm_token(token)
    return data['idx']['alias_map'].get(tnorm, token)

def canonicalize_genre_token(data: Dict[str, Any], token: str) -> str:
    """Normalize token via aliases, then return canonical casing."""
    resolved = resolve_alias(data, token)
    g = find_genre_by_name(data, resolved)
    return g['name'] if g else resolved

# ----------------------------
# Constraints
# ----------------------------
def validate_constraints(
    data: Dict[str, Any],
    *,
    primary_genre_id: Optional[str] = None,
    selected_genre_tokens: Optional[List[str]] = None,
    selected_subgenre: Optional[Dict[str, Any]] = None
) -> None:
    """
    Validate against constraints.json rules.
    Raises ValidationError if constraints violated.
    """
    constraints = data.get('constraints')
    if not constraints:
        return

    rules = constraints.get('rules', [])

    # Normalize tokens post-alias, case-insensitive
    normalized = []
    if selected_genre_tokens:
        for t in selected_genre_tokens:
            resolved = resolve_alias(data, t)
            normalized.append(_norm_token(resolved))

    for rule in rules:
        rtype = rule.get('rule')

        if rtype == 'primary_genre_must_be_engine':
            if primary_genre_id:
                g = find_genre_by_id(data, primary_genre_id)
                if g and g.get('role') != 'engine':
                    raise ValidationError(rule.get('message', 'Primary genre must be engine'), rule.get('id'))

        elif rtype == 'requires_subgenre':
            applies = set(rule.get('applies_to_genre_ids', []))
            if primary_genre_id and primary_genre_id in applies and selected_subgenre is None:
                raise ValidationError(rule.get('message', 'Container requires subgenre'), rule.get('id'))

        elif rtype == 'cannot_be_sole_genre':
            applies_to_tokens = [_norm_token(x) for x in rule.get('applies_to_tokens', [])]
            applies_set = set(applies_to_tokens)

            if normalized:
                non_mod = [t for t in normalized if t not in applies_set]
                if len(non_mod) == 0:
                    raise ValidationError(rule.get('message', 'Modifiers cannot be sole genre token'), rule.get('id'))

# ----------------------------
# Tags
# ----------------------------
def get_tags_for_subgenre(data, subgenre_id, engine=None):
    """Get all tags for a subgenre (including globals), optionally filtered by engine."""
    tags = []

    # Add global tags
    tags.extend(data['idx']['global_tags'])

    # Add subgenre-specific tags
    tags.extend(data['idx']['tags_by_subgenre'].get(subgenre_id, []))

    if engine:
        tags = [t for t in tags if t.get('engine', '').lower() == engine.lower()]

    return tags

def filter_tags_by_vocal_intent(tags: List[Dict[str, Any]], vocal_intent: VocalIntent) -> List[Dict[str, Any]]:
    """Filter tags based on conditional field and vocal intent (tri-state)."""
    out = []
    for t in tags:
        cond = t.get('conditional')
        if not cond:
            out.append(t)
            continue

        # Only inject instrumental tag when explicitly requested
        if cond == 'instrumental_only':
            if vocal_intent.value == 'instrumental':
                out.append(t)
        else:
            # Unknown condition: include by default
            out.append(t)

    return out

def get_instruments_for_subgenre(data, subgenre_id):
    """Get all instruments for a subgenre."""
    return [i for i in data['instruments'] if i['subgenre_id'] == subgenre_id]

# ----------------------------
# Selection
# ----------------------------
def weight_rank(item, index):
    """Calculate selection rank based on weight and position."""
    weight = item.get('weight', 1)
    return (4 - weight) * 100000 + index

def select_by_seed(items, seed, max_count=3):
    """Select items using weight-aware ranking and seed."""
    if not items:
        return []

    ranked = [(weight_rank(item, i), item) for i, item in enumerate(items)]
    ranked.sort(key=lambda x: x[0])

    start_idx = (seed - 1) % len(ranked)

    selected = []
    for i in range(min(max_count, len(ranked))):
        idx = (start_idx + i) % len(ranked)
        selected.append(ranked[idx][1])

    return selected

# ----------------------------
# Prompt Generation
# ----------------------------
def generate_prompt(
    data,
    subgenre_name,
    bpm=None,
    momentum=None,
    instrumental=False,
    vocals=False,
    vocal_mode=None,
    vocal_delivery=None,
    drum_source=None,
    seed=1,
    detail_level=2
):
    """
    Generate Style and Exclude prompts.

    Args:
        data: Loaded data dictionary
        subgenre_name: Target subgenre (e.g., "Synth Pop")
        bpm: Beats per minute (uses subgenre default if None)
        momentum: Energy descriptor (e.g., "Driving", "Laid-back")
        instrumental: If True, explicitly no vocals
        vocals: If True, explicitly include vocals
        vocal_mode: Vocal style (e.g., "Sung", "Rap")
        vocal_delivery: Vocal texture (e.g., "Smooth", "Raspy")
        drum_source: Drum type (e.g., "Acoustic", "Electronic", "808")
        seed: Variation seed 1-10 for deterministic variety
        detail_level: 1=minimal, 2=standard, 3=detailed

    Returns:
        dict with 'style', 'exclude', 'debug' keys
    """
    subgenre = find_subgenre(data, subgenre_name)
    if not subgenre:
        return {'error': f"Subgenre '{subgenre_name}' not found"}

    # Validate constraints
    try:
        validate_constraints(
            data,
            primary_genre_id=subgenre.get('primary_genre_id'),
            selected_subgenre=subgenre
        )
    except ValidationError as e:
        return {'error': str(e)}

    # Determine vocal intent (tri-state)
    if instrumental:
        vocal_intent = VocalIntent('instrumental')
    elif vocals:
        vocal_intent = VocalIntent('vocals')
    else:
        vocal_intent = VocalIntent('unspecified')

    # Get primary engine genre
    genre = find_genre_by_id(data, subgenre['primary_genre_id'])
    genre_name = genre['name'] if genre else ""

    # Get container genre if exists
    container_genre = None
    if subgenre.get('container_genre_id'):
        container_genre = find_genre_by_id(data, subgenre['container_genre_id'])

    # Use defaults from subgenre if not specified
    if bpm is None:
        bpm = subgenre.get('default_bpm', 120)
    if momentum is None:
        momentum = subgenre.get('default_momentum')

    # Collect tokens in hierarchy order
    tokens = []
    debug_info = {'subgenre_id': subgenre['subgenre_id'], 'selections': {}}

    # 1. Genre Core (engine first, then container, then subgenre)
    tokens.append(subgenre['name'])
    if genre_name and genre_name.lower() != subgenre['name'].lower():
        tokens.append(genre_name)

    # Container injection (if exists and not redundant with subgenre name)
    if container_genre:
        container_name = container_genre['name']
        # Avoid redundant injection if container name is in subgenre name
        if container_name.lower() not in subgenre['name'].lower():
            tokens.append(container_name)

    # 2. Vibe & Mood (from momentum)
    if momentum:
        tokens.append(f"{momentum} energy")

    # 3. Tempo & Rhythm
    tokens.append(f"{bpm} BPM")

    # Get tags by engine, filtered by vocal intent
    all_tags = get_tags_for_subgenre(data, subgenre['subgenre_id'])
    all_tags = filter_tags_by_vocal_intent(all_tags, vocal_intent)

    groove_tags = [t for t in all_tags if t.get('engine', '').lower() == 'groove']
    harmony_tags = [t for t in all_tags if t.get('engine', '').lower() == 'harmony']
    production_tags = [t for t in all_tags if t.get('engine', '').lower() == 'production']

    # Select tags based on seed and detail level
    tag_count = {1: 1, 2: 2, 3: 3}.get(detail_level, 2)

    selected_groove = select_by_seed(groove_tags, seed, tag_count)
    selected_harmony = select_by_seed(harmony_tags, seed, tag_count)
    selected_production = select_by_seed(production_tags, seed, tag_count)

    # Add groove phrases
    for tag in selected_groove:
        tokens.append(tag['phrase'])
    debug_info['selections']['groove'] = [t['phrase'] for t in selected_groove]

    # Add harmony phrases
    for tag in selected_harmony:
        tokens.append(tag['phrase'])
    debug_info['selections']['harmony'] = [t['phrase'] for t in selected_harmony]

    # 4. Instrumentation
    instruments = get_instruments_for_subgenre(data, subgenre['subgenre_id'])
    instrument_count = {1: 2, 2: 3, 3: 5}.get(detail_level, 3)
    selected_instruments = select_by_seed(instruments, seed, instrument_count)

    for inst in selected_instruments:
        tokens.append(inst['instrument_name'])
    debug_info['selections']['instruments'] = [i['instrument_name'] for i in selected_instruments]

    # 5. Vocal Character
    if vocal_intent.value == 'instrumental':
        tokens.append("instrumental")
    elif vocal_intent.value == 'vocals' or (vocal_mode or vocal_delivery):
        vocal_parts = []
        if vocal_delivery:
            vocal_parts.append(vocal_delivery)
        if vocal_mode:
            vocal_parts.append(vocal_mode.lower() + " vocals")
        if vocal_parts:
            tokens.append(", ".join(vocal_parts))

    # 6. Production Polish
    for tag in selected_production:
        tokens.append(tag['phrase'])
    debug_info['selections']['production'] = [t['phrase'] for t in selected_production]

    # Add drum source if specified
    if drum_source:
        tokens.append(f"{drum_source} drums")

    # Build exclude list
    excludes = []
    if vocal_intent.value == 'instrumental':
        excludes.extend(["No Rap", "No Spoken Word"])
    elif vocal_mode and vocal_mode.lower() == "rap":
        excludes.extend(["No Singing", "No Choir"])

    # Deduplicate tokens (case-insensitive)
    seen = set()
    unique_tokens = []
    for t in tokens:
        t_lower = t.lower()
        if t_lower not in seen:
            seen.add(t_lower)
            unique_tokens.append(t)

    return {
        'style': ", ".join(unique_tokens),
        'exclude': ", ".join(excludes) if excludes else "",
        'debug': debug_info
    }

def generate_from_preset(data, preset_name, seed_override=None):
    """Generate prompt from a preset configuration."""
    preset = find_preset(data, preset_name)
    if not preset:
        return {'error': f"Preset '{preset_name}' not found"}

    return generate_prompt(
        data,
        subgenre_name=preset.get('subgenre', ''),
        bpm=preset.get('bpm'),
        momentum=preset.get('momentum'),
        instrumental=(preset.get('vocalsmode', '').lower() == 'instrumental'),
        vocal_mode=preset.get('vocalmode'),
        vocal_delivery=preset.get('vocaldelivery'),
        drum_source=preset.get('drumsource'),
        seed=seed_override or preset.get('variationseed', 1),
        detail_level=preset.get('detaillevel', 2)
    )

def main():
    parser = argparse.ArgumentParser(description='Generate Suno v5.0 prompts')
    parser.add_argument('--subgenre', '-s', help='Target subgenre name')
    parser.add_argument('--preset', '-p', help='Use a preset configuration')
    parser.add_argument('--bpm', type=int, help='Tempo in BPM')
    parser.add_argument('--momentum', '-m', help='Energy level (Driving, Laid-back, Floating)')
    parser.add_argument('--instrumental', '-i', action='store_true', help='Instrumental mode (no vocals)')
    parser.add_argument('--vocals', '-v', action='store_true', help='Include vocals')
    parser.add_argument('--vocal-mode', help='Vocal style (Sung, Rap, Spoken)')
    parser.add_argument('--vocal-delivery', help='Vocal texture (Smooth, Raspy, Powerful)')
    parser.add_argument('--drum-source', help='Drum type (Acoustic, Electronic, 808, Cinematic)')
    parser.add_argument('--seed', type=int, default=1, help='Variation seed 1-10')
    parser.add_argument('--detail', type=int, default=2, choices=[1,2,3], help='Detail level')
    parser.add_argument('--debug', action='store_true', help='Show debug info')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--list-subgenres', action='store_true', help='List all subgenres')
    parser.add_argument('--list-presets', action='store_true', help='List all presets')
    parser.add_argument('--list-genres', action='store_true', help='List all genres with roles')

    args = parser.parse_args()

    # Guard against both vocal flags
    if args.instrumental and args.vocals:
        print("Error: cannot use both --vocals and --instrumental")
        return

    data = load_data()

    if args.list_genres:
        print("Available genres:")
        for g in sorted(data['genres'], key=lambda x: x.get('sort_order', 0)):
            role = g.get('role', 'unknown')
            print(f"  {g['name']} ({role})")
        return

    if args.list_subgenres:
        print("Available subgenres:")
        for sg in sorted(data['subgenres'], key=lambda x: x['name']):
            genre = find_genre_by_id(data, sg['primary_genre_id'])
            genre_name = genre['name'] if genre else "Unknown"
            container = ""
            if sg.get('container_genre_id'):
                c = find_genre_by_id(data, sg['container_genre_id'])
                container = f" [+{c['name']}]" if c else ""
            print(f"  {sg['name']} ({genre_name}{container})")
        return

    if args.list_presets:
        print("Available presets:")
        for p in data['presets']:
            print(f"  {p['name']}")
        return

    if args.preset:
        result = generate_from_preset(data, args.preset, args.seed if args.seed != 1 else None)
    elif args.subgenre:
        result = generate_prompt(
            data,
            subgenre_name=args.subgenre,
            bpm=args.bpm,
            momentum=args.momentum,
            instrumental=args.instrumental,
            vocals=args.vocals,
            vocal_mode=args.vocal_mode,
            vocal_delivery=args.vocal_delivery,
            drum_source=args.drum_source,
            seed=args.seed,
            detail_level=args.detail
        )
    else:
        parser.print_help()
        return

    if 'error' in result:
        print(f"Error: {result['error']}")
        return

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"STYLES: {result['style']}")
        print(f"EXCLUDE: {result['exclude']}")
        if args.debug:
            print(f"\nDEBUG: {json.dumps(result['debug'], indent=2)}")

if __name__ == '__main__':
    main()
