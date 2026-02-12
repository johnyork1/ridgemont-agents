---
name: suno-prompt-generator
description: Generate Suno v5.0 Style and Exclude prompts from minimal input. Use when creating cover song prompts, generating genre variations, batch-creating prompts across multiple subgenres, or when user asks to "generate a Suno prompt" or "create variations of a song." Supports 21 genres, 122 subgenres, 1127 tags, and 1223 instruments with deterministic seed-based variety. Part of the Ridgemont Studio system.
---

# Suno v5.0 Prompt Generator

Generate professional Suno v5 prompts from minimal input. The system handles tag selection, token ordering, and exclusion logic automatically.

## Quick Start

```bash
# Basic generation
python scripts/generate_prompt.py --subgenre "Synth Pop" --bpm 120 --instrumental

# With vocals
python scripts/generate_prompt.py --subgenre "Trap" --vocals --vocal-mode "Rap" --seed 3

# From preset
python scripts/generate_prompt.py --preset "Pop Anthem"

# List available subgenres/presets
python scripts/generate_prompt.py --list-subgenres
python scripts/generate_prompt.py --list-presets
```

## Common Workflows

### Generate variations for a cover song
When user provides a song and wants multiple genre versions:
1. Identify target subgenres from their request
2. Run generator for each subgenre with seeds 1-5 for variety
3. Output all Style/Exclude pairs for copy-paste into Suno

Example request: "Generate Suno prompts for 'Midnight Drive' in Synth Pop, Nu Disco, and Trap"
```bash
for genre in "Synth Pop" "Nu Disco" "Trap"; do
  echo "=== $genre ==="
  python scripts/generate_prompt.py --subgenre "$genre" --instrumental --seed 1
done
```

### Batch variations within one subgenre
Use different seeds (1-10) for deterministic variety:
```bash
for seed in 1 2 3 4 5; do
  python scripts/generate_prompt.py --subgenre "Synth Pop" --seed $seed --instrumental
done
```

### Find subgenres by genre
```bash
python scripts/generate_prompt.py --list-subgenres | grep -i "Rock"
```

## Generator Arguments

| Argument | Description |
|----------|-------------|
| `--subgenre, -s` | Target subgenre name (required unless using preset) |
| `--preset, -p` | Use named preset configuration |
| `--bpm` | Tempo (uses subgenre default if omitted) |
| `--momentum, -m` | Energy: Driving, Laid-back, Floating |
| `--instrumental, -i` | No vocals |
| `--vocals, -v` | Include vocals |
| `--vocal-mode` | Sung, Rap, Spoken |
| `--vocal-delivery` | Smooth, Raspy, Powerful, Intimate |
| `--drum-source` | Acoustic, Electronic, 808, Cinematic |
| `--seed` | Variation seed 1-10 (default: 1) |
| `--detail` | 1=minimal, 2=standard, 3=detailed |
| `--debug` | Show selection details |
| `--json` | Output as JSON |

## Data Files

Located in `assets/`:
- `genres.json` — 21 parent genres
- `subgenres.json` — 122 subgenres with defaults
- `subgenre_tags.json` — 1127 tags (Groove/Harmony/Production engines)
- `instruments.json` — 1223 instruments by subgenre
- `presets.json` — 9 named configurations

## Rules Reference

See `references/suno_v5_rules.md` for:
- Token hierarchy (strict ordering)
- Four-engine model (Groove, Harmony, Vocal, Production)
- User-approved overrides (instrumental mode, vocal requirements)
- Weight-aware selection logic

## Output Format

The generator produces:
```
STYLES: [comma-separated tokens in hierarchy order]
EXCLUDE: [negative prompts, if any]
```

Copy these directly into Suno v5 Custom Mode fields.

## Extending the Data

To add new subgenres or tags, edit the JSON files in `assets/`. Structure:

**subgenres.json entry:**
```json
{
  "subgenre_id": "SG0123",
  "name": "New Subgenre",
  "primary_genre_id": "G0001",
  "default_bpm": 120,
  "default_momentum": "Driving"
}
```

**subgenre_tags.json entry:**
```json
{
  "subgenre_id": "SG0123",
  "engine": "Groove",
  "tag_type": "Default",
  "phrase": "four on the floor, driving beat",
  "weight": 3
}
```
