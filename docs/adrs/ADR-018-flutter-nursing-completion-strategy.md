# ADR-018: Flutter Nursing Module — Completion Strategy & Hardening

**Date:** 2026-05-13  
**Status:** Proposed (pending Council approval before implementation)  
**Author:** Kimi Code CLI  
**Supersedes / amends:** ADR-009 (mobile client strategy) for the nursing feature only; defers full BLoC/Hive/drift migration to v2.  

## Context

The backend nursing module is live and tested (ADR-004). An initial Flutter scaffold (`afc59d6`) exists under `mathwise_build/lib/features/nursing/` but has not been compiled because Flutter SDK is unavailable in this environment. Before writing more Flutter code we must resolve architectural unknowns surfaced by introspection and real-time research.

The target learner is an adult preparing for the Telangana Staff Nurse / Nursing Officer recruitment exam. She accesses the app on a smartphone, may have intermittent connectivity, and reads Telugu more comfortably than English although the exam itself is English-only.

## Decision

Complete the Flutter nursing module using the following constraints and patterns.

### 1. Align with existing codebase patterns

Use **StatefulWidget + service classes**, matching the current MathWise app structure. Introduce a lightweight `NursingSessionController` that extends Flutter's built-in `ChangeNotifier` to manage cross-screen quiz state. Do not add `flutter_bloc`, `Riverpod`, `get_it`, `dio`, `hive`, or `drift` for nursing v1. This keeps the feature consistent with existing screens, adds zero new dependencies, and still solves cross-screen state without constructor plumbing.

> **Note:** ADR-009 recommended BLoC + Hive + drift for the long-term mobile architecture. That remains the strategic direction, but the actual codebase has not yet migrated to it. Nursing v1 will therefore be implemented in the current style, and a future v2 refactor will migrate it together with the rest of the app.

### 2. Update SDK constraints to match actual API usage

Update `mathwise_build/pubspec.yaml` from `sdk: '>=3.2.0 <4.0.0'` to:

```yaml
environment:
  sdk: '>=3.6.0 <4.0.0'
  flutter: '>=3.27.0'
```

**Rationale:** `pubspec.yaml`'s `sdk` field constrains the **Dart SDK** version, while the `flutter` field constrains the **Flutter SDK** version [^10]. Flutter 3.27.0 ships Dart 3.6.0, and the existing MathWise codebase already uses `Color.withValues(alpha: …)` introduced in Flutter 3.27.0 [^1]. Pinning both constraints prevents misleading compatibility claims and avoids `flutter pub get` failures. This also unlocks the current `PopScope.onPopInvokedWithResult` API (added in 3.22) [^2].

### 3. Replace deprecated back-button handling

Replace `WillPopScope` in `nursing_quiz_screen.dart` with `PopScope<Object?>` using `onPopInvokedWithResult`. Both `WillPopScope` and `PopScope.onPopInvoked` are deprecated [^2].

Use the recommended pattern: maintain a `_canPop` boolean, set `canPop: _canPop`, and in `onPopInvokedWithResult` set `_canPop = true` before calling `Navigator.of(context).pop()` once. This avoids `_debugLocked` navigation errors that can occur when issuing multiple pops inside the callback [^11]. Always check `if (didPop) return;` first and guard async work with `if (!mounted) return;`.

### 4. Offline-first fallback question bank

Bundle a static JSON file (`assets/nursing/nursing_seed_questions.json`) containing the verified nursing question bank. At app startup the `NursingApiService` attempts to fetch fresh questions; if the network fails, the app falls back to the bundled asset. This guarantees practice is available even with poor connectivity.

- The bundled asset is generated from the backend seed JSON during build.
- Fresh attempts are still sent to `/api/nursing/analyze` when online; offline attempts are queued in `SharedPreferences` and retried on the next successful call.
- Measure APK size impact with `flutter build apk --analyze-size` before release; if the seed grows beyond a few hundred KB, migrate to on-demand lazy loading or a local database (sqflite) instead of a monolithic bundled JSON [^12].
- This follows the offline-first principle documented in mobile-learning research: reliable access to content is a stronger predictor of continued use than real-time personalization in low-bandwidth contexts [^3].

### 5. Mock test UI: scrollable list + review navigation

The 80-question mock test will render as a vertically scrollable `ListView` with:
- Sticky progress indicator (`LinearProgressIndicator`).
- Previous/Next buttons and a floating “Submit” action.
- **Mark for review** toggle per question.
- Bottom-sheet **question navigation grid** accessible from the app bar.
- Pre-submit summary showing answered / unanswered / marked counts.

Rationale: Leading Indian exam-prep apps (Testbook, Adda247, Gradeup) provide analytics, navigation, and review as core features [^8]. Adult test-takers need the ability to skip hard questions and return later; removing this causes exam anxiety.

### 6. No `share_plus`; use `Clipboard` for PDF export

The PDF export screen will copy the generated HTML to the device clipboard instead of using a share sheet. This avoids adding `share_plus` and keeps the dependency surface minimal. Users can paste the HTML into WhatsApp, notes, or a browser.

### 7. Adult-learner UX and accessibility guidelines

Apply systematic-review evidence on mobile apps for older/adult learners [^4]:
- **Simplify:** one primary action per screen.
- **Large touch targets:** minimum 48×48 dp on Android and 44×44 pt on iOS for all interactive elements; this aligns with Material Design, Apple HIG, and WCAG 2.2 Level AAA [^5][^13].
- **Spacing:** ensure at least 24 dp/pt between adjacent small targets to satisfy WCAG 2.2 Level AA target-size exceptions [^13].
- **Icon + label:** every icon has a text label to reduce ambiguity and improve screen-reader discoverability.
- **Adequate spacing:** avoid controls near screen edges.
- **Calm palette:** use muted medical/teal tones; avoid childish gamification.
- **Telugu labels:** all UI chrome supports Telugu; question text stays English.
- **Text scaling:** layouts must remain usable at 200% system font size.
- **Screen-reader support:** all answer options and action buttons need semantic labels for TalkBack / VoiceOver.

### 7b. Onboarding and disclaimer

Add a **first-launch disclaimer** screen stating the app is for exam preparation only, not medical advice, and not a substitute for official training or syllabus. Add a **2–3 card onboarding** flow explaining Practice, Mock Test, and Weak-area Review. Keep total onboarding under 60 seconds and allow skip [^9].

### 8. Medical content trust signals

Display `source`, `verified_by`, and `last_reviewed` metadata on every question card, collapsed by default and expandable on tap. Research shows users with lower health literacy rely heavily on source credibility cues when evaluating medical information [^6].

### 9. Preserve quiz progress across process death

Mock and diagnostic tests are long-running (up to 60 minutes). Android and iOS can kill background processes to reclaim resources [^15]. To protect user progress:

- Persist the current quiz state (`questions`, `_currentIndex`, `_selectedAnswers`, `_remainingSeconds`, `mode`) to `SharedPreferences` on every answer selection and timer tick.
- On `initState`, if a persisted in-flight session exists and matches the requested mode/subject/topic, offer the user a "Resume previous test?" dialog instead of starting fresh.
- Clear the persisted state on `_submit()` or when the user explicitly abandons the test.
- Alternatively, enable `RestorationMixin` on `NursingQuizScreen` and set `restorationScopeId` on `MaterialApp` for automatic state restoration [^16].

This prevents lost work due to phone calls, low memory, or rotation on older devices, which is especially important for adult learners with limited test-taking time windows.

### 10. Configurable, resilient API client

Refactor `NursingApiService` to accept a configurable `baseUrl` and per-call timeout. Default production URL: `https://drmath.trelolabs.com`. Local development override via constructor parameter. Wrap network failures in a user-friendly `NursingApiException`. Add one immediate retry on timeout for the most critical calls, following 2026 resilience best practice of timeout + retry [^7].

Add lightweight API contract tests in `test/nursing/` that validate the JSON shape of `/api/nursing/status`, `/api/nursing/topics`, `/api/nursing/questions`, `/api/nursing/diagnostic/start`, `/api/nursing/mock/start`, and `/api/nursing/analyze` responses against documented schemas. Run these against the live backend in CI to catch schema drift early [^14].

## Consequences

### Positive
- Consistent with existing MathWise code; no architectural drift within the nursing v1 feature.
- `ChangeNotifier` session controller solves cross-screen state without new dependencies.
- Offline fallback increases reliability for the target user’s connectivity context.
- Minimal dependency additions (`http` and `shared_preferences` already added).
- Trust signals, disclaimer, and adult-learner UX reduce anxiety and improve perceived credibility.
- Mock navigation/mark-for-review aligns with leading exam-prep apps.
- Dual SDK constraint (Dart + Flutter) reflects reality, preventing misleading version claims.
- Recommended `PopScope` pattern avoids `_debugLocked` navigation crashes.
- API contract tests catch backend schema drift before release.

### Negative
- StatefulWidget + services does not scale as cleanly as BLoC/Riverpod; v2 will require refactor.
- Bundled JSON increases APK size by ~150–300 KB (mitigated by gzip in app bundle).
- `onPopInvokedWithResult` requires Flutter >=3.27, which is enforced by the SDK bump but may exclude users on older Flutter installations.
- Onboarding and disclaimer add one extra tap before first use.

### Negative
- StatefulWidget + services does not scale as cleanly as BLoC/Riverpod; v2 will require refactor.
- Bundled JSON increases APK size by ~150–300 KB (mitigated by gzip in app bundle).
- `onPopInvokedWithResult` requires Flutter >=3.27, which is enforced by the SDK bump but may exclude users on older Flutter installations.
- Onboarding and disclaimer add one extra tap before first use.

## Alternatives Considered

| Alternative | Why Not Chosen |
|-------------|----------------|
| Add `flutter_bloc` + `dio` + `hive` now | Would diverge from the actual existing codebase and increase TCO before the feature compiles. Defer to v2. |
| `share_plus` for PDF export | Adds native dependency and permission surface; clipboard is sufficient for v1. |
| Navigation grid for all 80 mock questions | Increases UI complexity; defer to v1.5 after core flow is verified. |
| Online-only question loading | Fails in poor connectivity, which is common for the target learner. |
| Keep SDK constraint at `>=3.2.0` | Existing `withValues` usage already requires Flutter 3.27 / Dart 3.6; would produce false compatibility claims. |
| Pin only Dart SDK | Flutter SDK constraint is separate; omitting it allows Flutter 3.27+ features to fail on older Flutter versions that still satisfy the Dart constraint. |
| Use `PopScope.onPopInvoked` | Deprecated since Flutter 3.22; would emit warnings on current stable (3.44 as of May 2026). |
| Use `Navigator.pop()` repeatedly inside `onPopInvokedWithResult` | Can trigger `_debugLocked` navigation errors; use `_canPop` state + single pop instead [^11]. |
| Add separate nursing app now | Higher TCO and slower delivery; module can be extracted later if needed. |
| Skip disclaimer/onboarding | Medical-adjacent content requires clear educational-purpose disclaimer; adult first-time users need orientation. |

## Compliance

- Follows Research-First Covenant: introspection, web research, DFS harvest of great-app techniques, and ADR completed before code.
- Follows 10-Persona Filter: adult-learner UX (Research Scientist/Clarity Communicator), offline-first (Resource Strategist/Infrastructure SRE), trust signals (Ethical Technologist).

## Implementation Notes

- Implementation is blocked pending approval of this ADR and the revised `nursing-flutter-completion-plan.md`.
- After approval, execution order: compile fixes → widget extraction → offline fallback wiring → new screens → service hardening → tests → manual verification.
- Great-app techniques harvested in `docs/research/dfs/dfs-09-flutter-great-apps-techniques.md` inform the performance, accessibility, and testing decisions above.

## References

[^1]: Flutter API docs. `Color.withValues`. https://api.flutter.dev/flutter/dart-ui/Color/withValues.html
[^2]: Flutter breaking changes. *Generic types in PopScope*. https://docs.flutter.dev/release/breaking-changes/popscope-with-result
[^3]: Ally, M. (2009). Mobile Learning: Transforming the Delivery of Education and Training. *AU Press*.
[^4]: Gómez-Hernández, M., et al. (2023). Design Guidelines of Mobile Apps for Older Adults: Systematic Review and Thematic Analysis. *JMIR mHealth and uHealth*, 11, e43186. doi:10.2196/43186
[^5]: Maestro (2026). *Best Practices for Accessibility Testing in Mobile Frameworks*. https://maestro.dev/insights/accessibility-testing-mobile-frameworks-best-practices
[^6]: Chen, X., Hay, J. L., Waters, E. A., Kiviniemi, M. T., et al. (2018). Health Literacy and Use and Trust in Health Information. *Journal of Health Communication*, 23(8), 724–734. doi:10.1080/10810730.2018.1511658
[^7]: TechShitanshu (2025). *Retry Timeout Pattern Explained: Resilient Competitive Microservices with Backoff 2026*. https://techshitanshu.com/retry-timeout-pattern-backoff/
[^8]: TryReadable (2026). *Testbook vs Adda247 vs Gradeup best app for SSC exam preparation*. https://www.tryreadable.ai/analysis/testbook-vs-adda247-vs-gradeup-best-app-for-ssc-exam-preparation
[^9]: TechAhead (2026). *19 Mobile App Onboarding Best Practices and Examples*. https://www.techaheadcorp.com/blog/19-mobile-app-onboarding-best-practices-examples/
[^10]: Dart docs. *The pubspec file — SDK constraints*. https://dart.dev/tools/pub/pubspec#sdk-constraints
[^11]: 掘金 (2025). *Flutter PopScope 返回拦截完整指南：易错点＋正确姿势＋实战示例*. https://juejin.cn/post/7580592190020452386
[^12]: Flutter docs. *Measuring your app's size*. https://docs.flutter.dev/perf/app-size
[^13]: W3C (2023). *WCAG 2.2 Understanding Success Criterion 2.5.5: Target Size (Enhanced)*. https://www.w3.org/WAI/WCAG22/Understanding/target-size-enhanced.html; and *2.5.8: Target Size (Minimum)*. https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html
[^14]: Redocly (2025). *API Contract Testing 101: Benefits, challenges, and when you need it*. https://redocly.com/learn/testing/contract-testing-101
[^15]: Square Developer Blog (2019). *Flutter, Android, and Process Death*. https://developer.squareup.com/blog/flutter-android-and-process-death/
[^16]: Kodeco (2023). *State Restoration of Flutter App*. https://www.kodeco.com/36759497-state-restoration-of-flutter-app
