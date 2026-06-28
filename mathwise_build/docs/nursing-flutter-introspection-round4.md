# Nursing Flutter Module — Round 4 Introspection, Self-Interview & Retrospect

**Date:** 2026-05-14  
**Scope:** Dig deeper into unknowns after wiring the remaining v1 screens in Phase 8.  
**Research covenant:** Unknowns were named, researched against first principles, and only then turned into plan changes.

---

## Part 1: Introspection — What Am I Still Hiding?

### Unknown 1: Are disclaimer and onboarding actually reachable?
The screens exist and have tests, but the main MathWise home screen navigates directly to `NursingHomeScreen()`. A first-time user never sees the disclaimer or onboarding. This makes the legal/educational disclaimer and the older-adult onboarding copy invisible in production.

### Unknown 2: Does the PDF screen use the topic selection?
The PDF screen lets users check/uncheck weak topics, but `_generate()` calls `exportPdf(widget.attempts)` with the full attempt list. The selected topics are ignored. This is a UX lie: the UI promises customization but the backend receives all attempts.

### Unknown 3: Is raw HTML useful on a phone?
The PDF preview renders the returned HTML string inside a `Text` widget. The user sees tags like `<html>`, `<body>`, `<h1>`, etc. For an adult learner studying on a smartphone, this is unusable. We need either HTML-to-text cleanup or proper HTML rendering.

### Unknown 4: Do we have any integration coverage?
We have 58 widget tests for individual screens, but no test exercises the full flow: entry → disclaimer → onboarding → home → subject → quiz → results → PDF. Widget tests miss navigation-stack interactions, process-death behavior, and cross-screen state.

### Unknown 5: Is the home-screen nursing card accessible?
The main `HomeScreen` tests fail with `RenderFlex overflowed by 53 pixels on the right` on the nursing card rows. This means the card does not fit small phone widths. A user with a budget smartphone may see clipped text or a broken layout before they ever reach nursing.

### Unknown 6: Should we add a new dependency for HTML rendering?
`flutter_html` and `flutter_widget_from_html_core` are popular, but AGENTS.md forbids adding dependencies without TCO analysis. We need to decide whether the benefit outweighs the cost, or whether a zero-dependency HTML-to-text stripper is enough.

### Unknown 7: Is `LanguageToggle` sharing the same storage instance?
`NursingSettingsScreen` can be injected with a `storage` instance, but `LanguageToggle` creates its own `NursingStorageService()`. Because `SharedPreferences` is a singleton-backed global, values sync, but the architectural inconsistency is a seam that could bite us if we ever replace SharedPreferences.

### Unknown 8: What is the right entry point for the nursing module?
We need a single screen that checks `disclaimerAccepted` and `onboardingSeen` and routes to the correct next screen. Without it, the main app has to know the internal routing rules of the nursing module.

---

## Part 2: Self-Interview

**Q: Why did I build onboarding/disclaimer screens without wiring them into the main flow?**
A: I followed the completion plan's file list, which listed the screens as separate items. I treated them as components rather than as a gated entry flow. The lesson: a screen that is never reached is dead code, no matter how well tested.

**Q: Is it acceptable to leave the PDF topic selection ignored?**
A: No. It violates the user's expectation and wastes backend compute. Either remove the selection UI or actually filter attempts by selected topics. Filtering is more useful.

**Q: Should we render HTML properly or strip it?**
A: The backend returns HTML because the web module uses it. On mobile, a plain-text study sheet is more useful than raw HTML tags. Stripping tags to readable text (with line breaks preserved) is the minimum viable fix and adds no dependency. Full HTML rendering can be deferred until we have images/tables that require it.

**Q: Do we need integration tests now?**
A: Widget tests give us confidence at the screen level, but the nursing module is a cross-screen user journey. At least one integration test for the happy path (entry → home → quiz → results) is worth the cost. It will catch navigation and service-lifetime issues that widget tests miss.

**Q: Should we fix the home screen nursing card overflow even though it's in `features/home`?**
A: Yes. The nursing card is the gateway to the module. If it overflows on small screens, users cannot reliably tap "Open". Fixing it is a nursing-adjacent accessibility fix, not a generic home-screen refactor.

**Q: Is adding `flutter_html` justified?**
A: Not for v1. The PDF preview is a secondary feature. The backend HTML is simple (`<h1>`, `<p>`, `<ul>`). A zero-dependency stripper is sufficient, keeps APK size down, and avoids a transitive dependency with native code. Defer `flutter_html` to v1.5 if we need rich rendering.

**Q: What about the `LanguageToggle` storage inconsistency?**
A: Accept it for v1 because SharedPreferences is effectively a global. Document it as technical debt. In v2, when we move to a scoped DI framework, the toggle should receive storage from its parent.

---

## Part 3: Research Findings

### 3.1 Testing pyramid for Flutter
Flutter teams commonly run 60-70% widget tests because they are fast and expressive, but integration tests are required for full-app flows and platform-channel behavior [^1][^2]. The recommendation is many fast tests at the base, fewer integration tests at the top [^1][^2]. Widget tests cannot catch navigation-stack or process-death regressions that span multiple screens.

### 3.2 Rendering HTML in Flutter
Flutter has no built-in HTML renderer. Options:
- `flutter_html` / `flutter_widget_from_html_core`: native widget rendering, but adds dependencies and potential native code [^3][^4].
- WebView: heavy, high RAM, isolated from Flutter [^3].
- Strip tags to plain text: zero dependency, sufficient for simple HTML [^3].

For read-only, simple HTML, stripping tags is the lowest-risk choice for v1.

### 3.3 Onboarding best practices for adult / older-adult learners
- Keep onboarding to 3–5 screens, total time under 30 seconds [^5][^6].
- Always provide a skip option [^5][^6].
- Focus on value to the user, not feature lists [^5][^6].
- For older adults: favor video tutorials, step-by-step contextual help, simple navigation, large fonts, and clear exits [^7].

Our current 3-screen onboarding with skip matches these guidelines, but it needs to be reachable to matter.

### 3.4 Offline-first mutation patterns
Offline-first apps store user intents in a queue and execute them when connectivity returns [^8][^9]. The UI should not need to know about the queue directly; the mutation layer decides whether to execute or enqueue [^9]. Our pending-analysis queue follows this pattern for analysis; PDF generation should similarly queue if offline.

---

## Part 4: Decisions and Plan Changes

### Decision 1: Create `NursingEntryScreen` as the module gateway
A single entry screen checks `disclaimerAccepted` and `onboardingSeen` and routes to the appropriate screen. The main MathWise home screen will navigate to `NursingEntryScreen()` instead of `NursingHomeScreen()`.

### Decision 2: Filter PDF attempts by selected topics
`NursingPdfScreen._generate()` will pass only attempts whose `topicId` is in `_selectedTopics`. If no topics are selected, disable the Generate button (already done). This makes the UI honest.

### Decision 3: Strip HTML tags for PDF preview
Use a simple helper to convert the backend HTML string to readable plain text for the preview. No new dependency. Keep the "Copy HTML" button for users who want the raw HTML.

### Decision 4: Add an integration test for the core nursing flow
Create `integration_test/nursing_flow_test.dart` that exercises entry → disclaimer → onboarding → home → subject → quiz → results. This is the smallest integration test that validates cross-screen navigation.

### Decision 5: Add accessibility tap-target tests for new screens
Ensure disclaimer, onboarding, settings, and PDF interactive elements meet Android/iOS tap-target guidelines.

### Decision 6: Fix the nursing card overflow in `HomeScreen`
Refactor `_buildNursingCard` to avoid fixed-width text rows that overflow on narrow screens. Use `Expanded`/`Flexible` or a `Column` layout.

### Decision 7: Queue PDF generation when offline
If `exportPdf` fails with `isOffline`, show a snackbar and queue the request for later sync. For v1, a simple "You are offline; PDF will be available when you reconnect" message is sufficient.

---

## Part 5: Updated Immediate Tasks

1. Create `NursingEntryScreen` and wire it from `HomeScreen`.
2. Filter attempts by selected topics in `NursingPdfScreen`.
3. Add HTML-to-text helper and use it in PDF preview.
4. Add offline handling for PDF generation.
5. Add integration test for core nursing flow.
6. Add tap-target tests for disclaimer, onboarding, settings, and PDF screens.
7. Fix nursing card overflow in `HomeScreen`.
8. Run all gates and commit.

---

## References

[^1]: SUSATEST. *Test Automation for Flutter Apps (2026)*. https://www.susatest.com/blog/test-automation-for-flutter  
[^2]: TestGuild. *Testing Flutter Apps in 2026: A Real-World Guide*. https://testguild.com/testing-flutter-apps/  
[^3]: Kindacode. *How to render HTML content in Flutter*. https://www.kindacode.com/article/how-to-render-html-content-in-flutter/  
[^4]: Flutter Gems. *Top Flutter HTML, CSS, SASS packages*. https://fluttergems.dev/html-css/  
[^5]: Scalebay. *Mobile App Onboarding That Converts*. https://www.scalebay.io/blog/improve-user-retention-and-monetization-with-high-performing-mobile-app-onboarding  
[^6]: Scandiweb. *User Onboarding Best Practices: 9 That Work in 2026*. https://scandiweb.com/blog/user-onboarding-best-practices/  
[^7]: Gómez-Hernández, M., et al. (2023). Design Guidelines of Mobile Apps for Older Adults. *JMIR mHealth and uHealth*. https://pmc.ncbi.nlm.nih.gov/articles/PMC10557006/  
[^8]: Locize. *Offline-First Apps: Architecture, Frameworks & Real Examples*. https://www.locize.com/blog/offline-first-apps  
[^9]: Tomasz Gil. *Offline Support in Web Apps: Foreground Queue for Offline Mutations*. https://blog.tomaszgil.me/offline-support-in-web-apps-foreground-queue-for-offline-mutations-part-5
