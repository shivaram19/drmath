# ADR-026: PWA-First Default Mobile Strategy

**Date:** 2026-05-05  
**Scope:** Mobile delivery layer for Dr. Math — defaulting to Progressive Web App (PWA) for both math and nursing, with Flutter retained only as a future optional native layer.  
**Research Phase:** Bidirectional / cross-domain impact analysis (mobile architecture, low-bandwidth EdTech, content economics).  
**Status:** Proposed.  
**Tracked in:** #52

---

## Context

Dr. Math currently maintains two mobile-facing artifacts:

1. A **Flutter Android app** (`mathwise_app/`) that builds a release APK and contains native UI screens for Class VII math.
2. A **nursing PWA** at `/nursing/` that serves a daily 5-question quiz, works offline after first load, and is installable from the browser.

The assumption has been that the Flutter app is the primary mobile product and that wiring it to the backend would complete the mobile e2e loop. However, deeper research challenges that assumption.

First, the Flutter screens currently display hardcoded/mock data and do not consume any backend API. Second, education is widely identified as a **PWA-first** domain: content needs search discoverability, updates are frequent, learners arrive via shared links, and install friction reduces enrollment [^1][^2][^3]. Khan Academy and Duolingo both maintain PWAs alongside native apps for reach [^4][^5]. Third, the target market (Indian Class VII students and nursing aspirants) often uses low-storage devices on intermittent connectivity, where a PWA of a few megabytes outperforms a native app of tens of megabytes [^1][^2]. Fourth, true e2e learning requires a local-first data model (offline attempts, sync queues, progress persistence), which the current Flutter shell does not have and the nursing PWA only partially has [^6][^7].

Finally, the existing content banks are not yet deep enough to support a credible adaptive experience. A 2025 meta-analysis shows spaced practice improves math learning (*g* = 0.28), but adaptive/IRT systems need large, calibrated item banks to reach acceptable reliability [^8][^9][^10]. Dr. Math currently has ~40 questions per math topic and 130 nursing questions — enough for a pilot, not enough for a true adaptive bank.

## Decision

### 1. Default mobile layer: PWA-first for both math and nursing

The **primary** mobile delivery layer will be a browser-based PWA for both Class VII math and nursing. The PWA will:

- Load the app shell, content, and daily questions from the backend.
- Cache assets and question payloads via a service worker.
- Store attempts, progress, and sync queues in IndexedDB so the learner can practice offline and sync when reconnecting.
- Use a spaced-repetition scheduler (SM-2 style) to select daily questions, replacing random selection.

### 2. Flutter app: retained but deprioritized

The Flutter app (`mathwise_app/`) remains in the repo and the release build toolchain stays functional. It is **not deleted**. However, it will not receive new feature work until the PWA loop is proven. After the PWA loop is proven, we will decide whether to:

- Wrap the PWA in a thin native shell for app-store presence, or
- Implement native-only features (camera, rich notifications) in Flutter that justify the maintenance cost.

### 3. E2E completion criteria

We will not claim “mobile e2e done” until all of the following are true:

1. A learner can answer questions offline and see progress sync later without duplication.
2. Daily questions are selected by spaced repetition, not random sampling.
3. Weak-area summary links back to concept explanations.
4. Each active topic has enough questions for at least 30 days of unique daily practice.
5. Deployment updates PWA assets without manual cache-busting.

### 4. Content depth target

- **Math:** 100+ verified questions per active topic before calling it adaptive-ready.
- **Nursing:** 500+ verified questions with `source_url`, `source_section`, and `verified_at` metadata (Phase 10.10 completion).

## Consequences

### Positive

- **Market fit:** PWA-first matches the low-storage, intermittent-connectivity reality of the target users.
- **Faster iteration:** Web deployments update instantly; no app-store review cycle.
- **Lower maintenance:** One PWA engine serves math and nursing; Flutter maintenance tax is deferred.
- **Offline-first by design:** IndexedDB + sync queue is easier to reason about in a web stack than in the current Flutter shell.
- **Search/discoverability:** PWAs are indexable and shareable via URL.

### Negative

- **App-store presence:** We lose Play Store discoverability until we wrap the PWA or revive Flutter.
- **Sunk cost:** Time already spent on Flutter UI is not yet returned in user value.
- **Native features:** Camera, background sync, and rich push notifications are more limited in PWAs.
- **Team skill mix:** A PWA-first strategy requires stronger web/IndexedDB skills; Flutter skills may atrophy.

### Neutral

- The nursing PWA becomes the reference implementation for the math PWA.
- ADR-021 (Android release build toolchain) remains accepted but its features are no longer on the critical path.

## Alternatives Considered

1. **Flutter-first native app.** Rejected as the default because the current Flutter app uses hardcoded data, requires app-store distribution, and is heavier than a PWA for the target market. Kept as optional future layer.
2. **Hybrid wrapper (Flutter WebView around PWA).** Rejected for now because it adds native complexity without native value; revisit after PWA retention data.
3. **Build both PWA and Flutter in parallel.** Rejected because it splits engineering focus before the learning loop is validated.
4. **Delete Flutter entirely.** Rejected because the release build toolchain and UI may be useful once the PWA loop is proven; deletion is premature.

## Council of Ten Deliberation Summary

- **Research Scientist:** Decision anchored in 2026 PWA/native comparisons, low-bandwidth EdTech architecture guidance, a 2025 math spacing meta-analysis, and IRT item-bank requirements.
- **First-Principles Engineer:** Defines mobile e2e by durable learner behavior (offline practice → sync → spaced review), not by built artifacts.
- **Distributed Systems Architect:** Proposes local-first IndexedDB store + backend sync queue as the default pattern.
- **Infrastructure-First SRE:** Offline sync and idempotent operations become first-class reliability concerns.
- **Ethical Technologist:** Reduces dependence on continuous connectivity, an equity issue for low-bandwidth learners.
- **Resource Strategist:** Defers Flutter maintenance cost until PWA retention justifies further investment.
- **Diagnostic Problem-Solver:** Root cause of “not e2e” is local state and adaptive selection, not lack of UI screens.
- **Curious Explorer:** Detailed findings documented in `docs/research/bidirectional/bidirectional-12-mobile-e2e-introspection.md`.
- **Clarity-Driven Communicator:** E2E completion criteria are explicit and testable.
- **Inner-Self Guided Builder:** The learner’s attention and data are respected; we do not ship a native shell that pretends to be a learning product.

## References

[^1]: TestMu AI. (2026, January 8). *PWA vs Native App: Ultimate Comparison Guide for 2026*. https://www.testmuai.com/learning-hub/pwa-vs-native/

[^2]: Vofox Solutions. (2026, January 15). *Progressive Web Apps vs Native Apps: Which Should You Choose in 2026*. https://vofoxsolutions.com/progressive-web-apps-vs-native-apps-in-2026

[^3]: Appy Pie. (2026, May 18). *Native vs Hybrid vs PWA: Which Wins for Your App Type? (2026 Guide)*. https://www.appypie.com/blog/native-vs-hybrid-vs-pwa

[^4]: Palnode. (2025, September 4). *Harnessing the Power of Progressive Web Apps (PWAs)*. https://palnode.com/harnessing-the-power-of-progressive-web-apps-pwas/

[^5]: Milosolutions. (2025, May 12). *Progressive Web Apps | Examples*. https://www.milosolutions.com/blog/progressive-web-apps-examples/

[^6]: 6B Education. (2026, March 26). *EdTech Development for Low-Bandwidth Environments: Offline-First Architecture Strategies*. https://6b.education/insight/edtech-development-for-low-bandwidth-environments-offline-first-architecture-strategies/

[^7]: eLeaP. (2025, October 10). *Offline Learning in LMS: Practical Strategies to Teach, Train, and Track Without the Internet*. https://www.eleapsoftware.com/glossary/offline-learning-in-lms-practical-strategies-to-teach-train-and-track-without-the-internet/

[^8]: Murray, E. (2025). *A Meta-analytic Review of the Effectiveness of Spacing and Retrieval Practice for Mathematics Learning*. University of York. https://pure.york.ac.uk/portal/en/publications/a-meta-analytic-review-of-the-effectiveness-of-spacing-and-retrie/

[^9]: Lyle, K. B., et al. (2022). Spaced retrieval practice imposes desirable difficulty in calculus learning. *Educational Psychology Review*. https://doi.org/10.1007/s10648-022-09677-2

[^10]: Zhang et al. (2024). Reliable and Efficient Amortized Model-based Evaluation (AIRBench adaptive testing experiments). arXiv. https://arxiv.org/html/2503.13335v1
