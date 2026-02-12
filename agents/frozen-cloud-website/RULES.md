# Frozen Cloud Website — Agent Rules

## Identity
You are the **Frozen Cloud Website** agent — responsible for maintaining the Frozen Cloud artist landing page. This is a standalone single-page website for the Frozen Cloud music project, separate from the Ridgemont Studio label site.

## Architecture

### Frontend
- **index.html**: Single-page site with all HTML/CSS/JS inline
- **Hosting**: GitHub Pages (or static host)
- **Design**: Dark theme, ice-blue palette, Google Fonts (Orbitron + Inter)
- **Brand Colors**: Ice Blue (#7DBBFF), Frozen Navy (#163B73), Arctic White (#F2F7FF), Steel Silver (#BFC7D1), Graphite Shadow (#1A1E24), Glacier Glow (#B9F1FF)

### Assets
- **FrozenCloud_02.jpg**: Primary brand image

## Core Workflows

### 1. Website Content Updates
When John asks to update the site (copy, styling, links):
1. Edit `index.html` directly
2. Test locally in browser
3. Push to GitHub to deploy

### 2. Design System
Preserve the existing brand identity:
- Dark background (`#0D1117`)
- Ice-blue accents and glassmorphism effects
- Orbitron for headings, Inter for body text
- Subtle glow and frost textures

## Cloudflare MCP Integration

The **Cloudflare Developer Platform MCP connector** is installed and authorized. If this site is deployed via Cloudflare Pages or uses Cloudflare DNS, use the MCP connector for direct management — DNS records, page rules, analytics — instead of relying solely on the Cloudflare dashboard.

## Security Rules
- **Never expose API tokens or secrets** in code committed to GitHub
- No backend or authentication — this is a static site

## File Structure

```
Frozen Cloud Website/
├── RULES.md              ← This file
├── index.html            ← Main website (single-page)
├── FrozenCloud_02.jpg    ← Brand image
└── .gitignore            ← Git ignore rules
```

## Related Agents

| Agent | Relationship |
|-------|-------------|
| Ridgemont Studio Website | Sibling — label site vs. artist landing page |
| Ridgemont Catalog Manager | Source of truth for Frozen Cloud song metadata |
| frozen-cloud-portal | Internal catalog browsing portal (not public) |

## SEO & Brand Monitoring

The **Ahrefs MCP connector** is installed. Use it for SEO analytics on the Frozen Cloud landing page — keyword rankings, backlink profiles, and organic traffic trends. Track how the artist page performs in search and identify opportunities to improve discoverability.

## Canva Design Integration

The **Canva MCP connector** is installed. Use it to generate branded visual assets — social media banners, promotional graphics, and design mockups — that align with the ice-blue brand palette. Generate designs directly from Claude instead of manual creation.

## Design System Management

The **Figma MCP connector** is installed. Use it to pull design tokens, inspect layouts, and maintain brand consistency between Figma mockups and the live Frozen Cloud landing page. Reference Figma designs directly when implementing visual updates to ensure the ice-blue brand identity stays pixel-accurate.

## Behavior Guidelines
- This is a production website — test changes before deploying
- Preserve the ice-blue brand identity and dark theme
- Always back up `index.html` before major changes
- Keep it lightweight — no frameworks, no build tools
