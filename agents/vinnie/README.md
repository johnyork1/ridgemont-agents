# 🩺 Dr. Vinnie Boombatz — Medical AI Agent Plugin

**Version**: 1.0.0  
**Platform**: Claude Cowork (Claude Desktop, macOS) — Opus 4.6  
**Author**: John York / Ridgemont Studio  

---

## What Is This?

Dr. Vinnie Boombatz is a comprehensive medical AI agent plugin for Claude Cowork that transforms Claude into a medical knowledge powerhouse. It combines 10 specialized medical skills, 8 slash commands, a dedicated research sub-agent, and connectors to PubMed and web search to deliver evidence-based medical information, research synthesis, and AI-in-medicine expertise.

**⚠️ IMPORTANT DISCLAIMER**: This agent provides medical *information* and *education*, NOT medical *advice*. It is not a substitute for professional medical consultation. Always consult qualified healthcare providers for personal medical decisions.

---

## Plugin Structure

```
dr-vinnie-boombatz/
├── .claude-plugin/
│   └── plugin.json          # Plugin manifest (name, version, metadata)
├── .mcp.json                # MCP connector configuration
├── CLAUDE.md                # Agent persona & behavioral instructions
├── README.md                # This file
├── agents/
│   └── medical-researcher.md # Research sub-agent for deep lit reviews
├── commands/
│   ├── differential.md       # /dr-vinnie-boombatz:differential
│   ├── drug-lookup.md        # /dr-vinnie-boombatz:drug-lookup
│   ├── research-review.md    # /dr-vinnie-boombatz:research-review
│   ├── interpret-labs.md     # /dr-vinnie-boombatz:interpret-labs
│   ├── ai-medicine-update.md # /dr-vinnie-boombatz:ai-medicine-update
│   ├── patient-explainer.md  # /dr-vinnie-boombatz:patient-explainer
│   ├── interaction-check.md  # /dr-vinnie-boombatz:interaction-check
│   └── screening.md          # /dr-vinnie-boombatz:screening
└── skills/
    ├── clinical-diagnosis/SKILL.md    # Diagnostic reasoning & differentials
    ├── pharmacology/SKILL.md          # Drug knowledge & interactions
    ├── medical-research/SKILL.md      # Literature search & evidence appraisal
    ├── ai-medical-advances/SKILL.md   # AI/ML in healthcare (flagship)
    ├── patient-education/SKILL.md     # Plain-language health education
    ├── emergency-medicine/SKILL.md    # Emergency recognition & protocols
    ├── lab-interpretation/SKILL.md    # Lab result interpretation
    ├── medical-imaging/SKILL.md       # Radiology & imaging guidance
    ├── preventive-medicine/SKILL.md   # Screening & prevention guidelines
    └── mental-health/SKILL.md         # Psychiatry & behavioral health
```

---

## Skills (10) — Auto-Activate Based on Context

| Skill | Triggers On |
|-------|------------|
| **Clinical Diagnosis** | Symptoms, conditions, differential diagnosis, diagnostic workups |
| **Pharmacology** | Medications, drug classes, side effects, dosing, interactions |
| **Medical Research** | Study questions, evidence synthesis, clinical trials, guidelines |
| **AI Medical Advances** | AI in healthcare, ML diagnostics, digital health, precision medicine |
| **Patient Education** | Plain-language explanations, health literacy, patient handouts |
| **Emergency Medicine** | Emergencies, trauma, acute conditions, triage, ACLS/BLS |
| **Lab Interpretation** | Blood work, lab panels, reference ranges, test results |
| **Medical Imaging** | X-rays, CT, MRI, ultrasound, when to order imaging |
| **Preventive Medicine** | Screenings, immunizations, lifestyle medicine, wellness |
| **Mental Health** | Psychiatric conditions, medications, therapy, crisis support |

---

## Slash Commands (8)

| Command | What It Does |
|---------|-------------|
| `/dr-vinnie-boombatz:differential [symptoms]` | Generate structured differential diagnosis |
| `/dr-vinnie-boombatz:drug-lookup [medication]` | Comprehensive drug information |
| `/dr-vinnie-boombatz:research-review [topic]` | Deep PubMed + web literature review |
| `/dr-vinnie-boombatz:interpret-labs [results]` | Interpret lab values in clinical context |
| `/dr-vinnie-boombatz:ai-medicine-update [topic]` | Latest AI-in-medicine breakthroughs |
| `/dr-vinnie-boombatz:patient-explainer [condition]` | Patient-friendly condition explanation |
| `/dr-vinnie-boombatz:interaction-check [drug list]` | Drug interaction analysis |
| `/dr-vinnie-boombatz:screening [age/sex/risk]` | Personalized screening recommendations |

---

## Connectors

### Active (Built-in)
- **PubMed** — 36M+ biomedical articles, full-text from PMC
- **Web Search** — Real-time medical news, FDA approvals, AI breakthroughs
- **Google Drive** — Personal medical reference library
- **Local Files** — Read/write reports and documents

### Recommended Future Additions (when MCP servers available)
- ClinicalTrials.gov, FDA OpenFDA, RxNorm, UMLS, SNOMED-CT, ICD-11, LOINC
- UpToDate, Cochrane Library (subscription-based)
- Notion/Obsidian (if using for medical knowledge base)

---

## Installation

### Option A: Direct folder install
1. Copy the entire `dr-vinnie-boombatz/` folder to your Claude plugins directory:
   ```
   ~/.claude/plugins/dr-vinnie-boombatz/
   ```
2. Restart Claude Desktop

### Option B: From your project folder
1. In Claude Cowork, grant access to the folder containing this plugin
2. Tell Claude: "Install the dr-vinnie-boombatz plugin from this folder"

### Option C: Via Claude Code CLI
```bash
claude plugin install dr-vinnie-boombatz --path "/Users/johnyork/My Drive/Ridgemont Studio/Claude Cowork/dr-vinnie-boombatz"
```

---

## Quick Start — Cowork Task Command

Once installed, switch to the **Tasks** tab in Claude Desktop and try:

```
You are Dr. Vinnie Boombatz. Search PubMed for the latest systematic reviews 
on GLP-1 receptor agonists for weight management published in the last 12 months. 
Summarize the key findings, note any new safety signals, and highlight any 
AI-assisted analysis in these studies. Save a report to my working folder.
```

---

## Example Prompts

**Clinical Question:**
> "What's the current evidence on SGLT2 inhibitors for heart failure in patients without diabetes?"

**Drug Lookup:**
> `/dr-vinnie-boombatz:drug-lookup semaglutide`

**AI Medicine:**
> `/dr-vinnie-boombatz:ai-medicine-update radiology AI FDA clearances 2025-2026`

**Lab Interpretation:**
> `/dr-vinnie-boombatz:interpret-labs WBC 15.2, CRP 85, Procalcitonin 2.1, Lactate 3.5 in a 67yo with fever and confusion`

**Patient Education:**
> `/dr-vinnie-boombatz:patient-explainer type 2 diabetes`

---

## Customization

This plugin is entirely file-based (Markdown + JSON). To customize:

- **Add specialty knowledge**: Create new `skills/[specialty]/SKILL.md` files
- **Add new commands**: Create new `commands/[name].md` files  
- **Connect more tools**: Edit `.mcp.json` to add MCP servers
- **Adjust persona**: Edit `CLAUDE.md` to change tone, focus areas, or disclaimers
- **Add sub-agents**: Create new `agents/[name].md` for specialized tasks

---

## License & Disclaimer

This plugin is for personal educational use. It does not provide medical advice. All medical information should be verified with qualified healthcare professionals. The author assumes no liability for decisions made based on information from this agent.
