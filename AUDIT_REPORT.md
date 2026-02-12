# Ridgemont Studio — Agent & Script Audit Report

**Date:** 2026-02-12
**Auditor:** Claude Opus 4.6
**Project root:** `/Users/johnyork/Ridgemont_Studio`
**Total size:** 2.2 GB (1.5 GB catalog media, 0.7 GB venv + assets + data)

---

## 1. Agent & Script Inventory

### Claude Desktop Agents

| Agent | Directory | Language | Entrypoint | Inputs | Outputs |
|-------|-----------|----------|-----------|--------|---------|
| Dr. Vinnie Boombatz | `agents/vinnie/` | Markdown (Claude plugin) + Python | Open `agents/vinnie/` as project in Claude Desktop | CLAUDE.md, 8 slash commands, 10 skills, PubMed MCP, sub-agents/ | Conversational; `src/generate_report.py` writes `output/vinnie_report.txt` |
| Make Videos | `agents/make-videos/` | Markdown (Claude Desktop project) | Open `agents/make-videos/` as project in Claude Desktop | CLAUDE.md → delegates to `scripts/` | Pipeline videos in `catalog/` |
| Suno | `agents/suno/` | Markdown (Claude Desktop project) | Open `agents/suno/` as project in Claude Desktop | CLAUDE.md → delegates to `scripts/generate_prompt.py` | stdout (style prompt) |

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
| node | 25.4.0 | (not currently used by any script) | OK |
| npm | 11.7.0 | (not currently used by any script) | OK |

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
| ~~HIGH~~ | `prep_characters.py` | ~~Hardcoded relative paths — no `--project-root`.~~ | FIXED 2026-02-12: Added `--project-root` arg (default: derived from `__file__`). Paths now resolve relative to project root. |
| ~~MODERATE~~ | `ingest_song.py` | ~~`mp3_path` positional arg relative to cwd, not project root.~~ | FIXED 2026-02-12: Relative `mp3_path` now resolved against `--project-root`. |
| ~~MODERATE~~ | `render_pro_video.py` | ~~`--bg` and `--lrc` args relative to cwd, not project root.~~ | FIXED 2026-02-12: Both paths now resolved against `--project-root` when not absolute. |
| LOW | `generate_prompt.py` | Assets path derived from `__file__` parent — works correctly but hardcoded structure assumption (`../assets/`). | Open |
| ~~LOW~~ | `ingest_vinnie.sh` | ~~No `PYTHONPATH` setup for script mode.~~ | FIXED 2026-02-12: Added `export PYTHONPATH` for `scripts/` before Python invocation. |

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

# ── Vinnie Agent ──────────────────────────────────────────

# Generate medical report from patient notes
$PY agents/vinnie/src/generate_report.py

# Custom patient dir
VINNIE_PATIENT_DIR=/path/to/notes $PY agents/vinnie/src/generate_report.py

# Interactive Python with venv
./ingest_vinnie.sh

# Run a script through Vinnie launcher
./ingest_vinnie.sh --script agents/vinnie/src/generate_report.py
```

---

## 5. Top 10 Fixes (prioritized)

### ~~1. `prep_characters.py` — Add `--project-root` arg~~ FIXED
**Impact:** HIGH — script silently fails or writes to wrong location if not run from project root.
**Fix applied:** Added `argparse` with `--project-root` (default: derived from `__file__`). Input/output paths now resolve relative to project root. Works from any working directory.

### ~~2. `ingest_song.py` — Resolve `mp3_path` relative to project root~~ FIXED
**Impact:** MODERATE — users passing relative paths from wrong cwd get confusing errors.
**Fix applied:** Relative `mp3_path` is now resolved against `--project-root` before being passed to the ingestion pipeline.

### ~~3. `render_pro_video.py` — Resolve `--bg` and `--lrc` relative to project root~~ FIXED
**Impact:** MODERATE — same cwd-relative issue as ingest_song.
**Fix applied:** Both `--bg` and `--lrc` are now resolved against `--project-root` when not absolute, consistent with how the script resolves all other paths.

### ~~4. `ingest_vinnie.sh` — Add PYTHONPATH for script mode~~ FIXED
**Impact:** LOW-MODERATE — scripts with local imports would fail in script mode.
**Fix applied:** Added `export PYTHONPATH="$SCRIPT_DIR/scripts:${PYTHONPATH:-}"` before the Python invocation block. Both interactive and script modes now have `scripts/` on the import path.

### ~~5. Add `CLAUDE.md` at project root for pipeline documentation~~ FIXED
**Impact:** MODERATE — Claude Desktop needs guidance on how to run the pipeline when working from the project root (not inside `agents/vinnie/`).
**Fix applied:** Created `CLAUDE.md` at project root documenting: project structure, Python env, full pipeline steps with commands, rendering extras, utilities, Vinnie agent usage, key data files, and shared utilities.

### ~~6. Standardize path handling with a shared utility~~ FIXED
**Impact:** LOW — current scripts work but use mixed `os.path` / `pathlib.Path`.
**Fix applied:** Added `resolve_path(path, project_root)` to `cache_utils.py`. Adopted in `ingest_song.py` and `render_pro_video.py` (replacing inline `os.path.isabs` checks). Available for all scripts via `from cache_utils import resolve_path`.

### 7. Add `.venv` to `.claudeignore` exclusions
**Impact:** LOW — already done in current `.claudeignore`. Verified present.
**Status:** ALREADY FIXED.

### ~~8. `production_log.csv` — Move to `output/`~~ FIXED
**Impact:** LOW — previously at project root, cluttered the top-level directory.
**Fix applied:** Updated `ingest_catalog.sh` and `batch_produce.py` to write `output/production_log.csv`. Moved the existing file into `output/`.

### ~~9. Remove stale `__pycache__/` in `scripts/`~~ FIXED
**Impact:** COSMETIC — 96 bytes, harmless but untidy.
**Fix applied:** Deleted during cleanup session 2026-02-12.

### 10. Node.js is installed but unused
**Impact:** INFORMATIONAL — `node` and `npm` are available via Homebrew but no scripts currently use them. No action needed unless disk space is a concern.
**Status:** NO ACTION REQUIRED.

---

## 6. Structural Health Summary

| Category | Status |
|----------|--------|
| Docker path remnants | CLEAN — none found |
| Python imports | CLEAN — all 18 scripts import successfully |
| pip dependency graph | CLEAN — no broken requirements |
| Required directories | CLEAN — data/, catalog/, assets/, output/ all present |
| Required assets | CLEAN — all JSON configs and character sprites present |
| Shell scripts | CLEAN — both call local .venv Python correctly |
| MCP config (Vinnie) | CLEAN — PubMed remote server configured |
| Claude plugin structure | CLEAN — 3 agents (vinnie plugin, make-videos project, suno project), plugin.json, CLAUDE.md, 8 commands, 10 skills, 1 sub-agent |

**Overall assessment:** The project is in excellent health post-migration. 8 of 10 audit items have been fixed. All scripts resolve file path arguments relative to `--project-root` and work from any working directory. A shared `resolve_path` utility standardizes path handling. Root `CLAUDE.md` documents the full pipeline. Production logs now write to `output/`. Only two informational items remain open (generate_prompt asset paths, Node.js unused) — neither requires action.
