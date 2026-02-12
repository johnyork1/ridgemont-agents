# Ecosystem Health Check Workflow

**Trigger:** Run daily or on-demand to validate ecosystem integrity

---

## Steps

### 1. Agent Config Validation
For each of the 11 agents, verify:
- Config file exists (RULES.md, CLAUDE.md, SYSTEM_PROMPT, etc.)
- Config contains required sections: Identity, Behavior Guidelines, Related Agents
- No stale file references (paths that point to moved/deleted files)
- Flag any agent with missing sections as STRUCTURAL ISSUE

### 2. Connector Availability
For each agent's embedded connector references:
- Verify the connector is still listed in claude.ai/settings/connectors
- Note any connectors that were disconnected or expired
- Flag as CONNECTOR DRIFT if config references an unavailable connector

### 3. Data Consistency
- Run catalog sync check: compare Catalog Manager → frozen-cloud-portal catalog.json
- Verify tracks.json in RSW matches released songs in catalog
- Check for orphaned backup files (keep max 5 per agent)

### 4. File Hygiene
- Count .DS_Store files across ecosystem (target: 0)
- Check for ~$ Word temp lock files
- Check for .bak files older than 30 days
- Measure total ecosystem disk usage

### 5. Agent Health Scoring
Score each agent 0-10 based on:
- Config completeness (Identity, Guidelines, Related Agents) — 3 pts
- Connector embedding accuracy — 2 pts
- File organization (no orphans, no bloat) — 2 pts
- Usage recency (active within 7 days = full marks) — 1 pt
- Skill/workflow coverage — 2 pts

### 6. Registry Update
- Update agent_registry.json with new health scores
- Add changelog entry if any scores changed
- Bump registry version (patch increment)

### 7. Output Report
```
ECOSYSTEM HEALTH CHECK — YYYY-MM-DD
════════════════════════════════════
Agents: XX/11 healthy
Connectors: XX/29 verified
Data Sync: ✅ / ⚠️ / ❌
File Hygiene: XX issues found
Ecosystem Score: X.X/10

[List any action items]
```

---

## Escalation Rules
- Score drop > 0.5 pts → investigate immediately
- Connector disconnected → flag for reconnection
- Data sync failure → run catalog-sync skill
- 3+ file hygiene issues → schedule bulk cleanup
