# Suno v5.0 Prompt Generation Rules

## Core Philosophy
Suno v5 rewards structural precision and explicit musical terminology. Treat prompt fields as **engineering control parameters**, not creative writing.

**Bad**: "A song that feels like a rainy day in London"  
**Good**: "Downtempo trip-hop, 85 BPM, minor key, rain texture foley, wet reverb on snare, intimate male whisper vocals"

## Output Structure

The generator produces three distinct text blocks that map 1:1 to Suno v5 Custom Mode:

| Generator Output | Suno Field | Purpose |
|------------------|------------|---------|
| Style Prompt | Style of Music | Genre, instruments, tempo, mix |
| Exclude Prompt | Exclude Styles | Negative prompting |
| Lyrics Payload | Lyrics | Structure tags + lyrics (future) |

## Style Prompt Token Hierarchy

Assemble tokens in this **exact order** for maximum consistency:

1. **Genre Core** — Foundational style (e.g., Future Bass, Delta Blues, Tech House)
2. **Vibe & Mood** — Emotional texture (e.g., Uplifting, Melancholic, Aggressive)
3. **Tempo & Rhythm** — BPM and groove feel (e.g., 128 BPM, four-on-the-floor, syncopated swing)
4. **Instrumentation** — Specific instruments (e.g., Roland TR-808, distorted Fender Stratocaster)
5. **Vocal Character** — Explicit vocal description (e.g., Raspy male baritone, ethereal female soprano)
6. **Production Polish** — Mix and spatial tags (e.g., Wide stereo field, tape saturation, gated reverb)

## Four-Engine Model

The generator uses four engines to assemble tokens:

- **Groove Engine** — Rhythm, grid, pocket, feel
- **Harmony Engine** — Key, mode, chord progressions, melodic character
- **Vocal Engine** — Vocal type, delivery, texture (when applicable)
- **Production Engine** — Mix character, spatial treatment, era/finish

## User-Approved Overrides

These override the default guidebook rules:

### Instrumental Mode
- Use **positive instruction**: "Instrumental only, no lead vocals"
- Do NOT use giant exclusion lists for instrumental mode
- Do NOT force "Male" or "Female" in exclusions for instrumental

### Vocal Descriptor Requirements
- Vocal descriptors required **only when vocals are explicitly requested**
- Do NOT require vocal descriptors by default
- Tiered pass criteria based on vocal intent

## Exclude Prompt Logic

Populate Exclude field only when specific constraints are active:

| Condition | Exclude Values |
|-----------|----------------|
| Instrumental mode | "No Vocals" (positive framing preferred) |
| Instrumental + safety | "No Rap, No Spoken Word" |
| Vocal Mode = Rap | "No Singing, No Choir" |
| Acoustic mode | "Synth, Electronic, Drum Machine, Autotune" |
| Strict genre purity | Conflicting genres (e.g., Metal → exclude Pop, Electronic) |

## Weight-Aware Selection

Tags and instruments have Weight values (1-3):
- **Weight 3** = Core/essential (selected first)
- **Weight 2** = Common/recommended
- **Weight 1** = Optional/flavor

Selection formula: `rank = (4 - weight) * 100000 + rowIndex`  
Lower rank = higher priority. Variation seed selects k-th item by rank.

## Deterministic Variety

The **Variation Seed** (1-10) provides reproducible variety:
- Same seed + same inputs = same output
- Different seeds = different tag/instrument selections within the same subgenre pool

## Validation Rules

A generated prompt passes validation if it contains:
- At least one Genre token
- At least one Instrument token
- Vocal descriptor (only if vocals explicitly requested)
