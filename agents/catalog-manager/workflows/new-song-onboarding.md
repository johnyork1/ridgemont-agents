# New Song Onboarding Workflow

**Trigger:** User adds a new song to the catalog via `> FC New`, `> PB New`, or `> BS New`

---

## Steps

### 1. Catalog Entry (This Agent)
- Add song to `data/catalog.json` with all required fields
- Auto-backup catalog before write (10-backup rotation)
- Validate: title, act, status, writers, splits, copyright number (if available)
- Log the addition in shortcode output

### 2. Portal Sync (frozen-cloud-portal)
- Run `catalog-sync` skill to push updated catalog.json to frozen-cloud-portal/data/
- Verify the new song appears in the portal's catalog browser
- If portal has a running Streamlit instance, note it needs restart

### 3. Website Update (Ridgemont Studio Website)
- If song status is "Released" or "Mastered":
  - Update `tracks.json` with streaming URL, title, artist, album art path
  - Run `sync-music.sh` to push audio to Cloudflare R2
- If song is still in production, skip — will trigger on status change

### 4. Pitch Readiness Check
- If song has copyright number + mastered status:
  - Auto-generate pitch template: `> Pitch "[Song Title]" "[Placeholder Supervisor]"`
  - Store HTML one-sheet in `pitches/` directory
- If not ready, log as "pending pitch prep"

### 5. Confirmation Output
Print summary:
```
✅ Song Onboarded: "[Title]" ([Act])
   Catalog: Added (entry #XX)
   Portal: Synced / Pending sync
   Website: Updated / Skipped (not released)
   Pitch: Ready / Pending (needs copyright #)
```

---

## Related Agents
- **frozen-cloud-portal** — receives catalog.json updates
- **Ridgemont Studio Website** — receives tracks.json + R2 audio
- **Frozen Cloud Website** — manual update if FC act (link to new release)
- **Make-Music** — upstream source of new compositions
