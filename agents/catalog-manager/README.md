# Ridgemont Catalog Manager

Music catalog database manager for Ridgemont Studio, tracking songs across three acts: Frozen Cloud Music, Park Bellevue Collective, and Bajan Sun Publishing.

## What It Does

- CRUD operations on a JSON-based song catalog with auto-generated IDs (`RS-YYYY-NNNN`)
- Natural language queries ("show me all unreleased Frozen Cloud tracks")
- Writer split management with per-act defaults (50/50 or 100%)
- Sync licensing search by mood, genre, tempo, and use case
- Audit logging, duplicate detection, and catalog exports (JSON, CSV)
- Syncs catalog data to the frozen-cloud-portal and ridgemont-website agents

## Usage

This is a Claude agent workspace. Open the `catalog-manager/` directory in Claude Code and interact conversationally to query or update the catalog.

Key data files live in `data/` (catalog.json, writers.json, acts.json, aliases.json). Exports are saved to `exports/`.

## Requirements

- Python 3.x (for helper scripts in `scripts/`)
- Claude Code with MCP connectors (MotherDuck for SQL queries, Notion for knowledge base)

## Related Agents

- **frozen-cloud-portal** -- reads catalog.json for browsing
- **ridgemont-website** -- uses catalog data for the public streaming player
