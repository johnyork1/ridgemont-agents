#!/usr/bin/env python3
"""
Master Agent — Automated Daily Monitor
Scans all Cowork agent folders, auto-discovers new agents, sends contents
to Claude API for analysis, and emails the audit report to John.

Setup:
  1. pip3 install anthropic
  2. Set environment variables (see CONFIG section below)
  3. Test: python3 daily_monitor.py
  4. Schedule with macOS launchd (see com.ridgemont.masteragent.monitor.plist)
"""

import os
import json
import hashlib
import smtplib
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ============================================================
# CONFIG — Update these values for your environment
# ============================================================

# Path to your Cowork folder containing all agent subfolders
COWORK_ROOT = os.environ.get("COWORK_ROOT", "/Users/johnyork/My Drive/Ridgemont Studio/Claude Cowork")

# Path to the Master Agent folder
MASTER_AGENT_DIR = os.environ.get("MASTER_AGENT_DIR", os.path.join(COWORK_ROOT, "Master Agent"))

# Anthropic API key — set as environment variable for security
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# Email configuration — uses Gmail App Password by default
# To use Gmail: enable 2FA, then create an App Password at https://myaccount.google.com/apppasswords
EMAIL_SENDER = os.environ.get("EMAIL_SENDER", "your_email@gmail.com")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD", "")  # Gmail App Password
EMAIL_RECIPIENT = os.environ.get("EMAIL_RECIPIENT", "your_email@gmail.com")
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))

# Claude model to use for analysis
CLAUDE_MODEL = "claude-sonnet-4-20250514"

# Files/folders to ignore when scanning
IGNORE_PATTERNS = {".DS_Store", "__pycache__", ".git", "node_modules", ".env"}

# Max file size to read (in bytes) — skip very large files
MAX_FILE_SIZE = 500_000  # 500KB


# ============================================================
# AUTO-DISCOVERY & REGISTRY MANAGEMENT
# ============================================================

# Folders to exclude from agent discovery (not actual agents)
EXCLUDED_FOLDERS = {".skills", "Master Agent", "Master_Agent", "__pycache__", ".git", "node_modules"}

# File extensions that indicate a folder is NOT an agent (add as needed)
NON_AGENT_INDICATORS = set()


def discover_agent_folders() -> list[str]:
    """Scan the Cowork root and return a list of agent folder names."""
    agent_folders = []
    if not os.path.exists(COWORK_ROOT):
        return agent_folders

    for item in sorted(os.listdir(COWORK_ROOT)):
        item_path = os.path.join(COWORK_ROOT, item)
        if (
            os.path.isdir(item_path)
            and item not in EXCLUDED_FOLDERS
            and item not in IGNORE_PATTERNS
            and not item.startswith(".")
        ):
            agent_folders.append(item)

    return agent_folders


def auto_update_registry(registry_path: str) -> dict:
    """
    Auto-update the agent registry:
    - Load existing registry (preserves any metadata you've manually added)
    - Discover all current agent folders on disk
    - Add new agents automatically
    - Mark removed agents as 'removed'
    - Save updated registry back to disk
    """
    # Load existing registry
    registry = {"registry_version": "1.0", "cowork_root_path": COWORK_ROOT, "agents": []}
    if os.path.exists(registry_path):
        try:
            with open(registry_path, "r") as f:
                registry = json.load(f)
        except (json.JSONDecodeError, OSError):
            pass

    # Build lookup of existing agents by folder name
    existing_by_folder = {}
    for agent in registry.get("agents", []):
        existing_by_folder[agent.get("folder_name", "")] = agent

    # Discover current folders on disk
    current_folders = discover_agent_folders()

    # Build updated agent list
    updated_agents = []
    next_id = len(registry.get("agents", [])) + 1

    for folder_name in current_folders:
        folder_path = os.path.join(COWORK_ROOT, folder_name)

        if folder_name in existing_by_folder:
            # Existing agent — preserve all manually-added metadata
            agent = existing_by_folder[folder_name]
            if agent.get("status") == "removed":
                agent["status"] = "active"
                agent["notes"] = agent.get("notes", "") + f" | Re-detected on {datetime.now().strftime('%Y-%m-%d')}."

            # Update last_modified from disk
            try:
                mtime = os.path.getmtime(folder_path)
                agent["last_modified"] = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
            except OSError:
                pass

            updated_agents.append(agent)
            print(f"  ✓ Existing: {folder_name}")
        else:
            # New agent — auto-create registry entry
            new_agent = {
                "id": f"agent_{next_id:02d}",
                "name": folder_name,
                "folder_name": folder_name,
                "folder_path": folder_path,
                "purpose": "AUTO-DISCOVERED — purpose not yet defined. Review and update.",
                "primary_workflows": [],
                "key_data_files": [],
                "rules_file": "RULES.md",
                "skills": [],
                "data_sources": [],
                "dependencies": [],
                "related_agents": [],
                "usage_frequency": "unknown",
                "last_modified": datetime.now().strftime("%Y-%m-%d"),
                "status": "new",
                "notes": f"Auto-discovered on {datetime.now().strftime('%Y-%m-%d')}. Needs review."
            }
            updated_agents.append(new_agent)
            next_id += 1
            print(f"  ★ NEW AGENT DISCOVERED: {folder_name}")

    # Check for removed agents (folder no longer exists)
    for folder_name, agent in existing_by_folder.items():
        if folder_name not in current_folders:
            agent["status"] = "removed"
            agent["notes"] = (agent.get("notes", "") +
                              f" | Folder not found on disk as of {datetime.now().strftime('%Y-%m-%d')}.")
            updated_agents.append(agent)
            print(f"  ✗ REMOVED: {folder_name} (folder no longer exists)")

    # Update registry
    registry["agents"] = updated_agents
    registry["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    registry["total_agents"] = len([a for a in updated_agents if a["status"] != "removed"])

    # Save updated registry
    os.makedirs(os.path.dirname(registry_path), exist_ok=True)
    with open(registry_path, "w") as f:
        json.dump(registry, f, indent=2)
    print(f"  Registry saved with {registry['total_agents']} active agents\n")

    return registry


# ============================================================
# FILE SCANNING
# ============================================================

def get_file_hash(filepath: str) -> str:
    """Generate MD5 hash of a file for change detection."""
    hasher = hashlib.md5()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except (OSError, PermissionError):
        return "unreadable"


def scan_agent_folder(agent_path: str) -> dict:
    """Scan an agent folder and return its structure and file metadata."""
    agent_data = {
        "path": agent_path,
        "name": os.path.basename(agent_path),
        "files": [],
        "total_files": 0,
        "total_size_bytes": 0,
    }

    for root, dirs, files in os.walk(agent_path):
        # Skip ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORE_PATTERNS]

        for filename in files:
            if filename in IGNORE_PATTERNS:
                continue

            filepath = os.path.join(root, filename)
            relative_path = os.path.relpath(filepath, agent_path)

            try:
                stat = os.stat(filepath)
                file_info = {
                    "relative_path": relative_path,
                    "size_bytes": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "hash": get_file_hash(filepath),
                    "content": None,
                }

                # Read file content if it's small enough and text-based
                text_extensions = {
                    ".md", ".txt", ".json", ".yaml", ".yml", ".py",
                    ".js", ".csv", ".xml", ".html", ".css", ".toml",
                    ".cfg", ".ini", ".sh", ".bat", ".rules"
                }
                ext = os.path.splitext(filename)[1].lower()
                if ext in text_extensions and stat.st_size < MAX_FILE_SIZE:
                    try:
                        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                            file_info["content"] = f.read()
                    except (OSError, UnicodeDecodeError):
                        file_info["content"] = "[Could not read file]"

                agent_data["files"].append(file_info)
                agent_data["total_files"] += 1
                agent_data["total_size_bytes"] += stat.st_size

            except OSError:
                continue

    return agent_data


def scan_all_agents() -> list[dict]:
    """Scan all agent folders in the Cowork root directory."""
    agents = []

    if not os.path.exists(COWORK_ROOT):
        print(f"ERROR: Cowork root not found: {COWORK_ROOT}")
        return agents

    for item in sorted(os.listdir(COWORK_ROOT)):
        item_path = os.path.join(COWORK_ROOT, item)
        if (
            os.path.isdir(item_path)
            and item not in EXCLUDED_FOLDERS
            and item not in IGNORE_PATTERNS
            and not item.startswith(".")
        ):
            print(f"  Scanning: {item}")
            agents.append(scan_agent_folder(item_path))

    return agents


# ============================================================
# CHANGE DETECTION
# ============================================================

SNAPSHOT_FILE = os.path.join(MASTER_AGENT_DIR, "data", "last_audit.json")


def load_previous_snapshot() -> dict:
    """Load the previous audit snapshot for comparison."""
    if os.path.exists(SNAPSHOT_FILE):
        try:
            with open(SNAPSHOT_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def save_snapshot(agents: list[dict]):
    """Save current scan as snapshot for next comparison."""
    snapshot = {}
    for agent in agents:
        agent_files = {}
        for f in agent["files"]:
            agent_files[f["relative_path"]] = {
                "hash": f["hash"],
                "size": f["size_bytes"],
                "modified": f["modified"],
            }
        snapshot[agent["name"]] = agent_files

    os.makedirs(os.path.dirname(SNAPSHOT_FILE), exist_ok=True)
    with open(SNAPSHOT_FILE, "w") as f:
        json.dump(snapshot, f, indent=2)


def detect_changes(agents: list[dict], previous: dict) -> list[dict]:
    """Compare current scan against previous snapshot to detect changes."""
    changes = []

    for agent in agents:
        agent_name = agent["name"]
        prev_files = previous.get(agent_name, {})
        curr_files = {f["relative_path"]: f for f in agent["files"]}

        # New files
        for path in curr_files:
            if path not in prev_files:
                changes.append({
                    "agent": agent_name,
                    "file": path,
                    "type": "ADDED",
                    "details": f"New file ({curr_files[path]['size_bytes']} bytes)",
                })

        # Deleted files
        for path in prev_files:
            if path not in curr_files:
                changes.append({
                    "agent": agent_name,
                    "file": path,
                    "type": "DELETED",
                    "details": "File removed",
                })

        # Modified files
        for path in curr_files:
            if path in prev_files:
                if curr_files[path]["hash"] != prev_files[path]["hash"]:
                    changes.append({
                        "agent": agent_name,
                        "file": path,
                        "type": "MODIFIED",
                        "details": f"Hash changed (modified: {curr_files[path]['modified']})",
                    })

    # New agents
    curr_agent_names = {a["name"] for a in agents}
    prev_agent_names = set(previous.keys())
    for name in curr_agent_names - prev_agent_names:
        changes.append({
            "agent": name,
            "file": "(entire agent)",
            "type": "NEW_AGENT",
            "details": "New agent folder detected",
        })
    for name in prev_agent_names - curr_agent_names:
        changes.append({
            "agent": name,
            "file": "(entire agent)",
            "type": "REMOVED_AGENT",
            "details": "Agent folder no longer exists",
        })

    return changes


# ============================================================
# CLAUDE API ANALYSIS
# ============================================================

def analyze_with_claude(agents: list[dict], changes: list[dict], registry: dict) -> str:
    """Send agent data to Claude API for analysis and get audit report."""
    try:
        import anthropic
    except ImportError:
        return "ERROR: anthropic package not installed. Run: pip3 install anthropic"

    if not ANTHROPIC_API_KEY:
        return "ERROR: ANTHROPIC_API_KEY environment variable not set."

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    # Load evaluation criteria and audit template
    eval_criteria_path = os.path.join(MASTER_AGENT_DIR, "data", "evaluation_criteria.md")
    audit_template_path = os.path.join(MASTER_AGENT_DIR, "data", "audit_template.md")

    eval_criteria = ""
    audit_template = ""
    try:
        with open(eval_criteria_path, "r") as f:
            eval_criteria = f.read()
    except OSError:
        eval_criteria = "(Evaluation criteria file not found)"

    try:
        with open(audit_template_path, "r") as f:
            audit_template = f.read()
    except OSError:
        audit_template = "(Audit template not found)"

    # Build the analysis prompt
    # Summarize agents to stay within token limits
    agent_summaries = []
    for agent in agents:
        summary = {
            "name": agent["name"],
            "total_files": agent["total_files"],
            "total_size_bytes": agent["total_size_bytes"],
            "files": [],
        }
        for f in agent["files"]:
            file_entry = {
                "path": f["relative_path"],
                "size": f["size_bytes"],
                "modified": f["modified"],
            }
            # Include content for rules/config files, truncate others
            if f["content"]:
                if any(keyword in f["relative_path"].lower() for keyword in
                       ["rules", "readme", "config", "skill", "instructions"]):
                    file_entry["content"] = f["content"][:5000]
                else:
                    file_entry["content"] = f["content"][:1000] + "\n...(truncated)"
            summary["files"].append(file_entry)
        agent_summaries.append(summary)

    # Identify new and removed agents for the prompt
    new_agents = [a["name"] for a in registry.get("agents", []) if a.get("status") == "new"]
    removed_agents = [a["name"] for a in registry.get("agents", []) if a.get("status") == "removed"]

    new_agents_note = ""
    if new_agents:
        new_agents_note = f"\n\n## ⚠️ NEWLY DISCOVERED AGENTS (give extra attention)\nThese agents were just auto-discovered and need initial evaluation: {', '.join(new_agents)}\nFor each new agent, analyze its rules and files to determine its purpose, suggest related agents, and flag any potential overlaps with existing agents."
    if removed_agents:
        new_agents_note += f"\n\n## ⚠️ REMOVED AGENTS\nThese agents no longer exist on disk: {', '.join(removed_agents)}\nNote any dependencies that may be broken."

    prompt = f"""You are the Master Agent — an orchestrator evaluating John's Cowork agent ecosystem.

Today's date: {datetime.now().strftime('%Y-%m-%d')}
{new_agents_note}

## Agent Registry
```json
{json.dumps(registry, indent=2)[:3000]}
```

## Current Agent Scan Data
```json
{json.dumps(agent_summaries, indent=2)[:15000]}
```

## Changes Since Last Audit
```json
{json.dumps(changes, indent=2)[:3000]}
```

## Evaluation Criteria
{eval_criteria[:3000]}

## Your Task
Generate a comprehensive daily audit report following this template structure:
{audit_template[:2000]}

Fill in ALL sections with specific, actionable analysis. Score each agent. Identify merge/split candidates.
Be direct and specific — John wants concrete recommendations, not vague observations.

If this is the first audit (no changes detected because no previous snapshot), note that and focus on
the structural analysis of each agent based on their rules and file organization."""

    try:
        message = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text
    except Exception as e:
        return f"ERROR calling Claude API: {str(e)}"


# ============================================================
# EMAIL DELIVERY
# ============================================================

def send_email(subject: str, body: str):
    """Send the audit report via email."""
    if not EMAIL_PASSWORD:
        print("WARNING: EMAIL_PASSWORD not set. Skipping email delivery.")
        print("Report saved to logs folder instead.")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECIPIENT

    # Plain text version
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECIPIENT, msg.as_string())
        print(f"Email sent to {EMAIL_RECIPIENT}")
        return True
    except Exception as e:
        print(f"ERROR sending email: {e}")
        return False


# ============================================================
# MAIN EXECUTION
# ============================================================

def main():
    """Run the daily monitoring pipeline."""
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"=== Master Agent Daily Monitor — {today} ===\n")

    # Step 1: Auto-discover agents and update registry
    print("Step 1: Auto-discovering agents and updating registry...")
    registry_path = os.path.join(MASTER_AGENT_DIR, "data", "agent_registry.json")
    registry = auto_update_registry(registry_path)

    # Step 2: Scan all agent folders
    print("Step 2: Scanning agent folders...")
    agents = scan_all_agents()
    print(f"  Found {len(agents)} agent folders\n")

    # Step 3: Detect changes
    print("Step 3: Detecting changes since last audit...")
    previous_snapshot = load_previous_snapshot()
    changes = detect_changes(agents, previous_snapshot)
    print(f"  Detected {len(changes)} changes\n")

    # Step 4: Analyze with Claude
    print("Step 4: Sending data to Claude for analysis...")
    report = analyze_with_claude(agents, changes, registry)
    print("  Analysis complete\n")

    # Step 5: Save report to logs
    print("Step 5: Saving report...")
    logs_dir = os.path.join(MASTER_AGENT_DIR, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    report_path = os.path.join(logs_dir, f"audit_{today}.md")
    with open(report_path, "w") as f:
        f.write(report)
    print(f"  Report saved: {report_path}\n")

    # Step 6: Save snapshot for next run
    print("Step 6: Saving snapshot for change detection...")
    save_snapshot(agents)
    print(f"  Snapshot saved: {SNAPSHOT_FILE}\n")

    # Step 7: Send email
    print("Step 7: Sending email report...")
    subject = f"🤖 Master Agent Audit — {today} | {len(changes)} changes detected"
    email_sent = send_email(subject, report)

    if not email_sent:
        print(f"\n📋 Report available at: {report_path}")

    print(f"\n=== Audit complete ===")


if __name__ == "__main__":
    main()
