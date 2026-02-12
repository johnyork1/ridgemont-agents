# /render-signature-manager
## Skill: Hash-Based Render Signature Manager

**Trigger:** `/render-signature-manager [song_id] [action]`

**References:** `scripts/render_signature.py`, RULES.md §4c, tech audit §9b

**What it does:** Manages SHA256 hash-based idempotency to prevent re-rendering unchanged content.

### How It Works
1. Compute: `SHA256(audio_bytes + artist_profile_JSON + manifest_JSON)`
2. Truncate to 16 hex characters
3. Store as `render_signature.txt` in output folder
4. Before render: compare current hash to stored hash
5. If match AND all 7 output files exist → SKIP
6. If mismatch → RE-RENDER
7. Support --force flag to override

### Actions
- `check` — Compare hashes, report if render needed
- `save` — Save current signature after successful render
- `force` — Clear signature to force next render

### Related Skills
`/batch-ffmpeg-processor`
