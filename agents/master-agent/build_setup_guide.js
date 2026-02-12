const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
        ShadingType, PageNumber, PageBreak, LevelFormat } = require('docx');

const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };
const cellMargins = { top: 80, bottom: 80, left: 120, right: 120 };

function cell(text, width, opts = {}) {
  const runs = Array.isArray(text) ? text : [new TextRun({ text, font: "Arial", size: 20, ...opts })];
  return new TableCell({
    borders,
    width: { size: width, type: WidthType.DXA },
    margins: cellMargins,
    shading: opts.header ? { fill: "1A1E24", type: ShadingType.CLEAR } : undefined,
    children: [new Paragraph({ children: runs })]
  });
}

function headerCell(text, width) {
  return cell([new TextRun({ text, font: "Arial", size: 20, bold: true, color: "7DBBFF" })], width, { header: true });
}

function row(cells) { return new TableRow({ children: cells }); }

function heading(text, level) {
  return new Paragraph({ heading: level, children: [new TextRun({ text, font: "Arial" })] });
}

function para(text, opts = {}) {
  return new Paragraph({
    spacing: { after: 120 },
    children: [new TextRun({ text, font: "Arial", size: 22, ...opts })]
  });
}

function stepPara(num, text) {
  return new Paragraph({
    spacing: { after: 80 },
    children: [
      new TextRun({ text: `Step ${num}: `, font: "Arial", size: 22, bold: true }),
      new TextRun({ text, font: "Arial", size: 22 })
    ]
  });
}

function agentSection(name, folder, purpose, rulesFile, connectors, skills, slashCmds) {
  const children = [
    heading(name, HeadingLevel.HEADING_2),
    para(`Folder: ${folder}`, { italics: true, color: "666666" }),
    para(purpose),
    new Paragraph({ spacing: { after: 40 }, children: [new TextRun({ text: "Setup Steps:", font: "Arial", size: 22, bold: true })] }),
    stepPara(1, `Open the Claude desktop app and start a new Cowork task.`),
    stepPara(2, `Click "Select folder" and navigate to: My Drive \u2192 Ridgemont Studio \u2192 Claude Cowork \u2192 ${folder}`),
    stepPara(3, `Select the folder. Claude reads ${rulesFile} and becomes ${name}.`),
  ];

  if (connectors && connectors.length > 0) {
    children.push(new Paragraph({ spacing: { before: 120, after: 40 }, children: [new TextRun({ text: "Connected MCP Connectors:", font: "Arial", size: 22, bold: true })] }));
    connectors.forEach(c => {
      children.push(new Paragraph({ spacing: { after: 40 }, children: [new TextRun({ text: `  \u2022  ${c}`, font: "Arial", size: 20 })] }));
    });
  }

  if (skills && skills.length > 0) {
    children.push(new Paragraph({ spacing: { before: 120, after: 40 }, children: [new TextRun({ text: "Skills & Commands:", font: "Arial", size: 22, bold: true })] }));
    skills.forEach(s => {
      children.push(new Paragraph({ spacing: { after: 40 }, children: [new TextRun({ text: `  \u2022  ${s}`, font: "Arial", size: 20 })] }));
    });
  }

  if (slashCmds && slashCmds.length > 0) {
    children.push(new Paragraph({ spacing: { before: 120, after: 40 }, children: [new TextRun({ text: "Slash Commands:", font: "Arial", size: 22, bold: true })] }));
    slashCmds.forEach(c => {
      children.push(new Paragraph({ spacing: { after: 40 }, children: [new TextRun({ text: `  ${c}`, font: "Arial", size: 20, color: "7DBBFF" })] }));
    });
  }

  children.push(new Paragraph({ children: [new PageBreak()] }));
  return children;
}

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 36, bold: true, font: "Arial", color: "7DBBFF" },
        paragraph: { spacing: { before: 240, after: 240 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: "Arial", color: "163B73" },
        paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, font: "Arial" },
        paragraph: { spacing: { before: 180, after: 80 }, outlineLevel: 2 } },
    ]
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
      }
    },
    headers: {
      default: new Header({
        children: [new Paragraph({
          alignment: AlignmentType.RIGHT,
          children: [new TextRun({ text: "Ridgemont Studio \u2022 Cowork Agent Setup Guide", font: "Arial", size: 16, color: "999999", italics: true })]
        })]
      })
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: "Page ", font: "Arial", size: 16, color: "999999" }), new TextRun({ children: [PageNumber.CURRENT], font: "Arial", size: 16, color: "999999" })]
        })]
      })
    },
    children: [
      // TITLE PAGE
      new Paragraph({ spacing: { before: 3000 } }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 }, children: [new TextRun({ text: "RIDGEMONT STUDIO", font: "Arial", size: 48, bold: true, color: "7DBBFF" })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 400 }, children: [new TextRun({ text: "Cowork Agent Setup Guide", font: "Arial", size: 32, color: "163B73" })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 }, children: [new TextRun({ text: "11 Agents \u2022 21+ MCP Connectors \u2022 Registry v2.8", font: "Arial", size: 22, color: "666666" })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 600 }, children: [new TextRun({ text: "February 8, 2026", font: "Arial", size: 22, color: "999999" })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "How to launch every agent in the Ridgemont Studio Cowork ecosystem.\nEach agent is a folder in your Google Drive. Start a new Cowork task, select the folder, and Claude becomes that agent.", font: "Arial", size: 20, color: "666666" })] }),

      new Paragraph({ children: [new PageBreak()] }),

      // PREREQUISITES
      heading("Before You Start", HeadingLevel.HEADING_1),
      para("All agent folders live at:"),
      para("My Drive \u2192 Ridgemont Studio \u2192 Claude Cowork", { bold: true }),
      new Paragraph({ spacing: { after: 200 } }),

      heading("How to Launch Any Agent", HeadingLevel.HEADING_3),
      stepPara(1, "Open the Claude desktop app."),
      stepPara(2, 'Click the "+" button to start a new Cowork task.'),
      stepPara(3, 'Click "Select folder" when prompted.'),
      stepPara(4, "Navigate to the agent\u2019s folder (listed below for each agent)."),
      stepPara(5, "Select the folder. Claude reads the config file and becomes that agent."),
      new Paragraph({ spacing: { after: 200 } }),

      heading("MCP Connectors (Account-Level)", HeadingLevel.HEADING_3),
      para("These are already installed on your account and available to ALL agents automatically. No per-agent setup needed."),
      new Paragraph({ spacing: { after: 100 } }),

      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [3000, 3000, 3360],
        rows: [
          row([headerCell("Connector", 3000), headerCell("Type", 3000), headerCell("Tools", 3360)]),
          row([cell("Google Drive", 3000), cell("OAuth", 3000), cell("File access", 3360)]),
          row([cell("Gmail", 3000), cell("OAuth", 3000), cell("Email search/read", 3360)]),
          row([cell("Google Calendar", 3000), cell("OAuth", 3000), cell("Calendar events", 3360)]),
          row([cell("GitHub", 3000), cell("OAuth", 3000), cell("Repos, PRs, issues", 3360)]),
          row([cell("LunarCrush", 3000), cell("MCP", 3000), cell("11 tools \u2014 crypto social intel", 3360)]),
          row([cell("Crypto.com", 3000), cell("MCP", 3000), cell("9 tools \u2014 market data", 3360)]),
          row([cell("PubMed", 3000), cell("MCP", 3000), cell("7 tools \u2014 medical research", 3360)]),
          row([cell("ChEMBL", 3000), cell("MCP", 3000), cell("6 tools \u2014 drug/compound data", 3360)]),
          row([cell("Clinical Trials", 3000), cell("MCP", 3000), cell("6 tools \u2014 trial search", 3360)]),
          row([cell("Cloudflare Dev Platform", 3000), cell("MCP", 3000), cell("Workers, D1, R2", 3360)]),
          row([cell("Indeed", 3000), cell("MCP", 3000), cell("Job search", 3360)]),
          row([cell("Play Sheet Music", 3000), cell("MCP", 3000), cell("ABC notation player", 3360)]),
          row([cell("Blockscout", 3000), cell("MCP", 3000), cell("Blockchain explorer", 3360)]),
          row([cell("bioRxiv", 3000), cell("MCP", 3000), cell("Preprint research", 3360)]),
          row([cell("Melon", 3000), cell("MCP", 3000), cell("26 tools \u2014 music charts", 3360)]),
          row([cell("Cloudinary", 3000), cell("MCP", 3000), cell("Image/video management", 3360)]),
          row([cell("Ahrefs", 3000), cell("MCP", 3000), cell("61 tools \u2014 SEO analytics", 3360)]),
          row([cell("Consensus", 3000), cell("MCP", 3000), cell("Scientific paper search", 3360)]),
          row([cell("ICD-10 Codes", 3000), cell("MCP", 3000), cell("9 tools \u2014 medical codes", 3360)]),
          row([cell("Scholar Gateway", 3000), cell("MCP", 3000), cell("Scholarly citations", 3360)]),
          row([cell("Canva", 3000), cell("MCP", 3000), cell("Design generation", 3360)]),
        ]
      }),

      new Paragraph({ children: [new PageBreak()] }),

      // AGENT SECTIONS
      heading("Agent Setup Instructions", HeadingLevel.HEADING_1),
      para("Each section below covers one agent. Follow the 3-step process to launch it."),
      new Paragraph({ spacing: { after: 200 } }),

      // 1. Master Agent
      ...agentSection(
        "Master Agent",
        "Master Agent",
        "Orchestrator and strategic advisor \u2014 auto-discovers agents, maintains the registry, runs daily audits with health scoring, and performs cross-agent analysis and optimization.",
        "RULES.md",
        ["Google Drive", "Gmail", "Google Calendar", "GitHub", "All MCP connectors"],
        ["xlsx (ecosystem dashboards)", "enterprise-search (cross-agent knowledge synthesis)", "skill-creator (build new agent skills)"],
        ["/audit \u2014 run ecosystem health audit", "/deep-dive \u2014 full optimization analysis"]
      ),

      // 2. Dr. Vinnie Boombatz
      ...agentSection(
        "Dr. Vinnie Boombatz",
        "dr-vinnie-boombatz",
        "Comprehensive medical AI agent \u2014 evidence-based medical information, research synthesis, drug lookups, lab interpretation, differential diagnosis, AI-in-medicine expertise. Uses PubMed for clinical evidence. NOT a licensed physician.",
        "CLAUDE.md",
        ["PubMed (36M+ articles)", "ChEMBL (drug/compound data)", "Clinical Trials", "bioRxiv (preprints)", "ICD-10 Codes", "Consensus (scientific papers)", "Scholar Gateway"],
        ["clinical-diagnosis", "pharmacology", "medical-research", "ai-medical-advances", "patient-education", "emergency-medicine", "lab-interpretation", "medical-imaging", "preventive-medicine", "mental-health", "pdf (clinical PDFs)", "docx (medical reports)"],
        ["/research [topic] \u2014 PubMed literature review", "/drug [name] \u2014 drug interaction lookup", "/dx [symptoms] \u2014 differential diagnosis", "/labs [results] \u2014 lab interpretation", "/supplement-protocol \u2014 supplement analysis", "/patient-ed [topic] \u2014 patient education", "/ai-medicine \u2014 AI in medicine updates", "/imaging [findings] \u2014 imaging interpretation"]
      ),

      // 3. Dewey Cheatem, Esq.
      ...agentSection(
        "Dewey Cheatem, Esq.",
        "dewey-cheatem-esq",
        "Legal research and advisory agent for U.S. Federal, California, and Idaho law \u2014 case law research via CourtListener, statute lookup, contract review, IRAC analysis, citation verification. NOT a licensed attorney.",
        "CLAUDE.md",
        ["CourtListener REST API (configured)", "Scholar Gateway (scholarly citations)", "Consensus", "Google Drive", "Web Search"],
        ["legal-memo (IRAC format)", "pdf (court filings)", "docx (legal documents)"],
        ["/memo [topic] \u2014 generate IRAC legal memo", "/case [citation] \u2014 case law lookup", "/statute [code] \u2014 statute search", "/cite-check [citation] \u2014 verify citation"]
      ),

      // 4. X-Posts
      ...agentSection(
        "X-Posts",
        "X-Posts",
        "Daily crypto/blockchain X posting for @4_Bchainbasics \u2014 3-5 posts daily with character mascots (Weeter & Blubby), deadpan voice styling, humanization algorithms, and approval workflow.",
        "x_daily_post_shortcut.md",
        ["LunarCrush (social intelligence)", "Crypto.com (market data)", "Blockscout (blockchain data)", "Ahrefs (SEO)", "X API MCP", "Claude in Chrome"],
        ["x-voice (brand voice)", "x-images (image generation)", "enterprise-search (cross-source trending)"],
        ["/daily \u2014 generate daily post batch", "/quote [url] \u2014 quote post", "/trending \u2014 trending topic scan"]
      ),

      // 5. Make Videos
      ...agentSection(
        "Make Videos",
        "Make Videos",
        "Multi-channel crypto/blockchain content automation for YouTube (Blockchain Basics + Cardano Daily) \u2014 script generation, recording aids, video rendering, and shorts packaging.",
        "YT_Content_Review/GAME_PLAN.md",
        ["LunarCrush", "Crypto.com", "Blockscout", "Cloudinary (image/video)", "Claude in Chrome"],
        ["yt-daily", "yt-pages", "yt-shorts (15-60s vertical)", "upload-all (multi-platform)", "pptx (pitch decks)", "xlsx (analytics tracking)"],
        ["/daily \u2014 generate daily show script", "/pages \u2014 create recording aid pages", "/shorts \u2014 generate short-form script", "/upload-all \u2014 batch upload to all platforms"]
      ),

      // 6. Ridgemont Catalog Manager
      ...agentSection(
        "Ridgemont Catalog Manager",
        "Ridgemont Catalog Manager",
        "Comprehensive music catalog management system for 162 songs across 3 acts \u2014 sync licensing, revenue tracking, pitch generation, shortcode commands, and Streamlit dashboard.",
        "docs/SYSTEM_PROMPT_V5.md",
        ["Melon (music charts, 26 tools)", "GitHub", "Google Drive"],
        ["catalog-sync (push data to portal/website)", "xlsx (revenue exports)", "docx (pitch letters)"],
        ["/search [query] \u2014 catalog search", "/pitch [song] \u2014 generate sync pitch", "/revenue \u2014 revenue report", "/sync \u2014 push catalog data to portal + website", "/deploy \u2014 deployment tracker"]
      ),

      // 7. Ridgemont Studio Website
      ...agentSection(
        "Ridgemont Studio Website",
        "Ridgemont Studio Website",
        "Music label website and platform \u2014 artist roster, authenticated music streaming via Cloudflare Workers, Firebase auth, artist portal, sync licensing marketplace.",
        "RULES.md",
        ["Cloudflare Dev Platform (Workers, D1, R2)", "Ahrefs (SEO)", "GitHub"],
        [],
        []
      ),

      // 8. Frozen Cloud Website
      ...agentSection(
        "Frozen Cloud Website",
        "Frozen Cloud Website",
        "Static HTML landing page for Frozen Cloud music artist \u2014 showcases releases, videos, sync licensing contact, and press kit.",
        "RULES.md",
        ["Cloudflare Dev Platform (optional)"],
        [],
        []
      ),

      // 9. Suno Studio
      ...agentSection(
        "Suno Studio",
        "Suno Studio",
        "Unified Suno AI workspace \u2014 deterministic prompt generation (4-engine architecture, 122 subgenres, 1228 tags, 1223 instruments, 9 presets) plus training materials and library organization.",
        "CLAUDE_INSTRUCTIONS.md",
        ["Melon (music charts for genre research)"],
        ["suno-prompt-generator", "create-shortcut (workflow automation)"],
        ["/generate \u2014 generate Suno prompt", "/genre [name] \u2014 subgenre deep dive", "/preset [name] \u2014 apply preset"]
      ),

      // 10. Make-Music
      ...agentSection(
        "Make-Music",
        "Make-Music",
        "Songwriting and MIDI composition workspace for acoustic guitar-based ballads \u2014 chord sheets, MIDI generation scripts, Logic Pro projects, and Suno prompts.",
        "RULES.md",
        ["Play Sheet Music (ABC notation)"],
        [],
        []
      ),

      // 11. Ridgemont Catalog Portal
      ...agentSection(
        "Ridgemont Catalog Portal",
        "frozen-cloud-portal",
        "Unified read-only Streamlit catalog portal for all 3 acts (Frozen Cloud, Park Bellevue, Bajan Sun) \u2014 dashboard, catalog browsing, deployment tracking, and financials.",
        "RULES.md",
        [],
        ["xlsx (catalog exports)", "catalog-sync (data from Catalog Manager)"],
        []
      ),

      // TROUBLESHOOTING
      heading("Troubleshooting", HeadingLevel.HEADING_1),
      new Paragraph({ spacing: { after: 200 } }),

      heading("Disk Space Error / ECONNRESET", HeadingLevel.HEADING_3),
      para("If you see \"No space left on device\" or \"API Error: ECONNRESET\", the Cowork session VM disk is full. Start a fresh Cowork task \u2014 each new task gets a clean disk. Your Google Drive files are never affected."),

      heading("Mount / Permission Issues", HeadingLevel.HEADING_3),
      para("If Claude says it can\u2019t find your files or the folder appears empty, the mount went stale. Just re-select the folder when prompted. This is a known Cowork quirk."),

      heading("macOS Permission Dialogs", HeadingLevel.HEADING_3),
      para("When Claude scans files on a Google Drive network volume, macOS may show \"Node.js wants to access a network volume\" dialogs. Click Allow \u2014 this is Claude reading your agent files, not anything suspicious."),

      heading("Connectors Not Showing", HeadingLevel.HEADING_3),
      para("MCP connectors are account-level (installed at claude.ai/settings/connectors). They\u2019re available to ALL Cowork sessions automatically. If one isn\u2019t working, go to claude.ai/settings/connectors and verify it shows as Configure or Connected."),
    ]
  }]
});

const outputPath = process.argv[2] || '/sessions/charming-magical-hopper/mnt/Master Agent/Cowork_Agent_Setup_Guide.docx';
Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync(outputPath, buffer);
  console.log(`Written to ${outputPath} (${(buffer.length / 1024).toFixed(0)} KB)`);
}).catch(err => console.error(err));
