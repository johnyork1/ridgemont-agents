# Claude Cowork — Universal Agent Instructions
# Location: /Users/johnyork/My Drive/Ridgemont Studio/Claude Cowork/CLAUDE.md
#
# This file contains shared rules and conventions for ALL Claude Cowork agents
# operating from this directory. Every agent should read and follow these rules.

---

## Browser Automation Rules

### Primary Browser: Brave (via Claude in Chrome MCP)
- **All browser-based agentic activity** (browsing, form filling, posting, scheduling, research) should use the **Brave browser** via Claude in Chrome MCP.
- John uses **Firefox for personal browsing**. Never interact with Firefox.
- Brave is always open with Claude in Chrome extension connected.
- If Claude in Chrome MCP returns "No Chrome extension connected," ask John to reconnect the extension in Brave (click the extension icon → Disconnect → Reconnect).

### Secondary Browser: Chrome for Testing (via Puppeteer MCP)
- Puppeteer MCP launches its own isolated Chromium instance ("Chrome for Testing").
- Use Puppeteer **only** for tasks that do NOT require authentication (e.g., scraping public pages, generating screenshots of public URLs).
- Puppeteer is **not logged into any accounts** — never use it for authenticated tasks (posting to X, checking email, etc.).

### Rule Summary
| Task Type | Use This |
|-----------|----------|
| Anything requiring login (X, Gmail, etc.) | Claude in Chrome (Brave) |
| Public page scraping / screenshots | Either — prefer Puppeteer for isolation |
| Research that needs no auth | Either |
| Posting to social media | Claude in Chrome (Brave) or X API MCP |

---

## File Handling Rules

### Working Directory
- Agents should use **relative paths** when referencing workflow files (`x_post_history.md`, `x_daily_post_shortcut.md`, etc.).
- Look for files in the current mounted/working directory first.
- If a file isn't found, check the X profile or web directly and create a fresh copy.
- Always save outputs to the working directory so they persist across sessions.

### Persistent Files (keep updated across sessions)
- `x_post_history.md` — full post history, phrases to avoid, style notes
- `x_daily_post_shortcut.md` — the X posting workflow definition
- `x_top_posts_[date].md` — daily trending post captures

---

## MCP Server Preferences

### Available MCP Servers (in order of preference for each task type)

**Posting to X:**
1. X API MCP (if configured) — fastest, most reliable
2. Claude in Chrome (Brave) — fallback if API unavailable

**Searching X:**
1. Claude in Chrome (Brave) — required (free API tier is write-only)
2. WebSearch tool — for general crypto news

**Scheduling Posts:**
1. Claude in Chrome (Brave) via X's Schedule Post UI — only method available
2. Future: external scheduler if integrated

**Web Research:**
1. WebSearch tool — for news, data, market info
2. Claude in Chrome (Brave) — for specific pages that need interaction

---

## Style and Tone (applies to X posting agent)

See `x_daily_post_shortcut.md` for full style rules. Key points:
- All lowercase, no apostrophes in contractions
- Data-driven, observational, not condescending
- Never use "crypto Twitter" — always "X"
- "we" energy over "you" energy
- Check `x_post_history.md` before every run to avoid repetition

---

## Cross-Source Research

When gathering trending topics and news for daily posts, **use the `enterprise-search` skill** to search across LunarCrush, Google Drive, Gmail, and all connected MCP sources in a single query. It decomposes your research question into targeted searches per source and synthesizes results with source attribution — much faster than searching each tool individually.

---

## Canva Design Integration

The **Canva MCP connector** is installed. Use it to generate social media graphics, post thumbnails, branded templates, and visual content for X posts — directly from Claude. Leverage Canva's design generation for quick visual assets instead of manual image creation.

## SEO & Brand Monitoring

The **Ahrefs MCP connector** is installed. Use it for SEO analytics, brand mention tracking, backlink analysis, and traffic insights. Monitor @4_Bchainbasics brand mentions across the web and track competitor content performance.

---

## Agent Behavior

### Current Phase: LEARNING
- Always present drafts for review before posting/scheduling.
- Track all edits John makes and update style rules accordingly.
- Goal: learn John's voice well enough to eventually operate autonomously.

### Safety
- Never post without explicit approval (until switched to AUTONOMOUS phase).
- Schedule posts — don't post multiple things live back-to-back.
- Always verify the correct browser/tool is being used before taking action.
