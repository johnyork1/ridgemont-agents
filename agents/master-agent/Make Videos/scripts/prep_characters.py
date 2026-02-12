#!/usr/bin/env python3
"""
Asset Factory: Transform flat character sheets into transparent PNG library.
Uses rembg for background removal and OpenCV for pose auto-slicing.
Run ONCE during setup, then only when new sheets are added.

Directory expectations:
  Input:  data/raw_sheets/
          Files named like: Weeter-happy.jpg, Blubby-cool.png,
          Together-hype.jpg, Weeter-poses_2.jpg
  Output: assets/characters/{character}/{emotion}/

Supports slice_overrides.json for manual bounding box corrections.
"""

import cv2
import os
import json
import numpy as np
from rembg import remove

MIN_POSE_WIDTH = 100
MIN_POSE_HEIGHT = 100
PADDING = 10

def load_slice_overrides(overrides_path):
    if os.path.exists(overrides_path):
        with open(overrides_path, 'r') as f:
            return json.load(f)
    return {}

def parse_filename(filename):
    base = os.path.splitext(filename)[0].lower()
    parts = base.split("-")
    if "together" in parts[0]:
        char_name = "together"
    elif "blubby" in parts[0]:
        char_name = "blubby"
    elif "weeter" in parts[0]:
        char_name = "weeter"
    else:
        char_name = "unknown"
    if len(parts) > 1:
        emotion_raw = parts[1].split("_")[0]
        emotion_map = {
            "happy": "happy", "hype": "hype", "cool": "cool",
            "sad": "sad", "angry": "angry", "smart": "smart",
            "love": "love", "neutral": "neutral", "fun": "fun",
            "poses": "neutral", "meme": "meme_sign", "sign": "meme_sign",
        }
        emotion = emotion_map.get(emotion_raw, "neutral")
    else:
        emotion = "neutral"
    return char_name, emotion

def strip_background(image_path):
    with open(image_path, 'rb') as f:
        input_data = f.read()
    output_data = remove(input_data)
    nparr = np.frombuffer(output_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
    return img

def auto_slice_poses(img):
    if img.shape[2] < 4:
        print("  WARNING: No alpha channel after background removal.")
        return []
    alpha = img[:, :, 3]
    contours, _ = cv2.findContours(alpha, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    pose_rects = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w >= MIN_POSE_WIDTH and h >= MIN_POSE_HEIGHT:
            pose_rects.append((x, y, w, h))
    pose_rects.sort(key=lambda r: (r[1] // 200, r[0]))
    sorted_poses = []
    for (x, y, w, h) in pose_rects:
        x1, y1 = max(0, x - PADDING), max(0, y - PADDING)
        x2, y2 = min(img.shape[1], x + w + PADDING), min(img.shape[0], y + h + PADDING)
        sorted_poses.append(img[y1:y2, x1:x2])
    return sorted_poses

def apply_overrides(filename, img, overrides):
    if filename not in overrides:
        return None
    manual_poses = []
    for box in overrides[filename]:
        x, y, w, h = box["x"], box["y"], box["w"], box["h"]
        name = box.get("name", f"override_{len(manual_poses)}")
        pose = img[y:y+h, x:x+w]
        manual_poses.append((name, pose))
    return manual_poses

def prep_characters(input_folder, output_base, overrides_path=None):
    overrides = load_slice_overrides(overrides_path or
                                      os.path.join(input_folder, "slice_overrides.json"))
    os.makedirs(output_base, exist_ok=True)
    for filename in sorted(os.listdir(input_folder)):
        if not filename.lower().endswith((".jpg", ".jpeg", ".png")):
            continue
        print(f"\nProcessing: {filename}")
        char_name, emotion = parse_filename(filename)
        print(f"  Character: {char_name}, Emotion: {emotion}")
        input_path = os.path.join(input_folder, filename)
        img = strip_background(input_path)
        print(f"  Background removed. Shape: {img.shape}")
        manual = apply_overrides(filename, img, overrides)
        if manual:
            print(f"  Using {len(manual)} manual overrides")
            for name, pose in manual:
                save_dir = os.path.join(output_base, char_name, emotion)
                os.makedirs(save_dir, exist_ok=True)
                save_path = os.path.join(save_dir, f"{name}.png")
                cv2.imwrite(save_path, pose)
                print(f"  Saved: {save_path}")
        else:
            poses = auto_slice_poses(img)
            print(f"  Auto-detected {len(poses)} poses")
            if len(poses) == 0:
                save_dir = os.path.join(output_base, char_name, emotion)
                os.makedirs(save_dir, exist_ok=True)
                save_path = os.path.join(save_dir, f"{char_name}_0.png")
                cv2.imwrite(save_path, img)
                print(f"  Saved (full sheet): {save_path}")
            else:
                for idx, pose in enumerate(poses):
                    save_dir = os.path.join(output_base, char_name, emotion)
                    os.makedirs(save_dir, exist_ok=True)
                    save_path = os.path.join(save_dir, f"{char_name}_{idx}.png")
                    cv2.imwrite(save_path, pose)
                    print(f"  Saved: {save_path}")
    print(f"\nAsset Factory complete. Output: {output_base}")
    print("NEXT: Rename auto-numbered files to descriptive names")
    print("(e.g., weeter_0.png → thumbs_up.png)")

if __name__ == "__main__":
    prep_characters(
        input_folder="data/raw_sheets",
        output_base="assets/characters",
        overrides_path="data/raw_sheets/slice_overrides.json"
    )
