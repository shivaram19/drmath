# Bidirectional-06: Phase 6 Monitoring & Correlation Experiment Plan

**Date:** 2026-05-13  
**Scope:** How to monitor the nursing module after launch and validate that the adaptive model helps users improve.  
**Research Phase:** Bidirectional — impact analysis  

## Current State

- Question bank expanded from 104 to 130 verified MCQs across 11 subjects.
- Every question carries `verified_by`, `last_reviewed`, `source`, and a report path.
- Adaptive model computes priority scores from accuracy (50%), speed (25%), confidence gap (15%), and consistency (10%).

## What We Need to Learn

1. Do users actually practice their weak areas?
2. Does practicing weak areas improve mock scores over time?
3. Are the cognitive/context tags useful for learners?
4. Which questions get reported most often?

## Monitoring Plan

### 1. Session Logging

Record each completed session in `output/nursing_sessions.jsonl`:

```json
{
  "session_id": "uuid",
  "started_at": "ISO8601",
  "mode": "diagnostic|topic|mock",
  "attempts_count": 20,
  "score": 0.75,
  "weak_areas": ["ap_cardiovascular", "fn_vital_signs"],
  "user_agent": "..."
}
```

Implementation: add `SessionLogger` to `web/services/nursing_service.py` and call it on submission.

### 2. Weekly Review Dashboard

Create a small admin endpoint `/manager/nursing` that shows:
- Total sessions this week
- Most-reported questions
- Lowest-scoring topics
- Average mock score trend

### 3. Correlation Experiment

After 50+ distinct sessions:

- **Hypothesis:** Users whose second mock is preceded by at least one weak-area practice session improve more than users who only take mocks.
- **Metric:** Δ mock score = second_mock_score − first_mock_score.
- **Analysis:** Compare Δ for users with ≥1 weak-area practice vs. users with none.
- **Threshold:** A difference of ≥5 percentage points is educationally meaningful for a high-stakes exam.

### 4. Safety Monitoring

- Review reported questions within 48 hours.
- Flag questions where report rate > 2%.
- Re-verify flagged questions against INC GNM syllabus.

## References

- `docs/research/dfs/dfs-05-nursing-diagnostic-model.md`
- `docs/research/dfs/dfs-06-nursing-content-verification.md`
- `docs/adrs/ADR-004-nursing-module.md`
