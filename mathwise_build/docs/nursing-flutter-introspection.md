# Nursing Flutter Module — Introspection, Unknowns, and Plan Revisions

**Date:** 2026-05-13  
**Scope:** Re-examine the Flutter completion plan after initial scaffold using first-principles reasoning and real-time research.  

---

## 1. What I Did

I built an initial Flutter nursing module inside the existing MathWise app:
- 4 screens (home, subjects, quiz, results)
- 3 models, 3 services
- 3 widgets
- Integration into the math home screen
- Dependencies `http` and `shared_preferences`

I could not compile or run it because Flutter SDK is not installed in this environment.

## 2. Unknowns Discovered

### Unknown 1: Will it compile?
The biggest risk. I used `WillPopScope`, modern Dart patterns, and `Color.withValues`. Any of these could fail depending on the exact Flutter/Dart version.

### Unknown 2: Is `StatefulWidget` + services the right architecture?
The existing MathWise app uses this pattern, but nursing has more cross-screen state (attempts, capability map, language). Passing state via constructors and `SharedPreferences` may become messy.

### Unknown 3: What happens when the API is unreachable?
The current `NursingApiService` throws exceptions. There is no offline fallback, retry, or cached question bank. This is a poor experience for users with intermittent connectivity.

### Unknown 4: How do adult learners interact with medical exam apps?
I assumed a simple list/card UI is enough. But adult learners may need bookmarking, review mode, spaced repetition cues, and clear progress tracking.

### Unknown 5: Should nursing be inside MathWise or a separate app?
The user said "app pages components of each page of app". This implies integration, but a separate nursing app would avoid mixing child math branding with adult nursing content.

### Unknown 6: How to handle 80-question mock UI?
A 80-question mock with scrolling may be fatiguing. Question navigation grid, swipe gestures, or pagination patterns need research.

### Unknown 7: Is HTTP sufficient?
`http` is simple but lacks interceptors, retry logic, and typed errors. `dio` is more powerful but adds a dependency.

## 3. First-Principles Reframing

The core need is **reliable, accessible exam practice for an adult learner on a smartphone**.

From first principles:
- The user must be able to practice even with poor connectivity.
- The UI must reduce cognitive load, not add it.
- The app must feel trustworthy for medical content.
- The architecture must be simple enough to maintain without a dedicated mobile team.

This suggests:
1. **Offline-first question bank.** Bundle a JSON question bank in assets and sync with API when online.
2. **Simple state management.** Provider or InheritedWidget is enough; no need for Riverpod/Bloc.
3. **Separate nursing brand within app.** Use calm, adult-appropriate colors; avoid childish gamification.
4. **Focus on core flows first.** Mock navigation grid and report screen are secondary to practice/results.

## 4. Real-Time Research Findings (2026-05)

### 4.1 Flutter SDK version and `PopScope`
- The existing codebase already uses `Color.withValues(alpha: …)`, which was introduced in **Flutter 3.27.0** [^1].
- `WillPopScope` is deprecated; `PopScope.onPopInvoked` itself was deprecated in **Flutter 3.22.0-12.0.pre** in favor of `onPopInvokedWithResult` [^2].
- Because the project effectively requires Flutter >=3.27, we can safely use `onPopInvokedWithResult` and should bump the `pubspec.yaml` SDK constraint to `>=3.27.0 <4.0.0` to match reality.

### 4.2 State management (2026 consensus)
- Riverpod is the most-recommended default for new Flutter projects in 2026 [^3].
- Provider is acceptable for small apps and legacy maintenance [^3].
- Bloc is recommended for enterprise/large teams [^3].
- **Decision for nursing v1:** Keep `StatefulWidget` + services to match the actual existing codebase; defer Riverpod/Bloc to a v2 refactor. This is a pragmatic consistency choice, not a strategic long-term choice.

### 4.3 HTTP client and resilience
- Industry best practice is timeout + retry with exponential backoff + jitter [^4].
- The `http` package does not provide built-in retry. For v1 we will implement `Future.timeout` and a lightweight retry wrapper; `dio` is deferred.

### 4.4 Offline-first mobile apps
- Mobile app best-practice guidelines explicitly recommend handling lost network with offline features and local caching [^5].
- Bundling a static JSON asset as a fallback is a low-complexity way to satisfy this for read-only content.

### 4.5 Adult / older-adult UX
- Systematic review of mobile apps for older adults found the two most significant guidelines are **Simplify** and **Increase size and distance between interactive controls** [^6].
- Recommended tap targets for older adults are >14 mm square; swipe targets >17.5 mm square [^7].
- Accessibility standards require minimum 48×48 dp (Android) and 44×44 points (iOS) touch targets [^8].
- Icons should have labels, layouts should minimize elements, and controls should not be near screen edges [^6].

### 4.6 Medical content trust
- Users with lower health literacy rely more heavily on source credibility cues when evaluating health information [^9].
- Displaying `source`, `verified_by`, and `last_reviewed` on every question supports trust and safe usage.

## 5. Hypotheses to Validate

1. `StatefulWidget` + services is maintainable for v1; Riverpod/Bloc will be introduced in v2.
2. Bundling questions as a local asset improves reliability and perceived performance.
3. A simple list-based mock UI is acceptable for v1; navigation grid can be deferred.
4. `http` + manual retry is sufficient; `dio` is unnecessary for v1.
5. Adult learners prefer clear progress and trust signals over gamification.

## 6. Decisions Reached

| Topic | Decision | Rationale |
|-------|----------|-----------|
| SDK constraint | Bump to `>=3.27.0 <4.0.0` | Existing code uses `withValues`; enables `onPopInvokedWithResult`. |
| Back navigation | `PopScope` with `onPopInvokedWithResult` | Current, non-deprecated API. |
| State management | `StatefulWidget` + services | Match existing codebase; defer architecture migration. |
| Offline fallback | Bundle `assets/nursing/nursing_seed_questions.json` | Guarantees practice despite poor connectivity. |
| Mock UI | Scrollable list with progress indicator; navigation grid deferred | Simplicity + accessibility first. |
| PDF sharing | `Clipboard` for HTML; no `share_plus` | Minimize dependencies. |
| Touch targets | Minimum 48×48 dp | Accessibility + older-adult research. |
| Trust signals | Show source/verified/reviewed metadata | Health-literacy research. |

## 7. Research Needed After v1 Compile

1. Actual widget-test behavior with `PopScope` on user’s Flutter version.
2. APK size impact of bundled JSON.
3. Real-world network failure modes and retry timing.
4. User feedback on mock test UI length and navigation.

## References

[^1]: Flutter API docs. `Color.withValues` introduced in Flutter 3.27.0. https://api.flutter.dev/flutter/dart-ui/Color/withValues.html
[^2]: Flutter breaking changes. *Generic types in PopScope*. https://docs.flutter.dev/release/breaking-changes/popscope-with-result
[^3]: Samioda (2026). *Flutter State Management in 2026: Riverpod vs Bloc vs Provider*. https://samioda.com/en/blog/flutter-state-management-2026
[^4]: TechShitanshu (2025). *Retry Timeout Pattern Explained: Resilient Competitive Microservices with Backoff 2026*. https://techshitanshu.com/retry-timeout-pattern-backoff/
[^5]: UOU SLM MCS-604. *Introduction to Mobile Architecture*. https://uou.ac.in/sites/default/files/slm/MCS-604.pdf
[^6]: Gómez-Hernández, M., et al. (2023). Design Guidelines of Mobile Apps for Older Adults: Systematic Review and Thematic Analysis. *JMIR mHealth and uHealth*, 11, e43186. doi:10.2196/43186
[^7]: Sousa, A., et al. *Creating Mobile Gesture-based Interaction Design Patterns for Older Adults*. University of Porto. https://repositorio-aberto.up.pt/bitstream/10216/68413/1/000155061.pdf
[^8]: Maestro (2026). *Best Practices for Accessibility Testing in Mobile Frameworks*. https://maestro.dev/insights/accessibility-testing-mobile-frameworks-best-practices
[^9]: Chen, X., et al. (2018). Health Literacy and Use and Trust in Health Information. *Journal of Health Communication*, 23(8), 724–734. doi:10.1080/10810730.2018.1511658
