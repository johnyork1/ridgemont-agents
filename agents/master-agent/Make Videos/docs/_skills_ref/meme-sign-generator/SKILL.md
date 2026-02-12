# /meme-sign-generator
## Skill: Meme Sign End Card Generator

**Trigger:** `/meme-sign-generator [title] [artist]`

**References:** `scripts/meme_sign_render.py`, RULES.md §5

**What it does:** Renders the Meme Sign end card with Song Title + Artist Name.

### Procedure
1. Load blank_sign.png template from assets/characters/together/meme_sign/
2. Render song title (bold, centered, black)
3. Render artist name below (regular, centered, gray)
4. Save rendered sign PNG
5. Sign gets breathing/bounce animation when composited into video

### Key Rules
- EVERY video ends with the Meme Sign
- Same breathing/bounce animation as character overlays
- Positioned within Safe Zone for each format type

### Related Skills
`/character-animator`, `/safe-zone-validator`
