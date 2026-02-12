# Make Videos Agent — Overhaul Strategy v3.0

**Date:** February 9, 2026
**Scope:** Complete rebuild from v2.0 (generic music video pipeline) to v3.0 (Weeter & Blubby branded video production engine)
**Reference Files:** `rules_make_videos.md` (new RULES.md v4), `mood_map.json`, `video_tech_audit_feb2026.md`

---

## Section 1: Current State & Gap Analysis

### v2.0 File Inventory

**Configuration:**
| File | Size | Purpose |
|------|------|---------|
| `RULES.md` (v2.0) | 12 KB | Identity, 10 behavior rules, 5-step pipeline, 7 formats |
| `data/genre_visual_map.json` | 16 KB | 21 genres → AI models, palettes, ComfyUI workflows |
| `data/genre_profile_templates.json` | 11 KB | 21 genre templates (typography, motifs, mood) |
| `data/OVERHAUL_STRATEGY_v2.0.md` | 25 KB | Prior strategy document |
| `data/video_tech_audit_feb2026.md` | — | Verified tech specs (copied from uploads) |

**Scripts (6):**
| Script | Pipeline Step | Function |
|--------|-------------|----------|
| `ingest_song.py` | Step 1 | Audio validation, dir creation, asset copy |
| `analyze_catalog.py` | Step 2 | librosa BPM/beats/key/mood → song_manifest.json |
| `artist_profile_generator.py` | Setup | Create/update artist_profile.json |
| `generate_visuals.py` | Step 3 | ComfyUI integration, Kling credit tracking |
| `batch_produce.py` | Step 4 | FFmpeg 7-format assembly |
| `catalog_outputs.py` | Step 5 | ffprobe validation, progress logging |

**Skills (9):** ingest-song, analyze-song, generate-visuals, assemble-video, batch-produce, artist-profile, format-convert, quality-check, upload-all

**Catalog:** 12 artist profiles, progress_log.json, job_queue.json

### Workflows & Tools Currently Used

- librosa for audio analysis (BPM, beats, key, mood estimation)
- ComfyUI API for visual generation (http://localhost:8188)
- FFmpeg via subprocess for video assembly
- Kling credit tracking (max 6/day)
- Pillow for placeholder frame generation
- matplotlib for visualizer frames
- Claude in Chrome for multi-platform upload (upload-all skill)

### Manual Bottlenecks

| Bottleneck | Current State | v3.0 Solution |
|-----------|---------------|---------------|
| No character overlay system | Manual PNG placement | Automated W&B breathing overlay via sprite animation |
| No vertical video strategy | Basic resize/crop | Blur-fill with FFmpeg filter_complex |
| No idempotency checking | Re-renders everything | SHA256 hash signatures skip unchanged songs |
| No preflight validation | Crashes mid-batch on missing assets | Fail-fast preflight checks entire batch first |
| No mood-based pose selection | Generic visuals | mood_map.json + librosa analysis → character poses |
| No Safe Zone enforcement | Overlays can be clipped by platform UI | Auto-snap function with format-aware zones |
| No confidence gating on analysis | Trusts all librosa output | Safety valve: key_confidence > 0.15, mode_confidence > 0.10 |
| No Creative Brief system | One-size-fits-all per genre | Per-song JSON overrides for visual decisions |
| No meme sign end card | Videos end abruptly | Dynamic W&B meme sign on every video |
| No baseline recipe | Requires AI models to produce anything | Ken Burns + beat pulse + W&B = Day 1 video |

### Gap Matrix

| v3.0 Requirement | v2.0 Status | Gap Severity |
|-------------------|-------------|-------------|
| Weeter & Blubby character system | **MISSING** | CRITICAL |
| Blur-fill vertical strategy (1080p) | **MISSING** | CRITICAL |
| Safe Zone enforcement (horizontal + vertical) | **MISSING** | CRITICAL |
| Hash-based idempotency (SHA256) | **MISSING** | HIGH |
| Preflight validation (Step 1.5) | **MISSING** | HIGH |
| Baseline Master Recipe (Ken Burns + W&B) | **MISSING** | HIGH |
| Project-root-relative paths in manifests | **MISSING** — uses CATALOG_ROOT env var | HIGH |
| librosa confidence scoring + safety valve | **MISSING** | HIGH |
| mood_map.json integration | **MISSING** | HIGH |
| Creative Brief system (per-song override) | **MISSING** | MODERATE |
| prep_characters.py (Asset Factory) | **MISSING** | MODERATE |
| meme_sign_render.py | **MISSING** | MODERATE |
| Shared modules (safe_zone, render_sig, preflight) | **MISSING** | MODERATE |
| 15 skill definitions | **PARTIAL** — 9 exist but wrong scope | MODERATE |
| RULES.md v4 with character dynamics + production rules | **MISSING** — v2.0 has no character content | CRITICAL |

**Verdict:** v2.0 is a structurally sound generic pipeline. v3.0 adds the character system, production guardrails, and automation intelligence that transform it into a branded video factory. Every script needs rewriting; every skill needs replacement.

---

## Section 2: Ridgemont Studio Catalog Requirements

### Scale

| Metric | Value |
|--------|-------|
| Songs | 121+ (growing) |
| Genres | 21 |
| Artists | 200+ fictional artists across 3 acts |
| Formats per song | 7 |
| Total video outputs | 847+ base (growing to 1,400+) |
| Character appearances | 100% — every video includes Weeter & Blubby |

### The 7 Output Formats

| # | Format | Aspect | Resolution | Duration | Notes |
|---|--------|--------|-----------|----------|-------|
| 1 | Full Music Video | 16:9 | 1920×1080 | Full length | The master |
| 2 | YouTube Short | 9:16 | 1080×1920 | ≤59 sec | Blur-fill from 1080p |
| 3 | TikTok Clip | 9:16 | 1080×1920 | 15-60 sec | Hook-first opening |
| 4 | Instagram Reel | 4:5 or 9:16 | 1080×1920 | ≤90 sec | Blur-fill |
| 5 | Lyric Video | 16:9 | 1920×1080 | Full length | Text overlay in Safe Zone |
| 6 | Audio-Reactive Visualizer | 16:9 | 1920×1080 | Full length | Deforum or custom Python |
| 7 | Sync Licensing Reel | 16:9 | 1920×1080 | 30-60 sec | Highlight, no lyrics |

All include animated Meme Sign end card. All vertical formats use blur-fill (1080p) or center-crop (4K). All overlays enforce Social UI Safe Zone on vertical outputs.

### Artist Visual Identity

Each artist gets `artist_profile.json` containing:
- Color palette (primary, secondary, accent colors)
- Typography (heading/body fonts, style)
- Visual motifs
- Color grading preferences
- Camera style
- `vertical_style`: blur_fill (default), stacked, or center_crop (4K only)
- `weeter_blubby_default`: end_card_meme_sign (default)
- `weeter_blubby_frequency`: every_video

### Weeter & Blubby Requirements

- **Weeter (Brown Bear):** Leader / Hype Man. Initiates action. Typically left, larger.
- **Blubby (Yellow-Green Alien):** Reactor / Sidekick. Responds to energy. Typically right, smaller.
- **NEVER** assign Blubby a leadership pose or Weeter a reaction pose (unless Creative Brief overrides).
- **Breathing animation mandatory** — no static PNGs ever. 2-second sine wave cycle (98%→102%).
- **Beat bounce** — 5-10px Y-axis offset on kick drum beats from librosa.
- **Meme Sign end card** on every video — dynamic text (Song Title + Artist Name) on blank_sign.png template.

### Blur-Fill Vertical Strategy

| Source | Strategy | Result |
|--------|----------|--------|
| 1080p (standard) | **Blur-Fill** | Video centered at full sharpness, blurred copy fills 1080×1920 background |
| 1080p + branding | **Stacked Layout** | Title bar (20%) + video (60%) + W&B/CTA bar (20%) |
| 4K | **Center Crop** | Clean 1215px crop scales to 1080×1920 |

**NEVER upscale a 607px center-crop to 1080px.** Default is blur-fill. Override via `artist_profile.json` field `"vertical_style": "stacked"`.

---

## Section 3: Technology Audit Integration

The tech audit (`video_tech_audit_feb2026.md`) contains verified, production-ready code patterns. Here's what maps where:

### Code Pattern → Target Script Mapping

| Tech Audit Code | Target Script | What It Provides |
|----------------|---------------|------------------|
| `prep_characters.py` (Section 8b) | `scripts/prep_characters.py` | Complete Asset Factory — rembg + OpenCV auto-slice. Copy verbatim. |
| `enforce_safe_zone()` (Section 9a) | `scripts/safe_zone.py` | Dual-axis safe zone auto-snap. Horizontal: center 56% (x: 424-1496 at 1920). Vertical: Y 10-65%, X 10-85%. |
| `compute_render_signature()` / `should_render()` (Section 9b) | `scripts/render_signature.py` | SHA256(audio + profile + manifest). Skip if hash matches AND all 7 outputs exist. |
| `preflight_validate()` (Section 9e) | `scripts/preflight_validator.py` | Verify all asset paths in manifest exist on disk. Abort missing-asset songs before render. |
| `analyze_song()` with confidence (Section 4) | `scripts/analyze_catalog.py` | librosa analysis with key_confidence > 0.15, mode_confidence > 0.10 safety valve. |
| FFmpeg blur-fill command (Section 4) | `scripts/batch_produce.py` | Exact filter_complex for 1080p→1080×1920 blur-fill. |
| `get_vertical_strategy()` / `build_vertical_command()` (Section 4) | `scripts/batch_produce.py` | Resolution-aware strategy selection (blur_fill vs center_crop vs stacked). |
| `generate_meme_sign()` (Section 8e) | `scripts/meme_sign_render.py` | PIL text rendering onto blank_sign.png template. |
| `breathing_scale()` (Section 8d) | `scripts/baseline_master.py` | Sine wave scale: `1.0 + 0.02 * sin(2πt/2.0)` — 2-second cycle, ±2%. |
| Baseline Master Recipe (Section 10) | `scripts/baseline_master.py` | Ken Burns pan + beat pulse + W&B breathing/bounce + meme sign end card. |
| Character dynamics JSON (Section 8a) | `data/mood_map.json` | Weeter/Blubby role definitions + pose assignments. Already provided by user. |
| Artist profile schema (Section 7) | `scripts/generate_artist_profile.py` | New fields: vertical_style, weeter_blubby_default, weeter_blubby_frequency. |

### Key Verified FFmpeg Commands

**Blur-fill (default for 1080p vertical):**
```bash
ffmpeg -i master.mp4 \
  -filter_complex "
    [0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=20:5[bg];
    [0:v]scale=1080:-2:force_original_aspect_ratio=decrease[fg];
    [bg][fg]overlay=(W-w)/2:(H-h)/2
  " \
  -c:v libx264 -crf 18 -preset medium -c:a aac -t 59 short_blurfill.mp4
```

**Center-crop (4K only):**
```bash
ffmpeg -i master_4k.mp4 -vf "crop=1215:2160:(iw-1215)/2:0,scale=1080:1920" \
  -c:v libx264 -crf 18 -c:a aac -t 59 short_crop.mp4
```

---

## Section 4: Custom Code Workflow Redesign

### 4a. The Canonical 6-Step Pipeline (with Preflight)

```
┌──────────────────────────────────────────────────────────────────────┐
│  STEP 0: ASSET PREP                                                  │
│  Run prep_characters.py (one-time setup)                             │
│  → assets/characters/{weeter,blubby,together}/{emotion}/{pose}.png   │
└──────────────────────────────────────┬───────────────────────────────┘
                                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STEP 1: INGESTION  (ingest_song.py)                                 │
│  Pull WAV/MP3 + metadata from Make-Music agent                       │
│  Check for creative_brief.json                                       │
│  → catalog/{artist}/{song_id}/audio.wav + metadata.json              │
└──────────────────────────────────────┬───────────────────────────────┘
                                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STEP 1.5: PREFLIGHT  (preflight_validator.py)                       │
│  Verify ALL asset paths exist on disk                                │
│  Audio file? Character PNGs? Backgrounds? Fonts?                     │
│  → PASS: proceed  |  FAIL: abort song, log PREFLIGHT_FAIL           │
└──────────────────────────────────────┬───────────────────────────────┘
                                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STEP 2: ANALYSIS  (analyze_catalog.py)                              │
│  librosa: BPM, beats, key (confidence), energy, duration             │
│  Safety valve: skip mood mapping if analysis_reliable=false           │
│  mood_map.json: select W&B poses (project-root-relative paths)       │
│  Priority chain: Creative Brief → Artist Profile → Mood Map → Genre  │
│  → song_manifest.json with all paths + metadata                      │
└──────────────────────────────────────┬───────────────────────────────┘
                                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STEP 3: CREATION  (baseline_master.py  OR  generate_visuals.py)     │
│  Phase 1: Baseline Recipe (Ken Burns + beat pulse + W&B overlay)     │
│  Phase 2+: ComfyUI genre workflows + AI-generated clips             │
│  All overlays within horizontal Safe Zone (center 56%)               │
│  → master_video.mp4 (1920×1080)                                     │
└──────────────────────────────────────┬───────────────────────────────┘
                                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STEP 4: ASSEMBLY  (batch_produce.py)                                │
│  Render 7 formats from master                                        │
│  Blur-fill for 1080p vertical | Center-crop for 4K                   │
│  Hash-based idempotency: SHA256 check → skip if unchanged            │
│  Animated W&B overlays with breathing + beat bounce                  │
│  Meme Sign end card on every format                                  │
│  Vertical Social UI Safe Zone enforcement                            │
│  → 7 output files + assembly_report.json                             │
└──────────────────────────────────────┬───────────────────────────────┘
                                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STEP 5: CATALOGING  (catalog_outputs.py)                            │
│  Save to catalog/{artist}/{song_id}/                                 │
│  Write render_signature.txt                                          │
│  Update progress_log.json                                            │
│  Generate upload_metadata.json per platform                          │
└──────────────────────────────────────────────────────────────────────┘
```

### 4b. Metadata & Audio Orchestration (analyze_catalog.py)

**Complete rewrite.** New capabilities:
1. librosa analysis with **confidence scoring** — key_confidence and mode_confidence computed
2. **Safety valve**: if key_confidence < 0.15 OR mode_confidence < 0.10 → `analysis_reliable: false` → skip mood mapping, use genre defaults
3. **Mood mapping** via mood_map.json — 7 rules evaluated against BPM/key/energy/genre → selects W&B poses
4. **Creative Brief merging**: if `creative_brief.json` exists, it overrides all automated decisions
5. **Artist profile check**: load artist_profile.json, apply visual overrides
6. **Project-root-relative paths**: all paths in manifest as `assets/characters/weeter/hype/rocket_ship.png` — never machine-specific
7. **Preflight integration**: after building manifest, verify all referenced paths exist

**Output:** song_manifest.json containing BPM, beats, key, mood, confidence scores, W&B pose paths, visual directives, and status (READY_FOR_ASSEMBLY or ABORTED_PREFLIGHT).

### 4c. Creative & Character Layer

**Creative Brief System:** Optional per-song `creative_brief.json` in `catalog/{artist}/{song_id}/`. Highest priority in the decision chain. Fields: mood_override, weeter_pose, blubby_pose, background_override, color_override.

**Asset Factory:** `prep_characters.py` from tech audit. Runs once to:
- Strip white backgrounds from character sheets (rembg)
- Auto-slice multi-pose sheets into individual PNGs (OpenCV)
- Organize into `assets/characters/{character}/{emotion}/{pose}.png`
- Support manual bounding box overrides via `slice_overrides.json`

**Character Dynamics (NEVER VIOLATE):**
- Weeter (Brown Bear): Leader. Poses: megaphone, rocket, money_bag, flexing, pointing, sunglasses. Left, larger.
- Blubby (Yellow-Green Alien): Reactor. Poses: mind_blown, magnifying_glass, scared, stars, thinking, peeking. Right, smaller.
- Never swap roles unless Creative Brief explicitly overrides.

**Breathing Animation (MANDATORY — no static PNGs):**
- 2-second sine wave scale: 98%→102% (`1.0 + 0.02 * sin(2πt/2.0)`)
- Beat bounce: 5-10px Y-axis offset on kick drum beats from librosa
- Entrance: bounce-in from bottom, ease-out (0.5 sec)
- Exit: fade out (0.3 sec)

**Mood Mapping:** `mood_map.json` with 7 rules:
- hype (BPM>140 + major), happy (BPM>120 + major), sad (BPM<90 + minor), moody (BPM 90-120 + minor), chill (BPM 90-120 + major), explosive (energy_high + BPM>130), sophisticated (jazz/classical)
- Default: happy/thumbs_up poses
- Safety valve: skip if analysis_reliable=false

**Meme Sign Generator:** `meme_sign_render.py` — PIL text rendering on blank_sign.png template. Song Title + Artist Name. Same breathing/bounce animation. Positioned within Safe Zone for each format type.

**AI Clip Library:** ToonCrafter + Kling builds over time. Stored in `assets/characters/animated/`.

### 4d. Production Rules (NON-NEGOTIABLE)

1. **Resolution Strategy:** Blur-fill for 1080p vertical. Center-crop for 4K only. **Never upscale 607px.**
2. **Horizontal Safe Zone:** Center 56% of 16:9 master (x: 424-1496 at 1920px width).
3. **Vertical Social UI Safe Zone:** Y 10-65%, X 10-85% on 9:16 outputs. Content Safe Zone avoids Following tabs (top 10%), Like/Comment/Share (right 15%), and Caption/username (bottom 25%).
4. **Hash-Based Idempotency:** SHA256(audio_bytes + artist_profile_JSON + manifest_JSON). Skip if hash matches AND all 7 outputs exist. Support `--force` flag.
5. **Librosa Confidence:** key_confidence > 0.15, mode_confidence > 0.10. Else skip mood mapping → genre fallback.
6. **Project-Root-Relative Paths:** All manifest paths as `assets/characters/...` format. No machine-specific paths. batch_produce.py reads as-is. No path concatenation.
7. **Preflight Validation (Step 1.5):** Verify all asset paths exist before rendering. Abort songs with missing assets. Log PREFLIGHT_FAIL. Run on entire batch first for fail-fast.

### 4e. Baseline Master Recipe (Phase 1)

Produces a professional video with zero AI dependency:
1. **Background:** Ken Burns pan (zoom + drift) on album art or genre-matched landscape
2. **Energy:** Beat-synced brightness pulse via FFmpeg `eq` filter at beat timestamps
3. **Characters:** W&B breathing/bounce at intro (3 sec) + Meme Sign end card (5 sec). Within horizontal Safe Zone.
4. **Branding:** Artist name + song title within Safe Zone. Artist profile colors.
5. **Audio:** Full track.

**Result:** Every song has a branded video on Day 1.

### 4f. Batch Processing

- JSON manifest → FFmpeg renders → 7 formats with blur-fill vertical
- Idempotency check (SHA256) before each song — skip unchanged
- Preflight validates entire batch first — fail-fast
- Safe Zone enforcement before each overlay composite
- Progress log: rendered / skipped / PREFLIGHT_FAIL / RENDER_FAIL
- Estimated throughput: ~14 min/song, 4-5 songs/hour

### 4g. Genre-to-Visual Decision Tree

Define visual styles for all 21 genres with:
- Default artist_profile.json field values (colors, typography, motifs)
- Default W&B poses per genre
- Default ComfyUI workflow (Phase 2+)
- Default background style for Baseline Recipe

Priority chain: Creative Brief → Artist Profile → Mood Map (if reliable) → Genre Defaults → System Default (happy/thumbs_up).

### 4h. Format Pipeline

7 outputs from 1 master. All include animated Meme Sign end card. Vertical formats use blur-fill (1080p). All overlays respect Social UI Safe Zone on vertical outputs.

| Format | From Master | Strategy | W&B Position |
|--------|-------------|----------|-------------|
| Full Music Video | Direct (16:9) | None | Horizontal Safe Zone |
| YouTube Short | Crop to 9:16 | Blur-fill | Vertical Safe Zone |
| TikTok Clip | Crop to 9:16 | Blur-fill | Vertical Safe Zone |
| Instagram Reel | Crop to 4:5 or 9:16 | Blur-fill | Vertical Safe Zone |
| Lyric Video | New render (16:9) | Text overlay | Horizontal Safe Zone |
| Visualizer | New render (16:9) | Audio-reactive | No character overlay |
| Sync Reel | Segment extract (16:9) | Highlight clip | Horizontal Safe Zone |

---

## Section 5: Implementation Plan

### Files to REPLACE

| Current File | Replaced By | Source |
|-------------|-------------|--------|
| `RULES.md` (v2.0) | `RULES.md` (v4 Final) | User-provided `rules_make_videos.md` |

### Files to COPY

| Source | Destination | Notes |
|--------|------------|-------|
| Tech audit Section 8b: `prep_characters.py` | `scripts/prep_characters.py` | Complete Asset Factory — copy verbatim |
| User-provided `mood_map.json` | `data/mood_map.json` | 7 mood rules + character dynamics + safety valve |
| User-provided `video_tech_audit_feb2026.md` | `data/video_tech_audit_feb2026.md` | Already exists — verify current |

### Files to REWRITE

| Script | Rewrite Scope | Key Additions |
|--------|--------------|---------------|
| `analyze_catalog.py` | **Full rewrite** | Confidence scoring, mood mapping, preflight, root-relative paths, Creative Brief merge |
| `batch_produce.py` | **Full rewrite** | Blur-fill vertical, safe zone enforcement, hash idempotency, W&B overlay, meme sign, 7-format pipeline |
| `artist_profile_generator.py` → `generate_artist_profile.py` | **Rename + rewrite** | New schema (vertical_style, weeter_blubby_default, weeter_blubby_frequency) |

### Files to CREATE (New Scripts — 10)

| Script | Type | Purpose |
|--------|------|---------|
| `scripts/safe_zone.py` | Shared module | `enforce_safe_zone()` with format-aware zones (master vs short/tiktok/reel) |
| `scripts/render_signature.py` | Shared module | SHA256 hash computation + `should_render()` + `save_render_signature()` |
| `scripts/preflight_validator.py` | Shared module | Verify all manifest asset paths exist. Returns missing list. |
| `scripts/baseline_master.py` | Pipeline Step 3 | Ken Burns pan + beat pulse + W&B breathing overlay → master_video.mp4 |
| `scripts/meme_sign_render.py` | Utility | PIL text onto blank_sign.png → dynamic meme sign per song |
| `scripts/beat_sync_cuts.py` | Utility | Video clips + beat JSON → beat-synced edit |
| `scripts/generate_thumbnails.py` | Utility | Artist profile + album art → platform-specific thumbnails |
| `scripts/lyric_video.py` | Format variant | Audio + LRC + background → lyric video with Safe Zone text |
| `scripts/visualizer.py` | Format variant | Audio + artist colors → audio-reactive visualization |

### Files to DELETE (replaced by rewrites)

| File | Reason |
|------|--------|
| `scripts/generate_visuals.py` | Replaced by baseline_master.py (Phase 1) + future ComfyUI integration (Phase 2) |
| `scripts/catalog_outputs.py` | Functionality merged into batch_produce.py (validation) + catalog step in pipeline |
| `scripts/ingest_song.py` | Rewritten to support Creative Brief checking + root-relative paths |
| All 9 existing `.skills/` SKILL.md files | Replaced by 15 new skills below |
| `data/genre_visual_map.json` | Replaced by updated genre decision tree with W&B pose defaults |
| `data/genre_profile_templates.json` | Replaced by updated templates with character integration |
| `workflows/video-production-pipeline.md` | Replaced by new 6-step pipeline workflow |

### Skills to CREATE (15)

| Skill | Script | Purpose |
|-------|--------|---------|
| `batch-ffmpeg-processor` | batch_produce.py | 7-format FFmpeg pipeline with blur-fill |
| `beat-sync-editor` | beat_sync_cuts.py | Beat-synchronized video editing |
| `thumbnail-generator` | generate_thumbnails.py | Platform-specific thumbnail creation |
| `format-converter` | batch_produce.py | Single-format conversion between the 7 types |
| `lyric-overlay` | lyric_video.py | LRC + audio → lyric video |
| `audio-analyzer` | analyze_catalog.py | librosa analysis + confidence + mood mapping |
| `comfyui-launcher` | generate_visuals.py (Phase 2) | ComfyUI workflow orchestration |
| `artist-profile-manager` | generate_artist_profile.py | Artist profile CRUD with new schema |
| `character-asset-factory` | prep_characters.py | Character sheet → transparent PNG library |
| `mood-mapper` | analyze_catalog.py | mood_map.json → W&B pose selection |
| `meme-sign-generator` | meme_sign_render.py | Dynamic meme sign creation |
| `character-animator` | baseline_master.py | Breathing + beat bounce sprite animation |
| `safe-zone-validator` | safe_zone.py | Safe Zone compliance checking |
| `baseline-recipe-builder` | baseline_master.py | Ken Burns + beat pulse + W&B master creation |
| `render-signature-manager` | render_signature.py | Hash idempotency management |

### Phased Rollout

**Phase 1 (Week 1-2): Foundation + Baseline Recipe**
- Replace RULES.md with v4 Final
- Copy prep_characters.py from tech audit → run it, rename outputs descriptively
- Copy mood_map.json to data/
- Create starter artist profiles for all artists (with new schema fields)
- Write shared modules: safe_zone.py, render_signature.py, preflight_validator.py
- Rewrite: analyze_catalog.py (confidence + mood + preflight + root-relative)
- Write: baseline_master.py, batch_produce.py, meme_sign_render.py
- Write: ingest_song.py (rewrite with Creative Brief + root-relative)
- **Result:** Every song gets a professional branded video. Pipeline is crash-resistant.

**Phase 2 (Week 3-4): AI Enhancement**
- ComfyUI setup and workflow testing
- ToonCrafter first 20 animated clips
- Daily Kling generations for character clip library
- Genre-to-visual decision tree as JSON config (updated with W&B defaults)
- Write: lyric_video.py, beat_sync_cuts.py
- Review/refine auto-generated artist profiles (mark human_reviewed: true)

**Phase 3 (Week 5-8): Scale & Polish**
- Write: visualizer.py, generate_thumbnails.py
- All 15 skill SKILL.md files
- Shotstack templates evaluation
- Master orchestrator chaining all 6 pipeline steps
- End-to-end testing across all genres
- Evaluate Cartoon Animator for long-form content

**Phase 4 (Month 3+): Weeter & Blubby Content Empire**
- Full character rigging in Cartoon Animator
- "W&B React" social content series
- Animated episodes
- Merchandise exploration

### Complete File Manifest (Post-Execution)

```
Make Videos/
├── RULES.md                              ← v4 Final (replaced)
├── data/
│   ├── mood_map.json                     ← User-provided (copied)
│   ├── video_tech_audit_feb2026.md       ← Reference (existing)
│   ├── genre_visual_map.json             ← Updated with W&B defaults
│   ├── genre_profile_templates.json      ← Updated with character fields
│   └── OVERHAUL_STRATEGY_v3.0.md         ← This document
├── scripts/
│   ├── prep_characters.py                ← Copied from tech audit
│   ├── safe_zone.py                      ← New shared module
│   ├── render_signature.py               ← New shared module
│   ├── preflight_validator.py            ← New shared module
│   ├── ingest_song.py                    ← Rewritten
│   ├── analyze_catalog.py                ← Rewritten
│   ├── generate_artist_profile.py        ← Renamed + rewritten
│   ├── baseline_master.py                ← New
│   ├── batch_produce.py                  ← Rewritten
│   ├── meme_sign_render.py               ← New
│   ├── beat_sync_cuts.py                 ← New
│   ├── generate_thumbnails.py            ← New
│   ├── lyric_video.py                    ← New
│   └── visualizer.py                     ← New
├── .skills/ (15 skills)
│   ├── batch-ffmpeg-processor/SKILL.md
│   ├── beat-sync-editor/SKILL.md
│   ├── thumbnail-generator/SKILL.md
│   ├── format-converter/SKILL.md
│   ├── lyric-overlay/SKILL.md
│   ├── audio-analyzer/SKILL.md
│   ├── comfyui-launcher/SKILL.md
│   ├── artist-profile-manager/SKILL.md
│   ├── character-asset-factory/SKILL.md
│   ├── mood-mapper/SKILL.md
│   ├── meme-sign-generator/SKILL.md
│   ├── character-animator/SKILL.md
│   ├── safe-zone-validator/SKILL.md
│   ├── baseline-recipe-builder/SKILL.md
│   └── render-signature-manager/SKILL.md
├── assets/
│   └── characters/                       ← Output of prep_characters.py
│       ├── weeter/{emotion}/{pose}.png
│       ├── blubby/{emotion}/{pose}.png
│       ├── together/{emotion}/{pose}.png
│       └── animated/                     ← AI clips (Phase 2+)
├── workflows/
│   └── video-production-pipeline.md      ← Updated for 6-step pipeline
├── catalog/
│   ├── {artist}/
│   │   ├── artist_profile.json           ← Updated schema
│   │   └── {song_id}/
│   │       ├── audio.wav
│   │       ├── song_manifest.json
│   │       ├── creative_brief.json       ← Optional
│   │       ├── render_signature.txt
│   │       ├── progress_log.json
│   │       ├── full_video.mp4
│   │       ├── short_916.mp4
│   │       ├── tiktok.mp4
│   │       ├── reel_4x5.mp4
│   │       ├── lyric_video.mp4
│   │       ├── visualizer.mp4
│   │       └── sync_reel.mp4
│   ├── progress_log.json
│   └── job_queue.json
└── data/raw_sheets/                      ← Input for prep_characters.py
    ├── Weeter-happy.jpg
    ├── Blubby-cool.png
    ├── Together-hype.jpg
    └── slice_overrides.json
```

---

## Section 6: Ecosystem Impact

### Agent Architecture

Make Videos stays as **one agent with two operational modes**:
- **Production Engine:** Technical execution of batch pipeline, FFmpeg commands, hash checks, safe zone enforcement
- **Creative Director:** Artist profiles, creative briefs, genre decision tree, quality review, character dynamics validation

### Integration Points

| Agent | Integration | Direction |
|-------|------------|-----------|
| **Ridgemont Catalog Manager** | Owns artist_profile.json + creative_brief.json storage | Reads from Catalog Manager |
| **Make-Music** | Outputs WAV/MP3 to monitored ingestion location | Receives from Make-Music |
| **Suno Prompt Generator** | Exports mood/genre classification data for mood_map.json | Receives genre data |
| **Canva (MCP)** | Bulk Create thumbnails, Brand Kit integration | Uses Canva API |
| **Figma (MCP)** | Genre visual identity templates | Uses Figma API |

### Future Agent Evaluation

| Candidate Agent | Purpose | Evaluate When |
|----------------|---------|---------------|
| Asset Library Manager | Central character asset versioning + retrieval | Phase 3 (Week 5-8) |
| Distribution Agent | Automated multi-platform upload + scheduling | Phase 3+ |

### Registry Update

Registry v3.3 → v3.4 after execution:
- Make Videos purpose updated to reference Weeter & Blubby
- Skills: 9 → 15
- Health score bump reflecting complete pipeline rebuild
- Notes reflecting v3.0 overhaul completion

---

## Execution Command

When ready to implement, say **"execute plan"** and the following will happen:
1. RULES.md replaced with v4 Final
2. mood_map.json and prep_characters.py copied to agent
3. 3 shared modules created (safe_zone, render_signature, preflight_validator)
4. 3 scripts fully rewritten (analyze_catalog, batch_produce, generate_artist_profile)
5. 4 new scripts created (baseline_master, meme_sign_render, ingest_song rewrite, + remaining)
6. 15 skill definitions created
7. Artist profiles updated with new schema fields
8. Registry updated to v3.4
9. All cross-references verified
