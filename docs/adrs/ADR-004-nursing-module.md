# ADR-004: Add `/nursing` Practice Module for Telangana Staff Nurse Recruitment

**Date:** 2026-05-13  
**Status:** Approved by Council of Ten (`DECISION-20260513-004`)  
**Author:** Kimi Code CLI  
**Supersedes / amends:** None  

## Context

Dr. Math currently serves Class VII adaptive math practice. The user's mother is preparing for the Telangana government staff-nurse recruitment examination. We need to extend the platform with a nursing-focused practice module while preserving the existing math functionality.

## Decision

Add a self-contained `/nursing` module to the Dr. Math FastAPI application with the following characteristics:

1. **SOLID package layout** under `web/`:
   - `web/routers/nursing.py` — HTTP endpoints.
   - `web/services/` — business logic (diagnostic, practice, mock, adaptive queue).
   - `web/repositories/question_repository.py` — data access abstraction.
   - `web/domain/models.py` + `web/domain/constants.py` — domain models and exam config.
   - `web/templates/nursing/` — Jinja2 templates.
   - `web/static/nursing/` — JS/CSS assets.

2. **Target exam pattern:** MHSRB Telangana Staff Nurse / Nursing Officer (80 MCQs, 80 marks, 60 min, English only, no negative marking), with syllabus expansion for TSPSC if needed later.

3. **Content strategy:**
   - Phase 1: 100+ hand-curated, reviewed MCQs sourced from the INC GNM syllabus.
   - Phase 2: LLM-generated questions with mandatory review before promotion to verified.
   - Every question carries `verification_status`, `source`, `concept_tag`, `verified_by`, and `last_reviewed`.
   - Questions are tagged with `cognitive_level` (remember/understand/apply/analyze) and `context` (theory/scenario/calculation) to support topic-wise practice in different dimensions.

4. **Adaptive assessment:**
   - Multi-dimensional diagnostic measuring accuracy, speed, confidence, and consistency.
   - Capability map stored in browser `localStorage`.
   - Weak-area drill and adaptive topic practice.

5. **Practice modes:**
   - Diagnostic test.
   - Topic-wise practice.
   - Full-length mock test (80 questions / 60 minutes).

6. **Observability & safety:**
   - `/nursing/status` health endpoint.
   - Structured session logging.
   - Medical disclaimer and "Report question" UI.

## Consequences

### Positive
- Reuses deployed Dr. Math infrastructure; no new runtime cost.
- Isolated package means Dr. Math math logic is untouched.
- Hand-curated seed content reduces medical-safety risk at launch.
- Multi-dimensional diagnostic personalises study better than random practice.

### Negative
- Adds maintenance surface: two parallel content pipelines (math + nursing).
- Telugu UI support is limited to labels, not question text, because the exam is English-only.
- Seed bank is small until LLM pipeline is wired and reviewed.

## Alternatives Considered

| Alternative | Why Not Chosen |
|-------------|----------------|
| Separate Flutter/repo | Higher TCO and slower delivery. |
| Pure LLM-generated content at launch | Medical content requires verification; unsafe. |
| Server-side user accounts | Adds stateful complexity beyond MVP needs. |
| TSPSC-only pattern | User confirmed MHSRB-style staff-nurse recruitment; TSPSC kept as future expansion. |

## Compliance

- Follows Research-First Covenant: BFS (`bfs-06`), DFS (`dfs-05`, `dfs-06`), Council decision (`DECISION-20260513-004`), then code.
- Follows 10-Persona Filter: privacy (anonymous), observability (logging), TCO (reuse), safety (verification), clarity (ADR + README).

## Implementation Notes

- 2026-05-13: Domain models and constants added with `cognitive_level`, `context`, and `format` dimension tags.
- 2026-05-13: `JsonFileQuestionRepository` added with filtering by subject, topic, cognitive level, context, difficulty, and concept tag.
- 2026-05-13: Adaptive queue service added for accuracy/speed/confidence/consistency scoring.
- 2026-05-13: `web/nursing/README.md` added documenting package conventions.
- 2026-05-13: `web/services/nursing_service.py` added with diagnostic, practice, mock, capability, PDF export, and report services.
- 2026-05-13: `web/routers/nursing.py` added and included in `web/main.py`; exposes `/nursing` HTML routes and `/api/nursing` JSON endpoints.
- 2026-05-13: Phase 3 UI added: Jinja2 templates, mobile-first CSS, vanilla JS session logic, Telugu glossary tooltips, and `localStorage` progress.
- 2026-05-13: Phase 4 E2E test added covering diagnostic → analysis → weak-area practice → mock → PDF → report.

## References

- `docs/research/bfs/bfs-06-telangana-staff-nurse-landscape.md`
- `docs/research/dfs/dfs-05-nursing-diagnostic-model.md`
- `docs/research/dfs/dfs-06-nursing-content-verification.md`
- `docs/research/dfs/dfs-08-nursing-question-dimensions.md`
- `docs/research/bfs/bfs-09-phase-0-granular-plan.md`
- `docs/decisions/DECISION-20260513-004-council-nursing-module.md`
- Indian Nursing Council, *GNM Syllabus*, 2015. https://www.iminursing.in/gnm-syllabus.pdf
