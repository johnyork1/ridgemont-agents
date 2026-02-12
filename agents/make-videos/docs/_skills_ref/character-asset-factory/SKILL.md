# /character-asset-factory
## Skill: W&B Character Asset Factory

**Trigger:** `/character-asset-factory`

**References:** `scripts/prep_characters.py`, RULES.md §5, tech audit §8b

**What it does:** Transforms raw character sheets into transparent PNG library using rembg + OpenCV.

### Procedure
1. Scan data/raw_sheets/ for character images
2. Parse filename → character name + emotion (Weeter-happy.jpg → weeter/happy/)
3. Strip background using rembg AI removal
4. Auto-detect individual poses via OpenCV contour detection
5. Apply manual overrides from slice_overrides.json if present
6. Save transparent PNGs to assets/characters/{char}/{emotion}/
7. Report: rename auto-numbered files to descriptive names

### One-Time Setup
Run ONCE during initial setup, then only when new character sheets are added.

### Related Skills
`/character-animator`, `/mood-mapper`
