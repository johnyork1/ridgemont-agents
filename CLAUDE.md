# Ridgemont Studio

Music production pipeline and AI agent workspace.

## Project Structure

```
agents/
  vinnie/            Dr. Vinnie Boombatz medical AI agent (Claude plugin)
  make-videos/       Make Videos pipeline agent (Claude Desktop project)
  suno/              Suno prompt generator agent (Claude Desktop project)
assets/              Character sprites, subgenre/instrument JSON databases
catalog/             Production catalog — artist/song dirs with manifests + rendered media
data/                Config JSONs (recipes, mood maps, genre defaults) + raw character sheets
docs/                Project documentation (AGENTS.md, STRUCTURE.md)
scripts/             18 Python scripts — core Make Videos pipeline
output/              Generated reports and production logs
```

## Python Environment

```bash
PY=.venv/bin/python3        # Python 3.13, all deps installed
```

All scripts use `--project-root` (default: derived from script location). Pass explicitly when calling from outside the project directory.

Relative file path arguments (mp3 paths, background images, LRC files) resolve against `--project-root`.

## Make Videos Pipeline

The pipeline processes songs in stages. Each stage reads/updates `catalog/{artist}/{song}/manifest.json`.

```bash
# Step 1: Ingest audio into catalog
$PY scripts/ingest_song.py path/to/song.mp3 --artist "Artist" --title "Title" --genre reggae

# Step 2: Analyze (audio features, mood, character assignment)
$PY scripts/analyze_catalog.py --song-id title --artist artist

# Step 3: Render master video (Ken Burns + characters + energy-reactive bounce)
$PY scripts/baseline_master.py --song-id title --artist artist

# Step 4: Render short clips (beat-synced TikTok/Shorts cuts)
$PY scripts/beat_sync_cuts.py --song-id title --artist artist

# Steps 1-4 combined (batch)
$PY scripts/batch_produce.py --input-dir /path/to/mp3s

# Full catalog re-analysis
./ingest_catalog.sh
```

## Rendering Extras

```bash
# Pro video (background image + synced lyrics)
$PY scripts/render_pro_video.py --song-id title --artist artist --bg assets/bg.png --lrc catalog/artist/title/lyrics.lrc

# Lyric overlay, visualizer, thumbnails, artist profiles, meme signs
$PY scripts/lyric_video.py --song-id title --artist artist
$PY scripts/visualizer.py --song-id title --artist artist
$PY scripts/generate_thumbnails.py --batch
$PY scripts/generate_artist_profile.py --batch
$PY scripts/meme_sign_render.py --text "Text" --song-id title --artist artist

# YouTube metadata
$PY scripts/generate_youtube_script.py --song-id title --artist artist
```

## Utilities

```bash
# Suno v5.0 prompt generator
$PY scripts/generate_prompt.py --genre reggae --mood chill --bpm 136
$PY scripts/generate_prompt.py --genre hip-hop --mood aggressive --json

# Preflight validation
$PY scripts/preflight_validator.py

# Character sprite extraction (from raw sheets)
$PY scripts/prep_characters.py
```

## Dr. Vinnie Boombatz Agent

Medical AI agent in `agents/vinnie/`. Open that directory as a project in Claude Desktop to activate the full agent (8 slash commands, 10 skills, PubMed MCP).

```bash
# Generate medical report from patient notes
$PY agents/vinnie/src/generate_report.py

# With custom patient directory
VINNIE_PATIENT_DIR=/path/to/notes $PY agents/vinnie/src/generate_report.py
```

## Make Videos Agent

Video pipeline agent in `agents/make-videos/`. Open that directory as a project in Claude Desktop.

## Suno Agent

Prompt generator agent in `agents/suno/`. Open that directory as a project in Claude Desktop.

## Key Data Files

| File | Purpose |
|------|---------|
| `data/baseline_recipe.json` | Video resolution, FPS, timing, codec settings |
| `data/mood_map.json` | Mood-to-visual mapping (colors, energy thresholds) |
| `data/genre_defaults.json` | Per-genre character poses and visual defaults |
| `data/beat_sync_strategies.json` | Short-form cut strategies by genre |
| `assets/subgenres.json` | 122 subgenres across 21 parent genres (Suno) |
| `assets/instruments.json` | Instrument database with families/descriptors (Suno) |
| `output/production_log.csv` | Batch production run log |

## Shared Utilities

`scripts/cache_utils.py` exports: `load_cache`, `save_cache`, `file_hash`, `resolve_path`, `get_default_cache_path`, `make_entry`

Use `resolve_path(path, project_root)` to normalize relative vs absolute paths in any script.
