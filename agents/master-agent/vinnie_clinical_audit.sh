#!/bin/bash
#──────────────────────────────────────────────────────────
# vinnie_clinical_audit.sh
# Clinical Audit of Dr. Vinnie Boombatz container internals
# Tests: catalog parsing, is_analyzed flag, script imports,
#        batch sizing analysis
#──────────────────────────────────────────────────────────
set -euo pipefail

RS="/Users/johnyork/Ridgemont_Studio"
IMAGE="vinnie-agent"
PASS=0
FAIL=0

report() {
  local status=$1 check=$2
  if [ "$status" = "PASS" ]; then
    echo "  ✅ PASS — $check"
    PASS=$((PASS + 1))
  else
    echo "  ❌ FAIL — $check"
    FAIL=$((FAIL + 1))
  fi
}

echo "═══════════════════════════════════════════════════════"
echo " Dr. Vinnie Boombatz — Clinical Self-Audit"
echo " 'The doctor will see himself now.'"
echo "═══════════════════════════════════════════════════════"
echo ""

#──────────────────────────────────────────────────────────
# TEST 1: Catalog Read — Parse a random manifest.json
#──────────────────────────────────────────────────────────
echo "── TEST 1: Catalog Read — manifest.json parsing ──"

CATALOG_READ=$(docker run --rm \
  -v "$RS/catalog:/app/catalog:ro" \
  "$IMAGE" -c "
import os, json, random

# Find all manifest.json files under the_ridgemonts
ridgemonts = '/app/catalog/the_ridgemonts'
manifests = []
for root, dirs, files in os.walk(ridgemonts):
    for f in files:
        if f == 'manifest.json':
            manifests.append(os.path.join(root, f))

if not manifests:
    print('ERROR: No manifest.json files found in the_ridgemonts/')
else:
    # Pick a random manifest
    chosen = random.choice(manifests)
    with open(chosen, 'r') as fp:
        data = json.load(fp)

    title = data.get('title', 'UNKNOWN')
    artist = data.get('artist', 'UNKNOWN')
    genre = data.get('genre', 'UNKNOWN')
    bpm = data.get('bpm', 'N/A')
    key_sig = data.get('key', 'N/A')
    analyzed = data.get('is_analyzed', 'MISSING')
    pipeline = data.get('pipeline_stage', 'MISSING')

    print(f'MANIFEST_OK')
    print(f'  File: {os.path.relpath(chosen, \"/app/catalog\")}')
    print(f'  Title: {title}')
    print(f'  Artist: {artist}')
    print(f'  Genre: {genre}')
    print(f'  BPM: {bpm} | Key: {key_sig}')
    print(f'  is_analyzed: {analyzed}')
    print(f'  pipeline_stage: {pipeline}')
    print(f'  Total manifests found: {len(manifests)}')
" 2>&1)

if echo "$CATALOG_READ" | grep -q "MANIFEST_OK"; then
  report "PASS" "Parsed random manifest from the_ridgemonts/"
  echo "$CATALOG_READ" | grep -v "MANIFEST_OK"
else
  report "FAIL" "Could not parse manifest"
  echo "$CATALOG_READ"
fi

#──────────────────────────────────────────────────────────
# TEST 2: is_analyzed flag verification
#──────────────────────────────────────────────────────────
echo ""
echo "── TEST 2: is_analyzed Flag Census ──"

ANALYZED_CHECK=$(docker run --rm \
  -v "$RS/catalog:/app/catalog:ro" \
  "$IMAGE" -c "
import os, json

total = 0
analyzed_true = 0
analyzed_false = 0
analyzed_missing = 0
pipeline_analyzed = 0

for root, dirs, files in os.walk('/app/catalog'):
    for f in files:
        if f == 'manifest.json':
            total += 1
            path = os.path.join(root, f)
            with open(path, 'r') as fp:
                data = json.load(fp)

            flag = data.get('is_analyzed')
            if flag is True:
                analyzed_true += 1
            elif flag is False:
                analyzed_false += 1
            else:
                analyzed_missing += 1

            if data.get('pipeline_stage') == 'analyzed':
                pipeline_analyzed += 1

print(f'CENSUS_OK')
print(f'  Total manifests: {total}')
print(f'  is_analyzed=true:  {analyzed_true}')
print(f'  is_analyzed=false: {analyzed_false}')
print(f'  is_analyzed=MISSING: {analyzed_missing}')
print(f'  pipeline_stage=analyzed: {pipeline_analyzed}')
print(f'  Coverage: {analyzed_true}/{total} ({100*analyzed_true//max(total,1)}%)')
" 2>&1)

if echo "$ANALYZED_CHECK" | grep -q "CENSUS_OK"; then
  report "PASS" "is_analyzed census complete"
  echo "$ANALYZED_CHECK" | grep -v "CENSUS_OK"
else
  report "FAIL" "is_analyzed census failed"
  echo "$ANALYZED_CHECK"
fi

#──────────────────────────────────────────────────────────
# TEST 3: Shared Script Integration
#──────────────────────────────────────────────────────────
echo ""
echo "── TEST 3: Shared Script Integration ──"

SCRIPT_AUDIT=$(docker run --rm "$IMAGE" -c "
import os, re

scripts_dir = '/app/scripts'
if not os.path.isdir(scripts_dir):
    print('ERROR: /app/scripts/ does not exist')
else:
    py_files = sorted([f for f in os.listdir(scripts_dir) if f.endswith('.py')])
    print(f'SCRIPTS_OK')
    print(f'  Python scripts: {len(py_files)}')

    # Check for specific utility modules
    manifest_modules = [f for f in py_files if 'manifest' in f.lower()]
    cache_modules = [f for f in py_files if 'cache' in f.lower()]
    log_modules = [f for f in py_files if 'log' in f.lower()]
    analyze_modules = [f for f in py_files if 'analy' in f.lower()]

    print(f'  Manifest modules: {manifest_modules or \"NONE\"}')
    print(f'  Cache modules: {cache_modules or \"NONE\"}')
    print(f'  Logging modules: {log_modules or \"NONE\"}')
    print(f'  Analysis modules: {analyze_modules or \"NONE\"}')

    # Check import chains
    import_from_scripts = 0
    cross_imports = {}
    for f in py_files:
        path = os.path.join(scripts_dir, f)
        try:
            with open(path, 'r') as fp:
                content = fp.read()
            # Look for inter-script imports
            imports = re.findall(r'(?:from|import)\s+([\w.]+)', content)
            local_imports = [i for i in imports if any(
                mod.replace('.py','') in i for mod in py_files if mod != f
            )]
            if local_imports:
                cross_imports[f] = local_imports
                import_from_scripts += 1
        except Exception:
            pass

    print(f'  Cross-imports: {import_from_scripts} scripts import siblings')
    if cross_imports:
        for script, imports in cross_imports.items():
            print(f'    {script} → {imports}')

    # Check for sys.path manipulation
    syspath_scripts = 0
    for f in py_files:
        path = os.path.join(scripts_dir, f)
        try:
            with open(path, 'r') as fp:
                content = fp.read()
            if 'sys.path' in content:
                syspath_scripts += 1
                print(f'  ⚠️  {f} manipulates sys.path')
        except:
            pass

    if syspath_scripts == 0:
        print(f'  No sys.path manipulation found')

    # List all scripts
    print(f'')
    print(f'  Full inventory:')
    for f in py_files:
        size = os.path.getsize(os.path.join(scripts_dir, f))
        print(f'    {f:40s} {size:>6,} bytes')
" 2>&1)

if echo "$SCRIPT_AUDIT" | grep -q "SCRIPTS_OK"; then
  report "PASS" "Shared scripts accessible"
  echo "$SCRIPT_AUDIT" | grep -v "SCRIPTS_OK"
else
  report "FAIL" "Scripts directory issue"
  echo "$SCRIPT_AUDIT"
fi

#──────────────────────────────────────────────────────────
# TEST 4: Context Window / Batch Analysis
#──────────────────────────────────────────────────────────
echo ""
echo "── TEST 4: Lyrics Batch Size Analysis ──"

BATCH_ANALYSIS=$(docker run --rm \
  -v "$RS/catalog:/app/catalog:ro" \
  "$IMAGE" -c "
import os

# Count all lyrics files and measure sizes
lyrics_files = []
total_chars = 0
total_words = 0

for root, dirs, files in os.walk('/app/catalog'):
    for f in files:
        if f.endswith('.txt') and 'lyric' in f.lower():
            path = os.path.join(root, f)
            try:
                with open(path, 'r', errors='replace') as fp:
                    content = fp.read()
                chars = len(content)
                words = len(content.split())
                lyrics_files.append({
                    'path': os.path.relpath(path, '/app/catalog'),
                    'chars': chars,
                    'words': words
                })
                total_chars += chars
                total_words += words
            except:
                pass

# Also check for .lrc files
for root, dirs, files in os.walk('/app/catalog'):
    for f in files:
        if f.endswith('.lrc'):
            path = os.path.join(root, f)
            try:
                with open(path, 'r', errors='replace') as fp:
                    content = fp.read()
                chars = len(content)
                words = len(content.split())
                lyrics_files.append({
                    'path': os.path.relpath(path, '/app/catalog'),
                    'chars': chars,
                    'words': words
                })
                total_chars += chars
                total_words += words
            except:
                pass

# Token estimation: ~4 chars per token for English text
est_tokens = total_chars // 4

# Claude context window: 200K tokens
# Safe working budget: ~150K tokens (leave room for system prompt + response)
CONTEXT_LIMIT = 150000

print(f'BATCH_OK')
print(f'  Lyrics files found: {len(lyrics_files)}')
print(f'  Total characters:   {total_chars:,}')
print(f'  Total words:        {total_words:,}')
print(f'  Estimated tokens:   {est_tokens:,}')
print(f'  Context budget:     {CONTEXT_LIMIT:,} tokens')
print(f'')

if est_tokens <= CONTEXT_LIMIT:
    print(f'  VERDICT: ✅ ALL LYRICS FIT IN ONE PASS')
    print(f'  Headroom: {CONTEXT_LIMIT - est_tokens:,} tokens remaining')
else:
    batch_count = (est_tokens // CONTEXT_LIMIT) + 1
    songs_per_batch = len(lyrics_files) // batch_count
    print(f'  VERDICT: ⚠️  BATCHING REQUIRED')
    print(f'  Overflow: {est_tokens - CONTEXT_LIMIT:,} tokens over budget')
    print(f'  Recommended batches: {batch_count}')
    print(f'  Songs per batch: ~{songs_per_batch}')

# Size distribution
if lyrics_files:
    sizes = sorted([lf['chars'] for lf in lyrics_files])
    avg = sum(sizes) // len(sizes)
    median = sizes[len(sizes)//2]
    smallest = sizes[0]
    largest = sizes[-1]

    print(f'')
    print(f'  Size distribution:')
    print(f'    Smallest: {smallest:,} chars')
    print(f'    Median:   {median:,} chars')
    print(f'    Average:  {avg:,} chars')
    print(f'    Largest:  {largest:,} chars')

    # Top 5 largest
    top5 = sorted(lyrics_files, key=lambda x: x['chars'], reverse=True)[:5]
    print(f'')
    print(f'  Largest 5 files:')
    for lf in top5:
        print(f'    {lf[\"path\"]:60s} {lf[\"chars\"]:>6,} chars')
" 2>&1)

if echo "$BATCH_ANALYSIS" | grep -q "BATCH_OK"; then
  report "PASS" "Batch analysis complete"
  echo "$BATCH_ANALYSIS" | grep -v "BATCH_OK"
else
  report "FAIL" "Batch analysis error"
  echo "$BATCH_ANALYSIS"
fi

#──────────────────────────────────────────────────────────
# TEST 5: Dockerfile ENV audit
#──────────────────────────────────────────────────────────
echo ""
echo "── TEST 5: Dockerfile Environment Variable Audit ──"

DOCKERFILE="$RS/Dockerfile.vinnie"
if [ -f "$DOCKERFILE" ]; then
  ENV_COUNT=$(grep -c "^ENV " "$DOCKERFILE" 2>/dev/null || echo "0")
  ARG_COUNT=$(grep -c "^ARG " "$DOCKERFILE" 2>/dev/null || echo "0")
  EXPOSE_COUNT=$(grep -c "^EXPOSE " "$DOCKERFILE" 2>/dev/null || echo "0")

  echo "  ENV directives:    $ENV_COUNT"
  echo "  ARG directives:    $ARG_COUNT"
  echo "  EXPOSE directives: $EXPOSE_COUNT"

  if [ "$ENV_COUNT" -eq 0 ]; then
    echo "  ⚠️  No ENV directives — API keys must be passed at runtime"
    echo "     Runtime fix: docker run -e OPENAI_API_KEY=sk-... vinnie-agent"
    report "PASS" "Dockerfile clean (no baked secrets) — runtime ENV needed"
  else
    report "PASS" "Dockerfile has $ENV_COUNT environment variable(s)"
  fi
else
  report "FAIL" "Dockerfile.vinnie not found"
fi

#──────────────────────────────────────────────────────────
# FINAL REPORT
#──────────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════════"
echo " CLINICAL SELF-AUDIT RESULTS"
echo "═══════════════════════════════════════════════════════"
echo "  Diagnostics passed: $PASS"
echo "  Diagnostics failed: $FAIL"
echo ""

if [ "$FAIL" -eq 0 ]; then
  echo "  🩺 Dr. Vinnie's Diagnosis: HEALTHY"
  echo ""
  echo "  'The patient — that's me — is in excellent shape."
  echo "   I can see the music, read the manifests, and"
  echo "   my instruments (scripts) are all calibrated.'"
else
  echo "  🩺 Dr. Vinnie's Diagnosis: NEEDS TREATMENT"
  echo "   $FAIL issue(s) require attention."
fi
echo "═══════════════════════════════════════════════════════"
