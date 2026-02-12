# Make Videos Agent

Lightweight Claude Desktop agent wrapper for the Ridgemont Studio music video production pipeline.

## Usage

Open this directory as a project in Claude Desktop. The CLAUDE.md file gives the agent full knowledge of the 18-script pipeline in `../../scripts/`.

## Scripts

See `../../scripts/` for the full pipeline. Key entry points:

- `ingest_song.py` — Import audio into catalog
- `analyze_catalog.py` — Audio analysis + mood + character assignment
- `baseline_master.py` — Render master video
- `beat_sync_cuts.py` — Render short-form clips
- `batch_produce.py` — Run steps 1-4 in sequence

## Requirements

- Python 3.13+ with `../../.venv/`
- ffmpeg (system)
