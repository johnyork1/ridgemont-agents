# /mood-mapper
## Skill: Audio-to-Mood Pose Mapper

**Trigger:** `/mood-mapper [song_id]`

**References:** `data/mood_map.json`, RULES.md §4d, §7

**What it does:** Maps audio analysis results to W&B character poses via mood rules.

### Procedure
1. Load analysis from manifest (BPM, key, energy, genre)
2. Check analysis_reliable flag — if false, skip to genre defaults
3. Evaluate mood_map.json rules in order (first match wins)
4. Rules: hype, happy, sad, moody, chill, explosive, sophisticated
5. Return pose paths (project-root-relative) for Weeter, Blubby, Together
6. Apply priority chain overrides if Creative Brief or Artist Profile present

### Mood Rules
| Mood | Condition |
|------|-----------|
| Hype | BPM > 140 AND major key |
| Happy | BPM > 120 AND major key |
| Sad | BPM < 90 AND minor key |
| Moody | BPM 90-120 AND minor key |
| Chill | BPM 90-120 AND major key |
| Explosive | Energy high AND BPM > 130 |
| Sophisticated | Genre jazz/classical |

### Related Skills
`/audio-analyzer`, `/character-animator`
