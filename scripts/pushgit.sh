#!/bin/bash
# Ridgemont Catalog Sync Script
# Syncs catalog.json to all three Streamlit portals

BASE="/Users/johnyork/My Drive/Ridgemont Studio/Claude Cowork"

echo "Syncing Ridgemont Catalog Manager..."
cd "$BASE/Ridgemont Catalog Manager" && git add -A && git commit -m "Sync catalog" && git push

echo "Copying catalog to Frozen Cloud Portal..."
cp "$BASE/Ridgemont Catalog Manager/data/catalog.json" "$BASE/frozen-cloud-portal/data/"
cd "$BASE/frozen-cloud-portal" && git add -A && git commit -m "Sync catalog" && git push

echo "Copying catalog to Park Bellevue Portal..."
cp "$BASE/Ridgemont Catalog Manager/data/catalog.json" "$BASE/park-bellevue-portal/data/"
cd "$BASE/park-bellevue-portal" && git add -A && git commit -m "Sync catalog" && git push

echo "Done! All portals synced."
