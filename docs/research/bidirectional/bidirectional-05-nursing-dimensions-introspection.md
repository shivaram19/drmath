# Bidirectional-05: Introspection — Did "Different Dimensions" Overcomplicate the Plan?

**Date:** 2026-05-13  
**Scope:** Re-examine the dimensions framework after the user's clarification.  
**Research Phase:** Bidirectional — meta-cognitive impact analysis  
**Author:** Kimi Code CLI  

## 1. What the User Actually Said

> "it's not entirely about exams , it's also topic wise questions asked in differnt dimensions"

Translation: The app should support **topic-wise practice** where questions are asked in **different ways/dimensions** — not just exam-simulation.

## 2. What I Did (Retrospect)

I immediately jumped to a 4-dimensional framework:
- Cognitive level (Bloom's)
- Question format (MCQ, T/F, etc.)
- Context (theory, scenario, etc.)
- Difficulty

This is comprehensive, but is it **necessary** for v1?

## 3. New Unknowns

### Unknown 1: Does "different dimensions" mean multiple formats or multiple cognitive levels?
The user might mean:
- (a) Same topic, different question types (MCQ, T/F, scenario).
- (b) Same topic, different depths of thinking (recall vs. application).
- (c) Same topic, different contexts (adult, child, emergency).
- (d) All of the above.

### Unknown 2: Is multi-format support worth the UI complexity?
True/False and fill-in-the-blank require different UI components, scoring logic, and answer validation. For a v1, this may be over-engineering.

### Unknown 3: Do different question formats actually improve exam performance?
Research is mixed. Active recall is well-supported, but the *format* of active recall matters less than the *effort* and *feedback*.

### Unknown 4: Can I tag 104 questions accurately without manual effort?
Manual tagging is error-prone and time-consuming. Heuristic tagging is faster but less precise.

### Unknown 5: Will the mother use format selection, or does she just want "more questions on this topic"?
A busy adult learner may not care about Bloom's taxonomy. She may simply want: "Show me questions on Midwifery."

## 4. First-Principles Reframing

The core need is **topic-wise mastery**. Dimensions are a *means*, not an end. The simplest version is:

> "Pick a topic → answer questions on that topic → get feedback → repeat."

Everything else is enrichment. If enrichment adds friction without proven benefit, it should be deferred.

## 5. Hypothesis

**Minimal viable v1:**
- Keep all questions as MCQ (matches the exam).
- Tag each question with `cognitive_level` (remember/understand/apply) and `context` (theory/scenario/calculation).
- UI filters: by topic, optionally by cognitive level.
- No true/false, fill-in-blank, or matching in v1.

This gives "different dimensions" without multiplying UI complexity.

## 6. What I Need to Validate

1. Evidence for/against multi-format practice in nursing/medical education.
2. Evidence that cognitive-level tagging helps learners.
3. Whether heuristic tagging is acceptable for a seed bank.
