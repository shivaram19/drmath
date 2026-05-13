# ADR-016: PM Question Review System

**Date:** 2026-05-13  
**Status:** Accepted  
**Scope:** Web UI + Database  
**Research Phase:** DFS — Synthesis of educational content evaluation frameworks

---

## Context

The content pipeline generates 40 MCQs per topic via LLM. Before any question reaches the Flutter app, a product manager must validate pedagogical quality. We need a system where PMs can:

1. Review individual questions across multiple pedagogical dimensions
2. Rate each question on research-backed quality metrics
3. Compare different prompt personas (Default, Storyteller, Visual-First, ZPD)
4. Leave qualitative feedback that drives prompt iteration

## Decision

Build a per-question review system with:
- **Database model:** `QuestionReview` with 4 rating dimensions (1-5 scale)
- **Web endpoints:** `/review/{slug}` (HTML), `/api/question-reviews` (REST)
- **Frontend:** Card-based question viewer with inline star ratings
- **Analytics:** Aggregate stats per generation, prompt leaderboard

## Rationale

### Why per-question, not per-generation?

Generation-level ratings (existing `Evaluation` model) mask question-level variance. A generation might average 4/5 while containing 10 unusable questions. Per-question granularity enables:
- Surgical re-generation of low-rated questions only
- Identification of systematic prompt flaws (e.g., "all questions at difficulty 4 have poor guidance")
- A/B testing at the question level, not topic level

### Why 4 dimensions?

Synthesized from three peer-reviewed evaluation frameworks:

| Our Dimension | Source | Original Metric |
|---------------|--------|----------------|
| Thought Direction | EQGBench (2025) [^1] | Competence-Oriented Guidance |
| Playfulness | OpenLearnLM (2025) [^2] | Scenario Alignment |
| Guidance Quality | EQGBench (2025) [^1] | Solution Explanation Quality |
| Curiosity Building | Bloom's AEQG (2024) [^3] | "Would you use it?" + engagement |

Clarity and Accuracy are treated as **gates**, not dimensions. A question failing either is marked 1-2 overall and queued for rewrite.

### Why star ratings (1-5) over pass/fail?

Pass/fail loses gradient signal. A question scoring 2/5 on Playfulness is salvageable with minor edits; a 1/5 needs full rewrite. The 5-point scale gives the prompt-engineering loop enough resolution to iterate.

## Consequences

### Positive
- Data-driven prompt selection via leaderboard
- Question-level quality gating before app release
- Qualitative feedback loop from PM to engineering

### Negative
- SQLite `question_reviews` table grows linearly with reviews (acceptable for <10k reviews)
- No user authentication; assumes single PM reviewer. If multiple PMs review, aggregate stats become averages of averages.

## Alternatives Considered

| Alternative | Rejected Because |
|-------------|-----------------|
| LLM-as-Judge auto-evaluation | OpenLearnLM (2025) [^2] showed significant discrepancy between LLM judges and human evaluators. Human-in-the-loop is mandatory for educational content. |
| Binary pass/fail only | Loses gradient signal for prompt iteration. |
| Review at generation level only | Masks question-level variance. |

## Implementation

- `db/models.py`: `QuestionReview` model
- `db/crud.py`: `create_or_update_question_review()`, `get_question_review_stats()`
- `web/main.py`: `/review/{slug}`, `/api/question-reviews` (POST/GET), `/api/question-reviews/stats/{id}`
- `web/templates/review.html`: Card-based UI with star ratings, filters, progress bar

## References

[^1]: EQGBench — From Answers to Questions: Evaluating LLMs' Educational Question Generation. ACL Anthology, 2025.
[^2]: OpenLearnLM Benchmark: A Unified Framework for Evaluating Knowledge, Skill, and Attitude in Educational LLMs. arXiv, 2025.
[^3]: Automated Educational Question Generation at Different Bloom's Skill Levels using LLMs. arXiv, 2024.
