#!/usr/bin/env python3
"""safe_zone.py - Platform-aware safe zone clamping for video overlays.

Ensures character overlays, text, and UI elements stay within the
visible safe area across different platforms.

Default safe zone (master/YouTube):
  Horizontal: center 56% (22% margin each side)
  Vertical: 10% from top to 65% from top

Usage (library):  from safe_zone import get_safe_bounds, clamp_position
Usage (CLI):      python safe_zone.py 1920 1080 [--platform youtube]
"""
import argparse, sys

SAFE_ZONES = {
    "youtube":         {"h_start": 0.22, "h_end": 0.78, "v_start": 0.10, "v_end": 0.65},
    "instagram_story": {"h_start": 0.08, "h_end": 0.92, "v_start": 0.12, "v_end": 0.75},
    "tiktok":          {"h_start": 0.08, "h_end": 0.92, "v_start": 0.10, "v_end": 0.70},
    "square":          {"h_start": 0.10, "h_end": 0.90, "v_start": 0.10, "v_end": 0.75},
    "default":         {"h_start": 0.22, "h_end": 0.78, "v_start": 0.10, "v_end": 0.65},
}


def get_safe_bounds(frame_w, frame_h, platform="default"):
    """Return the safe zone rectangle as (x, y, w, h) in pixels."""
    zone = SAFE_ZONES.get(platform, SAFE_ZONES["default"])
    x = int(frame_w * zone["h_start"])
    y = int(frame_h * zone["v_start"])
    w = int(frame_w * (zone["h_end"] - zone["h_start"]))
    h = int(frame_h * (zone["v_end"] - zone["v_start"]))
    return x, y, w, h


def clamp_position(overlay_x, overlay_y, overlay_w, overlay_h,
                   frame_w, frame_h, platform="default"):
    """Clamp an overlay position so it stays within the safe zone."""
    sx, sy, sw, sh = get_safe_bounds(frame_w, frame_h, platform)
    if overlay_w >= sw:
        cx = sx + (sw - overlay_w) // 2
    else:
        cx = max(sx, min(overlay_x, sx + sw - overlay_w))
    if overlay_h >= sh:
        cy = sy + (sh - overlay_h) // 2
    else:
        cy = max(sy, min(overlay_y, sy + sh - overlay_h))
    return cx, cy


def center_in_safe_zone(overlay_w, overlay_h, frame_w, frame_h,
                        platform="default"):
    """Return (x, y) to center an overlay within the safe zone."""
    sx, sy, sw, sh = get_safe_bounds(frame_w, frame_h, platform)
    return sx + (sw - overlay_w) // 2, sy + (sh - overlay_h) // 2


def main():
    parser = argparse.ArgumentParser(description="Print safe zone bounds.")
    parser.add_argument("width", type=int, help="Frame width in pixels")
    parser.add_argument("height", type=int, help="Frame height in pixels")
    parser.add_argument("--platform", default="default",
                        choices=list(SAFE_ZONES.keys()))
    args = parser.parse_args()
    x, y, w, h = get_safe_bounds(args.width, args.height, args.platform)
    print(f"Frame:     {args.width}x{args.height}")
    print(f"Platform:  {args.platform}")
    print(f"Safe zone: x={x}, y={y}, w={w}, h={h}")
    print(f"           ({x},{y}) to ({x+w},{y+h})")
    print(f"           Center: ({x + w//2}, {y + h//2})")


if __name__ == "__main__":
    main()
