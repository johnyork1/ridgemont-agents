#!/usr/bin/env python3
"""
Image generator for @4_Bchainbasics X posts.
Creates branded stat cards, quote cards, news headers, and chart templates.

Usage:
    python3 image_generator.py --type stat_card --headline "$72,400" --subtext "btc bounced here" --output card.png
    python3 image_generator.py --type quote_card --text "funny how everyone wants decentralization..." --output quote.png
    python3 image_generator.py --type news_header --date "feb 7, 2026" --output header.png
"""

import argparse
import os
import sys
import textwrap
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ─── Brand Colors ───
COLORS = {
    "bg":           "#0D1117",
    "accent":       "#00D4AA",
    "accent_alt":   "#FF6B35",
    "text_primary": "#FFFFFF",
    "text_secondary": "#8B949E",
    "text_muted":   "#484F58",
}

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple."""
    h = hex_color.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def hex_to_rgba(hex_color, alpha=255):
    """Convert hex color to RGBA tuple."""
    return hex_to_rgb(hex_color) + (alpha,)

# ─── Font Paths ───
FONT_DIR = "/usr/share/fonts/truetype/google-fonts"
FONTS = {
    "bold":        os.path.join(FONT_DIR, "Poppins-Bold.ttf"),
    "medium":      os.path.join(FONT_DIR, "Poppins-Medium.ttf"),
    "regular":     os.path.join(FONT_DIR, "Poppins-Regular.ttf"),
    "light":       os.path.join(FONT_DIR, "Poppins-Light.ttf"),
    "light_italic": os.path.join(FONT_DIR, "Poppins-LightItalic.ttf"),
}

# ─── Character Assets ───
ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")

# Pose-based character system — 65 poses across solo and paired
# Use "character_pose" format (e.g., "weeter_sad", "pair_money_rich")
# or mood keywords ("pump", "dump", "shock", etc.)
CHARACTER_POSES = {
    # ── Individual Weeter (20 poses) ──
    "weeter_neutral":          os.path.join(ASSETS_DIR, "weeter_neutral.png"),
    "weeter_celebrating":      os.path.join(ASSETS_DIR, "weeter_celebrating.png"),
    "weeter_surprised":        os.path.join(ASSETS_DIR, "weeter_surprised.png"),
    "weeter_sad":              os.path.join(ASSETS_DIR, "weeter_sad.png"),
    "weeter_presenting":       os.path.join(ASSETS_DIR, "weeter_presenting.png"),
    "weeter_sleeping_pillow":  os.path.join(ASSETS_DIR, "weeter_sleeping_pillow.png"),
    "weeter_thinking":         os.path.join(ASSETS_DIR, "weeter_thinking.png"),
    "weeter_cool_sunglasses":  os.path.join(ASSETS_DIR, "weeter_cool_sunglasses.png"),
    "weeter_flexing":          os.path.join(ASSETS_DIR, "weeter_flexing.png"),
    "weeter_megaphone":        os.path.join(ASSETS_DIR, "weeter_megaphone.png"),
    "weeter_sweating":         os.path.join(ASSETS_DIR, "weeter_sweating.png"),
    "weeter_money_eyes":       os.path.join(ASSETS_DIR, "weeter_money_eyes.png"),
    "weeter_angry_steaming":   os.path.join(ASSETS_DIR, "weeter_angry_steaming.png"),
    "weeter_grumpy":           os.path.join(ASSETS_DIR, "weeter_grumpy.png"),
    "weeter_shocked":          os.path.join(ASSETS_DIR, "weeter_shocked.png"),
    "weeter_laughing_haha":    os.path.join(ASSETS_DIR, "weeter_laughing_haha.png"),
    "weeter_brooding":         os.path.join(ASSETS_DIR, "weeter_brooding.png"),
    "weeter_eating":           os.path.join(ASSETS_DIR, "weeter_eating.png"),
    "weeter_arms_crossed":     os.path.join(ASSETS_DIR, "weeter_arms_crossed.png"),
    "weeter_sleepy_love":      os.path.join(ASSETS_DIR, "weeter_sleepy_love.png"),
    # ── Individual Blubby (13 poses) ──
    "blubby_neutral":          os.path.join(ASSETS_DIR, "blubby_neutral.png"),
    "blubby_celebrating":      os.path.join(ASSETS_DIR, "blubby_celebrating.png"),
    "blubby_surprised":        os.path.join(ASSETS_DIR, "blubby_surprised.png"),
    "blubby_confused":         os.path.join(ASSETS_DIR, "blubby_confused.png"),
    "blubby_excited":          os.path.join(ASSETS_DIR, "blubby_excited.png"),
    "blubby_sleeping_pillow":  os.path.join(ASSETS_DIR, "blubby_sleeping_pillow.png"),
    "blubby_thinking":         os.path.join(ASSETS_DIR, "blubby_thinking.png"),
    "blubby_cool_sunglasses":  os.path.join(ASSETS_DIR, "blubby_cool_sunglasses.png"),
    "blubby_scared":           os.path.join(ASSETS_DIR, "blubby_scared.png"),
    "blubby_detective":        os.path.join(ASSETS_DIR, "blubby_detective.png"),
    "blubby_mind_blown":       os.path.join(ASSETS_DIR, "blubby_mind_blown.png"),
    "blubby_shrugging":        os.path.join(ASSETS_DIR, "blubby_shrugging.png"),
    "blubby_rocket":           os.path.join(ASSETS_DIR, "blubby_rocket.png"),
    # ── Paired poses (32 poses — both characters together) ──
    "pair_waving":             os.path.join(ASSETS_DIR, "pair_waving.png"),
    "pair_jumping":            os.path.join(ASSETS_DIR, "pair_jumping.png"),
    "pair_crying":             os.path.join(ASSETS_DIR, "pair_crying.png"),
    "pair_angry":              os.path.join(ASSETS_DIR, "pair_angry.png"),
    "pair_facepalm":           os.path.join(ASSETS_DIR, "pair_facepalm.png"),
    "pair_worried":            os.path.join(ASSETS_DIR, "pair_worried.png"),
    "pair_laughing":           os.path.join(ASSETS_DIR, "pair_laughing.png"),
    "pair_confused":           os.path.join(ASSETS_DIR, "pair_confused.png"),
    "pair_sleeping":           os.path.join(ASSETS_DIR, "pair_sleeping.png"),
    "pair_money_rich":         os.path.join(ASSETS_DIR, "pair_money_rich.png"),
    "pair_scared":             os.path.join(ASSETS_DIR, "pair_scared.png"),
    "pair_sweating":           os.path.join(ASSETS_DIR, "pair_sweating.png"),
    "pair_rocket_moon":        os.path.join(ASSETS_DIR, "pair_rocket_moon.png"),
    "pair_running_panic":      os.path.join(ASSETS_DIR, "pair_running_panic.png"),
    "pair_thinking":           os.path.join(ASSETS_DIR, "pair_thinking.png"),
    "pair_detective":          os.path.join(ASSETS_DIR, "pair_detective.png"),
    "pair_reading":            os.path.join(ASSETS_DIR, "pair_reading.png"),
    "pair_skeptical":          os.path.join(ASSETS_DIR, "pair_skeptical.png"),
    "pair_mind_blown":         os.path.join(ASSETS_DIR, "pair_mind_blown.png"),
    "pair_teaching":           os.path.join(ASSETS_DIR, "pair_teaching.png"),
    "pair_cool_sunglasses":    os.path.join(ASSETS_DIR, "pair_cool_sunglasses.png"),
    "pair_flexing":            os.path.join(ASSETS_DIR, "pair_flexing.png"),
    "pair_shrugging":          os.path.join(ASSETS_DIR, "pair_shrugging.png"),
    "pair_thumbs_up":          os.path.join(ASSETS_DIR, "pair_thumbs_up.png"),
    "pair_thumbs_down":        os.path.join(ASSETS_DIR, "pair_thumbs_down.png"),
    "pair_high_five":          os.path.join(ASSETS_DIR, "pair_high_five.png"),
    "pair_popcorn":            os.path.join(ASSETS_DIR, "pair_popcorn.png"),
    "pair_megaphone":          os.path.join(ASSETS_DIR, "pair_megaphone.png"),
    "pair_holding_sign":       os.path.join(ASSETS_DIR, "pair_holding_sign.png"),
    "pair_selfie":             os.path.join(ASSETS_DIR, "pair_selfie.png"),
    "pair_dancing":            os.path.join(ASSETS_DIR, "pair_dancing.png"),
    "pair_whispering":         os.path.join(ASSETS_DIR, "pair_whispering.png"),
}

# Mood-to-pose mapping for automatic selection
# Each mood maps to a list of suitable poses (randomly selected at generation time)
MOOD_MAP = {
    "pump":      ["pair_money_rich", "pair_rocket_moon", "pair_jumping", "pair_high_five",
                  "pair_flexing", "weeter_celebrating", "weeter_money_eyes", "blubby_celebrating"],
    "dump":      ["pair_crying", "pair_scared", "pair_running_panic", "pair_sweating",
                  "pair_worried", "weeter_sad", "blubby_scared"],
    "news":      ["pair_reading", "pair_teaching", "pair_megaphone", "pair_detective",
                  "weeter_presenting", "weeter_megaphone", "blubby_detective"],
    "shock":     ["pair_mind_blown", "pair_facepalm", "weeter_shocked", "weeter_surprised",
                  "blubby_surprised", "blubby_mind_blown"],
    "funny":     ["pair_laughing", "pair_popcorn", "pair_dancing", "pair_selfie",
                  "weeter_laughing_haha", "weeter_eating", "blubby_excited"],
    "neutral":   ["pair_waving", "pair_shrugging", "pair_thumbs_up", "pair_thinking",
                  "weeter_neutral", "weeter_arms_crossed", "blubby_neutral"],
    "angry":     ["pair_angry", "pair_thumbs_down", "weeter_angry_steaming",
                  "weeter_grumpy", "weeter_brooding"],
    "confused":  ["pair_confused", "pair_skeptical", "blubby_confused",
                  "blubby_shrugging", "weeter_thinking"],
    "sleepy":    ["pair_sleeping", "weeter_sleeping_pillow", "blubby_sleeping_pillow",
                  "weeter_sleepy_love"],
    "confident": ["pair_cool_sunglasses", "pair_flexing", "weeter_cool_sunglasses",
                  "weeter_flexing", "blubby_cool_sunglasses", "weeter_arms_crossed"],
    "nervous":   ["pair_sweating", "pair_running_panic", "pair_worried",
                  "weeter_sweating", "blubby_scared"],
    "skeptical": ["pair_skeptical", "pair_detective", "blubby_detective",
                  "weeter_thinking", "blubby_thinking"],
    "secret":    ["pair_whispering", "pair_detective", "blubby_detective"],
    "custom":    ["pair_holding_sign"],
}

# ─── Dimensions ───
WIDTH = 1200
HEIGHT = 675
PADDING = 60
CORNER_RADIUS = 20

def get_font(style="medium", size=32):
    """Load a Poppins font at the given size."""
    try:
        return ImageFont.truetype(FONTS.get(style, FONTS["medium"]), size)
    except (OSError, IOError):
        # Fallback
        return ImageFont.truetype(FONTS["regular"], size)

def add_noise(img, intensity=6):
    """Add subtle grain/noise to the image for a more textured feel."""
    import numpy as np
    arr = np.array(img).astype(np.int16)
    noise = np.random.normal(0, intensity, arr.shape).astype(np.int16)
    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)

def round_corners(img, radius=CORNER_RADIUS):
    """Apply rounded corners to the image."""
    mask = Image.new('L', img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([0, 0, img.size[0]-1, img.size[1]-1], radius=radius, fill=255)

    result = img.copy()
    result.putalpha(mask)

    # Composite onto dark background for PNG with transparency
    bg = Image.new('RGBA', img.size, hex_to_rgba(COLORS["bg"]))
    bg.paste(result, mask=result.split()[3])
    return bg

def add_watermark(draw, width=WIDTH, height=HEIGHT):
    """Add @4_Bchainbasics + Weeter & Blubby™ watermark in bottom-left corner."""
    handle_font = get_font("light", 18)
    brand_font = get_font("medium", 16)
    handle = "@4_Bchainbasics"
    brand = "Weeter & Blubby\u2122"
    x = PADDING
    y = height - PADDING
    # Subdued handle
    draw.text((x, y), handle, fill=hex_to_rgba(COLORS["text_secondary"], 130), font=handle_font)
    # Bright brand mark with spacing
    bbox = draw.textbbox((x, y), handle, font=handle_font)
    gap = 18
    draw.text((bbox[2] + gap, y + 1), brand, fill=hex_to_rgba(COLORS["accent"], 200), font=brand_font)

def wrap_text(text, font, draw, max_width):
    """Word-wrap text to fit within max_width pixels. Respects explicit \\n line breaks."""
    # Split on explicit newlines first, then word-wrap each paragraph
    paragraphs = text.split('\n')
    lines = []

    for para in paragraphs:
        words = para.split()
        if not words:
            lines.append("")
            continue
        current_line = ""
        for word in words:
            test_line = f"{current_line} {word}".strip()
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)

    return lines

def create_stat_card(headline, subtext="", accent_color=None, output_path="stat_card.png"):
    """
    Create a stat card with a bold number/headline and optional subtext.

    Args:
        headline: The main stat (e.g., "$72,400", "43%", "2.1M ETH")
        subtext: Supporting text (e.g., "btc bounced here like it forgot something at home")
        accent_color: Override accent color (hex). Defaults to brand accent.
        output_path: Where to save the image.
    """
    img = Image.new('RGBA', (WIDTH, HEIGHT), hex_to_rgba(COLORS["bg"]))
    draw = ImageDraw.Draw(img)

    accent = accent_color or COLORS["accent"]

    # Headline (large stat)
    headline_font = get_font("bold", 72)
    bbox = draw.textbbox((0, 0), headline, font=headline_font)
    headline_h = bbox[3] - bbox[1]

    # Calculate vertical centering
    subtext_font = get_font("medium", 26)
    sub_lines = wrap_text(subtext, subtext_font, draw, WIDTH - PADDING * 2) if subtext else []
    sub_line_height = 36
    total_sub_height = len(sub_lines) * sub_line_height

    total_content_height = headline_h + 20 + total_sub_height
    # Position content around 1/3 from the top — keeps text clear of characters in bottom-right
    start_y = HEIGHT // 3 - total_content_height // 2

    # Draw headline
    draw.text((PADDING, start_y), headline, fill=hex_to_rgb(accent), font=headline_font)

    # Draw subtext lines
    y = start_y + headline_h + 20
    for line in sub_lines:
        draw.text((PADDING, y), line, fill=hex_to_rgb(COLORS["text_primary"]), font=subtext_font)
        y += sub_line_height

    # Watermark
    add_watermark(draw)

    # Add subtle accent line at top
    draw.rectangle([0, 0, WIDTH, 4], fill=hex_to_rgb(accent))

    # Post-processing
    img = img.convert('RGB')
    try:
        img = add_noise(img, intensity=4)
    except ImportError:
        pass  # numpy not available, skip noise
    img = img.convert('RGBA')
    img = round_corners(img)

    img.save(output_path, "PNG")
    return output_path

def create_quote_card(text, output_path="quote_card.png"):
    """
    Create a quote card with text on branded background.

    Args:
        text: The quote text (keep it short — 4 lines max)
        output_path: Where to save the image.
    """
    img = Image.new('RGBA', (WIDTH, HEIGHT), hex_to_rgba(COLORS["bg"]))
    draw = ImageDraw.Draw(img)

    # Quote text
    quote_font = get_font("medium", 32)
    max_text_width = WIDTH - PADDING * 2 - 40  # Extra padding for quote feel
    lines = wrap_text(text, quote_font, draw, max_text_width)

    line_height = 48
    total_text_height = len(lines) * line_height
    # Position content around 1/3 from the top — keeps text clear of characters in bottom-right
    start_y = HEIGHT // 3 - total_text_height // 2

    # Subtle left accent bar
    bar_x = PADDING - 10
    draw.rectangle(
        [bar_x, start_y - 10, bar_x + 4, start_y + total_text_height + 10],
        fill=hex_to_rgba(COLORS["accent"], 100)
    )

    # Draw quote text
    y = start_y
    for line in lines:
        draw.text((PADDING + 20, y), line, fill=hex_to_rgb(COLORS["text_primary"]), font=quote_font)
        y += line_height

    # Watermark
    add_watermark(draw)

    # Post-processing
    img = img.convert('RGB')
    try:
        img = add_noise(img, intensity=4)
    except ImportError:
        pass
    img = img.convert('RGBA')
    img = round_corners(img)

    img.save(output_path, "PNG")
    return output_path

def create_news_header(date_str="", output_path="news_header.png"):
    """
    Create the daily news header graphic.

    Args:
        date_str: The date string (e.g., "feb 7, 2026")
        output_path: Where to save the image.
    """
    # News header is shorter — 675 tall is too much for just a header
    header_height = 400
    img = Image.new('RGBA', (WIDTH, header_height), hex_to_rgba(COLORS["bg"]))
    draw = ImageDraw.Draw(img)

    # Title
    title_font = get_font("bold", 48)
    title = "todays notable news"
    bbox = draw.textbbox((0, 0), title, font=title_font)
    title_w = bbox[2] - bbox[0]
    title_x = (WIDTH - title_w) // 2
    title_y = header_height // 2 - 50

    # Emoji (drawn separately since Pillow may not render it)
    # Just draw the text — emoji rendering depends on system
    full_title = "\U0001f4f0 " + title
    try:
        bbox_full = draw.textbbox((0, 0), full_title, font=title_font)
        full_w = bbox_full[2] - bbox_full[0]
        title_x = (WIDTH - full_w) // 2
        draw.text((title_x, title_y), full_title, fill=hex_to_rgb(COLORS["text_primary"]), font=title_font)
    except Exception:
        draw.text((title_x, title_y), title, fill=hex_to_rgb(COLORS["text_primary"]), font=title_font)

    # Date
    if date_str:
        date_font = get_font("light", 24)
        bbox = draw.textbbox((0, 0), date_str, font=date_font)
        date_w = bbox[2] - bbox[0]
        date_x = (WIDTH - date_w) // 2
        draw.text((date_x, title_y + 65), date_str, fill=hex_to_rgb(COLORS["text_secondary"]), font=date_font)

    # Accent line below title
    line_y = title_y + 100
    line_w = 200
    line_x = (WIDTH - line_w) // 2
    draw.rectangle([line_x, line_y, line_x + line_w, line_y + 2], fill=hex_to_rgb(COLORS["accent"]))

    # Watermark
    add_watermark(draw, WIDTH, header_height)

    # Top accent bar
    draw.rectangle([0, 0, WIDTH, 4], fill=hex_to_rgb(COLORS["accent"]))

    # Post-processing
    img = img.convert('RGB')
    try:
        img = add_noise(img, intensity=4)
    except ImportError:
        pass
    img = img.convert('RGBA')
    img = round_corners(img, radius=CORNER_RADIUS)

    img.save(output_path, "PNG")
    return output_path

def add_sticker_outline(char_img, outline_width=5, outline_color=(255, 255, 255, 255)):
    """
    Add a sticker-style outline around a character image (RGBA with transparency).

    Creates a slightly larger silhouette in outline_color behind the character,
    giving it that clean sticker/emoji look that pops on any background.

    Args:
        char_img: RGBA PIL Image with transparency
        outline_width: Width of the outline in pixels
        outline_color: RGBA tuple for the outline (default: white)
    Returns:
        New RGBA image with outline (slightly larger than original)
    """
    import numpy as np

    # Expand canvas to make room for outline
    ow = outline_width
    orig_w, orig_h = char_img.size
    new_w = orig_w + 2 * ow
    new_h = orig_h + 2 * ow

    # Extract alpha channel and create dilated version for outline
    alpha = np.array(char_img.split()[3])

    # Create larger canvas for the alpha
    big_alpha = np.zeros((new_h, new_w), dtype=np.uint8)
    big_alpha[ow:ow+orig_h, ow:ow+orig_w] = alpha

    # Dilate the alpha to create outline silhouette
    # Use multiple passes of max filter for smooth, even dilation
    from PIL import ImageFilter
    dilated = Image.fromarray(big_alpha)
    for _ in range(ow):
        dilated = dilated.filter(ImageFilter.MaxFilter(3))
    dilated_arr = np.array(dilated)

    # Build the outline layer: dilated silhouette filled with outline color
    outline_layer = Image.new('RGBA', (new_w, new_h), (0, 0, 0, 0))
    outline_arr = np.array(outline_layer)
    mask = dilated_arr > 0
    outline_arr[mask] = outline_color
    outline_layer = Image.fromarray(outline_arr)

    # Paste original character on top (centered in the expanded canvas)
    char_on_canvas = Image.new('RGBA', (new_w, new_h), (0, 0, 0, 0))
    char_on_canvas.paste(char_img, (ow, ow), char_img)

    # Composite: outline behind, character on top
    result = Image.alpha_composite(outline_layer, char_on_canvas)
    return result


def load_character(name, target_height=200):
    """
    Load a character asset and resize to target height while preserving aspect ratio.

    Args:
        name: Full pose name like "weeter_sad", "blubby_excited", or shorthand
              "weeter"/"blubby" (defaults to neutral pose). Also accepts mood
              keywords: "pump", "dump", "shock", "funny", "neutral", "news"
        target_height: Desired height in pixels
    Returns:
        RGBA Image or None if asset not found
    """
    # Handle mood keywords — pick first matching pose
    if name in MOOD_MAP:
        name = MOOD_MAP[name][0]
    # Handle shorthand (just "weeter" or "blubby" → neutral pose)
    elif name in ("weeter", "blubby"):
        name = f"{name}_neutral"

    path = CHARACTER_POSES.get(name)
    if not path or not os.path.exists(path):
        return None
    char_img = Image.open(path).convert('RGBA')
    ratio = target_height / char_img.height
    new_width = int(char_img.width * ratio)
    char_img = char_img.resize((new_width, target_height), Image.LANCZOS)
    return char_img

def add_character(base_img, character="weeter", position="bottom-right", target_height=None,
                   opacity=220, sticker_outline=True, outline_width=4, outline_color=(255, 255, 255, 255)):
    """
    Composite a character onto the base image with optional sticker outline.

    Args:
        base_img: The base RGBA image
        character: "weeter", "blubby", pose name, or mood keyword
        position: "bottom-right", "bottom-left", "right-center", "left-center"
        target_height: Character height in pixels (default: 30% of image height)
        opacity: 0-255, how opaque the character should be
        sticker_outline: Whether to add a sticker-style outline (default: True)
        outline_width: Outline thickness in pixels (default: 4)
        outline_color: RGBA tuple for outline (default: white)
    Returns:
        New RGBA image with character composited
    """
    if target_height is None:
        target_height = int(base_img.height * 0.30)

    char_img = load_character(character, target_height)
    if char_img is None:
        return base_img

    # Add sticker outline for clean edge definition on any background
    if sticker_outline:
        char_img = add_sticker_outline(char_img, outline_width, outline_color)

    # Apply opacity
    if opacity < 255:
        r, g, b, a = char_img.split()
        import numpy as np
        a_arr = np.array(a).astype(np.float32)
        a_arr = (a_arr * opacity / 255).astype(np.uint8)
        a = Image.fromarray(a_arr)
        char_img = Image.merge('RGBA', (r, g, b, a))

    # Margins — generous enough that the sticker outline never gets clipped
    margin = 40  # uniform margin on all edges
    bottom_margin = 60  # extra bottom clearance for watermark
    bw, bh = base_img.size

    # Available space the character must fit inside (with margin on every side)
    avail_w = int(bw * 0.45)  # max 45% of card width
    avail_h = bh - bottom_margin - margin
    cw, ch = char_img.size

    # Scale down proportionally if the character exceeds available space
    if cw > avail_w or ch > avail_h:
        scale = min(avail_w / cw, avail_h / ch)
        char_img = char_img.resize((int(cw * scale), int(ch * scale)), Image.LANCZOS)
        cw, ch = char_img.size

    if position == "bottom-right":
        x = bw - cw - margin
        y = bh - ch - bottom_margin
    elif position == "bottom-left":
        x = margin
        y = bh - ch - bottom_margin
    elif position == "right-center":
        x = bw - cw - margin
        y = (bh - ch) // 2
    elif position == "left-center":
        x = margin
        y = (bh - ch) // 2
    else:
        x = bw - cw - margin
        y = bh - ch - bottom_margin

    # Final clamp: character must stay fully within the image bounds
    x = max(margin, min(x, bw - cw - margin))
    y = max(margin, min(y, bh - ch - margin))

    # Composite
    result = base_img.copy()
    result.paste(char_img, (x, y), char_img)
    return result

def create_chart_base():
    """
    Return matplotlib style parameters matching the brand.
    Use this when creating charts with matplotlib.

    Usage in matplotlib:
        import matplotlib.pyplot as plt
        style = create_chart_base()
        plt.rcParams.update(style)
    """
    return {
        'figure.facecolor': COLORS["bg"],
        'axes.facecolor': COLORS["bg"],
        'axes.edgecolor': COLORS["text_muted"],
        'axes.labelcolor': COLORS["text_secondary"],
        'text.color': COLORS["text_primary"],
        'xtick.color': COLORS["text_secondary"],
        'ytick.color': COLORS["text_secondary"],
        'grid.color': COLORS["text_muted"],
        'grid.alpha': 0.3,
        'figure.figsize': (12, 6.75),
        'figure.dpi': 100,
        'font.family': 'sans-serif',
        'font.size': 14,
        'axes.grid': True,
        'grid.linestyle': '--',
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate @4_Bchainbasics branded images")
    parser.add_argument("--type", required=True, choices=["stat_card", "quote_card", "news_header"],
                        help="Type of image to generate")
    parser.add_argument("--headline", default="", help="Main headline/stat (for stat_card)")
    parser.add_argument("--subtext", default="", help="Supporting text (for stat_card)")
    parser.add_argument("--text", default="", help="Quote text (for quote_card)")
    parser.add_argument("--date", default="", help="Date string (for news_header)")
    parser.add_argument("--accent", default=None, help="Override accent color (hex)")
    parser.add_argument("--character", default=None,
                        help="Character pose (e.g. weeter_sad, blubby_excited) or mood (pump, dump, shock, funny)")
    parser.add_argument("--char-position", default="bottom-right",
                        choices=["bottom-right", "bottom-left", "right-center", "left-center"],
                        help="Character position")
    parser.add_argument("--char-height", type=int, default=None, help="Character height in pixels")
    parser.add_argument("--output", required=True, help="Output file path")

    args = parser.parse_args()

    if args.type == "stat_card":
        create_stat_card(args.headline, args.subtext, args.accent, args.output)
    elif args.type == "quote_card":
        create_quote_card(args.text, args.output)
    elif args.type == "news_header":
        create_news_header(args.date, args.output)

    # Add character overlay if requested
    if args.character:
        base = Image.open(args.output).convert('RGBA')
        result = add_character(base, args.character, args.char_position, args.char_height)
        result.save(args.output, "PNG")

    print(f"Generated: {args.output}")
