---
name: pushgit
description: Push Ridgemont catalog updates to GitHub. Use this skill whenever the user types "pushgit" or asks to push/sync the catalog to GitHub or Streamlit portals.
---

# Pushgit - Ridgemont Catalog Sync

When the user triggers this skill, output the following command for them to copy and run in their Mac terminal:

```bash
cd "/Users/johnyork/My Drive/Ridgemont Studio/Claude Cowork/Ridgemont Catalog Manager" && git add -A && git commit -m "Sync catalog" && git push && cp "/Users/johnyork/My Drive/Ridgemont Studio/Claude Cowork/Ridgemont Catalog Manager/data/catalog.json" "/Users/johnyork/My Drive/Ridgemont Studio/Claude Cowork/frozen-cloud-portal/data/" && cd "/Users/johnyork/My Drive/Ridgemont Studio/Claude Cowork/frozen-cloud-portal" && git add -A && git commit -m "Sync catalog" && git push && cp "/Users/johnyork/My Drive/Ridgemont Studio/Claude Cowork/Ridgemont Catalog Manager/data/catalog.json" "/Users/johnyork/My Drive/Ridgemont Studio/Claude Cowork/park-bellevue-portal/data/" && cd "/Users/johnyork/My Drive/Ridgemont Studio/Claude Cowork/park-bellevue-portal" && git add -A && git commit -m "Sync catalog" && git push
```

Or remind them they can just type `pushgit` in their Mac terminal if they set up the alias.

This syncs:
1. Ridgemont Catalog Manager (main) → GitHub
2. Copies catalog.json to frozen-cloud-portal → GitHub
3. Copies catalog.json to park-bellevue-portal → GitHub

All three Streamlit apps will auto-deploy after the push.
