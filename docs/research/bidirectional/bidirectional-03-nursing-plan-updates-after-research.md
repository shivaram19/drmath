# Bidirectional-03: Plan Updates After Research Validation

**Date:** 2026-05-13  
**Scope:** Revise the `/nursing` implementation plan based on internet research and first-principles introspection.  
**Research Phase:** Bidirectional — cross-domain impact analysis  
**Author:** Kimi Code CLI  

## 1. Unknowns Investigated

| Unknown | Finding | Impact on Plan |
|---------|---------|----------------|
| Is MHSRB the right body? | Confirmed. MHSRB Telangana Nursing Officer 2025: 80 MCQs, 60 min, English only, no negative marking, 2322 vacancies, final merit list April 2026 [^1]. | Continue targeting MHSRB pattern; TSPSC kept as future expansion. |
| Are official PYQs freely available? | Testbook and coaching sites host MHSRB previous papers, likely behind paywalls. No freely downloadable official PDF found. | Seed bank remains syllabus-derived; Phase 6 will attempt to source or purchase official PYQs. |
| Does bilingual support help? | Bilingual MCQ books/apps are widespread in India (Hindi/English, Assamese/English) [^2][^3]. No peer-reviewed RCT found in quick search, but construct validity suggests reducing language load improves comprehension [^4]. | Add optional Telugu tooltips/translations for difficult terms, but keep the canonical question text in English. |
| Is the 4D adaptive model valid? | Research supports targeted weak-area practice and immediate feedback [^5][^6]. However, confidence calibration can be noisy [^7]. | Keep the model but make weights configurable and add an experiment to validate correlation with mock-score improvement. |
| Are there open nursing datasets? | MedMCQA is for medical (MBBS) entrance, not nursing recruitment [^8]. Nurseslabs is US-centric and free [^9]. Nothing matches MHSRB. | Build our own verified seed bank; do not rely on external datasets. |
| Is the SOLID structure overkill? | FastAPI best practices endorse modular routers/services for maintainability [^10][^11]. However, for a prototype, the folder depth can be reduced. | Keep modular separation but flatten slightly; avoid premature abstraction. |

## 2. First-Principles Changes

### Change A: Simplify folder structure
**Original:** `web/services/{diagnostic,practice,mock,adaptive}.py` + `web/repositories/`
**Revised:** Keep `web/routers/nursing.py`, `web/services/nursing.py` (all business logic), `web/repositories/nursing_repository.py`, `web/domain/nursing_models.py`. This reduces file count while preserving separation of concerns.

**Rationale:** The Council wanted SOLID, but SOLID does not require maximal file splitting. A single service module per feature is still single-responsibility if its public functions are cohesive.

### Change B: Add Telugu glossary/tooltips
**Original:** Telugu only in UI labels.
**Revised:** Add a `telugu_hint` field to selected difficult questions and a glossary JSON mapping common medical terms to Telugu.

**Rationale:** The exam is English-only, but comprehension support reduces extraneous cognitive load without changing the canonical question [^4].

### Change C: Make the adaptive model simpler and measurable
**Original:** 4-dimensional heuristic with fixed weights.
**Revised:** Keep accuracy (50%) and speed (25%) as primary; make confidence (15%) and consistency (10%) optional toggles. After 50 practice sessions, run a correlation check between priority scores and subsequent mock improvement.

**Rationale:** Accuracy + speed are directly observable. Confidence is subjective and should be validated before being treated as reliable.

### Change D: Add a static fallback export
**Original:** Web-only practice.
**Revised:** Add a "Download practice PDF" button that generates a simple A4 PDF of weak-area questions for offline study.

**Rationale:** If internet is unreliable or the mother prefers paper, she can still practice. This maximises the probability of exam pass, which is the first-principles goal.

### Change E: Stricter content verification workflow
**Original:** Questions marked `reviewed`.
**Revised:** Add `verified_by` and `last_reviewed` fields. Every clinical fact must map to a source concept. The "Report question" feature is mandatory, not optional.

**Rationale:** High-stakes medical content requires transparent provenance [^6].

## 3. Updated Phase Plan

| Phase | Focus | Test Gate |
|-------|-------|-----------|
| 0 | Foundation: models, repository, 104-Q seed bank | Repository parses all Qs; Pydantic valid |
| 1 | Single `nursing_service.py` with diagnostic/adaptive/practice/mock | Unit tests pass |
| 2 | `nursing.py` router + `/api/nursing/*` endpoints | Integration tests pass |
| 3 | UI templates + JS/CSS + Telugu glossary | Pages render; no console errors |
| 4 | E2E flow + PDF export | E2E tests pass; PDF generates |
| 5 | Docker deploy | Live status healthy |
| 6 | Expand to 200+ Qs + source verification + analytics | Log review clean |

## 4. References

[^1]: Careers360, "MHSRB Telangana Staff Nurse Recruitment 2025: Final Merit List", 2026. https://medicine.careers360.com/articles/mhsrb-telangana-nursing-officer-recruitment
[^2]: Amazon India, bilingual MCQ books for UPHESC Assistant Professor.
[^3]: 50000+ Assam GK Bilingual MCQ app.
[^4]: ResearchGate, "Validating MCQs: A Critical Step in Specialist Training", 2025. https://www.researchgate.net/publication/386549283_Validating_MCQs_A_Critical_Step_in_Specialist_Training
[^5]: Academic Medicine, "Two-Phase Individual Assessments: A Second-Chance Assessment Strategy With Individualized Feedback", 2024.
[^6]: ResearchGate, "Promoting Deep Learning Through Higher-Order Thinking Questions", 2025.
[^7]: Dunlosky & Rawson (2012). Overconfidence produces underachievement. *Learning and Instruction*.
[^8]: GitHub, medmcqa/medmcqa — Medical MCQ dataset.
[^9]: Nurseslabs, "Nursing Test Bank: Free Practice Questions".
[^10]: Restack, "FastAPI Best Folder Structure".
[^11]: GitHub, Irfanakbari/python-fastapi-best-practice.
