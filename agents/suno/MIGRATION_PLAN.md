# Suno Genre Architecture Migration Plan

## Overview

This plan restructures the genre taxonomy to maximize musical control in Suno by ensuring genres represent true "engine drivers" — categories that reliably control rhythm templates, harmonic language, song form, and instrumentation defaults.

## Current State

| File | Count |
|------|-------|
| genres.json | 21 genres |
| subgenres.json | 122 subgenres |
| subgenre_tags.json | 1127 tags |
| aliases.json | does not exist |

## Target State

| File | Count |
|------|-------|
| genres.json | 14 engine genres |
| subgenres.json | 122 subgenres (30 reassigned) |
| subgenre_tags.json | ~1135 tags |
| aliases.json | NEW (~15 entries) |

---

## 1. genres.json Changes

### REMOVE (7 genres)

| Genre ID | Name | Reason |
|----------|------|--------|
| G0010 | Folk | Umbrella, not engine |
| G0012 | Latin | Regional umbrella |
| G0017 | World | Too vague |
| G0018 | Ambient | Texture/energy, not engine |
| G0019 | Indie | Modifier, not engine |
| G0020 | Alternative | Modifier, not engine |
| G0021 | Cinematic | Production style |

### KEEP (14 engine genres)

| Genre ID | Name |
|----------|------|
| G0001 | Pop |
| G0002 | Rock |
| G0003 | Hip Hop |
| G0004 | R&B |
| G0005 | Electronic |
| G0006 | Country |
| G0007 | Jazz |
| G0008 | Blues |
| G0009 | Classical |
| G0011 | Reggae |
| G0013 | Metal |
| G0014 | Punk |
| G0015 | Funk |
| G0016 | Gospel |

---

## 2. subgenres.json Changes — Parent Reassignment

| Subgenre | Current Parent | New Parent | Reasoning |
|----------|----------------|------------|-----------|
| Contemporary Folk | Folk | Country | Acoustic, storytelling tradition |
| Traditional Folk | Folk | Country | Acoustic roots |
| Indie Folk | Folk | Pop | Modern folk-pop hybrid |
| Anti-Folk | Folk | Rock | Raw, punk-adjacent energy |
| Salsa | Latin | Jazz | Complex harmony, improvisation |
| Bachata | Latin | Pop | Romantic pop structure |
| Bossa Nova | Latin | Jazz | Jazz harmony, smooth groove |
| Cumbia | Latin | Electronic | Dance-driven, repetitive |
| Merengue | Latin | Pop | Upbeat pop energy |
| Latin Pop | Latin | Pop | Pop structure |
| Afrobeat | World | Funk | Groove-driven, polyrhythmic |
| K-Pop | World | Pop | Pop production + structure |
| J-Pop | World | Pop | Pop structure |
| Celtic | World | Country | Acoustic, folk tradition |
| Bollywood | World | Pop | Pop production |
| Dark Ambient | Ambient | Electronic | Synthesis-based |
| Space Ambient | Ambient | Electronic | Synthesis-based |
| Drone | Ambient | Electronic | Synthesis-based |
| New Age | Ambient | Electronic | Synthesis-based |
| Indie Rock | Indie | Rock | Rock engine |
| Indie Electronic | Indie | Electronic | Electronic engine |
| Dream Pop | Indie | Pop | Pop structure with texture |
| Lo-fi Indie | Indie | Pop | Pop structure |
| Grunge | Alternative | Rock | Rock engine |
| Britpop | Alternative | Rock | Rock engine |
| Alternative Metal | Alternative | Metal | Metal engine |
| Industrial | Alternative | Electronic | Electronic engine |
| Epic Orchestral | Cinematic | Classical | Orchestral arrangement |
| Cinematic Electronic | Cinematic | Electronic | Electronic engine |
| Horror Score | Cinematic | Classical | Orchestral arrangement |
| Action Score | Cinematic | Classical | Orchestral arrangement |

---

## 3. subgenre_tags.json Changes

### ADD production/texture tags (from Cinematic)

```json
{"tag_type": "Production", "phrase": "cinematic reverb", "weight": 2}
{"tag_type": "Production", "phrase": "film score harmony", "weight": 2}
{"tag_type": "Production", "phrase": "minimal underscore", "weight": 1}
{"tag_type": "Production", "phrase": "sparse arrangement", "weight": 2}
{"tag_type": "Production", "phrase": "wide stereo imaging", "weight": 2}
{"tag_type": "Production", "phrase": "trailer music", "weight": 2}
{"tag_type": "Production", "phrase": "epic build", "weight": 2}
{"tag_type": "Production", "phrase": "tension and release", "weight": 2}
```

---

## 4. NEW: aliases.json

```json
[
  {"canonical": "Hip Hop", "aliases": ["hip-hop", "rap", "hiphop"]},
  {"canonical": "R&B", "aliases": ["rnb", "rhythm and blues", "contemporary r&b"]},
  {"canonical": "Electronic", "aliases": ["edm", "electronica", "dance music"]},
  {"canonical": "Rock", "aliases": ["rock and roll", "rock n roll"]},
  {"canonical": "Country", "aliases": ["country western", "americana"]},
  {"canonical": "Jazz", "aliases": ["jazzy"]},
  {"canonical": "Classical", "aliases": ["orchestral", "symphonic"]},
  {"canonical": "Metal", "aliases": ["heavy metal"]},
  {"canonical": "Punk", "aliases": ["punk rock"]},
  {"canonical": "Funk", "aliases": ["funky"]},
  {"canonical": "Gospel", "aliases": ["spiritual", "church music"]},
  {"canonical": "Blues", "aliases": ["bluesy"]},
  {"canonical": "Reggae", "aliases": ["reggae music"]}
]
```

---

## 5. Optional Future Enhancement: Role Field

Add a `role` field to categorize non-engine items:

```json
{"name": "Cinematic", "role": "production_modifier"}
{"name": "Indie", "role": "modifier"}
{"name": "Lo-fi", "role": "texture"}
{"name": "Latin", "role": "regional"}
```

Suggested roles:
- `engine` — true genre driver
- `subgenre` — narrowed style
- `regional` — geographic/cultural modifier
- `production_modifier` — mix/production style
- `texture` — sonic character

---

## Implementation Steps

1. **Backup** all current JSON files
2. **Update genres.json** — remove 7 non-engine genres
3. **Update subgenres.json** — reassign 30 subgenres to new parents
4. **Update subgenre_tags.json** — add cinematic production tags
5. **Create aliases.json** — new file with synonym mappings
6. **Update generate_prompt.py** — integrate aliases lookup
7. **Test** with sample prompts across all reassigned subgenres

---

## Why This Works

- **Suno** responds best to clear genre engines
- **Claude** performs better with orthogonal dimensions
- Eliminates dead prompts like "Indie Cinematic Alternative"
- Presets become meaningful behavior selectors
- Originality improves without sacrificing control
