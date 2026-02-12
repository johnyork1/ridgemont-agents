from midiutil import MIDIFile

TEMPO = 73
BEATS_PER_BAR = 4

# Verified guitar voicings using correct MIDI note numbers
# Middle C = C4 = MIDI 60
#
# G2=43, A2=45, B2=47, C3=48, D3=50, E3=52, F#3=54, G3=55, A3=57, B3=59
# C4=60, D4=62, E4=64, F#4=66, G4=67

CHORD_VOICINGS = {
    # G major: G-B-D (open position)
    'G':  [43, 47, 50, 55, 59, 67],   # G2, B2, D3, G3, B3, G4

    # D major: D-F#-A (open position)
    'D':  [50, 54, 57, 62],           # D3, F#3, A3, D4

    # A minor: A-C-E (open position)
    'Am': [45, 52, 57, 60, 64],       # A2, E3, A3, C4, E4

    # C major: C-E-G (open position)
    'C':  [48, 52, 55, 60, 64],       # C3, E3, G3, C4, E4

    # B minor: B-D-F# (barre position)
    'Bm': [47, 54, 59, 62, 66],       # B2, F#3, B3, D4, F#4
}

def add_chord(midi, track, chord_name, start_beat, duration, velocity=85):
    notes = CHORD_VOICINGS[chord_name]
    for note in notes:
        midi.addNote(track, 0, note, start_beat, duration, velocity)

def add_verse_section(midi, track, start_bar):
    beat = start_bar * BEATS_PER_BAR

    # Line 1: G - D - Am - D (4 bars)
    add_chord(midi, track, 'G', beat, 4); beat += 4
    add_chord(midi, track, 'D', beat, 4); beat += 4
    add_chord(midi, track, 'Am', beat, 4); beat += 4
    add_chord(midi, track, 'D', beat, 4); beat += 4

    # Line 2: G - D - Am - C/D (4 bars)
    add_chord(midi, track, 'G', beat, 4); beat += 4
    add_chord(midi, track, 'D', beat, 4); beat += 4
    add_chord(midi, track, 'Am', beat, 4); beat += 4
    add_chord(midi, track, 'C', beat, 2); beat += 2
    add_chord(midi, track, 'D', beat, 2); beat += 2

    # Line 3: G - D - Am - D (4 bars)
    add_chord(midi, track, 'G', beat, 4); beat += 4
    add_chord(midi, track, 'D', beat, 4); beat += 4
    add_chord(midi, track, 'Am', beat, 4); beat += 4
    add_chord(midi, track, 'D', beat, 4); beat += 4

    # Line 4: G - D - Am - C/D (4 bars)
    add_chord(midi, track, 'G', beat, 4); beat += 4
    add_chord(midi, track, 'D', beat, 4); beat += 4
    add_chord(midi, track, 'Am', beat, 4); beat += 4
    add_chord(midi, track, 'C', beat, 2); beat += 2
    add_chord(midi, track, 'D', beat, 2); beat += 2

    return 16

def add_bridge_section(midi, track, start_bar):
    beat = start_bar * BEATS_PER_BAR

    # Line 1: Am - D - G - Bm - C - D (4 bars)
    add_chord(midi, track, 'Am', beat, 4); beat += 4
    add_chord(midi, track, 'D', beat, 4); beat += 4
    add_chord(midi, track, 'G', beat, 4); beat += 4
    add_chord(midi, track, 'Bm', beat, 2); beat += 2
    add_chord(midi, track, 'C', beat, 1); beat += 1
    add_chord(midi, track, 'D', beat, 1); beat += 1

    # Line 2: Am - D - G - Bm - C - D (4 bars)
    add_chord(midi, track, 'Am', beat, 4); beat += 4
    add_chord(midi, track, 'D', beat, 4); beat += 4
    add_chord(midi, track, 'G', beat, 4); beat += 4
    add_chord(midi, track, 'Bm', beat, 2); beat += 2
    add_chord(midi, track, 'C', beat, 1); beat += 1
    add_chord(midi, track, 'D', beat, 1); beat += 1

    return 8

def add_outro_section(midi, track, start_bar):
    beat = start_bar * BEATS_PER_BAR

    # Phrase 1: G - D - Am - C/D (4 bars)
    add_chord(midi, track, 'G', beat, 4); beat += 4
    add_chord(midi, track, 'D', beat, 4); beat += 4
    add_chord(midi, track, 'Am', beat, 4); beat += 4
    add_chord(midi, track, 'C', beat, 2); beat += 2
    add_chord(midi, track, 'D', beat, 2); beat += 2

    # Phrase 2: G - D - Am - D (4 bars)
    add_chord(midi, track, 'G', beat, 4); beat += 4
    add_chord(midi, track, 'D', beat, 4); beat += 4
    add_chord(midi, track, 'Am', beat, 4); beat += 4
    add_chord(midi, track, 'D', beat, 4); beat += 4

    # Phrase 3: G - D - Am - C/D/G (4 bars)
    add_chord(midi, track, 'G', beat, 4); beat += 4
    add_chord(midi, track, 'D', beat, 4); beat += 4
    add_chord(midi, track, 'Am', beat, 4); beat += 4
    add_chord(midi, track, 'C', beat, 1); beat += 1
    add_chord(midi, track, 'D', beat, 1); beat += 1
    add_chord(midi, track, 'G', beat, 2); beat += 2

    return 12

# Create MIDI
midi = MIDIFile(1)
track = 0
midi.addTempo(track, 0, TEMPO)
midi.addProgramChange(track, 0, 0, 25)

current_bar = 0

print("Generating 'Getting Old' at 73 BPM...")
print("\nChord voicings (MIDI notes):")
for name, notes in CHORD_VOICINGS.items():
    print(f"  {name}: {notes}")

print(f"\nStructure:")

print(f"  Verse 1: bars {current_bar+1}-", end="")
bars = add_verse_section(midi, track, current_bar)
current_bar += bars
print(f"{current_bar}")

print(f"  Bridge 1: bars {current_bar+1}-", end="")
bars = add_bridge_section(midi, track, current_bar)
current_bar += bars
print(f"{current_bar}")

print(f"  Verse 2: bars {current_bar+1}-", end="")
bars = add_verse_section(midi, track, current_bar)
current_bar += bars
print(f"{current_bar}")

print(f"  Bridge 2: bars {current_bar+1}-", end="")
bars = add_bridge_section(midi, track, current_bar)
current_bar += bars
print(f"{current_bar}")

print(f"  Outro: bars {current_bar+1}-", end="")
bars = add_outro_section(midi, track, current_bar)
current_bar += bars
print(f"{current_bar}")

total_beats = current_bar * BEATS_PER_BAR
duration_seconds = total_beats * 60 / TEMPO
minutes = int(duration_seconds // 60)
seconds = int(duration_seconds % 60)

print(f"\nTotal: {current_bar} bars ({minutes}:{seconds:02d})")

output_path = "/sessions/nice-laughing-heisenberg/mnt/Make-Music/Getting_Old_73bpm.mid"
with open(output_path, 'wb') as f:
    midi.writeFile(f)
print(f"\nSaved: {output_path}")
