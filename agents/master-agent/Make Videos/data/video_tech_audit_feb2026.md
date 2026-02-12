# Make Videos Agent — Technology Audit
## Researched February 8, 2026 | For Ridgemont Studio
## FINAL VERSION v4 — All Feedback Incorporated (Claude + Gemini + ChatGPT)

> **Purpose:** Drop this file into `Make Videos/data/` so the Master Agent has verified, current information when executing the overhaul prompt.

---

## 1. OPEN SOURCE / LOCAL VIDEO GENERATION MODELS

### Tier 1: Best for MacBook Pro (Apple Silicon)

| Model | Params | Min VRAM | Resolution | Length | Mac Support | Notes |
|-------|--------|----------|------------|--------|-------------|-------|
| **Wan 2.1 T2V-1.3B** | 1.3B | ~8 GB | 480p | 5s | Via ComfyUI + GGUF | Best entry point. Consumer GPU friendly. Apache 2.0 license. |
| **LTX-2** | 19B | 8-12 GB (distilled) | Up to 4K | 10s+ | ComfyUI native | Audio-conditioned multimodal video generation — accepts audio input to condition visual output. Does NOT generate or modify music. Released Jan 2026. Camera-motion LoRAs available. |
| **Stable Video Diffusion XT** | N/A | ~6 GB (optimized) | 576x1024 | 2-4s (25 frames) | Yes, via ComfyUI | Image-to-video only. Older but proven stable on Mac. Verified working Dec 2025. |

### Tier 2: Requires NVIDIA GPU or Cloud

| Model | Params | Min VRAM | Resolution | Length | Notes |
|-------|--------|----------|------------|--------|-------|
| **HunyuanVideo 1.5** | 8.3B | 13.6 GB (720p) | Up to 1080p | 10s | Tencent open source. Step-distilled RTX 4090 in 75 sec. Apache 2.0. |
| **Wan 2.1/2.2 14B** | 14B | 24+ GB | 720p | 5-10s | Full quality. Text-to-video + image-to-video + video editing + video-to-audio. |
| **SkyReels V1** | 13B+ | 24+ GB | 544x960 | 12s | HunyuanVideo fine-tune on 10M film clips. 33 expressions, 400+ movements. |

### Tier 3: Specialized

| Model | Use Case | Notes |
|-------|----------|-------|
| **Wan2.2-S2V** | Audio-driven video (lip sync, singing, dialogue) | Native ComfyUI. Music videos from audio + reference image. |
| **Deforum** | Audio-reactive visual generation | Latent space interpolation synced to music. Abstract/psychedelic. |
| **stable-diffusion-videos** | Music-synced image morphing | Python library. Beat-aware interpolation. Free. |

### Tier 4: Character Animation (For Weeter & Blubby)

| Tool | Type | Cost | Best For | Notes |
|------|------|------|----------|-------|
| **ToonCrafter** | Open source AI | Free (needs GPU) | Interpolating between two cartoon keyframes | 512x320, ~2 sec clips. ComfyUI integration. ~24GB VRAM (cloud ~$1-2/hr). |
| **Kling 3.0 Omni** | Commercial AI | 66 credits/day free | Image-to-video for mascots, native audio + lip-sync + multi-shot (6 cuts) | Launched Feb 4, 2026. |
| **Kling 2.6 Motion Control** | Commercial AI | Free tier | Transfer dance/gesture/reaction from reference video onto character image | Mascot animation is documented use case. |
| **Cartoon Animator (Reallusion)** | Traditional software | ~$149 one-time | Full rigging, lip-sync, webcam mocap, unlimited animation | Best for long-form 10-30 min content. |
| **Sprite Animation (Python)** | Code-based | Free | Breathing, bouncing, entrance/exit on still PNGs | MoviePy + sine wave + beat-sync. Zero GPU. |

### Key Insight: Mac Feasibility
- **Wan2mac** fork exists for Apple Silicon
- ComfyUI on Mac uses GGUF format (lower quality but runs locally)
- Realistic: 480p, 5-second clips on Mac. Volume production → cloud GPUs.

---

## 2. COMMERCIAL AI VIDEO — FREE TIERS (as of Feb 2026)

| Tool | Free Tier | Quality | Best For | Limitations |
|------|-----------|---------|----------|-------------|
| **Kling 3.0 Omni** | 30 credits new users | Up to 1080p | Unified text/image/video with native audio + lip-sync + multi-shot | Launched Feb 4, 2026. |
| **Kling 2.6** | 66 credits/day (resets) = 1-6 videos/day | 720p watermarked | Motion Control for mascot animation. Up to 3 min with Extend. | Slow (5-30 min). Degrades after 30s. |
| **Luma AI** | 500 credits/month | Draft resolution | Cinematic quality, best parallax/depth | Low priority queue. |
| **Pika 2.5** | Limited free credits | Good for social | Pikaswaps, Pikaffects, fast 42s renders | Credits exhaust fast. |
| **Runway Gen-4** | Limited trial | 720p watermarked | Best character consistency | No real free tier. Standard $12/mo. |

### Critical Reality Check
> **One 8-second render uses 15-35% of monthly free credits.** For 200+ artists, free tiers supplement — they don't power — the pipeline. Exception: Kling's daily reset makes it viable for building an animated character clip library over weeks.

---

## 3. VIDEO EDITING APIs (Developer-Centric)

| API | Free Tier | Pricing | Key Strength |
|-----|-----------|---------|--------------|
| **Shotstack** | Free sandbox, full API, unlimited testing | From $49/mo (200 min @ 720p) | JSON timeline editing, batch render, webhooks |
| **Creatomate** | Free trial | From $41/mo ($0.28/min) | Lowest per-minute cost. Renders <15 sec. |
| **Rendi** | Free tier | Pay per use | Raw FFmpeg via cloud API |

---

## 4. FREE LOCAL TOOLS (The Production Backbone)

### FFmpeg

- **Cost:** Free, open source. Install: `brew install ffmpeg`

### CRITICAL — The 1080p-to-Vertical Resolution Strategy

When your master is 1080p (1920x1080) and you need 9:16 (1080x1920) output, **simple center-cropping gives you a 607px-wide slice** — which looks terrible when platforms stretch it to fill a phone screen. **Do NOT upscale 607px to 1080px** — that creates visible blur.

**Three strategies, in order of preference:**

| Strategy | When to Use | Output | Quality |
|----------|-------------|--------|---------|
| **Blur-Fill** | 1080p source (standard) | 1080x1920 | **Best for 1080p** — sharp video centered with stylized blurred background |
| **Stacked Layout** | 1080p source + branding emphasis | 1080x1920 | **Pro look** — title bar (20%) + video (60%) + W&B/CTA bar (20%) |
| **Center Crop** | 4K source only | 1080x1920 | **Best overall** — clean 1215px crop scales perfectly |

**Strategy 1: Blur-Fill (RECOMMENDED DEFAULT for 1080p sources)**

The 16:9 video is scaled to fit the width of 1080px (resulting in 1080x607), centered vertically in a 1080x1920 frame, with a heavily blurred + darkened copy of the video filling the background. This is what professional creators use on YouTube Shorts and TikTok.

```bash
# Blur-Fill: 1080p master → sharp 1080x1920 vertical
ffmpeg -i master.mp4 \
  -filter_complex "
    [0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=20:5[bg];
    [0:v]scale=1080:-2:force_original_aspect_ratio=decrease[fg];
    [bg][fg]overlay=(W-w)/2:(H-h)/2
  " \
  -c:v libx264 -crf 18 -preset medium -c:a aac -t 59 short_blurfill.mp4
```

**Strategy 2: Stacked Layout (for branded content)**
```
┌─────────────────────┐
│   ARTIST NAME       │  ← Top 20%: Branding bar (artist colors)
│   Song Title        │
├─────────────────────┤
│                     │
│   16:9 VIDEO        │  ← Middle 60%: The actual video content
│   (scaled to fit)   │
│                     │
├─────────────────────┤
│   🐻 W&B + CTA     │  ← Bottom 20%: Characters + "Listen Now"
└─────────────────────┘
```
Build in MoviePy by compositing three layers onto a 1080x1920 canvas.

**Strategy 3: Center Crop (4K sources ONLY)**
```bash
# 4K master → clean crop to 1080x1920
ffmpeg -i master_4k.mp4 -vf "crop=1215:2160:(iw-1215)/2:0,scale=1080:1920" \
  -c:v libx264 -crf 18 -c:a aac -t 59 short_crop.mp4
```

**Decision Logic in `batch_produce.py`:**
```python
def get_vertical_strategy(master_width, master_height):
    """Choose the best 9:16 strategy based on source resolution."""
    if master_width >= 3840:
        return "center_crop"      # 4K → clean crop + scale
    else:
        return "blur_fill"        # 1080p → blur-fill (default)
    # Stacked layout is an artist_profile.json option:
    # "vertical_style": "stacked" overrides blur_fill

def build_vertical_command(master_path, output_path, strategy, duration=59):
    if strategy == "center_crop":
        vf = "crop=1215:2160:(iw-1215)/2:0,scale=1080:1920"
        return f'ffmpeg -i {master_path} -vf "{vf}" -c:v libx264 -crf 18 -c:a aac -t {duration} {output_path}'
    elif strategy == "blur_fill":
        fc = (
            "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=20:5[bg];"
            "[0:v]scale=1080:-2:force_original_aspect_ratio=decrease[fg];"
            "[bg][fg]overlay=(W-w)/2:(H-h)/2"
        )
        return f'ffmpeg -i {master_path} -filter_complex "{fc}" -c:v libx264 -crf 18 -c:a aac -t {duration} {output_path}'
    # stacked_layout handled by MoviePy compositing (see batch_produce.py)
```

**Standard Horizontal FFmpeg Commands (no change needed):**
```bash
# Full Music Video — the 16:9 master (no crop)
# Already 1920x1080, just copy or re-encode

# Instagram Reel (4:5) — blur-fill also works here
ffmpeg -i master.mp4 \
  -filter_complex "
    [0:v]scale=1080:1350:force_original_aspect_ratio=increase,crop=1080:1350,boxblur=20:5[bg];
    [0:v]scale=1080:-2:force_original_aspect_ratio=decrease[fg];
    [bg][fg]overlay=(W-w)/2:(H-h)/2
  " \
  -c:v libx264 -crf 18 -c:a aac -t 90 reel_4x5.mp4
```

### Python Libraries

| Library | Purpose | Install |
|---------|---------|---------|
| **librosa** | BPM, beat tracking, onset detection, key estimation, energy | `pip install librosa` |
| **MoviePy** | Video assembly, compositing, character overlay animation, stacked layouts | `pip install moviepy` |
| **Pillow/PIL** | Thumbnails, lyric cards, Meme Sign text rendering | `pip install Pillow` |
| **rembg** | AI background removal from character sheets | `pip install rembg` |
| **OpenCV** | Auto-slice character pose sheets into individual images | `pip install opencv-python` |
| **pydub** | Audio segment extraction, format conversion | `pip install pydub` |
| **Manim** | Kinetic typography for lyric videos | `pip install manim` |

### librosa Code Pattern (with Confidence Scoring)
```python
import librosa
import numpy as np

def analyze_song(audio_path):
    y, sr = librosa.load(audio_path)
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)
    onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
    onset_times = librosa.frames_to_time(onset_frames, sr=sr)
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    key_strengths = chroma.mean(axis=1)
    estimated_key = int(key_strengths.argmax())
    rms = librosa.feature.rms(y=y)[0].mean()

    # KEY CONFIDENCE SCORING
    sorted_strengths = np.sort(key_strengths)[::-1]
    key_confidence = float((sorted_strengths[0] - sorted_strengths[1]) / sorted_strengths[0])

    # MAJOR/MINOR ESTIMATION
    major_third = key_strengths[(estimated_key + 4) % 12]
    minor_third = key_strengths[(estimated_key + 3) % 12]
    is_major = bool(major_third > minor_third)
    mode_confidence = float(abs(major_third - minor_third) / max(major_third, minor_third))

    return {
        "bpm": float(tempo),
        "beat_times": beat_times.tolist(),
        "onset_times": onset_times.tolist(),
        "estimated_key": estimated_key,
        "is_major_key": is_major,
        "key_confidence": key_confidence,
        "mode_confidence": mode_confidence,
        "energy_level": float(rms),
        "duration": float(librosa.get_duration(y=y, sr=sr)),
        "analysis_reliable": key_confidence > 0.15 and mode_confidence > 0.10
    }
```
> **SAFETY VALVE:** If `analysis_reliable` is `false`, the mood mapper MUST fall back to genre defaults. Never assign character poses based on unreliable key/mode detection. BPM and beat timestamps remain reliable regardless.

---

## 5. ComfyUI — LOCAL WORKFLOW ENGINE

- Native Wan 2.1/2.2, LTX-2, ToonCrafter support
- Wan2.2-S2V workflow: audio-driven video from reference image
- Mac compatible with GGUF models and MPS backend
- Install via ComfyUI Desktop app (comfy.org), requires 16GB+ RAM, Apple M1+

---

## 6. CANVA & FIGMA INTEGRATION

- **Canva (MCP):** Template thumbnails, Brand Kit, Bulk Create from CSV, video editing (unlimited)
- **Figma (MCP):** Genre visual identity design system, component library, batch asset export

---

## 7. ARTIST PROFILE SYSTEM

### artist_profile.json — Per-Artist Visual Identity

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
    "comfyui_workflow": "workflows/edm_glitch_neon.json",
    "sd_prompt_prefix": "cyberpunk neon club, glitch art, dark background, electric cyan and magenta"
  },
  "vertical_style": "blur_fill",
  "weeter_blubby_default": "end_card_meme_sign",
  "weeter_blubby_frequency": "every_video",
  "created": "2026-02-08",
  "auto_generated": true,
  "human_reviewed": false
}
```

- New field: `"vertical_style"` — options: `"blur_fill"` (default), `"stacked"`, `"center_crop"` (4K only)
- `analyze_catalog.py` checks for this file. If present, visual traits override genre defaults.
- If missing, auto-generate a starter from genre defaults, flag `"human_reviewed": false`.

---

## 8. WEETER & BLUBBY CHARACTER SYSTEM

### 8a. Character Dynamics (Personality Rules)

```json
{
  "_character_dynamics": {
    "weeter": {
      "role": "The Leader / Hype Man",
      "species": "Brown Bear",
      "traits": "confident, loud, protective, initiates action, bigger presence",
      "pose_bias": "megaphone, rocket, money_bag, flexing, pointing, sunglasses",
      "note": "Weeter LEADS. He is the initiator, the announcer, the one taking action."
    },
    "blubby": {
      "role": "The Reactor / Sidekick",
      "species": "Yellow-Green Alien",
      "traits": "curious, emotional, surprised, follows Weeter's lead, smaller presence",
      "pose_bias": "mind_blown, magnifying_glass, scared, stars, thinking, peeking",
      "note": "Blubby REACTS. He responds to what Weeter does or what the music does."
    },
    "together": {
      "dynamic": "Classic big guy / little guy comedy duo. Weeter leads (typically left, larger), Blubby reacts (right, smaller).",
      "note": "NEVER assign Blubby a leadership pose (megaphone, pointing) or Weeter a pure reaction pose (mind_blown, scared) unless the Creative Brief explicitly overrides."
    },
    "_phase2_character_development": {
      "note": "Create an 'Empathetic/Sad' Blubby pose (comforting hug, gentle pat, teary-eyed solidarity) to complement Weeter's crying pose for melancholy songs. The current Blubby 'scared' pose feels too anxious for songs that are sad but hopeful."
    }
  }
}
```

### 8b. The Asset Factory

**Problem:** Raw character sheets are multi-pose JPGs on white backgrounds. Unusable for compositing.

**Solution: `prep_characters.py`**

```python
#!/usr/bin/env python3
"""
Asset Factory: Transform flat character sheets into transparent PNG library.
Uses rembg for background removal and OpenCV for pose auto-slicing.
Run ONCE during setup, then only when new sheets are added.

Directory expectations:
  Input:  data/raw_sheets/
          Files named like: Weeter-happy.jpg, Blubby-cool.png,
          Together-hype.jpg, Weeter-poses_2.jpg
  Output: assets/characters/{character}/{emotion}/

Supports slice_overrides.json for manual bounding box corrections.
"""

import cv2
import os
import json
import numpy as np
from rembg import remove

MIN_POSE_WIDTH = 100
MIN_POSE_HEIGHT = 100
PADDING = 10

def load_slice_overrides(overrides_path):
    if os.path.exists(overrides_path):
        with open(overrides_path, 'r') as f:
            return json.load(f)
    return {}

def parse_filename(filename):
    base = os.path.splitext(filename)[0].lower()
    parts = base.split("-")
    if "together" in parts[0]:
        char_name = "together"
    elif "blubby" in parts[0]:
        char_name = "blubby"
    elif "weeter" in parts[0]:
        char_name = "weeter"
    else:
        char_name = "unknown"
    if len(parts) > 1:
        emotion_raw = parts[1].split("_")[0]
        emotion_map = {
            "happy": "happy", "hype": "hype", "cool": "cool",
            "sad": "sad", "angry": "angry", "smart": "smart",
            "love": "love", "neutral": "neutral", "fun": "fun",
            "poses": "neutral", "meme": "meme_sign", "sign": "meme_sign",
        }
        emotion = emotion_map.get(emotion_raw, "neutral")
    else:
        emotion = "neutral"
    return char_name, emotion

def strip_background(image_path):
    with open(image_path, 'rb') as f:
        input_data = f.read()
    output_data = remove(input_data)
    nparr = np.frombuffer(output_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
    return img

def auto_slice_poses(img):
    if img.shape[2] < 4:
        print("  WARNING: No alpha channel after background removal.")
        return []
    alpha = img[:, :, 3]
    contours, _ = cv2.findContours(alpha, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    pose_rects = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w >= MIN_POSE_WIDTH and h >= MIN_POSE_HEIGHT:
            pose_rects.append((x, y, w, h))
    pose_rects.sort(key=lambda r: (r[1] // 200, r[0]))
    sorted_poses = []
    for (x, y, w, h) in pose_rects:
        x1, y1 = max(0, x - PADDING), max(0, y - PADDING)
        x2, y2 = min(img.shape[1], x + w + PADDING), min(img.shape[0], y + h + PADDING)
        sorted_poses.append(img[y1:y2, x1:x2])
    return sorted_poses

def apply_overrides(filename, img, overrides):
    if filename not in overrides:
        return None
    manual_poses = []
    for box in overrides[filename]:
        x, y, w, h = box["x"], box["y"], box["w"], box["h"]
        name = box.get("name", f"override_{len(manual_poses)}")
        pose = img[y:y+h, x:x+w]
        manual_poses.append((name, pose))
    return manual_poses

def prep_characters(input_folder, output_base, overrides_path=None):
    overrides = load_slice_overrides(overrides_path or
                                      os.path.join(input_folder, "slice_overrides.json"))
    os.makedirs(output_base, exist_ok=True)
    for filename in sorted(os.listdir(input_folder)):
        if not filename.lower().endswith((".jpg", ".jpeg", ".png")):
            continue
        print(f"\nProcessing: {filename}")
        char_name, emotion = parse_filename(filename)
        print(f"  Character: {char_name}, Emotion: {emotion}")
        input_path = os.path.join(input_folder, filename)
        img = strip_background(input_path)
        print(f"  Background removed. Shape: {img.shape}")
        manual = apply_overrides(filename, img, overrides)
        if manual:
            print(f"  Using {len(manual)} manual overrides")
            for name, pose in manual:
                save_dir = os.path.join(output_base, char_name, emotion)
                os.makedirs(save_dir, exist_ok=True)
                save_path = os.path.join(save_dir, f"{name}.png")
                cv2.imwrite(save_path, pose)
                print(f"  Saved: {save_path}")
        else:
            poses = auto_slice_poses(img)
            print(f"  Auto-detected {len(poses)} poses")
            if len(poses) == 0:
                save_dir = os.path.join(output_base, char_name, emotion)
                os.makedirs(save_dir, exist_ok=True)
                save_path = os.path.join(save_dir, f"{char_name}_0.png")
                cv2.imwrite(save_path, img)
                print(f"  Saved (full sheet): {save_path}")
            else:
                for idx, pose in enumerate(poses):
                    save_dir = os.path.join(output_base, char_name, emotion)
                    os.makedirs(save_dir, exist_ok=True)
                    save_path = os.path.join(save_dir, f"{char_name}_{idx}.png")
                    cv2.imwrite(save_path, pose)
                    print(f"  Saved: {save_path}")
    print(f"\nAsset Factory complete. Output: {output_base}")
    print("NEXT: Rename auto-numbered files to descriptive names")
    print("(e.g., weeter_0.png → thumbs_up.png)")

if __name__ == "__main__":
    prep_characters(
        input_folder="data/raw_sheets",
        output_base="assets/characters",
        overrides_path="data/raw_sheets/slice_overrides.json"
    )
```

**slice_overrides.json example:**
```json
{
  "Together-meme_sign.jpg": [
    {"x": 50, "y": 30, "w": 800, "h": 900, "name": "blank_sign"}
  ],
  "Weeter-poses_2.jpg": [
    {"x": 10, "y": 10, "w": 300, "h": 400, "name": "rocket_ship"},
    {"x": 320, "y": 10, "w": 280, "h": 400, "name": "megaphone"}
  ]
}
```

**Output structure:**
```
assets/characters/
├── weeter/
│   ├── happy/       (thumbs_up.png, laughing.png, celebrating.png)
│   ├── hype/        (rocket_ship.png, megaphone.png, money_bag.png)
│   ├── cool/        (sunglasses.png, arms_crossed_cool.png)
│   ├── sad/         (crying.png, worried.png)
│   ├── angry/       (fists_clenched.png, steam.png)
│   ├── smart/       (monocle.png, reading.png, pointing.png)
│   ├── love/        (heart_eyes.png, lying_down_heart.png)
│   └── neutral/     (waving.png, bowl.png, thinking.png)
├── blubby/
│   ├── happy/       (excited_stars.png, thumbs_up.png)
│   ├── hype/        (mind_blown.png)
│   ├── cool/        (sunglasses.png)
│   ├── sad/         (scared.png)
│   ├── smart/       (magnifying_glass.png, reading.png)
│   └── neutral/     (thinking.png, curious.png)
├── together/
│   ├── happy/       (thumbs_up_duo.png, celebrating.png, selfie.png)
│   ├── hype/        (rocket_duo.png, money_rain.png)
│   ├── cool/        (sunglasses_duo.png, flexing.png)
│   ├── sad/         (hugging_scared.png, both_worried.png)
│   ├── smart/       (detective_duo.png, both_thinking.png, reading_duo.png)
│   ├── fun/         (popcorn.png, megaphone_scared.png)
│   └── meme_sign/   (blank_sign.png)  ← THE KEY ASSET
├── animated/        ← ToonCrafter/Kling clips (built over time)
└── slice_overrides.json
```

### 8c. Automated Mood Mapping

See separate file: `mood_map.json` (delivered alongside this audit).

All paths are **project-root-relative** (e.g., `assets/characters/weeter/hype/rocket_ship.png`). The manifest generated by `analyze_catalog.py` must write these project-root-relative paths so `batch_produce.py` never guesses directory locations.

**Priority chain:** Creative Brief → artist_profile.json → Mood Map (if analysis reliable) → Genre defaults → Default happy pose

**SAFETY VALVE:** If `analysis_reliable` is `false` (key_confidence < 0.15 or mode_confidence < 0.10), skip mood mapping, use genre default poses. Log reason.

### 8d. Character Animation (The "Alive" Layer)

**Level 1: Sprite Animation (Every Video — Free, Automated)**
```python
import numpy as np
def breathing_scale(t):
    return 1.0 + 0.02 * np.sin(2 * np.pi * t / 2.0)  # 2-sec cycle, ±2%
```
- **Breathing:** Sine wave scale (98% → 102%) over 2-second cycle
- **Beat Bounce:** Y-axis offset 5-10px on kick drum timestamps from librosa
- **Entrance:** Bounce-in from bottom, ease-out curve (0.5 sec)
- **Exit:** Fade out over 0.3 sec

**Level 2: AI-Animated Clips (Build Over Time)**
- ToonCrafter, Kling 2.6 Motion Control, Kling 3.0 Omni
- Store in `assets/characters/animated/`

**Level 3: Full Animation (Cartoon Animator — Phase 3+)**
- ~$149 one-time. Rig once, animate forever.

### 8e. The Meme Sign Generator

Template: `assets/characters/together/meme_sign/blank_sign.png`

```python
from PIL import Image, ImageDraw, ImageFont

def generate_meme_sign(song_title, artist_name, sign_template_path, output_path):
    sign = Image.open(sign_template_path)
    draw = ImageDraw.Draw(sign)
    font_title = ImageFont.truetype("fonts/bold.ttf", 48)
    font_artist = ImageFont.truetype("fonts/regular.ttf", 36)
    cx, cy = sign.width // 2, sign.height // 2
    draw.text((cx, cy - 30), song_title, font=font_title, anchor="mm", fill="black")
    draw.text((cx, cy + 30), f"by {artist_name}", font=font_artist, anchor="mm", fill="#333333")
    sign.save(output_path)
```

### 8f. Integration Tiers

| Tier | Where | What | Cost | Automation |
|------|-------|------|------|------------|
| **Every video** (1,400+) | End card | Meme Sign + sprite breathing/bounce | Free | 100% automated |
| **Selected videos** | Beat drop / chorus | Pre-animated reaction clip from library | ~$1-2/clip one-time | 95% automated |
| **Hero releases** | Featured throughout | Full Kling 3.0 or Cartoon Animator sequences | $0-149 | 50% automated |
| **Future long-form** | Dedicated content | 10-30 min animated episodes | $149 one-time | Manual + rigged |

---

## 9. PRODUCTION RULES

### 9a. The Social UI Safe Zone (Both Axes)

**CRITICAL:** Overlays must avoid BOTH the horizontal crop zones AND the platform UI elements.

**For the 16:9 Master (horizontal Safe Zone — survives center crop):**
```
┌──────────────────────────────────────────────────┐
│ DANGER │         SAFE ZONE (56%)        │ DANGER │
│  (22%) │   x: 424px to 1496px           │  (22%) │
│  CUT   │   (at 1920px master width)     │  CUT   │
└──────────────────────────────────────────────────┘
```

**For 9:16 Vertical Outputs (Social UI Safe Zone):**
Platform UIs (TikTok, Reels, Shorts) cover significant portions of the vertical frame:
```
┌─────────────────────┐
│   ⚠ TOP 10%         │  ← "Following" / "For You" tabs
│                     │
│   ✅ SAFE ZONE      │  ← Characters and text go HERE
│   (10%-65% from top)│     Center-aligned, upper portion
│                     │
│   ⚠ RIGHT 15%      │  ← Like / Comment / Share buttons
│                     │
│   ⚠ BOTTOM 25%     │  ← Caption text, music info, username
└─────────────────────┘
```

**The Vertical Content Safe Zone** for overlays on 9:16 output:
- Y-axis: Between 10% and 65% from the top (pixels 192-1248 at 1920px height)
- X-axis: Between 10% and 85% from the left (pixels 108-918 at 1080px width)
- **Weeter & Blubby and the Meme Sign must be positioned within this zone on vertical formats**

**Safe Zone Auto-Snap Implementation:**
```python
def enforce_safe_zone(overlay_x, overlay_y, overlay_w, overlay_h,
                      frame_width, frame_height, format_type="master"):
    """
    Auto-snap overlay into appropriate safe zone.
    Returns corrected (x, y) position.
    """
    if format_type == "master":
        # Horizontal: only worry about left/right crop
        safe_left = int(frame_width * 0.22)   # 424 at 1920
        safe_right = int(frame_width * 0.78)  # 1496 at 1920
        if overlay_x < safe_left:
            overlay_x = safe_left
        if overlay_x + overlay_w > safe_right:
            overlay_x = safe_right - overlay_w
        if overlay_w > (safe_right - safe_left):
            overlay_x = (frame_width - overlay_w) // 2

    elif format_type in ("short", "tiktok", "reel"):
        # Vertical: avoid platform UI on all sides
        safe_left = int(frame_width * 0.10)    # 108 at 1080
        safe_right = int(frame_width * 0.85)   # 918 at 1080
        safe_top = int(frame_height * 0.10)    # 192 at 1920
        safe_bottom = int(frame_height * 0.65) # 1248 at 1920

        if overlay_x < safe_left:
            overlay_x = safe_left
        if overlay_x + overlay_w > safe_right:
            overlay_x = safe_right - overlay_w
        if overlay_y < safe_top:
            overlay_y = safe_top
        if overlay_y + overlay_h > safe_bottom:
            overlay_y = safe_bottom - overlay_h

        # Center horizontally if wider than safe zone
        if overlay_w > (safe_right - safe_left):
            overlay_x = (frame_width - overlay_w) // 2

    return overlay_x, overlay_y
```

**Contract:** Every overlay script MUST call `enforce_safe_zone()` with the correct `format_type` before compositing. Master format uses horizontal-only rules. Vertical formats use full social UI safe zone. No exceptions.

### 9b. Idempotency / Hash-Based Render Signatures

```python
import hashlib
import json
import os

def compute_render_signature(song_audio_path, artist_profile_path, manifest_entry):
    hasher = hashlib.sha256()
    with open(song_audio_path, 'rb') as f:
        hasher.update(f.read())
    if os.path.exists(artist_profile_path):
        with open(artist_profile_path, 'rb') as f:
            hasher.update(f.read())
    hasher.update(json.dumps(manifest_entry, sort_keys=True).encode())
    return hasher.hexdigest()[:16]

def should_render(song_audio_path, artist_profile_path, manifest_entry, output_dir):
    sig_path = os.path.join(output_dir, "render_signature.txt")
    current_sig = compute_render_signature(song_audio_path, artist_profile_path, manifest_entry)
    if not os.path.exists(sig_path):
        return True
    with open(sig_path, 'r') as f:
        stored_sig = f.read().strip()
    if current_sig != stored_sig:
        return True
    expected = ["full_video.mp4", "short_916.mp4", "tiktok.mp4",
                "reel_4x5.mp4", "lyric_video.mp4", "visualizer.mp4", "sync_reel.mp4"]
    for fname in expected:
        if not os.path.exists(os.path.join(output_dir, fname)):
            return True
    return False

def save_render_signature(song_audio_path, artist_profile_path, manifest_entry, output_dir):
    sig = compute_render_signature(song_audio_path, artist_profile_path, manifest_entry)
    with open(os.path.join(output_dir, "render_signature.txt"), 'w') as f:
        f.write(sig)
```

**Support `--force` flag to override.**

### 9c. Librosa Confidence Safety Valve

If `analysis_reliable` is `false` (key_confidence < 0.15 or mode_confidence < 0.10):
- Skip mood mapping → use genre defaults
- Log: "low confidence analysis — using genre defaults"
- BPM and beat timestamps remain reliable

### 9d. Project-Root-Relative Paths in Manifests

**HARD RULE:** All asset paths — in `mood_map.json`, manifests, and configs — must be **project-root-relative** (e.g., `assets/characters/weeter/hype/rocket_ship.png`). Never use machine-specific absolute paths (e.g., `/Users/john/Ridgemont/assets/...`) which break when moving between machines. Never use ambiguous fragments (e.g., `hype/rocket_ship.png`) that require guessing the parent directory.

`analyze_catalog.py` writes these root-relative paths to the manifest. `batch_produce.py` reads them as-is — no concatenation, no guessing.

```json
{
  "weeter_pose": "assets/characters/weeter/hype/rocket_ship.png",
  "blubby_pose": "assets/characters/blubby/hype/mind_blown.png",
  "together_pose": "assets/characters/together/hype/rocket_duo.png",
  "meme_sign_template": "assets/characters/together/meme_sign/blank_sign.png"
}
```

If `batch_produce.py` ever constructs a path by string concatenation, that is a BUG.

### 9e. Preflight Validation (Step 1.5)

**CRITICAL:** Before any rendering begins, `analyze_catalog.py` must verify that every asset path in the manifest actually exists on disk. A single renamed or missing PNG will crash the batch hours into processing.

```python
def preflight_validate(manifest):
    """
    Step 1.5: Verify all referenced assets exist before rendering.
    Call AFTER mood mapping, BEFORE passing manifest to batch_produce.py.
    Returns list of missing paths. Empty list = all clear.
    """
    paths_to_check = [
        manifest.get("weeter_pose"),
        manifest.get("blubby_pose"),
        manifest.get("together_pose"),
        manifest.get("meme_sign_template"),
        manifest.get("audio_source"),
        manifest.get("background_image"),
    ]
    missing = [p for p in paths_to_check if p and not os.path.exists(p)]
    return missing

# In analyze_catalog.py, after building the manifest:
missing = preflight_validate(manifest)
if missing:
    manifest["status"] = "ABORTED_PREFLIGHT"
    manifest["missing_assets"] = missing
    log.error(f"PREFLIGHT FAIL: {song_title} — missing: {missing}")
else:
    manifest["status"] = "READY_FOR_ASSEMBLY"
```

**Rules:**
- If ANY path is missing → abort that song, log the missing files, continue to next song
- Never let a missing-asset song enter the FFmpeg queue
- The progress log must show "PREFLIGHT_FAIL" distinct from "RENDER_FAIL"
- Run preflight on the ENTIRE batch first before rendering anything (fail-fast)

---

## 10. BASELINE MASTER RECIPE (Phase 1 — Immediate Value)

**The Phase 1 Master Video (Ken Burns + Beat Pulse + W&B):**
1. **Background:** 16:9 Ken Burns pan on album art or genre-matched landscape
2. **Energy:** Beat-synced brightness pulse via FFmpeg `eq` filter
3. **Characters:** W&B breathing/bounce at intro (3 sec) + Meme Sign end card (5 sec). Within horizontal Safe Zone.
4. **Branding:** Artist name + song title within Safe Zone. Artist profile colors.
5. **Audio:** Full track.

**From Master → 7 Formats:**
- Full Video: the master itself
- Short/TikTok/Reel: blur-fill strategy (1080p) or center-crop (4K). W&B repositioned to vertical Social UI Safe Zone.
- Lyric Video: text overlay within Safe Zone
- Visualizer: audio-reactive, no character overlay needed
- Sync Reel: highlight segment, no lyrics

**Result:** Professional, branded video for every song on Day 1.

---

## 11. RECOMMENDED ARCHITECTURE

### The Canonical 6-Step Pipeline:

| Step | Name | Primary Action |
|------|------|----------------|
| **0** | **Asset Prep** | Run `prep_characters.py`. One-time setup. |
| **1** | **Ingestion** | Pull WAV/MP3 + metadata from Make-Music. |
| **1.5** | **Preflight** | Verify all asset paths exist on disk. Abort songs with missing assets before rendering. |
| **2** | **Analysis** | `analyze_catalog.py`: BPM, mood, confidence, W&B pose selection. Write project-root-relative paths to manifest. |
| **3** | **Creation** | Baseline Recipe (Phase 1) or ComfyUI (Phase 2+). All overlays within horizontal Safe Zone. |
| **4** | **Assembly** | `batch_produce.py`: 7 formats. Blur-fill for 1080p vertical. Hash idempotency. Vertical Social UI Safe Zone for character overlays. |
| **5** | **Cataloging** | Save to `/catalog/{artist}/{song}/`. Update progress log + render_signature.txt. |

### Cost Estimate
- **Phase 1:** $0 — all local, free tools
- **Phase 2+:** $0-50/month cloud GPU
- **Character library:** ~$30-50 one-time (50 ToonCrafter clips)
- **Cartoon Animator (Phase 3):** $149 one-time

---

## 12. WHAT WON'T WORK

| Approach | Why It Fails |
|----------|-------------|
| Relying solely on AI video free tiers | 1 video = 15-35% of monthly credits. |
| Running HunyuanVideo 13B on MacBook | Needs 60-80GB VRAM. |
| Manual video editing per song | 1,400+ videos not humanly feasible. |
| Static character PNGs pasted into video | Looks amateur. Breathing animation mandatory. |
| Ignoring artist visual consistency | Without artist_profile.json, catalog looks random. |
| Upscaling 607px crop to 1080px | Visible blur. Use blur-fill or stacked layout. |
| Trusting librosa key detection blindly | Confidence scoring prevents wrong mood mapping. |
| File-exists-only idempotency | Misses config changes. Use hash signatures. |
| Relative path fragments in mood_map or manifest | Path mismatch crashes batch. Use project-root-relative paths. |
| Skipping preflight validation | Missing/renamed PNG crashes batch hours in. Validate all paths before rendering. |
| Assigning Blubby leadership poses | Breaks character dynamics. Weeter leads, Blubby reacts. |
| Placing overlays in bottom 25% of vertical | TikTok/Reels UI covers it. Use Social UI Safe Zone. |
| Centering text at edges of 16:9 master | Gets cut in 9:16 crop. Horizontal Safe Zone (center 56%). |

---

*Re-verify quarterly. Free tiers shift frequently.*
*Last verified: February 8, 2026*
