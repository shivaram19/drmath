# BFS-07: `/nursing` Module — End-to-End Implementation Plan

**Date:** 2026-05-13  
**Scope:** Build the Telangana Staff Nurse practice module inside Dr. Math, phase by phase, with a test gate after each phase.  
**Research Phase:** BFS — implementation planning  
**Author:** Kimi Code CLI  
**Updated by:** `bidirectional-03-nursing-plan-updates-after-research.md`, `dfs-08-nursing-question-dimensions.md`

## 0. Principles Governing This Plan

1. **One phase, one test gate.** No phase is considered complete until its smoke test passes.
2. **Dr. Math math pipeline remains untouched.** All nursing code lives in isolated `web/nursing/` paths or clearly named `nursing_*` files.
3. **Modular but not over-engineered.** Use FastAPI `APIRouter`, a single service module, and a single repository module.
4. **No runtime LLM calls in v1.** The seed bank is static JSON.
5. **Medical content provenance.** Every clinical question maps to a source concept and includes a "Report question" feature.
6. **MCQ-first, topic-wise practice.** After research, v1 keeps MCQ only and adds lightweight `cognitive_level` + `context` tags instead of supporting multiple question formats. See `dfs-08-nursing-question-dimensions.md`.
7. **Pre-commit hook compliance.** Every commit is conventional; ADRs/research notes already exist.

## 1. Revised Folder Layout

```
web/
├── routers/
│   └── nursing.py              # HTTP endpoints (thin controllers)
├── services/
│   └── nursing_service.py      # Diagnostic, adaptive, practice, mock logic
├── repositories/
│   └── nursing_repository.py   # JSON question bank access
├── domain/
│   ├── nursing_models.py       # Pydantic models
│   └── nursing_constants.py    # Exam patterns, weights, defaults
├── templates/nursing/
│   ├── index.html              # landing + subject explorer
│   ├── diagnostic.html         # diagnostic test
│   ├── practice.html           # topic practice
│   └── mock.html               # full mock test
└── static/nursing/
    ├── nursing.css             # nursing-specific styles
    └── nursing.js              # diagnostic, practice, mock, analytics, i18n
```

**Rationale:** SOLID is preserved (router/service/repository separation) without excessive file splitting. This matches FastAPI best practices for small-to-medium features [^10][^11].

## 2. Question Dimensions (v1)

Based on `dfs-08-nursing-question-dimensions.md`:

| Dimension | Values | Purpose |
|-----------|--------|---------|
| `format` | `mcq` only in v1 | Matches real exam; minimizes UI complexity |
| `cognitive_level` | `remember`, `understand`, `apply`, `analyze` | Lets learners practice same topic at different depths |
| `context` | `theory`, `scenario`, `calculation` | Adds variety without changing interaction |
| `difficulty` | `1`, `2`, `3` | Existing adaptive signal |
| `topic_id` / `subject_id` | Existing tree | Topic-wise filtering |

**Deferred formats:** true/false, fill-in-blank, matching, assertion-reason, image-based, audio/video.

## 3. Phase Breakdown

### Phase 0 — Foundation & Data
**Goal:** Domain models, constants, topic tree, and seed question bank exist and validate.

**Files:**
- `data/nursing_topics.json` ✅
- `output/nursing_staff_nurse_output.json` ✅
- `scripts/generate_nursing_seed.py` ✅
- `web/domain/nursing_models.py`
- `web/domain/nursing_constants.py`
- `web/repositories/nursing_repository.py`

**Changes after research:**
- Add `verified_by`, `last_reviewed`, `cognitive_level`, `context`, and optional `telugu_hint` fields to question model.
- Add `glossary.json` for common medical terms (English → Telugu).
- Auto-tag seed questions with heuristics + spot-check; document confidence.

**Test Gate 0:**
```bash
python3 scripts/generate_nursing_seed.py
python3 -c "import json; d=json.load(open('output/nursing_staff_nurse_output.json')); assert d['meta']['total_questions'] >= 100"
python3 -m pytest tests/test_nursing_repository.py -q
```
**Success:** Repository returns 104 questions; all Pydantic models parse without errors; 100% of questions have `cognitive_level` and `context`.

---

### Phase 1 — Backend Services
**Goal:** Business logic for diagnostic, adaptive ranking, topic practice, mock tests, and PDF export works independently of HTTP and UI.

**Files:**
- `web/services/nursing_service.py` (replaces separate service files)

**Changes after research:**
- Adaptive model: accuracy (50%) + speed (25%) primary; confidence (15%) and consistency (10%) are togglable.
- Practice service filters by `subject`, `topic`, `cognitive_level`, `context`, `difficulty`.
- Mock service returns 80 MCQs matching exam blueprint.
- Add `generate_practice_pdf(subject_id, topic_id)` helper.
- Add `report_question(question_id, reason)`.

**Test Gate 1:**
```bash
python3 -m pytest tests/test_nursing_services.py -q
```
Tests must cover:
- Adaptive queue computes priority scores from attempts.
- Diagnostic service builds a capability map.
- Practice service returns questions filtered by subject/topic/cognitive/context.
- Mock service returns an 80-question randomized paper.
- PDF helper produces a non-empty bytes object.

**Success:** All service unit tests pass; no import errors; edge cases handled.

---

### Phase 2 — API Router
**Goal:** FastAPI endpoints expose the services to the frontend.

**Files:**
- `web/routers/nursing.py`
- Modify `web/main.py` to include the router at `/nursing` and `/api/nursing`.

**Endpoints:**
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/nursing` | Landing page / subject explorer |
| GET | `/nursing/practice` | Topic practice page |
| GET | `/nursing/mock` | Full mock test page |
| GET | `/nursing/diagnostic` | Diagnostic test page |
| GET | `/api/nursing/topics` | Topic tree + counts |
| GET | `/api/nursing/questions` | Filtered questions (`subject`, `topic`, `cognitive_level`, `context`, `difficulty`) |
| POST | `/api/nursing/diagnostic/start` | Returns diagnostic question set |
| POST | `/api/nursing/mock/start` | Returns 80-question mock set |
| POST | `/api/nursing/report` | Report a question issue |
| GET | `/api/nursing/pdf` | Download weak-area practice PDF |
| GET | `/api/nursing/status` | Health/status endpoint |

**Test Gate 2:**
```bash
python3 -m pytest tests/test_nursing_api.py -q
curl -s http://127.0.0.1:8000/api/nursing/status | jq
```
**Success:** All endpoints return valid JSON; status endpoint reports healthy.

---

### Phase 3 — Frontend UI
**Goal:** Browser pages for landing, diagnostic, topic practice, and mock test render and function.

**Files:**
- `web/templates/nursing/index.html`
- `web/templates/nursing/diagnostic.html`
- `web/templates/nursing/practice.html`
- `web/templates/nursing/mock.html`
- `web/static/nursing/nursing.css`
- `web/static/nursing/nursing.js`
- `web/static/nursing/glossary.json`

**Features:**
- Landing page: subject explorer, start diagnostic, start mock, download PDF.
- Diagnostic: 20 questions, timer, confidence slider, submit → capability map.
- Topic practice: pick subject/topic, optionally filter by `cognitive_level` and `context`, answer questions, immediate feedback, Telugu tooltip toggle.
- Mock test: 80 questions, 60-minute countdown, review screen.
- Progress: stored in `localStorage` (`nursing_attempts`, `nursing_capability_map`).
- Language toggle: English/Telugu UI labels.

**Test Gate 3:**
```bash
python3 -m web.main &
curl -s http://127.0.0.1:8000/nursing | grep -i "staff nurse"
curl -s http://127.0.0.1:8000/nursing/practice | grep -i "practice"
curl -s http://127.0.0.1:8000/nursing/mock | grep -i "mock"
```
**Success:** Pages render without 500 errors; JS console has no fatal errors on initial load.

---

### Phase 4 — Integration & End-to-End Flow
**Goal:** Full user journey works: diagnostic → capability map → weak-area drill → mock test → results → PDF export.

**Test Gate 4:**
```bash
python3 -m pytest tests/test_nursing_e2e.py -q
```
E2E tests simulate:
1. Start diagnostic.
2. Answer 20 questions.
3. Verify capability map is returned.
4. Start a weak-area practice session based on lowest capability.
5. Complete a mini mock (5 questions) and verify score calculation.
6. Request a PDF export and verify non-empty response.

**Success:** E2E tests pass; score calculation matches expected formula.

---

### Phase 5 — Docker & Deploy
**Goal:** Container restarts cleanly; new routes are reachable in production.

**Commands:**
```bash
docker compose down
docker compose up -d --build
# Or if build is unnecessary:
docker compose restart drmath-app
sleep 5
curl -s https://drmath.trelolabs.com/api/nursing/status | jq
```

**Test Gate 5:**
- `/nursing` reachable on live domain.
- `/api/nursing/status` returns healthy.
- Existing `/` and `/manager` routes still work.

**Success:** Live site shows nursing module; no regressions in math pages.

---

### Phase 6 — Content Expansion & Monitoring
**Goal:** Add more questions and observe usage.

**Actions:**
1. Generate 100 additional MCQs using LLM pipeline with nursing persona and verification.
2. Add `verified_by` and `last_reviewed` to every question.
3. Review `nursing_session_log` entries weekly to validate diagnostic dimensions.
4. Correlation experiment: after 50 sessions, check if priority scores predict mock improvement.

**Test Gate 6:**
- Question bank reaches 200+ verified MCQs.
- Report endpoint stores flagged question IDs.
- No critical errors in container logs.

## 4. Testing Strategy

| Level | File | Responsibility |
|-------|------|----------------|
| Unit | `tests/test_nursing_repository.py` | JSON parsing, filtering by subject/topic/cognitive/context |
| Unit | `tests/test_nursing_services.py` | Adaptive scoring, diagnostic, mock generation, PDF |
| Integration | `tests/test_nursing_api.py` | Endpoint contracts, JSON shape |
| E2E | `tests/test_nursing_e2e.py` | Full user flow |
| Manual | Browser + curl | UI rendering, mobile responsiveness |

## 5. Commit Plan

Each phase gets one conventional commit:
- `feat(nursing): add domain models, repository, and seed question bank`
- `feat(nursing): add diagnostic, practice, mock, and adaptive service`
- `feat(nursing): add FastAPI routes for nursing practice`
- `feat(nursing): add browser UI with Telugu glossary and PDF export`
- `test(nursing): add unit, integration, and e2e tests`
- `ops(nursing): deploy nursing module via docker compose`

## 6. Rollback Plan

If any phase fails its test gate, the previous phase remains intact. Because the module is isolated:
- Reverting `web/routers/nursing.py` and the `web/main.py` router inclusion removes the feature.
- `data/nursing_topics.json` and `output/nursing_staff_nurse_output.json` are data files and do not affect existing math routes.

## 7. Open Questions Before Phase 0 Begins

1. Should the mock test enforce strict 60-minute auto-submit, or allow self-paced completion with a timer?
2. Should Telugu appear only in UI labels, or also as optional tooltip translations for difficult English terms? (Plan recommends tooltips.)
3. Do you want a simple admin page at `/manager/nursing` to view report flags?

## 8. References

- `docs/adrs/ADR-004-nursing-module.md`
- `docs/decisions/DECISION-20260513-004-council-nursing-module.md`
- `docs/research/bidirectional/bidirectional-03-nursing-plan-updates-after-research.md`
- `docs/research/bidirectional/bidirectional-04-nursing-cross-domain-impact.md`
- `docs/research/bidirectional/bidirectional-05-nursing-dimensions-introspection.md`
- `docs/research/dfs/dfs-08-nursing-question-dimensions.md`
- `docs/research/bfs/bfs-08-nursing-altruistic-landscape.md`
- `docs/principles/nursing-altruistic-framework.md`
- `web/nursing/README.md`
