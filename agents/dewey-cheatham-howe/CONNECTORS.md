# Dewey Cheatem, Esq. — Connectors Guide

## Required Connectors (MCP Servers)

### 1. CourtListener MCP Server ⭐ PRIMARY
**What it does**: Searches millions of federal and state court opinions, verifies citations, accesses PACER dockets, looks up judges, and queries the eCFR (federal regulations).
**Free?**: Yes — Free Law Project (501(c)(3) nonprofit)
**API Key**: Free — register at https://www.courtlistener.com/sign-in/ then get token from settings
**Install**:
```bash
git clone https://github.com/Travis-Prall/court-listener-mcp
cd CourtListener
cp .env.example .env
# Edit .env and add your COURTLISTENER_API_TOKEN
uv sync
uv run start
```
**MCP Config** (add to Claude Desktop settings or .mcp.json):
```json
{
  "courtlistener": {
    "type": "url",
    "url": "http://localhost:8000/mcp/"
  }
}
```

### 2. Web Search (Built-in)
**What it does**: Real-time lookups on Cornell LII, Justia, California Legislature, Idaho Legislature, and other free legal databases.
**Free?**: Yes — included with Claude
**Install**: Already available in Claude Desktop / Cowork
**Use for**: Statute text, regulation lookups, recent legal news, court websites

### 3. Google Drive (Built-in)
**What it does**: Search and retrieve legal documents stored in your Google Drive.
**Free?**: Yes — included with Claude when Google Workspace connector is enabled
**Install**: Enable in Claude Desktop → Settings → Connectors → Google Workspace
**Use for**: Your personal legal documents, contracts, estate planning files

### 4. Filesystem Access (Built-in in Cowork)
**What it does**: Read/write files in designated folders on your Mac.
**Free?**: Yes — included with Cowork
**Install**: Grant folder access when starting a Cowork task
**Use for**: Reading uploaded contracts, saving research memos, organizing legal files

## Optional Connectors (Enhanced Capabilities)

### 5. Google Scholar MCP Server
**What it does**: Search Google Scholar for legal opinions and academic legal scholarship.
**Free?**: Yes — uses Google Scholar web interface
**Install**:
```bash
git clone https://github.com/yourusername/google-scholar-mcp
cd google-scholar-mcp
pip install -r requirements.txt
```
**Note**: Rate-limited by Google. Use CourtListener as primary case law source.

### 6. Anthropic Legal Plugin (Official Baseline)
**What it does**: Anthropic's official legal plugin for Cowork. Covers contract review, NDA triage, compliance workflows.
**Free?**: Yes (with Claude Pro/Max/Team/Enterprise subscription)
**Install**:
```bash
claude plugin marketplace add anthropics/knowledge-work-plugins
claude plugin install legal@knowledge-work-plugins
```
**Note**: This is a great starting point that Dewey Cheatem extends significantly with case law research, jurisdiction-specific knowledge, and citation verification capabilities.

## Connector Status

| Connector | Status | Required? | Cost |
|-----------|--------|-----------|------|
| CourtListener MCP | ✅ Installed (run `uv sync && uv run python -m app.server` from CourtListener/) | **Yes** | Free |
| Web Search | Built-in | **Yes** | Free |
| Google Drive | Built-in | Recommended | Free |
| Filesystem | Built-in (Cowork) | **Yes** | Free |
| Google Scholar MCP | Install needed | Optional | Free |
| Anthropic Legal Plugin | Install via CLI | Optional | Free |

## Setup Checklist
- [x] Register for free CourtListener account and get API token
- [x] Clone and set up CourtListener MCP server (installed in CourtListener/ subfolder, .env configured)
- [ ] Enable Google Workspace connector in Claude Desktop
- [ ] Grant filesystem access to your legal documents folder
- [ ] (Optional) Install Google Scholar MCP
- [ ] (Optional) Install Anthropic's official legal plugin as a base layer

## First Run
To start the CourtListener MCP server on your Mac:
```bash
cd "/Users/johnyork/My Drive/Ridgemont Studio/Claude Cowork/dewey-cheatem-esq/CourtListener"
uv sync       # one-time: installs Python dependencies
uv pip install markdown   # one-time: missing dependency fix
uv run python -m app.server --transport http   # starts server at http://localhost:8000/mcp/
```
