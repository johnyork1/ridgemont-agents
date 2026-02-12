# Docker Migration Blueprints — Ridgemont Studio Agent Ecosystem

**Generated:** February 11, 2026
**Source Directories Audited:**
- `~/.claude/skills/`
- `/Users/johnyork/My Drive/Ridgemont Studio/Claude Cowork/`
- `/Users/johnyork/My Drive/Ridgemont Studio/Claude Cowork/Master Agent/`

**Total Agents Found:** 13 + 1 utility skill
**Total Connectors Referenced:** 29 (4 OAuth + 25 MCP)

---

## BLUEPRINT 01: Make Videos

**Agent ID:** agent_02 | **Health Score:** 9.8/10
**Path:** `Master Agent/Make Videos/`
**Role:** Full-stack automated video production pipeline for 121+ song catalog across 21 genres featuring Weeter & Blubby mascot characters.

### Purpose & Function
6-step pipeline that transforms audio files into multi-format branded music videos:
Step 0 → Asset Prep (character extraction from sprite sheets)
Step 1 → Song Ingestion (audio copy, directory scaffolding)
Step 1.5 → Preflight Validation (all asset paths verified)
Step 2 → Audio Analysis (BPM, key, energy, mood mapping via librosa)
Step 3 → Video Creation (Ken Burns, character overlay, beat-sync, color grading)
Step 4 → Multi-Format Assembly (7 output formats with blur-fill vertical strategy)
Step 5 → Cataloging (hash-based idempotency, catalog storage)

### Dependencies

**Python (pip):**
| Package | Used By | Purpose |
|---------|---------|---------|
| librosa | analyze_catalog.py | BPM, beats, key detection, energy curves |
| numpy | analyze_catalog.py, prep_characters.py | Numerical arrays for audio/image data |
| Pillow | generate_thumbnails.py, meme_sign_render.py | Image compositing, text rendering |
| opencv-python | prep_characters.py | Image processing, contour detection |
| rembg | prep_characters.py | AI background removal from character sheets |

**System Tools:**
| Tool | Used By | Purpose |
|------|---------|---------|
| FFmpeg | baseline_master.py, batch_produce.py, lyric_video.py, visualizer.py | Video rendering, transcoding, filter chains |

**Python stdlib** (all scripts): argparse, json, os, sys, subprocess, logging, math, datetime, hashlib, shutil, pathlib, re, textwrap

### Data Sources

**Configuration JSONs (read):**
- `data/mood_map.json` — BPM/key → character pose mapping (7 mood conditions)
- `data/genre_defaults.json` — 21 genre visual defaults (poses, backgrounds, color grading)
- `data/genre_visual_identity.json` — Extended genre profiles (colors, typography, motifs, ComfyUI prompts)
- `data/output_formats.json` — 7 output format specs (master, short, tiktok, reel, lyric, visualizer, sync)
- `data/baseline_recipe.json` — Animation constants (1920x1080, 30fps, intro/endcard timing)
- `data/beat_sync_strategies.json` — Platform-specific edit strategies (hook-first, energy-peak)
- `data/lyric_config.json` — Lyric overlay rendering settings
- `data/youtube_script_config.json` — YouTube metadata generation templates

**Per-Song Data (read/write):**
- `catalog/{artist}/{song}/manifest.json` — Analysis results, beat grid, segments
- `catalog/{artist}/{song}/artist_profile.json` — Visual overrides per artist
- `catalog/{artist}/{song}/creative_brief.json` — Thematic direction
- `catalog/{artist}/{song}/lyrics.lrc` — Timestamped lyrics
- `catalog/{artist}/{song}/youtube/` — Generated YouTube metadata

**Asset Directories (read):**
- `assets/characters/weeter/{mood}/{pose}.png`
- `assets/characters/blubby/{mood}/{pose}.png`
- `assets/characters/together/{mood}/{pose}.png`
- `data/raw_sheets/` — Source sprite sheets (12 sprites + 41 singles)

### Environment Variables
None — all paths are project-root-relative. Pass `--project-root` to every script.

### Entry Points
```bash
python scripts/prep_characters.py --project-root /app        # Step 0
python scripts/ingest_song.py <song_id> <artist> --project-root /app  # Step 1
python scripts/preflight_validator.py <song_id> <artist> --project-root /app  # Step 1.5
python scripts/analyze_catalog.py <song_id> <artist> --project-root /app  # Step 2
python scripts/baseline_master.py <song_id> <artist> --project-root /app  # Step 3
python scripts/batch_produce.py <song_id> <artist> --project-root /app  # Step 4
python scripts/generate_youtube_script.py <song_id> <artist> --project-root /app  # Optional
```

### Docker Notes
- Heaviest container: needs librosa + numpy + opencv + rembg + ffmpeg
- GPU optional (rembg uses ONNX runtime, runs on CPU)
- Mount catalog/ as persistent volume for song data
- Mount assets/ as read-only volume for character PNGs
- All renders write to catalog/{artist}/{song}/outputs/

---

## BLUEPRINT 02: Master Agent

**Agent ID:** agent_13 | **Health Score:** 9.6/10
**Path:** `Master Agent/`
**Role:** Orchestrator, registry keeper, and daily health auditor for the entire ecosystem.

### Purpose & Function
Auto-discovers all 13 agents, maintains the central agent_registry.json, runs daily health audits with scoring (0-10), sends email alerts on degradation, and uses Claude API for intelligent analysis.

### Dependencies

**Python (pip):**
| Package | Used By | Purpose |
|---------|---------|---------|
| anthropic | daily_monitor.py | Claude API for intelligent audit analysis |

**Python stdlib:** os, json, hashlib, smtplib, subprocess, datetime, timedelta, pathlib, email.mime.text, email.mime.multipart

### Data Sources

**Read/Write:**
- `agent_registry.json` — Central registry (13 agents, 29 connectors, health scores)
- `last_audit.json` — Most recent audit results
- `logs/` — Historical audit logs
- `audit_template.md` — Report template
- `evaluation_criteria.md` — Health scoring rubric

### Environment Variables
```
COWORK_ROOT=/Users/johnyork/My Drive/Ridgemont Studio/Claude Cowork
MASTER_AGENT_DIR=${COWORK_ROOT}/Master Agent
ANTHROPIC_API_KEY=<your_anthropic_api_key>
EMAIL_SENDER=<your_gmail@gmail.com>
EMAIL_PASSWORD=<gmail_app_password>
EMAIL_RECIPIENT=<recipient@gmail.com>
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

### Entry Point
```bash
python daily_monitor.py
```

### Docker Notes
- Lightweight container: only needs `anthropic` pip package + stdlib
- Requires ANTHROPIC_API_KEY (Claude model: claude-sonnet-4-20250514)
- Requires Gmail App Password for email notifications
- Mount agent_registry.json and logs/ as persistent volumes
- Schedule via cron or Docker healthcheck interval

---

## BLUEPRINT 03: Ridgemont Catalog Manager

**Agent ID:** agent_04 | **Health Score:** 9.8/10
**Path:** `Ridgemont Catalog Manager/`
**Role:** Central operational engine for the 98-song music catalog across three acts.

### Purpose & Function
Streamlit web dashboard for catalog metadata management, financials, pitching status, deployment tracking, and shortcode automation.

### Dependencies

**Python (pip):**
| Package | Used By | Purpose |
|---------|---------|---------|
| streamlit | catalog_manager.py / app.py | Web UI dashboard |
| pandas | catalog_manager.py | Catalog data manipulation |

**Python stdlib:** json, os, sys

### Data Sources

**Read/Write:**
- `data/catalog.json` — Master catalog (98 songs, 3 acts)
- `data/artists.json` — Artist metadata

**Documentation:**
- `docs/SYSTEM_PROMPT_V5.md` — System instructions (v5.5)

### Environment Variables
None documented — Streamlit defaults.

### Entry Point
```bash
streamlit run catalog_manager.py --server.port 8501
```

### External Connectors Referenced
Melon (charts), MotherDuck (SQL analytics), Stripe (payments), PayPal (payments), Cloudflare R2 (storage), GitHub (version control)

### Docker Notes
- Expose port 8501 for Streamlit UI
- Mount data/ as persistent volume for catalog.json
- Connector credentials handled via MCP (not in container)

---

## BLUEPRINT 04: Frozen Cloud Portal

**Agent ID:** agent_10 | **Health Score:** 8.6/10
**Path:** `frozen-cloud-portal/`
**Role:** Read-only Streamlit dashboard for catalog browsing, deployment tracking, financial review.

### Purpose & Function
Public-facing or internal read-only view of the catalog. Browsing by act, artist, genre. Deployment status and financial summaries.

### Dependencies

**Python (pip):**
| Package | Used By | Purpose |
|---------|---------|---------|
| streamlit | app.py | Web UI |
| pandas | app.py | Data display |

### Data Sources
Same catalog JSON files as Catalog Manager (read-only).

### Environment Variables
None documented.

### Entry Point
```bash
streamlit run app.py --server.port 8502
```

### External Connectors Referenced
MotherDuck (SQL analytics), Amplitude (user behavior analytics)

### Docker Notes
- Expose port 8502
- Read-only mount to catalog data volume
- Can share base image with Catalog Manager

---

## BLUEPRINT 05: Suno Studio

**Agent ID:** agent_06 | **Health Score:** 9.2/10
**Path:** `Suno Studio/`
**Role:** Suno v5.0 AI music prompt generator with deterministic 4-engine architecture.

### Purpose & Function
Generates structured Suno.com prompts from genre + mood + instrumentation parameters. Supports 122 subgenres, 1228 tags, 1223 instruments. Deterministic output — same inputs always produce same prompt.

### Dependencies

**Python (pip):** None — stdlib only.
**Python stdlib:** json, os, sys, logging, argparse

### Data Sources

**Read:**
- `assets/subgenres.json` — 122 subgenres
- `assets/subgenre_tags.json` — 1228 tags
- `assets/instruments.json` — 1223 instruments
- `CLAUDE_INSTRUCTIONS.md` — System prompt

### Environment Variables
None.

### Entry Point
```bash
python scripts/generate_prompt.py --genre reggae --mood chill --bpm 136
```

### Docker Notes
- Smallest possible container: Python stdlib only, no pip packages
- Mount assets/ as read-only volume
- Stateless — no persistent storage needed

---

## BLUEPRINT 06: Make-Music

**Agent ID:** agent_03 | **Health Score:** 7.6/10
**Path:** `Make-Music/`
**Role:** Songwriting and MIDI composition workspace for acoustic guitar-based ballads.

### Purpose & Function
MIDI file generation for guitar strumming patterns, chord progressions, and song arrangements. Designed for import into Logic Pro or other DAWs.

### Dependencies

**Python (pip):**
| Package | Used By | Purpose |
|---------|---------|---------|
| midiutil | MIDI scripts | MIDI file generation |

**External Tools:**
| Tool | Purpose |
|------|---------|
| Logic Pro | DAW (Mac-only, not containerizable) |

### Data Sources
- `midi_acoustic_guitar_strumming_guide.md` — Composition reference
- `RULES.md` — Agent rules

### Environment Variables
None.

### Entry Point
Python MIDI generation scripts (varies by composition task).

### External Connectors Referenced
Suno.com (AI music generation), Melon (charts)

### Docker Notes
- Lightweight: only needs midiutil pip package
- Logic Pro integration is Mac-native — MIDI export is the Docker boundary
- Output: .mid files for external DAW consumption

---

## BLUEPRINT 07: X-Posts

**Agent ID:** agent_09 | **Health Score:** 9.2/10
**Path:** `X-Posts/`
**Role:** Daily crypto/blockchain X (Twitter) content pipeline (3-5 posts/day) with Weeter & Blubby voice.

### Purpose & Function
Automated posting to @4_Bchainbasics X account. Crypto market analysis, blockchain education, community engagement. Posts use the Weeter & Blubby mascot personality.

### Dependencies

**Python (pip):** None — operates via Claude skills and MCP connectors.

**Skills:**
- x-voice (voice/tone styling for W&B personality)
- x-images (image generation for posts)

### Data Sources
- `x_daily_post_shortcut.md` — Daily workflow definition
- `x_post_history.md` — Post archive/log
- `humanization_settings.md` — Voice calibration parameters

### Environment Variables
X API credentials managed via MCP connector (not in local env).

### Entry Point
Skill-based: triggered via `/x-posts` command or daily shortcut.

### External Connectors Referenced
X API (MCP), Canva (images), Ahrefs (SEO), Claude in Chrome (browser automation), WebSearch

### Docker Notes
- No local Python — this agent orchestrates via MCP connectors
- Docker container would be a thin orchestration layer
- X API credentials must be mounted as secrets
- Consider running as a scheduled cron job

---

## BLUEPRINT 08: Ridgemont Studio Website

**Agent ID:** agent_05 | **Health Score:** 9.4/10
**Path:** `Ridgemont Studio Website/`
**Role:** Music label platform with artist roster, authenticated streaming, and sync licensing marketplace.

### Purpose & Function
Firebase-authenticated website with Cloudflare Workers for serverless compute and R2 for media storage. Artist pages, track streaming, sync licensing portal.

### Dependencies

**Frontend:** HTML, CSS, JavaScript
**Backend Services:**
| Service | Purpose |
|---------|---------|
| Firebase SDK | User authentication |
| Cloudflare Workers | Serverless API endpoints |
| Cloudflare R2 | Audio/media cloud storage |

### Data Sources
- `index.html` — Main landing page
- `worker.js` — Cloudflare Worker code
- `tracks.json` — Track metadata for streaming
- `sync-music.sh` — Audio sync deployment script

### Environment Variables
Firebase and Cloudflare credentials (managed via their respective dashboards, not local .env).

### Entry Point
Static site deployment — no single entry point. Deploy via Cloudflare Pages or similar.

### External Connectors Referenced (8 — most connected)
Cloudflare, Cloudinary, Canva, Ahrefs, Figma, Amplitude, Stripe, PayPal

### Docker Notes
- Static site — better served via Cloudflare Pages than Docker
- worker.js deploys to Cloudflare Workers (not containerizable)
- Firebase auth is client-side SDK
- If containerized: simple nginx/static-server image

---

## BLUEPRINT 09: Frozen Cloud Website

**Agent ID:** agent_01 | **Health Score:** 7.8/10
**Path:** `Frozen Cloud Website/`
**Role:** Static HTML landing page for the Frozen Cloud music artist brand.

### Purpose & Function
Single-page promotional site with artist imagery, branding, and streaming links.

### Dependencies
**Frontend:** HTML, CSS, JavaScript, Google Fonts API

### Data Sources
- `index.html` — Landing page
- `FrozenCloud_02.jpg` — Hero image

### Environment Variables
None.

### Entry Point
Static HTML file — deploy via any web server.

### External Connectors Referenced
Cloudflare, Ahrefs, Canva, Figma

### Docker Notes
- Trivial: single nginx container serving static files
- Or skip Docker entirely — deploy via Cloudflare Pages

---

## BLUEPRINT 10: Bajan Sun Website

**Agent ID:** agent_07 | **Health Score:** 7.4/10
**Path:** `Bajan Sun Website/`
**Role:** Artist landing page for Act 3 of the Ridgemont catalog.

### Purpose & Function
Static promotional site for the Bajan Sun artist persona.

### Dependencies
HTML/CSS/JavaScript only.

### Data Sources
Static HTML/image files.

### Environment Variables
None.

### Entry Point
Static HTML deployment.

### Docker Notes
Same as Frozen Cloud — trivial static site. Consider combining all artist sites into one nginx container with path-based routing.

---

## BLUEPRINT 11: Park Bellevue Website

**Agent ID:** agent_08 | **Health Score:** 8.0/10
**Path:** `Park Bellevue Website/`
**Role:** Artist landing page for Act 2 of the Ridgemont catalog.

### Purpose & Function
Static promotional site for the Park Bellevue artist persona.

### Dependencies
HTML/CSS/JavaScript only.

### Data Sources
Static HTML/image files.

### Environment Variables
None.

### Entry Point
Static HTML deployment.

### Docker Notes
Same as other artist sites — bundle into shared static-sites container.

---

## BLUEPRINT 12: Dewey Cheatem, Esq.

**Agent ID:** agent_11 | **Health Score:** 9.2/10
**Path:** `dewey-cheatem-esq/`
**Role:** Legal research and advisory agent for U.S. Federal, California, and Idaho law.

### Purpose & Function
Legal research across case law, statutes, and regulations. Produces legal memos and case analysis. Specialized in entertainment law relevant to the music label.

### Dependencies

**Python (pip):**
Managed via `uv` package manager — dependencies in CourtListener MCP server (exact packages TBD from pyproject.toml).

**System Tools:**
| Tool | Purpose |
|------|---------|
| uv | Python package manager (replaces pip) |

### Data Sources
- `CLAUDE.md` — Agent instructions
- `CONNECTORS.md` — Connector documentation
- `free-legal-sources.md` — Free legal data sources reference
- `CourtListener/` — MCP server for case law

### Environment Variables
CourtListener API credentials (via MCP configuration).

### Entry Point
```bash
cd CourtListener && uv run python -m app.server --transport http
```

### External Connectors Referenced
CourtListener (case law), Consensus (academic), Scholar Gateway (papers), Web Search

### Docker Notes
- Needs `uv` installed (or convert to pip with requirements.txt)
- CourtListener MCP runs as HTTP server — expose port
- Legal database access via API keys as mounted secrets
- Skills: legal-memo, pdf

---

## BLUEPRINT 13: Dr. Vinnie Boombatz

**Agent ID:** agent_12 | **Health Score:** 9.4/10
**Path:** `dr-vinnie-boombatz/`
**Role:** Comprehensive medical AI research agent with 8+ biomedical databases.

### Purpose & Function
Medical research across clinical trials, drug databases, genomics, and biomedical literature. 10+ specialized skills from clinical diagnosis to emergency medicine.

### Dependencies

**Python (pip):**
Managed via MCP connectors — no local Python scripts. Agent operates entirely through connected research databases.

### Data Sources
- `CLAUDE.md` — System instructions
- `README.md` — Documentation
- `.mcp.json` — MCP connector configuration
- `agents/medical-researcher.md` — Research workflow definition

### Environment Variables
API credentials for each research database (via MCP):
- PubMed API key
- ChEMBL API access
- ClinicalTrials.gov API
- bioRxiv API
- ICD-10 lookup
- NPI Registry

### Entry Point
MCP-based — no standalone script. Operates within Claude Cowork as a conversational agent.

### External Connectors Referenced (8 — most research-connected)
PubMed, ChEMBL, Clinical Trials, bioRxiv, ICD-10, Consensus, Scholar Gateway, NPI Registry

### Skills (10)
clinical-diagnosis, pharmacology, medical-research, ai-medical-advances, patient-education, emergency-medicine, lab-interpretation, medical-imaging, preventive-medicine, mental-health

### Docker Notes
- Thin orchestration container — most work happens via API calls
- All database credentials as mounted secrets
- MCP server configuration needed for each connector
- No heavy local compute — network-bound agent

---

## BLUEPRINT 14: create-shortcut (Utility Skill)

**Path:** `~/.claude/skills/create-shortcut/`
**Role:** Template/documentation skill for creating scheduled Claude shortcuts.

### Purpose & Function
Provides workflow guidance for creating reusable, schedulable shortcuts within Claude Cowork. Not an executable agent.

### Dependencies
None — pure documentation.

### Data Sources
- `SKILL.md` — Skill definition and workflow instructions

### Environment Variables
None.

### Entry Point
Invoked via Claude's `set_scheduled_task` tool.

### Docker Notes
Not containerizable — this is a Claude platform feature, not a standalone service.

---

## GLOBAL DEPENDENCY SUMMARY

### Python Packages (All Agents Combined)
```
librosa          # Make Videos — audio analysis
numpy            # Make Videos — numerical computing
Pillow           # Make Videos — image compositing
opencv-python    # Make Videos — image processing
rembg            # Make Videos — AI background removal
streamlit        # Catalog Manager, Portal — web dashboards
pandas           # Catalog Manager, Portal — data manipulation
anthropic        # Master Agent — Claude API
midiutil         # Make-Music — MIDI generation
```

### System Tools
```
ffmpeg           # Make Videos — video rendering
uv               # Dewey Cheatem — Python package manager
```

### Environment Variables (All Agents Combined)
```
COWORK_ROOT              # Master Agent — ecosystem root path
MASTER_AGENT_DIR         # Master Agent — agent directory
ANTHROPIC_API_KEY        # Master Agent — Claude API key
EMAIL_SENDER             # Master Agent — Gmail sender
EMAIL_PASSWORD           # Master Agent — Gmail App Password
EMAIL_RECIPIENT          # Master Agent — notification recipient
SMTP_SERVER              # Master Agent — SMTP host (smtp.gmail.com)
SMTP_PORT                # Master Agent — SMTP port (587)
```

### External Services Requiring API Credentials
```
Anthropic Claude API     # Master Agent daily monitoring
Gmail SMTP               # Master Agent email alerts
X/Twitter API            # X-Posts agent
CourtListener API        # Dewey Cheatem legal research
PubMed API               # Dr. Vinnie Boombatz
ChEMBL API               # Dr. Vinnie Boombatz
ClinicalTrials.gov API   # Dr. Vinnie Boombatz
Firebase                 # Ridgemont Studio Website
Cloudflare Workers/R2    # Ridgemont Studio Website
Stripe                   # Ridgemont Studio Website, Catalog Manager
PayPal                   # Ridgemont Studio Website, Catalog Manager
MotherDuck               # Catalog Manager, Portal
Melon                    # Catalog Manager, Make-Music
Canva                    # X-Posts, Websites
Ahrefs                   # X-Posts, Websites
Figma                    # Websites
Amplitude                # Ridgemont Studio Website, Portal
Cloudinary               # Ridgemont Studio Website, Make Videos
Notion                   # Master Agent
Zapier                   # Master Agent
Consensus                # Dewey Cheatem, Dr. Vinnie Boombatz
Scholar Gateway          # Dewey Cheatem, Dr. Vinnie Boombatz
```

---

## RECOMMENDED DOCKER ARCHITECTURE

### Container Group 1: Video Production
- **make-videos** — Python 3.11 + librosa + numpy + Pillow + cv2 + rembg + ffmpeg
- Volumes: catalog/, assets/, data/
- CPU-intensive, optional GPU for rembg

### Container Group 2: Web Dashboards
- **catalog-manager** — Python 3.11 + streamlit + pandas (port 8501)
- **frozen-cloud-portal** — Python 3.11 + streamlit + pandas (port 8502)
- Shared volume: catalog data

### Container Group 3: Orchestration
- **master-agent** — Python 3.11 + anthropic (lightweight, cron-scheduled)
- Secrets: ANTHROPIC_API_KEY, EMAIL_PASSWORD
- Volume: agent_registry.json, logs/

### Container Group 4: Static Sites
- **static-sites** — nginx serving all 4 websites (Ridgemont, Frozen Cloud, Bajan Sun, Park Bellevue)
- Or deploy directly to Cloudflare Pages (no Docker needed)

### Container Group 5: Research Agents
- **dewey-legal** — Python 3.11 + uv + CourtListener MCP server
- **dr-vinnie** — Thin Python + MCP connectors
- Both network-bound, minimal compute

### Container Group 6: Content Pipeline
- **suno-studio** — Python 3.11 (stdlib only, smallest image)
- **make-music** — Python 3.11 + midiutil
- **x-posts** — Orchestration only (MCP connectors)
