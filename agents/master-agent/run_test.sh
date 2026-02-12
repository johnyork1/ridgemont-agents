#!/bin/bash
# ============================================
# Make Videos Pipeline — Test Runner
# Song: "Crazy" by Echoes of Jahara (Reggae)
# ============================================
# Run from the Make Videos folder:
#   cd "/Users/johnyork/My Drive/Ridgemont Studio/Claude Cowork/Make Videos"
#   bash run_test.sh
# ============================================

set -e
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
echo "=== Make Videos Pipeline Test ==="
echo "Project root: $PROJECT_ROOT"
echo ""

# Step 0: Install dependencies
echo "--- Installing Python dependencies ---"
pip3 install librosa Pillow numpy moviepy --break-system-packages --quiet 2>/dev/null || \
pip3 install librosa Pillow numpy moviepy --quiet
echo "Dependencies installed."
echo ""

# Step 1: Verify test files exist
echo "--- Verifying test song files ---"
SONG_DIR="$PROJECT_ROOT/ingestion/crazy"
for f in "Crazy (Reggae).mp3" "artist_profile.json" "creative_brief.json" "background.jpg" "lyrics.lrc"; do
    if [ -f "$SONG_DIR/$f" ]; then
        echo "  ✓ $f"
    else
        echo "  ✗ MISSING: $f"
        exit 1
    fi
done
echo ""

# Step 2: Run audio analysis
echo "--- Step 2: Audio Analysis ---"
cd "$PROJECT_ROOT"
python3 -c "
import sys, os, json
sys.path.insert(0, 'scripts')

# Minimal analysis test — just librosa
import librosa
import numpy as np

audio_path = 'ingestion/crazy/Crazy (Reggae).mp3'
print(f'Loading: {audio_path}')
y, sr = librosa.load(audio_path)
print(f'Sample rate: {sr}, Duration: {len(y)/sr:.1f}s')

# BPM and beats
tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
beat_times = librosa.frames_to_time(beat_frames, sr=sr)
bpm_val = float(tempo) if not isinstance(tempo, np.ndarray) else float(tempo[0])
print(f'BPM: {bpm_val:.1f}, Beats: {len(beat_times)}')

# Key estimation with confidence
chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
key_strengths = chroma.mean(axis=1)
estimated_key = int(key_strengths.argmax())
key_names = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']

sorted_strengths = np.sort(key_strengths)[::-1]
key_confidence = float((sorted_strengths[0] - sorted_strengths[1]) / sorted_strengths[0])

major_third = key_strengths[(estimated_key + 4) % 12]
minor_third = key_strengths[(estimated_key + 3) % 12]
is_major = bool(major_third > minor_third)
mode_confidence = float(abs(major_third - minor_third) / max(major_third, minor_third))

mode = 'major' if is_major else 'minor'
reliable = key_confidence > 0.15 and mode_confidence > 0.10
print(f'Key: {key_names[estimated_key]} {mode} (confidence: {key_confidence:.3f})')
print(f'Mode confidence: {mode_confidence:.3f}')
print(f'Analysis reliable: {reliable}')

# Energy
rms = librosa.feature.rms(y=y)[0].mean()
energy = 'high' if rms > 0.15 else ('medium' if rms > 0.08 else 'low')
print(f'Energy: {energy} (RMS: {float(rms):.4f})')

# Load mood map
mood = 'genre_default'
if os.path.exists('data/mood_map.json'):
    with open('data/mood_map.json') as f:
        mm = json.load(f)
    if reliable:
        for rule in mm.get('rules', []):
            cond = rule['condition']
            match = True
            if 'bpm >' in cond:
                threshold = float(cond.split('bpm >')[1].split(' AND')[0].strip())
                if bpm_val <= threshold: match = False
            if 'bpm <' in cond:
                threshold = float(cond.split('bpm <')[1].split(' AND')[0].strip())
                if bpm_val >= threshold: match = False
            if 'major_key' in cond and not is_major: match = False
            if 'minor_key' in cond and is_major: match = False
            if 'energy_high' in cond and energy != 'high': match = False
            if match:
                mood = rule['mood']
                print(f'Mood matched: {mood}')
                print(f'  Weeter: {rule.get(\"weeter_pose\", \"default\")}')
                print(f'  Blubby: {rule.get(\"blubby_pose\", \"default\")}')
                break
    else:
        print('Low confidence — using genre defaults')
else:
    print('No mood_map.json found')

# Build manifest
duration = float(librosa.get_duration(y=y, sr=sr))
manifest = {
    'song_id': 'crazy',
    'artist': 'Echoes of Jahara',
    'genre': 'Reggae',
    'audio_source': 'ingestion/crazy/Crazy (Reggae).mp3',
    'bpm': bpm_val,
    'beats': {'beat_times': beat_times.tolist(), 'beat_count': len(beat_times)},
    'key': {'key_name': key_names[estimated_key], 'mode': mode,
            'key_confidence': round(key_confidence, 4),
            'mode_confidence': round(mode_confidence, 4)},
    'energy': {'level': float(rms), 'category': energy},
    'duration': duration,
    'analysis_reliable': reliable,
    'mood': mood,
    'background_image': 'ingestion/crazy/background.jpg',
    'pipeline': {'status': 'ANALYZED', 'analyzed_at': __import__('datetime').datetime.now().isoformat()}
}

# Save manifest
out_dir = 'catalog/Echoes of Jahara/crazy'
os.makedirs(out_dir, exist_ok=True)
manifest_path = os.path.join(out_dir, 'manifest.json')
with open(manifest_path, 'w') as f:
    json.dump(manifest, f, indent=2)
print(f'')
print(f'Manifest saved: {manifest_path}')
print(f'=== Analysis Complete ===')
"

echo ""
echo "--- Step 3: Baseline Master Video ---"
echo "(Building Ken Burns + audio video...)"

python3 -c "
import json, os, subprocess

# Load manifest
with open('catalog/Echoes of Jahara/crazy/manifest.json') as f:
    m = json.load(f)

bg = 'ingestion/crazy/background.jpg'
audio = 'ingestion/crazy/Crazy (Reggae).mp3'
duration = m['duration']
output = 'catalog/Echoes of Jahara/crazy/master_video.mp4'

# Ken Burns on background + audio
cmd = (
    f'ffmpeg -y -loop 1 -i \"{bg}\" -i \"{audio}\" '
    f'-filter_complex \"[0:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,'
    f'zoompan=z=\\\"min(zoom+0.0001,1.15)\\\":x=\\\"iw/2-(iw/zoom/2)+30*on/900\\\":y=\\\"ih/2-(ih/zoom/2)+15*on/900\\\":d=900:s=1920x1080:fps=30\" '
    f'-c:v libx264 -crf 18 -preset medium -tune stillimage '
    f'-c:a aac -b:a 192k -shortest -t {duration:.0f} '
    f'\"{output}\"'
)

print(f'Rendering master ({duration:.0f}s)...')
result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
if result.returncode == 0:
    size = os.path.getsize(output) / 1024 / 1024
    print(f'Master video created: {output} ({size:.1f} MB)')
else:
    print(f'FFmpeg error: {result.stderr[:300]}')
    # Try simpler fallback
    print('Trying simplified render...')
    cmd2 = f'ffmpeg -y -loop 1 -i \"{bg}\" -i \"{audio}\" -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a aac -shortest -t {duration:.0f} \"{output}\"'
    r2 = subprocess.run(cmd2, shell=True, capture_output=True, text=True)
    if r2.returncode == 0:
        print(f'Simplified master created: {output}')
    else:
        print(f'Render failed: {r2.stderr[:200]}')
"

echo ""
echo "--- Step 4: Blur-Fill Short (9:16) ---"

python3 -c "
import subprocess, os

master = 'catalog/Echoes of Jahara/crazy/master_video.mp4'
output = 'catalog/Echoes of Jahara/crazy/short_blurfill.mp4'

if not os.path.exists(master):
    print('No master video — skipping')
    exit(0)

cmd = (
    f'ffmpeg -y -i \"{master}\" '
    f'-filter_complex \"'
    f'[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=20:5[bg];'
    f'[0:v]scale=1080:-2:force_original_aspect_ratio=decrease[fg];'
    f'[bg][fg]overlay=(W-w)/2:(H-h)/2'
    f'\" -c:v libx264 -crf 18 -preset medium -c:a aac -t 59 '
    f'\"{output}\"'
)

print('Rendering blur-fill vertical (59s max)...')
result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
if result.returncode == 0:
    size = os.path.getsize(output) / 1024 / 1024
    print(f'Short created: {output} ({size:.1f} MB)')
else:
    print(f'Error: {result.stderr[:300]}')
"

echo ""
echo "========================================="
echo "  PIPELINE TEST COMPLETE"
echo "========================================="
echo "Check catalog/Echoes of Jahara/crazy/ for:"
echo "  - manifest.json (analysis results)"
echo "  - master_video.mp4 (16:9 master)"
echo "  - short_blurfill.mp4 (9:16 vertical)"
echo "========================================="
