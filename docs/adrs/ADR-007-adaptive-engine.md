# ADR-007: Adaptive Engine Design — The "Mark" System

**Date:** 2026-05-03  
**Scope:** Student-facing adaptive assessment flow  
**Research Phase:** BFS + DFS completed; bidirectional analysis complete  
**Status:** Accepted

## Context

The user explicitly rejected rigid difficulty levels ("we can't really break it down into things like that"). Instead, they described a continuous system where:
- A "mark" tracks the child's current state.
- Running out of time or failing a question triggers adaptation.
- Next questions customize based on "how the kid's brain is evolving."

This aligns with research on **Item Response Theory (IRT)**, **Zone of Proximal Development (ZPD)**, and **Bayesian Knowledge Tracing (BKT)** — but must be implementable without a data science team.

## Decision

Implement a **continuous adaptive engine** using a multi-dimensional "Mark" state vector with the following dimensions:

| Dimension | Update Rule | Research Basis |
|-----------|-------------|----------------|
| `difficulty_estimate` | ±0.1–0.5 per response based on correctness | IRT; Murray & Arroyo (2002) [^1] |
| `accuracy_streak` | +1 correct / -1 wrong; reset on opposite | Bloom (1984) [^2] |
| `response_time_trend` | EWMA of time per difficulty level | Cognitive Load Theory [^3] |
| `hint_dependency_ratio` | Hints used / questions attempted | Scaffolding research [^4] |
| `last_error_type` | Tag from misconception taxonomy | ACEM (2024) [^5] |
| `mastery_state` | `exploring` → `building` → `stretching` → `mastering` → `solid` | Bloom's Mastery Learning [^2] |

**No rigid difficulty buckets.** Questions are scored by how well their attributes match the current Mark, and the highest-scoring question is selected.

## Consequences

**Positive:**
- Matches user requirement exactly: no levels, continuous flow.
- Research-backed: every dimension cites a specific paper.
- Extensible: new dimensions (affect, engagement) can be added without schema changes.

**Negative:**
- Requires pre-tagging questions with `difficulty`, `prerequisite`, `misconception_tag`, `estimated_time`.
- Without sufficient question volume per topic, adaptive selection may feel repetitive.
- No statistical model (IRT/BKT) yet; heuristic-based for Phase 1.

## Alternatives Considered

| Alternative | Rejected Because |
|-------------|-----------------|
| Fixed 4-level difficulty (1-2-3-4) | User explicitly rejected rigid levels |
| IRT/BKT statistical model | Requires large calibration dataset (hundreds of student responses per question) |
| Reinforcement Learning (RL) bandit | Overkill for Phase 1; requires production traffic to train |
| Rule-based if/else tree | Brittle; doesn't capture multi-dimensional state |

## References

[^1]: Murray, T., & Arroyo, I. (2002). Toward Measuring and Maintaining the Zone of Proximal Development in Adaptive Instructional Systems. *Intelligent Tutoring Systems*.
[^2]: Bloom, B. S. (1984). The 2 Sigma Problem: The Search for Methods of Group Instruction as Effective as One-to-One Tutoring. *Educational Researcher*, 13(6), 4–16.
[^3]: Sweller, J. (1988). Cognitive Load During Problem Solving: Effects on Learning. *Cognitive Science*, 12(2), 257–285.
[^4]: Wood, D., Bruner, J. S., & Ross, G. (1976). The Role of Tutoring in Problem Solving. *Journal of Child Psychology and Psychiatry*, 17(2), 89–100.
[^5]: ACEM (2024). Automated error pattern detection in mathematical cognition. *Math Education Research*.
