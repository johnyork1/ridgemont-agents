# Deep Dive v2 — Skills, Plugins & Connectors Optimization
**Date:** 2026-02-08
**Registry:** v2.5 → targeting v2.6
**Ecosystem:** 11 agents, 4 OAuth + 9 MCP connectors, 3 custom skills, 7 system skills

---

## CURRENT INVENTORY

### Installed Connectors (13 total)
| Connector | Type | Tools | Primary Agent(s) |
|---|---|---|---|
| Google Drive | OAuth | — | All |
| Gmail | OAuth | — | Master Agent, Dewey |
| Google Calendar | OAuth | — | X-Posts |
| GitHub | OAuth | — | RSW, Catalog Manager |
| ChEMBL | MCP | 6 | Dr. Vinnie |
| Clinical Trials | MCP | 6 | Dr. Vinnie |
| Cloudflare Dev Platform | MCP | — | RSW, Frozen Cloud Website |
| Crypto.com | MCP | 9 | X-Posts, Make Videos |
| Indeed | MCP | — | (general) |
| LunarCrush | MCP | 11 | X-Posts, Make Videos |
| Play Sheet Music | MCP | 1 | Make-Music |
| PubMed | MCP | 7 | Dr. Vinnie |
| Canva | MCP | — | (available, not connected) |

### Custom Skills (3)
| Skill | Location | Primary Agent |
|---|---|---|
| x-voice | .skills/x-voice/ | X-Posts |
| x-images | .skills/x-images/ | X-Posts |
| pushgit | .skills/pushgit/ | Ridgemont Catalog Manager |

### System Skills (7 available in Cowork)
| Skill | Used By | Unused By (should be) |
|---|---|---|
| docx | Dewey, Dr. Vinnie | Ridgemont Catalog Manager (pitch letters), Master Agent (reports) |
| xlsx | — | Ridgemont Catalog Manager (revenue exports), Make Videos (analytics) |
| pptx | — | Make Videos (pitch decks), Master Agent (ecosystem reports) |
| pdf | — | Dewey (legal filings), Dr. Vinnie (clinical summaries) |
| skill-creator | — | Master Agent (building new agent skills) |
| create-shortcut | Master Agent | All agents (automation) |
| enterprise-search | — | Master Agent (cross-agent knowledge synthesis) |

---

## TIER 1 — IMMEDIATE HIGH-IMPACT (Do Now)

### 1A. Skill References Missing from Agent Configs
These system skills exist and are free — agents just don't know about them yet.

| Agent | Skill to Add | Why |
|---|---|---|
| **Ridgemont Catalog Manager** | `xlsx` | Revenue tracking, catalog exports, expense reports — core workflow produces tabular data but never references the xlsx skill |
| **Ridgemont Catalog Manager** | `docx` | Pitch letters, supervisor communications — already generates HTML decks but could produce professional Word docs |
| **Make Videos** | `pptx` | Pitch decks for brand deals, sponsor outreach — currently no presentation capability |
| **Dewey Cheatem** | `pdf` | Legal filings, court document analysis, form filling — handles PDFs constantly but doesn't reference the pdf skill |
| **Dr. Vinnie Boombatz** | `pdf` | Clinical summaries, research syntheses, patient-facing reports as PDF |
| **Master Agent** | `xlsx` | Ecosystem health dashboards, audit exports as spreadsheets |
| **Master Agent** | `enterprise-search` | Cross-agent knowledge synthesis — search across all connected sources at once |
| **Master Agent** | `skill-creator` | Build new skills for agents that need them |

### 1B. Custom Skill Gaps — Build These
| New Skill | For Agent | What It Does |
|---|---|---|
| **yt-shorts** | Make Videos | Short-form vertical video workflow (15-60s) — currently marked TODO in GAME_PLAN.md |
| **upload-all** | Make Videos | Batch multi-platform upload (YouTube, TikTok, Instagram, Rumble) — currently manual via Chrome |
| **catalog-sync** | Ridgemont Catalog Manager | Formalize the pushgit workflow + add validation, webhook triggers, and auto-portal-refresh |
| **legal-memo** | Dewey Cheatem | IRAC-format legal memo template with proper citation formatting, disclaimer injection, and docx output |

### 1C. Connector: Blockscout (Blockchain Data)
- **UUID:** 48425fdb-37c1-408d-9606-30e16847b6a8
- **For:** X-Posts, Make Videos
- **Why:** On-chain transaction analysis, wallet tracking, contract verification. Complements LunarCrush (social sentiment) and Crypto.com (market data) with actual blockchain data. Gives @4_Bchainbasics real alpha.

### 1D. Connector: Melon (Music Charts)
- **UUID:** 02224ef2-6652-422e-9a70-fa93f699ab8f
- **For:** Ridgemont Catalog Manager, Make-Music, Suno Studio
- **Why:** Browse music charts, artist songs/albums, genre data. Direct feed into catalog decisions and music production direction.

---

## TIER 2 — STRONG VALUE (This Week)

### 2A. Connectors to Install

| Connector | UUID | For Agent(s) | Why |
|---|---|---|---|
| **Cloudinary** | c93e842b-830f-4b4a-bbd1-6e3af0199a8f | Make Videos, RSW, Frozen Cloud | Image/video asset management, transformation, CDN delivery. Replaces manual asset handling. |
| **Ahrefs** | 098cb32a-ba21-4770-97dd-78bb54655419 | RSW, X-Posts, Frozen Cloud | SEO analytics, brand mention tracking, traffic analysis. Critical for web presence. 60+ tools. |
| **Consensus** | 65247229-f0c7-49df-9044-fcbb8b3894c6 | Dewey, Dr. Vinnie | Scholarly research search with citations. Complements PubMed (medical) and CourtListener (legal) with broader academic coverage. |
| **bioRxiv** | 7f750eb6-c3cb-47d7-9269-d35c43fe9925 | Dr. Vinnie | Preprint access for cutting-edge medical/bio research before peer review. |
| **ICD-10 Codes** | bd8c051d-df35-44c0-a8b8-084b700e1f21 | Dr. Vinnie | Medical classification codes lookup — essential for any clinical documentation workflow. |
| **Scholar Gateway** | ff091334-0f12-4d0e-a973-c00467dd3818 | Dewey, Dr. Vinnie | Enhanced scholarly search with semantic matching. Broader than PubMed. |

### 2B. Skill References to Embed

| Agent | Action | Config File |
|---|---|---|
| **X-Posts** | Add `enterprise-search` reference for cross-source trending research | CLAUDE.md |
| **Make Videos** | Add `xlsx` reference for analytics tracking spreadsheets | GAME_PLAN.md |
| **Suno Studio** | Add `create-shortcut` reference for automating prompt generation workflows | CLAUDE_INSTRUCTIONS.md |
| **frozen-cloud-portal** | Add `xlsx` reference for catalog data exports | RULES.md |

### 2C. Cross-Agent Integration Improvements
| Integration | What | Impact |
|---|---|---|
| **LunarCrush → Make Videos CLAUDE.md** | LunarCrush is referenced in GAME_PLAN.md but NOT in any top-level agent config. Embed in main Make Videos config. | Ensures every session knows to use it |
| **Cloudflare Dev Platform → RSW RULES.md** | RSW uses Cloudflare Workers/R2 but its RULES.md doesn't reference the new Cloudflare MCP connector | Workers deployments directly from Claude |
| **Cloudflare Dev Platform → Frozen Cloud Website** | Same — this agent runs on Cloudflare but doesn't know the MCP connector exists | Direct deployment capability |
| **pushgit skill → frozen-cloud-portal RULES.md** | Portal depends on catalog sync but doesn't reference the pushgit skill | Self-prompt to run sync |

---

## TIER 3 — STRATEGIC (This Month)

### 3A. Financial Infrastructure Connectors

| Connector | UUID | For Agent(s) | Why |
|---|---|---|---|
| **Stripe** | de127013-63f1-43d0-8dd2-b6cb5b4e5d1b | RSW, Catalog Manager | Payment processing for sync licensing marketplace — RSW describes this feature but has no payment backend |
| **PayPal** | 001103b7-bcde-4b9c-b5d4-f209c2fed1f3 | RSW, Catalog Manager | Alternative payment option for licensing deals |

### 3B. Advanced Analytics

| Connector | UUID | For Agent(s) | Why |
|---|---|---|---|
| **MotherDuck** | 0929a5c7-38ce-40ab-8aad-af9ce34553c7 | Catalog Manager, frozen-cloud-portal | Natural language data querying over catalog data. "Show me all unreleased Frozen Cloud tracks sorted by revenue potential." |
| **Windsor.ai** | 360c0c31-4bb6-42ca-8e50-5da0a100a68e | X-Posts, RSW | Unified marketing analytics across 325+ sources. One connector to rule all marketing metrics. |
| **Amplitude** | 8e40fa13-4654-4387-bbad-12b8ecc81351 | frozen-cloud-portal, RSW | User analytics for web properties — understand listener behavior |

### 3C. Project Management & Orchestration

| Connector | UUID | For Agent(s) | Why |
|---|---|---|---|
| **Notion** | 69f3a300-cc60-48c4-b237-dfac56530dbf | Master Agent, all | Knowledge base for the entire ecosystem. Meeting notes, project plans, agent documentation. |
| **Zapier** | 1f6f271e-3d29-4241-b35e-8abe6def4891 | Master Agent | Workflow automation connecting all 11 agents with external triggers — "when new song added to catalog, auto-push to portal and create X post" |

### 3D. Medical Agent Power-Ups

| Connector | UUID | For Agent(s) | Why |
|---|---|---|---|
| **NPI Registry** | e3b3e96f-6b4d-468d-a4b6-89f484b7e21c | Dr. Vinnie | US healthcare provider lookup — validate provider credentials |
| **Function Health** | 48527e54-fe84-4dc6-b97f-c8e0763bca97 | Dr. Vinnie | Lab test insights, biomarker analysis, personalized health plans |
| **Medidata** | 2011b8ca-e6e5-4eed-b954-2249e521a3a9 | Dr. Vinnie | Clinical trial site ranking and research documentation |

### 3E. Design & Creative

| Connector | UUID | For Agent(s) | Why |
|---|---|---|---|
| **Canva** (already available) | eb9240f2-e1c1-43c1-828f-0fda40c22e4c | X-Posts, RSW, Frozen Cloud | Design generation, templates, brand kits. Already in connector list — just needs Connect click. |
| **Figma** | c758d038-d8eb-4421-b426-9dd68dc7f84a | RSW, Frozen Cloud Website | Design system management, collaborative design for web properties |

---

## AGENT-BY-AGENT OPTIMIZATION SCORECARD

| Agent | Current | After Tier 1 | After Tier 2 | Key Additions |
|---|---|---|---|---|
| **X-Posts** | 8.8 | 9.0 | 9.2 | Blockscout, enterprise-search, Ahrefs |
| **Make Videos** | 7.6 | 8.0 | 8.4 | yt-shorts skill, upload-all skill, pptx, Cloudinary |
| **Make-Music** | 7.2 | 7.4 | 7.6 | Melon charts, Play Sheet Music integration |
| **Ridgemont Catalog Manager** | 8.8 | 9.2 | 9.4 | xlsx, docx, catalog-sync skill, Melon |
| **Ridgemont Studio Website** | 7.8 | 8.2 | 8.6 | Cloudflare MCP ref, Ahrefs, Cloudinary |
| **Suno Studio** | 8.8 | 8.8 | 9.0 | create-shortcut, Melon |
| **Frozen Cloud Website** | 5.0 | 5.4 | 6.0 | Cloudflare MCP ref, needs RULES.md |
| **frozen-cloud-portal** | 7.2 | 7.4 | 7.8 | xlsx, pushgit ref |
| **Master Agent** | 8.8 | 9.2 | 9.4 | xlsx, enterprise-search, skill-creator |
| **Dewey Cheatem** | 8.8 | 9.0 | 9.4 | pdf skill, legal-memo skill, Consensus, Scholar Gateway |
| **Dr. Vinnie Boombatz** | 7.6 | 8.0 | 8.6 | pdf skill, bioRxiv, ICD-10, Consensus |
| **ECOSYSTEM** | 8.3 | 8.6 | 9.0 | +2 connectors, +8 skill refs, +4 new skills |

---

## TIER 1 IMPLEMENTATION CHECKLIST

- [ ] Embed `xlsx` skill reference in Ridgemont Catalog Manager SYSTEM_PROMPT_V5.md
- [ ] Embed `docx` skill reference in Ridgemont Catalog Manager SYSTEM_PROMPT_V5.md
- [ ] Embed `pptx` skill reference in Make Videos GAME_PLAN.md
- [ ] Embed `pdf` skill reference in Dewey Cheatem CLAUDE.md
- [ ] Embed `pdf` skill reference in Dr. Vinnie Boombatz CLAUDE.md
- [ ] Embed `xlsx` + `enterprise-search` + `skill-creator` references in Master Agent RULES.md
- [ ] Install Blockscout connector
- [ ] Install Melon connector
- [ ] Build yt-shorts skill stub for Make Videos
- [ ] Build upload-all skill stub for Make Videos
- [ ] Build catalog-sync skill stub for Ridgemont Catalog Manager
- [ ] Build legal-memo skill stub for Dewey Cheatem
- [ ] Update agent_registry.json to v2.6

---

## SUMMARY

The ecosystem has strong bones but is only using **3 of 10 available skill types** and **13 of 68+ relevant connectors**. The biggest bang-for-buck is Tier 1: embedding skill references in agent configs (zero-cost, immediate capability uplift) and adding Blockscout + Melon connectors (fills the two biggest data gaps — on-chain crypto and music chart intelligence).

Projected ecosystem score after Tier 1: **8.6/10** (up from 8.3).
Projected ecosystem score after Tier 2: **9.0/10**.
