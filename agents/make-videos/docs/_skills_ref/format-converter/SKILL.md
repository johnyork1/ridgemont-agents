# /format-converter
## Skill: Resolution-Aware Format Converter

**Trigger:** `/format-converter [master_path] [format]`

**References:** `scripts/batch_produce.py`, RULES.md §4a

**What it does:** Converts master 16:9 video to any target format with proper vertical strategy.

### Procedure
1. Probe master resolution via ffprobe
2. Select vertical strategy (blur-fill / center-crop / stacked)
3. Build appropriate FFmpeg command
4. Execute render with quality settings (CRF 18, medium preset)
5. Verify output file size and format

### Key Rules
- 1080p source → ALWAYS blur-fill (never upscale 607px crop)
- 4K source → center-crop
- artist_profile.json `vertical_style: stacked` → stacked layout
- All vertical overlays → Social UI Safe Zone

### Related Skills
`/safe-zone-validator`, `/batch-ffmpeg-processor`
