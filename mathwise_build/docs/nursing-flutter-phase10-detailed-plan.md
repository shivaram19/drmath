# MathWise Nursing Flutter Module — Phase 10 Fine-Grained Execution Plan

**Date:** 2026-06-28  
**Scope:** Turn the Round 6 strategic decisions into a sequenced, gated, persona-reviewed engineering plan.  
**Governance:** This plan is written under the Research-First Covenant and the Council of Ten consensus protocol inherited from `voice-revenge-vizuara-ai/AGENTS.md` and this repo's `AGENTS.md` [^1][^2]. Every phase below is a Proposal that must pass the 10-persona filter before code is written.

---

## 0. How to Use This Plan

1. **Do not write code for any phase until its Proposal has been approved by the Council of Ten and the required ADR(s) exist.**
2. Each phase contains a `PROPOSAL`, `RISK LEVEL`, `COUNCIL DELIBERATION` template, `DECISION`, `ADR(s)`, `GRANULAR TASKS`, and `GATE`.
3. Before starting a phase, copy the Council table into a decision log (`docs/decisions/DECISION-YYYYMMDD-NNN-phase.md`), fill in each persona's stance, and resolve any blocking concerns.
4. All citations are numbered and listed at the end of this document.

---

## Council of Ten — Top-Level Review of Phase 10

**PROPOSAL:** Execute the Round 6 revised Phase 10 backlog in the order listed below: validate channel/value proposition first, then harden the native build, then add vernacular/UX/habit features, then observability/CI/CD.

**RATIONALE:** Round 6 showed that engineering optimization (APK size, release builds) is wasted if the target learner cannot discover, trust, or habitually use the app. The new order front-loads user-validation and compliance work.

**RISK LEVEL:** High (multiple architectural decisions, legal exposure under DPDPA, product-strategy pivot).

### Council Deliberation

| Persona | Stance | Key Point |
|---|---|---|
| Research Scientist | CONCERN | The PWA/channel decision needs user data, not just industry benchmarks. Propose a problem interview before ADR-019 is finalized. |
| First-Principles Engineer | ENDORSE | The atomic user need is daily practice on an existing device; the plan derives channel choices from that need. |
| Distributed Systems Architect | CONCERN | Adding a web/PWA path duplicates deployment surfaces. Need a single origin/edge story (nginx + CDN) to avoid operational sprawl. |
| Infrastructure-First SRE | ENDORSE | CI/CD and observability are explicitly included. But crash reporting must be opt-in to respect privacy. |
| Diagnostic Problem-Solver | ENDORSE | Root-cause ordering is correct: build failure and overflow are symptoms; channel/trust fit is the deeper disease. |
| Ethical Technologist | BLOCK | DPDPA notice/consent and content-trust mechanisms cannot be deferred. They must precede any public link/share. |
| Resource Strategist | CONCERN | PWA + native doubles maintenance. Need a clear "web-first, native-for-repeat-users" scope boundary. |
| Curious Explorer | ENDORSE | The problem interview and PWA landing page are cheap experiments that surface unknown unknowns. |
| Clarity-Driven Communicator | BLOCK | ADR-019, ADR-020, and ADR-021 must exist before Phase 10 code begins. |
| Inner-Self Guided Builder | ENDORSE | This plan serves the learner's real constraints (time, language, trust) rather than the builder's stack preferences. |

### Resolution

- **BLOCK 1 (Ethical Technologist):** Privacy notice and consent flow (Phase 10.2) must be completed before any public URL or share hook is enabled.
- **BLOCK 2 (Clarity-Driven Communicator):** Draft ADR-019 (distribution), ADR-020 (privacy/consent), and ADR-021 (localization) before the first engineering commit of Phase 10.
- **CONCERN 1 (Research Scientist):** Embed a problem interview into Phase 10.16; its findings can revise ADR-019 before finalization.
- **CONCERN 2 (Distributed Systems Architect):** The PWA landing page must be served from the same `drmath.trelolabs.com` origin and reuse the existing nginx/static infra.
- **CONCERN 3 (Resource Strategist):** PWA v1 is scoped to a single-page daily quiz; full feature parity is explicitly out of scope.

**DECISION:** Approved, subject to writing ADR-019, ADR-020, and ADR-021, and completing Phase 10.2 before any public distribution.

---

## Phase 10.1 — Define Value Proposition & Ship a Lightweight Web/PWA Landing Quiz

**PROPOSAL:** Create a shareable web page at `https://drmath.trelolabs.com/nursing/` that loads a 5-question daily quiz without requiring an app install. It will be a static HTML/JS shell that fetches questions from the existing `/api/nursing/questions` endpoint or uses a small embedded fallback JSON.

**RATIONALE:** Bharat users are app-install-averse and storage-constrained; a zero-install quiz is the fastest way to validate demand and collect learner feedback before investing further in native APK optimization [^3][^4].

**RISK LEVEL:** Medium

### Council Deliberation

| Persona | Stance | Key Point |
|---|---|---|
| Research Scientist | ENDORSE | PWA engagement benchmarks (Twitter Lite, Starbucks) are well documented [^3][^4]. |
| First-Principles Engineer | ENDORSE | The atomic action is answering a question; the web path preserves that action with lowest friction. |
| Distributed Systems Architect | CONCERN | Need CORS, caching, and offline-fallback policy for the API call. |
| Infrastructure-First SRE | CONCERN | Need basic metrics: page loads, quiz starts, completion rate. |
| Diagnostic Problem-Solver | ENDORSE | If nobody opens the web quiz, we have learned the channel hypothesis is wrong before building more native code. |
| Ethical Technologist | BLOCK | Cannot enable public data collection without privacy notice and consent (Phase 10.2). |
| Resource Strategist | ENDORSE | A static landing page is cheap; it tests demand before Play Store investment. |
| Curious Explorer | ENDORSE | This is the highest-leverage experiment in Phase 10. |
| Clarity-Driven Communicator | BLOCK | Requires ADR-019 before code. |
| Inner-Self Guided Builder | ENDORSE | Meets the user on the device she already uses. |

**DECISION:** Approved, contingent on ADR-019 and Phase 10.2 privacy notice/consent.

### ADR(s)
- **ADR-019:** Native vs. PWA-first distribution strategy for MathWise Nursing.

### Granular Tasks
1. **Research & design**
   - 1.1 Read existing `/api/nursing/questions` contract and confirm CORS headers on `drmath.trelolabs.com`.
   - 1.2 Decide landing-page copy in English + Telugu (conversational, not formal).
   - 1.3 Create a low-fidelity wireframe (text description sufficient) with hero, language toggle, "Start 5 questions" CTA, and result card.
2. **Static asset setup**
   - 2.1 Create `web/static/nursing/index.html`.
   - 2.2 Add `web/static/nursing/app.js` (vanilla JS, no build step).
   - 2.3 Add `web/static/nursing/styles.css` (mobile-first, 44px+ touch targets).
   - 2.4 Create a fallback JSON `web/static/nursing/daily.json` with 5 questions (syllabus-audited later in Phase 10.6).
3. **PWA manifest & service worker**
   - 3.1 Add `manifest.json` with `start_url`, `display: standalone`, icons (reuse MathWise icon).
   - 3.2 Add a minimal service worker that caches the shell and fallback JSON.
   - 3.3 Register the service worker only after the user taps "Add to home screen" or starts a quiz.
4. **API integration**
   - 4.1 `fetch('/api/nursing/questions?mode=daily&limit=5')`.
   - 4.2 On network failure, serve `daily.json` from cache.
   - 4.3 Render one question at a time; show immediate feedback; compute a simple score.
5. **Share hook**
   - 5.1 Add a "Share with a friend" button using the Web Share API, falling back to WhatsApp `https://wa.me/?text=...`.
6. **Nginx routing**
   - 6.1 Add a location block in `nginx.http.conf` (and `nginx.ssl.conf`) to serve `/nursing/` from `web/static/nursing/`.
   - 6.2 Ensure `/nursing/` works with and without trailing slash.
7. **Validation**
   - 7.1 Open `https://drmath.trelolabs.com/nursing/` on a budget Android phone and Chrome.
   - 7.2 Verify offline reload serves cached quiz.
   - 7.3 Verify Web Share or WhatsApp fallback opens.

### Acceptance Criteria / Gate
- [ ] `curl https://drmath.trelolabs.com/nursing/` returns 200 with HTML.
- [ ] Page loads in under 3s on a simulated 3G connection.
- [ ] Quiz can be completed offline using the fallback JSON.
- [ ] Share button generates a working link.
- [ ] Lighthouse PWA audit score ≥ 80.
- [ ] No analytics or tracking scripts are present until Phase 10.2 consent is added.

### Files to Create/Modify
- Create: `web/static/nursing/index.html`, `web/static/nursing/app.js`, `web/static/nursing/styles.css`, `web/static/nursing/manifest.json`, `web/static/nursing/sw.js`, `web/static/nursing/daily.json`
- Modify: `nginx.http.conf`, `nginx.ssl.conf`

---

## Phase 10.2 — Add DPDPA-Compliant Privacy Notice & Consent Flow

**PROPOSAL:** Before collecting any personal data (quiz answers, device info, crash logs), show a standalone, plain-language privacy notice at first launch in both English and Telugu, and obtain explicit consent. Provide a settings screen where consent can be reviewed and withdrawn.

**RATIONALE:** India's DPDPA, 2023 requires free, specific, informed, and unconditional consent; notices must be clear, standalone, and available in English/Eighth Schedule languages [^5][^6]. Edtech platforms that over-collect data risk penalties up to ₹250 crore and erode user trust [^6][^7].

**RISK LEVEL:** Critical

### Council Deliberation

| Persona | Stance | Key Point |
|---|---|---|
| Research Scientist | ENDORSE | DPDPA text and draft rules are authoritative sources [^5][^6]. |
| First-Principles Engineer | ENDORSE | The atomic requirement is user autonomy; ask before storing. |
| Distributed Systems Architect | CONCERN | Consent state must be durable, queryable, and versioned if the notice changes. |
| Infrastructure-First SRE | CONCERN | Need audit log of consent changes for incident response. |
| Diagnostic Problem-Solver | ENDORSE | Root cause of privacy risk is collection without consent; this fixes it. |
| Ethical Technologist | ENDORSE | Respects the learner and builds trust. |
| Resource Strategist | ENDORSE | Cheap insurance against large regulatory penalties. |
| Curious Explorer | CONCERN | Need to measure consent opt-in rate to detect overly broad language. |
| Clarity-Driven Communicator | BLOCK | Requires ADR-020 before code. |
| Inner-Self Guided Builder | ENDORSE | The right thing to do, even if it adds friction. |

**DECISION:** Approved, contingent on ADR-020.

### ADR(s)
- **ADR-020:** Privacy notice, consent, and data-minimization policy for MathWise Nursing.

### Granular Tasks
1. **Legal/policy drafting**
   - 1.1 Draft `mathwise_build/docs/privacy-policy.md` and a user-facing notice.
   - 1.2 Translate notice into Telugu (conversational, not formal legal Telugu).
   - 1.3 List every data item collected, purpose, retention period, and deletion mechanism.
2. **Storage for consent**
   - 2.1 Add keys to `NursingStorageService`:
     - `privacyNoticeAcceptedAt` (ISO timestamp)
     - `privacyNoticeVersion` (string)
     - `analyticsConsent` (bool)
     - `crashReportingConsent` (bool)
   - 2.2 Expose `Future<bool> hasAcceptedCurrentNotice(String version)`.
3. **Flutter UI**
   - 3.1 Create `NursingPrivacyNoticeScreen`.
   - 3.2 Show it from `NursingEntryScreen` before routing to disclaimer/home if not accepted.
   - 3.3 Use two toggles: (a) required — accept notice to use app; (b) optional — allow crash/analytics.
   - 3.4 Add "Read full policy" link that opens a web view or external browser to `/privacy`.
4. **Settings integration**
   - 4.1 Add a "Privacy & Data" tile in `NursingSettingsScreen`.
   - 4.2 Allow re-open notice and withdraw optional consent.
   - 4.3 On withdrawal, disable analytics/crash reporting and clear queued events.
5. **Web landing parity**
   - 5.1 Add the same notice as a modal in `web/static/nursing/index.html` before storing any answers.
   - 5.2 Store consent in `localStorage`; do not call the API until accepted.
6. **Backend/log audit**
   - 6.1 Ensure no server-side logging stores PII without purpose limitation.
   - 6.2 Document data retention schedule in `docs/`.

### Acceptance Criteria / Gate
- [ ] First launch shows privacy notice before any network call.
- [ ] User cannot proceed without accepting required notice.
- [ ] Optional analytics/crash consent is off by default and can be toggled later.
- [ ] Settings screen shows current consent state and policy version.
- [ ] Withdrawing optional consent disables the relevant SDKs.
- [ ] Notice is available in English and Telugu.

### Files to Create/Modify
- Create: `mathwise_build/docs/privacy-policy.md`, `lib/features/nursing/screens/nursing_privacy_notice_screen.dart`
- Modify: `lib/features/nursing/services/nursing_storage_service.dart`, `lib/features/nursing/screens/nursing_entry_screen.dart`, `lib/features/nursing/screens/nursing_settings_screen.dart`, `web/static/nursing/index.html`, `web/static/nursing/app.js`

---

## Phase 10.3 — Fix and Pin Java/Gradle/AGP Toolchain

**PROPOSAL:** Make `flutter build apk --release` and `flutter build appbundle --release` succeed deterministically by pinning Java 17, Gradle 8.x, and AGP 8.x, and document them in an ADR and CI matrix.

**RATIONALE:** The release build currently fails with `Unsupported class file major version 65` during JetifyTransform of `bcprov-jdk18on-1.80.jar` [^8]. A reproducible toolchain is prerequisite to size analysis and trustworthy CI artifacts.

**RISK LEVEL:** High

### Council Deliberation

| Persona | Stance | Key Point |
|---|---|---|
| Research Scientist | ENDORSE | Flutter's own migration guide documents compatible Java/Gradle/AGP triples [^8]. |
| First-Principles Engineer | ENDORSE | Deterministic builds require deterministic inputs; pinning is the fix. |
| Distributed Systems Architect | ENDORSE | CI matrix must match local dev exactly. |
| Infrastructure-First SRE | ENDORSE | Pinning prevents "works on my machine" incidents. |
| Diagnostic Problem-Solver | ENDORSE | Root cause is version skew; the fix is version pinning, not a one-off patch. |
| Ethical Technologist | ENDORSE | Reproducible builds are a trust signal. |
| Resource Strategist | CONCERN | Need to ensure CI runner supports the chosen Java version without custom images. |
| Curious Explorer | CONCERN | Test the chosen triple on a clean machine before CI commit. |
| Clarity-Driven Communicator | BLOCK | Requires ADR (can be folded into ADR-018 update or a new ADR-022). |
| Inner-Self Guided Builder | ENDORSE | Boring, well-understood technology is the right choice. |

**DECISION:** Approved, contingent on updating ADR-018 or creating ADR-022.

### ADR(s)
- **ADR-018 update or ADR-022:** Reproducible Android build toolchain for Flutter 3.27.

### Granular Tasks
1. **Survey current versions**
   - 1.1 Read `android/gradle/wrapper/gradle-wrapper.properties`.
   - 1.2 Read `android/app/build.gradle` AGP version.
   - 1.3 Read `android/settings.gradle` plugin versions.
   - 1.4 Run `flutter doctor -v` and record active Java version.
2. **Select target triple**
   - 2.1 Based on Flutter 3.27.0 docs: Java 17, Gradle 8.0.2+, AGP 8.1.0+ [^8].
   - 2.2 Verify `bcprov-jdk18on` compatibility with the chosen AGP/Gradle versions.
3. **Update Android project**
   - 3.1 Update `gradle-wrapper.properties` to Gradle 8.5 (or 8.7).
   - 3.2 Update `android/app/build.gradle` `compileSdkVersion`, `minSdkVersion`, `targetSdkVersion`.
   - 3.3 Update `android/settings.gradle` plugin versions.
   - 3.4 Update `android/build.gradle` if needed.
   - 3.5 Add `android/app/proguard-rules.pro` for release obfuscation (prep for size phase).
4. **Document local setup**
   - 4.1 Add `mathwise_build/.fvmrc` pinning Flutter 3.27.0 (already planned).
   - 4.2 Add `mathwise_build/android/README.md` with required Java/Gradle/AGP versions.
5. **CI verification**
   - 5.1 Add a GitHub Actions job (Phase 10.12) using `subosito/flutter-action@v2` with Flutter 3.27.0 and `setup-java@v4` with Java 17.
6. **Validation**
   - 6.1 Run `flutter clean && flutter pub get`.
   - 6.2 Run `flutter build apk --release`.
   - 6.3 Run `flutter build appbundle --release`.

### Acceptance Criteria / Gate
- [ ] `flutter build apk --release` succeeds on a clean checkout with Java 17.
- [ ] `flutter build appbundle --release` succeeds.
- [ ] CI job using the pinned versions produces the same result.
- [ ] Documented triple is committed to ADR-018/ADR-022.

### Files to Create/Modify
- Modify: `mathwise_build/android/gradle/wrapper/gradle-wrapper.properties`, `mathwise_build/android/app/build.gradle`, `mathwise_build/android/settings.gradle`, `mathwise_build/android/app/proguard-rules.pro`
- Create: `mathwise_build/android/README.md`, `mathwise_build/.fvmrc` (if not exists)

---

## Phase 10.4 — Establish 20 MB Release-APK Size Budget

**PROPOSAL:** Run `flutter build apk --analyze-size` on the release build, identify the top contributors, and apply `--split-per-abi`, ProGuard/R8, image/font pruning, and JSON lazy-loading until the per-ABI APK is ≤20 MB (ideally ≤15 MB).

**RATIONALE:** Bharat-first apps treat ~15 MB as a soft ceiling because users delete large apps to free space [^9]. The current debug APK is 104 MB and not representative; release analysis is needed before optimization.

**RISK LEVEL:** Medium

### Council Deliberation

| Persona | Stance | Key Point |
|---|---|---|
| Research Scientist | ENDORSE | Flutter docs provide the canonical size-analysis workflow [^10]. |
| First-Principles Engineer | ENDORSE | Smaller artifact = lower friction = more installs. |
| Distributed Systems Architect | CONCERN | Split-per-ABI means three APKs or one AAB; decide distribution policy. |
| Infrastructure-First SRE | ENDORSE | Size should be a CI metric. |
| Diagnostic Problem-Solver | ENDORSE | Must measure before cutting; otherwise we cut the wrong things. |
| Ethical Technologist | ENDORSE | Reduces data usage for low-bandwidth users. |
| Resource Strategist | CONCERN | AAB requires Play Store; direct APK hosting needs `--split-per-abi` + device ABI selection. |
| Curious Explorer | ENDORSE | Size analysis will reveal unexpected bloat. |
| Clarity-Driven Communicator | BLOCK | Requires ADR-018 update or ADR-023 for size budget. |
| Inner-Self Guided Builder | ENDORSE | Respects the user's storage constraints. |

**DECISION:** Approved, contingent on ADR-018 update or ADR-023.

### ADR(s)
- **ADR-018 update or ADR-023:** Release APK size budget and optimization strategy.

### Granular Tasks
1. **Baseline measurement**
   - 1.1 Run `flutter build apk --release --analyze-size`.
   - 1.2 Record total size, native libraries per ABI, asset sizes, and font/package contributions.
   - 1.3 Save JSON snapshot to `mathwise_build/docs/size-baseline.json`.
2. **Native library splitting**
   - 2.1 Build `flutter build apk --release --split-per-abi`.
   - 2.2 Record `app-arm64-v8a-release.apk`, `app-armeabi-v7a-release.apk`, `app-x86_64-release.apk` sizes.
3. **Asset audit**
   - 3.1 Check size of `assets/nursing/nursing_seed_questions.json`.
   - 3.2 If >300 KB, switch to lazy-load: ship subject index only, fetch questions on first use and persist in `SharedPreferences`/`sqflite`.
   - 3.3 Convert large PNG/JPEG assets to WebP.
   - 3.4 Audit `google_fonts` usage; subset or bundle only needed font weights.
4. **Code shrinking**
   - 4.1 Enable R8/ProGuard in `android/app/build.gradle`.
   - 4.2 Add keep rules for Dart-reflected classes and `NursingQuestion` deserialization.
5. **Dependency pruning**
   - 5.1 Review `pubspec.yaml`; remove unused packages.
   - 5.2 Evaluate whether `cached_network_image` and `shimmer` are justified for v1.
6. **Distribution policy**
   - 6.1 Decide: AAB for Play Store, split APKs for direct nginx hosting, or both.
   - 6.2 Update `scripts/deploy.sh` to copy the correct artifact and record ABI.
7. **CI metric**
   - 7.1 Add a CI step that fails the build if the release APK exceeds 20 MB.

### Acceptance Criteria / Gate
- [ ] `flutter build apk --release --split-per-abi` produces per-ABI APKs ≤20 MB.
- [ ] Size analysis JSON is committed to `docs/`.
- [ ] CI fails if any APK exceeds the budget.
- [ ] App still passes all widget tests after obfuscation.

### Files to Create/Modify
- Create: `mathwise_build/docs/size-baseline.json`, `mathwise_build/docs/size-reduction-plan.md`
- Modify: `mathwise_build/android/app/build.gradle`, `mathwise_build/pubspec.yaml`, `mathwise_build/scripts/deploy.sh`

---

## Phase 10.5 — Fix `HomeScreen` Nursing Card Overflows

**PROPOSAL:** Refactor `HomeScreen._buildNursingCard` (and other summary cards) to use `Flexible`/`Expanded` text, `FittedBox`/ellipsis, and `Wrap` or `Column` layouts so the card never overflows on screens ≥320 dp wide. Add a widget test at 360×640.

**RATIONALE:** The nursing card is the front door. If it overflows on narrow budget phones, users may never enter the module [^11].

**RISK LEVEL:** Low

### Council Deliberation

| Persona | Stance | Key Point |
|---|---|---|
| Research Scientist | ENDORSE | Material Design responsive layouts are canonical. |
| First-Principles Engineer | ENDORSE | Layout should adapt to available space, not assume a fixed width. |
| Distributed Systems Architect | ENDORSE | Stateless UI change. |
| Infrastructure-First SRE | ENDORSE | Widget test catches regression. |
| Diagnostic Problem-Solver | ENDORSE | Fixes the symptom (overflow) and the cause (fixed-width Row). |
| Ethical Technologist | ENDORSE | Accessibility: small screens are common in Bharat. |
| Resource Strategist | ENDORSE | Low cost, high user-acquisition impact. |
| Curious Explorer | ENDORSE | Add a visual regression test to learn if other cards break. |
| Clarity-Driven Communicator | ENDORSE | Document the 360 dp minimum supported width. |
| Inner-Self Guided Builder | ENDORSE | The user's first screen must not look broken. |

**DECISION:** Approved.

### ADR(s)
- None (UI fix; document in commit message and update completion plan).

### Granular Tasks
1. **Reproduce**
   - 1.1 Run `flutter test test/visual_screenshots_test.dart` and capture overflow dimensions.
2. **Refactor card layout**
   - 2.1 Replace fixed-width `Row` children with `Expanded`/`Flexible`.
   - 2.2 Wrap title/description in `Expanded(child: Text(..., overflow: TextOverflow.ellipsis, maxLines: 2))`.
   - 2.3 Use `Wrap` for action chips if multiple actions exist.
   - 2.4 Ensure the "Open" button has a minimum 48×48 dp tap target and does not force the row wider than the screen.
3. **Other cards**
   - 3.1 Apply the same pattern to any other summary cards in `HomeScreen` that overflow.
4. **Widget test**
   - 4.1 Add `test/features/home/home_screen_overflow_test.dart` with `tester.binding.window.physicalSizeTestValue = Size(360, 640) * tester.binding.window.devicePixelRatio`.
   - 4.2 Pump `HomeScreen`, tap nursing card, and assert no `FlutterError` of type overflow.
5. **Visual regression (optional)**
   - 5.1 Update or extend `visual_screenshots_test.dart` to render at 360 dp and compare golden.

### Acceptance Criteria / Gate
- [ ] `flutter test test/features/home/` passes at 360 dp width.
- [ ] `flutter test test/visual_screenshots_test.dart` no longer reports nursing-card overflow.
- [ ] Nursing card remains usable at 320 dp width.

### Files to Modify
- Modify: `mathwise_build/lib/features/home/home_screen.dart`
- Create: `mathwise_build/test/features/home/home_screen_overflow_test.dart`

---

## Phase 10.6 — Audit & Tag Nursing Seed Questions Against Real Syllabi

**PROPOSAL:** Compare `assets/nursing/nursing_seed_questions.json` against AIIMS NORCET, ESIC Nursing Officer, RRB Staff Nurse, and Telangana ANM/GNM syllabi. Tag each question with `examCategory`, `subject`, `topic`, and `cognitiveLevel`. Remove or relabel questions that do not map to a real exam topic.

**RATIONALE:** Nursing exam prep is high-stakes; learners need confidence that every question is syllabus-relevant. TaRL evidence shows that instruction matched to the learner's actual level produces large learning gains, but only if the content is valid [^12].

**RISK LEVEL:** Medium

### Council Deliberation

| Persona | Stance | Key Point |
|---|---|---|
| Research Scientist | ENDORSE | Syllabus documents and TaRL evidence are authoritative [^12][^13]. |
| First-Principles Engineer | ENDORSE | A question bank's value = coverage × validity. |
| Distributed Systems Architect | CONCERN | Tag schema changes affect API and storage; need migration path. |
| Infrastructure-First SRE | ENDORSE | Add a CI check that every new question has required tags. |
| Diagnostic Problem-Solver | ENDORSE | Root cause of low trust is unvalidated content. |
| Ethical Technologist | ENDORSE | Prevents misleading medical content. |
| Resource Strategist | CONCERN | Manual audit is labor-intensive; scope to top 2 target exams first. |
| Curious Explorer | ENDORSE | Audit will reveal gaps and duplication. |
| Clarity-Driven Communicator | BLOCK | Requires ADR-024 or update to ADR-016 (question review system). |
| Inner-Self Guided Builder | ENDORSE | Builds the trust that the learner's mother needs. |

**DECISION:** Approved, contingent on ADR-024/ADR-016 update.

### ADR(s)
- **ADR-024:** Nursing question taxonomy and syllabus-mapping policy.

### Granular Tasks
1. **Define taxonomy**
   - 1.1 Create `mathwise_build/docs/nursing-syllabus-taxonomy.md` listing subjects and topics for:
     - AIIMS NORCET
     - ESIC Nursing Officer
     - RRB Staff Nurse
     - Telangana ANM/GNM
   - 1.2 Define enums in Dart: `NursingSubject`, `NursingExamCategory`, `CognitiveLevel`.
2. **Schema update**
   - 2.1 Add fields to `NursingQuestion` JSON/Dart model:
     - `examCategory` (list of strings)
     - `subjectId`, `topicId`
     - `cognitiveLevel` (remember/understand/apply/analyze)
     - `source` (optional citation)
     - `reviewedAt` (ISO timestamp)
   - 2.2 Update `scripts/generate_nursing_flutter_assets.sh` to preserve tags.
3. **Audit process**
   - 3.1 Load `output/nursing_staff_nurse_output.json`.
   - 3.2 For each question, map to the closest syllabus topic or mark `UNMAPPED`.
   - 3.3 Flag questions with medically sensitive answers for expert review.
   - 3.4 Remove or quarantine questions that cannot be mapped.
4. **Expert review queue**
   - 4.1 Add a `reviewStatus` field: `pending`, `approved`, `rejected`.
   - 4.2 The report-question flow (existing) can set status to `pending`.
5. **Validation script**
   - 5.1 Create `scripts/validate_nursing_seed.py` that asserts:
     - Every question has required tags.
     - No `UNMAPPED` questions in production seed.
     - Cognitive levels are valid.
6. **CI gate**
   - 6.1 Run `scripts/validate_nursing_seed.py` in CI before Flutter build.

### Acceptance Criteria / Gate
- [ ] 100% of production seed questions have `subjectId`, `topicId`, `examCategory`, and `cognitiveLevel`.
- [ ] No unmapped medical questions remain in the seed.
- [ ] Validation script passes in CI.
- [ ] Flutter app loads the tagged JSON without parse errors.

### Files to Create/Modify
- Create: `mathwise_build/docs/nursing-syllabus-taxonomy.md`, `mathwise_build/scripts/validate_nursing_seed.py`
- Modify: `mathwise_build/lib/features/nursing/models/nursing_question.dart`, `mathwise_build/scripts/generate_nursing_flutter_assets.sh`, `mathwise_build/assets/nursing/nursing_seed_questions.json`

---

## Phase 10.7 — Implement Bilingual Localization + TTS Glossary

**PROPOSAL:** Replace the English-first UI with `flutter_localizations` ARB files for English and Telugu-English mixed copy, add a "read question aloud" TTS button, and add glossary tooltips for English medical terms. Avoid formal Telugu script for UI labels.

**RATIONALE:** 58% of Indian internet users use voice search weekly; low-literacy users engage more with voice and native-language content [^14][^15]. Formal Telugu translation can feel alien in a medical-exam context where English terms are standard.

**RISK LEVEL:** Medium

### Council Deliberation

| Persona | Stance | Key Point |
|---|---|---|
| Research Scientist | ENDORSE | Voice and vernacular engagement data are well documented [^14][^15]. |
| First-Principles Engineer | ENDORSE | The goal is comprehension, not literal translation. |
| Distributed Systems Architect | CONCERN | ARB + TTS increases asset size and platform-channel surface; test on both Android and web. |
| Infrastructure-First SRE | ENDORSE | Add a metric for TTS usage. |
| Diagnostic Problem-Solver | ENDORSE | Solves the root cause (language barrier) better than direct translation. |
| Ethical Technologist | ENDORSE | Accessibility and inclusion. |
| Resource Strategist | CONCERN | TTS adds a dependency (`flutter_tts`) with platform-specific behavior; need fallback. |
| Curious Explorer | ENDORSE | Test which users prefer TTS vs reading. |
| Clarity-Driven Communicator | BLOCK | Requires ADR-021. |
| Inner-Self Guided Builder | ENDORSE | Meets the mother where she is. |

**DECISION:** Approved, contingent on ADR-021.

### ADR(s)
- **ADR-021:** Vernacular-first localization strategy for MathWise Nursing.

### Granular Tasks
1. **ARB setup**
   - 1.1 Add `flutter_localizations` and `intl` dependencies.
   - 1.2 Create `lib/l10n/app_en.arb` and `lib/l10n/app_te.arb`.
   - 1.3 Add `MaterialApp.localizationsDelegates` and `supportedLocales`.
2. **Copy strategy**
   - 2.1 Use conversational Telugu-English mixed strings (e.g., "每日 5 questions practice చేద్దాం" patterns adapted for Telugu).
   - 2.2 Keep formal Telugu for disclaimer/privacy text only.
3. **High-friction screen translations**
   - 3.1 Translate: privacy notice, disclaimer, onboarding, nursing card, quiz, results, PDF preview, settings.
4. **TTS integration**
   - 4.1 Add `flutter_tts` dependency (TCO check: free, offline on device).
   - 4.2 Add a speaker icon to `QuestionCard` that reads the question stem and options.
   - 4.3 Handle TTS unavailable (web, older devices) by hiding the icon.
5. **Glossary tooltips**
   - 5.1 Create `GlossaryService` with a map of English medical term → Telugu explanation.
   - 5.2 Wrap medical terms in `QuestionCard` with `Tooltip` or `InkWell` showing the Telugu explanation.
6. **Language persistence**
   - 6.1 Store selected locale in `NursingStorageService`.
   - 6.2 Apply locale on app start.
7. **Tests**
   - 7.1 Add widget tests that pump with `Locale('te')` and assert translated strings appear.
   - 7.2 Test TTS button visibility with mocked `FlutterTts`.

### Acceptance Criteria / Gate
- [ ] App launches in Telugu-English mixed mode without overflow.
- [ ] All nursing screens show translated strings.
- [ ] TTS button reads a sample question on Android.
- [ ] Glossary tooltip shows Telugu explanation for at least 20 medical terms.
- [ ] Widget tests pass for both `en` and `te` locales.

### Files to Create/Modify
- Create: `mathwise_build/lib/l10n/app_en.arb`, `mathwise_build/lib/l10n/app_te.arb`, `mathwise_build/lib/features/nursing/services/glossary_service.dart`
- Modify: `mathwise_build/pubspec.yaml`, `mathwise_build/lib/main.dart`, `mathwise_build/lib/features/nursing/widgets/question_card.dart`, `mathwise_build/lib/features/nursing/services/nursing_storage_service.dart`

---

## Phase 10.8 — Add Micro-Sessions & Resume-After-Interruption

**PROPOSAL:** Allow quiz lengths of 5, 10, 20, or 80 questions. Persist progress after every answer and on timer tick. On app restart or screen re-entry, offer a one-tap resume dialog if an in-flight session exists.

**RATIONALE:** Adult women in India face severe time poverty and household interruptions; uninterrupted 30–60 minute sessions are unrealistic [^16][^17]. Auto-save prevents trust-breaking data loss [^18].

**RISK LEVEL:** Medium

### Council Deliberation

| Persona | Stance | Key Point |
|---|---|---|
| Research Scientist | ENDORSE | Time-use research shows women have less leisure/learning time [^16][^17]. |
| First-Principles Engineer | ENDORSE | The atomic promise is "practice when you can"; resume preserves that promise. |
| Distributed Systems Architect | CONCERN | In-flight state must be schema-versioned to survive model changes. |
| Infrastructure-First SRE | ENDORSE | Add metrics: session resume rate, abandonment rate. |
| Diagnostic Problem-Solver | ENDORSE | Root cause of churn is not lack of features but lack of fit to fragmented time. |
| Ethical Technologist | ENDORSE | Reduces stress for caregivers. |
| Resource Strategist | ENDORSE | Reuses existing `SharedPreferences`; no new dependency. |
| Curious Explorer | ENDORSE | Experiment: default to 10 questions and measure completion rate. |
| Clarity-Driven Communicator | ENDORSE | Document the resume behavior in the manual QA checklist. |
| Inner-Self Guided Builder | ENDORSE | The right feature for the user's reality. |

**DECISION:** Approved.

### ADR(s)
- None (behavioral feature; document in commit message).

### Granular Tasks
1. **Quiz length selector**
   - 1.1 Add `questionCount` parameter to diagnostic/practice start.
   - 1.2 Show a bottom sheet or dialog on `NursingHomeScreen` before starting a session.
2. **Persist progress**
   - 2.1 In `NursingSessionController`, after each answer and timer tick, write to `SharedPreferences`:
     - `nursing_inflight_mode`
     - `nursing_inflight_subject_id`, `nursing_inflight_topic_id`
     - `nursing_inflight_index`
     - `nursing_inflight_answers` (JSON map)
     - `nursing_inflight_remaining_seconds`
     - `nursing_inflight_questions` (serialized list)
     - `nursing_inflight_updated_at`
3. **Resume dialog**
   - 3.1 On entering `NursingQuizScreen`, check for in-flight session.
   - 3.2 If found and params match, show `AlertDialog`: "You have 7 questions remaining. Resume or start new?"
   - 3.3 If params differ, discard old session silently (or warn).
4. **Expiration**
   - 4.1 Discard in-flight sessions older than 7 days to avoid stale state.
5. **Tests**
   - 5.1 Unit test `NursingSessionController` save/restore.
   - 5.2 Widget test resume dialog.

### Acceptance Criteria / Gate
- [ ] User can choose 5/10/20/80 question sessions.
- [ ] Killing the app mid-quiz and reopening offers resume.
- [ ] Resume restores question index, selected answers, and timer.
- [ ] Sessions older than 7 days are ignored.

### Files to Modify
- Modify: `mathwise_build/lib/features/nursing/controllers/nursing_session_controller.dart`, `mathwise_build/lib/features/nursing/screens/nursing_quiz_screen.dart`, `mathwise_build/lib/features/nursing/screens/nursing_home_screen.dart`, `mathwise_build/lib/features/nursing/services/nursing_storage_service.dart`

---

## Phase 10.9 — Add Habit Prompts & Tiny-Win Celebrations

**PROPOSAL:** Add a daily reminder anchored to a user-chosen routine, celebrate small wins ("5 questions done today"), and show a gentle re-engagement nudge after low-activity periods. Avoid shame or streak-loss pressure.

**RATIONALE:** BJ Fogg's behavior model shows habits form when motivation, ability, and a prompt converge; tiny habits anchored to existing routines and immediate celebration wire behavior [^19][^20]. Mobile app retention is brutal without early habit formation [^21].

**RISK LEVEL:** Low

### Council Deliberation

| Persona | Stance | Key Point |
|---|---|---|
| Research Scientist | ENDORSE | Fogg's model and retention benchmarks are canonical [^19][^20][^21]. |
| First-Principles Engineer | ENDORSE | Habit = trigger + action + reward; this phase adds all three. |
| Distributed Systems Architect | CONCERN | Local notifications require platform permissions and careful scheduling. |
| Infrastructure-First SRE | ENDORSE | Track notification grant rate and re-engagement lift. |
| Diagnostic Problem-Solver | ENDORSE | Root cause of low retention is missing habit loop, not missing features. |
| Ethical Technologist | BLOCK | Notifications must be opt-in and non-manipulative; no guilt messaging. |
| Resource Strategist | CONCERN | `flutter_local_notifications` adds a dependency; evaluate TCO. |
| Curious Explorer | ENDORSE | A/B test default reminder time vs user-chosen anchor. |
| Clarity-Driven Communicator | ENDORSE | Document tone guidelines (celebration, not pressure). |
| Inner-Self Guided Builder | ENDORSE | Supports the learner without exploiting her anxiety. |

**DECISION:** Approved, contingent on notifications being opt-in and celebration-focused.

### ADR(s)
- None (behavioral UX; document tone in design notes).

### Granular Tasks
1. **Permission flow**
   - 1.1 Add `flutter_local_notifications` (or use system alarm if minimizing deps).
   - 1.2 Request notification permission only after the user opts in on settings screen.
2. **Reminder setup**
   - 2.1 In `NursingSettingsScreen`, add "Daily reminder" tile.
   - 2.2 Let user pick a time and anchor label: "After morning tea", "After lunch", "After putting kids to bed".
   - 2.3 Schedule a daily local notification with gentle copy: "Time for a quick nursing practice. Just 5 questions."
3. **Tiny-win celebration**
   - 3.1 After finishing any quiz, show a `SnackBar` or animated badge: "Great! You practiced today."
   - 3.2 On `NursingHomeScreen`, show a "Today's practice" indicator if the user completed a session today.
4. **Re-engagement nudge**
   - 4.1 If no session for 3 days, show a non-blocking card: "Start with just 5 questions when you have a minute."
5. **Tests**
   - 5.1 Unit test notification scheduling logic.
   - 5.2 Widget test settings toggle and celebration UI.

### Acceptance Criteria / Gate
- [ ] Notifications are opt-in and can be disabled.
- [ ] Celebration appears after every completed session.
- [ ] Re-engagement card appears after 3 days of inactivity.
- [ ] No guilt or streak-loss language anywhere.

### Files to Modify
- Modify: `mathwise_build/lib/features/nursing/screens/nursing_settings_screen.dart`, `mathwise_build/lib/features/nursing/screens/nursing_home_screen.dart`, `mathwise_build/lib/features/nursing/screens/nursing_results_screen.dart`, `mathwise_build/lib/features/nursing/services/nursing_storage_service.dart`
- Create: `mathwise_build/lib/features/nursing/services/nursing_reminder_service.dart`

---

## Phase 10.10 — Make PDF Generation Offline-First

**PROPOSAL:** Persist pending PDF generation requests in `NursingStorageService`. When connectivity returns, retry the queue. Show a "PDF queued" state in the UI.

**RATIONALE:** `NursingPdfScreen` currently shows an offline snackbar but loses the user's request. Offline-first systems treat local storage as the source of truth and use an outbox pattern for every mutation [^22].

**RISK LEVEL:** Medium

### Council Deliberation

| Persona | Stance | Key Point |
|---|---|---|
| Research Scientist | ENDORSE | Offline-first outbox pattern is well established [^22]. |
| First-Principles Engineer | ENDORSE | User intent must survive network failure. |
| Distributed Systems Architect | CONCERN | Queue can grow; need idempotency and retry caps. |
| Infrastructure-First SRE | ENDORSE | Add metric: pdf_queue_depth. |
| Diagnostic Problem-Solver | ENDORSE | Root cause is request loss; the fix is persistence. |
| Ethical Technologist | ENDORSE | Respects users with intermittent connectivity. |
| Resource Strategist | ENDORSE | Uses existing storage; no new dependency for v1. |
| Curious Explorer | ENDORSE | Measure how often the queue is non-empty. |
| Clarity-Driven Communicator | BLOCK | Requires ADR-023 if not already covered. |
| Inner-Self Guided Builder | ENDORSE | Keeps the promise of "your PDF will be ready." |

**DECISION:** Approved, contingent on ADR-023.

### ADR(s)
- **ADR-023:** Offline-first PDF generation queue for MathWise Nursing.

### Granular Tasks
1. **Queue data model**
   - 1.1 Define `PendingPdfRequest` with `id`, `attemptsJson`, `selectedTopics`, `createdAt`, `retryCount`.
   - 1.2 Add `NursingStorageService` methods:
     - `Future<List<PendingPdfRequest>> getPendingPdfRequests()`
     - `Future<void> addPendingPdfRequest(PendingPdfRequest req)`
     - `Future<void> removePendingPdfRequest(String id)`
2. **UI changes**
   - 2.1 In `NursingPdfScreen._generate()`, on offline failure, persist request and show "PDF queued — we'll generate it when you're back online."
   - 2.2 Add a "Pending PDFs" tile in `NursingSettingsScreen` showing count and retry.
3. **Retry logic**
   - 3.1 On app foreground and on network state change (use `connectivity_plus` or a periodic poll), drain the queue.
   - 3.2 Retry with exponential backoff and max 3 attempts per request.
   - 3.3 On success, show notification/local snackbar and remove from queue.
   - 3.4 On permanent failure, surface an error and keep the request for manual retry.
4. **Tests**
   - 4.1 Unit test queue add/remove/drain.
   - 4.2 Widget test offline queueing UI.

### Acceptance Criteria / Gate
- [ ] PDF request queued when offline.
- [ ] Queue drained automatically when connectivity returns.
- [ ] Max retry limit prevents infinite loops.
- [ ] User can see pending count in settings.

### Files to Modify
- Modify: `mathwise_build/lib/features/nursing/screens/nursing_pdf_screen.dart`, `mathwise_build/lib/features/nursing/services/nursing_storage_service.dart`, `mathwise_build/lib/features/nursing/screens/nursing_settings_screen.dart`
- Create: `mathwise_build/lib/features/nursing/models/pending_pdf_request.dart`, `mathwise_build/lib/features/nursing/services/nursing_pdf_queue_service.dart`

---

## Phase 10.11 — Add WhatsApp/Telegram Community Share Hooks

**PROPOSAL:** Add "Share today's score" and "Challenge a friend" buttons that generate a WhatsApp/Telegram message with a deep link back to the web landing quiz. Do not build in-app chat.

**RATIONALE:** Exam prep in India is deeply social; aspirants already use WhatsApp/Telegram groups for doubt-solving and motivation [^23][^24]. Piggybacking on these platforms is cheaper and more trusted than building social features from scratch.

**RISK LEVEL:** Low

### Council Deliberation

| Persona | Stance | Key Point |
|---|---|---|
| Research Scientist | ENDORSE | WhatsApp/Telegram group usage for exam prep is well documented [^23][^24]. |
| First-Principles Engineer | ENDORSE | Use the platform the user already has. |
| Distributed Systems Architect | ENDORSE | No server-side chat state. |
| Infrastructure-First SRE | ENDORSE | Track share events and referral landings. |
| Diagnostic Problem-Solver | ENDORSE | Root cause of isolation is lack of community hook, not lack of features. |
| Ethical Technologist | CONCERN | Ensure shared messages are not spammy or coercive. |
| Resource Strategist | ENDORSE | Zero marginal infrastructure cost. |
| Curious Explorer | ENDORSE | Test which message copy drives return visits. |
| Clarity-Driven Communicator | ENDORSE | Document share URL format and UTM tags. |
| Inner-Self Guided Builder | ENDORSE | Community support helps the mother stay motivated. |

**DECISION:** Approved.

### ADR(s)
- None (integration with external platform; document in commit message).

### Granular Tasks
1. **Deep link format**
   - 1.1 Define `https://drmath.trelolabs.com/nursing/?ref=share&score=7&total=10&sender=uuid`.
   - 1.2 Parse query params in `web/static/nursing/app.js` to show a personalized welcome.
2. **Share buttons**
   - 2.1 Add "Share score" button on `NursingResultsScreen`.
   - 2.2 Add "Challenge a friend" button on `NursingHomeScreen`.
   - 2.3 Use `share_plus` or `url_launcher` to open WhatsApp/Telegram with pre-filled text.
3. **Message copy**
   - 3.1 Draft Telugu-English mixed messages:
     - "I scored 7/10 in today's Staff Nurse practice on MathWise. Can you beat me? {link}"
4. **Privacy**
   - 4.1 Do not include name or PII in the share URL.
   - 4.2 Use an opaque sender token if tracking referrals.
5. **Tests**
   - 5.1 Widget test that share button constructs expected URL.

### Acceptance Criteria / Gate
- [ ] Share button opens WhatsApp/Telegram with pre-filled message.
- [ ] Shared link opens the web landing quiz.
- [ ] No PII is included in the URL.

### Files to Modify
- Modify: `mathwise_build/lib/features/nursing/screens/nursing_results_screen.dart`, `mathwise_build/lib/features/nursing/screens/nursing_home_screen.dart`, `web/static/nursing/app.js`
- Create: `mathwise_build/lib/features/nursing/services/nursing_share_service.dart`

---

## Phase 10.12 — Add GitHub Actions CI/CD

**PROPOSAL:** Add a GitHub Actions workflow that runs `flutter analyze`, `flutter test test/features/nursing`, and `flutter build apk --release --split-per-abi` on every push to `main` and every pull request. Upload release APKs as artifacts.

**RATIONALE:** Manual builds are error-prone and unrepeatable. CI is a prerequisite for safe iteration and trustworthy artifacts.

**RISK LEVEL:** Medium

### Council Deliberation

| Persona | Stance | Key Point |
|---|---|---|
| Research Scientist | ENDORSE | CI/CD best practices are canonical. |
| First-Principles Engineer | ENDORSE | Reproducible pipeline = deterministic output. |
| Distributed Systems Architect | ENDORSE | Matrix should match local pinned toolchain. |
| Infrastructure-First SRE | ENDORSE | Build artifacts must be versioned and retained. |
| Diagnostic Problem-Solver | ENDORSE | Catches release-build regressions early. |
| Ethical Technologist | ENDORSE | Reduces chance of shipping debug builds to users. |
| Resource Strategist | CONCERN | GitHub Actions minutes have a cost; cache aggressively. |
| Curious Explorer | ENDORSE | CI will surface environment issues we cannot reproduce locally. |
| Clarity-Driven Communicator | BLOCK | Requires ADR-025 or update to deployment docs. |
| Inner-Self Guided Builder | ENDORSE | Professional discipline that protects the user. |

**DECISION:** Approved, contingent on ADR-025.

### ADR(s)
- **ADR-025:** CI/CD pipeline and artifact management for MathWise Nursing.

### Granular Tasks
1. **Workflow file**
   - 1.1 Create `.github/workflows/nursing.yml`.
   - 1.2 Trigger on `push` to `main` and `pull_request`.
   - 1.3 Job steps:
     - Checkout
     - Setup Java 17
     - Setup Flutter 3.27.0
     - `flutter pub get`
     - `flutter analyze lib/features/nursing`
     - `flutter test test/features/nursing`
     - `flutter build apk --release --split-per-abi`
     - `flutter build appbundle --release`
     - Upload APKs and AAB as artifacts
2. **Caching**
   - 2.1 Cache `~/.pub-cache`, `~/.gradle`, `android/.gradle`.
3. **Gates**
   - 3.1 Add size-budget check step (Phase 10.4).
   - 3.2 Add seed-validation step (Phase 10.6).
4. **Branch protection**
   - 4.1 Require the CI job to pass before merging to `main`.

### Acceptance Criteria / Gate
- [ ] CI passes on `main`.
- [ ] CI produces release APKs and AAB as artifacts.
- [ ] PRs cannot merge if CI fails.

### Files to Create/Modify
- Create: `.github/workflows/nursing.yml`
- Modify: GitHub branch protection rules (manual).

---

## Phase 10.13 — Add Crash Reporting & Minimal Analytics

**PROPOSAL:** Integrate a lightweight, privacy-respecting crash reporter (e.g., Sentry open-source or Firebase Crashlytics if ADR approves) and track only essential events: module entry, quiz start, quiz completion, PDF generation attempt, and fatal errors. All analytics require opt-in consent from Phase 10.2.

**RATIONALE:** We cannot distinguish "user did not install" from "user installed and crashed" without observability. But data collection must be minimal and consented.

**RISK LEVEL:** Medium

### Council Deliberation

| Persona | Stance | Key Point |
|---|---|---|
| Research Scientist | ENDORSE | Observability is necessary for iterative improvement. |
| First-Principles Engineer | ENDORSE | Measure only what is needed to verify hypotheses. |
| Distributed Systems Architect | CONCERN | Crash reporter is a network dependency; must queue if offline. |
| Infrastructure-First SRE | ENDORSE | Need dashboards: crash-free rate, quiz completion funnel. |
| Diagnostic Problem-Solver | ENDORSE | Root cause of silent failure is lack of telemetry. |
| Ethical Technologist | BLOCK | Analytics must be opt-in and avoid behavioral profiling. |
| Resource Strategist | CONCERN | Sentry/Firebase have cost/privacy trade-offs; TCO required. |
| Curious Explorer | ENDORSE | Start with a small event dictionary and expand based on questions. |
| Clarity-Driven Communicator | BLOCK | Requires ADR-020 update (data inventory) and ADR-025. |
| Inner-Self Guided Builder | ENDORSE | Observability serves the user only if it leads to fixes, not surveillance. |

**DECISION:** Approved, contingent on opt-in consent and ADR-020/ADR-025 updates.

### ADR(s)
- **ADR-020 update:** Include analytics/crash data in data inventory.

### Granular Tasks
1. **Select tool**
   - 1.1 Compare Sentry open-source, Firebase Crashlytics, and self-hosted Plausible/PostHog.
   - 1.2 Choose based on cost, data residency, and offline queue support.
2. **SDK integration**
   - 2.1 Add SDK to `pubspec.yaml`.
   - 2.2 Initialize only if `crashReportingConsent` is true.
3. **Event dictionary**
   - 3.1 `nursing_module_opened`
   - 3.2 `quiz_started` (with mode, questionCount)
   - 3.3 `quiz_completed` (with score, duration)
   - 3.4 `pdf_generation_attempted` (with success/offline/error)
   - 3.5 `fatal_error` (automatic)
4. **Offline buffering**
   - 4.1 If SDK does not support offline queue, batch events in `SharedPreferences` and flush on connectivity.
5. **Dashboards**
   - 5.1 Create a Sentry/Firebase dashboard or document query URLs.
6. **Tests**
   - 6.1 Unit test that events are not sent when consent is false.

### Acceptance Criteria / Gate
- [ ] Crash reporter initialized only after opt-in.
- [ ] Manual fatal crash test reaches the dashboard.
- [ ] Events respect offline buffering.
- [ ] Data inventory in ADR-020 updated.

### Files to Modify
- Modify: `mathwise_build/pubspec.yaml`, `mathwise_build/lib/main.dart`, `mathwise_build/lib/features/nursing/services/nursing_storage_service.dart`

---

## Phase 10.14 — Document Manual Device Smoke-Test Checklist

**PROPOSAL:** Write a concise checklist that a human can run on a physical Android device in 5 minutes to verify core flows after each release.

**RATIONALE:** Integration tests cannot run in this environment and need a device/emulator. A manual checklist is the minimum verification loop until CI integration tests are possible.

**RISK LEVEL:** Low

### Council Deliberation

| Persona | Stance | Key Point |
|---|---|---|
| Research Scientist | ENDORSE | Manual testing complements automated testing. |
| First-Principles Engineer | ENDORSE | Checklist converts implicit knowledge into repeatable process. |
| Distributed Systems Architect | ENDORSE | No architecture change. |
| Infrastructure-First SRE | ENDORSE | Defines release readiness. |
| Diagnostic Problem-Solver | ENDORSE | Catches device-specific issues CI cannot. |
| Ethical Technologist | ENDORSE | Protects users from broken releases. |
| Resource Strategist | ENDORSE | Cheap quality gate. |
| Curious Explorer | ENDORSE | Iterate checklist based on real failures. |
| Clarity-Driven Communicator | ENDORSE | Document in `docs/checklists/`. |
| Inner-Self Guided Builder | ENDORSE | A responsible release process. |

**DECISION:** Approved.

### Granular Tasks
1. Create `mathwise_build/docs/checklists/nursing-device-smoke-test.md`.
2. Include steps:
   - Install release APK on a budget Android phone (≤4 GB RAM).
   - Open app, accept privacy notice.
   - Tap nursing card, accept disclaimer, complete/skip onboarding.
   - Start a 5-question practice quiz, answer, see feedback.
   - Submit and view results.
   - Generate a PDF (or see offline queue message).
   - Toggle language.
   - Background app during quiz, resume.
   - Share score via WhatsApp.
   - Uninstall and verify no stale data remains.
3. Add a template for recording device model, OS version, and pass/fail per step.

### Acceptance Criteria / Gate
- [ ] Checklist exists and is reviewed by at least one human.
- [ ] First smoke test is completed and recorded before the next public APK update.

### Files to Create
- Create: `mathwise_build/docs/checklists/nursing-device-smoke-test.md`

---

## Phase 10.15 — Draft ADR-019: Native vs. PWA-First Distribution Strategy

**PROPOSAL:** Write ADR-019 documenting the decision to lead with a lightweight PWA landing quiz for discovery and use the native Flutter app for engaged repeat users. Include alternatives considered, consequences, and a reversal trigger.

**RATIONALE:** ADR-019 is a blocking dependency for Phase 10.1 and the overall product strategy.

**RISK LEVEL:** High

### Council Deliberation

| Persona | Stance | Key Point |
|---|---|---|
| Research Scientist | ENDORSE | Decision must cite PWA/native benchmarks [^3][^4]. |
| First-Principles Engineer | ENDORSE | Derive from user constraints (storage, install friction). |
| Distributed Systems Architect | CONCERN | Must document how native and web share backend/data model. |
| Infrastructure-First SRE | ENDORSE | Document deployment and rollback plan. |
| Diagnostic Problem-Solver | ENDORSE | Include reversal trigger (e.g., web conversion <2%). |
| Ethical Technologist | ENDORSE | Document accessibility and low-bandwidth considerations. |
| Resource Strategist | ENDORSE | Include TCO comparison. |
| Curious Explorer | ENDORSE | Frame as an experiment with success metrics. |
| Clarity-Driven Communicator | ENDORSE | ADR is the deliverable. |
| Inner-Self Guided Builder | ENDORSE | Choose the channel that serves the learner, not the builder. |

**DECISION:** Approved.

### ADR(s)
- **ADR-019:** Native vs. PWA-first distribution strategy for MathWise Nursing.

### Granular Tasks
1. Draft ADR with sections: Context, Decision, Consequences, Alternatives (native-only, PWA-only, full feature parity), Reversal Trigger, References.
2. Include metrics: web quiz starts, native installs from web, Day-7 retention per channel.
3. Review with the Council of Ten before finalization.
4. Commit ADR before Phase 10.1 code.

### Acceptance Criteria / Gate
- [ ] ADR-019 committed to `docs/adrs/`.
- [ ] ADR includes reversal trigger and success metrics.

### Files to Create
- Create: `docs/adrs/ADR-019-native-vs-pwa-distribution.md`

---

## Phase 10.16 — Conduct Problem Interview with Target Learners

**PROPOSAL:** Run a 30-minute structured interview with at least 3 Telugu-speaking adult nursing-exam aspirants (including the user's mother) before the next engineering sprint. Document findings and use them to revise ADR-019, ADR-021, and Phase 10 priorities.

**RATIONALE:** Round 6 identified many assumptions; user ground-truth is the highest-leverage input before further engineering.

**RISK LEVEL:** Medium

### Council Deliberation

| Persona | Stance | Key Point |
|---|---|---|
| Research Scientist | ENDORSE | User interviews are primary evidence for UX decisions. |
| First-Principles Engineer | ENDORSE | Validates or falsifies assumptions. |
| Distributed Systems Architect | ENDORSE | No system change. |
| Infrastructure-First SRE | ENDORSE | No operational change. |
| Diagnostic Problem-Solver | ENDORSE | Finds root user needs. |
| Ethical Technologist | ENDORSE | Respects user voice. |
| Resource Strategist | ENDORSE | Cheap compared to building the wrong thing. |
| Curious Explorer | ENDORSE | Highest-value unknown unknown reduction. |
| Clarity-Driven Communicator | ENDORSE | Document in `docs/research/`. |
| Inner-Self Guided Builder | ENDORSE | Ensures we build what is right. |

**DECISION:** Approved.

### ADR(s)
- None (research activity).

### Granular Tasks
1. **Recruitment**
   - 1.1 Identify 3–5 participants: user's mother, 2–4 other aspirants.
   - 1.2 Obtain verbal consent; explain the interview is for app improvement.
2. **Interview guide**
   - 2.1 Current preparation routine (time of day, duration, devices).
   - 2.2 Apps/groups/books currently used and why.
   - 2.3 Biggest friction in current preparation.
   - 2.4 Language preference: English, Telugu, or mixed.
   - 2.5 Willingness to install an app vs. using a web link.
   - 2.6 What would make them practice daily.
   - 2.7 Trust cues expected from a nursing prep app.
3. **Execution**
   - 3.1 Record notes (not audio, unless consent).
   - 3.2 Keep interview conversational, not survey-like.
4. **Synthesis**
   - 4.1 Create `docs/research/bfs-05-nursing-learner-interviews.md`.
   - 4.2 List top 5 insights and 3 priority changes.
   - 4.3 Update ADR-019, ADR-021, and this plan accordingly.

### Acceptance Criteria / Gate
- [ ] Interview notes committed to `docs/research/`.
- [ ] At least 3 interviews completed.
- [ ] Findings lead to at least one change in Phase 10 ordering or scope.

### Files to Create
- Create: `docs/research/bfs-05-nursing-learner-interviews.md`

---

## Cross-Phase Dependencies & Risk Register

| Phase | Hard Dependencies | Biggest Risk | Mitigation |
|---|---|---|---|
| 10.1 Web landing | ADR-019, 10.2 privacy | Public data collection without consent | Do not deploy until 10.2 is done |
| 10.2 Privacy | ADR-020 | Legal exposure under DPDPA | Review by someone familiar with Indian data law |
| 10.3 Toolchain | ADR-018/022 | CI/local mismatch | Test on clean machine before CI commit |
| 10.4 Size budget | 10.3 | Obfuscation breaks app | Full widget-test run after R8 |
| 10.5 Overflow | None | Visual regression | Golden test at 360 dp |
| 10.6 Content audit | ADR-024 | Manual labor slips | Scope to top 2 exams; validation script |
| 10.7 Localization | ADR-021, 10.6 | TTS platform bugs | Fallback hiding |
| 10.8 Micro-sessions | None | Stale state corruption | Schema version + 7-day expiry |
| 10.9 Habit prompts | None | Notification permission denial | Opt-in, no pressure |
| 10.10 PDF queue | ADR-023 | Infinite retry loops | Max attempts + backoff |
| 10.11 Share hooks | 10.1, 10.2 | Spammy UX | PII-free, opt-in share |
| 10.12 CI/CD | ADR-025, 10.3 | Cost overruns | Aggressive caching |
| 10.13 Analytics | ADR-020 update | Consent bypass | Unit tests for consent gate |
| 10.14 Checklist | None | Not used | Make it part of release ritual |
| 10.15 ADR-019 | Round 6 research | Analysis paralysis | Time-box to 2 days |
| 10.16 Interviews | None | Recruitment bias | Recruit outside immediate family too |

---

## Decision Log Index

Each phase that requires a Council decision must produce a file at `docs/decisions/`:

- `DECISION-20260628-001-phase10-top-level.md`
- `DECISION-20260628-002-phase10-1-web-landing.md`
- `DECISION-20260628-003-phase10-2-privacy-consent.md`
- `DECISION-20260628-004-phase10-3-toolchain.md`
- `DECISION-20260628-005-phase10-4-size-budget.md`
- `DECISION-20260628-006-phase10-6-content-audit.md`
- `DECISION-20260628-007-phase10-7-localization.md`
- `DECISION-20260628-008-phase10-10-pdf-queue.md`
- `DECISION-20260628-009-phase10-12-cicd.md`
- `DECISION-20260628-010-phase10-13-analytics.md`
- `DECISION-20260628-011-phase10-15-adr-019.md`

---

## References

[^1]: `voice-revenge-vizuara-ai/AGENTS.md`. Agent Operating Instructions: Voice Agent Architecture Project. https://github.com/shivaram19/voice-revenge-vizuara-ai/blob/main/AGENTS.md

[^2]: `AGENTS.md` (project root). Agent Operating Instructions: Dr. Math — Adaptive Math Content Pipeline.

[^3]: Codingclave. (2026). *PWA vs Native App for Indian Businesses (2026 Guide)*. https://codingclave.com/blog/pwa-vs-native-app-india-2026

[^4]: Mubbits. (2026). *PWA vs Native Apps in 2026*. https://mubbits.com/blog/pwa-vs-native-apps-2026

[^5]: Nishith Desai. (2025). *Legal Update and Technology Law Analysis — Digital Personal Data Protection Act, 2023*. https://www.nishithdesai.com/fileadmin/user_upload/Html/Hotline/Technology_Law_Analysis_Jan0625-M.html

[^6]: CookieYes. (2026). *India Digital Personal Data Protection Act (DPDPA 2025)*. https://www.cookieyes.com/blog/india-digital-personal-data-protection-act-dpdpa/

[^7]: DPDP Consultants. (2026). *DPDP Act & EdTech: What Happens to Student Data Now?* https://www.dpdpconsultants.com/blog.php?id=75&title=dpdp-act-for-edtech-what-happens-to-all-that-student-data-organizations-have-been-collecting

[^8]: Flutter Docs. (2026). *Android Java Gradle migration guide*. https://docs.flutter.dev/release/breaking-changes/android-java-gradle-migration-guide

[^9]: AppsOnAir. (2026). *Reducing Flutter App Size Effectively*. https://www.appsonair.com/blogs/reducing-flutter-app-size-effectively

[^10]: Flutter Docs. (2026). *Measuring your app's size*. https://docs.flutter.dev/perf/app-size

[^11]: ProductGrowth.in. (2026). *Mobile-First UX for Bharat: Tier 2/3 India Design Guide*. https://productgrowth.in/resources/guides/mobile-first-bharat/

[^12]: Teaching at the Right Level Africa. (2025). *TaRL Evidence — India*. https://teachingattherightlevel.org/impact-and-learning/tarl-evidence/history-of-tarls-evidence-in-india/

[^13]: UBS Optimus Foundation. *Teaching at the Right Level — Impactful Philanthropy White Paper*. https://www.ubs.com/global/en/sustainability-impact/our-insights/publications/_jcr_content/root/contentarea/mainpar/toplevelgrid_3723985/col_1/tabteaser/tabteasersplit_397097488/innergrid_copy_copy__949281929/col_3/teaser_copy_copy/linklist/link.0846205010.file/PS9jb250ZW50L2RhbS9hc3NldHMvY2Mvc3VzdGFpbmFiaWxpdHktaW1wYWN0L2RvYy9waGlsYW50aHJvcHkvbGVhcm5pbmctY2VudGVyL3Vicy1pbXBhY3RmdWwtcGhpbGFudGhyb3B5LXdoaXRlLXBhcGVyLnBkZg==/ubs-impactful-philanthropy-white-paper.pdf

[^14]: Rajesh R. Nair. (2026). *Voice Search Optimization for Indian English: How to Rank in 2026*. https://rajeshrnair.com/blog/aeo/ai-search-optimization/voice-search-optimization-indian-english-2026.html

[^15]: Free Press Journal. (2026). *Breaking Barriers: How Indic Language AI Is Building A Truly Inclusive Digital India*. https://www.freepressjournal.in/tech/breaking-barriers-how-indic-language-ai-is-building-a-truly-inclusive-digital-india

[^16]: Flynn, S., Brown, J., Johnson, A., & Rodger, S. (2011). *Barriers to Education for the Marginalized Adult Learner*. https://www.csmh.uwo.ca/docs/publications/Flynn,%20Brown,%20Johnson%20and%20Rodger%202011.pdf

[^17]: UNESCO. (2020). *Global Education Monitoring Report 2020: Inclusion and education — All means all*. https://www.right-to-education.org/sites/right-to-education.org/files/resource-attachments/GEM_Report_Inclusion_2020_En.pdf

[^18]: Square Developer Blog. (2019). *Flutter, Android, and Process Death*. https://developer.squareup.com/blog/flutter-android-and-process-death/

[^19]: Fogg, B. J. *Fogg Behavior Model*. https://www.behaviormodel.org/

[^20]: Fogg, B. J. (2020). *Tiny Habits: The Small Changes That Change Everything*. Houghton Mifflin Harcourt.

[^21]: Business of Apps. (2025). *Mobile App Retention*. https://www.businessofapps.com/guide/mobile-app-retention/

[^22]: Anurag. (2025). *Offline-First Architecture in Flutter: Part 1 — SQLite Local Storage and Conflict Resolution*. https://dev.to/anurag_dev/implementing-offline-first-architecture-in-flutter-part-1-local-storage-with-conflict-resolution-4mdl

[^23]: Oliveboard. (2025). *Telegram and WhatsApp Groups for Exam Preparation, Benefits and Drawbacks*. https://www.oliveboard.in/blog/telegram-and-whatsapp-groups-for-exam-preparation-benefits-and-drawbacks/

[^24]: The Hindu BusinessLine. (2024). *How Telegram is losing the battle to WhatsApp in India?* https://www.thehindubusinessline.com/data-stories/data-focus/telegram-is-losing-the-battle-to-whatsapp-in-india-data-shows/article68572823.ece
