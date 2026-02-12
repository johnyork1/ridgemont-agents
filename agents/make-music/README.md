# Make Music

MIDI generation and songwriting workspace for composing songs, creating chord sheets, and drafting Suno AI prompts.

## What It Does

- Generates realistic acoustic guitar MIDI files for Logic Pro using Python `midiutil`
- Applies strumming realism: strum spread, velocity ramps, humanization, guitar-correct voicings
- Creates chord sheets in plain text format
- Drafts quick Suno AI prompts for demo production

## Usage

Provide a song name, chord progression, BPM, time signature, and style. The agent generates:

- MIDI file: `[song_name]_[bpm]bpm.mid`
- Chord sheet: `[Song_Title]_Chord_Sheet.txt`
- Suno prompt: `[Song_Title]_Suno.txt`

Test MIDI files go in `Tests/`. Generation scripts are named `generate_[song].py`.

## Requirements

- Python 3.x
- `midiutil` (`pip install midiutil`)
- Logic Pro (for importing generated MIDI files)

## Related Agents

- **catalog-manager** -- add finished songs once they reach demo status or beyond
