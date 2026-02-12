# Make Videos Agent — Comprehensive Overhaul Strategy v2.0
## From Crypto YouTube Engine → Music Video Production Pipeline
### Ridgemont Studio | February 2026

> **Scope:** Transform the Make Videos agent from a crypto YouTube content creator into a full-scale music video production pipeline serving 121+ songs, 21 genres, and 200+ fictional artists across 7 output formats.

---

## Table of Contents

1. [Current State & Gap Analysis](#section-1)
2. [Ridgemont Studio Catalog Requirements](#section-2)
3. [Technology Audit Integration](#section-3)
4. [Custom Code Workflow Redesign](#section-4)
5. [Implementation Plan](#section-5)
6. [Ecosystem Impact](#section-6)

---

## Section 1: Current State & Gap Analysis

### What Exists and Works

The Make Videos agent currently operates as a **crypto YouTube content engine** with the following established capabilities:

- **Daily Content Pipeline** (`daily-content-pipeline.md`): Automated workflow for "Blockchain Basics" (@4blockchainbasics) that handles research, script generation, and upload scheduling for YouTube
- **Multi-Platform Upload Automation** (`upload-all` skill): Chrome-based browser automation capable of publishing to YouTube, TikTok, Instagram, Rumble, and Truth Social from a single source
- **Voice Reference System** (`Voice_Reference/` directory): Comprehensive style guide and voice profile capturing John's crypto-presenting persona
- **Remotion Framework Integration** (v4.0.414, React 19): Installed and operational, with one completed promotional video for Ridgemont Studio (`RidgemontVideo.tsx`) plus HelloWorld and WeeterAndBlubby demos
- **Skill Set** (3 skills): `yt-shorts` for short-form generation, `yt-cardano-daily` for daily crypto episodes, and `upload-all` for multi-platform distribution
- **Browser Automation Foundation**: Established Chrome integration patterns for headless operations

### Manual Bottlenecks Identified

- **No Automated Video Production**: All video content is manually recorded by John; no programmatic video generation
- **No Batch Processing**: Everything operates one-at-a-time; no pipeline for processing 121+ songs
- **Missing Audio Analysis Tools**: No librosa, no beat detection, no BPM extraction
- **No AI Video Generation Integration**: ComfyUI not integrated; no Wan, no LTX, no SVD
- **No FFmpeg Pipeline**: No format conversion automation
- **Stale Content Review**: `YT_Content_Review/` contains only a handful of dated files

### Vague or Outdated Rules

- **GAME_PLAN.md as Config**: Entirely YouTube/crypto-focused; no ecosystem-standard sections
- **No RULES.md**: Lacks standard Identity, Behavior Guidelines, or Related Agents sections
- **Cloudinary Referenced But Not Integrated**: Asset management tool mentioned but no integration exists
- **Irrelevant Success Metrics**: KPIs reference "1,000 YouTube subscribers"
- **YouTube-Specific Analytics**: Sections assume Creator Studio dashboard

### Structural Gaps for Music Video Production

- Zero music video production capability
- No artist visual identity system
- No genre-to-visual mapping
- No catalog integration with Ridgemont Catalog Manager
- No batch assembly pipeline
- No format pipeline (7 formats from single source)
- No artist_profile.json system
- Remotion underutilized (one static promo only)

### The Fundamental Disconnect

| Crypto YouTube Pipeline | Music Video Production Pipeline |
|---|---|
| Daily research + topical scripts | Pre-composed songs + fixed audio |
| Live recording + minimal editing | Audio analysis + visual synthesis |
| One format (YouTube 16:9) | Seven formats from single source |
| Subscriber growth metrics | Catalog consistency + licensing readiness |
| Editorial calendar cadence | Batch processing at scale |

The current infrastructure solves the wrong problem entirely. A comprehensive rebuild is required.

---

## Section 2: Ridgemont Studio Catalog Requirements

### Scale Parameters

- **121+ Songs** currently in catalog, with ongoing additions via Make-Music → Suno Studio pipeline
- **200+ Fictional Artists** distributed across 21 genres
- **21 Genre Categories**: Pop, Rock, Hip Hop, R&B, Electronic, Country, Jazz, Blues, Classical, Folk, Reggae, Latin, Metal, Punk, Funk, Gospel, World, Ambient, Indie, Alternative, Cinematic
- **7 Output Formats per Song**: Minimum **847 total video assets**
- **Catalog Growth**: Continuous; new songs trigger new production workflows

### Seven Output Format Specifications

1. **Full Music Video** (16:9, 3-5 min) — Narrative or performance style; highest production value; primary showcase
2. **YouTube Short** (9:16, 15-59 sec) — Hook-driven vertical clip; text overlay with artist name + song title
3. **TikTok Clip** (9:16, 15-60 sec) — Trending-style with burned-in captions and glitch transitions
4. **Instagram Reel** (9:16, 15-90 sec) — Polished visual-first; artist signature graphics
5. **Lyric Video** (16:9, full length) — Kinetic typography synced to audio via librosa beat data
6. **Audio-Reactive Visualizer** (16:9, full length) — Beat-synced abstract visuals; no text
7. **Sync Licensing Reel** (16:9, 30-60 sec) — Clean professional showcase; no overlays; highest quality

### artist_profile.json System

Every artist requires a visual identity configuration file:

```json
{
  "artist_name": "DJ Chromosphere",
  "genre": "Electronic / EDM",
  "publishing_entity": "Frozen Cloud Music",
  "visual_identity": {
    "primary_colors": ["#00E5FF", "#FF00FF", "#0D0D0D"],
    "secondary_colors": ["#7B1FA2", "#00BCD4"],
    "typography": {
      "heading_font": "Orbitron",
      "body_font": "Exo 2",
      "style": "all-caps, tight tracking"
    },
    "visual_motifs": ["glitch textures", "neon grid lines", "particle clouds"],
    "color_grading": "high contrast, cool shadows, neon highlights",
    "camera_style": "fast cuts, zoom pulses on beat, dutch angles",
    "reference_images": ["assets/chromosphere_ref_01.png"],
    "comfyui_workflow": "workflows/edm_glitch_neon.json",
    "sd_prompt_prefix": "cyberpunk neon club, glitch art, dark background, electric cyan and magenta"
  },
  "thumbnail_template": "templates/edm_thumbnail_v2.psd",
  "brand_watermark": "assets/frozen_cloud_watermark.png",
  "auto_generated": true,
  "human_reviewed": false
}
```

### Brand Consistency Requirement

Without enforced artist_profile.json standards, each video generation becomes random and the catalog looks incoherent. Every video produced — all 7 formats for every song — must reference the artist's profile for color palette enforcement, typography consistency, visual motif application, and camera/style uniformity.

---

## Section 3: Technology Audit Integration

*Reference: `data/video_tech_audit_feb2026.md` (verified February 8, 2026)*

**Priority**: Open Source/Local → Python Libraries → FFmpeg → Developer APIs → AI Video Free Tiers

### Tier 1: Mac-Feasible Local Models (Primary)

| Model | Params | VRAM | Output | Key Use Case |
|---|---|---|---|---|
| **Wan 2.1 T2V-1.3B** | 1.3B | ~8 GB | 480p, 5s | Best entry point. Consumer GPU friendly. |
| **LTX-2** | 19B | 8-12 GB (distilled) | Up to 4K, 10s+ | Audio+video sync in single pass. Jan 2026. |
| **Stable Video Diffusion XT** | N/A | ~6 GB | 576x1024, 2-4s | Image-to-video. Proven stable on Mac. |

### Specialized Audio-Driven Models (Critical)

| Model | Use Case | Why Critical |
|---|---|---|
| **Wan2.2-S2V** | Audio-driven lip sync, singing, dialogue | Native music video generation from audio |
| **Deforum** | Audio-reactive abstract visuals | Essential for Electronic/Ambient/Metal genres |
| **stable-diffusion-videos** | Beat-aware interpolation | Smooth transitions between prompts |

### Python Production Backbone

| Library | Purpose | Key Function |
|---|---|---|
| **librosa** | BPM, beat detection, onset, key, chroma | Core analysis — every cut must be beat-synced |
| **MoviePy** | Programmatic video editing, compositing | Clip assembly, text overlays, transitions |
| **Pillow** | Image processing, thumbnails | Brand overlays, lyric cards at scale |
| **pydub** | Audio manipulation | Format conversion, silence detection |
| **Manim** | Motion graphics, kinetic typography | Lyric video animations |

### FFmpeg — Format Pipeline Engine

All 7 formats derive from single source via FFmpeg:
```bash
# Full → YouTube Short (center crop 9:16, 59s max)
ffmpeg -i full_video.mp4 -vf "crop=ih*9/16:ih,scale=1080:1920" -t 59 -c:a aac short.mp4
# Full → Instagram Reel (4:5 crop, 90s)
ffmpeg -i full_video.mp4 -vf "crop=ih*4/5:ih,scale=1080:1350" -t 90 -c:a aac reel.mp4
# Full → TikTok (9:16, 60s)
ffmpeg -i full_video.mp4 -vf "crop=ih*9/16:ih,scale=1080:1920" -t 60 -c:a aac tiktok.mp4
```

### Free Tier Supplementation (NOT Primary)

- **Kling 2.6**: 66 credits/day for 1-6 supplemental hero shots
- **Luma AI**: 500 credits/month for cinematic quality
- **Critical Reality**: One 8-second render uses 15-35% of monthly free credits. Free tiers are supplements only.

### What WON'T Work at Scale

| Approach | Why It Fails |
|---|---|
| Relying solely on AI free tiers | 1 video uses 15-35% of monthly credits |
| Running 13B+ models on MacBook | Needs 60-80GB VRAM |
| Manual editing per song | 847+ videos not humanly feasible |
| Paid tiers without automation | Even $95/mo Runway can't cover volume |
| Ignoring artist visual consistency | Catalog looks incoherent |

### Technology Stack Summary

| Layer | Primary Tool | Purpose |
|---|---|---|
| Audio Analysis | librosa | BPM, beats, key, spectrum |
| Local AI Video | Wan 2.1 + LTX-2 | Generate video frames on Mac |
| Audio-Sync Video | Wan2.2-S2V | Music video with beat/lip sync |
| Motion Graphics | Manim | Kinetic typography, lyric videos |
| Workflow Engine | ComfyUI | Integrate all models, batch processing |
| Video Composition | MoviePy | Assemble clips, overlays, graphics |
| Format Pipeline | FFmpeg | Crop, resize, transcode all 7 formats |
| Catalog Integration | artist_profile.json | Visual consistency across 200+ artists |
| Free Tier Supplement | Kling 2.6, Luma AI | Hero shots only |

---

## Section 4: Custom Code Workflow Redesign

### 4A. The 5-Step Production Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: INGESTION (8-12s per song)                             │
│  ingest_song.py — validate audio, init directory, load profile  │
├─────────────────────────────────────────────────────────────────┤
│  STEP 2: ANALYSIS (15-25s per song)                             │
│  analyze_catalog.py — librosa BPM/beats/key/mood → manifest     │
├─────────────────────────────────────────────────────────────────┤
│  STEP 3: CREATION (3-8 min per song)                            │
│  generate_visuals.py — ComfyUI genre workflow → raw clips       │
├─────────────────────────────────────────────────────────────────┤
│  STEP 4: ASSEMBLY (8-12 min per song)                           │
│  batch_produce.py — FFmpeg + MoviePy → all 7 formats            │
├─────────────────────────────────────────────────────────────────┤
│  STEP 5: CATALOGING (3-5s per song)                             │
│  catalog_outputs.py — validate, log, notify Master Agent        │
└─────────────────────────────────────────────────────────────────┘
```

**Step 1: Ingestion** — Pull new song from Make-Music (WAV/MP3 + metadata). Validate audio integrity. Check for existing artist_profile.json; create starter if missing. Copy to `/catalog/{artist}/{song}/`. Script: `ingest_song.py`

**Step 2: Analysis** — librosa extracts BPM, beat_times, onset_times, estimated_key, duration, chroma. Calculate mood/energy score. Map genre → visual style via decision tree. Output: `song_manifest.json`. Script: `analyze_catalog.py`

**Step 3: Creation** — Generate visual assets using genre-appropriate pipeline (Wan2.2-S2V for performance, Deforum for audio-reactive, Wan 2.1/LTX-2 for narrative, Manim for typography, SVD for scenic). Apply artist_profile.json styling. Script: `generate_visuals.py`

**Step 4: Assembly** — FFmpeg renders all 7 formats. Beat-synced cuts using librosa data. MoviePy for compositing. Pillow for thumbnails. Manim for lyric animations. Script: `batch_produce.py`

**Step 5: Cataloging** — Save to `/catalog/{artist}/{song}/{format}/`. Update progress log. Flag failures. Notify Master Agent. Generate upload metadata per platform. Script: `catalog_outputs.py`

### 4B. Genre-to-Visual Decision Tree (All 21 Genres)

| Genre | Visual Style | Primary Model | Color Palette | Motion Style | Workflow Type |
|---|---|---|---|---|---|
| **Pop** | Bright, colorful, high-energy | Wan2.2-S2V | Saturated pinks, yellows, blues | Fast cuts on beat; energetic zoom | audio_driven_performance |
| **Rock** | Gritty, high-contrast, cinematic | SVD XT | Charcoal, steel gray, deep red | Slow-mo instruments; dramatic shifts | image_to_video_cinematic |
| **Hip Hop** | Urban, bold typography | Wan2.2-S2V | Black, white, gold, neon | Rapid cuts; glitch transitions | audio_driven_performance_glitch |
| **R&B** | Smooth, intimate, warm | LTX-2 | Gold, rose gold, cream | Slow deliberate motion; long takes | cinematic_slow_motion |
| **Electronic** | Neon, glitch, particles | Deforum | Cyan, magenta, purple, black | Strobing on kicks; geometric | audio_reactive_electronic |
| **Country** | Warm earth tones, natural | SVD XT | Sunset gold, sage, sky blue | Slow pastoral pans; lens flare | image_to_video_scenic |
| **Jazz** | Noir aesthetic, smoky | SVD XT | Navy, charcoal, accent golds | Slow dolly; heavy film grain | image_to_video_noir |
| **Blues** | Raw, vintage film | SVD XT | Sepia, dust brown, pale blue | Slow dolly; textured overlays | image_to_video_vintage |
| **Classical** | Elegant, orchestral | LTX-2 | Deep black, rich gold, cream | Sweeping cinematic; long tracking | cinematic_orchestral |
| **Folk** | Earthy, handcrafted | SVD XT | Warm brown, sage, natural | Soft focus; instrument close-ups | image_to_video_pastoral |
| **Reggae** | Tropical, sun-drenched | Wan 2.1 T2V | Bright yellow, turquoise, lime | Relaxed steady motion; warm | audio_driven_tropical |
| **Latin** | Passionate, rhythmic | Wan2.2-S2V | Deep red, gold, warm orange | Fast syncopated; dance focus | audio_driven_dance_rhythmic |
| **Metal** | Dark, aggressive | Deforum | Black, deep red, white | Rapid cuts on drops; strobe | audio_reactive_metal |
| **Punk** | Raw, DIY, collage | SVD XT | Black, white, neon accents | Rapid-fire; VHS effects | image_to_video_diy_collage |
| **Funk** | Groovy, retro 70s | Wan 2.1 T2V | Burnt orange, mustard, gold | Groovy syncopated; disco lighting | audio_driven_funk_disco |
| **Gospel** | Uplifting, light-filled | LTX-2 | White, gold, sky blue | Sweeping uplifting; light rays | cinematic_spiritual |
| **World** | Cultural diversity, patterns | SVD XT | Rich jewel tones | Slow respectful pans; pattern morph | image_to_video_cultural_motifs |
| **Ambient** | Atmospheric, ethereal | Deforum | Muted pastels, soft grays | Slow drift; NO beat sync; fog | audio_reactive_ambient_drift |
| **Indie** | Lo-fi, quirky, analog | SVD XT | Desaturated + accent colors | Gentle jerky; film grain; VHS | image_to_video_analog_quirky |
| **Alternative** | Experimental, mixed media | Deforum + SVD | Eclectic, unpredictable | Chaotic intentional; hybrid | audio_reactive_experimental |
| **Cinematic** | Epic, widescreen | LTX-2 | Deep blue, rich gold, cinematic | Sweeping widescreen; dramatic | cinematic_epic_dramatic |

### 4C. Format Pipeline (7 Formats from Single Source)

| Format | Resolution | FPS | Duration | Processing | FFmpeg Pattern |
|---|---|---|---|---|---|
| Full Music Video | 1920×1080 | 24 | Full | Title/end cards + watermark | `scale=1920:1080,fps=24` |
| YouTube Short | 1080×1920 | 30 | 45-59s | Center crop + text overlay | `crop=ih*9/16:ih,scale=1080:1920` -t 59 |
| TikTok Clip | 1080×1920 | 30 | 55-60s | Glitch transitions + captions | `crop=ih*9/16:ih,scale=1080:1920` -t 60 |
| Instagram Reel | 1080×1920 | 30 | 80-90s | Polished + beat-pulse text | `crop=ih*9/16:ih,scale=1080:1920` + fade |
| Lyric Video | 1920×1080 | 24 | Full | Manim kinetic typography | Background blur + lyric overlay |
| Audio Visualizer | 1920×1080 | 60 | Full | Deforum/FFmpeg showfreqs | `showfreqs=s=1920x1080:mode=line` |
| Sync Licensing | 1920×1080 | 24 | 30-60s | Clean cut, no overlays | `pad=1920:1216:0:68:black` + CRF 16 |

### 4D. Batch Processing Architecture

**Queue System**: JSON-based job queue at `/catalog/job_queue.json` with priority ordering, retry logic (max 3), and per-format status tracking.

**Parallelization Strategy**:
- Ingestion + Analysis: 2-4 songs in parallel (CPU only)
- Creation: 1 song at a time (GPU serialized)
- Assembly: 7 formats in parallel per song
- Cataloging: Batch multiple songs

**Throughput Estimate**:
- ~14 minutes per song (single machine, 4-core CPU, 1 GPU)
- ~4-5 songs/hour
- ~33 songs per 8-hour day
- **121 songs in 3-4 workdays** on single machine

---

## Section 5: Implementation Plan

### 5A. New RULES.md Summary

Repositions agent as **Technical Director — Video Production Pipeline** with 10 behavior rules:

1. ALWAYS check artist_profile.json before generating visuals
2. ALWAYS run librosa analysis before generation — every cut must be beat-synced
3. ALWAYS produce all 7 output formats — no partial deliveries
4. ALWAYS maintain artist visual identity consistency
5. PRIORITIZE local/free tools over paid APIs
6. NEVER exceed 6 Kling clips/day — queue overflow for next day
7. ALWAYS validate outputs before cataloging
8. BATCH process by genre for workflow reuse
9. ALWAYS update progress log after each step
10. REFER specialist questions to appropriate agents

**Related Agents**: Ridgemont Catalog Manager (data source), Make-Music (upstream), frozen-cloud-portal (downstream), X-Posts (downstream), Legal (advisory), YouTube/TikTok Automations (executor), Master Agent (oversight)

### 5B. Eight Skills

| # | Skill | Trigger | Purpose |
|---|---|---|---|
| 1 | `/analyze-song` | Song ID + audio path | Librosa analysis → song_manifest.json |
| 2 | `/generate-visuals` | Song ID + workflow type | ComfyUI genre workflow → raw clips |
| 3 | `/assemble-video` | Song ID + artist name | FFmpeg + MoviePy → all 7 formats |
| 4 | `/batch-produce` | Genre + count | Full pipeline for multiple songs |
| 5 | `/artist-profile` | Artist name + action | Create/update artist_profile.json |
| 6 | `/format-convert` | Source + target format | FFmpeg single-format conversion |
| 7 | `/upload-all` | Song ID + platforms | Multi-platform upload (updated for music) |
| 8 | `/quality-check` | Song ID + format | Validate resolution, sync, codec, integrity |

### 5C. Six Python Scripts

| # | Script | Purpose | Dependencies |
|---|---|---|---|
| 1 | `ingest_song.py` | Validate audio, init directory, load profile | pydub, librosa, json, shutil |
| 2 | `analyze_catalog.py` | Librosa analysis → song_manifest.json | librosa, numpy, json |
| 3 | `generate_visuals.py` | Genre-mapped ComfyUI generation | requests, json, subprocess |
| 4 | `batch_produce.py` | Assemble all 7 formats from clips + audio | moviepy, ffmpeg, Pillow, Manim |
| 5 | `catalog_outputs.py` | Validate, log, notify, generate upload metadata | json, os, requests |
| 6 | `artist_profile_generator.py` | Auto-generate profiles from genre defaults | json, colorsys |

### 5D. Integration Points

**Upstream**: Ridgemont Catalog Manager → Make Videos (new song trigger + metadata); Make-Music → Make Videos (audio delivery)

**Downstream**: Make Videos → frozen-cloud-portal (video embeds); Make Videos → X-Posts (clips for promotion); Make Videos → YouTube/TikTok Automations (upload-ready files); Make Videos → Legal (sync reel review)

**Oversight**: Make Videos → Master Agent (completion status, health metrics, daily summary)

### 5E. Three-Phase Rollout

**Phase 1: Foundation (Week 1-2)**
- Create new RULES.md
- Write + test `ingest_song.py` and `analyze_catalog.py`
- Create `/analyze-song` and `/artist-profile` skills
- Generate starter profiles for all 200+ artists
- Set up ComfyUI on Mac with Wan 2.1 1.3B GGUF
- Pilot with 5 test songs across genre clusters

**Phase 2: Production Pipeline (Week 3-4)**
- Write + test `generate_visuals.py` and `batch_produce.py`
- Build 5 genre-specific ComfyUI workflows
- Create `/generate-visuals`, `/assemble-video`, `/format-convert`, `/batch-produce`, `/quality-check` skills
- Render first 20 songs through full pipeline
- Test all 7 output formats; target ≥95% quality pass rate

**Phase 3: Scale & Optimize (Week 5-8)**
- Write `catalog_outputs.py`; update `/upload-all` skill
- Process remaining 100+ songs (target: 5-10 songs/day)
- Connect all downstream agents
- Full ecosystem integration test
- Complete documentation (OPERATIONS.md, TROUBLESHOOTING.md)
- Target: 121+ songs × 7 formats = 847+ videos complete

---

## Section 6: Ecosystem Impact

### 6A. Agent Split Evaluation

| Option | Description | Recommendation |
|---|---|---|
| **A: Single Agent** | Make Videos handles everything | Simple but context bloat at scale |
| **B: Two Agents** | Production Engine + Creative Director | **RECOMMENDED** — clear separation, human QA gate |
| **C: Three Agents** | Engine + Director + Distribution | Over-engineered for 121 songs |

**Recommendation: Option B (Two Agents)**

1. **Make Videos — Production Engine**: Pipeline execution (ingest → analyze → generate → assemble → validate → catalog). Skills: `/analyze-song`, `/generate-visuals`, `/assemble-video`, `/batch-produce`, `/quality-check`, `/format-convert`

2. **Make Videos — Creative Director**: Style decisions, artist profiles, quality gates, human approval workflows. Skills: `/artist-profile`, `/review-quality`, `/approve-batch`, `/artist-style-audit`

This provides clear separation, keeps context manageable, and introduces a natural human oversight point before distribution.

### 6B. Changes to Other Agents

| Agent | Change Required | Priority |
|---|---|---|
| **Ridgemont Catalog Manager** | Add `video_status` field to song records; add workflow trigger for new songs | High |
| **Make-Music** | Ensure completion notifications include audio path + metadata | High |
| **frozen-cloud-portal** | Add video embed sections to artist pages | High |
| **X-Posts** | Add music video clip posting workflow | Medium |
| **YouTube/TikTok Automations** | Update upload workflow for music video metadata | High |
| **Legal** | Add sync licensing reel review workflow | Medium |
| **Master Agent** | Add video production metrics to health check | Medium |

### 6C. New Agent Assessment

| Proposed Agent | Recommendation | Rationale |
|---|---|---|
| **Video QA Agent** | Not needed now | Keep as skill within Make Videos; revisit at 500+ songs |
| **Distribution Agent** | Not needed now | `/upload-all` skill sufficient; revisit if A/B testing needed |
| **Artist Identity Agent** | Not needed now | Creative Director handles profiles; revisit for merchandising |

---

## Cost Estimate

| Category | Monthly Cost |
|---|---|
| Local generation (ComfyUI, FFmpeg, Python) | $0 (electricity only) |
| Cloud GPU rental (if needed) | $0-100 |
| Kling 2.6 free tier | $0 (66 clips/day) |
| Luma AI free tier | $0 (500 credits/month) |
| Shotstack sandbox | $0 (development/testing) |
| **Total realistic budget** | **$0-100/month** |

---

## Success Metrics

- **Coverage**: 121+ songs × 7 formats = 847+ video assets
- **Quality**: ≥97% pass rate on quality-check validation
- **Throughput**: ≥5 songs/day sustained processing
- **Sync**: Audio/video sync within ±50ms tolerance for ≥98% of outputs
- **Consistency**: 100% of videos reference artist_profile.json
- **Integration**: All downstream agent handoffs working
- **Timeline**: Full catalog processing complete within 8 weeks

---

*Strategy document v2.0 — Generated February 2026*
*Full detailed specifications for each section available in companion documents*
