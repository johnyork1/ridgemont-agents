# Daily X Post Shortcut — @4_Bchainbasics

## Schedule: Every day at 6 AM PT

## Workflow Mode: DRAFT → REVIEW → PUBLISH

### Current Phase: LEARNING
- Always present drafted posts to John for review/editing FIRST
- Do NOT post or schedule autonomously until John says the style is dialed in
- When John edits a post, note what he changed and incorporate into style rules
- Goal: learn John's voice well enough to eventually post autonomously

### Workflow Steps:
1. Draft 3-5 posts (see Steps below)
2. Present all posts to John for review
3. John edits/approves each post
4. Once approved, schedule posts at random times throughout the day (spread out, not back-to-back)
5. After John's edits, update style rules with any patterns from his changes

### Future Phase: AUTONOMOUS
- Once John is confident in the output, switch to auto-schedule
- Posts get drafted and scheduled without review
- John can still edit scheduled posts in X's "Scheduled posts" section

---

## Task Description

Draft a daily series of 3-5 X posts for the account @4_Bchainbasics (4 Blockchain Basics). The account is a crypto/Web3 commentary account based in Northern California.

### Steps:

1. **Connect to browser and review profile.**
   - Use Claude in Chrome MCP (Brave browser) to navigate to https://x.com/4_Bchainbasics
   - Review the last 48 hours of posts. Note all topics, hooks, and phrases already used.
   - If X API MCP is available, use it for searching/posting instead of browser automation.

2. **Check post history file for repetition avoidance.**
   - Look for `x_post_history.md` in the current working directory (mounted folder or outputs).
   - If not found, check the X profile directly and create a fresh history file.
   - Update this file with any new posts found on the profile.

3. **Search for the latest crypto and Web3 news.**
   - **Use LunarCrush MCP first** — primary tool for real-time social intelligence on topics, brands, stocks, and crypto. Pull trending topics, social sentiment, and engagement metrics before anything else.
   - Then supplement with WebSearch for specific numbers: prices, liquidation data, ETF flows, Fear & Greed index, etc.
   - Focus on the past 24 hours.

4. **Pull Top 5 Trending Posts from X.**
   - Search X using advanced search (browser or X API MCP):
     `(crypto OR blockchain OR bitcoin) min_faves:50 min_replies:10 -giveaway -giving -send -"random person" -"lucky follower" since:[yesterday's date]`
   - Filter to "Top" tab. Skip giveaway/spam posts.
   - Capture: author, handle, post text, reply count, like count, RT count, views.
   - Note **why each post worked** (patterns: simple questions, contrarian takes, founder quotes, ecosystem drama, community encouragement).
   - Save to `x_top_posts_[date].md` in the working directory.

5. **Draft Hot Take Quote Posts for All 5 Trending Posts.**
   - Write a quote-post-style hot take for each of the 5 trending posts.
   - CHECK UNIQUENESS: navigate to each original post's replies, scan the top 10-15 replies.
   - Score each hot take:
     - **Unique** = angle not seen in any replies → auto-qualify
     - **Fairly Unique** = angle seen in 1-2 replies but not dominant → auto-qualify
     - **Partially Saturated** = angle seen in 3+ replies → revise to a fresh angle, then re-qualify
     - **Saturated** = most common reply theme → must revise to a completely different angle
   - Only quote posts scored "Fairly Unique" or better get scheduled.
   - **Scheduling rule for quote posts:**
     - Rank qualified quote posts by uniqueness (most unique first)
     - Post #1 (most unique): post IMMEDIATELY
     - Post #2: schedule 45-70 minutes after Post #1 (random within range)
     - Post #3+: each scheduled 45-70 minutes after the previous one (random within range)

6. **Load the x-voice skill** before drafting ANY posts.
   - Read `.skills/x-voice/SKILL.md` to load voice patterns and post type distribution.
   - Every post must pass the quality check in that skill before being presented.

7. **Draft 5-7 ORIGINAL posts** using the x-voice post type distribution:
   - **1x Today's Notable News** — straight news with 📰 header, always the first post of the day
   - **3-4x Witty/Clever posts** (70%) — use Norm MacDonald voice patterns from x-voice skill
   - **1-2x Varied tone posts** — rotate through: serious, tongue-in-cheek, meditative, deep, superficial, confessional
   - **2x Manual Direct Posts** — draft 2 additional standout original posts for John to post manually via the X app (not API). These should be your best work. Add to Google Calendar "Personal To Do" daily event.
   - **2x Manual Reply Posts** — draft 2 reply posts for John to post manually as replies to trending/high-engagement posts. Pick posts where a sharp reply would get visibility (large accounts, active threads, timely topics). Include the URL of the post to reply to plus the reply text. Add to Google Calendar "Personal To Do" daily event alongside the manual direct posts.

8. **Generate images for 2-3 posts** using the x-images skill:
   - Load the x-images skill from `.skills/x-images/SKILL.md`
   - Always: news header for "Today's Notable News" post
   - Pick 1-2 more: stat card for a data-driven post, or quote card for the day's sharpest one-liner
   - Run `scripts/image_generator.py` from the x-images skill directory
   - Save images to the X-Posts working directory

9. **Present ALL posts (originals + quote posts) WITH images to John for review.** Wait for edits/approval.

10. **Once approved, schedule everything:**
   - Quote posts: staggered timing (first immediately, then 45-70 min apart)
   - Original posts: random times throughout the day (morning, midday, afternoon, evening — not overlapping with quote post times)
   - Manual direct posts (2x): send to Google Calendar "Personal To Do" daily event (NOT posted via API). See Google Calendar Integration below.
   - Manual reply posts (2x): send to Google Calendar "Personal To Do" daily event with the URL to reply to + reply text. See Google Calendar Integration below.
   - Use X API MCP if available; otherwise use X's Schedule Post UI via Claude in Chrome.

### Google Calendar Integration (Manual Posts)
- **Calendar:** John York (Personal) — ID: `johnyork1@gmail.com`
- **Event:** "Personal To Do" — recurring daily all-day event (recurring ID: `1236ifftda1o801068icu7cmq9_R20251003`)
- **How:** Each day during the workflow, fetch today's "Personal To Do" event instance, then APPEND the 4 manual posts (2 direct + 2 replies) to the existing description (do NOT overwrite existing to-do items).
- **Format:** Add a section like:
  ```
  📱 X Manual Posts:

  DIRECT POST 1:
  [post text here]

  DIRECT POST 2:
  [post text here]

  REPLY 1 — reply to: [URL of post to reply to]
  [reply text here]

  REPLY 2 — reply to: [URL of post to reply to]
  [reply text here]
  ```
- **Tool:** Use `list_gcal_events` to find today's instance, then update via Google Calendar MCP.

11. **Save the final posts** to `x_posts_[date].md` in the working directory.

12. **Update `x_post_history.md`** with the new posts, phrases/hooks used, and themes covered.

13. **Boost Review (end of day or next morning):**
    Check previous day's posts for boost candidates. A post qualifies if ANY of these are true:
    - **Early velocity:** 3+ likes or 2+ replies within the first hour
    - **Author engagement:** The person you quoted replied to or liked your take
    - **Debate spark:** Higher-than-usual reply-to-like ratio (people have opinions)
    - **Gateway content:** Explains something simply + has a follow CTA
    Flag qualifying posts in `x_post_history.md` with [BOOST CANDIDATE] tag.
    Present candidates to John with a recommended boost budget ($1-5 per post to start).

### Style Rules (CRITICAL):
- **ALWAYS load `.skills/x-voice/SKILL.md` first** — it contains the full voice engine
- All lowercase, minimal punctuation
- No apostrophes in contractions (dont, isnt, weve, theyre, etc.)
- Short punchy lines with line breaks between points
- Data-driven — always cite specific numbers when possible
- NEVER use "crypto Twitter" — always say "crypto X" or just refer to the community
- NEVER use the word "Twitter" — the platform is "X"
- Tone: sharp, witty, observational — like Norm MacDonald talking about crypto
- No lecturing the audience ("most of you" / "you need to" etc.)
- Use "we" energy over "you" energy
- Every post must pass the x-voice Quality Check before publishing
- Emojis: only 📰 for Today's Notable News header. No others unless genuinely warranted
- No hashtags in post body
- No video content unless specifically requested

### Phrases to Avoid Repeating (check history file for latest list):
- "volatility is the price of admission"
- "buying this dip or waiting for lower?"
- "zoom out"
- "when the big money runs, you pay attention"
- "no wrong answers"
- "weve been here before"
- "pay attention to what people say at the bottom vs the top"

### Style Edits Log (track John's changes to learn his voice):
- [Feb 7] Prefers not to sound condescending — no "most of you" or "screenshots don't lie"
- [Feb 7] Prefers "we" framing over "you" framing

### Success Criteria:
- Posts feel authentic to the @4_Bchainbasics voice
- No topic or angle repeated from the last 48 hours
- Mix of themes (not all doom/crash content)
- All data points are current and accurate
- Posts presented for review before publishing
- Posts scheduled at random times, not clustered together
