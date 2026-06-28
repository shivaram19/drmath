# ADR-022: Consent-Gated Analytics for MathWise Nursing PWA

**Date:** 2026-06-28  
**Scope:** Collect the minimum anonymous telemetry needed to measure Phase 10.1/10.6 campaign effectiveness without storing personal identifiers or firing trackers before consent.  
**Research Phase:** BFS — lightweight analytics for Bharat PWAs; DPDPA-compliant event collection.  
**Status:** Approved by Council of Ten.

---

## Context

The MathWise Nursing landing page (`/nursing/`) is now live and publicly shareable (ADR-019). To decide whether the PWA-first strategy is working, we need a small set of funnel signals:

- `landing_quiz_started` — does the value proposition convert a visitor into a quiz attempt?
- `question_answered` — do users engage with the full 5-question flow?
- `quiz_completed` — completion rate, with aggregate score only.
- `score_shared` — does the WhatsApp share CTA get used?

DPDPA Section 6 requires free, specific, informed, unambiguous consent before any non-essential processing [^1][^2]. Because these events are not necessary to deliver the quiz itself, they must be gated by the consent record already established in ADR-020. No cookies, fingerprinting, or third-party scripts may be used.

The target learner uses low-end Android devices on intermittent networks, so the telemetry channel must be tiny, resilient to dropped connections, and not block UI interactions.

---

## Decision

**Implement a server-side analytics endpoint that records only anonymous, consent-gated JSONL events, and wire the landing-page client to send events only after affirmative consent.**

Specifically:

1. **Client-side gate:** `trackEvent()` in `web/static/nursing/app.js` returns immediately unless `hasConsent()` returns `true`. Consent is read from the same `mw_privacy_consent` record used by the share button.
2. **Event types tracked:**
   - `landing_quiz_started` — when the user taps “Start 5 Questions”.
   - `question_answered` — after each option selection; includes only question index, selected/correct keys, correctness boolean, and `topic_id` from the question bank.
   - `quiz_completed` — when the final question is answered; includes aggregate `score` and `total`.
   - `score_shared` — when the share button is tapped; includes aggregate `score` and `total`.
3. **No identifiers sent:** The payload contains no IP, device ID, user agent snapshot, or geolocation. The server intentionally does not enrich events with `remote_addr`.
4. **Transport:** `navigator.sendBeacon` with `fetch(..., keepalive: true)` fallback, so clicks and completions are not lost on page navigation or network blips.
5. **Server endpoint:** `POST /api/nursing/analytics` accepts `event`, `timestamp`, `consent_version`, and `metadata`, appends a line to `data/nursing_events.jsonl`, and returns `{"status": "recorded"}`.
6. **Retention:** Events are retained only as long as server logs (30 days, per ADR-020 logrotate policy); the JSONL file is gitignored and not part of backups.
7. **Graceful degradation:** If the endpoint is unavailable, events are silently dropped. The quiz remains fully functional offline.

---

## Consequences

### Positive
- Provides objective data for the PWA reversal trigger defined in ADR-019 (<2% quiz starts per visitor in 30 days or >20% native install conversion).
- Respects DPDPA consent by design: no event is recorded before an affirmative “I agree”.
- No third-party trackers or cookies, preserving page weight (~28 KB shell) and trust.
- JSONL format is trivial to inspect, rotate, and archive without a database dependency.

### Negative
- Events are anonymous and client-timestamped, so we cannot correlate a single learner across sessions or deduplicate accidental retries.
- Server logs still contain IP/timestamp for the beacon request itself; the 30-day rotation policy applies.

### Neutral
- The analytics file grows linearly with traffic; rotation must be handled by the existing 30-day logrotate schedule or a future dedicated policy.

---

## Alternatives Considered

1. **Google Analytics / Plausible / other third-party script:** Rejected. Any third-party script would require additional consent disclosure, increase payload, and potentially leak IP/UA to an external processor [^3].
2. **Collect all events without consent:** Rejected. DPDPA Section 6 requires opt-in consent for non-essential processing [^1].
3. **Store events in SQLite:** Rejected for v1. JSONL keeps the analytics path stateless and avoids schema migrations for an experimental measurement channel.

---

## Council of Ten Deliberation Summary

| Persona | Stance | Key Point |
|---|---|---|
| Research Scientist | ENDORSE | Funnel metrics are the minimum signal needed to test the PWA hypothesis empirically. |
| First-Principles Engineer | ENDORSE | If analytics cannot work without consent, the core quiz still works without consent. |
| Distributed Systems Architect | ENDORSE | Beacon + JSONL is stateless, idempotent-friendly, and needs no new service. |
| Infrastructure-First SRE | ENDORSE | 30-day retention, no PII, and gitignore keep operational risk minimal. |
| Ethical Technologist | ENDORSE | Consent gate, no identifiers, and no third-party scripts align with data-minimization principles. |
| Resource Strategist | ENDORSE | Avoids paid analytics subscriptions and vendor lock-in. |
| Diagnostic Problem-Solver | ENDORSE | Measures the real questions (do users start, finish, and share?) instead of vanity page views. |
| Curious Explorer | ENDORSE | Simple JSONL enables rapid ad-hoc analysis without a dashboard. |
| Clarity-Driven Communicator | ENDORSE | ADR makes the event schema and retention explicit. |
| Inner-Self Guided Builder | ENDORSE | Learners are not treated as data sources unless they explicitly agree. |

---

## Action Items

- [x] Add `trackEvent()` to `web/static/nursing/app.js` gated by `hasConsent()`.
- [x] Fire `landing_quiz_started`, `question_answered`, `quiz_completed`, and `share_clicked` events.
- [x] Implement `POST /api/nursing/analytics` in `web/routers/nursing.py`.
- [x] Append events to `data/nursing_events.jsonl` and gitignore the file.
- [x] Add pytest coverage for the events endpoint.
- [x] Update `STATE.md` to mark Phase 10.6a complete and add ADR-022.

---

## References

[^1]: Government of India. (2023). *The Digital Personal Data Protection Act, 2023*. India Code. https://www.indiacode.nic.in/handle/123456789/22037?view_type=browse

[^2]: Digital Personal Data Protection Act, 2023, §6 (Consent). https://www.dpdpa.com/dpdpa2023/chapter-2/section6.html

[^3]: Data Protection Network. (2023). *Guidance Note: Analytics and Consent*. https://dpnetwork.org.uk/resources/guidance-notes/analytics-and-consent/
