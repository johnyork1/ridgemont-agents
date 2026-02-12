---
name: x-images
description: >
  Image creation engine for @4_Bchainbasics X posts. Use this skill whenever creating, selecting,
  or reviewing images for X/Twitter posts. Handles stat cards, quote cards, news headers, and
  data visualizations. MUST be loaded before generating any images for X posts. Also use when
  the user mentions post images, visual content for X, branded graphics, or wants to add
  images to any scheduled posts. Works alongside the x-voice skill — voice first, then images.
---

# X Image Engine — @4_Bchainbasics

Images appear on 20-30% of daily posts. The goal is to stop the scroll — not to be pretty.
Every image should make the post more impactful than text alone. If the image doesn't add
anything, skip it.

## When to Add an Image

Add images to these post types (pick 2-3 per day from the 8-10 daily posts):

1. **Today's Notable News** — always gets a news header card
2. **Stat-driven posts** — any post built around a specific number or data point
3. **Your sharpest one-liner** — the day's best witty post gets a quote card
4. **Market movement posts** — charts or price data visualizations

Do NOT add images to:
- Quick-hit observational posts that work perfectly as text
- Replies or community engagement
- Posts where the humor is in the words, not the visual

## Image Types

### Type 1: Stat Card
A bold number or data point on a dark background. Used when a post leads with data.

Layout:
```
┌─────────────────────────┐
│                         │
│     $72,400             │  ← Large accent-colored number
│     btc bounced here    │  ← Small white subtext
│     like it forgot      │
│     something at home   │
│                         │
│          @4_Bchainbasics│  ← Handle, bottom-right, subtle
└─────────────────────────┘
```

When to use: Posts with price data, percentage moves, TVL numbers, volume stats.

### Type 2: Quote Card
Your own text on a branded background. Used for your sharpest take of the day.

Layout:
```
┌─────────────────────────┐
│                         │
│  "funny how everyone    │  ← White text, medium weight
│   wants decentralization│
│   until they lose       │
│   their password"       │
│                         │
│          @4_Bchainbasics│
└─────────────────────────┘
```

When to use: Your best one-liner or philosophical gut punch of the day.
Keep it SHORT — if the quote needs more than 4 lines, it's too long for a card.

### Type 3: News Header
A branded header graphic for the daily "todays notable news" post.

Layout:
```
┌─────────────────────────┐
│                         │
│  📰 todays notable news │  ← Branded header
│     feb 7, 2026         │  ← Date
│                         │
│          @4_Bchainbasics│
└─────────────────────────┘
```

When to use: Always on the daily news post. Same style every day for brand consistency.

### Type 4: Data Visualization
A matplotlib-generated chart showing market data, trends, or comparisons.

When to use: Posts about market trends, price history, comparing assets, or on-chain data.
Keep charts clean — dark background, minimal gridlines, accent colors, no chartjunk.

---

## Brand Identity

### Colors
- **Background:** #0D1117 (deep dark, like GitHub dark mode)
- **Accent:** #00D4AA (crypto teal — used for numbers, highlights, chart lines)
- **Text primary:** #FFFFFF (white)
- **Text secondary:** #8B949E (muted gray — for handles, dates, subtext)
- **Accent alt:** #FF6B35 (warm orange — for emphasis, warnings, "hot" data)

### Typography
- **Headlines/numbers:** Poppins Bold
- **Body text:** Poppins Medium
- **Handle/watermark:** Poppins Light

### Dimensions
- X timeline images: **1200 x 675 px** (16:9 ratio, optimal for feed)
- Square option: **1080 x 1080 px** (when content needs more vertical space)

### Watermark
Every image includes `@4_Bchainbasics` in the bottom-right corner.
Color: #8B949E at ~60% opacity. Never prominent — it's a signature, not a billboard.

### Characters: Weeter & Blubby (IP owned by John York)
Original cartoon characters that make @4_Bchainbasics visually unique. Weeter is about 40-50% larger than Blubby.
- **Weeter** — larger brown bear-like creature with yellow eyes and a name badge
- **Blubby** — smaller olive/green creature with yellow eyes, antennae, and a name badge

**Pose Library** (in `assets/` directory):

| Character | Pose | File | Use When |
|-----------|------|------|----------|
| Weeter | Neutral (standing) | `weeter_neutral.png` | Default, general posts |
| Weeter | Celebrating (hands up) | `weeter_celebrating.png` | Pumps, good news, wins |
| Weeter | Surprised (shocked face) | `weeter_surprised.png` | Unexpected moves, breaking news |
| Weeter | Sad (head scratch, frown) | `weeter_sad.png` | Dumps, losses, bad takes |
| Weeter | Presenting (pointing out) | `weeter_presenting.png` | Explaining, showing data |
| Blubby | Neutral (standing) | `blubby_neutral.png` | Default, general posts |
| Blubby | Celebrating (hands up) | `blubby_celebrating.png` | Pumps, good news, wins |
| Blubby | Surprised (shocked face) | `blubby_surprised.png` | Unexpected moves, breaking news |
| Blubby | Confused (question mark) | `blubby_confused.png` | Dumb takes, confusing market moves |
| Blubby | Excited (sparkles, waving) | `blubby_excited.png` | Great news, hype, celebrations |

**Mood shortcuts** (auto-selects best pose):
- `pump` → Weeter celebrating / Blubby excited
- `dump` → Weeter sad / Blubby confused
- `shock` → Weeter surprised / Blubby surprised
- `funny` → Weeter presenting / Blubby excited
- `news` → Weeter presenting / Blubby neutral
- `neutral` → Weeter neutral / Blubby neutral

**When to use characters (roughly 1 per day, not every image):**
- Stat cards where the data is dramatic (big dump, big pump) — match pose to mood
- The day's best quote card — character in the corner adds personality
- Any post with a humorous or absurd tone — characters amplify the vibe

**When NOT to use characters:**
- Today's Notable News header — keep it clean and professional
- Serious/urgent posts — characters undercut gravity
- Data visualizations/charts — characters distract from the data

**How to add via CLI:**
```bash
# Specific pose
python3 image_generator.py --type stat_card --headline "$72,400" \
  --subtext "btc bounced here" --character weeter_celebrating \
  --char-position bottom-right --output card.png

# Mood shortcut (auto-selects pose)
python3 image_generator.py --type stat_card --headline="-12.4%" \
  --subtext "eth chose violence" --character dump \
  --char-position bottom-right --output dump.png
```
Options: `--character [pose or mood]`, `--char-position bottom-right|bottom-left|right-center|left-center`, `--char-height [pixels]`

---

## How to Generate Images

### Primary Method: Python (Pillow + matplotlib)
Run the image generator script:

```bash
python3 /path/to/.skills/x-images/scripts/image_generator.py \
  --type stat_card \
  --headline "$72,400" \
  --subtext "btc bounced here like it forgot something at home" \
  --output /path/to/output.png
```

Script location: `scripts/image_generator.py` (in this skill's directory)

Available types: `stat_card`, `quote_card`, `news_header`, `chart`

For charts, use matplotlib directly with the brand colors defined in the script.

### Secondary Method: Canva (if MCP connected)
If the Canva MCP is available, use it for:
- More polished designs when time allows
- Template-based graphics with complex layouts
- Any design that needs elements beyond what Pillow handles well

Canva workflow: search for a minimal dark template → customize with brand colors → export as PNG.

### Post-Processing (always apply)
After generating any image, apply these finishing touches to make it feel less "generated":
1. Subtle noise/grain layer (2-3% opacity) — makes it feel textured
2. Slight corner rounding (20px radius) — softer feel
3. Verify file size is under 5MB (X limit)
4. Save as PNG for graphics, JPEG (quality 92) for photos/charts

---

## Integration with Workflow

During the daily posting workflow (step 7):
1. Draft all 8-10 posts using x-voice skill
2. Identify which 2-3 posts get images (see "When to Add an Image" above)
3. Generate images using this skill
4. Present posts WITH their images to John for review
5. When posting via API, attach the image file to the tweet

For manual posts (the 2 sent to Google Calendar):
- If a manual post gets an image, save the image to the workspace folder
- Include the file path in the calendar event so John can find it easily

---

## Anti-Detection Notes

These images are NOT photorealistic AI art — they're designed graphics (stat cards, branded
text overlays, data visualizations). This is the same type of content that Bloomberg, Bankless,
The Block, and every professional media account produces. There is nothing to "detect" because
these are legitimate graphic design outputs, not AI-generated photography or illustration.

The subtle noise/grain layer and rounded corners are standard design practices that also happen
to make the output feel more polished and less "flat" — which is a bonus.

---

## Quality Check Before Attaching

1. Does the image make the post MORE impactful? → If not, post text-only
2. Is the text readable at mobile size? → If not, increase font size or reduce text
3. Does it match the brand colors? → No random colors or gradients
4. Is the watermark present but subtle? → Check bottom-right
5. Would this look at home next to Bloomberg or Bankless content? → That's the standard
