# DECISION-20260612-001: MVP Browser Learning Experience Scope

**Date:** 2026-06-12  
**Proposal:** Build an end-to-end in-browser MVP adaptive math learning experience for Indian Class VII students with 8 features: anonymous identity, topic selection, adaptive practice loop, immediate feedback, progressive hints, session summary, spaced-repetition review queue, and pedagogical dimension selector.  
**Risk Level:** High  
**Final Decision:** Approved with constraints.  

---

## Proposal

Build F1–F8 as the student-facing MVP:

| Feature | Description |
|---------|-------------|
| F1 | Anonymous browser-token identity (no signup) |
| F2 | Topic selection from 10 CBSE Class VII topics |
| F3 | Adaptive practice loop with heuristic Mark updates |
| F4 | Immediate correctness feedback + explanation |
| F5 | 3-level progressive hint ladder |
| F6 | Session summary dashboard |
| F7 | Simplified spaced-repetition review queue |
| F8 | Pedagogical dimension selector |

Constraints:
- No runtime LLM calls; hints/explanations from pre-generated content only.
- Cross-session state stored primarily in browser `localStorage`.
- No gamification, no parent dashboard, no full accounts in MVP.

## Council Deliberation

| Persona | Stance | Key Point |
|---------|--------|-----------|
| Research Scientist | Endorse | Aligns with immediate feedback, scaffolded hints, continuous mastery, and spaced repetition research. |
| First-Principles Engineer | Endorse | Covers the atomic student action loop completely. |
| Distributed Systems Architect | Concern | Returning anonymous identity strategy must be defined. |
| Infrastructure-First SRE | Concern | Need coverage data: which questions have usable hints? |
| Diagnostic Problem-Solver | Concern | Heuristic adaptive rule must be explicit, not arbitrary. |
| Ethical Technologist | Endorse | Anonymous-first design is correct for child privacy. |
| Resource Strategist | Concern | Must cap cost; no runtime LLM calls is good. |
| Curious Explorer | Endorse | Proposes A/B testing the 4 dimensions. |
| Clarity-Driven Communicator | **Block** | Requires ADR-020 before code. |
| Inner-Self Guided Builder | Endorse | Serves the child first. |

## Rationale

The Council agreed the feature set is pedagogically sound, technically feasible, and aligned with the project's research-first values. The blocking concerns were procedural (ADR) and architectural (anonymous identity + adaptive rule precision), both addressed in the final proposal.

## Final Proposal

1. Implement F1–F8.
2. Anonymous identity via browser `localStorage` token + `X-Student-Token` header.
3. Cross-session review queue stored in `localStorage`.
4. Explicit heuristic adaptive selection and Mark update rules.
5. No runtime LLM calls.
6. Write ADR-020 before any implementation.

## Dissent Recorded

None.

## Action Items

- [ ] Write `docs/adrs/ADR-020-mvp-browser-learning-experience.md`
- [ ] Audit generated question JSON for hint coverage
- [ ] Implement `students`, `sessions`, `attempts`, `hint_requests`, `student_marks` tables
- [ ] Build `/learn` frontend and API endpoints
- [ ] Define success metrics dashboard
