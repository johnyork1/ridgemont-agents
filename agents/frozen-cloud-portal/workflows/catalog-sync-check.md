# Catalog Sync Validation Workflow

**Trigger:** Run manually or after any catalog update to verify data consistency

---

## Steps

### 1. Load Both Sources
- Read `data/catalog.json` (this portal's local copy)
- Read `../Ridgemont Catalog Manager/data/catalog.json` (source of truth)

### 2. Compare Song Counts
- Count total songs in each file
- If mismatch: flag as SYNC ERROR with exact delta

### 3. Compare Song Records
For each song in the source catalog:
- Verify it exists in the portal copy (match by song ID or title + act)
- Compare key fields: title, act, status, writers, copyright_number
- Flag any field mismatches as DRIFT warnings

### 4. Check for Orphaned Records
- Identify any songs in the portal copy that don't exist in the source
- These indicate deleted or renamed songs that didn't propagate

### 5. Validation Output
```
CATALOG SYNC REPORT
─────────────────────
Source (Catalog Manager): XX songs
Portal (Local Copy):     XX songs
Status: ✅ IN SYNC / ⚠️ DRIFT DETECTED / ❌ OUT OF SYNC

Mismatches: [list any field-level diffs]
Orphans: [list any portal-only records]
Action: [Run catalog-sync to fix / Manual review needed]
```

### 6. Auto-Fix (if authorized)
- If simple count mismatch, copy source catalog.json to portal
- If field drift, copy source catalog.json to portal (source is always authoritative)
- Log the sync action with timestamp

---

## Data Flow
```
Ridgemont Catalog Manager/data/catalog.json (SOURCE OF TRUTH)
         ↓ catalog-sync skill
frozen-cloud-portal/data/catalog.json (READ-ONLY COPY)
```
