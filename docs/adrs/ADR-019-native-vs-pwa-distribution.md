# ADR-019: Native vs. PWA-First Distribution Strategy for MathWise Nursing

**Date:** 2026-06-28  
**Scope:** Decide the primary distribution channel for the MathWise Nursing module and the role of the existing Flutter native app.  
**Research Phase:** BFS — Bharat mobile distribution, PWA capabilities, competitive EdTech channels.  
**Status:** Approved by Council of Ten (top-level Phase 10 review).

---

## Context

The MathWise Nursing module is currently a Flutter native APK served from `https://drmath.trelolabs.com/mathwise.apk`. Round 6 surfaced that:

1. The debug APK is 104 MB and the release target is 15–20 MB, but even a 15 MB install competes for scarce storage on budget devices.
2. The average Indian smartphone user installs zero new apps per month; app-store discovery is extremely competitive [^1].
3. Bharat users on 2–4 GB phones frequently delete large apps to free space for photos, videos, and WhatsApp [^2].
4. Existing Indian EdTech leaders (Testbook, Adda247, Physics Wallah) reach millions through low-cost subscriptions, YouTube, and WhatsApp/Telegram communities, not primarily through app-store search [^3][^4].
5. Progressive Web Apps in 2026 support install-to-home-screen, offline caching, push notifications, background sync, camera/microphone, geolocation, payments, and biometric auth on Android [^5][^6].
6. Case studies such as Twitter Lite and Starbucks show dramatic data and size reductions versus native apps [^5][^6].

The target learner is a Telugu-speaking adult woman preparing for Telangana/Andhra Pradesh staff-nurse exams, often using a shared budget phone with intermittent connectivity and limited uninterrupted study time.

---

## Decision

**Lead with a lightweight PWA/web landing quiz for discovery and first-time use; use the Flutter native app for engaged repeat users who explicitly choose to install.**

Specifically:

1. **Primary entry point:** A shareable web page at `https://drmath.trelolabs.com/nursing/` that lets a user complete a 5-question daily quiz with zero install.
2. **Native app role:** An optional, richer install for users who want full mock tests, offline question banks, PDF generation, and habit reminders.
3. **Feature parity boundary:** The PWA v1 is intentionally scoped to a single-page daily quiz, language toggle, and share-to-WhatsApp. Full subject browsing, mock tests, PDFs, and settings remain native-only.
4. **Shared backend:** Both channels use the same `/api/nursing/*` endpoints and the same static origin `drmath.trelolabs.com`.
5. **Reversal trigger:** If the web quiz drives fewer than 2% of visitors to start a quiz within 30 days, or if native install-to-usage conversion from the web landing exceeds 20%, we will reconsider native-first.

---

## Consequences

### Positive
- Lower user-acquisition friction: no app store, no storage negotiation, no 20 MB download.
- Faster experimentation: landing copy, question sets, and share messages can be updated by redeploying static files.
- Better fit for shared-family phones where installing an app requires social negotiation.
- The native app can be positioned as the "serious preparation" channel, justifying its larger size.

### Negative
- Two deployment surfaces to maintain (web static files + Flutter builds).
- PWA capabilities on iOS/Safari are more restricted than on Android (limited background sync, no web push before 16.4); our primary audience is Android, so this is acceptable for v1.
- Analytics and crash reporting must be implemented separately for web and native, or unified via a common backend.

### Neutral
- Existing Flutter codebase remains the source of truth for core logic; the web landing is a thin, stateless shell.

---

## Alternatives Considered

1. **Native-only (current path):** Optimize the APK to 15 MB and distribute via direct download. Rejected because install friction and storage anxiety remain high for the target audience [^2].
2. **PWA-only:** Abandon the Flutter app and rebuild everything as a PWA. Rejected because the existing Flutter investment is significant, and offline-first features (full mock test, PDF queue) are easier to implement reliably in native code today.
3. **Full feature parity between PWA and native:** Rejected because it doubles initial development effort without validating whether users will open the web quiz at all.

---

## Council of Ten Deliberation Summary

| Persona | Stance | Key Point |
|---|---|---|
| Research Scientist | CONCERN → RESOLVED | PWA benchmarks are strong, but user data from a problem interview (Phase 10.16) can revise this ADR before finalization. |
| First-Principles Engineer | ENDORSE | Derives from the atomic user need: answer a question on the device she already has. |
| Distributed Systems Architect | CONCERN → RESOLVED | PWA must be served from the same `drmath.trelolabs.com` origin and reuse existing nginx/static infra. |
| Infrastructure-First SRE | ENDORSE | Observability must cover both channels. |
| Diagnostic Problem-Solver | ENDORSE | Fixes the deeper problem (discovery/install friction) before optimizing APK size. |
| Ethical Technologist | ENDORSE | Reduces data usage and storage pressure on low-resource users. |
| Resource Strategist | CONCERN → RESOLVED | Scope boundary (single-page daily quiz) prevents maintenance sprawl. |
| Curious Explorer | ENDORSE | The PWA landing is a cheap experiment. |
| Clarity-Driven Communicator | ENDORSE | ADR documents the decision, reversal trigger, and alternatives. |
| Inner-Self Guided Builder | ENDORSE | Serves the learner's constraints rather than the builder's stack preference. |

---

## Action Items

- [x] ADR written.
- [ ] Implement PWA landing page (Issue #33).
- [ ] Add privacy notice and consent before public distribution (Issue #34).
- [ ] Add web-side analytics event for `landing_quiz_started`.
- [ ] Measure reversal trigger metrics after 30 days of deployment.

---

## References

[^1]: Mubbits. (2026). *PWA vs Native Apps in 2026*. https://mubbits.com/blog/pwa-vs-native-apps-2026

[^2]: Codingclave. (2026). *PWA vs Native App for Indian Businesses (2026 Guide)*. https://codingclave.com/blog/pwa-vs-native-app-india-2026

[^3]: Reward Eagle. (2026). *Testbook vs Unacademy vs BYJU's vs Adda247 — Honest 2026 Comparison*. https://rewardeagle.com/store/testbook-coupons

[^4]: Business Model Canvas Template. (2024). *What Is the Competitive Landscape of Adda247 Company?* https://businessmodelcanvastemplate.com/blogs/competitors/adda247-competitive-landscape

[^5]: GitNexa. (2026). *PWA vs Native App Development: Complete 2026 Guide*. https://www.gitnexa.com/blogs/pwa-vs-native-app-development

[^6]: Easycomm. (2026). *Progressive Web App vs Native App: 2026 Comparison*. https://easycomm.io/blog/progressive-web-app-vs-native-app/
