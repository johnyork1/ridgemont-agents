# Master Agent

Orchestrator and strategic advisor for the entire Claude Cowork agent ecosystem.

## What It Does

- Auto-discovers agent folders and maintains `agent_registry.json` as the single source of truth
- Runs daily audits: scans for file changes, checks rules for completeness, identifies redundancies
- Health-scores each agent (1-10) on clarity, scope, data quality, utilization, and effectiveness
- Recommends merging overlapping agents or splitting overloaded ones
- Routes cross-agent queries by reading relevant files from multiple agents and synthesizing answers
- Onboards newly discovered agents with automatic registry population

## Usage

Open the `master-agent/` directory in Claude Code. Common commands:

- "Run daily audit" -- generates a report in `logs/audit_YYYY-MM-DD.md`
- "Check all agents" -- scans the ecosystem and updates the registry
- "Health score [agent]" -- rates an agent across five dimensions

## Key Files

- `agent_registry.json` -- discovered agents and their metadata
- `audit_template.md` -- report template for daily audits
- `evaluation_criteria.md` -- health scoring rubrics
- `last_audit.json` -- previous audit snapshot for change detection

## Requirements

- Claude Code with access to the Cowork directory
- Zapier and Notion MCP connectors (optional, for automation and knowledge base)
