# Introspection / Self-Interview / Retrospect — Phase 10.7 Responsive Pass

**Date:** 2026-06-28  
**Scope:** Why the HomeScreen responsive pass became a full narrow-screen audit, and what first-principles changed the plan.

---

## 1. Initial assumptions (what I believed at the start)

1. Only `HomeScreen` had narrow-screen overflows (Course Progress row, Games card, bottom nav).
2. The existing visual-screenshot tests simulated real device viewports (375×812, 390×844, etc.).
3. A threshold of 360 dp was the right place to switch layouts because the issue title said "320–360 dp pass."
4. Bottom navigation should always show text labels because the existing widget cited Nielsen on discoverability.

## 2. What research revealed

### Flutter viewport testing
`TestFlutterView.physicalSize` is in **physical pixels**; logical dp = `physicalSize / devicePixelRatio` [^1]. The existing test set `physicalSize = Size(375, 812)` and `devicePixelRatio = 2.0`, so the layout was actually rendered at **187.5 × 406 dp**, not 375 × 812. This means:
- Some "passes" were passing at half the intended logical size.
- Some overflows I was chasing were artifacts of a misconfigured test, not real 360 dp devices.

### Material 3 bottom-navigation guidance
When a bottom nav has **four or five** destinations, inactive views can be shown as icons only [^2]. This directly resolves the bottom-nav crowding without reducing touch targets.

### Responsive first principles
- Layout decisions should be **constraint-driven** (can this content fit side-by-side in the available width?), not device-name-driven [^3].
- The project already encodes this in `ContentMinWidths.twoStatCardsSideBySide = 330` and `Breakpoints.medium = 600`. Those constants are a better basis for switches than an arbitrary 360 dp.

## 3. Self-interview

**Q: Should I fix the visual test even though it was not part of the original task?**  
A: Yes. A test that validates the wrong viewport size is worse than no test — it gives false confidence. Fixing it is a precondition for trusting any responsive work.

**Q: Does fixing the test force scope expansion?**  
A: It reveals overflows in `topic_choice`, `topics_subtopics`, `curriculum_grid`, `curriculum_list`, and `curriculum_stepper`. These are real constraints on 320–430 dp phones, not test artifacts.

**Q: Should I hide those overflows to stay within "Phase 10.7 HomeScreen only"?**  
A: No. If the corrected test exposes real rendering errors on the target devices, leaving them unaddressed would make the test fix destructive. The honest scope becomes: HomeScreen + the shared widgets and other screens that now fail under realistic viewport sizes.

**Q: What is the smallest principled change?**  
A: Reuse the existing `ContentMinWidths` constants for side-by-side thresholds, wrap long texts in `Expanded`/`Flexible`, and make the bottom nav follow Material 3 icon-only guidance for inactive items on phones.

## 4. Adjusted plan

1. Fix `test/visual_screenshots_test.dart` so logical viewport matches the named sizes.
2. Fix shared widgets:
   - `top_app_bar.dart`: title Row uses `MainAxisSize.min` to avoid forced expansion.
   - `bottom_nav_bar.dart`: inactive items show icon-only on compact widths.
3. Fix `HomeScreen` cards: Continue (progress row), Games (vertical compact layout), Nursing (vertical compact layout).
4. Fix surfaced overflows in other screens:
   - `topic_choice_screen.dart` header text.
   - `topics_subtopics_screen.dart` progress overview (stack cards when narrow).
   - `curriculum_grid_screen.dart` CTA cards and topic tiles.
   - `curriculum_list_screen.dart` row overflow.
   - `curriculum_stepper_screen.dart` row overflows.
5. Regenerate golden images with `--update-goldens`.
6. Run full `flutter test` and `flutter analyze`.
7. Update `STATE.md` and note the expanded scope.

## 5. Retrospect — what I would do differently next time

- Check the test harness **before** treating its failures as ground truth.
- Look at existing constants (`ContentMinWidths`, `Breakpoints`) before inventing new thresholds.
- Cite sources before committing to a layout rule; e.g., "labels always visible" sounds like good UX but conflicts with Material 3 for 4+ items.

---

## References

[^1]: Flutter API docs — `TestFlutterView.physicalSize` / `devicePixelRatio`; logical size = physical size / DPR. https://api.flutter.dev/flutter/flutter_test/TestFlutterView/physicalSize.html

[^2]: Material UI / Material Design 3 — Bottom Navigation: "If there are four or five actions, display inactive views as icons only." https://mui.com/material-ui/react-bottom-navigation/

[^3]: Flutter docs — "Use LayoutBuilder for constraint-based adaptation, not MediaQuery for device size." https://docs.flutter.dev/ui/adaptive-responsive/best-practices
