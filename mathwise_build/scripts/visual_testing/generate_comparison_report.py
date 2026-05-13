#!/usr/bin/env python3
"""Generate side-by-side comparison images and a detailed gap report."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).parent.parent.parent
DESIGN_DIR = BASE_DIR / "screenshots" / "designs"
APP_DIR = BASE_DIR / "screenshots" / "current_app"
REPORT_DIR = BASE_DIR / "screenshots"

SCREENS = [
    ("home", "Home"),
    ("curriculum_list", "Learning / Curriculum"),
    ("games_screen", "Games"),
    ("profile_screen", "Profile"),
    ("concept_content", "Concept Content"),
    ("class_selection", "Class Selection"),
    ("topic_choice", "Topic Choice"),
    ("practice_question", "Practice Question"),
]

VIEWPORTS = ["mobile", "tablet"]


def create_comparison_image(design_path, app_path, output_path, title):
    """Create a side-by-side comparison image."""
    try:
        design = Image.open(design_path)
    except:
        design = Image.new("RGB", (390, 844), color=(240, 240, 240))
    try:
        app = Image.open(app_path)
    except:
        app = Image.new("RGB", (390, 844), color=(240, 240, 240))

    # Resize to same height for comparison
    target_height = min(design.height, app.height, 1200)
    design_ratio = target_height / design.height
    app_ratio = target_height / app.height

    design = design.resize((int(design.width * design_ratio), target_height), Image.LANCZOS)
    app = app.resize((int(app.width * app_ratio), target_height), Image.LANCZOS)

    # Create combined image with labels
    gap = 40
    label_height = 60
    total_width = design.width + gap + app.width
    total_height = target_height + label_height

    combined = Image.new("RGB", (total_width, total_height), color=(255, 255, 255))
    draw = ImageDraw.Draw(combined)

    # Paste images
    combined.paste(design, (0, label_height))
    combined.paste(app, (design.width + gap, label_height))

    # Draw labels
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    except:
        font = ImageFont.load_default()
        font_small = font

    draw.text((20, 15), "🎨 Stitch Design", fill=(44, 95, 159), font=font)
    draw.text((design.width + gap + 20, 15), "📱 Current App", fill=(200, 50, 50), font=font)

    # Draw title
    draw.text((total_width // 2 - 150, total_height - 30), title, fill=(50, 50, 50), font=font_small)

    # Draw separator line
    draw.line([(design.width + gap // 2, label_height), (design.width + gap // 2, total_height)], fill=(200, 200, 200), width=2)

    combined.save(output_path)
    return output_path


def generate_report():
    """Generate comparison images and markdown report."""
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    comparison_paths = []
    for screen_key, screen_name in SCREENS:
        for vp in VIEWPORTS:
            design_path = DESIGN_DIR / f"{screen_key}_{vp}.png"
            app_path = APP_DIR / f"{screen_key}_{vp}.png"

            # Fallback for app screenshots with different naming
            if not app_path.exists():
                if screen_key == "curriculum_list":
                    app_path = APP_DIR / f"learning_{vp}.png"
                elif screen_key == "games_screen":
                    app_path = APP_DIR / f"games_{vp}.png"
                elif screen_key == "profile_screen":
                    app_path = APP_DIR / f"profile_{vp}.png"

            output_path = REPORT_DIR / f"compare_{screen_key}_{vp}.png"

            if design_path.exists() and app_path.exists():
                create_comparison_image(design_path, app_path, output_path, f"{screen_name} — {vp}")
                comparison_paths.append((screen_name, vp, output_path))
                print(f"Generated: {output_path.name}")
            else:
                print(f"Missing: design={design_path.exists()}, app={app_path.exists()} for {screen_key}_{vp}")

    # Generate markdown report
    report_md = f"""# MathWise Design vs App — Gap Analysis Report

**Generated:** 2026-05-09  
**Design Source:** Google Stitch (Project 3966336930966192369)  
**App Version:** Flutter build/web/  
**Viewports:** Mobile (390×844), Tablet (1024×768)

---

## Summary of Gaps

| Screen | Priority | Key Gaps |
|--------|----------|----------|
| Home | P2 | Tablet: Missing bento grid layout |
| Learning/Curriculum | P1 | No expandable accordion; wrong bottom nav labels |
| Games | P1 | Text truncation, vertical overflow, stats layout broken |
| Profile | P1 | Mobile: Stats stack vertically instead of horizontal grid |
| Concept Content | P1 | Not accessible in current app flow |
| Class Selection | P1 | Not accessible in current app flow |
| Topic Choice | P1 | Not accessible in current app flow |
| Practice Question | P1 | Not accessible in current app flow |

---

## Detailed Findings

### 1. 🏠 Home Screen

**Mobile (390×844):**
- ✅ Greeting section matches design
- ✅ Continue Learning card present with progress bar
- ✅ Daily Practice card present
- ✅ Math Playground summary present
- ⚠️ Missing hamburger menu in app bar (design has it)
- ⚠️ Profile avatar is generic icon, not actual photo

**Tablet (1024×768):**
- ❌ **MAJOR:** Design uses bento grid (2-col main cards, 3-col recommended). App shows single column.
- ❌ **MAJOR:** Math Playground card should be horizontal row with icon+text+button. App stacks vertically.
- ❌ Recommended topics should be 3-column grid. App shows 1 column.

### 2. 📚 Learning / Curriculum List

**Mobile (390×844):**
- ✅ Chapter cards present
- ❌ **MAJOR:** No expand/collapse accordion behavior. Design shows expanded Geometry with sub-topics (Lines, Angles, Triangles, Circles).
- ❌ **MAJOR:** Missing sub-topic status indicators (COMPLETE, RESUME, LOCKED).
- ❌ **MAJOR:** Bottom nav mismatch. Design shows Learn/Practice/Progress/Profile. App shows Home/Learning/Games/Profile.
- ❌ Missing "Resume" button on current sub-topic.

**Tablet (1024×768):**
- ❌ Would need to verify responsive behavior (no app screenshot available).

### 3. 🎮 Games Screen

**Mobile (390×844):**
- ✅ Study Time and Lifelines stats present
- ❌ **MAJOR:** Stats should be in horizontal row. App stacks vertically causing overflow.
- ❌ **MAJOR:** "Play & Learn" header text truncated to "Play & Le..."
- ❌ **MAJOR:** Weekly Challenge card cut off / below fold due to overflow
- ❌ Game card text descriptions truncated
- ⚠️ Star badge positioning differs from design

**Tablet (1024×768):**
- ❌ Would need horizontal layout for stats and game cards. Likely broken.

### 4. 👤 Profile Screen

**Mobile (390×844):**
- ✅ Avatar, name, grade, badges present
- ❌ **MAJOR:** Stats (Study Hours, Topics Done, Accuracy) stack vertically. Design shows 3-column horizontal grid.
- ❌ **MAJOR:** Achievements and Topic Progress pushed below fold due to vertical stacking.
- ❌ Badge grid not properly formatted (should be 4 in a row).
- ⚠️ Avatar is placeholder, not actual image.

**Tablet (1024×768):**
- ✅ **GOOD:** App shows horizontal stat grid (3 columns) — matches design!
- ✅ Achievements and Topic Progress side-by-side — matches design!
- ✅ Badge grid (4 columns) — matches design!
- ⚠️ Minor: spacing and padding differences.

### 5. 📖 Concept Content

**Not accessible in current app flow.**
- Design shows: Real-life example, classification guide with images, Pythagorean connection, quick check quiz, practice CTA.
- **Action:** Need to implement this screen or verify it's reachable via Learning → Chapter → Topic → Learn Concept.

### 6. 🎓 Class Selection

**Not accessible in current app flow.**
- Design shows: "Welcome back, Alex!" header, class cards (5-10) with progress bars, daily challenge banner, streak days card.
- **Action:** Need to verify if this is the first screen after onboarding or reachable from Learning tab.

### 7. 🎯 Topic Choice

**Not accessible in current app flow.**
- Design shows: Topic progress bar, "Learn Concept" and "Practice Problems" choice cards with icons and CTAs.
- **Action:** Need to implement or verify navigation path.

### 8. ❓ Practice Question

**Not accessible in current app flow.**
- Design shows: Question counter, progress bar, question text, SVG diagram, 4-option answer grid, Submit button, feedback state with Review Concept / Next Question buttons, dot indicators.
- **Action:** Need to implement or verify navigation path.

---

## Responsive Issues Summary

| Viewport | Screens with Issues |
|----------|-------------------|
| Mobile (390×844) | Games (overflow), Profile (vertical stack), Learning (no accordion) |
| Tablet (1024×768) | Home (missing bento grid), Games (likely overflow), Learning (unknown) |

---

## Recommended Fix Order

### Phase 1: Critical Fixes (P1)
1. **Profile Mobile** — Convert stat cards to horizontal grid (`Wrap` + `Expanded` or `Row`)
2. **Games Mobile** — Fix text truncation with `Expanded`/`Flexible`; use horizontal stats row
3. **Learning** — Implement expandable accordion for chapter cards; show sub-topics
4. **Navigation** — Verify Class Selection → Curriculum → Topic Choice → Concept/Practice flow exists

### Phase 2: Layout Fixes (P2)
5. **Home Tablet** — Implement bento grid layout (2-col for main cards, 3-col for recommended)
6. **Games Tablet** — Horizontal layout for stats and game cards
7. **Bottom Nav** — Align nav items with design (Home/Learning/Games/Profile globally; or context-aware)

### Phase 3: Polish (P3)
8. Add hamburger menu to app bar
9. Use actual profile avatar images
10. Fine-tune spacing, shadows, and border radii to match design tokens exactly

---

*Report generated by design comparison pipeline.*
"""

    report_path = REPORT_DIR / "GAP_ANALYSIS_REPORT.md"
    report_path.write_text(report_md)
    print(f"\nReport saved: {report_path}")

    return comparison_paths


if __name__ == "__main__":
    generate_report()
