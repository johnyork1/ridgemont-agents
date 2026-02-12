# /character-animator
## Skill: W&B Character Animation Engine

**Trigger:** `/character-animator [song_id]`

**References:** RULES.md §5, tech audit §8d

**What it does:** Applies mandatory "Alive" animation to all character overlays.

### Animation Layers (MANDATORY)
1. **Breathing:** 2-second sine-wave scale (98% → 102%) — `1.0 + 0.02 * sin(2πt/2.0)`
2. **Beat Bounce:** 5-10px Y-axis offset on kick drum beats from librosa
3. **Entrance:** Bounce-in from bottom, ease-out (0.5 sec)
4. **Exit:** Fade out (0.3 sec)

### Key Rule
**Static PNGs are NEVER acceptable.** Every character overlay must have breathing animation at minimum.

### Integration Tiers
| Tier | Where | Method | Cost |
|------|-------|--------|------|
| Every video | End card + intro | Sprite breathing/bounce | Free |
| Selected | Beat drops | Pre-animated Kling clips | ~1-2/clip |
| Hero releases | Throughout | Full Kling 3.0 / Cartoon Animator | 0-149 |

### Related Skills
`/character-asset-factory`, `/meme-sign-generator`, `/beat-sync-editor`
