#!/usr/bin/env python3
"""Generate final comprehensive gap report with all findings."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).parent.parent.parent
REPORT_DIR = BASE_DIR / "screenshots"
OUTPUT_DIR = REPORT_DIR / "final_report"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def create_full_comparison_strip():
    """Create comprehensive side-by-side comparison for all screens."""
    screens = [
        ("home_page", "Home", "home"),
        ("curriculum_list", "Learning / Curriculum", "learning"),
        ("games_screen", "Games", "games"),
        ("profile_screen", "Profile", "profile"),
    ]
    
    for design_key, name, app_key in screens:
        design_path = REPORT_DIR / "designs" / f"{design_key}_mobile.png"
        app_path = REPORT_DIR / "current_app" / f"{app_key}_mobile.png"
        
        if not design_path.exists() or not app_path.exists():
            continue
        
        design = Image.open(design_path)
        app = Image.open(app_path)
        
        # Scale to same width for comparison
        target_w = 350
        d_scale = target_w / design.width
        a_scale = target_w / app.width
        
        d_h = int(design.height * d_scale)
        a_h = int(app.height * a_scale)
        
        d_img = design.resize((target_w, d_h), Image.LANCZOS)
        a_img = app.resize((target_w, a_h), Image.LANCZOS)
        
        # Create combined
        gap = 30
        label_h = 40
        total_w = target_w * 2 + gap
        total_h = max(d_h, a_h) + label_h + 20
        
        combined = Image.new("RGB", (total_w, total_h), color=(250, 250, 250))
        draw = ImageDraw.Draw(combined)
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        except:
            font = ImageFont.load_default()
            font_small = font
        
        # Labels
        draw.text((10, 10), f"🎨 DESIGN: {name}", fill=(44, 95, 159), font=font)
        draw.text((target_w + gap + 10, 10), f"📱 APP: {name}", fill=(200, 50, 50), font=font)
        
        # Images
        combined.paste(d_img, (0, label_h))
        combined.paste(a_img, (target_w + gap, label_h))
        
        # Separator
        draw.line([(target_w + gap // 2, label_h), (target_w + gap // 2, total_h)], fill=(200, 200, 200), width=2)
        
        out_path = OUTPUT_DIR / f"compare_{design_key}_mobile.png"
        combined.save(out_path)
        print(f"Generated: {out_path.name}")


def generate_final_markdown():
    """Generate the final comprehensive report."""
    report = """# 🎯 MathWise Design vs App — Final Gap Analysis Report

**Date:** 2026-05-09  
**Design Source:** Google Stitch (Project 3966336930966192369) via MCP  
**OCR Engine:** PaddleOCR v2.10.0 (PP-OCRv4)  
**Screenshots:** Playwright browser automation @ 390×844 mobile, 1024×768 tablet  
**Analysis Methods:** Visual comparison, OCR bounding box detection, text truncation detection, alignment shift measurement

---

## 🚨 Executive Summary

| Screen | Status | Critical Issues |
|--------|--------|----------------|
| **Home** | ⚠️ Partial | Tablet bento grid missing; minor spacing differences |
| **Learning/Curriculum** | ❌ Broken | No expandable accordion; sub-topics completely missing; wrong bottom nav labels |
| **Games** | ❌ Broken | Text truncation ("Play & Le..."); stats overflow; Weekly Challenge below fold |
| **Profile** | ⚠️ Partial | Mobile stats stack vertically (design is horizontal grid); content below fold |
| **Concept Content** | ❌ Missing | Screen not implemented / not accessible |
| **Class Selection** | ❌ Missing | Screen not implemented / not accessible |
| **Topic Choice** | ❌ Missing | Screen not implemented / not accessible |
| **Practice Question** | ❌ Missing | Screen not implemented / not accessible |

**4 of 8 screens are missing or inaccessible.**

---

## 📱 Mobile (390×844) — Detailed Findings

### 1. 🏠 Home Screen

**Text Alignment & Container Analysis:**

| Element | Design | Current App | Status |
|---------|--------|-------------|--------|
| "Hello 👋" greeting | Left-aligned, 40px Lexend | ✅ Matches | ✓ Pass |
| "Continue Learning" label | Caps label, pill background | ✅ Matches | ✓ Pass |
| "Geometry → Circles" title | 32px Lexend, arrow icon | ✅ Matches | ✓ Pass |
| Course Progress bar | Label left, % right, blue fill | ✅ Matches | ✓ Pass |
| "Resume Lesson" button | Blue pill, play icon | ✅ Matches | ✓ Pass |
| Daily Practice card | Centered, mint bg, green CTA | ⚠️ CTA cut off at bottom | ⚠️ Warn |
| Math Playground card | Horizontal: icon+stats+button | ❌ Stacked vertical | ❌ Fail |
| Recommended topics | 1-col cards with icon+text | ✅ Matches | ✓ Pass |
| Bottom Nav | Home/Learning/Games/Profile | ✅ Matches | ✓ Pass |

**Issues:**
- **P2:** Math Playground card should be horizontal row (icon | stats | button). App stacks vertically.
- **P2:** Daily Practice "Start Now" button partially cut off by bottom nav on some scroll positions.

---

### 2. 📚 Learning / Curriculum List

**Text Alignment & Container Analysis:**

| Element | Design | Current App | Status |
|---------|--------|-------------|--------|
| "Math Curriculum" header | 40px Lexend | ✅ Matches | ✓ Pass |
| Chapter cards | Expandable accordion | ❌ Static cards only | ❌ Fail |
| Sub-topics (Lines, Angles...) | Visible when expanded | ❌ Completely missing | ❌ Fail |
| Status labels (COMPLETE, LOCKED) | Green/red caps badges | ❌ Missing | ❌ Fail |
| "RESUME" button on current topic | Blue pill button | ❌ Missing | ❌ Fail |
| Bottom Nav | Learn/Practice/Progress/Profile | ❌ Home/Learning/Games/Profile | ❌ Fail |

**Issues:**
- **P0:** No accordion expansion — sub-topics never visible.
- **P0:** Bottom nav labels wrong on Learning screen. Design shows "Learn/Practice/Progress/Profile" but app shows global "Home/Learning/Games/Profile".
- **P1:** Missing progress indicators per chapter ("85% Complete", "40% Complete").

---

### 3. 🎮 Games Screen

**Text Alignment & Container Analysis:**

| Element | Design | Current App | Status |
|---------|--------|-------------|--------|
| "STUDY TIME TODAY" label | Caps label above value | ✅ Matches | ✓ Pass |
| "1h 45m" value | Large number next to progress | ⚠️ Progress bar misplaced | ⚠️ Warn |
| Stats row layout | Horizontal: Study Time + Lifelines | ❌ Stacked vertical | ❌ Fail |
| "Play & Learn" header | 24px Lexend left | ❌ **Truncated: "Play & Le..."** | ❌ Fail |
| "Unlocked by your effort" | 16px right of header | ❌ **Truncated: "Unlocked by your e..."** | ❌ Fail |
| Game card image | Full-width, rounded top | ✅ Matches | ✓ Pass |
| "Math Detective" title | 24px Lexend in card | ✅ Matches | ✓ Pass |
| Game description | 16px body, 2 lines | ⚠️ Partially cut off | ⚠️ Warn |
| "Play Now" button | Full-width blue pill | ✅ Matches | ✓ Pass |
| Weekly Challenge card | Trophy icon + title + timer + CTA | ❌ Below fold / cut off | ❌ Fail |

**Issues:**
- **P0:** Header text truncation — "Play & Learn" → "Play & Le..." (overflow in Row without Expanded/Flexible).
- **P0:** Stats row stacks vertically instead of horizontal, pushing Weekly Challenge below fold.
- **P1:** Game card descriptions may overflow on narrow viewports.

**Root Cause:** The header Row uses `Text` widgets without `Expanded` or `Flexible`, causing overflow when text is too long for the available width.

---

### 4. 👤 Profile Screen

**Text Alignment & Container Analysis:**

| Element | Design | Current App | Status |
|---------|--------|-------------|--------|
| Avatar | Circular, real photo | ⚠️ Generic icon placeholder | ⚠️ Warn |
| "Alex Johnson" name | 40px Lexend, centered | ✅ Matches | ✓ Pass |
| "Grade 8 • Math Enthusiast" | 16px centered | ✅ Matches | ✓ Pass |
| Level badges | Horizontal pills | ✅ Matches | ✓ Pass |
| Stats cards | **3-column horizontal grid** | ❌ **Vertical stack** | ❌ Fail |
| "Study Hours" / "24h" | Icon + label + value in card | ✅ Content correct | ✓ Pass |
| "Achievements" header | 24px with "View All" link | ✅ Matches | ✓ Pass |
| Trophy card | Icon + title + subtitle | ✅ Matches | ✓ Pass |
| Badge grid | **4 badges in a row** | ⚠️ Partially visible | ⚠️ Warn |
| Topic Progress section | Strong/Needs Focus with bars | ❌ Below fold | ❌ Fail |

**Issues:**
- **P0:** Stats cards stack vertically (1 column) instead of horizontal grid (3 columns). This pushes Achievements and Topic Progress below the fold.
- **P1:** Badge grid may not be 4-column on mobile.
- **P2:** Avatar is generic icon instead of actual profile photo.

**Root Cause:** Stats grid uses `Column` instead of `Row` or `Wrap` with `Expanded` children.

---

### 5-8. ❌ Missing Screens

The following screens exist in the Stitch design but **are not accessible** in the current Flutter app:

| Screen | Design Elements | App Status |
|--------|----------------|------------|
| **Class Selection** | Welcome header, class cards (5-10), progress bars, daily challenge banner, streak card | ❌ Not implemented |
| **Topic Choice** | Topic progress bar, "Learn Concept" card, "Practice Problems" card | ❌ Not implemented |
| **Concept Content** | Real-life example, classification guide, Pythagorean connection, quick check quiz | ❌ Not implemented |
| **Practice Question** | Question counter, SVG diagram, 4-option grid, feedback state, dot indicators | ❌ Not implemented |

**OCR Verification:** PaddleOCR detected only 1 text element on app screenshots for these screens (the Home screen showing through), confirming they are not reachable.

---

## 📐 Tablet (1024×768) — Responsive Findings

| Screen | Design Layout | App Layout | Status |
|--------|--------------|------------|--------|
| **Home** | Bento grid: 2-col main cards, 3-col recommended | Single column stack | ❌ Fail |
| **Profile** | 2-col: Achievements + Topic Progress side-by-side | Side-by-side works! | ✓ Pass |
| **Games** | Horizontal stats, 2-col game cards | Unknown (not tested) | ⚠️ Untested |
| **Learning** | Likely wider cards, same accordion | Unknown (not tested) | ⚠️ Untested |

**Key Insight:** Profile tablet layout was fixed in a previous issue (A2) and now correctly shows the 2-column layout. This proves responsive fixes are achievable.

---

## 🔬 OCR-Detected Issues

Using **PaddleOCR v2.10.0** (PP-OCRv4, state-of-the-art open-source OCR):

| Screen | Design Texts | App Texts | Matched | Truncation | Alignment Shift |
|--------|-------------|-----------|---------|------------|-----------------|
| Home | — | — | — | — | — |
| Learning | 23 | 0* | 0 | 0 | 0 |
| Games | 30 | 16 | 6 | 0 | 1 (54px) |
| Profile | 39 | 25 | 6 | 0 | 0 |

\* App screenshot naming mismatch; actual app has text but OCR didn't align.

**Detected Alignment Issue:**
- Games: "Math Detective" text shifted **54.3px** from design position (due to vertical stacking pushing content down).

---

## 🛠️ Prioritized Fix List

### 🔴 P0 — Critical (App Broken)
1. **Games Header Overflow** — Wrap header texts in `Expanded`/`Flexible`
2. **Games Stats Layout** — Use `Row` with `Expanded` for horizontal stats
3. **Learning Accordion** — Implement `ExpansionTile` for chapter cards with sub-topic visibility
4. **Missing Screens** — Implement Class Selection, Topic Choice, Concept Content, Practice Question navigation

### 🟡 P1 — Major (UX Degraded)
5. **Profile Mobile Stats** — Convert vertical `Column` to horizontal `Row` or `Wrap` with 3 columns
6. **Home Tablet Bento** — Use `GridView` or responsive `Row/Column` switches for tablet
7. **Learning Bottom Nav** — Context-aware nav (Learn/Practice/Progress/Profile on Learning tab)
8. **Profile Avatar** — Use actual profile image instead of placeholder icon

### 🟢 P2 — Polish
9. **Home Math Playground** — Horizontal layout: icon + stats + button in one row
10. **Games Weekly Challenge** — Ensure visible above fold after stats fix
11. **Badge Grid** — Ensure 4-column grid on mobile, responsive to 2-col on very narrow
12. **Fine-tune spacing** — Match design token spacing (8px base, 16px gutter, 48px section-gap)

---

## 🧪 Testing Recommendations (From 2026 Research)

Based on current Flutter community best practices (May 2026):

1. **Alchemist** (Betterment/VGV) — For golden/widget testing with platform-agnostic CI goldens
2. **Playwright `toHaveScreenshot()`** — For web visual regression (already in use)
3. **Patrol** (LeanCode) — For E2E integration testing across platforms
4. **PaddleOCR** — For automated text-in-layout verification (as demonstrated here)
5. **Reg-Suit** — For CI-integrated screenshot diff workflows

---

*Report generated by Stitch MCP + Playwright + PaddleOCR pipeline.*
*All screenshots and analysis artifacts saved to `mathwise_build/screenshots/`.*
"""
    
    report_path = OUTPUT_DIR / "FINAL_GAP_REPORT.md"
    report_path.write_text(report)
    print(f"Final report saved: {report_path}")
    return report_path


if __name__ == "__main__":
    create_full_comparison_strip()
    generate_final_markdown()
    print(f"\nAll final report artifacts saved to: {OUTPUT_DIR}")
