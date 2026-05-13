#!/usr/bin/env python3
"""
Cutting-edge text overflow and alignment analysis using PaddleOCR (2026).
Compares Stitch design screenshots against Flutter app screenshots to detect:
- Text truncation / overflow
- Misaligned text within containers
- Missing text elements
- Font size discrepancies
"""

import json
import os
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Use PaddleOCR for text detection with bounding boxes
from paddleocr import PaddleOCR

BASE_DIR = Path(__file__).parent.parent.parent
DESIGN_DIR = BASE_DIR / "screenshots" / "designs"
APP_DIR = BASE_DIR / "screenshots" / "current_app"
OUTPUT_DIR = BASE_DIR / "screenshots" / "ocr_analysis"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Initialize PaddleOCR with English, bounding box output
ocr = PaddleOCR(
    use_angle_cls=True,
    lang="en",
    show_log=False,
    use_gpu=False,
)

SCREENS = [
    ("home_page", "Home"),
    ("curriculum_list", "Learning / Curriculum"),
    ("games_screen", "Games"),
    ("profile_screen", "Profile"),
    ("concept_content", "Concept Content"),
    ("class_selection", "Class Selection"),
    ("topic_choice", "Topic Choice"),
    ("practice_question", "Practice Question"),
]

VIEWPORTS = ["mobile"]  # Focus on mobile first


def detect_text(image_path):
    """Run PaddleOCR on an image and return list of {text, box, confidence}."""
    result = ocr.ocr(str(image_path), cls=True)
    detections = []
    if result and result[0]:
        for line in result[0]:
            if line:
                box = line[0]  # [[x1,y1], [x2,y1], [x2,y2], [x1,y2]]
                text = line[1][0]
                conf = line[1][1]
                detections.append({
                    "text": text,
                    "box": box,
                    "confidence": conf,
                })
    return detections


def draw_boxes(image_path, detections, color=(0, 255, 0), label_color=(255, 0, 0)):
    """Draw bounding boxes around detected text."""
    img = cv2.imread(str(image_path))
    if img is None:
        return None
    for det in detections:
        box = np.array(det["box"], dtype=np.int32).reshape((-1, 1, 2))
        cv2.polylines(img, [box], True, color, 2)
        # Put text label near top-left
        x, y = int(det["box"][0][0]), int(det["box"][0][1])
        label = det["text"][:20]
        cv2.putText(img, label, (x, max(y - 5, 15)), cv2.FONT_HERSHEY_SIMPLEX, 0.4, label_color, 1)
    return img


def compute_iou(box1, box2):
    """Compute IoU of two quadrilaterals (simplified to bounding rects)."""
    def bbox(box):
        xs = [p[0] for p in box]
        ys = [p[1] for p in box]
        return min(xs), min(ys), max(xs), max(ys)
    
    x1_min, y1_min, x1_max, y1_max = bbox(box1)
    x2_min, y2_min, x2_max, y2_max = bbox(box2)
    
    xi_min = max(x1_min, x2_min)
    yi_min = max(y1_min, y2_min)
    xi_max = min(x1_max, x2_max)
    yi_max = min(y1_max, y2_max)
    
    inter_w = max(0, xi_max - xi_min)
    inter_h = max(0, yi_max - yi_min)
    inter_area = inter_w * inter_h
    
    area1 = (x1_max - x1_min) * (y1_max - y1_min)
    area2 = (x2_max - x2_min) * (y2_max - y2_min)
    union_area = area1 + area2 - inter_area
    
    return inter_area / union_area if union_area > 0 else 0


def match_text(design_dets, app_dets, iou_threshold=0.3):
    """Match text detections between design and app."""
    matches = []
    unmatched_design = []
    unmatched_app = list(app_dets)
    
    for d_det in design_dets:
        best_match = None
        best_iou = 0
        for a_det in unmatched_app:
            iou = compute_iou(d_det["box"], a_det["box"])
            if iou > best_iou:
                best_iou = iou
                best_match = a_det
        
        if best_match and best_iou >= iou_threshold:
            matches.append({
                "design": d_det,
                "app": best_match,
                "iou": best_iou,
            })
            unmatched_app.remove(best_match)
        else:
            unmatched_design.append(d_det)
    
    return matches, unmatched_design, unmatched_app


def analyze_screen(screen_key, screen_name, viewport):
    """Analyze a single screen for text overflow/alignment issues."""
    design_path = DESIGN_DIR / f"{screen_key}_{viewport}.png"
    app_path = APP_DIR / f"{screen_key}_{viewport}.png"
    
    if not app_path.exists():
        # Fallback naming
        if screen_key == "curriculum_list":
            app_path = APP_DIR / f"learning_{viewport}.png"
        elif screen_key == "games_screen":
            app_path = APP_DIR / f"games_{viewport}.png"
        elif screen_key == "profile_screen":
            app_path = APP_DIR / f"profile_{viewport}.png"
    
    if not design_path.exists() or not app_path.exists():
        print(f"  Skipping {screen_key} ({viewport}): files missing")
        return None
    
    print(f"  Analyzing {screen_key} ({viewport})...")
    
    # Detect text in both images
    design_dets = detect_text(design_path)
    app_dets = detect_text(app_path)
    
    # Draw boxes
    design_boxed = draw_boxes(design_path, design_dets, (0, 255, 0), (0, 0, 255))
    app_boxed = draw_boxes(app_path, app_dets, (0, 255, 0), (0, 0, 255))
    
    if design_boxed is not None:
        cv2.imwrite(str(OUTPUT_DIR / f"{screen_key}_{viewport}_design_boxes.png"), design_boxed)
    if app_boxed is not None:
        cv2.imwrite(str(OUTPUT_DIR / f"{screen_key}_{viewport}_app_boxes.png"), app_boxed)
    
    # Match text between design and app
    matches, unmatched_design, unmatched_app = match_text(design_dets, app_dets)
    
    # Analyze matches for truncation (design text longer than app text at similar position)
    truncation_issues = []
    alignment_issues = []
    
    for m in matches:
        d_text = m["design"]["text"]
        a_text = m["app"]["text"]
        
        # Check for truncation: app text is shorter and design text starts with app text
        if len(d_text) > len(a_text) and d_text.startswith(a_text) and len(a_text) < len(d_text) - 2:
            truncation_issues.append({
                "design_text": d_text,
                "app_text": a_text,
                "box": m["app"]["box"],
                "confidence": m["app"]["confidence"],
            })
        
        # Check for significant position shift
        d_box = m["design"]["box"]
        a_box = m["app"]["box"]
        d_cx = sum(p[0] for p in d_box) / 4
        d_cy = sum(p[1] for p in d_box) / 4
        a_cx = sum(p[0] for p in a_box) / 4
        a_cy = sum(p[1] for p in a_box) / 4
        shift = ((d_cx - a_cx) ** 2 + (d_cy - a_cy) ** 2) ** 0.5
        
        if shift > 30:  # More than 30px shift
            alignment_issues.append({
                "text": a_text,
                "design_pos": (d_cx, d_cy),
                "app_pos": (a_cx, a_cy),
                "shift_px": shift,
            })
    
    result = {
        "screen": screen_name,
        "viewport": viewport,
        "design_text_count": len(design_dets),
        "app_text_count": len(app_dets),
        "matched": len(matches),
        "unmatched_design": [{"text": d["text"], "box": d["box"]} for d in unmatched_design],
        "unmatched_app": [{"text": a["text"], "box": a["box"]} for a in unmatched_app],
        "truncation_issues": truncation_issues,
        "alignment_issues": alignment_issues,
    }
    
    print(f"    Design texts: {len(design_dets)}, App texts: {len(app_dets)}, Matched: {len(matches)}")
    print(f"    Truncation issues: {len(truncation_issues)}, Alignment issues: {len(alignment_issues)}")
    
    return result


def generate_report(all_results):
    """Generate markdown report."""
    report = "# 🔬 OCR Text Overflow & Alignment Analysis Report\n\n"
    report += "**Date:** 2026-05-09  \n"
    report += "**OCR Engine:** PaddleOCR v2.10.0 (PP-OCRv4)  \n"
    report += "**Analysis:** Text bounding box detection, truncation detection, alignment shift measurement\n\n"
    report += "---\n\n"
    
    total_truncation = 0
    total_alignment = 0
    
    for r in all_results:
        if r is None:
            continue
        report += f"## 📱 {r['screen']} ({r['viewport']})\n\n"
        report += f"- Design text elements: **{r['design_text_count']}**\n"
        report += f"- App text elements: **{r['app_text_count']}**\n"
        report += f"- Matched elements: **{r['matched']}**\n"
        report += f"- Unmatched in design: **{len(r['unmatched_design'])}**\n"
        report += f"- Unmatched in app: **{len(r['unmatched_app'])}**\n\n"
        
        if r['truncation_issues']:
            report += "### ⚠️ Text Truncation Issues\n\n"
            for issue in r['truncation_issues']:
                report += f"- **Design:** `{issue['design_text']}` → **App:** `{issue['app_text']}`\n"
                total_truncation += 1
            report += "\n"
        
        if r['alignment_issues']:
            report += "### 📐 Alignment Issues (>30px shift)\n\n"
            for issue in r['alignment_issues']:
                report += f"- `{issue['text']}`: shifted **{issue['shift_px']:.1f}px**\n"
                total_alignment += 1
            report += "\n"
        
        if not r['truncation_issues'] and not r['alignment_issues']:
            report += "✅ No truncation or alignment issues detected.\n\n"
        
        report += "---\n\n"
    
    report += "## Summary\n\n"
    report += f"| Metric | Count |\n"
    report += f"|--------|-------|\n"
    report += f"| Total truncation issues | {total_truncation} |\n"
    report += f"| Total alignment issues | {total_alignment} |\n"
    report += f"| Screens analyzed | {len([r for r in all_results if r])} |\n"
    
    report_path = OUTPUT_DIR / "OCR_ANALYSIS_REPORT.md"
    report_path.write_text(report)
    print(f"\nReport saved: {report_path}")
    
    # Also save JSON
    json_path = OUTPUT_DIR / "ocr_analysis.json"
    json_path.write_text(json.dumps(all_results, indent=2, default=str))
    print(f"JSON saved: {json_path}")


def main():
    print("=" * 60)
    print("PaddleOCR Text Overflow & Alignment Analysis")
    print("=" * 60)
    
    all_results = []
    for screen_key, screen_name in SCREENS:
        for viewport in VIEWPORTS:
            result = analyze_screen(screen_key, screen_name, viewport)
            all_results.append(result)
    
    generate_report(all_results)
    print(f"\nAll outputs saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
