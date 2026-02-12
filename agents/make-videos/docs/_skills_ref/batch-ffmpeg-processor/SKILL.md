# /batch-ffmpeg-processor
## Skill: Batch FFmpeg Format Processor

**Trigger:** `/batch-ffmpeg-processor [song_id] [artist]`

**References:** `scripts/batch_produce.py`, RULES.md §4a, §6

**What it does:** Renders all 7 output formats from a master video using resolution-aware vertical strategy.

### Procedure
1. Load `manifest.json` from `catalog/{artist}/{song_id}/`
2. Verify pipeline status is `READY_FOR_ASSEMBLY`
3. Check render signature — skip if hash matches and all outputs exist
4. Probe master video resolution with ffprobe
5. Select vertical strategy: blur-fill (1080p) or center-crop (4K)
6. Render all 7 formats via `batch_produce.py`
7. Save assembly report and render signature
8. Update progress log

### Error Handling
| Error | Action |
|-------|--------|
| Master not found | Abort — run baseline_master.py first |
| FFmpeg failure | Log format, continue to next, report in assembly_report |
| Hash match | Skip render (use --force to override) |
| Preflight abort | Cannot render — fix missing assets |

### Related Skills
`/baseline-recipe-builder`, `/format-converter`, `/render-signature-manager`
