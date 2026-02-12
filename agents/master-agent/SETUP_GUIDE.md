# Master Agent — Setup Guide

## What You're Setting Up

A fully automated daily monitoring system for your Cowork agent ecosystem. Every morning at 7 AM, your Mac will:

1. Auto-discover all agent folders (new agents are picked up automatically)
2. Update the registry without any manual editing
3. Scan all agent folders for file changes
4. Send the data to Claude's API for intelligent analysis
5. Generate an audit report with health scores and recommendations
6. Email you the report
7. Save a log so you have a history of changes over time

---

## Folder Structure

After setup, your Master Agent folder should look like this:

```
Master Agent/
├── RULES.md                   ← Rules for using this as a Cowork agent
├── SETUP_GUIDE.md             ← This file
├── data/
│   ├── agent_registry.json    ← Auto-populated (never edit manually)
│   ├── audit_template.md      ← Template for daily reports
│   ├── evaluation_criteria.md ← Scoring rubrics
│   └── last_audit.json        ← Auto-generated snapshot (don't edit)
├── scripts/
│   ├── daily_monitor.py                          ← The automation script
│   └── com.ridgemont.masteragent.monitor.plist   ← macOS scheduler
├── skills/                    ← Reserved for future Cowork skills
└── logs/                      ← Daily reports saved here
    └── audit_2026-02-07.md    ← Example log file
```

---

## Step-by-Step Setup

### Step 1: Get an Anthropic API Key

1. Go to https://console.anthropic.com
2. Create an account or sign in
3. Go to API Keys and create a new key
4. Copy the key — you'll need it in Step 3

Note: API usage costs money. Each daily audit will use roughly $0.03-0.10 depending on how much data your agents contain. That's about $1-3/month.

### Step 2: Set Up Gmail App Password (for email delivery)

1. Go to https://myaccount.google.com/security
2. Enable 2-Factor Authentication if not already on
3. Go to https://myaccount.google.com/apppasswords
4. Create a new App Password for "Mail" on "Mac"
5. Copy the 16-character password

If you prefer not to use email, the script will still save reports to the `logs/` folder. You can skip this step.

### Step 3: Install the Python Dependency

Open Terminal and run:

```bash
pip3 install anthropic
```

### Step 4: Test the Script Manually

Open Terminal and run:

```bash
# Set your API key
export ANTHROPIC_API_KEY="sk-ant-your-key-here"

# Optional: set email credentials
export EMAIL_SENDER="your_email@gmail.com"
export EMAIL_PASSWORD="your-gmail-app-password"
export EMAIL_RECIPIENT="your_email@gmail.com"

# Run the monitor
python3 "/Users/johnyork/My Drive/Ridgemont Studio/Claude Cowork/Master Agent/scripts/daily_monitor.py"
```

Check the output. If it works, you'll see a report saved in the `logs/` folder and (if email is configured) receive an email.

### Step 5: Schedule Daily Automation

1. Edit the plist file to add your credentials:

```bash
nano "/Users/johnyork/My Drive/Ridgemont Studio/Claude Cowork/Master Agent/scripts/com.ridgemont.masteragent.monitor.plist"
```

Replace these placeholders:
- `YOUR_API_KEY_HERE` → Your Anthropic API key
- `your_email@gmail.com` → Your actual email
- `YOUR_GMAIL_APP_PASSWORD_HERE` → Your Gmail App Password

2. Copy the plist to LaunchAgents:

```bash
cp "/Users/johnyork/My Drive/Ridgemont Studio/Claude Cowork/Master Agent/scripts/com.ridgemont.masteragent.monitor.plist" \
   ~/Library/LaunchAgents/com.ridgemont.masteragent.monitor.plist
```

3. Load it:

```bash
launchctl load ~/Library/LaunchAgents/com.ridgemont.masteragent.monitor.plist
```

4. Test it:

```bash
launchctl start com.ridgemont.masteragent.monitor
```

### Step 6: Verify

Check these locations:
- `logs/` folder for the audit report
- Your email inbox for the daily report
- `logs/monitor_stdout.log` for script output
- `logs/monitor_stderr.log` for any errors

---

## Using the Master Agent in Cowork (Manual Mode)

You can also use the Master Agent directly in Cowork as a regular agent. Open the Master Agent folder in Claude Desktop Cowork and use the first command below to kick it off.

---

## Adding New Agents

Just create a new agent folder in your Cowork directory as you normally would. The next time the daily monitor runs (or you run a manual audit in Cowork), the new agent will be auto-discovered, added to the registry, and included in the analysis. You never need to update the registry manually.

---

## Troubleshooting

**Script won't run:** Check that python3 is at `/usr/bin/python3`. Run `which python3` to verify.

**API errors:** Verify your API key is valid at https://console.anthropic.com. Check that you have credits/billing set up.

**Email not sending:** Double-check your Gmail App Password. Regular passwords won't work — you need the 16-character App Password.

**LaunchAgent not firing:** Check `logs/monitor_stderr.log`. Also try `launchctl list | grep masteragent` to confirm it's loaded.

**Laptop was asleep at 7 AM:** The `MisfireGracePeriod` setting will run the script within 1 hour of waking up. Your Mac does need to be powered on.
