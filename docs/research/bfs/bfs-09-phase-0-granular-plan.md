# BFS-09: Phase 0 Granular Implementation Plan

**Date:** 2026-05-13  
**Scope:** Foundation & data layer for the `/nursing` module. No HTTP, no UI, no service logic.  
**Goal:** A validated question bank + domain models + repository that the rest of the module can depend on.  

---

## 1. What Phase 0 Must Deliver

1. `output/nursing_staff_nurse_output.json` regenerated with:
   - `cognitive_level` and `context` tags on every question.
   - `format: "mcq"`.
   - `verified_by` and `last_reviewed` metadata.
2. `web/domain/nursing_constants.py` — single source of truth for enums and exam config.
3. `web/domain/nursing_models.py` — Pydantic v2 models for type-safe data handling.
4. `web/repositories/nursing_repository.py` — read-only data access over the JSON bank.
5. `tests/test_nursing_repository.py` — unit tests proving the repository works.

No other files are touched in Phase 0.

---

## 2. File: `web/domain/nursing_constants.py`

### Purpose
Centralize all string constants and enumerations so the rest of the module does not use magic strings. This makes renaming a value trivial and prevents typos in filters.

### Contents

```python
from enum import Enum


class CognitiveLevel(str, Enum):
    REMEMBER = "remember"
    UNDERSTAND = "understand"
    APPLY = "apply"
    ANALYZE = "analyze"


class QuestionContext(str, Enum):
    THEORY = "theory"
    SCENARIO = "scenario"
    CALCULATION = "calculation"


class QuestionFormat(str, Enum):
    MCQ = "mcq"


class VerificationStatus(str, Enum):
    REVIEWED = "reviewed"
    PENDING = "pending"
    FLAGGED = "flagged"


DEFAULT_SOURCE = "INC GNM Syllabus / Standard Nursing Textbooks"
DEFAULT_VERIFIED_BY = "GNM syllabus cross-check + INC textbook review"


class ExamPattern:
    MHSRB_STAFF_NURSE = "mhsrb_staff_nurse"
    TOTAL_QUESTIONS = 80
    DURATION_MINUTES = 60
    NEGATIVE_MARKING = False
```

### Rationale line-by-line

- `CognitiveLevel`, `QuestionContext`, `QuestionFormat`, `VerificationStatus` are `str, Enum` because Pydantic v2 serializes them as strings automatically and FastAPI can expose them in OpenAPI schemas.
- The enum names are UPPER_SNAKE while values are lowercase kebab-case/words: this is the Python convention for constants while keeping JSON values readable.
- `DEFAULT_SOURCE` and `DEFAULT_VERIFIED_BY` exist because 104 questions share the same source string; centralizing it avoids drift if we later need to cite a different textbook set.
- `ExamPattern` is a plain class (not enum) because these values are numeric/boolean config, not a closed set of string choices.
- `TOTAL_QUESTIONS = 80` and `DURATION_MINUTES = 60` come directly from `data/nursing_topics.json` exam metadata.
- `NEGATIVE_MARKING = False` is explicit so the scoring service never accidentally subtracts marks.

---

## 3. File: `web/domain/nursing_models.py`

### Purpose
Define the shape of every object crossing the nursing module boundary. Pydantic gives us validation, serialization, and clear error messages when the JSON bank drifts.

### Contents

```python
from typing import Optional
from pydantic import BaseModel, Field, field_validator

from web.domain.nursing_constants import (
    CognitiveLevel,
    QuestionContext,
    QuestionFormat,
    VerificationStatus,
)


class NursingQuestion(BaseModel):
    id: int
    subject_id: str
    topic_id: str
    concept_tag: str
    difficulty: int = Field(ge=1, le=3)
    cognitive_level: CognitiveLevel
    context: QuestionContext
    format: QuestionFormat = QuestionFormat.MCQ
    question: str
    options: list[str]
    correct_answer: str = Field(pattern=r"^[A-D]$")
    explanation: str
    source: str
    verification_status: VerificationStatus
    verified_by: Optional[str] = None
    last_reviewed: Optional[str] = None
    telugu_hint: Optional[str] = None

    @field_validator("options")
    @classmethod
    def _four_options(cls, v: list[str]) -> list[str]:
        if len(v) != 4:
            raise ValueError("MCQ must have exactly 4 options")
        return v


class QuestionBankMeta(BaseModel):
    total_questions: int
    language: str
    source: str
    verification_status: VerificationStatus
    verified_by: Optional[str] = None
    last_reviewed: Optional[str] = None
    generated_at: Optional[str] = None
    dimensions: Optional[dict] = None


class QuestionBank(BaseModel):
    topic: str
    exam_pattern: str
    meta: QuestionBankMeta
    questions: list[NursingQuestion]
```

### Rationale line-by-line

- `BaseModel` from Pydantic v2 is used throughout (the project already depends on `pydantic>=2.0.0`).
- `id: int` — integer IDs are simple, sortable, and match the existing seed bank.
- `subject_id: str`, `topic_id: str` — kept as strings rather than enums because the topic tree may grow; we validate topic IDs inside the repository against `nursing_topics.json`.
- `concept_tag: str` — a short human-readable label for analytics and weak-area grouping.
- `difficulty: int = Field(ge=1, le=3)` — enforces the 1–3 scale documented in the plan.
- `cognitive_level: CognitiveLevel` — mandatory dimension tag; no default, because Phase 0 requires 100% coverage.
- `context: QuestionContext` — mandatory dimension tag; no default, same reason.
- `format: QuestionFormat = QuestionFormat.MCQ` — default is MCQ; when later formats are added, this field is already present.
- `question: str` — the stem.
- `options: list[str]` — four answer choices.
- `correct_answer: str = Field(pattern=r"^[A-D]$")` — restricts to A–D; matches the seed bank format. If we later add assertion-reason questions with different answer keys, this validator will be relaxed.
- `explanation: str` — shown after answering; required for learning, not optional.
- `source: str` — traceability for medical facts.
- `verification_status: VerificationStatus` — `reviewed` / `pending` / `flagged`.
- `verified_by: Optional[str] = None` — name of reviewer or method; optional to keep existing data importable.
- `last_reviewed: Optional[str] = None` — ISO date string; optional for import flexibility.
- `telugu_hint: Optional[str] = None` — placeholder for optional Telugu explanation; does not block Phase 0.
- `@field_validator("options")` — ensures every question has exactly four options. A malformed seed file fails fast at load time.
- `QuestionBankMeta` — separates metadata from the question list so the repository can return meta without loading all questions if desired.
- `dimensions: Optional[dict] = None` — holds the cognitive/context counts generated by the seed script; optional so older banks still parse.
- `QuestionBank` — root model mirroring `output/nursing_staff_nurse_output.json` exactly.

---

## 4. File: `web/repositories/nursing_repository.py`

### Purpose
Isolate JSON file access from business logic. The service layer will call this repository, not `json.load` directly. This makes it easy to swap the backend (e.g., SQLite) later without touching services.

### Contents

```python
import json
from pathlib import Path
from typing import Optional

from pipeline.config import OUTPUT_DIR
from web.domain.nursing_constants import CognitiveLevel, QuestionContext
from web.domain.nursing_models import NursingQuestion, QuestionBank


DEFAULT_BANK_PATH = OUTPUT_DIR / "nursing_staff_nurse_output.json"


class NursingRepository:
    def __init__(self, bank_path: Optional[Path] = None):
        self._bank_path = bank_path or DEFAULT_BANK_PATH
        self._bank: Optional[QuestionBank] = None

    def _load(self) -> QuestionBank:
        if self._bank is None:
            raw = json.loads(self._bank_path.read_text(encoding="utf-8"))
            self._bank = QuestionBank.model_validate(raw)
        return self._bank

    def reload(self) -> None:
        """Force re-read from disk (useful after seed regeneration)."""
        self._bank = None

    def get_meta(self) -> dict:
        return self._load().meta.model_dump()

    def get_all_questions(self) -> list[NursingQuestion]:
        return self._load().questions

    def get_question_by_id(self, question_id: int) -> Optional[NursingQuestion]:
        for q in self._load().questions:
            if q.id == question_id:
                return q
        return None

    def filter_questions(
        self,
        *,
        subject_id: Optional[str] = None,
        topic_id: Optional[str] = None,
        cognitive_level: Optional[CognitiveLevel] = None,
        context: Optional[QuestionContext] = None,
        difficulty: Optional[int] = None,
        concept_tag: Optional[str] = None,
    ) -> list[NursingQuestion]:
        result = self._load().questions
        if subject_id is not None:
            result = [q for q in result if q.subject_id == subject_id]
        if topic_id is not None:
            result = [q for q in result if q.topic_id == topic_id]
        if cognitive_level is not None:
            result = [q for q in result if q.cognitive_level == cognitive_level]
        if context is not None:
            result = [q for q in result if q.context == context]
        if difficulty is not None:
            result = [q for q in result if q.difficulty == difficulty]
        if concept_tag is not None:
            result = [q for q in result if q.concept_tag == concept_tag]
        return result

    def count_by_subject(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for q in self._load().questions:
            counts[q.subject_id] = counts.get(q.subject_id, 0) + 1
        return counts

    def list_subjects(self) -> list[str]:
        return sorted({q.subject_id for q in self._load().questions})

    def list_topics(self, subject_id: Optional[str] = None) -> list[str]:
        questions = self._load().questions
        if subject_id is not None:
            questions = [q for q in questions if q.subject_id == subject_id]
        return sorted({q.topic_id for q in questions})
```

### Rationale line-by-line

- `DEFAULT_BANK_PATH = OUTPUT_DIR / "nursing_staff_nurse_output.json"` — reuses the existing `OUTPUT_DIR` constant from `pipeline.config` so the repository does not hardcode paths.
- `__init__(bank_path: Optional[Path] = None)` — dependency injection. Tests can pass a temporary JSON file; production uses the default.
- `self._bank: Optional[QuestionBank] = None` — lazy-load cache. The file is read once per repository instance, reducing disk I/O during a single request.
- `_load()` — private because callers should use public methods; returns a validated `QuestionBank`.
- `json.loads(...read_text(...))` — explicit encoding `utf-8` for Telugu content that may appear later.
- `QuestionBank.model_validate(raw)` — Pydantic v2 way to parse a dict; raises clear errors if the seed file is malformed.
- `reload()` — allows tests to regenerate the bank and re-read without creating a new repository instance.
- `get_meta()` — returns metadata dict; useful for status endpoints and admin views.
- `get_all_questions()` — raw access for diagnostic/mock builders.
- `get_question_by_id()` — O(n) lookup is acceptable for 104 questions; no index needed yet.
- `filter_questions()` — keyword-only arguments (`*,`) force callers to name filters, preventing positional confusion among many optional filters.
- Each filter is applied sequentially in the order: subject → topic → cognitive → context → difficulty → concept. Order does not affect correctness, but this matches the mental model of narrowing down.
- `count_by_subject()` — used by the landing page to show "X questions in Anatomy & Physiology".
- `list_subjects()` and `list_topics()` — provide the filter dropdowns on the UI without parsing `nursing_topics.json` separately.

---

## 5. File: `tests/test_nursing_repository.py`

### Purpose
Prove the repository works and that every seed question passes Pydantic validation. This is the Phase 0 test gate.

### Contents

```python
import json
from pathlib import Path

import pytest

from web.domain.nursing_constants import CognitiveLevel, QuestionContext
from web.domain.nursing_models import QuestionBank
from web.repositories.nursing_repository import NursingRepository


@pytest.fixture
def repo():
    return NursingRepository()


def test_seed_bank_validates(repo):
    bank = repo._load()
    assert isinstance(bank, QuestionBank)
    assert bank.meta.total_questions == len(bank.questions)


def test_all_questions_have_dimensions(repo):
    for q in repo.get_all_questions():
        assert q.cognitive_level in set(CognitiveLevel)
        assert q.context in set(QuestionContext)
        assert q.format.value == "mcq"
        assert q.verified_by
        assert q.last_reviewed


def test_filter_by_subject(repo):
    qs = repo.filter_questions(subject_id="anatomy_physiology")
    assert len(qs) > 0
    assert all(q.subject_id == "anatomy_physiology" for q in qs)


def test_filter_by_topic_and_cognitive(repo):
    qs = repo.filter_questions(
        topic_id="ap_cardiovascular",
        cognitive_level=CognitiveLevel.REMEMBER,
    )
    assert len(qs) > 0
    assert all(q.topic_id == "ap_cardiovascular" for q in qs)
    assert all(q.cognitive_level == CognitiveLevel.REMEMBER for q in qs)


def test_filter_by_context_calculation(repo):
    qs = repo.filter_questions(context=QuestionContext.CALCULATION)
    assert len(qs) > 0
    assert all(q.context == QuestionContext.CALCULATION for q in qs)


def test_get_question_by_id(repo):
    q = repo.get_question_by_id(1)
    assert q is not None
    assert q.id == 1


def test_count_by_subject(repo):
    counts = repo.count_by_subject()
    assert "anatomy_physiology" in counts
    assert sum(counts.values()) == repo.get_meta()["total_questions"]


def test_list_topics(repo):
    topics = repo.list_topics(subject_id="anatomy_physiology")
    assert "ap_cardiovascular" in topics
    assert len(topics) == len(set(topics))
```

### Rationale line-by-line

- `pytest` is used because it is the standard Python test runner and requires no new dependency.
- `repo()` fixture — creates one repository per test. Tests are independent.
- `test_seed_bank_validates` — ensures the entire JSON file parses as a `QuestionBank` and that `meta.total_questions` is consistent.
- `test_all_questions_have_dimensions` — enforces Phase 0 requirement: 100% of questions have `cognitive_level`, `context`, `format`, `verified_by`, and `last_reviewed`.
- `test_filter_by_subject` — basic subject filtering works.
- `test_filter_by_topic_and_cognitive` — combined filters work (the core "topic-wise + different dimensions" use case).
- `test_filter_by_context_calculation` — proves context filtering works.
- `test_get_question_by_id` — lookup by ID works.
- `test_count_by_subject` — aggregation works and totals match.
- `test_list_topics` — topic listing per subject works and has no duplicates.

---

## 6. Test Gate 0 Command

```bash
python3 scripts/generate_nursing_seed.py
python3 -m pytest tests/test_nursing_repository.py -q
```

**Success criteria:**
- Seed script runs without error.
- All repository tests pass.
- 104 questions are validated.
- No question lacks `cognitive_level`, `context`, `format`, `verified_by`, or `last_reviewed`.

---

## 7. Files NOT Created in Phase 0

| File | Why deferred |
|------|--------------|
| `web/services/nursing_service.py` | Business logic belongs in Phase 1, after data layer is solid. |
| `web/routers/nursing.py` | HTTP layer belongs in Phase 2. |
| `web/templates/nursing/*.html` | UI belongs in Phase 3. |
| `web/static/nursing/*` | Assets belong in Phase 3. |
| `glossary.json` | Telugu tooltips are optional; can be added in Phase 3 without breaking models. |
| `tests/test_nursing_services.py` | No service exists yet. |
| `tests/test_nursing_api.py` | No router exists yet. |
| `tests/test_nursing_e2e.py` | Full flow needs all preceding phases. |

---

## 8. Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Heuristic cognitive/context tags are wrong for some questions | Tags are documented as approximate; Phase 6 includes manual review. |
| Pydantic validators reject valid future questions | Validators are narrow (4 options, A–D answers); will be relaxed when new formats are added. |
| Repository loads entire bank into memory | 104 questions is tiny; if bank grows to 10,000+, repository will be switched to SQLite. |
| `pipeline.config.OUTPUT_DIR` changes | Only one place (`DEFAULT_BANK_PATH`) references it; easy to update. |

---

## 9. Approval Checklist

Before proceeding to implementation, confirm:

- [ ] Constants (`CognitiveLevel`, `QuestionContext`, `QuestionFormat`, `VerificationStatus`, `ExamPattern`) are correct.
- [ ] Model fields and validators are acceptable.
- [ ] Repository interface is sufficient for Phase 1 service layer.
- [ ] Test coverage is adequate for Phase 0 gate.
