# /baseline-recipe-builder
## Skill: Phase 1 Baseline Master Video Builder

**Trigger:** `/baseline-recipe-builder [song_id] [artist]`

**References:** `scripts/baseline_master.py`, RULES.md §9

**What it does:** Generates a professional master video using the Phase 1 Baseline Recipe.

### The Baseline Recipe
1. **Background:** Ken Burns pan (zoom 1.0→1.15 + drift) on album art or genre landscape
2. **Energy:** Beat-synced brightness pulse via FFmpeg eq filter
3. **Characters:** W&B breathing/bounce at intro (3s) + Meme Sign end card (5s)
4. **Branding:** Artist name + song title within Safe Zone
5. **Audio:** Full track

### Why This Matters
This guarantees every song has a branded video on Day 1 with ZERO AI dependency.

### Error Handling
| Error | Action |
|-------|--------|
| No album art | Generate solid color background from artist profile |
| Complex filter fail | Retry with simplified Ken Burns only |
| No manifest | Abort — run analyze_catalog.py first |

### Related Skills
`/audio-analyzer`, `/character-animator`, `/meme-sign-generator`
