# Music Idea Capture & Analysis System

## Overview
A MacBook-based system to record, analyze, and auto-categorize musical ideas (riffs, chord progressions, vocals, melodies).

---

## Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐     ┌──────────────┐
│   CAPTURE   │ ──▶ │     ANALYZE      │ ──▶ │   CATEGORIZE    │ ──▶ │    STORE     │
│  (Record)   │     │  (Detect/Trans)  │     │  (Tag/Classify) │     │  (Database)  │
└─────────────┘     └──────────────────┘     └─────────────────┘     └──────────────┘
```

---

## 1. CAPTURE LAYER

### Hardware
- **Built-in Mac mic** - Quick ideas
- **USB audio interface** (Focusrite Scarlett, etc.) - Guitar/instrument recording
- **MIDI controller** - Direct MIDI input

### Software Options
| Tool | Use Case | Notes |
|------|----------|-------|
| **QuickTime** | Fast voice memo | Built-in, no setup |
| **Audio Hijack** | System audio capture | Can record any app |
| **Logic Pro** | Full quality recording | Best for instruments |
| **SoundSource** | Quick mic access | Menu bar utility |

### Recommended: Keyboard Shortcut Recording
Set up a global hotkey (e.g., `Cmd+Shift+R`) to instantly start recording via Automator or BetterTouchTool.

---

## 2. ANALYSIS LAYER

### A. Chord Detection
| Tool | Type | Accuracy | Notes |
|------|------|----------|-------|
| **Chord ai** | App (iOS/Mac) | ~85% | Real-time, easy |
| **Moises** | App/Web | ~90% | Also does stem separation |
| **Chordify** | Web | ~80% | Free tier available |
| **librosa + ML** | Python | Variable | Full control, requires coding |

### B. Pitch/Melody Detection
| Tool | Type | Best For |
|------|------|----------|
| **Basic Pitch** (Spotify) | Python/CLI | Polyphonic audio → MIDI |
| **Melodyne** | Plugin | Surgical pitch editing |
| **CREPE** | Python | Monophonic pitch tracking |
| **Tony** (VAMP) | Desktop app | Melody annotation |

### C. Vocal Transcription (Lyrics)
| Tool | Type | Accuracy |
|------|------|----------|
| **Whisper** (OpenAI) | Python/CLI | 95%+ (best free option) |
| **MacWhisper** | Mac app | Whisper with GUI |
| **Descript** | App | Excellent, subscription |

### D. BPM/Key Detection
| Tool | Notes |
|------|-------|
| **librosa** | `librosa.beat.beat_track()`, `librosa.feature.chroma` |
| **Essentia** | Professional-grade analysis |
| **Moises** | All-in-one solution |

### E. Audio Fingerprinting / Similarity
| Tool | Use Case |
|------|----------|
| **Chromaprint** | Find similar recordings |
| **Dejavu** | Audio fingerprinting in Python |

---

## 3. CATEGORIZATION LAYER

### Auto-Generated Metadata
For each recording, extract:
```json
{
  "id": "uuid",
  "filename": "idea_2024-01-15_143022.wav",
  "created": "2024-01-15T14:30:22",
  "duration_sec": 45,
  "type": "vocal_melody",  // riff, chord_progression, vocal, beat
  "key": "G major",
  "bpm": 73,
  "chords": ["G", "D", "Am", "C"],
  "time_signature": "4/4",
  "lyrics": "I drink my coffee extra slow...",
  "midi_file": "idea_2024-01-15_143022.mid",
  "tags": ["ballad", "acoustic", "melancholy"],
  "energy": 0.3,  // 0-1 scale
  "mood": "reflective"
}
```

### Classification Logic
```
IF has_pitch_variation AND no_detected_chords:
    type = "vocal_melody" or "riff"
ELIF multiple_simultaneous_notes:
    type = "chord_progression"
ELIF has_lyrics_detected:
    type = "vocal_with_lyrics"
ELIF percussive_onset_ratio > 0.7:
    type = "beat/rhythm"
```

---

## 4. STORAGE LAYER

### Folder Structure
```
~/Music/Ideas/
├── 2024/
│   ├── 01-January/
│   │   ├── chord_progressions/
│   │   ├── melodies/
│   │   ├── vocals/
│   │   └── riffs/
│   └── 02-February/
├── by_key/
│   ├── C_major/
│   ├── G_major/
│   └── A_minor/
├── by_bpm/
│   ├── 60-80/
│   ├── 80-100/
│   └── 100-120/
└── database.json  (or SQLite)
```

### Database Options
| Option | Pros | Cons |
|--------|------|------|
| **JSON file** | Simple, portable | Slow for 1000+ entries |
| **SQLite** | Fast queries, single file | Requires SQL |
| **Notion** | Visual, tagging, mobile | Requires internet |
| **Airtable** | Spreadsheet-like, API | Free tier limits |

---

## 5. RECOMMENDED TOOL STACK

### For Maximum Depth of Analysis:

```
CAPTURE:        Logic Pro or Audio Hijack (high quality)
                    │
                    ▼
STEM SPLIT:     Demucs or Spleeter (isolate vocals/instruments)
                    │
                    ▼
ANALYSIS:       ┌───┴───┐
                │       │
            Vocals   Instruments
                │       │
                ▼       ▼
            Whisper  Basic Pitch
            (lyrics) (melody→MIDI)
                │       │
                ▼       ▼
            Chord ai / librosa
            (chord detection)
                │
                ▼
ORGANIZE:       Python script → SQLite + organized folders
                    │
                    ▼
BROWSE:         Custom web UI or Notion database
```

---

## 6. INSTALLATION COMMANDS

```bash
# Python environment
python3 -m venv ~/music-capture-env
source ~/music-capture-env/bin/activate

# Core analysis libraries
pip install librosa soundfile numpy scipy

# Spotify's Basic Pitch (audio → MIDI)
pip install basic-pitch

# OpenAI Whisper (vocal transcription)
pip install openai-whisper

# Stem separation
pip install demucs

# Audio fingerprinting
pip install chromaprint pyacoustid
```

### Mac Apps to Install
- **MacWhisper** - GUI for Whisper (App Store or macwhisper.com)
- **Chord ai** - Real-time chord detection (App Store)
- **Audio Hijack** - Record any audio source (rogueamoeba.com)
- **MIDI Guitar 2** - Guitar → MIDI (jamorigin.com)

---

## 7. AUTOMATION SCRIPT OUTLINE

```python
#!/usr/bin/env python3
"""
music_capture.py - Analyze and categorize musical recordings
"""

import os
import json
from datetime import datetime
from pathlib import Path

# Analysis imports
import librosa
from basic_pitch.inference import predict
import whisper

def analyze_recording(audio_path):
    """Full analysis pipeline for a recording"""

    # Load audio
    y, sr = librosa.load(audio_path)

    # Basic features
    duration = librosa.get_duration(y=y, sr=sr)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)

    # Key detection
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    # ... key detection logic

    # Melody extraction (Basic Pitch)
    midi_data, _, _ = predict(audio_path)

    # Vocal transcription (Whisper)
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    lyrics = result["text"]

    return {
        "duration": duration,
        "bpm": float(tempo),
        "key": detected_key,
        "lyrics": lyrics,
        "midi": midi_data
    }

def categorize(analysis):
    """Determine type and tags based on analysis"""
    # ... classification logic
    pass

def save_to_database(metadata, db_path):
    """Save metadata to JSON/SQLite"""
    pass

if __name__ == "__main__":
    import sys
    audio_file = sys.argv[1]
    result = analyze_recording(audio_file)
    print(json.dumps(result, indent=2))
```

---

## 8. QUICK START WORKFLOW

### Daily Use:
1. **Record** - Hit global hotkey, hum/play idea
2. **Drop** - Drag audio file to "Inbox" folder
3. **Auto-process** - Folder action triggers analysis script
4. **Review** - Open database/Notion to browse tagged ideas

### Weekly Review:
- Browse by key/tempo to find compatible ideas
- Combine related snippets into song drafts
- Archive or delete weak ideas

---

## 9. COST BREAKDOWN

| Tool | Cost | Required? |
|------|------|-----------|
| Basic Pitch | Free | Yes |
| Whisper | Free | Yes |
| Demucs | Free | Optional |
| librosa | Free | Yes |
| Chord ai | $5/mo | Recommended |
| MacWhisper | $30 one-time | Convenient |
| Audio Hijack | $72 one-time | Optional |
| Logic Pro | $200 one-time | You have it |

**Minimum cost: $0** (all Python tools are free)
**Recommended: ~$35** (MacWhisper + Chord ai trial)

---

## Next Steps

1. **Install Python tools** (commands above)
2. **Set up folder structure**
3. **Test with a sample recording**
4. **Build automation script**
5. **Create database schema**

Would you like me to build the automation script for you?
