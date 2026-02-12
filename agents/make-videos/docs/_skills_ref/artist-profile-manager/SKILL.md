# /artist-profile-manager
## Skill: Artist Visual Profile Manager

**Trigger:** `/artist-profile-manager [artist] [genre]`

**References:** `scripts/generate_artist_profile.py`, RULES.md §7, tech audit §7

**What it does:** Creates, updates, and reviews artist_profile.json visual identity files.

### Procedure
1. Check if profile exists at catalog/{artist}/artist_profile.json
2. If missing: auto-generate from genre defaults (10+ genre templates)
3. Flag as auto_generated: true, human_reviewed: false
4. Include: brand colors, typography, visual motifs, camera style, ComfyUI workflow, SD prompt prefix
5. Set vertical_style (default: blur_fill)
6. Set W&B frequency (default: every_video with meme sign)

### Review Process
- Auto-generated profiles must be human-reviewed before hero releases
- Set human_reviewed: true after review
- Use --force to regenerate

### Related Skills
`/mood-mapper`, `/audio-analyzer`
