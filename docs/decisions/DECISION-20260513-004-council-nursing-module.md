# DECISION-20260513-004: Council of Ten — Add `/nursing` Module to Dr. Math

**Date:** 2026-05-13  
**Scope:** Dr. Math web application — new nursing recruitment practice module  
**Risk Level:** Medium  
**Final Decision:** Approved with revisions  

---

## Phase 1: Proposal

**PROPOSAL:** Add a `/nursing` practice module to the existing Dr. Math FastAPI web app for a Telangana government staff-nurse recruitment candidate.

**RATIONALE:**
- The user's mother needs a focused, browser-based practice tool for the MHSRB Telangana Staff Nurse / Nursing Officer recruitment exam.
- Reusing the existing Dr. Math web stack (FastAPI + Jinja2 + SQLite + Docker + nginx) is faster and cheaper than a separate app.
- A SOLID-driven sub-package (`web/routers/nursing.py`, `web/services/`, `web/repositories/`, `web/domain/`) keeps the change isolated and extensible.
- A hand-curated seed question bank (~200 MCQs) provides immediate, trustworthy practice while an LLM generation pipeline is prepared for later expansion.
- Multi-dimensional diagnostic (accuracy, speed, confidence, consistency) identifies weak and fast areas.
- Anonymous `localStorage` progress tracking matches the approved Dr. Math MVP pattern.

**HIGH-LEVEL DESIGN:**
1. `data/nursing_topics.json` — topic tree for MHSRB syllabus.
2. `output/nursing_staff_nurse_output.json` — seed MCQ bank.
3. `web/domain/models.py` + `web/domain/constants.py` — Pydantic models and exam config.
4. `web/repositories/question_repository.py` — abstraction over JSON/DB/LLM sources.
5. `web/services/{diagnostic_service,practice_service,mock_test_service,adaptive_queue}.py` — business logic.
6. `web/routers/nursing.py` — HTTP endpoints.
7. `web/templates/nursing/*.html` + `web/static/nursing/*` — UI.
8. `web/main.py` — registers the nursing router.

---

## Phase 2: Asynchronous Deliberation

### 1. Research Scientist
**ENDORSE** — The BFS note (`bfs-06-telangana-staff-nurse-landscape.md`) already cites multiple secondary sources and one primary source (INC GNM syllabus PDF). The MHSRB pattern is well-attested across coaching aggregators.  
**CONCERN (non-blocking)** — We still lack an official MHSRB notification PDF for the latest cycle. The seed bank must be labelled "syllabus-derived" until official PYQs are sourced.

### 2. First-Principles Engineer
**ENDORSE** — The decomposition is sound: exam → subjects → topics → subtopics → concepts → MCQs. The adaptive queue derives from the axiom that practice should be personalised by demonstrated capability, not fixed difficulty levels.  
**CONCERN (non-blocking)** — "Confidence" self-report is subjective. We should validate whether it improves prediction beyond accuracy + speed.

### 3. Distributed Systems Architect
**ENDORSE** — Stateless API endpoints + static JSON file repo + client-side progress storage is a simple, scalable pattern for a single-user-at-a-time study tool. No shared mutable state.  
**CONCERN (non-blocking)** — If we later add server-side progress, we must migrate `localStorage` carefully to avoid data loss.

### 4. Infrastructure-First SRE
**ENDORSE** — Reuses existing Docker/nginx/SQLite infra. No new runtime dependencies.  
**CONCERN (blocking?)** — We need at least one metric/observability hook: log how many diagnostic/practice/mock sessions run, and how many 404s occur on nursing routes. Without this we cannot detect breakage.  
**RESOLVED** — Proposal revised to include structured logging via the existing `Generation`/pipeline logger or FastAPI middleware, plus a `/nursing/status` health endpoint.

### 5. Diagnostic Problem-Solver
**ENDORSE** — Root cause is clear: the user's mother lacks a personalised, high-quality practice tool. This treats the root cause, not the symptom.  
**CONCERN (non-blocking)** — Edge case: what if `localStorage` is cleared? We should warn the user and export/import progress. Also, what if the seed bank has a wrong answer? We need a "report question" mechanism.

### 6. Ethical Technologist
**ENDORSE** — Anonymous tracking respects privacy. Medical content is handled cautiously with hand-curated seeds.  
**CONCERN (non-blocking)** — Nursing exam is high-stakes. We must add a disclaimer that this is a practice aid, not a substitute for textbooks or official notifications. Also, Telugu UI support improves accessibility.

### 7. Resource Strategist
**ENDORSE** — TCO is low: no new dependencies, no new VM, no API calls in v1. Development cost is front-loaded in seed curation.  
**CONCERN (non-blocking)** — Seed curation of 200 MCQs is labour-intensive. Could we start with 100 high-impact questions and expand?  
**RESOLVED** — Proposal revised: Phase 1 target is 100 verified MCQs across high-weight subjects; Phase 2 adds 100 more.

### 8. Curious Explorer
**ENDORSE** — The multi-dimensional diagnostic is a natural experiment. We can log per-topic accuracy/speed and learn which dimensions actually predict exam readiness.  
**CONCERN (non-blocking)** — Propose an experiment: after 50 practice sessions, correlate diagnostic capability map with mock-test scores to validate the model.

### 9. Clarity-Driven Communicator
**BLOCK** — The BFS research note exists, but no formal ADR has been written yet. Also, the folder structure must be documented in `AGENTS.md` or a `README` so future contributors know where to add nursing code.  
**RESOLVED** — Proposal revised: write `docs/adrs/ADR-004-nursing-module.md` and update `docs/decisions/DECISION-20260513-003-telangana-nursing-module.md` before code. Add a short `web/nursing/README.md` for folder conventions.

### 10. Inner-Self Guided Builder
**ENDORSE** — This serves the user's deeper need: helping his mother qualify with dignity and confidence. Building it inside Dr. Math also honours the existing investment.  
**CONCERN (non-blocking)** — Ensure the UI is calm and non-overwhelming for an adult learner. Avoid gamification that feels childish.

---

## Phase 3: Blocking Check

- **Clarity-Driven Communicator BLOCKED** due to missing ADR and folder documentation.
- **Resolution:** Revised proposal includes writing ADR-004 and a `web/nursing/README.md` before any implementation code.
- No other blocking concerns remain.

---

## Phase 4: Consensus Round

All non-blocking concerns were addressed by revising the proposal:
1. Seed bank labelled syllabus-derived until official PYQs sourced.
2. Include `/nursing/status` health endpoint + structured session logging.
3. Reduce Phase 1 seed target from 200 to 100 verified MCQs.
4. Add medical disclaimer and "report question" UI.
5. Validate diagnostic dimensions through later experiment.
6. Ensure adult-appropriate UI design.

No persona dissents after revisions.

---

## Phase 5: Final Decision

**DECISION:** Approved  
**FINAL PROPOSAL:** Add a SOLID-structured `/nursing` module to Dr. Math for Telangana staff-nurse recruitment practice. Begin with 100 verified MCQs, multi-dimensional diagnostic, topic practice, and full-length mock. Write ADR-004 and `web/nursing/README.md` before implementation. Include health endpoint, session logging, disclaimer, and report-question feature.  
**DISSENT RECORDED:** None.  
**RATIONALE:** The proposal addresses the root cause with low TCO, respects privacy, reuses existing infra, and includes safeguards for high-stakes medical content. All blocking concerns resolved by documentation and observability commitments.

---

## Phase 6: Documentation Action Items

- [x] BFS research note: `docs/research/bfs/bfs-06-telangana-staff-nurse-landscape.md`
- [x] Council decision log: `docs/decisions/DECISION-20260513-004-council-nursing-module.md`
- [ ] ADR: `docs/adrs/ADR-004-nursing-module.md`
- [ ] Folder README: `web/nursing/README.md`
- [ ] Implementation code
- [ ] Tests / smoke checks
- [ ] Update `docs/decisions/INDEX.md`
