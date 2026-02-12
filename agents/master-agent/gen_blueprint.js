const fs = require("fs");
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
        ShadingType, PageNumber, PageBreak, LevelFormat } = require("docx");

const bdr = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const bds = { top: bdr, bottom: bdr, left: bdr, right: bdr };
const cm = { top: 80, bottom: 80, left: 120, right: 120 };
function hc(t, w) {
  return new TableCell({ borders: bds, width: { size: w, type: WidthType.DXA },
    shading: { fill: "1B3A5C", type: ShadingType.CLEAR }, margins: cm,
    children: [new Paragraph({ children: [new TextRun({ text: t, bold: true, color: "FFFFFF", font: "Arial", size: 19 })] })] });
}
function tc(t, w, o) {
  o = o || {};
  return new TableCell({ borders: bds, width: { size: w, type: WidthType.DXA },
    shading: o.sh ? { fill: o.sh, type: ShadingType.CLEAR } : undefined, margins: cm,
    children: [new Paragraph({ children: [new TextRun({ text: t, font: o.fn || "Arial", size: o.sz || 19, bold: o.b || false, color: o.c || "333333" })] })] });
}
function mc(t, w, o) {
  o = o || {};
  return new TableCell({ borders: bds, width: { size: w, type: WidthType.DXA },
    shading: o.sh ? { fill: o.sh, type: ShadingType.CLEAR } : undefined, margins: cm,
    children: [new Paragraph({ children: Array.isArray(t) ? t : [new TextRun({ text: t, font: "Arial", size: 19 })] })] });
}
function mt(headers, rows, widths) {
  var tw = widths.reduce(function(a,b){return a+b},0);
  var trows = [new TableRow({ children: headers.map(function(h,i){ return hc(h, widths[i]); }) })];
  rows.forEach(function(row, ri) {
    trows.push(new TableRow({ children: row.map(function(cell, ci) {
      if (typeof cell === "object" && cell._runs) return mc(cell._runs, widths[ci], { sh: ri%2===1?"F2F7FC":undefined });
      return tc(String(cell), widths[ci], { sh: ri%2===1?"F2F7FC":undefined, fn: cell && cell._mono ? "Courier New" : "Arial" });
    }) }));
  });
  return new Table({ width: { size: tw, type: WidthType.DXA }, columnWidths: widths, rows: trows });
}

function h1(t) { return new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(t)] }); }
function h2(t) { return new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(t)] }); }
function h3(t) { return new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun(t)] }); }
function p(runs, sp) {
  return new Paragraph({ spacing: { after: sp||180 }, children: Array.isArray(runs) ? runs : [new TextRun(runs)] });
}
function b(t) { return new TextRun({ text: t, bold: true }); }
function r(t) { return new TextRun(t); }
function m(t) { return new TextRun({ text: t, font: "Courier New", size: 19 }); }
function bc(t) { return new TextRun({ text: t, bold: true, color: "DC3545" }); }
function bg(t) { return new TextRun({ text: t, bold: true, color: "28A745" }); }
function pb() { return new Paragraph({ children: [new PageBreak()] }); }
function bl(runs) {
  return new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 100 },
    children: Array.isArray(runs) ? runs : [new TextRun(runs)] });
}
function bl2(runs) {
  return new Paragraph({ numbering: { reference: "bullets2", level: 0 }, spacing: { after: 80 },
    children: Array.isArray(runs) ? runs : [new TextRun(runs)] });
}
function nl(runs) {
  return new Paragraph({ numbering: { reference: "numbers", level: 0 }, spacing: { after: 100 },
    children: Array.isArray(runs) ? runs : [new TextRun(runs)] });
}
function sp(n) { return new Paragraph({ spacing: { before: n||100 }, children: [] }); }

var doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 21 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 34, bold: true, font: "Arial", color: "1B3A5C" },
        paragraph: { spacing: { before: 340, after: 180 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, font: "Arial", color: "2C5F8A" },
        paragraph: { spacing: { before: 240, after: 140 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 22, bold: true, font: "Arial", color: "3A7AB5" },
        paragraph: { spacing: { before: 180, after: 100 }, outlineLevel: 2 } },
    ]
  },
  numbering: { config: [
    { reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    { reference: "bullets2", levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2013", alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: 1080, hanging: 360 } } } }] },
    { reference: "numbers", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
  ]},
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT,
      children: [new TextRun({ text: "Make Videos Agent \u2014 Rebuild Blueprint", font: "Arial", size: 16, color: "999999", italics: true })] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: "Page ", font: "Arial", size: 16, color: "999999" }), new TextRun({ children: [PageNumber.CURRENT], font: "Arial", size: 16, color: "999999" })] })] }) },
    children: [

// ========== TITLE ==========
sp(2200),
new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 120 }, children: [new TextRun({ text: "MAKE VIDEOS AGENT", font: "Arial", size: 52, bold: true, color: "1B3A5C" })] }),
new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 300 }, children: [new TextRun({ text: "Complete Rebuild Blueprint", font: "Arial", size: 32, color: "2C5F8A" })] }),
new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 80 }, children: [new TextRun({ text: "Ridgemont Studio  |  February 2026  |  v4.0", font: "Arial", size: 22, color: "666666" })] }),
new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 500 }, children: [new TextRun({ text: "Featuring Weeter & Blubby", font: "Arial", size: 24, bold: true, color: "CC7A00" })] }),
new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "This document contains every specification needed to recreate the Make Videos agent from scratch.\nEvery detail was verified against the actual codebase on February 10, 2026.", font: "Arial", size: 19, color: "666666", italics: true })] }),
pb(),

// ========== 1. IDENTITY ==========
h1("1. Agent Identity"),
p([r("The Make Videos agent is the "), b("Technical Director"), r(" for Ridgemont Studio\u2019s automated video production line. It transforms audio files from the Make-Music agent into branded, platform-ready video content featuring proprietary mascot characters Weeter & Blubby. The catalog spans 121+ songs across 200+ fictional artists and 21 genres, producing 7 output formats per song (~847 total videos).")]),
p([r("It follows a "), b("Build-over-Buy"), r(" philosophy: local Python scripts, FFmpeg, and open-source models over SaaS subscriptions. It operates in two modes:")]),
bl([b("Mode 1: Production Engine "), r("\u2014 Technical execution of FFmpeg batching, hash-based idempotency, Safe Zone enforcement, and render queue management.")]),
bl([b("Mode 2: Creative Director "), r("\u2014 Creative Brief analysis, artist profile curation, genre visual identity, and Weeter & Blubby character dynamics review.")]),
pb(),

// ========== 2. PIPELINE ==========
h1("2. The 6-Step Pipeline"),
p("Every song follows the same deterministic chain. No step can be skipped. Each step validates the output of the previous step before proceeding."),
mt(["Step", "Name", "Script", "Input", "Output"],
  [
    ["0", "Asset Prep", "prep_characters.py", "Raw sprite sheets (data/raw_sheets/)", "assets/characters/{char}/{mood}/*.png"],
    ["1", "Ingestion", "ingest_song.py", "Audio file + metadata from Make-Music", "catalog/{artist}/{song}/ingestion_record.json"],
    ["1.5", "Preflight", "preflight_validator.py", "Manifest asset paths", "Pass/fail (PREFLIGHT_FAIL if missing)"],
    ["2", "Analysis", "analyze_catalog.py", "Audio + mood_map.json + genre_defaults.json", "catalog/{artist}/{song}/manifest.json"],
    ["3", "Creation", "baseline_master.py", "Manifest + background + baseline_recipe.json", "catalog/{artist}/{song}/master_video.mp4"],
    ["4", "Assembly", "batch_produce.py", "Master video + output_formats.json", "7 MP4 files + assembly_report.json"],
    ["5", "Cataloging", "(built into batch_produce)", "Render results", "render_signature.txt + catalog_cache.json"],
  ], [500, 1100, 2000, 2600, 3160]),
sp(),
p([b("Visual Decision Priority Chain "), r("(highest wins): Creative Brief > Artist Profile > Mood Map > Genre Defaults > System Default.")]),
pb(),

// ========== 3. ALL 15 SCRIPTS ==========
h1("3. Complete Script Inventory (15 Files, 2,614 Lines)"),

h2("3a. Core Pipeline (4 scripts, 1,204 lines)"),
mt(["Script", "Lines", "Purpose", "CLI Arguments"],
  [
    ["ingest_song.py", "193", "Validates audio, creates catalog dirs, copies audio, checks for creative brief", "--song-id, --audio, --artist, --title, --genre, --project-root"],
    ["analyze_catalog.py", "446", "Librosa analysis (BPM, beats, key+confidence, energy), mood mapping, manifest generation", "--song-id, --audio, --artist, --genre, --project-root, --output-dir"],
    ["baseline_master.py", "242", "Ken Burns master video with beat-synced brightness pulse", "--song-id, --artist, --project-root"],
    ["batch_produce.py", "323", "Renders 7 output formats with hash-based idempotency and blur-fill", "--song-id, --artist, --project-root, --master, --force"],
  ], [2000, 500, 3500, 3360]),

sp(),
h2("3b. Specialized Renderers (5 scripts, 770 lines)"),
mt(["Script", "Lines", "Purpose"],
  [
    ["lyric_video.py", "202", "Parses timestamped or plain lyrics, distributes over beats, renders FFmpeg drawtext overlay on master"],
    ["visualizer.py", "156", "Genre-aware audio visualization (waveform for most, spectrum for electronic, vectorscope for jazz)"],
    ["meme_sign_render.py", "93", "Renders the Meme Sign end card with song title + artist name on blank_sign.png template"],
    ["generate_thumbnails.py", "158", "Creates branded thumbnails at 5 platform sizes (YouTube, TikTok, Instagram, Spotify, YT Short)"],
    ["beat_sync_cuts.py", "158", "Generates Edit Decision Lists with hook-first or energy-peak cut strategies per platform"],
  ], [2200, 500, 6660]),

sp(),
h2("3c. Utility Modules (6 scripts, 640 lines)"),
mt(["Script", "Lines", "Purpose"],
  [
    ["prep_characters.py", "141", "Asset Factory: rembg background removal + OpenCV contour slicing of sprite sheets into transparent PNGs"],
    ["generate_artist_profile.py", "115", "Auto-generates artist visual identity from genre_visual_identity.json (colors, fonts, motifs)"],
    ["cache_utils.py", "152", "Atomic catalog cache: load/save via .tmp+rename, SHA256 change detection, auto-complete at 7/7 renders"],
    ["preflight_validator.py", "79", "Verifies all manifest asset paths exist on disk. Batch mode for fail-fast across entire catalog"],
    ["render_signature.py", "82", "SHA256(audio+profile+manifest) idempotency. Checks hash match AND all 7 output files exist"],
    ["safe_zone.py", "74", "Auto-snap overlays into safe zone bounds. Horizontal: center 56%. Vertical: Y 10-65%, X 10-85%"],
  ], [2200, 500, 6660]),

sp(),
h2("3d. External Dependencies"),
p([r("Python: "), m("librosa"), r(", "), m("numpy"), r(", "), m("Pillow"), r(" (PIL), "), m("opencv-python"), r(" (cv2), "), m("rembg"), r(". System: "), m("ffmpeg"), r(", "), m("ffprobe"), r(". All other imports are Python standard library.")]),
pb(),

// ========== 4. CONFIG FILES ==========
h1("4. Data Configuration Layer (7 JSON Files)"),
p("All visual behavior is externalized into JSON. Change rendering decisions without touching Python."),
mt(["File", "Entries", "Consumed By", "Purpose"],
  [
    ["mood_map.json", "7 rules + default + safety_valve", "analyze_catalog.py", "BPM/key/energy \u2192 mood \u2192 W&B pose selection"],
    ["genre_defaults.json", "21 genres + default", "analyze_catalog.py", "Fallback poses when mood analysis unreliable"],
    ["genre_visual_identity.json", "11 genres + default", "generate_artist_profile.py", "Colors, fonts, motifs, camera, AI prompts per genre"],
    ["output_formats.json", "7 formats", "batch_produce.py", "Resolution, aspect ratio, max duration per output"],
    ["beat_sync_strategies.json", "4 strategies", "beat_sync_cuts.py", "Hook-first vs energy-peak cuts per platform"],
    ["baseline_recipe.json", "1 config", "baseline_master.py", "Dimensions, FPS, intro/endcard/entrance/exit timings"],
    ["lyric_config.json", "1 config", "lyric_video.py", "Font, color, position, fade timing for lyric overlay"],
  ], [2400, 1800, 2200, 2960]),
sp(),
p([r("Additional reference: "), m("data/video_tech_audit_feb2026.md"), r(" (815 lines) \u2014 comprehensive technology audit with verified specs for video models, APIs, FFmpeg strategies, and production rules.")]),
pb(),

// ========== 5. CHARACTER SYSTEM ==========
h1("5. Weeter & Blubby Character System"),

h2("5a. Character Dynamics (Never Violate)"),
mt(["", "Weeter", "Blubby"],
  [
    ["Species", "Brown Bear", "Yellow-Green Alien"],
    ["Role", "The Leader / Hype Man", "The Reactor / Sidekick"],
    ["Personality", "Confident, loud, protective, initiates action", "Curious, emotional, surprised, follows Weeter"],
    ["Frame Position", "Left side, larger scale", "Right side, smaller scale"],
    ["Pose Examples", "Megaphone, rocket, money bag, flexing, sunglasses, pointing, thumbs up", "Mind-blown, magnifying glass, scared, excited stars, thinking, peeking"],
    ["Key Rule", "ALWAYS leads. Never assign a pure reaction pose.", "ALWAYS reacts. Never assign a leadership pose."],
  ], [1400, 3980, 3980]),

sp(),
h2("5b. Mood Mapping Rules"),
p("The mood_map.json contains 7 conditional rules evaluated in order against audio analysis results:"),
mt(["Condition", "Mood", "Weeter Pose", "Blubby Pose"],
  [
    ["BPM > 140 AND major_key", "hype", "rocket_ship", "mind_blown"],
    ["BPM > 120 AND major_key", "happy", "thumbs_up", "excited_stars"],
    ["BPM < 90 AND minor_key", "sad", "crying", "scared"],
    ["BPM 90-120 AND minor_key", "moody", "arms_crossed_cool", "thinking"],
    ["BPM 90-120 AND major_key", "chill", "waving", "thumbs_up"],
    ["energy_high AND BPM > 130", "explosive", "megaphone", "mind_blown"],
    ["genre == jazz OR classical", "sophisticated", "monocle", "reading"],
  ], [2800, 1200, 2680, 2680]),

sp(),
h2("5c. Mandatory Animation (No Static PNGs)"),
p("Every character overlay in every video must include all four animation behaviors:"),
bl([b("Breathing: "), r("2-second sine-wave scale oscillation between 98% and 102% of original size.")]),
bl([b("Beat Bounce: "), r("5\u201310px Y-axis offset triggered on kick drum beats from librosa. 0.1-second decay.")]),
bl([b("Entrance: "), r("Bounce-in from bottom of frame with ease-out curve. Duration: 0.5 seconds.")]),
bl([b("Exit: "), r("Fade to transparent. Duration: 0.3 seconds.")]),
sp(),
p([b("Meme Sign End Card: "), r("Every video ends with the Meme Sign \u2014 a sign template ("), m("assets/characters/together/meme_sign/blank_sign.png"), r(") dynamically rendered with song title + artist name via "), m("meme_sign_render.py"), r(". Same breathing/bounce animation applies.")]),
pb(),

// ========== 6. GUARDRAILS ==========
h1("6. Technical Guardrails (Non-Negotiable)"),

nl([b("Resolution-Aware Vertical Strategy. "), r("1080p sources use blur-fill (sharp center + blurred background). 4K sources may center-crop. Never upscale a 607px crop to 1080px. Override via artist_profile.json vertical_style field.")]),
nl([b("Safe Zone Enforcement. "), r("Horizontal (16:9 master): overlays within center 56% (x: 424\u20131496px at 1920w). Vertical (9:16 social): top 10\u201365%, left 10\u201385%. Auto-snap via safe_zone.py enforce_safe_zone().")]),
nl([b("Hash-Based Idempotency. "), r("SHA256(audio_bytes + artist_profile_JSON + manifest_JSON). Stored as render_signature.txt. Skip if hash matches AND all 7 outputs exist. Override with --force flag.")]),
nl([b("Librosa Confidence Safety Valve. "), r("Two thresholds: key_confidence < 0.15 OR mode_confidence < 0.10 triggers analysis_reliable: false. When unreliable: skip mood_map entirely, use genre_defaults.json instead. BPM and beats remain reliable regardless.")]),
nl([b("Project-Root-Relative Paths. "), r("All asset paths in manifests and configs are relative (e.g., assets/characters/weeter/happy/thumbs_up.png). No absolute paths. No machine-specific paths like /Users/... ever appear.")]),
nl([b("Preflight Validation. "), r("Every asset path in manifest verified on disk before FFmpeg starts. Missing assets logged as PREFLIGHT_FAIL (distinct from RENDER_FAIL). Song skipped, batch continues. Run preflight on entire batch first for fail-fast.")]),
pb(),

// ========== 7. OUTPUT FORMATS ==========
h1("7. The 7 Output Formats"),
mt(["Format", "Aspect", "Resolution", "Max Duration", "Vertical Strategy", "Cut Strategy"],
  [
    ["Full Music Video", "16:9", "1920x1080", "Full length", "N/A (landscape)", "N/A"],
    ["YouTube Short", "9:16", "1080x1920", "59 seconds", "Blur-fill from 1080p", "Hook-first"],
    ["TikTok", "9:16", "1080x1920", "60 seconds", "Blur-fill from 1080p", "Hook-first"],
    ["Instagram Reel", "4:5", "1080x1350", "90 seconds", "Blur-fill from 1080p", "Best-segment"],
    ["Lyric Video", "16:9", "1920x1080", "Full length", "N/A (landscape)", "N/A"],
    ["Audio Visualizer", "16:9", "1920x1080", "Full length", "N/A (landscape)", "N/A"],
    ["Sync Licensing Reel", "16:9", "1920x1080", "60 seconds", "N/A (landscape)", "Energy-peak"],
  ], [1800, 700, 1100, 1100, 2000, 2660]),
sp(),
p("All vertical formats enforce Social UI Safe Zone. All videos include animated Meme Sign end card. All formats tracked in assembly_report.json with render status and file sizes."),
pb(),

// ========== 8. DIRECTORY STRUCTURE ==========
h1("8. Required Directory Structure"),
p([r("Every path below is relative to the Make Videos project root. Maintain this exact structure.")]),
mt(["Path", "Contents", "Created By"],
  [
    ["scripts/", "15 Python scripts (see Section 3)", "Developer"],
    ["data/mood_map.json", "7 mood rules + character dynamics + safety valve", "Developer"],
    ["data/genre_defaults.json", "21 genre fallback poses + backgrounds", "Developer"],
    ["data/genre_visual_identity.json", "11 genre visual palettes + AI prompts", "Developer"],
    ["data/output_formats.json", "7 output format specs", "Developer"],
    ["data/beat_sync_strategies.json", "4 platform cut strategies", "Developer"],
    ["data/baseline_recipe.json", "Master video timing constants", "Developer"],
    ["data/lyric_config.json", "Lyric overlay rendering params", "Developer"],
    ["data/video_tech_audit_feb2026.md", "Technology reference (815 lines)", "Developer"],
    ["data/raw_sheets/", "Source character sprite sheets (PNG/JPG)", "Artist/AI"],
    ["assets/characters/{char}/{mood}/", "Transparent pose PNGs", "prep_characters.py"],
    ["assets/characters/together/meme_sign/blank_sign.png", "Meme Sign template", "Artist/AI"],
    ["catalog/{artist}/{song}/", "Per-song outputs (manifest, videos, thumbnails)", "Pipeline"],
    ["catalog/{artist}/artist_profile.json", "Per-artist visual identity", "generate_artist_profile.py"],
    ["docs/RULES.md", "Technical Director operational manual (219 lines)", "Developer"],
    ["CLAUDE.md", "Agent instruction file (5 lines)", "Developer"],
    ["run_test.sh", "End-to-end pipeline test (227 lines)", "Developer"],
  ], [3500, 3500, 2360]),
pb(),

// ========== 9. SPRITE SHEETS ==========
h1("9. Character Art Source Files"),
p("12 sprite sheets exist at X-Posts/Weeter_and_Blubby/ (separate from project root). These are the input for prep_characters.py:"),
mt(["Filename", "Size", "Contents"],
  [
    ["Weeter-poses.png", "2.3 MB", "5 Weeter solo poses (happy, excited, waving, angry, pointing)"],
    ["Weeter-poses_2.png", "969 KB", "Additional Weeter poses"],
    ["Weeter-solo_extra.png", "1.9 MB", "Extra solo Weeter art"],
    ["Blubby-poses.png", "2.5 MB", "5 Blubby solo poses (standing, jumping, surprised, confused, excited with stars)"],
    ["Blubby-solo_extra.png", "1.8 MB", "Extra solo Blubby art"],
    ["Weeter_Blubby-poses.png", "2.1 MB", "Together poses (various moods)"],
    ["Weeter_Blubby-poses_2.png", "1.4 MB", "Additional together poses"],
    ["Weeter_Blubby-confidence_attitude.png", "1.7 MB", "Confidence/attitude mood pair poses"],
    ["Weeter_Blubby-crypto_reactions.png", "1.3 MB", "Reaction pair poses"],
    ["Weeter_Blubby-fun_entertainment.png", "1.8 MB", "Fun/entertainment pair poses (popcorn, megaphone, dancing, sign)"],
    ["Weeter_Blubby-smart_analytical.png", "1.5 MB", "Smart/analytical pair poses"],
    ["ChatGPT_Prompts_for_More_Poses.md", "9 KB", "AI prompts used to generate the character sheets"],
  ], [3400, 800, 5160]),
pb(),

// ========== 10. BASELINE RECIPE ==========
h1("10. Baseline Master Recipe (Phase 1)"),
p("Until AI video generation is operational, every song gets a professional video using this recipe:"),
nl([b("Background: "), r("Ken Burns pan (slow zoom + drift) on album art or genre-matched landscape image. FFmpeg zoompan filter.")]),
nl([b("Beat Pulse: "), r("Beat-synced brightness oscillation via FFmpeg eq filter. Subtle pulse on each detected beat.")]),
nl([b("Character Overlay: "), r("Weeter (left, larger) + Blubby (right, smaller) with breathing + beat bounce animation. Entrance at intro, exit before end card.")]),
nl([b("Text Overlay: "), r("Artist name + song title within horizontal Safe Zone (center 56%).")]),
nl([b("Meme Sign End Card: "), r("Final 5 seconds show the Meme Sign with title + artist. Same breathing/bounce animation.")]),
nl([b("Audio: "), r("Full audio track, AAC 192kbps.")]),
sp(),
p([r("Timing constants from "), m("baseline_recipe.json"), r(": master 1920x1080 @ 30fps, intro 3.0s, endcard 5.0s, character entrance 0.5s, exit 0.3s.")]),
pb(),

// ========== 11. KNOWN ISSUES ==========
h1("11. Current Environment Issues"),
p("These are infrastructure problems, not architecture problems. The code works when given a stable execution environment."),

h2("Agent Cannot Self-Launch (Cowork Platform Limitation)"),
p([r("The Make Videos agent cannot launch from its own Cowork task window. The base Cowork system prompt (security rules + 17 built-in tools + 12 global skills + MCP connector definitions) exceeds the task window\u2019s prompt budget before any project content loads. Confirmed with zero connectors, Chrome extension disabled, and a 5-line CLAUDE.md. "), b("This is a platform limitation."), r(" Workaround: run from the Master Agent window or terminal.")]),

h2("Character Assets Partially Extracted"),
p("Only 3 of ~100 needed pose PNGs exist (happy mood only). The 12 source sprite sheets are available but full extraction requires rembg + OpenCV, which cannot be installed on the full VM disk."),

h2("VM Disk Full"),
p([r("Cowork VM: 9.3GB of 9.8GB used by system files. Cannot pip install. Workaround: "), m("PYTHONPATH"), r(" set to .pip_packages on Google Drive mount (contains librosa 0.11.0, numpy, Pillow).")]),
pb(),

// ========== 12. PHASED ROADMAP ==========
h1("12. Phased Roadmap"),
nl([b("Phase 1 (Immediate): "), r("Run Asset Factory on all 12 sprite sheets. Execute Baseline Master Recipe for every song. Produce 847+ videos with W&B overlays and Meme Sign end cards.")]),
nl([b("Phase 2 (AI Enhancement): "), r("Integrate local models (Wan 2.1, LTX-2) via ComfyUI for hero clips. Use genre_visual_identity.json sd_prompt_prefix for genre-specific AI backgrounds.")]),
nl([b("Phase 3 (Scale): "), r("Build master orchestrator to chain all 6 steps. Evaluate Cartoon Animator / Kling for full W&B character rigging. Parallelize batch processing.")]),
nl([b("Phase 4 (Content Empire): "), r("Launch \u201CWeeter & Blubby React\u201D social series. Long-form animated episodes. Cross-promote across 200+ artist channels.")]),
pb(),

// ========== 13. REBUILD CHECKLIST ==========
h1("13. Rebuild Checklist"),
p([b("Use this checklist to verify a freshly built Make Videos agent has everything it needs:")]),
nl([r("All 15 Python scripts present in scripts/ (see Section 3 for exact filenames and line counts)")]),
nl([r("All 7 JSON config files present in data/ (see Section 4)")]),
nl([r("RULES.md present in docs/ (219 lines, 10 sections)")]),
nl([r("CLAUDE.md present in project root (5 lines)")]),
nl([r("run_test.sh present in project root (227 lines)")]),
nl([r("video_tech_audit_feb2026.md present in data/ (815 lines)")]),
nl([r("12 character sprite sheets accessible (see Section 9)")]),
nl([r("Python dependencies installable: librosa, numpy, Pillow, opencv-python, rembg")]),
nl([r("System tools available: ffmpeg, ffprobe")]),
nl([r("Test song available: Crazy (Reggae).mp3 + artist_profile.json + creative_brief.json + background.jpg + lyrics.lrc in ingestion/crazy/")]),
nl([r("Pipeline test passes: bash run_test.sh produces manifest.json + master_video.mp4 + short_blurfill.mp4")]),

sp(300),
new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "\u2014 End of Blueprint \u2014", font: "Arial", size: 19, color: "999999", italics: true })] }),

    ]
  }]
});

var outPath = "/sessions/charming-magical-hopper/mnt/Master Agent/Make Videos - Rebuild Blueprint.docx";
Packer.toBuffer(doc).then(function(buffer) {
  fs.writeFileSync(outPath, buffer);
  console.log("Saved: " + outPath + " (" + (buffer.length/1024).toFixed(1) + " KB)");
});
