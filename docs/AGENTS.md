# Ridgemont Studio — Agent Index

## Agents

| # | Agent | Directory | Type | Entry Point |
|---|-------|-----------|------|-------------|
| 1 | Dr. Vinnie Boombatz | `agents/vinnie/` | Claude Desktop plugin | `./run.sh` or open in Claude Desktop |
| 2 | Dewey, Cheatham & Howe | `agents/dewey-cheatham-howe/` | Claude Desktop plugin | `./run.sh` or open in Claude Desktop |
| 3 | Make Videos | `agents/make-videos/` | Claude Desktop project | `./run.sh` (prints pipeline commands) |
| 4 | Suno | `agents/suno/` | Claude Desktop project | `./run.sh` or `python3 scripts/generate_prompt.py` |
| 5 | Make Music | `agents/make-music/` | MIDI/Songwriting workspace | `./run.sh` or `python3 generate_getting_old.py` |
| 6 | Master Agent | `agents/master-agent/` | Ecosystem orchestrator | `./run.sh` or `python3 daily_monitor.py` |
| 7 | Catalog Manager | `agents/catalog-manager/` | Catalog database | `./run.sh` or `python3 scripts/catalog_manager.py` |
| 8 | X-Posts | `agents/x-posts/` | Crypto Twitter agent | `./run.sh` or open in Claude Desktop |
| 9 | Frozen Cloud Website | `agents/frozen-cloud-website/` | Static artist site | `./run.sh` (opens index.html) |
| 10 | Frozen Cloud Portal | `agents/frozen-cloud-portal/` | Streamlit catalog portal | `./run.sh` or `streamlit run app.py` |
| 11 | Ridgemont Studio Website | `agents/ridgemont-website/` | Public label site | `./run.sh` (opens index.html) |

### Shared

| Resource | Directory | Description |
|----------|-----------|-------------|
| Shared Skills | `agents/.skills/` | x-images (character image gen), x-voice (audio gen), pushgit (git automation) |

## How to Use

Each agent can be opened as a **project** in Claude Desktop (the CLAUDE.md / RULES.md file acts as the system prompt). Agents with Python scripts can also be run directly via `./run.sh`.

## Agent Details

### Dr. Vinnie Boombatz (`agents/vinnie/`)

Medical AI consultant built on Claude Opus.

- **Plugin**: `.claude-plugin/plugin.json`
- **System prompt**: `CLAUDE.md`
- **Commands** (8): ai-medicine-update, differential, drug-lookup, interaction-check, interpret-labs, patient-explainer, research-review, screening
- **Skills** (10): ai-medical-advances, clinical-diagnosis, emergency-medicine, lab-interpretation, medical-imaging, medical-research, mental-health, patient-education, pharmacology, preventive-medicine
- **Sub-agents**: `sub-agents/medical-researcher.md` — PubMed literature search specialist
- **MCP**: PubMed remote server (`.mcp.json`)
- **Scripts**: `src/generate_report.py` — generates medical reports from patient notes

### Dewey, Cheatham & Howe (`agents/dewey-cheatham-howe/`)

Legal research and advisory agent covering U.S. federal, California, and Idaho law.

- **System prompt**: `CLAUDE.md`
- **MCP**: CourtListener case law API (`.mcp.json` + `CourtListener/` MCP server)
- **Skills** (8): case-law-research, statute-lookup, contract-review, legal-writing, california-law, idaho-law, legal-citation, compliance-check
- **Output dirs**: `documents/`, `research/`, `contracts/`, `briefs/`, `citations/`

### Make Videos (`agents/make-videos/`)

Music video production pipeline wrapper.

- **System prompt**: `CLAUDE.md`
- **Scripts**: 18 Python scripts in `../../scripts/`
- **Pipeline**: ingest → analyze → render master → render shorts
- **Extras**: pro video, lyric video, visualizer, thumbnails, artist profiles, meme signs, YouTube metadata

### Suno (`agents/suno/`)

Suno v5.0 style prompt generator with curated asset databases.

- **System prompt**: `CLAUDE.md` + `CLAUDE_INSTRUCTIONS.md`
- **Scripts**: `scripts/generate_prompt.py` (local), also available at `../../scripts/generate_prompt.py`
- **Assets**: 122 subgenres, 1127 tags, 1223 instruments, presets, constraints, modifiers
- **References**: `references/suno_v5_rules.md`

### Make Music (`agents/make-music/`)

Songwriting and MIDI composition workspace for Logic Pro.

- **System prompt**: `RULES.md`
- **Scripts**: `generate_getting_old.py` (MIDI generation)
- **Assets**: MIDI files, chord sheets, Suno prompt drafts
- **Guides**: `midi_acoustic_guitar_strumming_guide.md`, `Ridgemont_Jam_Session_Spec.md`

### Master Agent (`agents/master-agent/`)

Ecosystem orchestrator that monitors all agents, maintains registry, and performs audits.

- **System prompt**: `RULES.md`
- **Scripts**: `daily_monitor.py` (health checks), `build_setup_guide.js`, `gen_blueprint.js`, `gen_report.js`
- **Data**: `agent_registry.json` (master registry), `last_audit.json`
- **Sub-agent**: `Make Videos/` — embedded Make Videos copy with skills references
- **Logs**: `logs/` — audit history

### Catalog Manager (`agents/catalog-manager/`)

Unified catalog database for all Ridgemont music (Frozen Cloud, Park Bellevue, Bajan Sun).

- **Scripts**: `scripts/catalog_manager.py`, `scripts/app.py`, `scripts/watch_and_upload.py`
- **Data**: `data/catalog.json` (source of truth), `data/artists.json`, `data/albums.json`
- **Exports**: `exports/`, `pitch_decks/`, `dashboards/`

### X-Posts (`agents/x-posts/`)

Crypto Twitter agent for @4_Bchainbasics. Drafts, schedules, and posts to X.

- **System prompt**: `CLAUDE.md`
- **Workflow**: `x_daily_post_shortcut.md` (daily posting workflow)
- **History**: `x_post_history.md` (post archive + style notes)
- **Scheduled**: `Scheduled/` — queued posts
- **Characters**: `Weeter_and_Blubby/` — character pose assets

### Frozen Cloud Website (`agents/frozen-cloud-website/`)

Single-page artist landing page with ice-blue brand identity.

- **System prompt**: `RULES.md`
- **Site**: `index.html` (static single-page app)
- **Brand**: Ice Blue (#7DBBFF), Frozen Navy (#163B73), Arctic White (#F2F7FF)

### Frozen Cloud Portal (`agents/frozen-cloud-portal/`)

Streamlit read-only portal for browsing the Ridgemont music catalog.

- **System prompt**: `RULES.md`
- **App**: `app.py` (Streamlit multi-act browser)
- **Data**: `data/catalog.json` (synced from Catalog Manager)
- **Requirements**: `requirements.txt`

### Ridgemont Studio Website (`agents/ridgemont-website/`)

Public-facing label website with authenticated music streaming.

- **System prompt**: `RULES.md`
- **Site**: `index.html` (single-page app)
- **Worker**: `worker.js` (Cloudflare Worker for authenticated streaming)
- **Config**: `wrangler.toml`, `firebase.json`, `tracks.json`
- **Deploy**: `sync-music.sh` (upload to Cloudflare R2)

### Shared Skills (`agents/.skills/`)

Cross-agent skill library.

| Skill | Description |
|-------|-------------|
| `pushgit/` | Git push automation |
| `x-images/` | X post image generation with Weeter & Blubby character assets (78 PNGs) |
| `x-voice/` | X post voice/audio generation |
