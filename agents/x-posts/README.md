# X Posts

Crypto Twitter content agent for the @4_Bchainbasics account -- drafts, schedules, and manages daily posts on X.

## What It Does

- Drafts crypto/blockchain posts in a specific voice: all lowercase, no apostrophes, data-driven, observational
- Researches trending crypto topics via WebSearch and LunarCrush
- Tracks post history in `x_post_history.md` to avoid repetition
- Schedules posts via X API MCP or Claude in Chrome (Brave browser)
- Currently in LEARNING phase: all posts require approval before publishing

## Usage

Open the `x-posts/` directory in Claude Code. Common workflows:

- "Draft a daily post" -- researches trends and writes a post for review
- "Schedule a post" -- queues an approved post via X's schedule UI
- "Show post history" -- reviews past posts to avoid repeated phrases

## Key Files

- `x_post_history.md` -- full post history and style notes
- `x_daily_post_shortcut.md` -- posting workflow definition and style rules
- `x_top_posts_[date].md` -- daily trending post captures

## Requirements

- X API MCP connector (primary posting method)
- Claude in Chrome MCP with Brave browser (fallback and scheduling)
