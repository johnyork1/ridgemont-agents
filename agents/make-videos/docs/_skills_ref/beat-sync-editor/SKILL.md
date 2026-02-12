# /beat-sync-editor
## Skill: Beat-Synchronized Edit Decision List Generator

**Trigger:** `/beat-sync-editor [song_id] [format]`

**References:** `scripts/beat_sync_cuts.py`, RULES.md §6

**What it does:** Generates platform-optimized cut points using beat/onset data from analysis.

### Procedure
1. Load manifest.json for beat_times and onset_times
2. Select strategy: hook-first (TikTok/Short), best-segment (Reel), energy-peak (Sync Reel)
3. Find optimal segment via onset density clustering
4. Snap cut points to nearest beats
5. Generate EDL JSON with timestamps, fade settings, strategy metadata

### Error Handling
| Error | Action |
|-------|--------|
| No beat data | Use duration-based even distribution |
| Manifest missing | Abort — run analyze_catalog.py first |
| Duration < max | Use full song (no cutting needed) |

### Related Skills
`/audio-analyzer`, `/batch-ffmpeg-processor`
