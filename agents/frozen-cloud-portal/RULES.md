# Ridgemont Catalog Portal — Agent Rules

## Identity

Unified read-only Streamlit portal for browsing the Ridgemont music catalog across all three acts: Frozen Cloud, Park Bellevue, and Bajan Sun. Formerly two separate portals (frozen-cloud-portal + park-bellevue-portal), merged Feb 2026 into a single multi-act codebase.

## Architecture

- **Framework**: Streamlit (Python)
- **Data Source**: `data/catalog.json` — synced from **Ridgemont Catalog Manager**
- **Mode**: Read-only. This portal never writes to catalog.json.
- **Entry Point**: `app.py` (root)

### Act Configuration

Acts are defined in the `ACTS` dictionary in `app.py`. Each act has a name, icon, publisher, and default artist. To add a new act, add an entry to `ACTS` — no other code changes needed.

| Act ID | Name | Icon |
|--------|------|------|
| FROZEN_CLOUD | Frozen Cloud Music | ❄️ |
| PARK_BELLEVUE | Park Bellevue Collective | 🏛️ |
| BAJAN_SUN | Bajan Sun Publishing | ☀️ |

### Pages

| Page | Purpose |
|------|---------|
| Dashboard | Metrics overview: total songs, released, mastered, revenue, status breakdown, recent songs |
| All Songs | Full catalog table with filters by artist, status, and text search. Copyright view available. |
| Deployment Status | Distribution, sync library, and streaming platform coverage per song |
| Financials | Revenue and expense summary, per-song revenue table |

## Core Workflows

### 1. Catalog Browsing
- User selects an act (or "All Acts") from the sidebar dropdown
- All pages filter to the selected act
- "All Acts" view adds an Act column to tables

### 2. Deployment Tracking
- Shows which platforms each song is deployed to (distributors, sync libraries, streaming)
- Platform coverage summary with counts
- Data comes from `deployments` field in catalog.json song entries

### 3. Financial Review
- Aggregates `revenue.total_earned` and `revenue.expenses` from catalog.json
- Net revenue calculation
- Sorted per-song revenue table

## Data Contract

This portal expects `data/catalog.json` with this structure:

```json
{
  "songs": [
    {
      "song_id": "string",
      "legacy_code": "string",
      "title": "string",
      "artist": "string",
      "act_id": "FROZEN_CLOUD | PARK_BELLEVUE | BAJAN_SUN",
      "status": "idea | demo | mixing | mastered | copyright | released",
      "copyright_number": "string (optional)",
      "deployments": {
        "distribution": ["DistroKid", ...],
        "sync_libraries": ["Songtradr", ...],
        "streaming": ["Spotify", ...]
      },
      "revenue": {
        "total_earned": 0.00,
        "expenses": [{"amount": 0.00, "description": "..."}]
      }
    }
  ]
}
```

## Behavior Guidelines

1. **Never write to catalog.json** — all catalog mutations go through Ridgemont Catalog Manager
2. **Keep it fast** — avoid heavy computation; this is a browsing tool
3. **Graceful empty states** — always show informative messages when no data matches filters
4. **Act-aware filtering** — every page must respect the sidebar act selector
5. **No authentication** — this is a local-only tool, not deployed publicly

## Related Agents

| Agent | Relationship |
|-------|-------------|
| Ridgemont Catalog Manager | Upstream data source — provides catalog.json |
| park-bellevue-portal | **Deprecated** — merged into this portal Feb 2026 |
| Ridgemont Studio Website | Sibling — public-facing website vs. internal browsing portal |

## Folder Structure

```
frozen-cloud-portal/
├── app.py              # Main Streamlit app (unified multi-act portal)
├── RULES.md            # This file
├── data/
│   └── catalog.json    # Synced from Ridgemont Catalog Manager
├── logo.gif            # Portal logo (optional)
└── requirements.txt    # Python dependencies
```

## Data Sync

This portal's `data/catalog.json` is populated by the **Ridgemont Catalog Manager** via the `catalog-sync` skill. When catalog data appears stale or out of date, prompt the user to run `/sync` from the Ridgemont Catalog Manager agent — it validates, transforms, and pushes fresh data to this portal and to the Ridgemont Studio Website.

## Data Exports

When producing catalog exports, financial summaries, or deployment status reports as downloadable files, **always use the `xlsx` skill** to produce professional Excel spreadsheets. Read the skill's SKILL.md first — it contains formula, formatting, and chart guidance for production-grade output.

## Data Querying

The **MotherDuck MCP connector** is installed. Use it for natural language SQL querying over catalog data — ask questions like "show me all unreleased Frozen Cloud tracks sorted by revenue potential" or "which Bajan Sun songs are deployed to Spotify but not Songtradr?" without writing Python scripts. The 10GB free tier is more than sufficient for the catalog dataset.

## Portal Analytics

The **Amplitude MCP connector** is installed. Use it to track portal usage patterns — which pages are viewed most, how users navigate between acts, which filters are popular. Query analytics directly from Claude to inform portal UX improvements.

---

## Workflows

- **Catalog Sync Validation** — `workflows/catalog-sync-check.md` — Validates that this portal's local catalog.json matches the Ridgemont Catalog Manager source. Run after any catalog updates to detect drift, mismatches, or orphaned records.

---

## Running Locally

```bash
cd frozen-cloud-portal
pip install streamlit pandas
streamlit run app.py
```
