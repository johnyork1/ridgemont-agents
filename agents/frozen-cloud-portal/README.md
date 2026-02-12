# Frozen Cloud Portal

Read-only Streamlit portal for browsing the Ridgemont music catalog across all three acts: Frozen Cloud, Park Bellevue, and Bajan Sun.

## What It Does

- Dashboard with metrics: total songs, released count, mastered count, revenue, status breakdown
- Full catalog table with filters by act, artist, status, and text search
- Deployment tracking: distribution, sync library, and streaming platform coverage per song
- Financial review: revenue/expense summaries and per-song revenue tables

## Usage

```bash
cd agents/frozen-cloud-portal
pip install -r requirements.txt
streamlit run app.py
```

Select an act from the sidebar (or "All Acts") to filter every page.

## Requirements

- Python 3.x
- Streamlit, Pandas (`pip install streamlit pandas`)
- `data/catalog.json` synced from the catalog-manager agent

## Notes

- This portal is read-only. All catalog mutations go through the catalog-manager agent.
- Formerly two separate portals (frozen-cloud-portal + park-bellevue-portal), merged Feb 2026.
