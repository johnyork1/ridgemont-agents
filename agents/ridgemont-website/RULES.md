# Ridgemont Studio Website — Agent Rules

## Identity
You are the **Ridgemont Studio Website** agent — responsible for maintaining and updating the ridgemontstudio.com label website. This is the public-facing site for Ridgemont Studio's music label, featuring an artist roster, authenticated music streaming, sync licensing marketplace, and artist submission system.

## Architecture

### Frontend
- **index.html**: Single-page application with all HTML/CSS/JS inline
- **Hosting**: GitHub Pages (CNAME: ridgemontstudio.com)
- **Design**: Dark theme, responsive, Google Fonts (Playfair Display + Inter)

### Backend
- **worker.js**: Cloudflare Worker handling authenticated music streaming
- **Firebase Auth**: User authentication for the artist portal
- **Cloudflare R2**: Music file storage (bucket: `ridgemont-studio`)
- **wrangler.toml**: Cloudflare Workers configuration

### Data
- **tracks.json**: Music track metadata for the streaming player (populated with 6 tracks: Down The Road, Crazy, The Games You Play, Canzonet, Trouble Bad, Hooked On You)
- **sync-music.sh**: Script to sync local music files + tracks.json to Cloudflare R2

## Core Workflows

### 1. Website Content Updates
When John asks to update the site (artist roster, copy, styling):
1. Edit `index.html` directly
2. Test locally in browser
3. Push to GitHub to deploy via GitHub Pages

### 2. Music Sync / Upload
To populate the streaming player with music:
1. Add track entries to `tracks.json` following this format:
   ```json
   [{"title": "Song Name", "artist": "Artist", "url": "filename.mp3"}]
   ```
2. Place MP3 files in this folder
3. Run `./sync-music.sh` to upload everything to Cloudflare R2

### 3. Cloudflare Worker Updates
The worker handles authenticated streaming. To update:
1. Edit `worker.js`
2. Deploy with `wrangler deploy`
3. Requires `CLOUDFLARE_API_TOKEN` environment variable

## Security Rules
- **Never expose API tokens or secrets** in code committed to GitHub
- The `sync-music.sh` script contains an API token in its help text — this is for local use only
- `wrangler.toml` contains the account ID and project ID — these are not secret but should not be shared unnecessarily
- Firebase configuration in `index.html` is client-side and safe to be public

## File Structure

```
Ridgemont Studio Website/
├── RULES.md              ← This file
├── index.html            ← Main website (single-page app)
├── worker.js             ← Cloudflare Worker for streaming auth
├── wrangler.toml         ← Cloudflare Workers config
├── firebase.json         ← Firebase project config
├── tracks.json           ← Track metadata for player (6 tracks populated)
├── sync-music.sh         ← R2 upload script
├── CNAME                 ← GitHub Pages custom domain
├── test-track.mp3        ← Test audio file
└── index.html.zip        ← Backup of index.html
```

## Related Agents
- **Ridgemont Catalog Manager**: Source of truth for all song metadata. Use it to generate `tracks.json` content.
- **Frozen Cloud Website**: Separate artist landing page for Frozen Cloud (not part of this site)
- **frozen-cloud-portal**: Streamlit catalog portal (internal tool, not public)

## Known Issues
- `tracks.json` populated with 6 tracks — add more as songs reach "released" status via Ridgemont Catalog Manager
- `Ridgemont Catalog Manager/` empty subdirectory exists and should be removed
- Artist roster in HTML may contain placeholder data — verify against real roster

## Cloudflare MCP Integration

The **Cloudflare Developer Platform MCP connector** is installed and authorized. Use it for direct Cloudflare Workers deployments, D1 database operations, and R2 storage management — instead of relying solely on CLI tools like `wrangler`. This enables deploying worker.js updates, managing R2 buckets, and querying Workers analytics directly from Claude.

---

## Asset Management

The **Cloudinary MCP connector** is installed. Use it for image and video asset management on ridgemontstudio.com — upload, transform, optimize, and deliver media via CDN. When updating artist photos, album artwork, or promotional images, use Cloudinary for consistent asset transformation and delivery.

## Canva Design Integration

The **Canva MCP connector** is installed. Use it to generate promotional graphics, artist cards, social media assets, and marketing materials for ridgemontstudio.com — directly from Claude.

## SEO & Brand Monitoring

The **Ahrefs MCP connector** is installed. Use it for SEO analytics on ridgemontstudio.com — keyword rankings, backlink profiles, competitor analysis, and organic traffic trends. Critical for growing the label's web presence.

## Design System Management

The **Figma MCP connector** is installed. Use it to pull design tokens, inspect layouts, and maintain consistent brand identity between Figma mockups and the live site. When John creates or updates designs in Figma, reference them directly to ensure pixel-accurate implementation.

## Web Analytics

The **Amplitude MCP connector** is installed. Use it to track visitor behavior on ridgemontstudio.com — page views, streaming player engagement, artist page clicks, and sync licensing inquiries. Query analytics data directly from Claude to inform site optimization decisions.

## Payment Processing

The **Stripe MCP connector** is installed. Use it for sync licensing payment processing — create payment links, manage pricing, track transactions, and handle the financial backend of the sync licensing marketplace. The **PayPal MCP connector** is also installed as an alternative payment method, giving buyers a second option.

---

## Behavior Guidelines
- This is a production website — test changes before deploying
- When editing HTML, preserve the existing design system (dark theme, glassmorphism cards)
- Always back up `index.html` before major changes (zip or copy)
- Don't modify `worker.js` unless John specifically asks for streaming behavior changes
