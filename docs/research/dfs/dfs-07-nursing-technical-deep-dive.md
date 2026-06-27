# DFS-07: Technical Deep-Dive — `/nursing` Module Architecture

**Date:** 2026-05-13  
**Scope:** Detailed technical design for the nursing practice module.  
**Research Phase:** DFS — depth-first architecture and implementation deep-dive  
**Author:** Kimi Code CLI  

## 1. Technology Choices

| Layer | Choice | Rationale |
|-------|--------|-----------|
| Web framework | FastAPI (existing) | Reuse Dr. Math stack; no new dependency. |
| Templating | Jinja2 (existing) | Server-side rendering keeps v1 simple. |
| Data store | Static JSON + localStorage | No DB migration needed; anonymous by design. |
| CSS | Vanilla CSS (existing style.css base) | No new build step. |
| JS | Vanilla ES6 | No framework; keep bundle tiny. |
| PDF export | `fpdf2` or WeasyPrint | `fpdf2` is lighter and sufficient for simple MCQ PDFs. |

**TCO note:** `fpdf2` adds one small dependency. Alternative: generate a simple HTML page with print stylesheet (zero dependency). We will evaluate in Phase 1.

## 2. Data Model Detail

### Question
```json
{
  "id": 1,
  "subject_id": "anatomy_physiology",
  "topic_id": "ap_cardiovascular",
  "concept_tag": "normal blood pressure",
  "difficulty": 1,
  "question": "What is the normal adult blood pressure?",
  "options": ["A) 90/60 mmHg", "B) 120/80 mmHg", "C) 140/90 mmHg", "D) 100/70 mmHg"],
  "correct_answer": "B",
  "explanation": "Normal adult blood pressure is approximately 120/80 mmHg.",
  "telugu_hint": "సాధారణ వయస్కుడి రక్తపోటు సుమారు 120/80 mmHg.",
  "source": "INC GNM Syllabus / Anatomy & Physiology",
  "verification_status": "reviewed",
  "verified_by": "GNM textbook cross-check",
  "last_reviewed": "2026-05-13"
}
```

### Capability Map (localStorage)
```json
{
  "subjects": {
    "anatomy_physiology": {
      "accuracy": 0.75,
      "speed_score": 0.60,
      "confidence_gap": 0.15,
      "consistency_score": 0.80,
      "priority_score": 0.32
    }
  },
  "topics": { ... }
}
```

### Attempt Log (localStorage)
```json
[
  {
    "question_id": 1,
    "selected_option": "B",
    "is_correct": true,
    "time_seconds": 12.5,
    "confidence": 4,
    "subject_id": "anatomy_physiology",
    "topic_id": "ap_cardiovascular",
    "timestamp": "2026-05-13T10:00:00Z"
  }
]
```

## 3. Adaptive Algorithm Detail

For each subject/topic with attempts `a_1...a_n`:

```
accuracy = correct / n
median_time = median(time for correct attempts) or median(all times)
speed_score = clamp(1 - (median_time / 45 - 1)^2, 0, 1)
mean_confidence = mean(confidence)  # 1-5 scale
norm_confidence = (mean_confidence - 1) / 4
confidence_gap = |norm_confidence - accuracy|
std_dev = sqrt(variance of last 5 correctness values)
consistency_score = 1 - std_dev
priority = (1-accuracy)*0.5 + (1-speed)*0.25 + gap*0.15 + (1-consistency)*0.10
```

**Validation hook:** After 50 sessions, compute Pearson correlation between `priority_score` and subsequent mock-score delta. If `r < 0.2`, disable confidence dimension.

## 4. API Contract

### GET `/api/nursing/topics`
Returns subject/topic tree with question counts.

### POST `/api/nursing/diagnostic/start`
Request: `{ "per_subject": 2 }`  
Response: `{ "questions": [...], "duration_seconds": 1200 }`

### GET `/api/nursing/questions?subject=...&topic=...&limit=...`
Response: `{ "questions": [...] }`

### POST `/api/nursing/mock/start`
Response: `{ "questions": [...80...], "duration_seconds": 3600 }`

### POST `/api/nursing/report`
Request: `{ "question_id": 1, "reason": "incorrect answer" }`  
Response: `{ "status": "recorded" }`

### GET `/api/nursing/pdf?subject=...&topic=...`
Response: PDF bytes.

## 5. Security & Privacy

- No PII collected.
- All progress in browser `localStorage`.
- Report endpoint logs only question_id + reason; no user identity.
- No user-generated content stored on server except report logs.

## 6. Performance Budget

- Page first paint: < 2s on 3G.
- Question JSON payload: < 100 KB for 80 questions.
- localStorage limit: ~5 MB; attempt log will be pruned to last 500 entries.

## 7. Failure Modes

| Failure | Mitigation |
|---------|------------|
| Seed bank JSON corrupted | Validate on load; fallback to empty state with user message. |
| localStorage cleared | Warn user; offer JSON export/import. |
| PDF generation fails | Fallback to printable HTML page. |
| Wrong answer in bank | Report button + periodic audit. |

## 8. References

- `docs/research/dfs/dfs-05-nursing-diagnostic-model.md`
- `docs/research/dfs/dfs-06-nursing-content-verification.md`
- `docs/research/bfs/bfs-07-nursing-module-implementation-plan.md`
