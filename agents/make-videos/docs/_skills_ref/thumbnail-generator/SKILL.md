# /thumbnail-generator
## Skill: Branded Thumbnail Generator

**Trigger:** `/thumbnail-generator [song_id] [artist] [title]`

**References:** `scripts/generate_thumbnails.py`, RULES.md §8

**What it does:** Creates branded thumbnails for YouTube, TikTok, Instagram, and Spotify using artist profile colors.

### Procedure
1. Load artist_profile.json for brand colors
2. Load manifest for character pose paths
3. Generate thumbnails for each platform size
4. Apply artist brand colors as background/accent
5. Add song title + artist text within safe zones
6. Overlay W&B together pose on thumbnails
7. Save to catalog/{artist}/{song_id}/thumbnails/

### Error Handling
| Error | Action |
|-------|--------|
| No artist profile | Use default Ridgemont brand colors |
| No character pose | Generate text-only thumbnails |
| Font missing | Fall back to system default fonts |

### Related Skills
`/artist-profile-manager`, `/character-asset-factory`
