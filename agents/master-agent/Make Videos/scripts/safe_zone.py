#!/usr/bin/env python3
"""
Safe Zone Enforcement Module — Ridgemont Studio
Ensures all overlays stay within platform-safe regions.

Horizontal Safe Zone (16:9 master): center 56% (x: 424-1496 at 1920px)
Vertical Social UI Safe Zone (9:16): Y 10-65%, X 10-85%

Usage:
    from safe_zone import enforce_safe_zone
    x, y = enforce_safe_zone(x, y, w, h, frame_w, frame_h, "master")
"""

def enforce_safe_zone(overlay_x, overlay_y, overlay_w, overlay_h,
                      frame_width, frame_height, format_type="master"):
    """
    Auto-snap overlay into appropriate safe zone.
    Returns corrected (x, y) position.
    
    format_type:
        "master" — 16:9 horizontal, only horizontal safe zone
        "short", "tiktok", "reel" — 9:16 vertical, full social UI safe zone
    """
    if format_type == "master":
        # Horizontal: only worry about left/right crop
        safe_left = int(frame_width * 0.22)   # 424 at 1920
        safe_right = int(frame_width * 0.78)  # 1496 at 1920
        if overlay_x < safe_left:
            overlay_x = safe_left
        if overlay_x + overlay_w > safe_right:
            overlay_x = safe_right - overlay_w
        if overlay_w > (safe_right - safe_left):
            overlay_x = (frame_width - overlay_w) // 2

    elif format_type in ("short", "tiktok", "reel"):
        # Vertical: avoid platform UI on all sides
        safe_left = int(frame_width * 0.10)    # 108 at 1080
        safe_right = int(frame_width * 0.85)   # 918 at 1080
        safe_top = int(frame_height * 0.10)    # 192 at 1920
        safe_bottom = int(frame_height * 0.65) # 1248 at 1920

        if overlay_x < safe_left:
            overlay_x = safe_left
        if overlay_x + overlay_w > safe_right:
            overlay_x = safe_right - overlay_w
        if overlay_y < safe_top:
            overlay_y = safe_top
        if overlay_y + overlay_h > safe_bottom:
            overlay_y = safe_bottom - overlay_h

        # Center horizontally if wider than safe zone
        if overlay_w > (safe_right - safe_left):
            overlay_x = (frame_width - overlay_w) // 2

    return overlay_x, overlay_y


def get_safe_zone_bounds(frame_width, frame_height, format_type="master"):
    """Return (left, top, right, bottom) bounds for the given format."""
    if format_type == "master":
        return (
            int(frame_width * 0.22),
            0,
            int(frame_width * 0.78),
            frame_height
        )
    elif format_type in ("short", "tiktok", "reel"):
        return (
            int(frame_width * 0.10),
            int(frame_height * 0.10),
            int(frame_width * 0.85),
            int(frame_height * 0.65)
        )
    return (0, 0, frame_width, frame_height)
