# DFS-05: Multi-Dimensional Diagnostic Model for Nursing Exam Practice

**Date:** 2026-05-13  
**Scope:** Adaptive assessment engine inside the `/nursing` module.  
**Research Phase:** DFS — depth-first technology/pedagogy deep-dive  
**Author:** Kimi Code CLI  

## 1. Problem

A generic MCQ app gives every learner the same sequence. We need a diagnostic that quickly identifies:
- Which subjects/topics the candidate already knows.
- Which topics she can answer correctly but slowly (needs speed drills).
- Which topics she answers incorrectly (needs concept study).
- Which topics she is guessing on (low confidence/low accuracy).

## 2. First-Principles Derivation

The goal of practice is to maximise expected exam score. For a multiple-choice exam with no negative marking (MHSRB pattern), expected score is:

```
E[score] = Σᵢ P(correctᵢ)
```

To maximise it, allocate study time to topics where `P(correct)` can be improved most per unit time. Therefore the diagnostic must estimate `P(correct)` and `learning rate` per topic.

We cannot directly observe learning rate, but we can observe proxies:
1. **Accuracy** — observed `P(correct)`.
2. **Speed** — time per question; slow accuracy suggests partial fluency.
3. **Confidence** — self-reported certainty; large accuracy-confidence gap reveals illusion of knowing.
4. **Consistency** — variance across similar questions; high variance suggests unstable knowledge.

## 3. Dimensions & Definitions

| Dimension | Measured As | Interpretation |
|-----------|-------------|----------------|
| **Accuracy** | `correct / attempted` | Current knowledge level. |
| **Speed** | median seconds per correct answer | Fluency; exam is 60 min / 80 Q = 45 s/Q. |
| **Confidence** | self-report 1–5 after each answer | Metacognitive awareness. |
| **Consistency** | standard deviation of accuracy over last N questions on topic | Stable vs. fragile knowledge. |

## 4. Capability Map Algorithm (v1)

For each subject/topic, compute a 4-tuple `(accuracy, speed_score, confidence_accuracy_gap, consistency_score)`.

### Speed score
```
speed_score = clamp(1 - (median_seconds - target_seconds) / target_seconds, 0, 1)
target_seconds = 45   # MHSRB: 60 min / 80 Q
```

### Confidence-accuracy gap
```
gap = |mean_confidence - accuracy|
```
High gap → candidate either overconfident or underconfident on that topic.

### Consistency score
```
consistency_score = 1 - std_dev_accuracy   # over last 5 questions
```

### Topic priority score (what to study next)
```
priority = (1 - accuracy) * w1 + (1 - speed_score) * w2 + gap * w3 + (1 - consistency_score) * w4
```
Default weights: `w1=0.5, w2=0.25, w3=0.15, w4=0.10`. Weights can be tuned after data.

## 5. Diagnostic Test Design

- **Length:** 20 questions (one per high-weight subtopic).
- **Rules:**
  - No hints during diagnostic.
  - Record time per question.
  - Ask confidence after each answer.
  - Stop a subject early if accuracy is clearly very high or very low (adaptive shortening).
- **Output:** A heatmap stored in `localStorage` under `nursing_capability_map`.

## 6. Validation Experiment

After 50 practice sessions, correlate the diagnostic priority score with subsequent mock-test score improvement per topic. If correlation < 0.3, drop the confidence dimension or retune weights.

## 7. Relation to Research

- **Self-regulated learning** literature shows confidence calibration improves study allocation [^1].
- **Spaced repetition** algorithms (SM-2, FSRS) optimise retention; our priority score optimises short-term score gain [^2].
- **Item Response Theory** would be ideal but overkill for v1; we use a heuristic approximation [^3].

## 8. References

[^1]: Dunlosky, J., & Rawson, K. A. (2012). Overconfidence produces underachievement: Inaccurate self evaluations undermine students' learning and retention. *Learning and Instruction*, 22(4), 271–280.
[^2]: Wozniak, P. A., & Gorzelanczyk, E. J. (1994). Optimization of repetition spacing in the practice of learning. *Acta Neurobiologiae Experimentalis*, 54, 59–69.
[^3]: Hambleton, R. K., Swaminathan, H., & Rogers, H. J. (1991). *Fundamentals of Item Response Theory*. Sage.
