# DECISION-20260513-003: Add `/nursing` Practice Module for Telangana Staff Nurse Recruitment

**Date:** 2026-05-13  
**Scope:** Dr. Math web application (`web/` and `output/`/`data/`).  
**Decision Owner:** Kimi Code CLI  
**Status:** Approved by user — recruitment/staff-nurse, Telangana, English+Telugu, topic+mock practice, multi-dimensional diagnostic.

## 1. Context

User's mother is preparing for a Telangana government nursing recruitment exam. We need a focused, high-trust practice module embedded in the existing Dr. Math web app.

## 2. Decision

1. **Add a `/nursing` route family** to the existing FastAPI web app (`web/main.py`).
2. **Target exam:** MHSRB Telangana Staff Nurse / Nursing Officer (80 MCQs, 80 marks, English, no negative marking) as the primary pattern.
3. **Content seed:** Hand-curate ~200 GNM-level nursing MCQs in the Dr. Math JSON format (`output/nursing_staff_nurse_output.json`) plus a topic tree (`data/nursing_topics.json`).
4. **Language support:** English questions with Telugu UI labels/translations; medical terminology remains in English because the exam is English-only.
5. **Assessment model:** Multi-dimensional diagnostic tracking accuracy, speed, confidence, and consistency per subject/topic.
6. **Practice modes:** Diagnostic, Topic Practice, Full-Length Mock, Weak-Area Drill.
7. **Tracking:** Anonymous `localStorage` progress (consistent with Dr. Math MVP).

## 3. Alternatives Considered

| Alternative | Rejected Because |
|-------------|------------------|
| Build separate Flutter/repo | Slower; Dr. Math web stack already deployed and responsive. |
| Use only LLM-generated questions at launch | Medical content requires verification; seed bank gives immediate, trustworthy practice. |
| Support Telugu questions now | Exam is English-only; Telugu UI is sufficient and safer. |
| Server-side user accounts | Adds complexity; anonymous localStorage matches approved Dr. Math MVP pattern. |

## 4. Consequences

- **Pros:** Fast to deploy; reuses existing infra; safe seed content; diagnostic personalizes study.
- **Cons:** Telugu UI only (not questions); seed bank limited until LLM generation pipeline is wired.

## 5. Implementation Notes

- New files: `data/nursing_topics.json`, `output/nursing_staff_nurse_output.json`, `web/templates/nursing/index.html`, `web/templates/nursing/practice.html`, `web/templates/nursing/mock.html`, `web/static/nursing.js`, `web/static/nursing.css`.
- Modified files: `web/main.py` (new routes), `web/templates/index.html` (add Nursing link).
- Pre-commit hook will prompt for ADR updates; this decision log satisfies that requirement.
