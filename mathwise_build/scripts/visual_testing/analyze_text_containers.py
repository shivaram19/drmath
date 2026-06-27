#!/usr/bin/env python3
"""Analyze text alignment and overflow within containers by cropping key regions."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).parent.parent.parent
DESIGN_DIR = BASE_DIR / "screenshots" / "designs"
APP_DIR = BASE_DIR / "screenshots" / "current_app"
OUTPUT_DIR = BASE_DIR / "screenshots" / "text_analysis"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def crop_region(img_path, x, y, w, h, label, save_path):
    """Crop a region and save with label overlay."""
    img = Image.open(img_path)
    # Scale coords if image is larger/smaller than expected
    scale_x = img.width / 390 if img.width != 390 else 1
    scale_y = img.height / 844 if img.height != 844 else 1
    
    x = int(x * scale_x)
    y = int(y * scale_y)
    w = int(w * scale_x)
    h = int(h * scale_y)
    
    crop = img.crop((x, y, x + w, y + h))
    
    # Add border and label
    bordered = Image.new("RGB", (crop.width + 4, crop.height + 24), color=(255, 0, 0))
    bordered.paste(crop, (2, 22))
    draw = ImageDraw.Draw(bordered)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
    except:
        font = ImageFont.load_default()
    draw.text((4, 2), label, fill=(255, 255, 255), font=font)
    
    bordered.save(save_path)
    return save_path


def analyze_home_screen():
    """Analyze Home screen text containers."""
    print("\n=== HOME SCREEN TEXT ANALYSIS ===")
    
    # Define key text regions (x, y, w, h) for mobile viewport
    regions = [
        ("greeting", 20, 80, 350, 60, "Greeting text"),
        ("continue_label", 30, 160, 200, 25, "'CONTINUE LEARNING' label"),
        ("chapter_title", 30, 190, 280, 60, "Chapter title 'Geometry → Circles'"),
        ("chapter_desc", 30, 255, 330, 40, "Chapter description"),
        ("progress_label", 30, 310, 150, 25, "'Course Progress' label"),
        ("progress_pct", 310, 310, 60, 25, "Progress percentage"),
        ("resume_btn", 30, 370, 330, 50, "Resume Lesson button"),
        ("daily_title", 30, 470, 330, 30, "'Daily Practice' title"),
        ("daily_subtitle", 30, 505, 330, 25, "'10 Questions Ready' subtitle"),
        ("daily_btn", 30, 545, 330, 50, "'Start Now' button"),
        ("playground_title", 30, 640, 200, 30, "'Math Playground' title"),
        ("playground_stats", 30, 675, 330, 50, "Playground stats row"),
        ("enter_games_btn", 30, 735, 330, 45, "'Enter Games' button"),
    ]
    
    for key, x, y, w, h, label in regions:
        for source, src_dir in [("design", DESIGN_DIR), ("app", APP_DIR)]:
            img_path = src_dir / "home_page_mobile.png"
            if img_path.exists():
                save_path = OUTPUT_DIR / f"home_{source}_{key}.png"
                crop_region(img_path, x, y, w, h, f"{source}: {label}", save_path)
    
    print(f"Cropped {len(regions)} regions. Saved to {OUTPUT_DIR}")


def analyze_games_screen():
    """Analyze Games screen text containers — known overflow area."""
    print("\n=== GAMES SCREEN TEXT ANALYSIS ===")
    
    regions = [
        ("stats_row", 20, 60, 350, 80, "Stats row (Study Time + Lifelines)"),
        ("header_title", 20, 150, 200, 35, "'Play & Learn' header"),
        ("header_subtitle", 200, 150, 170, 35, "'Unlocked by your effort'"),
        ("game1_badge", 240, 195, 120, 30, "Game 1 star badge"),
        ("game1_title", 20, 340, 350, 35, "'Math Detective' title"),
        ("game1_desc", 20, 380, 350, 50, "Game 1 description"),
        ("game1_btn", 20, 440, 350, 50, "'Play Now' button"),
        ("game2_badge", 240, 500, 120, 30, "Game 2 star badge"),
        ("game2_title", 20, 645, 350, 35, "'Puzzle Escape' title"),
        ("game2_desc", 20, 685, 350, 50, "Game 2 description"),
        ("weekly_title", 80, 770, 280, 30, "'Weekly Challenge' title"),
        ("weekly_timer", 80, 805, 280, 25, "Timer text"),
        ("weekly_btn", 20, 850, 350, 50, "'Join Competition' button"),
    ]
    
    for key, x, y, w, h, label in regions:
        for source, src_dir in [("design", DESIGN_DIR), ("app", APP_DIR)]:
            img_path = src_dir / "games_screen_mobile.png"
            if img_path.exists():
                save_path = OUTPUT_DIR / f"games_{source}_{key}.png"
                crop_region(img_path, x, y, w, h, f"{source}: {label}", save_path)
    
    print(f"Cropped {len(regions)} regions.")


def analyze_profile_screen():
    """Analyze Profile screen text containers."""
    print("\n=== PROFILE SCREEN TEXT ANALYSIS ===")
    
    regions = [
        ("name", 20, 60, 350, 45, "Name 'Alex Johnson'"),
        ("grade", 20, 110, 350, 25, "Grade info"),
        ("badges", 80, 145, 230, 30, "Level badges"),
        ("stat1", 20, 200, 350, 70, "Stat card 1 (Study Hours)"),
        ("stat2", 20, 280, 350, 70, "Stat card 2 (Topics Done)"),
        ("stat3", 20, 360, 350, 70, "Stat card 3 (Accuracy)"),
        ("achieve_header", 20, 450, 350, 35, "'Achievements' header"),
        ("trophy_card", 20, 500, 350, 70, "Trophy card"),
        ("badge_grid", 20, 580, 350, 80, "Badge grid (4 items)"),
        ("progress_header", 20, 670, 350, 35, "'Topic Progress' header"),
        ("progress_bar1", 20, 715, 350, 45, "Progress bar 1"),
        ("progress_bar2", 20, 770, 350, 45, "Progress bar 2"),
    ]
    
    for key, x, y, w, h, label in regions:
        for source, src_dir in [("design", DESIGN_DIR), ("app", APP_DIR)]:
            img_path = src_dir / "profile_screen_mobile.png"
            if not img_path.exists():
                img_path = src_dir / "profile_mobile.png"
            if img_path.exists():
                save_path = OUTPUT_DIR / f"profile_{source}_{key}.png"
                crop_region(img_path, x, y, w, h, f"{source}: {label}", save_path)
    
    print(f"Cropped {len(regions)} regions.")


def analyze_learning_screen():
    """Analyze Learning/Curriculum screen text containers."""
    print("\n=== LEARNING SCREEN TEXT ANALYSIS ===")
    
    regions = [
        ("header_title", 20, 60, 350, 45, "'Math Curriculum' title"),
        ("header_subtitle", 20, 110, 350, 50, "Subtitle text"),
        ("chapter1", 20, 180, 350, 80, "Chapter 1 card"),
        ("chapter2", 20, 275, 350, 80, "Chapter 2 card (expanded header)"),
        ("subtopic1", 40, 365, 330, 45, "Sub-topic 'Lines'"),
        ("subtopic2", 40, 415, 330, 45, "Sub-topic 'Angles'"),
        ("subtopic3", 40, 465, 330, 45, "Sub-topic 'Triangles' (current)"),
        ("subtopic4", 40, 515, 330, 45, "Sub-topic 'Circles' (locked)"),
        ("chapter3", 20, 575, 350, 80, "Chapter 3 card (locked)"),
    ]
    
    for key, x, y, w, h, label in regions:
        for source, src_dir in [("design", DESIGN_DIR), ("app", APP_DIR)]:
            img_path = src_dir / "curriculum_list_mobile.png"
            if not img_path.exists():
                img_path = src_dir / "learning_mobile.png"
            if img_path.exists():
                save_path = OUTPUT_DIR / f"learning_{source}_{key}.png"
                crop_region(img_path, x, y, w, h, f"{source}: {label}", save_path)
    
    print(f"Cropped {len(regions)} regions.")


def analyze_practice_screen():
    """Analyze Practice Question screen text containers."""
    print("\n=== PRACTICE QUESTION TEXT ANALYSIS ===")
    
    regions = [
        ("mastery_label", 20, 55, 350, 25, "'Geometry Mastery' label"),
        ("question_counter", 20, 85, 350, 40, "'Question 1 of 8'"),
        ("progress_bar", 20, 135, 350, 20, "Progress bar"),
        ("question_text", 30, 170, 330, 80, "Question text"),
        ("diagram", 30, 260, 330, 150, "SVG diagram area"),
        ("option_a", 30, 420, 330, 55, "Option A"),
        ("option_b", 30, 485, 330, 55, "Option B (selected)"),
        ("option_c", 30, 550, 330, 55, "Option C"),
        ("option_d", 30, 615, 330, 55, "Option D"),
        ("submit_btn", 30, 685, 330, 55, "'Submit Answer' button"),
        ("feedback_title", 30, 755, 330, 35, "'Not quite right'"),
        ("feedback_desc", 30, 795, 330, 45, "Feedback description"),
    ]
    
    for key, x, y, w, h, label in regions:
        for source, src_dir in [("design", DESIGN_DIR), ("app", APP_DIR)]:
            img_path = src_dir / "practice_question_mobile.png"
            if img_path.exists():
                save_path = OUTPUT_DIR / f"practice_{source}_{key}.png"
                crop_region(img_path, x, y, w, h, f"{source}: {label}", save_path)
    
    print(f"Cropped {len(regions)} regions.")


def create_comparison_strip():
    """Create a visual strip comparing design vs app for key overflow areas."""
    
    # Focus on the most problematic areas
    comparisons = [
        ("games_header", DESIGN_DIR / "games_screen_mobile.png", APP_DIR / "games_mobile.png", 
         20, 140, 350, 60, "Games: 'Play & Learn' Header"),
        ("games_stats", DESIGN_DIR / "games_screen_mobile.png", APP_DIR / "games_mobile.png",
         20, 55, 350, 90, "Games: Stats Row"),
        ("profile_stats", DESIGN_DIR / "profile_screen_mobile.png", APP_DIR / "profile_mobile.png",
         20, 195, 350, 240, "Profile: Stats Cards"),
        ("learning_subtopics", DESIGN_DIR / "curriculum_list_mobile.png", APP_DIR / "learning_mobile.png",
         20, 270, 350, 300, "Learning: Expanded Chapter + Sub-topics"),
    ]
    
    for name, design_path, app_path, x, y, w, h, label in comparisons:
        if not design_path.exists() or not app_path.exists():
            continue
            
        design = Image.open(design_path)
        app = Image.open(app_path)
        
        d_crop = design.crop((x, y, x + w, y + h))
        a_crop = app.crop((x, y, x + w, y + h))
        
        # Resize to same width
        target_w = 400
        d_scaled = d_crop.resize((target_w, int(d_crop.height * target_w / d_crop.width)), Image.LANCZOS)
        a_scaled = a_crop.resize((target_w, int(a_crop.height * target_w / a_crop.width)), Image.LANCZOS)
        
        gap = 20
        total_h = max(d_scaled.height, a_scaled.height) + 40
        combined = Image.new("RGB", (target_w * 2 + gap, total_h), color=(245, 245, 245))
        draw = ImageDraw.Draw(combined)
        
        combined.paste(d_scaled, (0, 40))
        combined.paste(a_scaled, (target_w + gap, 40))
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        except:
            font = ImageFont.load_default()
        
        draw.text((10, 10), f"🎨 DESIGN: {label}", fill=(44, 95, 159), font=font)
        draw.text((target_w + gap + 10, 10), f"📱 APP: {label}", fill=(200, 50, 50), font=font)
        
        # Draw red boxes around text areas in app
        draw.rectangle([(target_w + gap, 40), (target_w * 2 + gap, 40 + a_scaled.height)], outline=(255, 0, 0), width=2)
        
        save_path = OUTPUT_DIR / f"compare_{name}.png"
        combined.save(save_path)
        print(f"Comparison strip: {save_path.name}")


if __name__ == "__main__":
    analyze_home_screen()
    analyze_games_screen()
    analyze_profile_screen()
    analyze_learning_screen()
    analyze_practice_screen()
    create_comparison_strip()
    print(f"\nAll text analysis saved to {OUTPUT_DIR}")
