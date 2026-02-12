# /safe-zone-validator
## Skill: Safe Zone Compliance Validator

**Trigger:** `/safe-zone-validator [format_type]`

**References:** `scripts/safe_zone.py`, RULES.md §4b, tech audit §9a

**What it does:** Validates and auto-snaps overlays into platform-safe regions.

### Safe Zones
**Horizontal (16:9 master):**
- Center 56%: x = 424-1496px at 1920px width

**Vertical Social UI (9:16 outputs):**
- Top 10% → AVOID (Following/For You tabs)
- Right 15% → AVOID (Like/Comment/Share)
- Bottom 25% → AVOID (Caption, music info)
- **Content Safe Zone:** Y 10-65%, X 10-85%

### Contract
Every overlay script MUST call `enforce_safe_zone()` with correct `format_type` before compositing. Auto-snap moves violations back into bounds.

### Related Skills
`/batch-ffmpeg-processor`, `/character-animator`, `/lyric-overlay`
