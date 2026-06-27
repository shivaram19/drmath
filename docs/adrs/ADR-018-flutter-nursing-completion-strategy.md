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

### 2. Update SDK constraint to match actual API usage

Bump `mathwise_build/pubspec.yaml` from `sdk: '>=3.2.0 <4.0.0'` to `sdk: '>=3.27.0 <4.0.0'`.

**Rationale:** The existing MathWise codebase already uses `Color.withValues(alpha: …)`, which was introduced in Flutter 3.27.0 [^1]. Pretending the project supports older versions is misleading and will cause compile failures. This also unlocks the current `PopScope.onPopInvokedWithResult` API (added in 3.22) [^2].

### 3. Replace deprecated back-button handling

Replace `WillPopScope` in `nursing_quiz_screen.dart` with `PopScope<Object?>` using `onPopInvokedWithResult`. Both `WillPopScope` and `PopScope.onPopInvoked` are deprecated [^2].

### 4. Offline-first fallback question bank

Bundle a static JSON file (`assets/nursing/nursing_seed_questions.json`) containing the verified nursing question bank. At app startup the `NursingApiService` attempts to fetch fresh questions; if the network fails, the app falls back to the bundled asset. This guarantees practice is available even with poor connectivity.

- The bundled asset is generated from the backend seed JSON during build.
- Fresh attempts are still sent to `/api/nursing/analyze` when online; offline attempts are queued in `SharedPreferences` and retried on the next successful call.
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

### 7. Adult-learner UX guidelines

Apply systematic-review evidence on mobile apps for older/adult learners [^4]:
- **Simplify:** one primary action per screen.
- **Large touch targets:** minimum 48×48 dp for answer options (44×44 pt on iOS) [^5].
- **Icon + label:** every icon has a text label to reduce ambiguity.
- **Adequate spacing:** avoid controls near screen edges.
- **Calm palette:** use muted medical/teal tones; avoid childish gamification.
- **Telugu labels:** all UI chrome supports Telugu; question text stays English.

### 7b. Onboarding and disclaimer

Add a **first-launch disclaimer** screen stating the app is for exam preparation only, not medical advice, and not a substitute for official training or syllabus. Add a **2–3 card onboarding** flow explaining Practice, Mock Test, and Weak-area Review. Keep total onboarding under 60 seconds and allow skip [^9].

### 8. Medical content trust signals

Display `source`, `verified_by`, and `last_reviewed` metadata on every question card, collapsed by default and expandable on tap. Research shows users with lower health literacy rely heavily on source credibility cues when evaluating medical information [^6].

### 9. Configurable, resilient API client

Refactor `NursingApiService` to accept a configurable `baseUrl` and per-call timeout. Default production URL: `https://drmath.trelolabs.com`. Local development override via constructor parameter. Wrap network failures in a user-friendly `NursingApiException`. Add one immediate retry on timeout for the most critical calls, following 2026 resilience best practice of timeout + retry [^7].

## Consequences

### Positive
- Consistent with existing MathWise code; no architectural drift within the nursing v1 feature.
- `ChangeNotifier` session controller solves cross-screen state without new dependencies.
- Offline fallback increases reliability for the target user’s connectivity context.
- Minimal dependency additions (`http` and `shared_preferences` already added).
- Trust signals, disclaimer, and adult-learner UX reduce anxiety and improve perceived credibility.
- Mock navigation/mark-for-review aligns with leading exam-prep apps.
- SDK constraint reflects reality, preventing misleading version claims.

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
| Keep SDK constraint at `>=3.2.0` | Existing `withValues` usage already requires 3.27; would produce false compatibility claims. |
| Use `PopScope.onPopInvoked` | Deprecated since Flutter 3.22; would emit warnings on current stable (3.44 as of May 2026). |
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
