# Dr. Math Adaptive Engine Design

## Research-Driven Architecture

---

## The Core Problem (What the User Wants)

> "There is a mark. When a kid runs out of time or can't solve it, the next question should adapt. Questions customize according to the kid's brain and how it's evolving."

**Translation:** A continuous adaptive assessment system that tracks multiple dimensions of a child's performance and selects the next question dynamically — no rigid levels, no forced progression.

---

## Architecture: The "Mark" System

### What is a "Mark"?

A Mark is a **multi-dimensional state vector** representing a child's current capability:

```json
{
  "student_id": "student_123",
  "topic": "integers",
  "dimensions": {
    "accuracy_rate": 0.72,
    "avg_response_time_ms": 45000,
    "hints_needed_ratio": 0.15,
    "current_difficulty_estimate": 2.3,
    "mastery_level": "building",
    "last_error_type": "sign_confusion",
    "streak_correct": 2,
    "streak_wrong": 0,
    "confidence_trend": "rising"
  },
  "question_history": [
    {
      "question_id": "int_001",
      "correct": true,
      "time_ms": 32000,
      "hints_used": 0,
      "difficulty": 2,
      "error_type": null
    }
  ]
}
```

### Dimensions Tracked (Research-Backed)

| Dimension | Source | Why It Matters |
|-----------|--------|----------------|
| **Accuracy streak** | Bloom (1984) | 3 correct → harder; 2 wrong → easier |
| **Response time** | Murray & Arroyo (2002) | Fast + right = mastery; Slow + wrong = struggling |
| **Hints used** | Wood et al. (1976) | Hint vector (3,1,0,0) = mastery reached |
| **Error type** | ACEM (2024) | Same error twice → targeted micro-lesson |
| **Confidence** | Warshauer (2015) | Long pause + wrong = anxiety; Quick wrong = overconfidence |
| **Difficulty estimate** | Item Response Theory | Continuous ability score, not bucketed levels |

---

## The Adaptive Flow (No Rigid Levels)

```
┌─────────────────────────────────────────────────────────────┐
│  CHILD ANSWERS QUESTION N                                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  EVALUATE RESPONSE                                          │
│  ├── Correct? → accuracy +1, streak +1                      │
│  ├── Time? → compare to estimated_time                      │
│  ├── Hints? → track hint dependency                         │
│  └── Error type? → log misconception                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  UPDATE "MARK"                                              │
│  ├── Adjust difficulty_estimate (±0.1 to ±0.5)             │
│  ├── Update mastery_level (building/stretching/mastering)   │
│  └── Flag if spaced repetition needed                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  SELECT QUESTION N+1                                        │
│  ├── Same concept, simpler numbers? (if struggling)         │
│  ├── Same concept, harder variant? (if mastering)           │
│  ├── Prerequisite review? (if gap detected)                 │
│  ├── Targeted misconception? (if same error twice)          │
│  └── Interleaved review? (if spaced repetition due)         │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  PRESENT QUESTION N+1                                       │
│  └── Record start_time for timeout tracking                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Question Selection Algorithm

### Step 1: Calculate Adaptive Score

```python
def calculate_adaptive_score(mark, question_pool):
    """
    Score each candidate question based on how well it matches
    the child's current mark.
    """
    scores = []
    for q in question_pool:
        score = 0

        # Difficulty match (closer to estimate = better)
        score += 10 - abs(q.difficulty - mark.difficulty_estimate)

        # Penalize recently seen questions
        if q.id in mark.recent_questions:
            score -= 20

        # Boost questions targeting known misconceptions
        if q.misconception_tag == mark.last_error_type:
            score += 15

        # Boost prerequisite questions if gap detected
        if q.prerequisite in mark.known_gaps:
            score += 12

        # Time appropriateness
        if q.estimated_time <= mark.avg_response_time_ms * 1.2:
            score += 5

        scores.append((q, score))

    # Return highest-scoring question
    return max(scores, key=lambda x: x[1])[0]
```

### Step 2: Timeout Handling

```python
def handle_timeout(mark, current_question):
    """
    When a child runs out of time, DON'T mark as wrong immediately.
    Instead, adapt the next question based on timeout pattern.
    """
    if current_question.difficulty > mark.difficulty_estimate:
        # Timeout on hard question = expected, lower difficulty slightly
        mark.difficulty_estimate -= 0.1
        return "easier_variant"
    else:
        # Timeout on easy question = possible anxiety or distraction
        mark.confidence_trend = "anxious"
        return "same_difficulty_rephrased"
```

---

## Mastery Detection (Not Rigid Levels)

Instead of "Level 1, 2, 3, 4", we use a **continuous mastery spectrum**:

| State | Criteria | What Happens |
|-------|----------|--------------|
| **Exploring** | First 3 questions on topic | Full worked examples, high hint availability |
| **Building** | 60-70% accuracy, needs hints sometimes | Gradual fading of worked examples |
| **Stretching** | 70-85% accuracy, mostly independent | Mix of familiar and novel problems |
| **Mastering** | 85%+ accuracy, fast, no hints | Interleaved review + advanced applications |
| **Solid** | Consistent mastery over time | Spaced repetition only |

**Key:** A child can move back and forth between states. Mastery is not permanent without review.

---

## Data Model: The Builder Database

```json
{
  "students": {
    "student_id": {
      "marks": {
        "topic_slug": {
          "dimensions": {...},
          "history": [...],
          "mastery_state": "building",
          "last_session": "2026-05-03T10:00:00Z"
        }
      }
    }
  },
  "questions": {
    "question_id": {
      "topic": "integers",
      "difficulty": 2.3,
      "prerequisite": "number_line_basics",
      "misconception_tag": "sign_confusion",
      "estimated_time_ms": 45000,
      "adaptive_tags": ["visual", "multi_step", "word_problem"]
    }
  },
  "sessions": {
    "session_id": {
      "student_id": "...",
      "topic": "integers",
      "questions_asked": [...],
      "adaptation_log": [...],
      "prompt_id_used": "ebfbe654"
    }
  }
}
```

---

## Implementation Roadmap

### Phase 1: Static Adaptive (Now)
- Pre-generate question pools with research-backed prompts
- Tag questions with difficulty, prerequisites, misconceptions
- Simple adaptive selection based on accuracy streak

### Phase 2: Dynamic Adaptive (Next)
- Real-time mark updates during sessions
- Timeout detection and handling
- Interleaved spaced repetition

### Phase 3: Personalized Adaptive (Future)
- Student-specific misconception tracking
- Deep personalization (interests, pace, learning style)
- Predictive analytics (which topics will be hard next)

---

## Prompt Integration

Each prompt template from `PROMPT_TEMPLATES.md` generates questions with different **adaptive tags**:

| Prompt Template | Adaptive Focus | Question Tags Generated |
|-----------------|----------------|------------------------|
| ZPD Adaptive Tutor | Difficulty progression | `estimated_time`, `prerequisite`, `hint` |
| Productive Struggle Coach | Struggle timing | `struggle_time`, `worked_example` |
| Visual-First Thinker | Representation type | `visual_required`, `diagram_type` |
| Misconception Hunter | Error diagnosis | `misconception_tag`, `distractor_reason` |
| Mastery Tracker | Unit progression | `mastery_unit`, `mastery_criterion` |
| Cultural Storyteller | Context relevance | `story_context`, `cultural_element` |

---

## References

1. Bloom, B. S. (1984). The 2 Sigma Problem.
2. Vygotsky, L. S. (1978). Mind in Society.
3. Kapur, M. (2008). Productive Failure.
4. Murray & Arroyo (2002). ZPD in Adaptive Systems.
5. Sweller & Cooper (1985). Worked Examples.
6. Hamdan & Gunderson (2017). Number Lines.
7. ACEM (2024). Error Pattern Detection.
8. Black & Wiliam (1998). Formative Assessment.
