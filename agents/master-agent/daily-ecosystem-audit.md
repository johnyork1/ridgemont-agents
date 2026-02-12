# /audit — Master Agent Daily Ecosystem Audit

Run a full health audit of all Cowork agents in the Ridgemont Studio ecosystem.

## Objective

Scan every agent folder under the Cowork root, check for hygiene issues, score health, update the registry, and produce a versioned audit report.

## Steps

1. **Read the registry** at `Master Agent/agent_registry.json` to get the current agent list, health scores, and last audit version number.

2. **Read the last audit** at `Master Agent/last_audit.json` to get the previous audit version and baseline.

3. **Scan every agent directory** listed in the registry. For each agent folder, check for:
   - `~$` temp/lock files (Word/Excel) — these must be flagged for deletion
   - `.bak` backup files — advisory only
   - `__pycache__/` directories — advisory only
   - `node_modules/` without `.gitignore` — flag
   - `.env` files with secrets — note as accepted risk
   - `venv/` directories — advisory only
   - Stale references in RULES.md or CLAUDE.md (referencing deleted files)
   - New files or directories not documented in the agent's instruction file
   - Empty directories

4. **Score each agent** on 5 dimensions (1-10 scale):
   - **Clarity**: How well-defined are the agent's instructions?
   - **Scope**: Is the agent's purpose well-bounded and non-overlapping?
   - **Data Quality**: Are data files clean, current, and well-organized?
   - **Utilization**: Is the agent producing real outputs?
   - **Effectiveness**: Does the agent achieve its stated purpose?

   Health score = weighted average (equal weights).

5. **Calculate ecosystem score** = average of all agent health scores, rounded to 1 decimal.

6. **Identify action items** — anything requiring human approval (deletions, config changes) or automated fixes (stale references, missing documentation).

7. **Generate audit report** at `Master Agent/logs/audit_YYYY-MM-DD_vN.md` with:
   - Audit version (increment from last audit)
   - Agent-by-agent findings
   - Ecosystem scorecard with trend arrows vs. previous audit
   - Action items table

8. **Update `Master Agent/last_audit.json`** with new snapshot data.

9. **Update `Master Agent/agent_registry.json`**:
   - Bump registry version (increment minor)
   - Update health scores for any changed agents
   - Add changelog entry summarizing findings
   - Update issue lists per agent

10. **Report results** — summarize: agents scanned, issues found, ecosystem score, action item count.

## Constraints

- Handle mount/permission issues silently — never narrate infrastructure problems to the user.
- Do NOT delete files without explicit user approval. Flag them as action items.
- Do NOT modify agent instruction files (RULES.md, CLAUDE.md) without explicit user approval.
- Advisory items (`.bak`, `__pycache__`, `venv/`) do not require action — just note them.
- If an agent folder is empty or missing, flag it but do not remove from registry.

## Success Criteria

- All agent folders scanned with zero missed
- Registry and last_audit.json updated with correct version numbers
- Audit report saved to logs/
- Ecosystem score calculated and compared to previous
- Action items clearly listed with severity
