# ADR-020: DPDPA Privacy Notice and Consent Flow for MathWise Nursing

**Date:** 2026-06-28  
**Scope:** Comply with India’s Digital Personal Data Protection Act, 2023 before publicly distributing or promoting the MathWise Nursing PWA landing page.  
**Research Phase:** BFS — DPDPA notice/consent requirements, lightweight consent UX for Bharat mobile users.  
**Status:** Approved by Council of Ten.

---

## Context

The MathWise Nursing PWA at `https://drmath.trelolabs.com/nursing/` is now live (Phase 10.1). Before it can be shared publicly on WhatsApp/Telegram or linked from paid channels, we must meet the notice and consent obligations of the Digital Personal Data Protection Act, 2023 (DPDPA) [^1].

Key DPDPA requirements relevant to a lightweight quiz landing page:

1. **Section 5 — Notice:** A Data Fiduciary must give the Data Principal a clear, plain-language notice at or before the point of collection, describing the personal data processed, the purpose, how rights can be exercised, and how to complain [^1][^2].
2. **Section 6 — Consent:** Consent must be free, specific, informed, unconditional, unambiguous, and given through a clear affirmative action; it must be as easy to withdraw as it is to give [^1][^2].
3. **Sections 12–14 — Data Principal Rights:** Access, correction/erasure, and grievance redressal must be available [^1].
4. **Section 8(5) — Security Safeguards:** Reasonable technical and organisational measures must protect personal data [^1].

The PWA currently collects no intentionally identifying data, but it does:
- Fetch questions from `/api/nursing/questions` (server logs IP/timestamp).
- Store quiz attempts and capability maps in `localStorage` in the full nursing app (`nursing.js`).
- Offer a "Share Score" button that constructs a message containing the user’s score and URL.
- Will soon add lightweight analytics events (e.g., `landing_quiz_started`) to measure the ADR-019 reversal trigger.

These touch points are sufficient to require a privacy notice and a consent gate for analytics/sharing before public promotion.

---

## Decision

**Implement a minimal, DPDPA-aligned privacy notice and consent flow before any public distribution or paid promotion of the nursing landing page.**

Specifically:

1. **Privacy notice page** at `/privacy` (static HTML) covering:
   - What data is collected (server logs, localStorage, optional analytics, share text).
   - Purpose of processing (quiz delivery, offline fallback, improvement, sharing only when initiated).
   - Data principal rights (access, correction, erasure, grievance) and contact details.
   - Security and retention summary.
   - Plain English + Telugu headings for the Bharat audience.
2. **First-visit consent banner** on `/nursing/`:
   - Shows before analytics fire or share actions.
   - Requires a clear affirmative tap ("I agree") after linking to the privacy notice.
   - Records consent timestamp and version in `localStorage` (`mw_privacy_consent`).
   - Provides a "Withdraw consent / Privacy" link that clears the record and disables analytics/share.
   - Does **not** block viewing the landing page or taking the offline quiz — consent is only required for analytics and share features, keeping the quiz itself accessible without precondition [^2].
3. **Conditional share button:** If consent is missing, tapping "Share Score" opens the consent dialog first; after consent, it opens the native/Web Share flow.
4. **Service worker cache:** Add `/privacy` to the shell cache so the notice remains available offline.
5. **Deployment:** Serve `/privacy` as a static page via nginx (`location = /privacy`) with a FastAPI fallback for local development.

---

## Consequences

### Positive
- Public sharing campaigns (WhatsApp, Telegram, paid ads) can proceed legally.
- Consent record is client-side and versioned, providing evidence of informed consent.
- Privacy page works offline, reinforcing trust on low-connectivity devices.
- Minimal scope: no cookie banner for purely necessary operations, only for analytics/share.

### Negative
- Slightly more friction before the first share or analytics event.
- Client-side consent records can be cleared by the user; we cannot prove consent server-side. For our low-risk quiz this is acceptable, but a future registered Consent Manager may be required at scale [^2].

### Neutral
- Privacy page is static; future DPDPA rule changes require a deploy to update.

---

## Alternatives Considered

1. **Full Consent Manager (registered with Data Protection Board):** Rejected for v1 due to cost and complexity; reserved for scale or if designated a Significant Data Fiduciary [^2].
2. **Cookie-style opt-out banner:** Rejected because DPDPA requires affirmative opt-in, not implied consent [^2].
3. **Bundle consent with terms of service:** Rejected because Section 6(1)(a) prohibits making consent a precondition for service [^2].

---

## Council of Ten Deliberation Summary

| Persona | Stance | Key Point |
|---|---|---|
| Research Scientist | ENDORSE | DPDPA Sections 5 and 6 are clear; notice-before-consent sequence is mandatory. |
| First-Principles Engineer | ENDORSE | The atomic user need (take a quiz) must not depend on consent. |
| Distributed Systems Architect | ENDORSE | Static privacy page + localStorage consent keeps the architecture stateless and simple. |
| Infrastructure-First SRE | CONCERN → RESOLVED | Ensure `/privacy` is cached offline and served over HTTPS; no PII stored server-side. |
| Ethical Technologist | ENDORSE | No analytics until explicit consent; data minimization by design. |
| Resource Strategist | ENDORSE | A static page is the cheapest compliant path; defer Consent Manager spend. |
| Diagnostic Problem-Solver | ENDORSE | Solves the real blocker (legal readiness) rather than adding more quiz features. |
| Curious Explorer | ENDORSE | Records consent version for future A/B testing of notice copy. |
| Clarity-Driven Communicator | ENDORSE | ADR documents exact scope and what is out of scope for v1. |
| Inner-Self Guided Builder | ENDORSE | Protects the learner’s dignity and autonomy before asking them to promote the product. |

---

## Action Items

- [x] Create `web/static/nursing/privacy.html` with DPDPA-aligned disclosures in English + Telugu.
- [x] Add consent banner and conditional share logic to `web/static/nursing/app.js`.
- [x] Cache `/nursing/privacy` in `web/static/nursing/sw.js`.
- [x] Serve `/nursing/privacy` via nginx `try_files $uri.html` and FastAPI fallback.
- [x] Update deploy script to copy nursing static assets (including `privacy.html`) to nginx webroot.
- [x] Update nursing landing test and close Issue #34.

---

## References

[^1]: Government of India. (2023). *The Digital Personal Data Protection Act, 2023*. India Code. https://www.indiacode.nic.in/handle/123456789/22037?view_type=browse

[^2]: Digital Personal Data Protection Act, 2023, §6 (Consent). https://www.dpdpa.com/dpdpa2023/chapter-2/section6.html

[^3]: Secure Privacy. (2026). *India DPDPA Privacy Policy Requirements & Compliance Guide*. https://secureprivacy.ai/blog/india-dpdpa-privacy-policy-requirements-compliance-guide

[^4]: PrecisionTech. (2026). *ISO/IEC 27701:2019 PIMS Certification India — DPDPA 2023 Alignment*. https://precisiontech.in/certifications/iso-27701-2019/
