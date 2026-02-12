# Ridgemont Studio Website

Public-facing label website for ridgemontstudio.com, featuring artist roster, authenticated music streaming, sync licensing, and artist submissions.

## What It Does

- Single-page application with dark theme and glassmorphism design
- Authenticated music streaming via Cloudflare Worker + Firebase Auth
- Music files stored on Cloudflare R2 (bucket: `ridgemont-studio`)
- Track metadata in `tracks.json` (currently 6 tracks)
- Hosted on GitHub Pages with CNAME for ridgemontstudio.com

## Usage

Edit `index.html` for content updates, then push to GitHub to deploy.

To sync music files to Cloudflare R2:
```bash
./sync-music.sh
```

To deploy the streaming worker:
```bash
wrangler deploy
```

## Requirements

- GitHub Pages for hosting
- Cloudflare account (Workers, R2 storage)
- Firebase project (authentication)
- `wrangler` CLI and `CLOUDFLARE_API_TOKEN` env var for worker deploys

## Related Agents

- **catalog-manager** -- source of truth for song metadata and tracks.json content
- **frozen-cloud-website** -- separate artist landing page (not part of this site)
