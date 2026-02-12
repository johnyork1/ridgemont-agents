# X API MCP Server Setup Guide

## Why This Matters
Currently the X posting workflow relies on browser automation (clicking through X's UI). An X API MCP server lets Claude post directly via API — faster, more reliable, no UI breakage.

## Step 1: Get X API Developer Credentials (Free Tier)

1. Go to https://developer.x.com
2. Sign in with your @4_Bchainbasics X account
3. Click "Apply" and answer the questions about your use case
4. Accept the Developer Agreement and submit
5. Check email for verification from `developer-accounts@x.com`

### Get Your API Keys
1. Go to https://console.x.com
2. Navigate to your App → "Keys and tokens"
3. Generate and copy these 4 values:
   - **API Key** (Consumer Key)
   - **API Secret Key** (Consumer Secret)
   - **Access Token**
   - **Access Token Secret**

### Free Tier Limitations
- 1,500 posts/month (plenty for daily posting)
- Write-only — can POST tweets but NOT search/read via API
- For searching, you'll still need browser automation or upgrade to Basic ($200/mo)

## Step 2: Install the MCP Server

### Recommended: mbelinky/x-mcp-server
Most feature-complete option. Supports posting, searching, media uploads, rate limiting.

**Option A — npx (simplest, no install needed):**
The MCP config below uses npx to run the server on demand.

**Option B — Clone locally:**
```bash
cd ~/
git clone https://github.com/mbelinky/x-mcp-server.git
cd x-mcp-server
npm install
npm run build
```

## Step 3: Configure in Claude Desktop / Cowork

Edit: `~/Library/Application Support/Claude/claude_desktop_config.json`

Add to the `mcpServers` section:

```json
{
  "mcpServers": {
    "x-api": {
      "command": "npx",
      "args": ["-y", "@mbelinky/x-mcp-server"],
      "env": {
        "API_KEY": "YOUR_API_KEY_HERE",
        "API_SECRET_KEY": "YOUR_API_SECRET_HERE",
        "ACCESS_TOKEN": "YOUR_ACCESS_TOKEN_HERE",
        "ACCESS_TOKEN_SECRET": "YOUR_ACCESS_TOKEN_SECRET_HERE"
      }
    }
  }
}
```

If you cloned locally instead:
```json
{
  "mcpServers": {
    "x-api": {
      "command": "node",
      "args": ["/Users/johnyork/x-mcp-server/dist/index.js"],
      "env": {
        "API_KEY": "YOUR_API_KEY_HERE",
        "API_SECRET_KEY": "YOUR_API_SECRET_HERE",
        "ACCESS_TOKEN": "YOUR_ACCESS_TOKEN_HERE",
        "ACCESS_TOKEN_SECRET": "YOUR_ACCESS_TOKEN_SECRET_HERE"
      }
    }
  }
}
```

## Step 4: Restart and Verify

1. Completely quit Claude Desktop (Cmd+Q)
2. Reopen Claude Desktop
3. In a new conversation, ask Claude to post a test tweet
4. If it works, the X API MCP is connected

## What This Enables
- Direct tweet posting without browser automation
- Faster execution (API call vs UI clicks)
- More reliable (no DOM selectors to break)
- Rate limit awareness

## What Still Needs Browser Automation
- Quote tweeting (not fully supported in free tier API)
- Searching X for trending posts (free tier is write-only)
- Scheduling posts (X API doesn't have a scheduling endpoint — would need browser UI or a separate scheduler)

## Impact on Workflow
Once set up, the daily X post workflow will:
- Use X API MCP for posting original tweets (Steps 6, 8)
- Still use Claude in Chrome for searching trending posts (Step 4) and scheduling (Step 8)
- Still use Claude in Chrome for quote posting (Step 5) until API support improves
