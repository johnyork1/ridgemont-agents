# /youtube-script
## Skill: YouTube Video Script & Metadata Generator

**Trigger:** `/youtube-script [song_id] [artist_slug]`

**References:** `scripts/generate_youtube_script.py`, `data/youtube_script_config.json`, RULES.md §8

**What it does:** Generates a complete YouTube publishing package — optimized title, SEO description with timestamps, discovery tags, and a video script with intro/outro narration and scene breakdown — all tailored to the song's genre, mood, and artist brand.

### Procedure
1. Load manifest.json for song analysis (BPM, key, mood, segments, duration)
2. Load artist_profile.json for brand voice and visual identity
3. Load creative_brief.json if available for thematic direction
4. Load genre_defaults.json + genre_visual_identity.json for genre context
5. Parse lyrics file (.lrc) if available for quotable lines
6. Generate YouTube title (≤70 chars, genre-aware, SEO keywords)
7. Generate description with:
   - Hook line (first 2 lines visible in search)
   - Song timestamps mapped from segment analysis
   - Artist bio blurb from profile
   - Standard links block (streaming, socials, website)
   - Hashtags (genre + mood + artist)
8. Generate discovery tags (30 max, genre + mood + related artists)
9. Generate video script:
   - Intro narration (5-10s, sets mood and introduces artist)
   - Scene-by-scene breakdown aligned to segments
   - Outro with call-to-action (subscribe, like, playlist)
10. Save all outputs to catalog/{artist}/{song_id}/youtube/

### Output Files
| File | Contents |
|------|----------|
| youtube_title.txt | SEO-optimized title |
| youtube_description.txt | Full description with timestamps |
| youtube_tags.txt | Comma-separated discovery tags |
| youtube_script.json | Structured narration + scene breakdown |

### Error Handling
| Error | Action |
|-------|--------|
| No manifest | Abort — run analyze_catalog.py first |
| No artist profile | Use genre defaults for brand voice |
| No lyrics | Skip quotable lines section |
| No creative brief | Derive theme from mood + genre |
| Duration unknown | Omit timestamp section |

### Genre-Aware Title Patterns
| Genre | Pattern Example |
|-------|----------------|
| reggae | 🌴 Artist - "Song" (Official Reggae Video) |
| hip-hop | 🔥 Artist - Song [Official Music Video] |
| electronic | ⚡ Artist - Song (Official Visualizer) |
| jazz | 🎷 Artist - "Song" | Full Performance |
| rock | 🎸 Artist - Song (Official Video) |
| _default_ | 🎵 Artist - "Song" (Official Music Video) |

### Related Skills
`/audio-analyzer`, `/thumbnail-generator`, `/artist-profile-manager`, `/lyric-overlay`
