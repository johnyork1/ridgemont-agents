# Suno Prompt Agent

Lightweight Claude Desktop agent wrapper for the Suno v5.0 style prompt generator.

## Usage

Open this directory as a project in Claude Desktop. The CLAUDE.md file gives the agent knowledge of the prompt generator and asset databases.

## Script

- `../../scripts/generate_prompt.py` — Generates optimized Suno style prompts from genre, mood, BPM, and vocal parameters

## Assets

- `../../assets/subgenres.json` — 122 subgenres across 21 parent genres
- `../../assets/subgenre_tags.json` — Tag descriptors per subgenre
- `../../assets/instruments.json` — Instrument families and descriptors

## Requirements

- Python 3.13+ with `../../.venv/`
