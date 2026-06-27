# Nursing Flutter Module — Round 2 Introspection & Self-Interview

**Date:** 2026-05-13  
**Scope:** Dig deeper into mental/blended-space unknowns after first round of research and planning.  

---

## Part 1: Introspection — What Am I Still Hiding From Myself?

### Hidden assumption 1: "The user wants nursing inside MathWise."
I assumed integration because the scaffold was placed inside `mathwise_build/`. But the user's mother is an adult learner preparing for a government exam. Mixing a child-focused math brand with adult nursing content may feel infantilizing or confusing. A separate "Dr. Math Nursing" build or a clearly separated module might be better.

### Hidden assumption 2: "Offline fallback = bundled JSON is enough."
Bundled JSON is simple, but it does not update when the backend adds/corrects questions unless the app is rebuilt. For a medical exam where answers can be challenged, stale content is a liability. We may need a lightweight cache-invalidation strategy.

### Hidden assumption 3: "StatefulWidget + services scales fine for v1."
The nursing module has cross-screen state: attempts, capability map, language preference, pending sync. Passing this through constructors will get messy quickly. Even for v1, a simple `ChangeNotifier` service might be cleaner than pure `setState`.

### Hidden assumption 4: "Widget tests are enough without running Flutter."
Without Flutter SDK in this environment, I cannot verify that my code compiles. Writing more code based on untested assumptions increases the risk of a cascade of compile errors when the user runs `flutter build`.

### Hidden assumption 5: "The backend endpoints already do exactly what the Flutter app needs."
I need to verify the actual API contracts. For example, does `/api/nursing/analyze` accept a list of `Attempt` objects exactly as I plan to serialize them? Does `/api/nursing/pdf` return HTML string or a file?

### Hidden assumption 6: "80 questions scrolled linearly is acceptable."
Adult test-takers may need to mark questions for review, skip hard ones, and return later. A linear scroll without navigation or flagging may cause real exam-anxiety.

### Hidden assumption 7: "Medical content liability is covered by 'Report question'."
A report button is reactive. We also need proactive disclaimers, clear source attribution, and possibly a "Not a substitute for professional training" statement.

### Hidden assumption 8: "Telugu UI labels are sufficient language support."
The exam is English-only, but explanations might be easier to understand in Telugu. Should we support bilingual explanations? What about text-to-speech for users with low literacy?

---

## Part 2: Self-Interview

**Q: Why not start with Riverpod or Bloc despite the existing codebase using StatefulWidget?**
A: To minimize dependencies and stay consistent. But consistency with a pattern that does not fit the feature is false economy. Nursing state crosses screens. A lightweight `NursingSessionController` extending `ChangeNotifier` would add zero new dependencies (Flutter provides it) and dramatically simplify the code.

**Q: Is bundled JSON really offline-first, or just offline-fallback?**
A: It is offline-fallback. True offline-first would cache server responses and sync bi-directionally. For v1, fallback is acceptable because the question bank is read-only. But we must document the difference and plan v2 sync.

**Q: What happens if the user's mother opens the app and has never used a smartphone for studying before?**
A: She needs onboarding: what the app does, how to practice, what the mock test simulates, and how to report errors. The current plan skips onboarding.

**Q: What if the 80-question mock test crashes because we load all 80 questions into memory at once?**
A: 80 question objects is small (~200 KB), but we should still use `ListView.builder` and avoid rebuilding all cards on every selection. We should also consider pagination or page-by-page mode for v1.5.

**Q: How do we know the bundled JSON stays in sync with the backend seed bank?**
A: We don't unless we automate the copy in `scripts/deploy.sh` or a Makefile. The plan should include a build script.

**Q: What about app store policies? Can we call this a "medical" or "exam prep" app?**
A: We should avoid claiming medical authority. Position it as "exam preparation" with disclaimers. This affects app store metadata and in-app copy.

**Q: Have I accounted for the fact that Flutter widget tests cannot catch all navigation/PopScope issues?**
A: No. `PopScope` behavior depends on the platform and route. Manual verification on a real Android device is essential.

**Q: Is the PDF export feature actually useful, or is it feature bloat?**
A: The web module has it, so parity is reasonable. But on mobile, copying HTML to clipboard is clunky. We should consider generating a plain-text summary instead of HTML, or defer PDF export to v1.5.

**Q: What about analytics and crash reporting?**
A: The plan has a session logger but no crash/analytics tool. For v1, manual error display + structured session logs are enough. For production, we need Firebase Crashlytics or Sentry, but that adds dependencies and privacy considerations.

**Q: What if the user has an older Android phone with limited RAM?**
A: We should avoid heavy widgets, large images, and unnecessary rebuilds. The bundled JSON should not be loaded into memory globally; load it lazily per screen.

---

## Part 3: Research Findings

### 3.1 Zero-dependency state management with ChangeNotifier

`ChangeNotifier` is part of `flutter:foundation` and does not require Provider or any external package [^1]. It can be used inside a `StatefulWidget` via `addListener(() => setState(() {}))` or passed down the tree via constructor. This gives us:
- Centralized quiz/session state without adding dependencies.
- Testability as a plain Dart class.
- A clean migration path to Provider/Riverpod later if needed.

### 3.2 Indian exam-prep app patterns

Leading Indian exam-prep apps (Testbook, Adda247, Gradeup) emphasize:
- Large mock-test libraries with detailed analytics [^2].
- Regional language support (Hindi + others) [^2].
- Clean, focused test-taking interface [^2].
- Performance tracking and rank prediction [^2].

Implication: Nursing v1 should prioritize mock-test analytics and clean navigation over gamification.

### 3.3 Medical / liability disclaimers

Standard practice for educational/medical-adjacent apps is to include:
- "For educational purposes only."
- "Not medical advice, diagnosis, or treatment."
- "Not a substitute for professional training or official syllabus."
- Limitation of liability clause [^3].

### 3.4 Onboarding for older / less tech-savvy adults

Best practices [^4][^5]:
- Keep onboarding under 60 seconds.
- One screen per concept.
- Use video tutorials where possible.
- Provide contextual help, not dense manuals.
- Allow skip.
- Show core value early.

### 3.5 Bilingual UI

Multilingual UI principles [^6]:
- Let users choose language explicitly.
- Use locale names, not flags.
- Plan for text expansion (e.g., Telugu may be longer than English).
- Use UTF-8 encoding.

### 3.6 Separate app vs module

Three migration strategies for adding Flutter to existing apps [^7]:
1. Add Flutter module to native app.
2. Add native parts to Flutter project.
3. Complete rewrite.

For Dr. Math, nursing is already inside the Flutter project as a feature. The pragmatic choice is to keep it as a clearly branded module within MathWise, with a future option to extract into a separate "Dr. Math Nursing" app if the user wants.

### 3.7 Backend API contracts verified

By reading `web/routers/nursing.py`:
- `GET /api/nursing/topics` → `{subjects, topics_by_subject, counts}`.
- `GET /api/nursing/questions?subject_id=&topic_id=...` → list of questions.
- `POST /api/nursing/diagnostic/start` body `{num_questions: int}` → `{questions: [...]}`.
- `POST /api/nursing/mock/start?pattern_key=...` → `{pattern_key, total_questions, questions: [...]}`.
- `POST /api/nursing/analyze` body `[Attempt, ...]` → `{subject_capabilities, topic_capabilities, dimension_capabilities}`.
- `POST /api/nursing/pdf` body `{attempts: [...], top_n: int}` → HTML string.
- `POST /api/nursing/report` body `{question_id, reason, user_id?}` → `{status, report}`.

### 3.8 Seed bank location and structure

The seed bank is at `output/nursing_staff_nurse_output.json` with 130 questions. Each question has: `id`, `subject_id`, `topic_id`, `concept_tag`, `difficulty`, `cognitive_level`, `context`, `format`, `question`, `options`, `correct_answer`, `explanation`, `source`, `verification_status`, `verified_by`, `last_reviewed`. This matches the existing `NursingQuestion` model.

---

## Part 4: New Decisions and Plan Changes

### Decision 1: Add a `NursingSessionController` using `ChangeNotifier`

Create `lib/features/nursing/controllers/nursing_session_controller.dart` extending `ChangeNotifier`. It will hold:
- Current quiz mode, question list, current index.
- Selected answers map.
- Timer state.
- Attempts list.
- Loading/error states.

This is passed into screens via constructor (no Provider dependency). This solves cross-screen state without adding packages.

### Decision 2: Generate bundled JSON from actual seed bank

Create a build script `scripts/generate_nursing_flutter_assets.sh` that copies `output/nursing_staff_nurse_output.json` to `mathwise_build/assets/nursing/nursing_seed_questions.json` and strips any non-essential metadata to reduce size.

### Decision 3: Add a Disclaimer screen

Add `lib/features/nursing/screens/nursing_disclaimer_screen.dart` shown on first launch. Content: educational purpose only, not medical advice, verify with official syllabus. User must tap "I understand" to proceed.

### Decision 4: Add a simple onboarding flow

Add `lib/features/nursing/screens/nursing_onboarding_screen.dart` with 2–3 swipeable cards:
1. "Practice by subject" with illustration.
2. "Take a full mock test" with timer info.
3. "Review weak areas" with capability map preview.

Each card has one message and a Next/Skip button.

### Decision 5: Enhance mock test with review/navigation

In the mock test, add:
- "Mark for review" toggle per question.
- Bottom-sheet question grid (v1, not deferred) so users can jump to any question.
- Summary before submit showing answered/unanswered/marked counts.

This addresses exam-anxiety and matches leading exam-prep apps.

### Decision 6: Support bilingual explanations via glossary, not separate text

For v1, keep question text English-only. Use the existing glossary tooltip for key Telugu terms. Do not add separate Telugu explanations yet; that requires content generation and review.

### Decision 7: Position as "exam preparation", not medical advice

All copy uses "exam preparation" and "practice". Disclaimer screen clarifies educational purpose.

---

## Part 5: Remaining Unknowns

1. How will the user actually run and verify builds? Need their Flutter version.
2. Should we add Firebase Crashlytics for v1.5 or v2?
3. What is the exact Telugu translation workflow for UI labels?
4. Should the nursing module have its own app icon/launcher if kept inside MathWise?

## References

[^1]: Flutter Docs. *Simple app state management*. https://docs.flutter.dev/data-and-backend/state-mgmt/simple
[^2]: TryReadable (2026). *Testbook vs Adda247 vs Gradeup best app for SSC exam preparation*. https://www.tryreadable.ai/analysis/testbook-vs-adda247-vs-gradeup-best-app-for-ssc-exam-preparation
[^3]: Routine Impact. *Medical & Liability Disclaimer*. https://www.routineimpact.com/disclaimer
[^4]: TechAhead (2026). *19 Mobile App Onboarding Best Practices and Examples*. https://www.techaheadcorp.com/blog/19-mobile-app-onboarding-best-practices-examples/
[^5]: UXCam (2026). *8 Mobile App Onboarding Best Practices*. https://uxcam.com/blog/better-mobile-onboarding/
[^6]: Phrase (2025). *7 Key UI Design Principles for Multilingual Apps*. https://phrase.com/blog/posts/ui-design-principles/
[^7]: MobiDev (2026). *Flutter App Development Guide 2026: Challenges & Best Practices*. https://mobidev.biz/blog/flutter-app-development
