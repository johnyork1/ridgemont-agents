# Ridgemont Jam Session
## Technical Specification v1.0

---

## Overview

A standalone Python application for macOS that captures guitar/vocal jam sessions, auto-slices recordings at user-triggered boundaries, analyzes each slice for musical metadata, and organizes everything into a searchable library.

---

## Target System

| Component | Spec |
|-----------|------|
| Machine | Apple M1 Max, 64GB RAM |
| OS | macOS 26.2 |
| Input | Built-in microphone |
| Controller | USB footswitch (to be acquired) |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        RIDGEMONT JAM SESSION                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │   CAPTURE   │───▶│    SLICE    │───▶│   ANALYZE   │───▶│    STORE    │  │
│  │             │    │             │    │             │    │             │  │
│  │ • Record    │    │ • Footswitch│    │ • Separate  │    │ • Organize  │  │
│  │ • Metronome │    │ • Silence   │    │ • Detect    │    │ • Index     │  │
│  │ • Monitor   │    │   fallback  │    │ • Transcribe│    │ • Export    │  │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘  │
│                                                                             │
│                              ┌─────────────┐                                │
│                              │   BROWSE    │                                │
│                              │             │                                │
│                              │ • Search    │                                │
│                              │ • Filter    │                                │
│                              │ • Preview   │                                │
│                              │ • Export    │                                │
│                              └─────────────┘                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Module 1: CAPTURE

### Purpose
Standalone Python recorder with metronome, replacing need for Logic Pro during capture.

### Features
- **Always-on listening** (armed but not recording until triggered)
- **Metronome** plays in headphones (not recorded)
- **Footswitch control:**
  - Press once → Start recording (visual indicator)
  - Press again → Stop recording, save slice, return to armed state
- **Level meter** showing input volume
- **Session metadata** captured at start (date, time, session ID)

### Technical Implementation
```python
# Core libraries
pyaudio          # Audio input/output
numpy            # Audio buffer processing
sounddevice      # Alternative audio I/O (lower latency)
pynput           # Keyboard/footswitch input detection

# Metronome
pygame           # or sounddevice for click generation
```

### Metronome Behavior
- User sets BPM before session (or taps tempo)
- Click plays through headphones only
- Visual beat indicator on screen
- Metronome BPM stored as "session_bpm" (reference, not enforced)

### Footswitch Mapping
- USB footswitch appears as keyboard input
- Map to a key (e.g., F13 or unused key)
- `pynput` listens for keypress events

### Fallback: Silence Detection
If no footswitch press for extended time AND silence detected > 3 seconds:
- Auto-save current buffer as slice
- Return to armed state
- Log: "Auto-sliced on silence (no footswitch detected)"

### Output
- WAV file per slice: `session_2024-02-08/raw/slice_001.wav`
- Session log: `session_2024-02-08/session.json`

---

## Module 2: SLICE

### Purpose
Process raw recordings into discrete, timestamped slices.

### Slice Triggers (Priority Order)
1. **Footswitch** - User presses to mark start/stop (PRIMARY)
2. **Silence detection** - Gap > 2.5 seconds (FALLBACK)

### Technical Implementation
```python
# For post-processing (if needed)
pydub            # split_on_silence, audio manipulation
librosa          # onset detection, beat alignment

# Silence detection parameters (configurable)
SILENCE_THRESHOLD_DB = -40
MIN_SILENCE_DURATION = 2.5  # seconds
```

### Slice Naming Convention
```
slice_001_HHMMSS.wav
slice_002_HHMMSS.wav
...
```

### Output
- Individual WAV files in `session_YYYY-MM-DD/raw/`
- Slice manifest: `slices.json` with timestamps, durations

---

## Module 3: ANALYZE

### Purpose
Extract musical metadata from each slice using ML models optimized for Apple Silicon.

### Analysis Pipeline (Per Slice)

```
┌─────────────┐
│  Raw WAV    │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│  STEP 1: Source Separation                  │
│  Tool: Demucs (or Spleeter)                 │
│  Output: vocals.wav, guitar.wav             │
└──────┬──────────────────────────┬───────────┘
       │                          │
       ▼                          ▼
┌─────────────────┐      ┌─────────────────┐
│  STEP 2a:       │      │  STEP 2b:       │
│  Vocal Analysis │      │  Guitar Analysis│
│                 │      │                 │
│  • Whisper      │      │  • librosa      │
│    (lyrics)     │      │    (key, BPM)   │
│  • Basic Pitch  │      │  • Chordino     │
│    (melody MIDI)│      │    (chords)     │
│  • CREPE        │      │  • Basic Pitch  │
│    (pitch curve)│      │    (MIDI)       │
└────────┬────────┘      └────────┬────────┘
         │                        │
         └───────────┬────────────┘
                     ▼
          ┌─────────────────────┐
          │  STEP 3: Merge      │
          │  Combine metadata   │
          │  Classify type      │
          │  Calculate energy   │
          └──────────┬──────────┘
                     ▼
          ┌─────────────────────┐
          │  STEP 4: Export     │
          │  • slice.wav        │
          │  • vocals.wav       │
          │  • guitar.wav       │
          │  • melody.mid       │
          │  • chords.mid       │
          │  • lyrics.txt       │
          │  • metadata.json    │
          └─────────────────────┘
```

### Technical Implementation

```python
# Source Separation
demucs           # Facebook's model, excellent on M1 (MPS acceleration)
                 # Separates: vocals, drums, bass, other

# Vocal Analysis
faster-whisper   # Optimized Whisper for Apple Silicon
                 # Output: timestamped lyrics transcript
basic-pitch      # Spotify's audio-to-MIDI (polyphonic)
                 # Output: melody MIDI with pitch bends
crepe            # Monophonic pitch tracking (optional, for vibrato detail)

# Guitar/Instrumental Analysis
librosa          # Key detection (chroma features)
                 # BPM detection (beat_track)
                 # Energy (RMS)
madmom           # More accurate beat/downbeat tracking
                 # Chord recognition (CNNChordFeatureProcessor)

# MIDI Generation
pretty_midi      # Create/manipulate MIDI files
midiutil         # Alternative MIDI writer (you're familiar with this)
```

### Metadata Schema (per slice)

```json
{
  "id": "slice_001",
  "session_id": "session_2024-02-08",
  "created": "2024-02-08T14:30:22",
  "duration_sec": 12.4,

  "musical": {
    "key": "G major",
    "key_confidence": 0.87,
    "bpm": 73.2,
    "bpm_confidence": 0.92,
    "time_signature": "4/4",
    "bars": 4,
    "chords": [
      {"time": 0.0, "chord": "G", "duration": 2.0},
      {"time": 2.0, "chord": "D", "duration": 2.0},
      {"time": 4.0, "chord": "Am", "duration": 2.0},
      {"time": 6.0, "chord": "C", "duration": 2.0}
    ]
  },

  "vocals": {
    "has_vocals": true,
    "lyrics": "I drink my coffee extra slow...",
    "lyrics_timestamped": [
      {"start": 0.5, "end": 2.1, "text": "I drink my coffee"},
      {"start": 2.3, "end": 3.8, "text": "extra slow"}
    ]
  },

  "classification": {
    "type": "verse",
    "energy": "low",
    "mood": "reflective",
    "tags": ["acoustic", "ballad"]
  },

  "files": {
    "audio_raw": "slice_001.wav",
    "audio_vocals": "slice_001_vocals.wav",
    "audio_guitar": "slice_001_guitar.wav",
    "midi_melody": "slice_001_melody.mid",
    "midi_chords": "slice_001_chords.mid",
    "lyrics": "slice_001_lyrics.txt"
  }
}
```

### Type Classification Logic

```python
def classify_type(duration, has_vocals, has_chords, rhythm_density):
    if duration < 8 and not has_vocals:
        return "riff"
    elif duration < 8 and has_vocals:
        return "hook"
    elif has_chords and len(chords) >= 4:
        return "chord_progression"
    elif has_vocals and duration > 15:
        return "verse" if rhythm_density < 0.5 else "chorus"
    else:
        return "idea"
```

---

## Module 4: STORE

### Purpose
Organize slices into a nested folder structure and maintain a searchable database.

### Folder Structure

```
~/Music/RidgemontLibrary/
├── sessions/
│   ├── 2024-02-08_143022/
│   │   ├── raw/
│   │   │   └── full_session.wav
│   │   ├── slices/
│   │   │   ├── slice_001/
│   │   │   │   ├── slice_001.wav
│   │   │   │   ├── slice_001_vocals.wav
│   │   │   │   ├── slice_001_guitar.wav
│   │   │   │   ├── slice_001_melody.mid
│   │   │   │   ├── slice_001_chords.mid
│   │   │   │   ├── slice_001_lyrics.txt
│   │   │   │   └── metadata.json
│   │   │   └── slice_002/
│   │   │       └── ...
│   │   └── session.json
│   └── 2024-02-10_091500/
│       └── ...
│
├── library/
│   ├── by_key/
│   │   ├── G_major/
│   │   │   ├── riffs/
│   │   │   │   └── slice_001.wav → (symlink to sessions/)
│   │   │   ├── chord_progressions/
│   │   │   └── verses/
│   │   ├── A_minor/
│   │   └── D_major/
│   └── by_type/
│       ├── riffs/
│       ├── chord_progressions/
│       ├── verses/
│       ├── choruses/
│       └── hooks/
│
├── database.sqlite
└── config.json
```

### Database Schema (SQLite)

```sql
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,
    created DATETIME,
    duration_sec REAL,
    slice_count INTEGER,
    notes TEXT
);

CREATE TABLE slices (
    id TEXT PRIMARY KEY,
    session_id TEXT,
    created DATETIME,
    duration_sec REAL,
    bars INTEGER,
    key TEXT,
    key_confidence REAL,
    bpm REAL,
    bpm_confidence REAL,
    time_signature TEXT,
    type TEXT,
    energy TEXT,
    has_vocals BOOLEAN,
    lyrics TEXT,
    chords_json TEXT,
    tags TEXT,
    path_audio TEXT,
    path_vocals TEXT,
    path_guitar TEXT,
    path_midi_melody TEXT,
    path_midi_chords TEXT,
    path_lyrics TEXT,
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);

CREATE INDEX idx_key ON slices(key);
CREATE INDEX idx_type ON slices(type);
CREATE INDEX idx_bpm ON slices(bpm);
CREATE INDEX idx_has_vocals ON slices(has_vocals);

-- Full-text search for lyrics
CREATE VIRTUAL TABLE lyrics_fts USING fts5(slice_id, lyrics);
```

### Symlink Strategy
- Master files live in `sessions/` (organized by date)
- `library/` contains symlinks organized by key/type
- Allows browsing by either date or musical attributes
- No file duplication

---

## Module 5: BROWSE

### Purpose
Searchable UI to find, preview, and export slices.

### Implementation: Streamlit Web App

```python
# Core
streamlit        # Web UI framework

# Features
- Sidebar filters (key, type, BPM range, has vocals)
- Search bar (searches lyrics, tags)
- Grid/list view of results
- Audio player per slice
- Waveform visualization
- Metadata display
- Export selected to folder (for Logic import)
- Batch operations (tag, delete, merge)
```

### UI Mockup

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  🎸 RIDGEMONT JAM SESSION                              [⚙️ Settings]        │
├──────────────────────┬──────────────────────────────────────────────────────┤
│                      │                                                      │
│  FILTERS             │  LIBRARY (47 slices)                    [List│Grid] │
│  ─────────────       │  ────────────────────────────────────────────────── │
│                      │                                                      │
│  🔍 Search...        │  ┌────────────────────────────────────────────────┐ │
│                      │  │ ▶ slice_001        G major │ verse │ 12s      │ │
│  Key                 │  │   "I drink my coffee extra slow..."           │ │
│  [All        ▼]      │  │   Chords: G - D - Am - C                       │ │
│                      │  │   [Play] [Export] [Edit Tags]                  │ │
│  Type                │  └────────────────────────────────────────────────┘ │
│  ☑ Riff              │  ┌────────────────────────────────────────────────┐ │
│  ☑ Chord Progression │  │ ▶ slice_002        G major │ riff │ 8s        │ │
│  ☑ Verse             │  │   (no vocals)                                  │ │
│  ☑ Chorus            │  │   Chords: Em - D                               │ │
│  ☐ Hook              │  │   [Play] [Export] [Edit Tags]                  │ │
│                      │  └────────────────────────────────────────────────┘ │
│  BPM                 │  ┌────────────────────────────────────────────────┐ │
│  [60]━━━━━━━[120]    │  │ ▶ slice_003        A minor │ hook │ 6s        │ │
│                      │  │   "Why do my feelings run so deep"            │ │
│  Has Vocals          │  │   Chords: Am - G - F                           │ │
│  ○ Any               │  │   [Play] [Export] [Edit Tags]                  │ │
│  ● Yes               │  └────────────────────────────────────────────────┘ │
│  ○ No                │                                                      │
│                      │  ────────────────────────────────────────────────── │
│  Session             │  [Export Selected (3)] [Create Playlist]            │
│  [All        ▼]      │                                                      │
│                      │                                                      │
└──────────────────────┴──────────────────────────────────────────────────────┘
```

### Export for Logic

"Export Selected" creates a folder:

```
~/Music/RidgemontExport/export_2024-02-08/
├── Audio/
│   ├── slice_001.wav
│   ├── slice_001_vocals.wav
│   ├── slice_001_guitar.wav
│   └── slice_003.wav
├── MIDI/
│   ├── slice_001_melody.mid
│   ├── slice_001_chords.mid
│   └── slice_003_melody.mid
├── Lyrics/
│   ├── slice_001_lyrics.txt
│   └── slice_003_lyrics.txt
└── session_notes.txt  (key, BPM, chord summary)
```

---

## MIDI Specifications (Logic-Optimized)

### Requirements
- Tempo embedded in MIDI file header
- Key signature embedded
- Time signature embedded
- Track names descriptive
- Program change for instrument hint

### MIDI Structure (Melody)

```
Track 0: Tempo + Time Signature + Key Signature
Track 1: "Vocal Melody" - Notes with pitch bends for expressiveness
```

### MIDI Structure (Chords)

```
Track 0: Tempo + Time Signature + Key Signature
Track 1: "Guitar Chords" - Block chords, full voicings
         Program: 25 (Acoustic Guitar Steel)
```

### Implementation

```python
from midiutil import MIDIFile

def create_logic_midi(notes, tempo, key, time_sig, filename):
    midi = MIDIFile(1)

    # Track 0 metadata
    midi.addTempo(0, 0, tempo)
    midi.addTimeSignature(0, 0, time_sig[0], int(log2(time_sig[1])), 24, 8)
    midi.addKeySignature(0, 0, key_to_sf(key), is_minor(key))
    midi.addTrackName(0, 0, "Guitar Chords")
    midi.addProgramChange(0, 0, 0, 25)  # Acoustic Guitar

    # Add notes...
    for note in notes:
        midi.addNote(...)

    with open(filename, 'wb') as f:
        midi.writeFile(f)
```

---

## Priority Implementation Order

Based on your ranking:

### Phase 1: Core Capture & Slice
1. ✅ Python recorder with footswitch support
2. ✅ Metronome (headphones only)
3. ✅ Silence fallback detection
4. ✅ Basic file output

### Phase 2: Melody & MIDI
5. ✅ Basic Pitch integration (audio → MIDI)
6. ✅ Logic-optimized MIDI export

### Phase 3: Browser UI
7. ✅ Streamlit app
8. ✅ SQLite database
9. ✅ Search/filter functionality

### Phase 4: Detection
10. ✅ Key detection (librosa)
11. ✅ Source separation (Demucs)
12. ✅ Vocal transcription (Whisper)
13. ✅ Chord detection
14. ✅ BPM detection

### Phase 5: Polish
15. ✅ Nested folder organization
16. ✅ Export workflow
17. ✅ Tag editing
18. ✅ Batch operations

---

## Dependencies (All Free)

```bash
# Create virtual environment
python3 -m venv ~/ridgemont-env
source ~/ridgemont-env/bin/activate

# Audio I/O
pip install pyaudio sounddevice numpy scipy

# Audio processing
pip install pydub librosa

# Source separation
pip install demucs

# Transcription & pitch
pip install faster-whisper basic-pitch

# MIDI
pip install midiutil pretty_midi

# Database
pip install sqlite3  # (built-in)

# UI
pip install streamlit

# Utilities
pip install watchdog pynput
```

### Footswitch Hardware
- Recommended: **iKKEGOL USB Foot Pedal** (~$15 Amazon)
- Appears as USB keyboard, sends configurable keystroke
- No drivers needed on macOS

---

## Configuration File

```json
{
  "app_name": "Ridgemont Jam Session",
  "version": "1.0.0",

  "paths": {
    "library_root": "~/Music/RidgemontLibrary",
    "sessions_dir": "sessions",
    "library_dir": "library",
    "export_dir": "~/Music/RidgemontExport"
  },

  "recording": {
    "sample_rate": 44100,
    "channels": 1,
    "format": "wav",
    "footswitch_key": "f13",
    "silence_threshold_db": -40,
    "silence_duration_sec": 2.5
  },

  "metronome": {
    "default_bpm": 73,
    "sound": "click_high.wav",
    "volume": 0.7
  },

  "analysis": {
    "separate_sources": true,
    "detect_key": true,
    "detect_bpm": true,
    "detect_chords": true,
    "transcribe_vocals": true,
    "generate_midi": true,
    "whisper_model": "medium"
  },

  "organization": {
    "structure": "nested",
    "symlinks": true
  }
}
```

---

## Next Steps

1. **Acquire footswitch** - iKKEGOL USB Foot Pedal (~$15)
2. **I build Phase 1** - Capture & Slice module
3. **Test recording workflow** - Verify footswitch + silence detection
4. **Iterate** - Add analysis and UI incrementally

---

Ready to start coding?
