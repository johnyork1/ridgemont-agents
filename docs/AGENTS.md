# Ridgemont Studio — Agent Index

## Agents

| Agent | Directory | Type | Description |
|-------|-----------|------|-------------|
| Dr. Vinnie Boombatz | `agents/vinnie/` | Claude Desktop plugin | Medical AI consultant with 8 slash commands, 10 skills, PubMed MCP, and a medical-researcher sub-agent |
| Make Videos | `agents/make-videos/` | Claude Desktop project | Music video production pipeline (18 Python scripts) |
| Suno | `agents/suno/` | Claude Desktop project | Suno v5.0 style prompt generator |

## How to Use

Each agent is designed to be opened as a **project** in Claude Desktop:

1. **Dr. Vinnie Boombatz**: Open `agents/vinnie/` as a project. Full plugin with commands, skills, sub-agents, and MCP servers.
2. **Make Videos**: Open `agents/make-videos/` as a project. CLAUDE.md teaches Claude the full video pipeline.
3. **Suno**: Open `agents/suno/` as a project. CLAUDE.md teaches Claude the prompt generator.

## Agent Details

### Dr. Vinnie Boombatz (`agents/vinnie/`)

- **Plugin**: `.claude-plugin/plugin.json`
- **System prompt**: `CLAUDE.md`
- **Commands** (8): ai-medicine-update, differential, drug-lookup, interaction-check, interpret-labs, patient-explainer, research-review, screening
- **Skills** (10): ai-medical-advances, clinical-diagnosis, emergency-medicine, lab-interpretation, medical-imaging, medical-research, mental-health, patient-education, pharmacology, preventive-medicine
- **Sub-agents**: `sub-agents/medical-researcher.md` — PubMed literature search specialist
- **MCP**: PubMed remote server (`.mcp.json`)
- **Scripts**: `src/generate_report.py` — generates medical reports from patient notes

### Make Videos (`agents/make-videos/`)

- **System prompt**: `CLAUDE.md`
- **Scripts**: 18 Python scripts in `../../scripts/`
- **Pipeline**: ingest → analyze → render master → render shorts
- **Extras**: pro video, lyric video, visualizer, thumbnails, artist profiles, meme signs, YouTube metadata

### Suno (`agents/suno/`)

- **System prompt**: `CLAUDE.md`
- **Script**: `../../scripts/generate_prompt.py`
- **Assets**: subgenres.json, subgenre_tags.json, instruments.json
