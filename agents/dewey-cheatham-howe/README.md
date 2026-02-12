# 🏛️ Dewey Cheatem, Esq.

### Comprehensive Legal Research & Advisory Agent for Claude Cowork

A custom Claude Cowork plugin providing deep legal research capabilities across U.S. federal, California, and Idaho law — powered entirely by free, publicly available legal databases.

> ⚠️ **DISCLAIMER**: This agent provides legal *information* and *research*, NOT legal *advice*. Always consult a licensed attorney before making legal decisions.

---

## What's Inside

### Skills (7)
| Skill | Description |
|-------|-------------|
| `case-law-research` | Search and analyze case law across federal, CA, and ID courts |
| `statute-lookup` | Look up and explain statutes, codes, and regulations |
| `contract-review` | Clause-by-clause contract analysis with risk flags |
| `legal-writing` | Draft legal memos, demand letters, and correspondence |
| `california-law` | California-specific legal knowledge (all 29 codes) |
| `idaho-law` | Idaho-specific legal knowledge |
| `legal-citation` | Citation verification and Bluebook formatting |
| `compliance-check` | Regulatory compliance analysis |

### Slash Commands (7)
| Command | Description |
|---------|-------------|
| `/dewey:research-case` | Research case law on a topic |
| `/dewey:lookup-statute` | Look up a specific statute |
| `/dewey:review-contract` | Review a contract for risks |
| `/dewey:draft-letter` | Draft a legal letter |
| `/dewey:verify-citation` | Verify legal citations |
| `/dewey:compliance-check` | Check compliance requirements |
| `/dewey:compare-laws` | Compare CA vs. ID law on a topic |

### Connectors
| Connector | Type | Purpose |
|-----------|------|---------|
| CourtListener MCP | External (free) | Case law, citations, PACER, judges, eCFR |
| Web Search | Built-in | Statute lookups, legal news, court websites |
| Google Drive | Built-in | Personal legal documents |
| Filesystem | Built-in | Local file access in Cowork |
| Google Scholar MCP | External (free, optional) | Academic legal scholarship |

### Free Legal Data Sources Accessed
- **CourtListener** — 3,352+ court jurisdictions, millions of opinions
- **Cornell Legal Information Institute (LII)** — U.S. Code, CFR, 50-state statutes
- **California Legislative Information** — All 29 California Codes
- **Idaho Legislature** — Idaho Statutes and Constitution
- **eCFR** — Federal regulations (always current)
- **Justia** — Case law, codes, and legal guides
- **Google Scholar Case Law** — Federal and state opinions
- **Caselaw Access Project** — Harvard's complete U.S. case law through 2020
- **Wex Legal Dictionary** — Plain-language legal definitions
- **GovInfo** — Federal Register, congressional materials

---

## Installation

### Prerequisites
- Claude Desktop for macOS with Cowork enabled
- Claude Pro, Max, Team, or Enterprise subscription
- Python 3.10+ and `uv` package manager (for CourtListener MCP)
- Free CourtListener API token (get at courtlistener.com/sign-in/)

### Step 1: Copy the Plugin
The plugin folder should already be at:
```
/Users/johnyork/My Drive/Ridgemont Studio/Claude Cowork/dewey-cheatem-esq/
```

### Step 2: Set Up CourtListener MCP Server
```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the CourtListener MCP server
cd ~/mcp-servers
git clone https://github.com/Travis-Prall/court-listener-mcp CourtListener
cd CourtListener

# Configure
cp .env.example .env
# Edit .env and add: COURTLISTENER_API_TOKEN=your_token_here

# Install dependencies
uv sync

# Test
uv run start
```

### Step 3: Install in Claude Desktop / Cowork
Option A — Via Cowork Plugin Upload:
1. Open Claude Desktop → Cowork (Tasks tab)
2. Upload the `dewey-cheatem-esq` folder as a custom plugin

Option B — Via Claude Code CLI:
```bash
claude plugin install /Users/johnyork/My\ Drive/Ridgemont\ Studio/Claude\ Cowork/dewey-cheatem-esq
```

### Step 4: Launch the Agent
In Claude Cowork, use this prompt to kick off Dewey:

```
Load the dewey-cheatem-esq plugin from /Users/johnyork/My Drive/Ridgemont Studio/Claude Cowork/dewey-cheatem-esq/

You are now Dewey Cheatem, Esq. — my comprehensive legal research agent. Read the CLAUDE.md file for your full instructions, persona, and capabilities. 

You have access to skills for case law research, statute lookup, contract review, legal writing, California law, Idaho law, citation verification, and compliance analysis.

Your primary data sources are CourtListener (case law API), Cornell LII, California Legislative Info, Idaho Legislature, eCFR, Justia, and Google Scholar Case Law — all free.

My wife and I live in Oakland, California. My mother lives in Idaho. Focus on federal, California, and Idaho law.

Ready when you are, counselor.
```

---

## Directory Structure
```
dewey-cheatem-esq/
├── .claude-plugin/
│   └── plugin.json              # Plugin manifest
├── .mcp.json                    # MCP connector configuration
├── CLAUDE.md                    # Agent persona, context, and instructions
├── CONNECTORS.md                # Detailed connector setup guide
├── README.md                    # This file
├── commands/
│   ├── research-case.md         # /dewey:research-case
│   ├── lookup-statute.md        # /dewey:lookup-statute
│   ├── review-contract.md       # /dewey:review-contract
│   ├── draft-letter.md          # /dewey:draft-letter
│   ├── verify-citation.md       # /dewey:verify-citation
│   ├── compliance-check.md      # /dewey:compliance-check
│   └── compare-laws.md          # /dewey:compare-laws
├── skills/
│   ├── case-law-research/
│   │   └── SKILL.md
│   ├── statute-lookup/
│   │   └── SKILL.md
│   ├── contract-review/
│   │   └── SKILL.md
│   ├── legal-writing/
│   │   └── SKILL.md
│   ├── california-law/
│   │   └── SKILL.md
│   ├── idaho-law/
│   │   └── SKILL.md
│   ├── legal-citation/
│   │   └── SKILL.md
│   └── compliance-check/
│       └── SKILL.md
├── references/
│   └── free-legal-sources.md    # Quick reference of all free data sources
└── assets/                      # Templates and sample documents (future)
```

---

## Version History
- **v1.0.0** (Feb 7, 2026) — Initial release. 8 skills, 7 commands, CourtListener MCP integration.

## Author
John York / Ridgemont Studio
Built with Claude Opus 4.6
