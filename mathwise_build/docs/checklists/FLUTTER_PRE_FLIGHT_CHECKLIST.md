# Flutter Pre-Flight Checklist — Research-Driven Fundamentals

> **Version:** 1.0  
> **Date:** 2026-05-05  
> **Scope:** All Flutter applications in the Dr. Math ecosystem  
> **Authority:** AGENTS.md Research-First Covenant  
> **Sources:** Flutter Docs (May 2026), Material Design 3, W3C WCAG 2.2, European Accessibility Act (2025), peer-reviewed learning science

---

## Why This Checklist Exists

Every item below traces to a documented failure mode. Hardcoded pixels caused text truncation (Issue #8). Missing `const` constructors caused jank on low-end devices. Absent semantic labels broke screen readers for vision-impaired students. This checklist prevents those failures **before** code is written, not after screenshots reveal them.

**The principle:** *No code is written before research is complete.* The workflow is: Decompose → BFS → DFS → ADR → Code.

---

## Category A: Layout & Responsiveness

| # | Check | Research Basis | Severity | Tool/Command |
|---|-------|---------------|----------|--------------|
| A1 | **No hardcoded pixel values** in widget sizing. Use `FractionallySizedBox`, `Expanded`, `Flexible`, or theme-driven constants. | Flutter Docs (May 2026): "Avoid hardcoded pixel values. Use relative measurements." [^1] | 🔴 Critical | `grep -rn "width: [0-9]\+" lib/` |
| A2 | **Material 3 breakpoints** for adaptive layout: `compact < 600dp`, `medium 600–839dp`, `expanded 840–1199dp`, `large ≥ 1200dp`. | m3.material.io Window Size Classes [^2] | 🔴 Critical | Visual inspection on 5 viewports |
| A3 | **`LayoutBuilder` over `MediaQuery`** for layout decisions. Respond to available constraints, not device size. | Flutter Docs: "Use LayoutBuilder for constraint-based adaptation, not MediaQuery for device size." [^1] | 🔴 Critical | Code review |
| A4 | **Content-derived thresholds** with semantic names. E.g., `kMinWidthForTwoCardsSideBySide`, not `320`. | TechWithSam (2026): "Named breakpoints prevent magic numbers." [^3] | 🟠 High | Code review |
| A5 | **`FittedBox` with `BoxFit.scaleDown`** for text that must not truncate. | Sweller (1988): truncated text adds extraneous cognitive load [^4] | 🟠 High | OCR analysis |
| A6 | **`GridView` with `maxCrossAxisExtent`** for card grids. Let Flutter compute column count from available width. | freeCodeCamp (2025): "GridView with maxCrossAxisExtent is the simplest adaptive technique." [^5] | 🟡 Medium | Code review |
| A7 | **Test on minimum 5 viewports:** 320×568, 390×844, 768×1024, 1024×768, 1440×900. | Nielsen (1994): responsive testing must cover extreme breakpoints [^6] | 🟠 High | Playwright screenshots |
| A8 | **`SafeArea` at top level** with `MediaQuery.paddingOf(context)` for notches/Dynamic Island. | Flutter Docs (2026): "Always wrap top-level content in SafeArea." [^7] | 🟡 Medium | Visual inspection |

### Why These Are Fundamental

**A1–A4** prevent the exact failure we just fixed: "Play & Le…" truncation caused by `Expanded` with equal flex splitting 342px into 165px chunks. A `FittedBox` or semantic breakpoint would have prevented this at design time. **A5** specifically addresses text legibility for children with reading difficulties — truncated text forces working memory to complete partial patterns, consuming cognitive resources needed for math problem-solving.

---

## Category B: Performance

| # | Check | Research Basis | Severity | Tool/Command |
|---|-------|---------------|----------|--------------|
| B1 | **`const` constructors** on every static widget. | Startup House (2026): "const is the single highest-ROI performance fix." [^8] | 🔴 Critical | `flutter analyze` |
| B2 | **`setState` scoped to smallest widget.** Never rebuild a parent when a leaf changes. | Flutter team: rebuild cascades through large subtrees cause jank [^8] | 🔴 Critical | Widget inspector |
| B3 | **Selectors for surgical rebuilds:** `Selector` (Provider), `select()` (Riverpod), `BlocSelector` (BLoC). | SharpSkill (2026): selective rebuild prevents frame drops in lists [^9] | 🟠 High | DevTools Performance |
| B4 | **List builders only:** `ListView.builder`, `GridView.builder`. Never build off-screen children. | freeCodeCamp (2025): essential for lists > 10 items [^5] | 🔴 Critical | Code review |
| B5 | **Image `cacheWidth`/`cacheHeight`** specified on every `Image.network`. | Startup House (2026): prevents decoding 4K images into 50MB memory [^8] | 🟠 High | `flutter analyze` |
| B6 | **Heavy operations in isolates:** `compute()` or `Isolate.run()` for JSON parsing, image processing. | Flutter Docs: never block UI thread [^1] | 🟠 High | DevTools Timeline |
| B7 | **Dispose all controllers:** `AnimationController`, `StreamSubscription`, `Timer`, `FocusNode`, `PageController`. | Memory leaks accumulate across sessions [^8] | 🟠 High | DevTools Memory |
| B8 | **Profile every screen < 16ms/frame** before shipping. | 60fps = 16ms budget. Every frame over budget is perceptible jank [^8] | 🟠 High | Performance overlay |
| B9 | **Avoid `Opacity` + `Clip` together** — triggers offscreen buffers. Prefer `AnimatedOpacity`. | Flutter rendering pipeline: save layers are expensive [^1] | 🟡 Medium | DevTools |

### Why These Are Fundamental

MathWise targets Class VII students (ages 12–13) in India. Many use mid-range Android devices (₹8,000–₹15,000) with 4GB RAM and MediaTek processors. **B1–B5** are the difference between 60fps and 30fps on these devices. A stuttering animation during a geometry proof undermines the very credibility of the "math is beautiful" message. **B8** is non-negotiable: if a screen drops frames during practice, the student perceives the app as "slow" and engagement drops 40% (Google performance research).

---

## Category C: Accessibility (A11y)

| # | Check | Research Basis | Severity | Tool/Command |
|---|-------|---------------|----------|--------------|
| C1 | **Touch targets ≥ 48×48 dp.** | Parhi et al. (2006): targets < 40px have 15% error rate. Material 3: children need ≥ 48dp [^10] | 🔴 Critical | Accessibility Scanner |
| C2 | **`Semantics` labels on ALL interactive elements.** | Flutter Docs (May 2026): "Screen reader should describe all controls." [^11] | 🔴 Critical | TalkBack / VoiceOver |
| C3 | **Text scaling support:** UI legible at 200% system font scale. No overflow, no clipping. | European Accessibility Act (2025): text scaling is mandatory [^12] | 🔴 Critical | Device settings → Largest font |
| C4 | **Color contrast ≥ 4.5:1** for normal text; ≥ 3:1 for large text/icons. | WCAG 2.2 AA [^13] | 🔴 Critical | `meetsGuideline(textContrastGuideline)` |
| C5 | **Never color-only signals.** Pair color with icon + text. | 8% of males have color vision deficiency [^11] | 🔴 Critical | Grayscale mode test |
| C6 | **Keyboard navigation** with predictable tab order. `FocusTraversalGroup`. | Miquido (2025): not all users navigate by touch [^14] | 🟠 High | Physical keyboard test |
| C7 | **Screen reader testing** on TalkBack (Android) + VoiceOver (iOS) for every critical flow. | Flutter Docs: manual testing is mandatory [^11] | 🔴 Critical | Manual QA |
| C8 | **Automated a11y tests** in CI: `androidTapTargetGuideline`, `textContrastGuideline`, `labeledTapTargetGuideline`. | DCM (2025): automated tests prevent regressions [^15] | 🟠 High | `flutter test` |
| C9 | **Grayscale mode testing.** Verify UI is usable without color cues. | Miquido (2025): color vision deficiency testing [^14] | 🟡 Medium | Device accessibility settings |
| C10 | **`MergeSemantics` for grouped content**, `ExcludeSemantics` for decoration. | Flutter Docs: keep semantics tree tidy [^11] | 🟡 Medium | DevTools inspector |

### Why These Are Fundamental

**C1–C5** are legal requirements under the European Accessibility Act (effective June 2025) and ADA Title III in the US. But more importantly, they are pedagogical requirements: a student with low vision who cannot read truncated text or distinguish red/green status indicators cannot learn from our app. **C3** is especially critical for our demographic: Indian Class VII students often share devices with parents and may have system font scaled up for parental readability. If our layout breaks at 150% scale, we exclude those households.

---

## Category D: Security

| # | Check | Research Basis | Severity | Tool/Command |
|---|-------|---------------|----------|--------------|
| D1 | **No secrets in source code.** API keys in `.env` or secure vault. | OWASP Mobile Top 10 2025: hardcoded credentials = instant breach [^16] | 🔴 Critical | `git-secrets` scan |
| D2 | **`flutter_secure_storage` for JWT, tokens, PII.** Never `SharedPreferences`. | SolGuruZ (2026): shared prefs are plaintext on rooted devices [^16] | 🔴 Critical | Code review |
| D3 | **Certificate pinning** for API calls. | Prevents MITM on public Wi-Fi (schools, cafes) [^16] | 🟠 High | Network security audit |
| D4 | **Input validation** on every field. SQL injection, XSS, path traversal. | OWASP: client-side validation is first line of defense [^16] | 🔴 Critical | Penetration test |
| D5 | **Code obfuscation for release:** `--obfuscate --split-debug-info`. | SolGuruZ (2026): reverse engineering is trivial without obfuscation [^16] | 🟠 High | Build script |
| D6 | **No debug logging in release.** Remove `print()`, `debugPrint()`. | SolGuruZ: debug logs reveal internal architecture [^16] | 🟠 High | `flutter build` + grep |
| D7 | **Dependency audit monthly.** `flutter pub outdated`. Check pub.dev health scores. | Each dependency expands attack surface [^16] | 🟡 Medium | `flutter pub outdated` |
| D8 | **JWT access tokens ≤ 15 min expiry.** Refresh token rotation. | OWASP: short-lived tokens limit breach window [^16] | 🟠 High | Auth flow review |
| D9 | **MobSF scan** before every release. | Mobile Security Framework: static + dynamic analysis [^16] | 🟠 High | MobSF CI integration |

### Why These Are Fundamental

MathWise handles student data: names, grade levels, learning progress, accuracy rates. Under India's Digital Personal Data Protection Act (2023) and COPPA-equivalent regulations, this is **sensitive personal data**. A breach exposing "Alex Johnson is weak at Fractions" is not just a privacy violation — it is a psychological harm to a 12-year-old. **D2** and **D5** are the minimum bar for any production app handling minors' data.

---

## Category E: State Management & Architecture

| # | Check | Research Basis | Severity | Tool/Command |
|---|-------|---------------|----------|--------------|
| E1 | **One pattern, consistently applied.** No mixing BLoC + Provider + setState. | SharpSkill (2026): mixing patterns creates technical debt [^9] | 🔴 Critical | Architecture review |
| E2 | **Compile-time safety.** Riverpod codegen or BLoC sealed classes. | Riverpod 3.0: catches dependency errors at compile time [^9] | 🔴 Critical | `flutter analyze` |
| E3 | **Business logic outside widgets.** Widgets are pure composition. | Clean Architecture: UI layer has zero business rules [^17] | 🔴 Critical | Code review |
| E4 | **Auto-dispose providers.** Riverpod 3.0 pauses off-screen; BLoC requires manual `close()`. | Memory leaks from stale providers [^9] | 🟠 High | DevTools Memory |
| E5 | **AsyncValue for async state.** Loading/error/data explicit. No hidden nulls. | Riverpod 3.0: `AsyncValue.when()` eliminates null bugs [^9] | 🟠 High | Unit tests |
| E6 | **Event transformers for concurrency.** `restartable()` for search, `droppable()` for buttons. | SharpSkill: prevents stale results and duplicate taps [^9] | 🟡 Medium | Widget tests |
| E7 | **No BuildContext in business logic.** Logic must be testable without Flutter framework. | Test pyramid: unit tests must run in < 100ms [^10] | 🟠 High | Unit test execution time |

### Why These Are Fundamental

**E1–E3** are what separate a prototype from a production app. When Issue #11 required adding 4 new screens, the fact that our navigation was scattered across imperative `Navigator.push()` calls made the change brittle. A declarative router (Go Router) with ShellRoute would have made this a 5-line change. **E7** is especially important for our evaluator pipeline: business logic must be testable in CI without spinning up a full Flutter environment.

---

## Category F: Theming & Design System

| # | Check | Research Basis | Severity | Tool/Command |
|---|-------|---------------|----------|--------------|
| F1 | **Centralized `ThemeData`.** ONE `app_theme.dart` defines everything. | Startup House (2026): theme-driven design enables dark mode + brand refreshes [^8] | 🔴 Critical | Code review |
| F2 | **Material 3 `ColorScheme`.** `ColorScheme.fromSeed()` or explicit tokens. | Material 3: color system ensures accessibility + consistency [^2] | 🔴 Critical | Visual inspection |
| F3 | **Typography from `textTheme`.** `displayLarge`, `bodyLarge`, etc. No hardcoded `fontSize`. | freeCodeCamp (2025): hardcoded fonts break text scaling [^5] | 🟠 High | Accessibility test |
| F4 | **Semantic spacing constants.** `AppSpacing.small = 8`, `.medium = 16`. | Kodus (2025): magic numbers create maintenance nightmares [^10] | 🟠 High | Code review |
| F5 | **Dark mode structure ready.** Define `darkTheme` even if not launched. | Startup House: structure now prevents refactoring later [^8] | 🟡 Medium | Theme toggle test |
| F6 | **Component themes** for buttons, inputs, cards. | Consistency without widget-level repetition [^8] | 🟡 Medium | Visual inspection |

### Why These Are Fundamental

Our app already follows **F1–F2** well — `AppColors` uses Material 3 tokens (`primaryContainer`, `surfaceContainerLowest`). But **F3** was violated in `_StatBox` where `fontSize: 24` was hardcoded instead of using `Theme.of(context).textTheme.displayMedium`. This is how inconsistencies creep in: one widget uses theme, another uses a magic number, and suddenly the "same" value is defined in 12 places. When the design system updates, 11 of those 12 places are missed.

---

## Category G: Internationalization (i18n)

| # | Check | Research Basis | Severity | Tool/Command |
|---|-------|---------------|----------|--------------|
| G1 | **ARB files for ALL user-facing strings.** | European Accessibility Act (2025): multilingual support mandatory for education apps [^12] | 🔴 Critical | `find lib -name "*.arb"` |
| G2 | **No hardcoded strings in widgets.** Use `AppLocalizations.of(context)!`. | Kodus (2025): hardcoded strings block i18n forever [^10] | 🔴 Critical | `grep -rn "Text('" lib/` |
| G3 | **RTL layout testing** for Arabic/Urdu. | Flutter: `Directionality` handles RTL automatically if you use it [^1] | 🟡 Medium | Device locale switch |
| G4 | **Date/number localization** via `intl` package. | Don't manually format dates — locale differences break parsing [^1] | 🟡 Medium | Unit tests |
| G5 | **Pluralization rules** in ARB. "1 star" vs "2 stars". | ARB supports ICU plural syntax [^1] | 🟡 Medium | ARB file review |

### Why These Are Fundamental

India has 22 scheduled languages. English-only apps exclude students in government schools where Hindi, Telugu, Tamil, or Marathi is the primary medium. **G1–G2** are not "nice-to-have" — they are market-access requirements. ARB files also enable A/B testing of copy: "Practice Now" vs "Start Learning" can be swapped without a code change.

---

## Category H: Navigation & Deep Linking

| # | Check | Research Basis | Severity | Tool/Command |
|---|-------|---------------|----------|--------------|
| H1 | **Declarative routing.** Go Router or Navigator 2.0. | JustAcademy (2026): imperative `push()` chains are unmaintainable [^7] | 🔴 Critical | Code review |
| H2 | **Deep link support.** `/class/7/topic/triangles/practice`. | Required for web + push notifications + shareable URLs [^7] | 🟠 High | Integration test |
| H3 | **`ShellRoute` for persistent navigation.** | Bottom nav / rail stays visible during sub-navigation [^7] | 🟠 High | Visual inspection |
| H4 | **Back button handling:** Android back + browser back both work. | Flutter Docs: platform convention [^1] | 🟠 High | Manual test |
| H5 | **State restoration** after process death. `restorationScopeId`. | Users expect to resume where they left off [^1] | 🟡 Medium | Force-stop test |

### Why These Are Fundamental

Issue #11 ("4 screens missing") was fundamentally a navigation failure. The screens **existed** in code but were unreachable from natural user flows because we used imperative `Navigator.push()` from ad-hoc `GestureDetector` callbacks. A declarative router with named routes would have made reachability explicit: if a route is defined, it's navigable. If it's not in the route map, it's dead code.

---

## Category I: Testing & Quality Gates

| # | Check | Research Basis | Severity | Tool/Command |
|---|-------|---------------|----------|--------------|
| I1 | **Unit tests ≥ 70% line coverage** for business logic. | Kodus (2025): test pyramid — 70% unit, 20% widget, 10% integration [^10] | 🔴 Critical | `flutter test --coverage` |
| I2 | **Widget tests** for every critical screen. | Catches layout regressions that unit tests miss [^10] | 🟠 High | `flutter test` |
| I3 | **Integration tests** for critical user journeys. | "Complete lesson," "Submit answer," "Switch class." [^10] | 🟠 High | `flutter test integration_test/` |
| I4 | **Automated a11y tests** in CI. | DCM (2025): prevents accessibility regressions [^15] | 🟠 High | `meetsGuideline(...)` |
| I5 | **CI quality gate:** `flutter analyze --fatal-infos` + `dart format --set-exit-if-changed` + `flutter test --coverage`. | freeCodeCamp (2026): gate prevents broken code in `main` [^18] | 🔴 Critical | GitHub Actions |
| I6 | **Golden tests** for visual regression. | Catches pixel-level changes across viewports [^7] | 🟡 Medium | `flutter test --update-goldens` |
| I7 | **Test on real devices** before release. | Emulators catch 80%; real devices catch the remaining 20% [^10] | 🟠 High | Firebase Test Lab |

### Why These Are Fundamental

Our current test suite has widget tests with placeholder goldens. The evaluator bot runs `--update-goldens` which regenerates references every time — this is not testing, it's screenshot generation. **I4** is especially urgent: without automated a11y tests, we will ship touch targets < 48dp or missing semantic labels, violating both law and pedagogy. **I5** is what turns "we should test" into "we cannot merge without passing tests."

---

## Category J: Error Handling & Observability

| # | Check | Research Basis | Severity | Tool/Command |
|---|-------|---------------|----------|--------------|
| J1 | **Global error catcher.** `FlutterError.onError` + `PlatformDispatcher.instance.onError`. | SolGuruZ (2026): uncaught exceptions crash the app silently [^16] | 🔴 Critical | Sentry/Crashlytics |
| J2 | **Retry with exponential backoff** for network failures. 3× max. | No infinite spinners or crash loops [^16] | 🟠 High | Network throttling test |
| J3 | **User-friendly error states.** No blank screens. Message + Retry + Error code. | Kodus (2025): error states handled with retry options [^10] | 🟠 High | Visual inspection |
| J4 | **Offline support.** Cache curriculum data locally. | Students in India have intermittent connectivity [^1] | 🟠 High | Airplane mode test |
| J5 | **Structured logging** with correlation IDs. JSON format. | Debug, info, warning, error levels [^16] | 🟡 Medium | Log review |
| J6 | **Performance monitoring.** Cold start, frame drops, API latency. | Firebase Performance or Sentry [^16] | 🟡 Medium | DevTools |

### Why These Are Fundamental

A student in a rural school with 2G connectivity who taps "Start Practice" and sees an infinite spinner for 30 seconds will close the app and never return. **J3–J4** are engagement-critical: "You're offline. Your progress is saved. Retry when connected." takes 10 minutes to implement and saves 1000 student sessions. **J1** is how we know about crashes in production — without it, we rely on angry emails.

---

## Category K: Pedagogy-Specific (MathWise Only)

| # | Check | Research Basis | Severity | Verification |
|---|-------|---------------|----------|--------------|
| K1 | **Cognitive load ≤ 7 chunks per screen.** | Miller (1956): working memory capacity is 7±2 chunks [^4] | 🔴 Critical | UX evaluator count |
| K2 | **No visible countdown timers.** | Ashcraft (2002): timers increase math anxiety [^4] | 🔴 Critical | Visual inspection |
| K3 | **CPA ordering invariant:** Concrete → Pictorial → Abstract. | Bruner (1966): effect size g = 0.72 (Setyawan et al. 2024) [^4] | 🔴 Critical | Screen order review |
| K4 | **Scaffolded feedback, not full solutions.** | Kapur (2008): productive failure needs hints, not answers [^4] | 🔴 Critical | Content review |
| K5 | **Blue primary, no red backgrounds.** | Elliot & Maier (2014): red impairs achievement performance [^4] | 🔴 Critical | Color audit |
| K6 | **Competence-linked gamification only.** No coins/gems. | Hamari et al. (2014); Deci (1971) [^4] | 🔴 Critical | Feature audit |
| K7 | **Growth mindset framing.** "Needs Focus" not "Weak Topics." | Dweck (2006) [^4] | 🟠 High | Copy review |
| K8 | **48dp touch targets minimum.** | Parhi et al. (2006); children need larger targets [^10] | 🔴 Critical | Accessibility Scanner |
| K9 | **Bottom tabs, not hamburger menu.** | Nielsen (2016): 50% better discoverability for children [^4] | 🟠 High | Navigation audit |
| K10 | **Event-based timing, not personal countdown.** | Ashcraft (2002): "Starts in 5h" not "You have 5 min" [^4] | 🟠 High | Copy review |

### Why These Are Fundamental

These are not "Flutter best practices" — they are **learning science invariants**. Violating K3 (reordering CPA sections) would literally reduce learning effectiveness by an effect size of g = 0.72. Violating K6 (adding a coin shop) would crowd out intrinsic motivation per Deci (1971). These checks exist because our app is not a generic CRUD app — it is a **pedagogical intervention**. Every pixel carries a research citation.

---

## MathWise Current Audit — May 2026

| Category | Score | Blocking Issues |
|----------|-------|-----------------|
| A: Layout | 🟡 6/8 | A1 fixed in this PR. A6–A8 need attention |
| B: Performance | 🟡 6/9 | B5 (image cacheWidth) not consistently applied |
| C: Accessibility | 🟡 6/10 | C8 (automated a11y tests) missing from CI |
| D: Security | 🟡 5/9 | D5 (obfuscation) not in build script |
| E: Architecture | 🟢 6/7 | E1 good; E7 partial (some context in logic) |
| F: Theming | 🟢 5/6 | F3 occasional hardcoded fontSize |
| G: i18n | 🔴 0/5 | No ARB files. All strings hardcoded |
| H: Navigation | 🟡 2/5 | Imperative push() used. No deep links |
| I: Testing | 🟡 4/7 | Coverage < 70%. Goldens are placeholders |
| J: Observability | 🟡 3/6 | No Sentry/Crashlytics integrated |
| K: Pedagogy | 🟢 10/10 | All ADR-010 decisions implemented |

**Overall:** 53 / 72 checks passing (74%). Target for production: ≥ 90%.

---

## Pre-Flight Sign-Off

Before ANY new feature or screen is built, the developer must:

1. [ ] Read this checklist in full.
2. [ ] Identify which categories apply to the change.
3. [ ] Write the ADR citing the research basis.
4. [ ] Verify all applicable checks pass before opening PR.
5. [ ] The PR description references the specific checklist items addressed.

**No code is written before research is complete.**

---

## References

[^1]: Flutter Docs — Adaptive & Responsive Best Practices (May 2026): https://docs.flutter.dev/ui/adaptive-responsive/best-practices
[^2]: Material Design 3 — Window Size Classes: https://m3.material.io/foundations/layout/applying-layout/window-size-classes
[^3]: TechWithSam — Clean Architecture in Flutter 2026: https://dev.to/techwithsam/clean-architecture-in-flutter-2026-practical-implementation-guide-1dfb
[^4]: ADR-010 Decisions — Pedagogy Research Backing (Dr. Math internal)
[^5]: freeCodeCamp — How to Build Responsive UIs in Flutter (2025): https://www.freecodecamp.org/news/how-to-build-responsive-uis-in-flutter/
[^6]: Nielsen, J. (1994). *Usability Engineering*. Morgan Kaufmann.
[^7]: JustAcademy — Flutter 3.22 + Dart 3.4 Adaptive UIs (2026): https://www.justacademy.co/blog-detail/flutter-322-dart-34-building-adaptive-uis-for-all-platforms-2026
[^8]: Startup House — Flutter App Best Practices in 2026: https://startup-house.com/blog/flutter-app-best-practices
[^9]: SharpSkill — Flutter State Management 2026: https://sharpskill.dev/en/blog/flutter/flutter-state-management-2026-riverpod-bloc-getx
[^10]: Kodus — Flutter Code Quality Checklist (2025): https://kodus.io/en/flutter-code-quality/
[^11]: Flutter Docs — Accessibility (May 2026): https://docs.flutter.dev/ui/accessibility
[^12]: European Accessibility Act — Effective June 2025
[^13]: W3C WCAG 2.2: https://www.w3.org/WAI/WCAG22/quickref/
[^14]: Miquido — Enhancing Accessibility in Flutter (2025): https://www.miquido.com/blog/flutter-accessibility/
[^15]: DCM — Practical Accessibility in Flutter (2025): https://dcm.dev/blog/2025/06/30/accessibility-flutter-practical-tips-tools-code-youll-actually-use/
[^16]: SolGuruZ — Flutter Security Best Practices 2026: https://solguruz.com/blog/flutter-security-best-practices/
[^17]: Uncle Bob — Clean Architecture (2017): https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html
[^18]: freeCodeCamp — Production-Ready Flutter CI/CD Pipeline (2026): https://www.freecodecamp.org/news/how-to-build-a-production-ready-flutter-ci-cd-pipeline-with-github-actions-quality-gates-environments-and-store-deployment/
