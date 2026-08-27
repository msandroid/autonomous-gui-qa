"""
Screenshot Visual Annotator: Draws bounding boxes and defect labels on images.
"""

import os
from typing import List, Dict, Any

class VisualAnnotator:
    """Draws bounding boxes on screenshots using Pillow."""

    SEVERITY_COLORS = {
        "CRITICAL": (220, 38, 38, 255),   # Red
        "HIGH": (234, 88, 12, 255),       # Orange
        "MEDIUM": (202, 138, 4, 255),     # Yellow
        "LOW": (37, 99, 235, 255),        # Blue
    }

    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def annotate(self, image_path: str, defects: List[Dict[str, Any]], step_name: str) -> str:
        try:
            from PIL import Image, ImageDraw, ImageFont
        except ImportError:
            print("[VisualAnnotator] Pillow not installed, skipping annotation.")
            return image_path

        if not os.path.exists(image_path):
            return image_path

        img = Image.open(image_path).convert("RGBA")
        overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)
        w, h = img.size

        font = None
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size=max(14, int(h * 0.018)))
        except Exception:
            font = ImageFont.load_default()

        for idx, defect in enumerate(defects, 1):
            bbox = defect.get("bounding_box", [0, 0, 0, 0])
            severity = defect.get("severity", "MEDIUM").upper()
            category = defect.get("category", "DEFECT")

            ymin, xmin, ymax, xmax = bbox
            px_ymin = int((ymin / 1000.0) * h)
            px_xmin = int((xmin / 1000.0) * w)
            px_ymax = int((ymax / 1000.0) * h)
            px_xmax = int((xmax / 1000.0) * w)

            color = self.SEVERITY_COLORS.get(severity, (234, 88, 12, 255))
            fill_color = (color[0], color[1], color[2], 40)

            # Box fill & outline
            draw.rectangle([px_xmin, px_ymin, px_xmax, px_ymax], outline=color, fill=fill_color, width=4)

            # Label banner
            label = f"#{idx} [{severity}] {category}"
            draw.rectangle([px_xmin, max(0, px_ymin - 24), px_xmin + len(label) * 9, px_ymin], fill=color)
            draw.text((px_xmin + 4, max(0, px_ymin - 22)), label, fill=(255, 255, 255, 255), font=font)

        out_img = Image.alpha_composite(img, overlay).convert("RGB")
        base_name = os.path.basename(image_path)
        annotated_path = os.path.join(self.output_dir, f"annotated_{step_name}_{base_name}")
        out_img.save(annotated_path, "PNG")
        return annotated_path
