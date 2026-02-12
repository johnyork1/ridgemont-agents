# /audio-analyzer
## Skill: Audio Analysis Engine

**Trigger:** `/audio-analyzer [song_id] [audio_path]`

**References:** `scripts/analyze_catalog.py`, RULES.md §3 Step 2, §4d

**What it does:** Runs librosa analysis with confidence scoring, mood mapping, and preflight validation.

### Procedure
1. Load audio with librosa
2. Extract BPM, beats, onsets, chroma, energy
3. Compute key confidence and mode confidence
4. If reliable: run mood_map.json rule matching
5. If unreliable: log warning, use genre defaults
6. Apply priority chain (Creative Brief → Artist Profile → Mood Map → Genre → Default)
7. Build manifest with project-root-relative paths
8. Run preflight validation on all asset paths
9. Save manifest.json and update progress log

### Safety Valve
- key_confidence < 0.15 OR mode_confidence < 0.10 → analysis_reliable: false
- Unreliable → skip mood map → genre defaults
- BPM and beats ALWAYS reliable

### Related Skills
`/mood-mapper`, `/artist-profile-manager`, `/safe-zone-validator`
