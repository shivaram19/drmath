# ADR-017: Multi-Prompt Batch Content Generation

**Date:** 2026-05-13  
**Status:** Accepted  
**Scope:** Pipeline Automation + Content Strategy  
**Research Phase:** BFS — Pedagogical persona landscape mapping

---

## Context

The content pipeline generates math questions for Indian Class VII students. A single "default" prompt produces adequate content, but it cannot explore the full pedagogical design space. We need to answer:

1. Which teaching approach works best for each topic?
2. How do we compare approaches rigorously?
3. How do we generate at scale without manual intervention?

## Decision

Generate every topic in **4 pedagogical dimensions** using distinct prompt personas, then A/B test via PM review ratings.

| Dimension | Prompt ID | Theory | Icon |
|-----------|-----------|--------|------|
| Default | `1624be66` | Scaffolded instruction (Rosenshine, 2012) [^1] | 🧮 |
| Cultural Storyteller | `cultural_storyteller` | Situated learning (Lave & Wenger, 1991) [^2] | 📖 |
| Visual-First | `visual_first` | CPA method (Bruner, 1966) [^3] | 👁️ |
| ZPD Adaptive | `zpd_adaptive` | Zone of Proximal Development (Vygotsky, 1978) [^4] | 🎯 |

Batch generation runs via `ThreadPoolExecutor` with 3 concurrent workers, respecting API rate limits.

## Rationale

### Why 4 dimensions?

Educational psychology offers multiple valid frameworks for teaching mathematics. No single approach dominates all topics. For example:
- **Fractions** benefit from Visual-First (diagrams of pizza slices)
- **Percentage** benefits from Cultural Storyteller (bazaar discounts, cricket stats)
- **Simple Equations** benefit from ZPD (scaffolded, just-harder problems)

Generating all 4 lets the PM empirically determine the best fit per topic via review ratings.

### Why concurrency=3?

OpenAI's `gpt-4o-mini` allows ~5 concurrent requests per API key for this tier. We use 3 workers to:
- Stay well under rate limits
- Leave headroom for other API calls (web app, testing)
- Complete 40 generations in ~15 minutes instead of ~60 minutes sequential

### Why skip-existing + resume?

Idempotency is a first-principle for batch pipelines. If a generation fails mid-batch (network error, API timeout), re-running the script should not regenerate already-successful files. This mirrors the **at-least-once delivery with deduplication** pattern from distributed systems.

### Why file-per-dimension naming?

```
{slug}_output.json              # Default
{slug}_storyteller_output.json  # Cultural Storyteller
{slug}_visual_output.json       # Visual-First
{slug}_zpd_output.json          # ZPD Adaptive
```

This naming scheme:
- Makes dimension explicit in the filesystem
- Allows the web UI to discover available dimensions via glob
- Prevents accidental overwrites between runs

## Consequences

### Positive
- Empirical A/B testing of pedagogical approaches
- Scalable to new topics (add topic to list, run batch script)
- Resume capability handles partial failures gracefully

### Negative
- **Cost:** 40 topics × 4 dimensions × 2 LLM calls = 320 API calls per full batch
- **Storage:** 40 JSON files (~20KB each) + raw HTML + adapted markdown = ~3MB per batch
- **Time:** ~15 minutes at 3-worker concurrency; sequential would be ~60 minutes

## Alternatives Considered

| Alternative | Rejected Because |
|-------------|-----------------|
| Single prompt with "hybrid" instructions | Dilutes each pedagogical approach. A prompt trying to be both visual AND story-driven produces mediocre versions of both. |
| Generate on-demand per topic | Does not enable cross-topic comparison or batch analytics. |
| More than 4 dimensions | Diminishing returns. 4 covers the major learning-science paradigms; adding more fragments the PM's attention. |

## Implementation

- `scripts/batch_generate_optimized.py`: ThreadPoolExecutor orchestrator
- `web/main.py`: `_list_topics()` groups multi-prompt files; `topic_page()` accepts `?prompt=` param
- `web/templates/topic.html`: Dimension switcher badges
- `web/templates/review.html`: Dimension switcher for review context

## References

[^1]: Rosenshine, B. (2012). Principles of Instruction: Research-Based Strategies That All Teachers Should Know. *American Educator*, 36(1), 12-19.
[^2]: Lave, J., & Wenger, E. (1991). *Situated Learning: Legitimate Peripheral Participation*. Cambridge University Press.
[^3]: Bruner, J. S. (1966). *Toward a Theory of Instruction*. Harvard University Press.
[^4]: Vygotsky, L. S. (1978). *Mind in Society: The Development of Higher Psychological Processes*. Harvard University Press.
