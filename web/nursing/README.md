# Dr. Math — Nursing Practice Module (`/nursing`)

This directory contains the **Telangana Staff Nurse recruitment practice module**. It is intentionally isolated from the Class VII math pipeline so that changes here do not affect math content.

## Folder Layout (SOLID)

```
web/
├── routers/nursing.py              # HTTP endpoints (thin controllers)
├── services/
│   ├── diagnostic_service.py       # Multi-dimensional capability assessment
│   ├── practice_service.py         # Topic practice orchestration
│   ├── mock_test_service.py        # Full-length mock exam flow
│   └── adaptive_queue.py           # Ranks next question by capability map
├── repositories/
│   └── question_repository.py      # Abstracts JSON/DB/LLM question sources
├── domain/
│   ├── models.py                   # Pydantic domain models
│   └── constants.py                # Exam patterns, weights, defaults
├── templates/nursing/              # Jinja2 HTML pages
└── static/nursing/                 # JS/CSS assets
```

## Design Principles

1. **Single Responsibility** — Each service does one thing.
2. **Open/Closed** — New exam patterns are new constants, not rewrites.
3. **Liskov Substitution** — `QuestionRepository` interface can be implemented by JSON file, DB, or LLM source without changing services.
4. **Interface Segregation** — Small API endpoints: `/diagnostic`, `/practice`, `/mock`, `/status`.
5. **Dependency Inversion** — Services depend on the repository interface, not on `output/*.json` directly.

## Data Files

- `data/nursing_topics.json` — subject/topic/subtopic tree.
- `output/nursing_staff_nurse_output.json` — seed MCQ bank.

## How to Add a New Question

1. Add the question object to `output/nursing_staff_nurse_output.json`.
2. Ensure `subject_id`, `topic_id`, and `concept_tag` match entries in `data/nursing_topics.json`.
3. Set `verification_status` to `reviewed` and `source` to a T1/T2 reference.
4. Run the local smoke test: `python -m pytest tests/test_nursing_module.py` (when available).

## How to Add a New Exam Pattern

1. Add a new `ExamPattern` entry in `web/domain/constants.py`.
2. Add a route in `web/routers/nursing.py` if the UI flow differs.
3. Update `web/templates/nursing/index.html` to expose the new pattern.

## Safety Note

Medical content is high-stakes. Never auto-promote LLM-generated questions to `verified`. All clinical questions must be reviewed against standard nursing textbooks or official syllabi.
