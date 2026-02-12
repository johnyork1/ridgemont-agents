# Catalog-Sync Skill

## Overview
Synchronize catalog data from Ridgemont Catalog Manager to downstream consumers (frozen-cloud-portal and Ridgemont Studio Website), maintaining data integrity and consistency across systems.

## Trigger Command
`/sync`

## Purpose
Ensures all downstream systems always have current, validated catalog data with automatic synchronization after any catalog write operation, preventing data drift and maintaining single source of truth.

## When to Invoke
- After any catalog write operation (add, edit, delete track records)
- Manually when synchronization status is uncertain
- On a scheduled basis (recommended: after business hours or on a defined sync window)
- After a catalog data restore or migration
- When downstream systems show stale or inconsistent data

## Automatic vs Manual

**Automatic Trigger (No command needed):**
- After any CREATE operation on tracks in Ridgemont Catalog Manager
- After any UPDATE operation on tracks in Ridgemont Catalog Manager
- After any DELETE operation on tracks in Ridgemont Catalog Manager
- Automatically runs without user intervention

**Manual Trigger:**
- `/sync` command when user wants to force synchronization
- Useful for troubleshooting or emergency data reconciliation
- Should complete within 5 minutes in normal conditions

## Source of Truth

**Primary Source:** `/Ridgemont Catalog Manager/data/catalog.json`

This is the only authoritative catalog source. All other systems are consumers.

**Source File Structure:**

```json
{
  "metadata": {
    "version": "1.0",
    "lastUpdated": "2025-02-08T10:30:00Z",
    "totalTracks": 150
  },
  "tracks": [
    {
      "id": "track_001",
      "title": "Track Title",
      "artist": "Artist Name",
      "album": "Album Name",
      "duration": 180,
      "releaseDate": "2025-01-15",
      "status": "released|draft|archived",
      "genres": ["genre1", "genre2"],
      "bpm": 120,
      "key": "C Major",
      "description": "Track description",
      "url": "https://example.com/track/001",
      "thumbnail": "https://cdn.example.com/track_001.jpg",
      "credits": {
        "producer": "Producer Name",
        "engineer": "Engineer Name",
        "featuring": ["Artist 2", "Artist 3"]
      },
      "streaming": {
        "spotify": "spotify:track:xxxxx",
        "apple": "https://music.apple.com/...",
        "youtube": "https://youtu.be/xxxxx"
      }
    }
  ]
}
```

## Destination Systems

### Destination 1: frozen-cloud-portal
- **Location:** `frozen-cloud-portal/data/catalog.json`
- **Format:** Exact replica of source file
- **Purpose:** Direct portal interface for catalog browsing
- **Sync Type:** Full copy, exact match

### Destination 2: Ridgemont Studio Website
- **Location:** `Ridgemont Studio Website/tracks.json`
- **Format:** Transformed and filtered version
- **Purpose:** Website streaming player data
- **Sync Type:** Filtered (released only) + transformed to player format

## Execution Steps

### STEP 1: Pre-Sync Validation (Duration: 1 minute)

**Action:** Validate source file integrity before sync

1. Check if source file exists: `/Ridgemont Catalog Manager/data/catalog.json`
   - If missing: STOP and report "Source file not found"

2. Verify source file is readable and not locked
   - If locked or unreadable: STOP and wait 10 seconds, retry once
   - If still fails: Report "Source file locked" and exit

3. Parse source JSON to verify valid format
   - If JSON parsing fails: STOP and report "Invalid JSON in source file: [error details]"
   - Extract and log the specific line/character causing error

4. Load source data into memory
   - Log total number of tracks: `[X] tracks loaded`
   - Log metadata version and last updated timestamp

**Output:**
- ✓ "Source validation passed" or
- ✗ "Source validation failed: [specific error]"
- Log: "Catalog has [X] total tracks, last updated [timestamp]"

**STOP if validation fails - do not proceed to sync**

---

### STEP 2: Schema Validation (Duration: 2 minutes)

**Action:** Validate source data against expected schema

Verify each track record contains required fields:

**Required Fields (must exist, cannot be null/empty):**
- `id` - Unique track identifier (string, format: track_###)
- `title` - Track title (string, 1-200 characters)
- `artist` - Primary artist name (string, 1-100 characters)
- `duration` - Duration in seconds (integer, 1-3600)
- `releaseDate` - ISO 8601 date (YYYY-MM-DD)
- `status` - Track status (enum: "released", "draft", "archived")

**Optional but Should Not Be Empty (if present):**
- `album` - Album name (string if present)
- `genres` - Array of genres (array of strings)
- `description` - Track description (string)
- `url` - Track URL (string, must be valid URL format)

**Validation Logic:**

1. Loop through all tracks in source file
2. For each track:
   - Check all required fields exist
   - Check required fields are not null, empty string, or empty array
   - Validate data types (string = string, integer = integer, etc.)
   - Validate enum values (status must be one of: released, draft, archived)
   - Validate ID format (must be "track_" followed by digits)
   - Validate dates are ISO 8601 format
   - Validate URLs are well-formed (start with http/https)

3. Count validation failures
4. If validation fails:
   - Log each failed track: "[ID] - [Field name]: [validation error]"
   - Count total failures
   - If failures > 5: STOP and report "Too many validation errors ([X] tracks failed)"
   - If failures 1-5: Report warnings but allow sync with warnings
   - If failures = 0: Report "All tracks passed schema validation"

5. Check for duplicate IDs:
   - If duplicate IDs found: STOP and report "Duplicate track IDs found: [list IDs]"

**Output:**
- ✓ "Schema validation passed: 0 errors"
- ⚠ "Schema validation with warnings: [X] tracks have issues"
- ✗ "Schema validation failed: [X] critical errors"

**STOP if critical errors - do not proceed to sync**

---

### STEP 3: Record Count Check (Duration: 1 minute)

**Action:** Verify track count hasn't dropped unexpectedly

1. Get count of tracks in source file
2. Get count of tracks in current frozen-cloud-portal (if exists)
3. Compare counts:
   - If difference > 20% AND is a decrease: **WARNING** - possible data loss
     - Log: "WARNING: Track count dropped from [old] to [new] (loss of [X] tracks)"
     - Ask for confirmation to proceed (auto-yes if no user input after 30 sec)
   - If difference < 20%: OK, continue
   - If increase: OK, continue (new tracks added)

4. Check for archived tracks:
   - Count tracks with status = "archived"
   - Log: "[X] archived tracks detected"

5. Check for draft tracks:
   - Count tracks with status = "draft"
   - Log: "[X] draft tracks detected"

**Output:**
- "Record count: [X] tracks total ([Y] released, [Z] draft, [W] archived)"
- ✓ "Count check passed"
- ⚠ "WARNING: Significant count decrease detected"

**Continue to next step (do not stop unless instructed)**

---

### STEP 4: Empty Field Check (Duration: 2 minutes)

**Action:** Identify tracks with missing important data

1. Loop through all tracks
2. For each required field, count how many tracks have empty/missing values
3. Log findings:
   - Tracks missing descriptions: [X]
   - Tracks missing genres: [X]
   - Tracks missing album: [X]
   - Tracks with invalid URLs: [X]
   - Tracks missing streaming links: [X]

4. Flag specific tracks that are incomplete:
   - If any released track is missing critical info (title, artist, duration), flag it
   - Log: "Released track [ID] missing [field]"

5. Severity assessment:
   - Critical (required fields missing from released tracks): STOP sync
   - Warning (optional fields empty on released tracks): Log warning, continue
   - Info (draft tracks missing optional fields): Log info only, continue

**Output:**
- "Empty field check complete: [X] potential issues detected"
- List any critical gaps that block sync
- Log warnings for minor gaps

**STOP if critical gaps found - do not sync**

---

### STEP 5: Sync to frozen-cloud-portal (Duration: 1 minute)

**Action:** Copy catalog.json to frozen-cloud-portal exact destination

1. Check if destination file exists: `frozen-cloud-portal/data/catalog.json`
   - If exists, create backup: `frozen-cloud-portal/data/catalog.json.backup.[timestamp]`
   - Log: "Backup created: catalog.json.backup.[timestamp]"

2. Copy source file to destination:
   - Source: `/Ridgemont Catalog Manager/data/catalog.json`
   - Destination: `frozen-cloud-portal/data/catalog.json`
   - Method: Direct file copy (preserves all data exactly)

3. Verify copy completed:
   - Check destination file exists
   - Compare file sizes (should be identical)
   - If sizes don't match: Report error and restore from backup

4. Log sync event:
   - Timestamp: [when sync occurred]
   - Source file size: [X] bytes
   - Destination file size: [X] bytes
   - Status: ✓ Success

**Output:**
- ✓ "Synced to frozen-cloud-portal: [timestamp]"
- Backup file: `catalog.json.backup.[timestamp]` created
- File size: [X] bytes

---

### STEP 6: Transform & Filter for Ridgemont Studio Website (Duration: 2 minutes)

**Action:** Create filtered and transformed version for website tracks.json

**Transformation Rules:**

1. **Filter:** Include ONLY tracks with `status: "released"`
   - Exclude all draft and archived tracks
   - Count tracks excluded: [X]

2. **Map Fields:** Transform catalog.json format to tracks.json format

   **Input Field → Output Field Mapping:**
   ```
   id → id
   title → title
   artist → artist
   album → album
   duration → duration (already in seconds)
   releaseDate → publishedDate (ISO 8601)
   genres → genres (keep as array)
   description → description
   url → sourceUrl
   thumbnail → coverImage

   streaming.spotify → streaming.spotify
   streaming.apple → streaming.appleMusic
   streaming.youtube → streaming.youtube
   ```

3. **Add Computed Fields:**
   - `durationFormatted`: Convert duration seconds to "mm:ss" format
   - `displayGenres`: Join genres with commas for UI display
   - `isExplicit`: Default to false (can be overridden if field exists in source)

4. **Output Format Example:**
   ```json
   {
     "metadata": {
       "version": "2.0",
       "lastUpdated": "2025-02-08T10:35:00Z",
       "totalTracks": 145
     },
     "tracks": [
       {
         "id": "track_001",
         "title": "Track Title",
         "artist": "Artist Name",
         "album": "Album Name",
         "duration": 180,
         "durationFormatted": "3:00",
         "publishedDate": "2025-01-15",
         "genres": ["genre1", "genre2"],
         "displayGenres": "genre1, genre2",
         "description": "Track description",
         "sourceUrl": "https://example.com/track/001",
         "coverImage": "https://cdn.example.com/track_001.jpg",
         "isExplicit": false,
         "streaming": {
           "spotify": "spotify:track:xxxxx",
           "appleMusic": "https://music.apple.com/...",
           "youtube": "https://youtu.be/xxxxx"
         }
       }
     ]
   }
   ```

**Transformation Steps:**

1. Create new JSON object with metadata
2. Create new tracks array
3. Loop through each released track in source:
   - Extract fields per mapping
   - Apply transformations (durationFormatted, displayGenres)
   - Add computed fields
   - Add to output tracks array
4. Update metadata.version to "2.0"
5. Update metadata.totalTracks to count of released tracks
6. Log transformation: "Transformed [X] released tracks, excluded [Y] draft/archived"

**Output:**
- "Filtered to [X] released tracks for website"
- "Transformed tracks.json format"

---

### STEP 7: Write to Ridgemont Studio Website (Duration: 1 minute)

**Action:** Save transformed data to website destination

1. Check if destination file exists: `Ridgemont Studio Website/tracks.json`
   - If exists, create backup: `Ridgemont Studio Website/tracks.json.backup.[timestamp]`
   - Log: "Backup created: tracks.json.backup.[timestamp]"

2. Write transformed JSON to destination:
   - Destination: `Ridgemont Studio Website/tracks.json`
   - Format: Pretty-printed JSON (2-space indentation)

3. Verify write completed:
   - Check destination file exists
   - Parse destination file to verify valid JSON
   - Check record count in destination matches transformed count
   - If count mismatch: Restore from backup and report error

4. Log sync event

**Output:**
- ✓ "Synced to Ridgemont Studio Website: [timestamp]"
- Backup file: `tracks.json.backup.[timestamp]` created
- File size: [X] bytes
- Record count: [Y] released tracks

---

### STEP 8: Post-Sync Verification (Duration: 2 minutes)

**Action:** Verify both destination files match expectations

1. **Verify frozen-cloud-portal/data/catalog.json:**
   - Read destination file
   - Parse as JSON
   - Count tracks: [X]
   - Verify matches source count
   - Sample check: Verify first track matches source first track (ID, title)
   - Log: "✓ frozen-cloud-portal verified: [X] tracks, valid JSON"

2. **Verify Ridgemont Studio Website/tracks.json:**
   - Read destination file
   - Parse as JSON
   - Count tracks: [X]
   - Verify count matches released track count (should be less than total)
   - Sample check: Verify first track is released status
   - Verify all tracks have transformed fields (durationFormatted, displayGenres)
   - Log: "✓ Ridgemont Studio Website verified: [X] released tracks, valid JSON"

3. **Compare record counts:**
   - Source total: [X]
   - frozen-cloud-portal: [Y] (should equal X)
   - Website: [Z] (should be less than X, only released)
   - Log relationships

4. **Detect any missing tracks:**
   - If frozen-cloud-portal count doesn't match source: Report error
   - If website count is more than source released count: Report error

**Output:**
- ✓ "Post-sync verification passed"
- frozen-cloud-portal: [X] tracks verified
- Ridgemont Studio Website: [Y] tracks verified
- Or ✗ "Verification failed: [specific issue]"

**If verification fails, restore from backups and report error**

---

### STEP 9: Logging (Duration: 1 minute)

**Action:** Append sync event to sync_log.md file

**Log File Location:** `Ridgemont Catalog Manager/sync_log.md`

**Log Format:**

```markdown
## Sync Event [Timestamp: 2025-02-08 10:35:00 UTC]

**Status:** ✓ SUCCESS / ⚠ WARNING / ✗ FAILED

**Duration:** [X] minutes [Y] seconds

**Initiator:** Automatic (after catalog write) / Manual (user command)

**Source File:**
- Location: `/Ridgemont Catalog Manager/data/catalog.json`
- Size: [X] bytes
- Total Tracks: [Y]
- Last Updated: [timestamp]

**Validation:**
- Schema validation: ✓ Passed ([X] validation checks)
- Record count check: ✓ Passed ([Y] total tracks)
- Empty field check: ✓ Passed ([0] critical issues)

**Track Distribution:**
- Released: [X] tracks
- Draft: [Y] tracks
- Archived: [Z] tracks

**Sync Operations:**
1. frozen-cloud-portal: ✓ Success ([X] tracks synced)
   - Destination: `frozen-cloud-portal/data/catalog.json`
   - Backup: `catalog.json.backup.[timestamp]`

2. Ridgemont Studio Website: ✓ Success ([Y] tracks synced - released only)
   - Destination: `Ridgemont Studio Website/tracks.json`
   - Backup: `tracks.json.backup.[timestamp]`

**Post-Sync Verification:**
- frozen-cloud-portal: ✓ Verified ([X] tracks)
- Ridgemont Studio Website: ✓ Verified ([Y] tracks)

**Issues/Warnings:**
- [None] or [list any issues encountered]

**Summary:**
Successfully synchronized catalog data to all downstream systems. No errors detected.

---
```

**Logging Steps:**

1. Create sync_log.md if it doesn't exist
2. Append new sync event entry (newest at top)
3. Include all template fields with actual values
4. Keep log file for historical reference
5. Trim log if it exceeds 100 entries (keep most recent 100)

**Output:**
- ✓ "Sync event logged to sync_log.md"
- Log entry timestamp: [when recorded]

---

### STEP 10: Final Status Report (Duration: 1 minute)

**Action:** Generate comprehensive sync completion report

**Report Contents:**

```
CATALOG SYNC COMPLETE

Timestamp: 2025-02-08 10:35:00 UTC
Duration: [X] minutes [Y] seconds
Status: ✓ SUCCESS

SOURCE DATA:
- File: /Ridgemont Catalog Manager/data/catalog.json
- Total Tracks: [X]
- Released: [Y]
- Draft: [Z]
- Archived: [W]

DESTINATION 1: frozen-cloud-portal
- Status: ✓ Synced
- File: frozen-cloud-portal/data/catalog.json
- Tracks: [X] (exact copy)
- Backup: catalog.json.backup.[timestamp]

DESTINATION 2: Ridgemont Studio Website
- Status: ✓ Synced
- File: Ridgemont Studio Website/tracks.json
- Tracks: [Y] (released only)
- Backup: tracks.json.backup.[timestamp]
- Transformation: catalog → tracks.json format

VALIDATIONS:
- Schema validation: ✓ Passed
- Record count: ✓ Verified
- Empty fields: ✓ No critical issues
- Post-sync verification: ✓ Both destinations verified

NEXT SYNC: [Calculated based on schedule or manual]
```

**Output to User:**
- Summary status: "✓ Catalog synchronized successfully"
- Key metrics: "[X] total tracks, [Y] released"
- Next action: None (sync complete) or [list any manual actions if needed]

## Error Handling

### Error: Source File Not Found
- **Cause:** Catalog file missing or moved
- **Action:** STOP immediately, report error
- **Recovery:** Restore from backup or check file location
- **Output:** "ERROR: Source file not found at /Ridgemont Catalog Manager/data/catalog.json"

### Error: Invalid JSON in Source
- **Cause:** JSON parsing error, malformed file
- **Action:** STOP immediately
- **Recovery:** Restore from backup, verify file integrity
- **Output:** "ERROR: JSON parse failed at [line:character] - [error details]"

### Error: Schema Validation Failures (>5 records)
- **Cause:** Multiple tracks with invalid data
- **Action:** STOP, do not sync
- **Recovery:** Fix source data, retry
- **Output:** "ERROR: [X] tracks failed validation"

### Error: Duplicate Track IDs
- **Cause:** Multiple tracks with same ID
- **Action:** STOP immediately
- **Recovery:** Resolve duplicates in source, reassign IDs
- **Output:** "ERROR: Duplicate IDs found: [list IDs]"

### Error: Destination File Write Failure
- **Cause:** Permission issues, disk full, file locked
- **Action:** Restore from backup, retry
- **Recovery:** Check permissions, disk space, file locks
- **Output:** "ERROR: Failed to write [destination] - [specific error]"

### Error: Verification Failed
- **Cause:** Synced file doesn't match source
- **Action:** Automatically restore backup
- **Recovery:** Investigate why sync failed, retry
- **Output:** "ERROR: Post-sync verification failed. Backup restored. [details]"

### Warning: Significant Data Loss Detected
- **Cause:** Track count decreased by >20%
- **Action:** Log warning, request confirmation
- **Recovery:** User can cancel and investigate
- **Output:** "WARNING: Track count dropped from [old] to [new]. Proceed? (yes/no)"

### Warning: Empty Fields on Released Tracks
- **Cause:** Optional fields missing from published tracks
- **Action:** Log warning, continue sync
- **Recovery:** Can update fields and resync
- **Output:** "WARNING: [X] released tracks missing descriptions"

## Safety Checks

**Never Overwrite Destination If:**

1. Source validation fails (schema, format, etc.)
2. Record count dropped >20% unexpectedly
3. Critical required fields are empty in released tracks
4. Duplicate IDs detected in source
5. Verification fails (destination doesn't match source after write)
6. File write fails for any reason

**Always Create Backup Before:**

1. Writing to frozen-cloud-portal/data/catalog.json
2. Writing to Ridgemont Studio Website/tracks.json
3. Any overwrite operation

**Backup Retention:**

- Keep backups for 30 days minimum
- Naming convention: `[filename].backup.[YYYY-MM-DD_HH:MM:SS]`
- Store in same directory as original file
- Automatically clean up backups older than 30 days

## Performance Targets

- Full sync should complete in 3-5 minutes (normal conditions)
- Pre-sync validation: < 1 minute
- Destination writes: < 1 minute each
- Post-sync verification: < 2 minutes
- Total max duration: 10 minutes (if experiencing issues)

## Related Skills

None - this is a standalone data synchronization skill.

## Support Information

**Sync Troubleshooting:**

1. Check sync_log.md for recent sync history and any errors
2. Verify source file exists and is not locked
3. Verify destination directories are writable
4. Check disk space on all systems
5. Verify file permissions allow read/write access
6. If persistent issues, restore from latest backup and contact admin

**Manual Sync:**

If automated sync fails, manual steps:

1. Backup both destination files
2. Copy `/Ridgemont Catalog Manager/data/catalog.json` to `frozen-cloud-portal/data/catalog.json`
3. Transform and copy to `Ridgemont Studio Website/tracks.json` (filtered, released only)
4. Verify both files
5. Append manual sync event to sync_log.md
