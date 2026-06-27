# Nursing Flutter Module — Completion & Hardening Plan

**Date:** 2026-05-13  
**Scope:** Take the initial nursing Flutter scaffold from commit `afc59d6` to a buildable, testable, feature-complete v1.  
**Constraint:** Flutter SDK is not available in this environment; all code must be written defensively and verified by the user with `flutter build`.  
**Prerequisite:** Approve ADR-018 and this plan before any Flutter code changes.

---

## 0. Goal and Success Criteria

**Goal:** A user can open the MathWise app, tap "Telangana Staff Nurse", and complete a full learning loop: choose subject/topic → practice questions → see results → practice weak areas → take a mock test.

**Success criteria:**
1. `flutter pub get` succeeds.
2. `flutter build apk --debug` succeeds with zero compile errors.
3. `flutter build apk --split-per-abi --release` succeeds and produces a reasonably sized APK.
4. All existing MathWise screens remain reachable.
5. At least one widget test passes for each nursing screen.
6. No runtime crashes on the four main flows: home, subject list, quiz, results.
7. Quiz screen works offline using the bundled fallback question bank.
8. Profile-mode frame times are acceptable (no sustained jank) on the quiz screen.

---

## 1. Immediate Fix Phase — Make It Compile

Before adding features, the existing scaffold must compile. We cannot run `flutter build` here, so we will audit line-by-line against the project's effective Flutter SDK constraints.

### 1.1 Audit `pubspec.yaml`

**File:** `mathwise_build/pubspec.yaml`  
**Changes needed:**
- Update SDK constraint from `>=3.2.0 <4.0.0` to `>=3.27.0 <4.0.0` because the existing codebase already uses `Color.withValues(alpha: …)`, which requires Flutter 3.27+.
- Verify `http: ^1.2.0` and `shared_preferences: ^2.2.2` remain compatible. Both are.
- Verify `assets/nursing/` is listed under `assets:`. Already added.
- Add the bundled fallback file explicitly: `assets/nursing/nursing_seed_questions.json`.

**Why:** Build fails if dependencies or SDK constraints are incompatible; assets must be enumerated.

### 1.2 Document Flutter version pinning

**File:** `mathwise_build/.fvmrc` (new) or a note in `mathwise_build/README.md`.

**Content:**
```json
{
  "flutter": "3.27.0"
}
```

**Why:** The existing codebase uses `Color.withValues` (Flutter 3.27+) and `PopScope.onPopInvokedWithResult` (Flutter 3.22+). Pinning the version prevents "works on my machine" build failures and matches how great apps like Google Pay and Nubank pin toolchain versions in CI [^6][^7].

### 1.3 Audit existing nursing Dart files for compile-time issues

**Files to audit:**
- `lib/features/nursing/models/nursing_question.dart`
- `lib/features/nursing/models/attempt.dart`
- `lib/features/nursing/models/capability.dart`
- `lib/features/nursing/services/nursing_api_service.dart`
- `lib/features/nursing/services/nursing_storage_service.dart`
- `lib/features/nursing/services/glossary_service.dart`
- `lib/features/nursing/widgets/nursing_app_bar.dart`
- `lib/features/nursing/widgets/language_toggle.dart`
- `lib/features/nursing/widgets/loading_state.dart`
- `lib/features/nursing/screens/nursing_home_screen.dart`
- `lib/features/nursing/screens/nursing_subject_screen.dart`
- `lib/features/nursing/screens/nursing_quiz_screen.dart`
- `lib/features/nursing/screens/nursing_results_screen.dart`
- `lib/features/home/home_screen.dart` (integration point)

**Likely issues to fix:**
1. `WillPopScope` in `nursing_quiz_screen.dart` is deprecated. Replace with `PopScope` + `onPopInvokedWithResult` (available since Flutter 3.22; safe because effective minimum is 3.27).
2. Missing `const` constructors and lint warnings may fail CI if `flutter_lints` treats warnings as errors.
3. Ensure no references to `WillPopScope` or `onWillPop` remain.
4. Ensure every new widget uses `const` constructors where possible — this is a performance habit practiced by high-scale apps like Google Pay [^5].

### 1.4 Replace `WillPopScope` with `PopScope`

**File:** `lib/features/nursing/screens/nursing_quiz_screen.dart`

**Current:**
```dart
return WillPopScope(
  onWillPop: _confirmExit,
  child: Scaffold(...)
);
```

**Planned change:**
```dart
return PopScope<Object?>(
  canPop: false,
  onPopInvokedWithResult: (didPop, result) async {
    if (didPop) return;
    final shouldPop = await _confirmExit();
    if (shouldPop && mounted) Navigator.of(context).pop();
  },
  child: Scaffold(...)
);
```

**Why:** `WillPopScope` and `PopScope.onPopInvoked` are deprecated; `onPopInvokedWithResult` is the current API as of Flutter 3.22+ [^1].

---

## 2. Widget Refactoring Phase — Extract Reusable Components

Currently screens embed question/options directly. We will extract reusable widgets so each screen is small and testable.

### 2.1 File: `lib/features/nursing/widgets/question_card.dart`

**Purpose:** Display a single question stem.

**Class:**
```dart
class QuestionCard extends StatelessWidget {
  final NursingQuestion question;
  final String? selectedAnswer;
  final ValueChanged<String>? onSelect;
  final bool showFeedback;
  final bool readOnly;
  final VoidCallback? onReport;
  
  const QuestionCard({
    super.key,
    required this.question,
    this.selectedAnswer,
    this.onSelect,
    this.showFeedback = false,
    this.readOnly = false,
    this.onReport,
  });
}
```

**Build method rationale:**
- Shows metadata row (`Q{n}/{total} • cognitive_level • context`).
- Shows question text in `Text` with `style: Theme.of(context).textTheme.titleMedium`.
- Builds 4 `OptionButton` children.
- If `showFeedback` is true, highlights correct/wrong options and shows `ExplanationCard`.
- Adds a small expandable trust row (`source`, `verified_by`, `last_reviewed`) to support health-literacy trust cues [^2].
- Adds a report icon if `onReport` is provided.

**Why:** Centralizes question rendering so `nursing_quiz_screen.dart`, review screens, and report screen share the same widget.

### 2.2 File: `lib/features/nursing/widgets/option_button.dart`

**Purpose:** Single A/B/C/D answer option.

**Class:**
```dart
class OptionButton extends StatelessWidget {
  final String option;
  final bool isSelected;
  final bool isCorrect;
  final bool showFeedback;
  final VoidCallback? onTap;
  
  const OptionButton({...});
}
```

**Build method rationale:**
- `Card` with `ListTile`.
- Minimum 48×48 dp tappable area (accessibility requirement) [^3].
- Background color logic:
  - `showFeedback && isCorrect` → green.
  - `showFeedback && isSelected && !isCorrect` → red.
  - `isSelected` → blue tint.
  - default → surface color.
- `onTap` only fires when `showFeedback` is false (i.e., practice mode before answer).
- Wraps label text in `Semantics(label: 'Option $letter')` for screen readers.

**Why:** Consistent touch targets, accessible semantics, and visual feedback.

### 2.3 File: `lib/features/nursing/widgets/explanation_card.dart`

**Purpose:** Show explanation after answering.

**Class:**
```dart
class ExplanationCard extends StatelessWidget {
  final String explanation;
  final String correctAnswer;
  const ExplanationCard({super.key, required this.explanation, required this.correctAnswer});
}
```

**Why:** Separates learning feedback from question stem.

### 2.4 File: `lib/features/nursing/widgets/capability_bar.dart`

**Purpose:** Visual bar for accuracy/priority score.

**Class:**
```dart
class CapabilityBar extends StatelessWidget {
  final String label;
  final double value; // 0.0 to 1.0
  final Color? color;
  const CapabilityBar({super.key, required this.label, required this.value, this.color});
}
```

**Why:** Reused on results screen and future dashboard.

### 2.5 File: `lib/features/nursing/widgets/timer_widget.dart`

**Purpose:** Countdown or elapsed timer.

**Class:**
```dart
class TimerWidget extends StatelessWidget {
  final int seconds;
  final bool isCountdown;
  const TimerWidget({super.key, required this.seconds, this.isCountdown = true});
}
```

**Why:** Consistent time display across diagnostic and mock.

### 2.6 File: `lib/features/nursing/widgets/glossary_tooltip.dart`

**Purpose:** Wrap medical terms with Telugu tooltip.

**Class:**
```dart
class GlossaryText extends StatelessWidget {
  final String text;
  final Map<String, String> glossary;
  const GlossaryText({super.key, required this.text, required this.glossary});
}
```

**Build method rationale:**
- Split text by whitespace.
- For each token, check lowercased glossary.
- If found, wrap in `Tooltip(message: teluguTerm, child: Text(term, style: highlighted))`.
- Otherwise render plain `TextSpan`.

**Why:** Provides Telugu support without changing question text (exam is English-only).

### 2.7 Performance rules borrowed from great apps

Great Flutter apps (Google Pay, Nubank, BMW, eBay Motors) share the following habits [^6][^9][^10]:

1. **Use `const` constructors** on every stateless widget that can be const.
2. **Split large `build()` methods** into smaller widgets to localize rebuilds.
3. **Localize `setState()`** to the smallest subtree that changes.
4. **Use `ListView.builder`** for long lists (question review, subject list) instead of eager `Column` with loops.
5. **Wrap complex/animating widgets** in `RepaintBoundary` only if profiling shows repaints are expensive.
6. **Profile in profile mode** on a physical device; debug mode numbers are not representative.
7. **Build release APK with `--split-per-abi`** to reduce download size.

These rules will be applied during widget extraction and verified in the manual checklist.

---

## 3. Offline-First Phase

### 3.1 Generate bundled fallback asset

**Source:** `output/nursing_staff_nurse_output.json` (verified backend seed bank with 130 questions).  
**Target:** `mathwise_build/assets/nursing/nursing_seed_questions.json`.  
**Build step:** Create `scripts/generate_nursing_flutter_assets.sh` that:
1. Verifies `output/nursing_staff_nurse_output.json` exists.
2. Extracts the `questions` array and writes it compactly to `mathwise_build/assets/nursing/nursing_seed_questions.json`.
3. Prints question count and file size.

**pubspec entry:**
```yaml
assets:
  - assets/nursing/nursing_seed_questions.json
```

**Why:** The actual seed bank is in `output/`, not `data/`. Automating the copy prevents stale fallback content.

### 3.2 Update `NursingApiService` to fall back to bundled asset

**Behavior:**
1. Attempt online fetch first.
2. On `TimeoutException`, `SocketException`, or any non-2xx response, log a structured warning.
3. Load `assets/nursing/nursing_seed_questions.json` via `DefaultAssetBundle` and parse into `List<NursingQuestion>`.
4. Apply the same filters (`subjectId`, `topicId`, `limit`, etc.) client-side when using the fallback.

**Why:** Guarantees the user can practice even when the backend or network is unavailable [^4].

### 3.3 Run JSON parsing off the main thread for large lists

Use `compute()` from `flutter/foundation.dart` to parse the bundled JSON if it grows beyond ~200 KB. For the current 130-question bank this is optional but recommended as a defensive habit.

### 3.3 Queue offline attempts for later sync

**File:** `lib/features/nursing/services/nursing_storage_service.dart`  
**Behavior:**
- When `analyzeAttempts` is called while offline, store the attempts list under a `pending_nursing_analysis` key in `SharedPreferences`.
- On the next successful online call, clear the pending key.
- Expose `hasPendingAnalysis` for the UI to show a "sync pending" indicator.

---

## 4. New Screen Phase

### 4.1 File: `lib/features/nursing/screens/nursing_disclaimer_screen.dart`

**Purpose:** Legal/educational disclaimer shown on first launch.

**State fields:**
- `bool _accepted`

**Build sections:**
1. Title: "Important — Read Before You Begin".
2. Body text:
   - "This app is for exam preparation and educational practice only."
   - "It is not medical advice, diagnosis, or treatment."
   - "Always verify answers with official INC/GNM syllabus and your institution."
3. Checkbox: "I understand".
4. `ElevatedButton` enabled only after checkbox is checked → stores acceptance in `SharedPreferences` and navigates to onboarding/home.

**Why:** Medical-adjacent content requires proactive liability protection and trust-building.

### 4.2 File: `lib/features/nursing/screens/nursing_onboarding_screen.dart`

**Purpose:** 2–3 card introduction for first-time users.

**State fields:**
- `int _currentPage`
- `PageController _pageController`

**Cards:**
1. "Practice by Subject" — choose a topic and practice MCQs.
2. "Full Mock Test" — 80 questions, 60 minutes, like the real exam.
3. "Review Weak Areas" — see where you need more practice.

**Navigation:** Next / Skip / Get Started buttons. Store `nursing_onboarding_seen` in `SharedPreferences`.

**Why:** Adult first-time smartphone learners benefit from brief, skippable orientation [^11].

### 4.3 File: `lib/features/nursing/screens/nursing_report_screen.dart`

**Purpose:** Report a questionable question.

**Route:** pushed from `QuestionCard` report icon.

**State fields:**
- `TextEditingController _reasonController`
- `bool _submitting`
- `bool _submitted`

**Build sections:**
1. `NursingAppBar(title: 'Report Question')`.
2. Read-only `QuestionCard` for the reported question.
3. Quick-reason chips: "Wrong answer", "Unclear wording", "Outdated", "Typo".
4. `TextField` for detailed reason.
5. `ElevatedButton` Submit → calls `NursingApiService.reportQuestion`.
6. Success state with "Thank you" and back button.

**Why:** Satisfies the safety requirement that every question is reportable.

### 4.4 File: `lib/features/nursing/screens/nursing_pdf_screen.dart`

**Purpose:** Generate weak-area practice PDF.

**Route:** pushed from results screen or home.

**State fields:**
- `List<Capability> weakTopics`
- `bool _generating`
- `String? _html`

**Build sections:**
1. `NursingAppBar(title: 'Practice PDF')`.
2. List of weak topics with checkboxes.
3. Generate button → calls `/api/nursing/pdf` with attempts (or uses cached attempts).
4. On success, show preview and a **"Copy HTML"** button using `Clipboard` from `flutter/services.dart`.

**Why:** Supports offline printable practice without adding `share_plus`.

### 4.5 File: `lib/features/nursing/screens/nursing_settings_screen.dart`

**Purpose:** Language and data preferences.

**State fields:**
- `String _language`
- `bool _clearing`

**Build sections:**
1. Language toggle tile.
2. Clear progress tile with confirmation dialog.
3. Disclaimer card.
4. Offline-mode indicator tile.

**Why:** Adult learners need control over language and data.

### 4.6 Quiz screen enhancements for mock mode

**File:** `lib/features/nursing/screens/nursing_quiz_screen.dart`

**Additions for `QuizMode.mock`:**
1. **Mark for review** toggle in the app bar or bottom sheet.
2. **Question navigation grid** bottom sheet triggered from app bar. Each cell shows:
   - Question number.
   - Color: answered = green, marked = orange, unanswered = grey.
   - Tap jumps to that question.
3. **Pre-submit summary** dialog when user taps Submit:
   - Total questions.
   - Answered count.
   - Unanswered count.
   - Marked count.
   - "Go back" and "Submit anyway" buttons.

**Why:** Adult test-takers need navigation and review control to manage time and anxiety during an 80-question mock [^12].

---

## 5. Service Hardening Phase

### 5.1 File: `lib/features/nursing/services/nursing_api_service.dart`

**Additions:**
- Constructor with configurable `baseUrl` and timeout:
  ```dart
  final String baseUrl;
  final Duration timeout;
  NursingApiService({
    this.baseUrl = 'https://drmath.trelolabs.com',
    this.timeout = const Duration(seconds: 10),
  });
  ```
- Wrap every `http` call with `.timeout(timeout)`.
- Catch `TimeoutException`, `SocketException`, and `http.ClientException` and throw `NursingApiException` with a user-friendly message and an `isOffline` flag.
- Add a lightweight retry wrapper (1 immediate retry on timeout) for `startDiagnostic`, `startMock`, and `analyzeAttempts`.
- Add `loadFallbackQuestions()` to read the bundled JSON asset.

**Why:** Hardcoded URLs and missing timeouts make local testing and error handling difficult; retries follow 2026 resilience best practices [^5].

### 5.2 File: `lib/features/nursing/services/nursing_session_logger.dart` (new)

**Purpose:** Log completed sessions for Phase 6 monitoring.

**Class:**
```dart
class NursingSessionLogger {
  Future<void> log({
    required String mode,
    required int attemptsCount,
    required double score,
    required List<String> weakAreas,
  });
}
```

**Storage:** Append JSON lines to `SharedPreferences` under key `nursing_sessions`.

**Why:** Enables the correlation experiment described in `bidirectional-06`.

---

## 6. State Management Decision

**Decision:** Keep `StatefulWidget` + services, but add a lightweight `NursingSessionController` extending `ChangeNotifier` for cross-screen quiz state. No Riverpod/Bloc for nursing v1.

**Controller responsibilities:**
- Hold current quiz mode, question list, current index.
- Track selected answers and mark-for-review flags.
- Manage mock timer.
- Build `Attempt` list on submit.
- Expose loading/error states.

**Why:**
- `ChangeNotifier` is part of `flutter:foundation` — zero new dependencies.
- Matches the actual existing MathWise codebase style.
- Solves cross-screen state (home → quiz → results → weak-area practice) without constructor plumbing.
- Easily migratable to Provider/Riverpod in v2.
- ADR-009’s BLoC/Hive/drift strategy remains the long-term direction and will be applied in a v2 refactor across the whole app.

**File:** `lib/features/nursing/controllers/nursing_session_controller.dart`

---

## 7. Testing Phase

### 7.1 Widget tests

**Files to create:**
- `test/features/nursing/nursing_home_screen_test.dart`
- `test/features/nursing/nursing_quiz_screen_test.dart`
- `test/features/nursing/nursing_results_screen_test.dart`
- `test/features/nursing/widgets/option_button_test.dart`

**Approach:**
- Pump widgets with mock `NursingApiService`.
- Use `mockito` or manual stub classes.
- Verify buttons, navigation, offline fallback, and error states.
- Add `androidTapTargetGuideline` and `iOSTapTargetGuideline` accessibility assertions for `OptionButton` [^3].

**Why:** Widget tests catch compile and layout regressions without needing a device. Accessibility assertions enforce the 48×48 dp / 44×44 pt minimum touch targets used by great apps [^3][^9].

### 7.2 Unit tests

**Files to create:**
- `test/features/nursing/models/attempt_test.dart`
- `test/features/nursing/services/nursing_storage_service_test.dart`
- `test/features/nursing/services/nursing_api_service_test.dart` (timeout + fallback logic)

**Why:** Models and storage are pure Dart and easy to unit test.

### 7.3 Accessibility checks

Add `androidTapTargetGuideline` and `iOSTapTargetGuideline` assertions in widget tests for `OptionButton`.

**Why:** Ensures 48×48 dp / 44×44 pt minimum touch targets [^3].

---

## 8. Integration Test Plan (Manual)

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Launch app | Home screen loads |
| 2 | Tap "Open" on Nursing card | Nursing home loads with subject list |
| 3 | Tap a subject | Topic list loads |
| 4 | Tap "Practice" on a topic | Quiz screen with 1st question |
| 5 | Select answer → Next | Move to next question |
| 6 | Finish all questions | Results screen shows score |
| 7 | Tap "Try Again" | New diagnostic quiz starts |
| 8 | Tap "Mock" from home | 80-question mock with timer |
| 9 | Background app during mock | Timer pauses or continues appropriately |
| 10 | Submit mock | Results screen shows score |
| 11 | Enable airplane mode and start practice | Questions load from bundled fallback JSON |
| 12 | Tap report icon on a question | Report screen opens and submits |
| 13 | Run `flutter run --profile` and scroll quiz | No sustained red bars in performance overlay |
| 14 | Run `flutter build apk --split-per-abi --release` | Build succeeds; APK size is reasonable |

---

## 9. File List to Create/Modify

### Modify
1. `pubspec.yaml` — bump SDK constraint, enumerate fallback JSON asset.
2. `lib/features/nursing/screens/nursing_quiz_screen.dart` — replace `WillPopScope` with `PopScope`, use new widgets, add mock navigation/review.
3. `lib/features/nursing/screens/nursing_home_screen.dart` — add settings button.
4. `lib/features/nursing/screens/nursing_results_screen.dart` — add PDF and weak-area practice buttons.
5. `lib/features/nursing/services/nursing_api_service.dart` — configurable baseUrl, timeouts, exceptions, fallback loader.
6. `lib/features/nursing/services/nursing_storage_service.dart` — pending-analysis queue.

### Create
7. `scripts/generate_nursing_flutter_assets.sh` — copy seed bank to Flutter assets.
8. `assets/nursing/nursing_seed_questions.json` (generated from backend seed).
9. `lib/features/nursing/controllers/nursing_session_controller.dart` — ChangeNotifier-based quiz state.
10. `lib/features/nursing/widgets/question_card.dart`
11. `lib/features/nursing/widgets/option_button.dart`
12. `lib/features/nursing/widgets/explanation_card.dart`
13. `lib/features/nursing/widgets/capability_bar.dart`
14. `lib/features/nursing/widgets/timer_widget.dart`
15. `lib/features/nursing/widgets/glossary_tooltip.dart`
16. `lib/features/nursing/widgets/question_grid_sheet.dart` — mock navigation bottom sheet.
17. `lib/features/nursing/widgets/submit_summary_dialog.dart` — pre-submit summary.
18. `lib/features/nursing/screens/nursing_disclaimer_screen.dart`
19. `lib/features/nursing/screens/nursing_onboarding_screen.dart`
20. `lib/features/nursing/screens/nursing_report_screen.dart`
21. `lib/features/nursing/screens/nursing_pdf_screen.dart`
22. `lib/features/nursing/screens/nursing_settings_screen.dart`
23. `lib/features/nursing/services/nursing_session_logger.dart`
24. `test/features/nursing/nursing_home_screen_test.dart`
25. `test/features/nursing/nursing_quiz_screen_test.dart`
26. `test/features/nursing/nursing_results_screen_test.dart`
27. `test/features/nursing/models/attempt_test.dart`
28. `test/features/nursing/services/nursing_storage_service_test.dart`
29. `test/features/nursing/services/nursing_api_service_test.dart`

---

## 10. Execution Order

1. **Update ADR-018** (already drafted) and get approval.
2. **Fix compile issues** (Phase 1) — SDK constraint, `PopScope`.
3. **Generate fallback asset** (Phase 3 offline-first) — run `scripts/generate_nursing_flutter_assets.sh`.
4. **Create session controller** (Phase 6 state management) — `NursingSessionController`.
5. **Refactor widgets** (Phase 2) — extract question/option/explanation/capability/timer/glossary.
6. **Add mock navigation widgets** (Phase 4.6) — question grid sheet, submit summary dialog.
7. **Add offline fallback wiring** (Phase 3) — API service fallback + pending queue.
8. **Add missing screens** (Phase 4) — disclaimer, onboarding, report, PDF, settings.
9. **Harden services** (Phase 5) — timeouts, retries, exceptions, session logger.
10. **Add tests** (Phase 7).
11. **Manual verification** (Phase 8).

Each phase gets one commit with a conventional message and a test/build gate.

---

## 11. Key Research Citations

[^1]: Flutter breaking changes. *Generic types in PopScope*. https://docs.flutter.dev/release/breaking-changes/popscope-with-result
[^2]: Chen, X., et al. (2018). Health Literacy and Use and Trust in Health Information. *Journal of Health Communication*, 23(8), 724–734. doi:10.1080/10810730.2018.1511658
[^3]: Maestro (2026). *Best Practices for Accessibility Testing in Mobile Frameworks*. https://maestro.dev/insights/accessibility-testing-mobile-frameworks-best-practices
[^4]: UOU SLM MCS-604. *Introduction to Mobile Architecture*. https://uou.ac.in/sites/default/files/slm/MCS-604.pdf
[^5]: TechShitanshu (2025). *Retry Timeout Pattern Explained: Resilient Competitive Microservices with Backoff 2026*. https://techshitanshu.com/retry-timeout-pattern-backoff/
[^6]: CueBytes (2026). *20 Best Flutter App Examples Built by Real Companies*. https://cuebytes.com/blog/flutter-app-examples-2026
[^7]: HireFlutterDev (2026). *25 Best Flutter Apps in Production (2026 Showcase)*. https://hireflutterdev.com/blog/best-examples-of-flutter-mobile-apps/
[^8]: TechWithSam (2026). *Clean Architecture in Flutter 2026 — Practical Implementation Guide*. https://dev.to/techwithsam/clean-architecture-in-flutter-2026-practical-implementation-guide-1dfb
[^9]: Flutter Docs. *Performance best practices*. https://docs.flutter.dev/perf/best-practices
[^10]: TechWithSam (2026). *Flutter Performance Optimization 2026*. https://dev.to/techwithsam/flutter-performance-optimization-2026-make-your-app-10x-faster-best-practices-2p07
[^11]: TechAhead (2026). *19 Mobile App Onboarding Best Practices and Examples*. https://www.techaheadcorp.com/blog/19-mobile-app-onboarding-best-practices-examples/
[^12]: TryReadable (2026). *Testbook vs Adda247 vs Gradeup best app for SSC exam preparation*. https://www.tryreadable.ai/analysis/testbook-vs-adda247-vs-gradeup-best-app-for-ssc-exam-preparation
