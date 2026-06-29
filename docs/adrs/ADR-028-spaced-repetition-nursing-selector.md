# ADR-028: Spaced-Repetition Question Selection for the Nursing PWA

**Date:** 2026-05-05  
**Scope:** Daily question selection algorithm for the nursing PWA.  
**Research Phase:** Implementation of ADR-026/027 (PWA-first local-first strategy).  
**Status:** Accepted.  
**Tracked in:** #53

---

## Context

The nursing PWA currently serves a random 5-question daily quiz. Random selection does not support retention or weak-area remediation. A 2025 meta-analysis found spaced practice has a robust small-to-medium effect on mathematics learning (*g* = 0.28) [^1], and spaced retrieval practice in calculus improved final-exam performance [^2].

ADR-026 and ADR-027 established PWA-first delivery and a local-first attempt store. The next step is to use the stored attempt history to select questions.

## Decision

### 1. Lightweight SM-2-style scheduler, client-side

The PWA will maintain per-question statistics in IndexedDB (`question_stats`):

- `question_id`
- `correct_count`
- `incorrect_count`
- `last_seen_at`
- `next_due_at`

On each answer:
- If correct, the interval doubles.
- If incorrect, the interval resets to 1 day.
- `next_due_at` is computed from the current interval.

### 2. Daily selection algorithm

When building a daily quiz:

1. Fetch a candidate pool from `/api/nursing/questions?limit=50`.
2. Load local `question_stats`.
3. Prioritize questions whose `next_due_at <= now` (due questions), sorted by weakness score.
4. Ensure at least 30% of the daily set consists of previously-seen weak-area items when history exists.
5. Fill remaining slots with unseen questions, then with non-due seen questions.
6. Fall back to random selection if no local history exists.

### 3. Privacy

All scheduling state remains in the browser’s IndexedDB. No scheduler state is sent to the backend beyond the individual attempt records already defined in ADR-027.

## Consequences

### Positive

- Learners see previously-missed questions resurface automatically.
- No backend state is needed for scheduling, preserving the local-first architecture.
- The same `question_stats` table and algorithm can be reused for the math PWA.

### Negative

- Cross-device spacing is not supported (no accounts).
- A small content bank limits the scheduler’s effectiveness.
- The 30% weak-area target may not be reachable early in a learner’s history.

## References

[^1]: Murray, E. (2025). *A Meta-analytic Review of the Effectiveness of Spacing and Retrieval Practice for Mathematics Learning*. University of York. https://pure.york.ac.uk/portal/en/publications/a-meta-analytic-review-of-the-effectiveness-of-spacing-and-retrie/

[^2]: Lyle, K. B., et al. (2022). Spaced retrieval practice imposes desirable difficulty in calculus learning. *Educational Psychology Review*. https://doi.org/10.1007/s10648-022-09677-2
