# /ingest-song
## Skill: Song Ingestion Pipeline

**Trigger:** `/ingest-song [song_id] [audio_path]`

**References:** `scripts/ingest_song.py`, RULES.md §3 Step 1

**What it does:** Ingests a new song into the Make Videos pipeline — copies audio, creates directory structure, checks for Creative Brief, and prepares for analysis.

### Procedure
1. Validate audio file exists and is WAV/MP3/FLAC format
2. Create catalog directory: `catalog/{artist}/{song_id}/`
3. Copy audio to song directory with standardized naming
4. Check for `creative_brief.json` in source directory (highest priority override)
5. Check for existing `artist_profile.json` — flag if missing
6. Initialize `progress_log.json` with ingestion timestamp
7. Write initial metadata (artist, title, genre, source path)
8. Report: ready for Step 2 (Analysis)

### Error Handling
| Error | Action |
|-------|--------|
| Audio file not found | Abort with clear error message |
| Unsupported format | Abort — only WAV/MP3/FLAC accepted |
| Song already ingested | Skip unless --force flag provided |
| No artist profile | Log warning — auto-generate during analysis |
| Creative Brief present | Log: "Creative Brief found — will override defaults" |

### Related Skills
`/audio-analyzer`, `/artist-profile-manager`
