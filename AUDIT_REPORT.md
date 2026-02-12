# Ridgemont Studio — Agent & Script Audit Report

**Date:** 2026-02-12 (updated after Cowork migration)
**Auditor:** Claude Opus 4.6
**Project root:** `/Users/johnyork/Ridgemont_Studio`
**Repo:** https://github.com/johnyork1/ridgemont-agents

---

## 1. Agent & Script Inventory

### All Agents (11 + shared skills)

| # | Agent | Directory | Type | Entry Point | MCP |
|---|-------|-----------|------|-------------|-----|
| 1 | Dr. Vinnie Boombatz | `agents/vinnie/` | Claude Desktop plugin | `./run.sh` or Claude Desktop | PubMed |
| 2 | Dewey, Cheatham & Howe | `agents/dewey-cheatham-howe/` | Claude Desktop plugin | `./run.sh` or Claude Desktop | CourtListener |
| 3 | Make Videos | `agents/make-videos/` | Claude Desktop project | `./run.sh` → `scripts/` | — |
| 4 | Suno | `agents/suno/` | Claude Desktop project | `./run.sh` or `scripts/generate_prompt.py` | — |
| 5 | Make Music | `agents/make-music/` | MIDI workspace | `./run.sh` or `generate_getting_old.py` | — |
| 6 | Master Agent | `agents/master-agent/` | Ecosystem orchestrator | `./run.sh` or `daily_monitor.py` | — |
| 7 | Catalog Manager | `agents/catalog-manager/` | Catalog database | `./run.sh` or `scripts/catalog_manager.py` | — |
| 8 | X-Posts | `agents/x-posts/` | Crypto Twitter agent | `./run.sh` or Claude Desktop | — |
| 9 | Frozen Cloud Website | `agents/frozen-cloud-website/` | Static artist site | `./run.sh` (opens index.html) | — |
| 10 | Frozen Cloud Portal | `agents/frozen-cloud-portal/` | Streamlit portal | `./run.sh` or `streamlit run app.py` | — |
| 11 | Ridgemont Studio Website | `agents/ridgemont-website/` | Public label site | `./run.sh` (opens index.html) | — |
| — | Shared Skills | `agents/.skills/` | Skill library | x-images, x-voice, pushgit | — |

### Migration Source

All agents migrated from `/Users/johnyork/My Drive/Ridgemont Studio/Claude Cowork` on 2026-02-12. Google Drive source is untouched (copy-only migration).

| Cowork Source | Repo Destination | Notes |
|--------------|-----------------|-------|
| `dewey-cheatham-howe` | `agents/dewey-cheatham-howe/` | Direct copy |
| `dr-vinnie-boombatz` | `agents/vinnie/` | Previously migrated from Docker |
| `Frozen Cloud Website` | `agents/frozen-cloud-website/` | Normalized name |
| `frozen-cloud-portal` | `agents/frozen-cloud-portal/` | Excluded venv/, .git/ |
| `Make-Music` | `agents/make-music/` | Normalized name |
| `Master Agent` | `agents/master-agent/` | Excluded .pip_*, *.mp4 (~80MB), duplicate Make Videos/ removed |
| `Ridgemont Catalog Manager` | `agents/catalog-manager/` | Excluded node_modules/, venv/, .git/, backups/, .env |
| `Ridgemont Studio Website` | `agents/ridgemont-website/` | Excluded node_modules/, .git/ |
| `Suno Studio` | `agents/suno/` | Merged into existing wrapper (assets, references, scripts added) |
| `X-Posts` | `agents/x-posts/` | Direct copy |
| `.skills` | `agents/.skills/` | Shared skills (x-images, x-voice, pushgit) |
| `pushgit.sh` | `scripts/pushgit.sh` | Utility script |
| `vinnie_integration.sh` | — | Skipped (obsolete Docker migration script) |

### Make Videos Pipeline (18 scripts)

| Script | Language | CLI Entrypoint | Inputs | Outputs |
|--------|----------|---------------|--------|---------|
| `ingest_song.py` | Python | `--artist --title mp3_path` | MP3 file, `data/` configs | `catalog/{artist}/{song}/manifest.json` + copied audio |
| `analyze_catalog.py` | Python | `--song-id --artist [--project-root]` | manifest, audio, `data/mood_map.json`, `data/genre_defaults.json`, `assets/characters/` | Updated manifest (stage: analyzed), cache |
| `baseline_master.py` | Python | `--song-id --artist [--project-root]` | manifest, `data/baseline_recipe.json`, `data/mood_map.json`, characters, audio | `catalog/{a}/{s}/{a}_{s}_master.mp4` |
| `beat_sync_cuts.py` | Python | `--song-id --artist [--strategy] [--project-root]` | manifest, `data/beat_sync_strategies.json`, audio | `catalog/{a}/{s}/{a}_{s}_short.mp4` |
| `batch_produce.py` | Python | `--input-dir [--project-root] [--genre] [--limit]` | Audio dir, all data/ configs | Runs steps 1-4 in sequence |
| `render_pro_video.py` | Python | `--song-id --artist --bg --lrc [--project-root]` | manifest, background image, LRC file, characters, audio | `catalog/{a}/{s}/{a}_{s}_pro.mp4` |
| `lyric_video.py` | Python | `--song-id --artist [--lrc] [--project-root]` | manifest, `data/lyric_config.json`, `data/baseline_recipe.json`, characters | `catalog/{a}/{s}/lyric.mp4` |
| `visualizer.py` | Python | `--song-id --artist [--project-root]` | manifest, `data/baseline_recipe.json`, `data/output_formats.json`, characters | `catalog/{a}/{s}/viz.mp4` |
| `generate_thumbnails.py` | Python | `--song-id --artist [--batch] [--project-root]` | manifest, `data/genre_visual_identity.json` | `catalog/{a}/{s}/thumb.png` |
| `generate_artist_profile.py` | Python | `--artist [--batch] [--project-root]` | manifests, `data/genre_visual_identity.json` | `catalog/{a}/profile.png` |
| `meme_sign_render.py` | Python | `--text [--song-id --artist] [--project-root]` | manifest, `data/genre_visual_identity.json` | `catalog/{a}/{s}/meme_sign.{png,mp4}` |
| `generate_youtube_script.py` | Python | `--song-id --artist [--project-root]` | manifest, `data/youtube_script_config.json`, LRC | `catalog/{a}/{s}/youtube/*.txt` |
| `generate_prompt.py` | Python | `--genre [--mood --bpm --subgenre --json]` | `assets/subgenres.json`, `assets/subgenre_tags.json`, `assets/instruments.json` | stdout (style prompt text or JSON) |
| `prep_characters.py` | Python | `[--project-root]` | `data/raw_sheets/` | `assets/characters/` |
| `preflight_validator.py` | Python | `[--project-root]` | project structure | stdout (validation report) |
| `cache_utils.py` | Python | (library) | `catalog/.catalog_cache.json` | `catalog/.catalog_cache.json` |
| `render_signature.py` | Python | (library) | audio path, manifest data | returns hash string |
| `safe_zone.py` | Python | (library) | none | returns geometry bounds |

### Shell Orchestrators

| Script | Calls | Purpose |
|--------|-------|---------|
| `ingest_catalog.sh` | `analyze_catalog.py` per song | Walk catalog, analyze all songs |
| `ingest_vinnie.sh` | `.venv/bin/python3 -i` or `--script` | Launch Vinnie Python env |
| `scripts/pushgit.sh` | git commands | Sync catalog.json across portals |

---

## 2. Dependency Status

### Python (primary runtime)

| Component | Version | Status |
|-----------|---------|--------|
| Python | 3.13.3 | OK |
| venv | `.venv/bin/python3` | OK |
| pip check | No broken requirements | OK |

### Third-party packages (all OK)

| Package | Used by | Status |
|---------|---------|--------|
| opencv-python-headless | prep_characters.py | OK |
| numpy | prep_characters.py, analyze_catalog.py | OK |
| rembg | prep_characters.py | OK |
| librosa | analyze_catalog.py (lazy) | OK |
| soundfile | analyze_catalog.py (lazy) | OK |
| onnxruntime | rembg dependency | OK |
| Pillow | general image ops | OK |
| openai | Vinnie agent | OK |
| requests | Vinnie agent | OK |
| python-docx | Vinnie agent | OK |
| pyyaml | Vinnie agent | OK |
| scipy | librosa dependency | OK |
| scikit-learn | librosa dependency | OK |

### System tools

| Tool | Version | Used by | Status |
|------|---------|---------|--------|
| ffmpeg | 8.0.1 | baseline_master, beat_sync_cuts, lyric_video, visualizer, meme_sign_render, generate_thumbnails, generate_artist_profile, render_pro_video | OK |
| node | 25.4.0 | ridgemont-website (worker.js), catalog-manager | OK |
| npm | 11.7.0 | ridgemont-website, catalog-manager | OK |

### Missing packages

None. All imports verified.

### Install instructions (fresh setup)

```bash
cd /Users/johnyork/Ridgemont_Studio
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
# System: brew install ffmpeg (already present)
```

---

## 3. Path & IO Contract Analysis

### Docker path remnants (`/app/`)

**Status: CLEAN.** No `/app/` references in any project source file. All Docker paths were removed during migration.

### Path strategy by script

All pipeline scripts follow a consistent pattern:
```python
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT_DEFAULT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
```

Plus `--project-root` argparse override. This means scripts work correctly when called from any directory, as long as `--project-root` is passed (or they're invoked from the project root).

### Output destinations

| Write target | Scripts | Notes |
|-------------|---------|-------|
| `catalog/{artist}/{song}/` | All pipeline scripts (manifests, videos, thumbnails) | Correct — co-located with source media |
| `catalog/.catalog_cache.json` | cache_utils.py | Correct — catalog-level metadata |
| `output/vinnie_report.txt` | src/generate_report.py | Correct — goes to output/ |
| `output/production_log.csv` | ingest_catalog.sh, batch_produce.py | Correct — goes to output/ |
| `assets/characters/` | prep_characters.py | Correct — generates character assets |

**No scripts write to unexpected locations.** All output stays within the project tree.

### Issues found

| Severity | Script | Issue | Status |
|----------|--------|-------|--------|
| ~~HIGH~~ | `prep_characters.py` | ~~Hardcoded relative paths — no `--project-root`.~~ | FIXED 2026-02-12 |
| ~~MODERATE~~ | `ingest_song.py` | ~~`mp3_path` positional arg relative to cwd, not project root.~~ | FIXED 2026-02-12 |
| ~~MODERATE~~ | `render_pro_video.py` | ~~`--bg` and `--lrc` args relative to cwd, not project root.~~ | FIXED 2026-02-12 |
| LOW | `generate_prompt.py` | Assets path derived from `__file__` parent — works correctly but hardcoded structure assumption (`../assets/`). | Open |
| ~~LOW~~ | `ingest_vinnie.sh` | ~~No `PYTHONPATH` setup for script mode.~~ | FIXED 2026-02-12 |

### Cross-script import chain

```
cache_utils.py ← ingest_song.py, analyze_catalog.py, baseline_master.py, batch_produce.py
render_signature.py ← baseline_master.py, lyric_video.py, batch_produce.py
```

All importing scripts use `sys.path.insert(0, SCRIPT_DIR)` — imports work from any working directory.

---

## 4. How to Run (one-liners)

```bash
# All commands assume: cd /Users/johnyork/Ridgemont_Studio
PY=.venv/bin/python3

# ── Pipeline ──────────────────────────────────────────────

# Step 1: Ingest a new song (relative paths resolve against --project-root)
$PY scripts/ingest_song.py --artist "frozen-cloud" --title "New Song" path/to/song.mp3 --project-root .

# Step 2: Analyze a song (audio features, mood, characters)
$PY scripts/analyze_catalog.py --song-id new-song --artist frozen-cloud --project-root .

# Step 3: Render master video
$PY scripts/baseline_master.py --song-id new-song --artist frozen-cloud --project-root .

# Step 4: Render short clips
$PY scripts/beat_sync_cuts.py --song-id new-song --artist frozen-cloud --project-root .

# Steps 1-4 combined (batch)
$PY scripts/batch_produce.py --input-dir /path/to/mp3s --project-root .

# Run full catalog analysis
./ingest_catalog.sh

# ── Rendering extras ──────────────────────────────────────

# Pro video (--bg and --lrc resolve against --project-root when relative)
$PY scripts/render_pro_video.py --song-id new-song --artist frozen-cloud --bg assets/bg.png --lrc catalog/frozen-cloud/new-song/lyrics.lrc --project-root .

# Lyric overlay video
$PY scripts/lyric_video.py --song-id new-song --artist frozen-cloud --project-root .

# Audio visualizer video
$PY scripts/visualizer.py --song-id new-song --artist frozen-cloud --project-root .

# Thumbnail
$PY scripts/generate_thumbnails.py --song-id new-song --artist frozen-cloud --project-root .

# All thumbnails (batch)
$PY scripts/generate_thumbnails.py --batch --project-root .

# Artist profile card
$PY scripts/generate_artist_profile.py --artist frozen-cloud --project-root .

# Meme sign
$PY scripts/meme_sign_render.py --text "Hello World" --song-id new-song --artist frozen-cloud --project-root .

# YouTube metadata
$PY scripts/generate_youtube_script.py --song-id new-song --artist frozen-cloud --project-root .

# ── Utilities ─────────────────────────────────────────────

# Suno prompt generator
$PY scripts/generate_prompt.py --genre reggae --mood chill --bpm 136

# Suno prompt (JSON output)
$PY scripts/generate_prompt.py --genre hip-hop --mood aggressive --vocals "male rap" --json

# Preflight validation
$PY scripts/preflight_validator.py --project-root .

# Prep character sprites (from raw sheets — works from any directory)
$PY scripts/prep_characters.py --project-root .

# ── Agents ────────────────────────────────────────────────

# Any agent (run its entrypoint)
cd agents/<name> && ./run.sh

# Vinnie: generate medical report
$PY agents/vinnie/src/generate_report.py

# Vinnie: custom patient dir
VINNIE_PATIENT_DIR=/path/to/notes $PY agents/vinnie/src/generate_report.py

# Vinnie: interactive Python with venv
./ingest_vinnie.sh

# Catalog Manager
cd agents/catalog-manager && python3 scripts/catalog_manager.py

# Master Agent: daily ecosystem audit
cd agents/master-agent && python3 daily_monitor.py

# Frozen Cloud Portal
cd agents/frozen-cloud-portal && streamlit run app.py

# Suno prompt (agent-local copy)
cd agents/suno && python3 scripts/generate_prompt.py --genre reggae --mood chill
```

---

## 5. Fix History

| # | Issue | Severity | Status |
|---|-------|----------|--------|
| 1 | `prep_characters.py` — no `--project-root` | HIGH | FIXED 2026-02-12 |
| 2 | `ingest_song.py` — `mp3_path` relative to cwd | MODERATE | FIXED 2026-02-12 |
| 3 | `render_pro_video.py` — `--bg`/`--lrc` relative to cwd | MODERATE | FIXED 2026-02-12 |
| 4 | `ingest_vinnie.sh` — no PYTHONPATH | LOW-MODERATE | FIXED 2026-02-12 |
| 5 | No root `CLAUDE.md` | MODERATE | FIXED 2026-02-12 |
| 6 | No shared `resolve_path` utility | LOW | FIXED 2026-02-12 |
| 7 | `.venv` in `.claudeignore` | LOW | ALREADY FIXED |
| 8 | `production_log.csv` at root | LOW | FIXED 2026-02-12 |
| 9 | Stale `__pycache__/` | COSMETIC | FIXED 2026-02-12 |
| 10 | Node.js unused | INFO | NO ACTION |
| 11 | Agent restructure (nested agents/, generate_report.py location, docx) | MODERATE | FIXED 2026-02-12 |
| 12 | Cowork migration (8 new agents, Suno merge, .skills, docs) | MAJOR | FIXED 2026-02-12 |
| 13 | Master Agent duplicate Make Videos/ (51 files) | LOW | FIXED 2026-02-12 — skills refs preserved in make-videos/docs/ |
| 14 | Master Agent test artifacts (.writetest, writetest2.txt) | COSMETIC | FIXED 2026-02-12 |

---

## 6. Structural Health Summary

| Category | Status |
|----------|--------|
| Docker path remnants | CLEAN — none found |
| Python imports | CLEAN — all 18 pipeline scripts import successfully |
| pip dependency graph | CLEAN — no broken requirements |
| Required directories | CLEAN — data/, catalog/, assets/, output/, agents/, docs/, scripts/ all present |
| Required assets | CLEAN — all JSON configs and character sprites present |
| Shell scripts | CLEAN — all call local .venv Python correctly |
| MCP config (Vinnie) | CLEAN — PubMed remote server configured |
| MCP config (Dewey) | CLEAN — CourtListener API + MCP server |
| Agent structure | CLEAN — 11 agents under agents/, all with README.md + run.sh |
| Shared skills | CLEAN — agents/.skills/ with x-images, x-voice, pushgit |
| Naming convention | CLEAN — all lowercase-hyphenated directory names |
| .gitignore | CLEAN — covers __pycache__, *.pyc, node_modules/, venv/, .wrangler/, .env, catalog/, output/ |
| Git repo | CLEAN — pushed to github.com/johnyork1/ridgemont-agents, 0 open PRs |

**Overall assessment:** The project is fully consolidated. All 11 agents from Claude Cowork are migrated into `agents/` with standardized naming, README.md, and run.sh entry points. The Make Videos pipeline (18 scripts) is clean with `--project-root` support and shared `resolve_path` utility. No duplicates, no Docker remnants, no test artifacts. Full documentation at `docs/AGENTS.md` and `docs/STRUCTURE.md`. 12 of 14 audit items fixed; 2 informational items remain open (generate_prompt asset paths, Node.js availability).
