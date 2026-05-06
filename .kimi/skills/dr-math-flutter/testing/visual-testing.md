# Visual Testing — Dual-Persona Pipeline

## Overview

The Dr. Math Flutter app uses a **dual-persona visual testing pipeline** that evaluates all 11 screens across 5 viewport sizes (55 screenshots total). The pipeline produces per-screen markdown reports with pass/fail verdicts, severity ratings, citations, and remediation guidance.

## The Two Personas

| Persona | Responsibility | Technology |
|---------|---------------|------------|
| **Screenshot Auditor** | Pixel-level layout + design token validation | Python Pillow + `design_tokens.json` |
| **UI/UX Engineer** | Qualitative UX evaluation against ADR-010 rubric | Structured heuristics + (optional) LLM vision |

## Quick Start

```bash
cd mathwise_build

# Generate all 55 screenshots
flutter test --update-goldens test/visual_screenshots_test.dart

# Run the full pipeline (builds, captures, audits, evaluates, reports)
python3 scripts/visual_test_pipeline.py

# Or run individual steps:
python3 scripts/screenshot_auditor.py --screenshots screenshots/YYYY-MM-DD_HH-MM-SS/
python3 scripts/ux_evaluator.py --screenshots screenshots/YYYY-MM-DD_HH-MM-SS/
python3 scripts/report_builder.py --reports reports/YYYY-MM-DD_HH-MM-SS/
```

## Output Structure

```
reports/YYYY-MM-DD_HH-MM-SS/
├── summary.md              ← Executive summary with overall score
├── home/
│   ├── ux_report.md        ← UI/UX Engineer findings
│   └── audit_report.md     ← Screenshot Auditor findings
├── practice_question/
│   └── ...
└── ... (11 screen directories)
```

## Screenshot Capture

Screenshots are generated via widget test golden files:

- **Source:** `test/visual_screenshots_test.dart`
- **Method:** `flutter test --update-goldens`
- **Screens:** All 11 screens (home, class_selection, topic_choice, topics_subtopics, curriculum_grid, curriculum_list, curriculum_stepper, concept_content, practice_question, games, profile)
- **Viewports:** 375×812, 390×844, 430×932, 768×1024, 1024×768
- **Location:** `test/goldens/<screen>/<viewport>.png`

> **Note:** Uses system fallback fonts to avoid GoogleFonts network requests in test environment. Layout, color, and spacing evaluation remains fully accurate.

## Evaluation Rubric

### Screenshot Auditor Checks

| Category | What It Checks |
|----------|---------------|
| Color Tokens | Sampled pixels match `design_tokens.json` palette |
| Touch Targets | Bottom nav and interactive regions ≥ 48dp |
| Background | Uses correct surface color (#F8F9FF) |
| Contrast | Text-on-background contrast ratios (WCAG AA) |
| No Red Backgrounds | ADR-010 D4: soft pink errorContainer, not red |

### UI/UX Engineer Checks

| Category | Rule | Source |
|----------|------|--------|
| Cognitive Load | ≤ 7 visible information chunks | Miller 1956, Sweller 1988 |
| Color Psychology | Blue primary, no red backgrounds | Elliot & Maier 2014 |
| Touch Targets | All tappable ≥ 48dp | Parhi et al. 2006 |
| Navigation | Persistent visible bottom tabs | Nielsen 2016 |
| Accessibility | Color not sole feedback; text scales | WCAG 2.1 AA, CAST UDL 2018 |
| Pedagogy | Screen-specific ADR-010 D1–D10 compliance | ADR-010 |
| Responsiveness | No horizontal overflow | — |

## Design Tokens

Token manifest: `scripts/design_tokens.json`

Derived from:
- `lib/core/constants/app_colors.dart`
- `lib/core/constants/app_theme.dart`
- `lib/shared/theme/pedagogy_tokens.dart`

Regenerate if theme changes:
```bash
# Manual: update scripts/design_tokens.json to match Dart source
```

## Interpreting Results

### Overall Score

| Range | Interpretation |
|-------|---------------|
| 90–100 | Excellent: minor issues only |
| 70–89 | Good: some medium issues to address |
| 50–69 | Fair: significant UX or token violations |
| < 50 | Poor: critical accessibility or pedagogy failures |

### Severity Levels

| Emoji | Level | Action |
|-------|-------|--------|
| 🔴 | Critical | Block release. Fix immediately. |
| 🟠 | High | Address before next sprint. |
| 🟡 | Medium | Plan fix within 2 sprints. |
| 🔵 | Low | Nice-to-have improvement. |
| ℹ️ | Info | Awareness only. No action required. |

## Known Limitations

1. **Fonts:** Widget test screenshots use system fallback fonts, not Lexend/Plus Jakarta Sans. Typography family verification is limited.
2. **Cognitive Load:** The chunk estimator uses color region heuristics. It may over-count on screens with rich Material 3 color palettes. Manual review recommended for screens scoring < 60.
3. **Scrollable Content:** Screenshots capture the viewport only. Content below the fold is not evaluated.
4. **Animation:** Static screenshots cannot evaluate motion design or transition quality.
5. **Semantic Accessibility:** Screenshot analysis cannot verify screen reader labels or focus order. Use `accessibility_tools` widget tests for semantic validation.

## Research Backing

- ADR-011: Visual Testing Pipeline
- BFS-02: Visual Testing Landscape
- DFS-02: Visual Testing Deep-Dive
- Bidirectional-02: Cross-Domain Impact Analysis

## References

- Miller, G. A. (1956). The Magical Number Seven, Plus or Minus Two. *Psychological Review*, 63(2), 81–97.
- Sweller, J. (1988). Cognitive Load During Problem Solving. *Cognitive Science*, 12(2), 257–285.
- Elliot, A. J., & Maier, M. A. (2014). Color and Psychological Functioning. *Annual Review of Psychology*, 65, 95–120.
- Parhi, P., et al. (2006). Target Size Study for One-Handed Thumb Use. *MobileHCI'06*.
- Nielsen, J. (2016). Hamburger Menus and Hidden Navigation Hurt UX Metrics. Nielsen Norman Group.
- CAST (2018). Universal Design for Learning Guidelines version 2.2.
