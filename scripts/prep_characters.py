import argparse
import cv2
import os
import numpy as np
from rembg import remove

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT_DEFAULT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))


def prep_characters(input_folder, output_base):
    if not os.path.exists(output_base):
        os.makedirs(output_base)
    for fileName in os.listdir(input_folder):
        if fileName.lower().endswith((".jpg", ".jpeg", ".png")):
            print(f"Processing sheet: {fileName}")
            input_path = os.path.join(input_folder, fileName)
            with open(input_path, 'rb') as i:
                no_bg = remove(i.read())
            img = cv2.imdecode(np.frombuffer(no_bg, np.uint8), cv2.IMREAD_UNCHANGED)
            alpha = img[:, :, 3]
            contours, _ = cv2.findContours(alpha, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            char_name = "weeter" if "weeter" in fileName.lower() else "blubby"
            emotion = fileName.split("-")[-1].split(".")[0] if "-" in fileName else "neutral"
            save_path = os.path.join(output_base, char_name, emotion)
            os.makedirs(save_path, exist_ok=True)
            for idx, cnt in enumerate(contours):
                x, y, w, h = cv2.boundingRect(cnt)
                if w > 100 and h > 100:
                    cv2.imwrite(f"{save_path}/{char_name}_{idx}.png", img[y:y+h, x:x+w])
    print("\nAsset Factory complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract character sprites from raw sheets (background removal + contour split)."
    )
    parser.add_argument("--project-root", default=PROJECT_ROOT_DEFAULT,
                        help="Project root directory (default: derived from script location)")
    args = parser.parse_args()

    root = args.project_root
    prep_characters(
        os.path.join(root, "data", "raw_sheets"),
        os.path.join(root, "assets", "characters"),
    )
