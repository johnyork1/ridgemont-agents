# Realistic Strummed Acoustic Guitar in Logic Pro — MIDI Programming Guide

## The Core Principle

MIDI strumming sounds fake when notes trigger simultaneously. Real strumming has **temporal spread**, **velocity variation**, and **imperfect timing** across strings. Stop thinking like a pianist — program like a guitarist.

---

## Method 1: Session Players (Fastest Path to Beautiful Results)

Logic Pro 11+ includes Session Players that generate musical strumming automatically.

**Setup:**
1. Create Software Instrument track → load acoustic guitar patch
2. In track header or Library, switch to **Session Player (Keyboard Player)**
3. Choose a strummed acoustic style/pattern
4. Enter chord symbols in the **Chord Track** (global track) or play block chords
5. Adjust Complexity, Intensity, Feel, Strum Pattern, Up/Down stroke mix
6. When happy → right-click region → **Convert to MIDI Region** to edit further

Best for: Quick sketches, song demos, getting musical results in minutes.

---

## Method 2: Logic Scripter Automation (The "Code" Approach)

Logic's **MIDI FX → Scripter** lets you write JavaScript that transforms block chords into strums automatically.

### Strumify Script — Paste into Scripter

```javascript
// Strumify: turn simultaneous chord notes into realistic strums
// Insert on guitar track: MIDI FX → Scripter → paste this code
// Play/sequence block chords — script spreads them as strums

var STRUM_MS = 26;         // base delay between strings in milliseconds (10-45 range)
var RANDOM_MS = 6;         // random timing per note (+/-)
var VEL_SLOPE = 3;         // velocity change per string (downstroke ramps up)
var MIN_VEL = 20;
var MAX_VEL = 120;

var chordBuffer = {};
var lastChordTime = -1;

function clamp(v, lo, hi) { 
  return Math.max(lo, Math.min(hi, v)); 
}

function HandleMIDI(event) {
  if (event instanceof NoteOn) {
    var t = event.beatPos;
    var key = t.toFixed(6);
    
    if (!chordBuffer[key]) chordBuffer[key] = [];
    chordBuffer[key].push({ 
      pitch: event.pitch, 
      vel: event.velocity, 
      chan: event.channel 
    });
    
    if (lastChordTime < 0) lastChordTime = t;
  }
  else {
    event.send();
  }
}

function ProcessMIDI() {
  for (var key in chordBuffer) {
    var notes = chordBuffer[key];
    if (!notes || notes.length === 0) continue;
    
    // Downstroke on strong beats, upstroke on weak beats
    var beat = parseFloat(key);
    var isDown = (Math.floor(beat * 2) % 4 === 0);
    
    // Sort pitches for strum direction
    notes.sort(function(a,b) { 
      return isDown ? (a.pitch - b.pitch) : (b.pitch - a.pitch); 
    });
    
    for (var i = 0; i < notes.length; i++) {
      var n = notes[i];
      
      var delayMs = (STRUM_MS * i) + (Math.random() * 2 - 1) * RANDOM_MS;
      var delay = delayMs / 1000.0;
      
      var vel = clamp(
        n.vel + (isDown ? (VEL_SLOPE * i) : (-VEL_SLOPE * i)), 
        MIN_VEL, 
        MAX_VEL
      );
      
      var on = new NoteOn();
      on.pitch = n.pitch;
      on.velocity = vel;
      on.channel = n.chan;
      
      var off = new NoteOff(on);
      off.channel = n.chan;
      
      on.sendAtBeat(parseFloat(key) + SecondsToBeats(delay));
      off.sendAtBeat(parseFloat(key) + SecondsToBeats(delay) + 0.9);
    }
    
    chordBuffer[key] = [];
  }
}

function SecondsToBeats(sec) {
  var tempo = GetTempo();
  return (sec * tempo) / 60.0;
}
```

### Tuning the Script

| Parameter | Range | Effect |
|-----------|-------|--------|
| `STRUM_MS` | 10-18 | Gentle, intimate |
| `STRUM_MS` | 18-30 | Normal strum |
| `STRUM_MS` | 30-45 | Aggressive, percussive |
| `RANDOM_MS` | 3-8 | Subtle humanization |
| `VEL_SLOPE` | 2-5 | Velocity ramp intensity |

---

## Method 3: Built-in Scripter Preset (Quick Alternative)

1. Create Software Instrument track → load acoustic guitar patch
2. Add **MIDI FX → Scripter**
3. Choose preset: **Factory → Guitar → Guitar Strummer**
4. Play block chords
5. Adjust Direction (positive = down, negative = up), Spread, Velocity Range

---

## Method 4: Manual Piano Roll Programming (Maximum Control)

### Step 1: Guitar-Correct Voicings

**Critical:** Don't voice chords like a pianist. Guitars span 2 octaves with doubled notes.

| Chord | Piano Roll Notes (low to high) |
|-------|-------------------------------|
| Open G | G2 – B2 – D3 – G3 – B3 – G4 |
| Open C | C3 – E3 – G3 – C4 – E4 – G4 |
| Open D | D2 – A2 – D3 – F#3 – A3 – D4 |
| Am | A2 – E3 – A3 – C4 – E4 – A4 |
| Em | E2 – B2 – E3 – G3 – B3 – E4 |

**Rules:**
- Spread notes across ~2 octaves
- Root at bottom, fifth next, then chord tones
- Don't always play 6 notes — real strums miss strings
- Avoid tight clusters below A2

### Step 2: Strum Spread (The "Waterfall")

Instead of simultaneous notes, offset each by 5-20 ticks (10-30ms):

**Downstrum Example (Em):**
| String | Note | Offset | Velocity |
|--------|------|--------|----------|
| 6 (Low E) | E2 | 0ms | 90 |
| 5 | B2 | +18ms | 93 |
| 4 | E3 | +36ms | 96 |
| 3 | G3 | +54ms | 100 |
| 2 | B3 | +72ms | 95 |
| 1 (High E) | E4 | +90ms | 88 |

**Upstrum:** Reverse the offset order (high strings first).

### Step 3: Q-Flam Shortcut

Select chord notes in Piano Roll, then in **Region Inspector**:
- **Q-Flam positive** (+10 to +30 ticks): Downstrum
- **Q-Flam negative** (-15 to -40 ticks): Upstrum

### Step 4: Velocity Shaping

| Strum Type | Bass Strings | Middle | Treble |
|------------|--------------|--------|--------|
| Downstroke | 90-110 | 85-100 | 70-85 |
| Upstroke | 50-70 | 70-85 | 85-100 |
| Ghost/muted | 30-50 | 35-55 | 40-60 |

### Step 5: Humanize

**Functions → MIDI Transform → Humanize:**
- Position: ±5-12 ticks
- Velocity: ±5-10

**Manual additions:**
- One or two strings slightly louder (creates melody within chord)
- Chord changes anticipate by 10-25ms (players lead changes)
- Let bass notes ring slightly into next chord

---

## Common Strumming Patterns

### Folk/Acoustic 4/4
```
Beat:   1      +      2      +      3      +      4      +
Strum:  D      D      D-U    U      D      U      D-U    U
        ↓      ↓      ↓↑     ↑      ↓      ↑      ↓↑     ↑
Vel:    100    70     90/60  55     95     50     85/55  50
```

### Pop Verse
```
Beat:   1      +      2      +      3      +      4      +
Strum:  D      -      D      U      U      D      U      -
        ↓             ↓      ↑      ↑      ↓      ↑
Vel:    100           85     60     55     90     50
```

### Ballad (Slow, Wide Spread)
```
Beat:   1             2             3             4
Strum:  D (slow)      -             D (slow)      U (gentle)
Spread: 80-120ms                    80-120ms      60ms
```

**Pattern Notes:**
- D = full downstrum (all 6 strings)
- U = partial upstrum (top 3-4 strings only)
- Ghost strums: very soft, 2-3 strings, between main hits
- Never quantize 100% to grid

---

## Extra Realism Techniques

1. **Muted "chucks":** Very short notes (32nd) with low velocity for percussive rhythm
2. **Ghost notes:** Quiet single picked notes between strums
3. **String skipping:** Don't always play all 6 strings
4. **Sustain overlap:** Let notes ring until next chord (legato)
5. **Slight early attacks:** Place chord changes 10-25ms before the beat

---

## Method Comparison

| Method | Speed | Realism | Best For |
|--------|-------|---------|----------|
| Session Player | ★★★★★ | ★★★★☆ | Fast sketching, demos |
| Scripter (custom code) | ★★★★☆ | ★★★★☆ | Automated strums, consistency |
| Scripter (preset) | ★★★★☆ | ★★★☆☆ | Quick block chord conversion |
| Q-Flam + velocity | ★★★☆☆ | ★★★★★ | Polished final parts |
| Full manual + humanize | ★★☆☆☆ | ★★★★★+ | Pro singer-songwriter productions |

---

## Recommended Workflow

1. **Sketch phase:** Session Player or Scripter preset for quick ideas
2. **Arrange phase:** Convert to MIDI, adjust patterns and voicings
3. **Polish phase:** Manual velocity/timing tweaks, humanize, add ghost strums
4. **Final phase:** A/B against reference tracks, adjust spread and dynamics

---

*Guide compiled for Ridgemont Studio — January 2026*
