# ADR-029: Weak-Area Concept Card in the Nursing PWA

**Date:** 2026-05-05  
**Scope:** Post-quiz weak-area summary and concept explanation card for the nursing PWA.  
**Research Phase:** Implementation of ADR-026/027/028 (PWA-first, local-first sync, spaced repetition).  
**Status:** Accepted.  
**Tracked in:** #54

---

## Context

After a quiz, learners benefit from immediate feedback on what they got wrong and a chance to review the underlying concept [^1]. ISSUE-002 requires the nursing PWA to surface the weakest topic and link to a concept explanation.

The backend already stores per-question explanations in the nursing seed bank. A dedicated concept-explanation adapter is planned (ISSUE-015), but the learner-facing feature should not wait for it.

## Decision

### 1. Compute weakest topic from the current quiz

The PWA tracks each answer in memory during the quiz. On the result screen, it groups attempts by `topic_id` and selects the topic with the lowest accuracy.

### 2. Synthesize concept explanation from question explanations

Until ISSUE-015 lands, the backend endpoint `GET /api/nursing/concept?topic_id=...` returns an explanation synthesized from up to 3 unique question explanations in that topic.

### 3. Cache concept cards offline

The PWA caches fetched concept cards in IndexedDB (`concept_cache`) so the review button works offline after the first fetch.

### 4. UI placement

The weak-area summary appears on the result screen below the score. Tapping “Review concept” opens a modal with the explanation.

## Consequences

### Positive

- Learners get immediate, actionable feedback after every quiz.
- Concept cards are available offline after first load.
- No new backend data model is required for v1.

### Negative

- The synthesized explanation may be disjointed compared to a hand-written concept card.
- A topic with no reviewed questions will return a placeholder.
- Concept cache is device-local; cross-device review is not supported.

## References

[^1]: Hattie, J., & Timperley, H. (2007). The power of feedback. *Review of Educational Research*, 77(1), 81–112. https://doi.org/10.3102/003465430298487
