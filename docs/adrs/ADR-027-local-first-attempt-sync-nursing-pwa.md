# ADR-027: Local-First Attempt Persistence and Sync for the Nursing PWA

**Date:** 2026-05-05  
**Scope:** Nursing PWA offline-first learner attempt storage, backend persistence, and idempotent sync.  
**Research Phase:** Implementation of ADR-026 (PWA-first default mobile strategy).  
**Status:** Accepted.  
**Tracked in:** #52

---

## Context

ADR-026 made the nursing PWA the reference mobile layer. One of its e2e gates is: *a learner can complete a quiz offline and see progress sync later without duplication.*

The current PWA records answers only as anonymous analytics events (`question_answered`, `quiz_completed`) via `sendBeacon`. These events are fire-and-forget, consent-gated, and not durable enough for progress tracking or spaced-repetition selection.

## Decision

### 1. Client-side: IndexedDB local-first store

The nursing PWA will write every answer immediately to an IndexedDB object store (`attempts`) and also enqueue it in a separate `syncQueue` object store.

- `attempts` is the durable ledger; it survives page reloads and device restarts.
- `syncQueue` holds attempts that have not yet been acknowledged by the backend.
- Each attempt gets a client-generated UUID (`client_attempt_id`) so the backend can deduplicate.
- A stable anonymous `session_id` is kept in `localStorage` so that a single browser/device maps to one learner record without PII.

### 2. Server-side: SQLite `nursing_attempts` table

Attempts are persisted in the existing SQLite database so they can later be queried by `question_id`, `topic_id`, `session_id`, and `answered_at` for spaced-repetition selection and weak-area analysis.

The table has a unique constraint on `client_attempt_id` to guarantee idempotency. The sync endpoint ignores duplicates and reports counts.

### 3. Sync behavior

- If the browser is online at answer time, the PWA immediately tries to flush the sync queue.
- If the browser is offline, attempts remain queued.
- On `window.online` and `visibilitychange` (tab becomes visible), the queue is flushed.
- Flush is idempotent: the backend ignores already-seen `client_attempt_id`s.

### 4. Privacy boundary

Attempt records contain no name, phone number, or persistent device identifier beyond an anonymous `session_id`. This is consistent with the existing DPDPA privacy notice and ADR-020/ADR-022.

## Consequences

### Positive

- Offline practice works: attempts survive 24+ hours without connectivity.
- Re-sync does not create duplicate records.
- The same table can feed future spaced-repetition and weak-area features.
- SQLite keeps attempt data queryable without adding a new dependency.

### Negative

- IndexedDB code increases PWA JavaScript complexity.
- Cross-device progress is not supported (no accounts). `session_id` is device/browser-local.
- Recovery from a corrupted local DB is manual (clear site data).

## Alternatives Considered

1. **Continue using analytics JSONL only.** Rejected: analytics events are not durable enough, not idempotent, and not queryable for adaptive selection.
2. **Store attempts in `localStorage`.** Rejected: `localStorage` is synchronous, limited to ~5 MB, and blocks the main thread; IndexedDB is the standard local-first store.
3. **Background Sync API.** Deferred: simpler `online`/`visibilitychange` listeners are sufficient for M1; Background Sync can be added later.

## References

[^1]: 6B Education. (2026, March 26). *EdTech Development for Low-Bandwidth Environments: Offline-First Architecture Strategies*. https://6b.education/insight/edtech-development-for-low-bandwidth-environments-offline-first-architecture-strategies/

[^2]: eLeaP. (2025, October 10). *Offline Learning in LMS: Practical Strategies to Teach, Train, and Track Without the Internet*. https://www.eleapsoftware.com/glossary/offline-learning-in-lms-practical-strategies-to-teach-train-and-track-without-the-internet/
