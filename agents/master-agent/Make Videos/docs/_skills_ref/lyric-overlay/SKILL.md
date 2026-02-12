# /lyric-overlay
## Skill: Lyric Video Overlay Generator

**Trigger:** `/lyric-overlay [song_id] [lyrics_file]`

**References:** `scripts/lyric_video.py`, RULES.md §4b, §6

**What it does:** Generates lyric video with timed text overlay within Safe Zone.

### Procedure
1. Parse lyrics file (timestamped or plain text)
2. If plain text: distribute over beats from manifest
3. Build FFmpeg drawtext filter chain with fade in/out
4. Position text within horizontal Safe Zone (center 56%)
5. Render lyric video from master
6. Save to outputs/lyric_video.mp4

### Error Handling
| Error | Action |
|-------|--------|
| No lyrics file | Abort — lyric video requires text input |
| No master video | Abort — run baseline_master.py first |
| No beat data | Distribute lyrics evenly over duration |

### Related Skills
`/audio-analyzer`, `/safe-zone-validator`
