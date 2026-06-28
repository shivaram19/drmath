# SOLID Audit — Dr. Math: A Research Software Scientist's View

**Date:** 2026-06-28  
**Scope:** Full-stack Python codebase (`pipeline/`, `web/`, `db/`, `src/`, deployment artifacts), with the lens of the five SOLID design principles.  
**Research Phase:** Bidirectional / cross-domain impact analysis  

---

## Prelude — The Scientists Who Liberated SOLID

This audit is written in the spirit of the researchers who turned software design from craft into reasoning: Edsger Dijkstra's separation of concerns, Bertrand Meyer's contract-driven modules, Barbara Liskov's behavioral subtyping, Robert C. Martin's cohesion-and-coupling principles, and Michael Feathers's acronym that made them unforgettable [^1][^2][^3][^4]. SOLID is not a style guide; it is a set of invariants that keep a system honest as it grows. When we violate them, we do not merely write "messy" code — we create latent debt that compounds at the boundaries between research, pedagogy, and production.

> "A class should have one, and only one, reason to change." — Robert C. Martin, on the Single Responsibility Principle [^1].

Dr. Math is at an inflection point: the nursing module is maturing into a real user-facing product while the original math-pipeline remains a research script that grew into production. That tension is visible in the architecture. This document names what is healthy, what is leaking, and what must be refactored before the next phase.

---

## Method

The audit was performed as a read-only code review. Three parallel exploration passes covered:

1. `pipeline/` — orchestration, scraping, LLM client, content adaptation, question generation, legacy DB wrappers.
2. `web/` + `db/` — FastAPI routes, services, repositories, SQLAlchemy models, CRUD.
3. `src/` + top-level deployment artifacts — the hexagonal skeleton, Docker, nginx.

Every claim below is backed by a concrete file path and line range. No files were modified during the audit.

---

## Executive Summary

| Finding | Severity | Principle |
|---|---|---|
| `pipeline/run.py::run_pipeline()` is a 180-line god function mixing orchestration, scraping, LLM calls, file I/O, DB writes, grounding logs, and error handling. | Critical | SRP, DIP |
| `web/main.py` is a 700-line god module owning marketing pages, manager dashboard, topic rendering, prompt builder, pipeline invocation, lab/compare UI, REST API, evaluations, and APK download. | Critical | SRP, DIP |
| `src/domain`, `src/application`, `src/infrastructure` are empty directories — dead hexagonal scaffolding. | High | SRP, honesty of structure |
| `pipeline/db.py` runs `Base.metadata.create_all(bind=engine)` at import time and mixes legacy wrappers, CRUD passthrough, and schema init. | High | SRP, DIP |
| `pipeline/llm_client.py::LLMClient` selects providers via `if/elif/else`; adding a new provider requires editing the class. | High | OCP, DIP |
| `db/crud.py::update_generation()` has 13 optional parameters and branches on each. | High | ISP, OCP |
| `web/main.py` imports both legacy `pipeline.db` and new `db.crud`, exposing two incompatible prompt APIs. | High | ISP, DIP |
| `db/models.py::Generation` contains `avg_rating`, `difficulty_dict`, and `timeline` properties — presentation logic inside an ORM model. | Medium | SRP |
| `web/routers/nursing.py` instantiates `NursingService()` as a module-level singleton, defeating its constructor abstraction. | Medium | DIP |
| `JsonFileQuestionRepository` adds public methods (`filter`, `get_meta`, `list_subjects`, etc.) not declared in `QuestionRepository`. | Medium | LSP, ISP |
| **Positive:** Nursing module uses a clean `QuestionRepository(ABC)`, `NursingService` builders, and Pydantic domain models. | — | SRP, OCP, DIP |

The codebase has **two architectural realities**: the nursing module already follows SOLID reasonably well, while the math pipeline and web main module remain procedural. The fastest path to health is to make the pipeline look more like the nursing module.

---

## 1. Single Responsibility Principle (SRP)

> "A class should have one, and only one, reason to change." [^1]

### 1.1 What is healthy

- `pipeline/config.py` owns only environment-dependent constants.
- `pipeline/content_adapter.py` and `pipeline/question_generator.py` each own one prompt-building concern.
- `pipeline/llm_client.py` isolates provider-specific construction.
- `web/domain/models.py` and `web/domain/constants.py` isolate data shapes and enums.
- `web/services/nursing_service.py` decomposes nursing logic into focused builders (`DiagnosticBuilder`, `PracticeBuilder`, `MockBuilder`).
- `web/repositories/question_repository.py` isolates question persistence behind an abstract repository.

### 1.2 What violates SRP

#### A. `pipeline/run.py::run_pipeline()` — the god function

```python
# pipeline/run.py, lines 21-177
def run_pipeline(topic: str, output_path: str, prompt_id: Optional[str] = None):
    # DB setup, prompt lookup
    db = SessionLocal()
    ...
    # Step 1: Scrape IXL topics
    ixl_topics = fetch_ixl_topics()
    ...
    # Step 2: Fetch MathIsFun content
    raw_html, mathisfun_url = search_mathisfun_topic(topic)
    raw_path = DATA_DIR / f"{slug}_raw.html"
    raw_path.write_text(raw_html, encoding="utf-8")
    ...
    # Step 3: Adapt content via LLM
    llm = LLMClient()
    adapted_content = llm.generate(...)
    ...
    # Step 4: Generate 40 questions
    raw_questions = llm.generate(...)
    questions = parse_json_array(raw_questions)
    ...
    # Step 5: Save output + DB + grounding logs
    crud.update_generation(...)
    crud.create_grounding_log(...)
```

This function changes for at least six different reasons: scraping strategy, LLM provider, output schema, persistence format, grounding policy, and error handling. Each reason is a distinct responsibility.

#### B. `web/main.py` — the god module

```python
# web/main.py, lines 105-120
@app.get("/", response_class=HTMLResponse)              # marketing homepage
@app.get("/manager", response_class=HTMLResponse)       # manager dashboard
@app.get("/topic/{slug}", response_class=HTMLResponse)  # topic viewer
@app.post("/generate")                                  # pipeline trigger
@app.get("/lab")                                        # prompt lab
@app.post("/api/evaluations")                           # evaluations API
@app.get("/mathwise.apk")                               # APK download
```

A single module owns routing, HTML rendering, JSON file parsing, business rules, and direct pipeline invocation. Adding a new page or API endpoint means editing this file.

#### C. `db/models.py::Generation` — persistence + presentation

```python
# db/models.py, lines 67-91
class Generation(Base):
    ...
    @property
    def avg_rating(self) -> Optional[float]: ...

    @property
    def difficulty_dict(self) -> dict: ...

    @property
    def timeline(self) -> List[dict]:
        """Return chronologically ordered pipeline steps with timestamps."""
        steps = []
        if self.scraped_at:
            steps.append({"step": "Scrape sources (IXL + MathIsFun)", ...})
        ...
```

`Generation` is an ORM persistence model, yet it owns response formatting (`timeline`) and analytics (`avg_rating`). Those properties exist because some template or API endpoint needs them; they should live in a response mapper or service, not in the database model.

#### D. `db/crud.py::create_prompt()` — persistence + versioning policy

```python
# db/crud.py, lines 19-63
def create_prompt(db: Session, name: str, ...):
    # If editing an existing prompt, check for no-op (identical text)
    if parent_id:
        parent = get_prompt(db, parent_id)
        if parent:
            if parent.system_prompt.strip() == system_prompt.strip() and ...:
                return parent
            version = len(parent.children) + 1 if parent.children else 1
    ...
    display_name = f"{name} (v{version} — {datetime.utcnow().strftime('%b %d, %H:%M')})"
```

The function decides when a version is a no-op, how versions are numbered, and how they are named. Those are application-level versioning rules, not persistence rules.

#### E. `pipeline/db.py` — schema init + legacy API + CRUD passthrough

```python
# pipeline/db.py, lines 11-16
from db.database import SessionLocal, Base, engine
from db import models
from db import crud

Base.metadata.create_all(bind=engine)
```

Importing this module has the side effect of creating database tables. It also exposes a legacy prompt API, a legacy generation API, and internal mapping helpers in one namespace.

#### F. Duplicate `strip_html` in `pipeline/run.py`

```python
# pipeline/run.py, lines 179-186
def strip_html(raw_html: str) -> str:
    from bs4 import BeautifulSoup
    ...
```

The same function already exists in `pipeline/content_adapter.py, lines 32-39`. Duplicating it gives `run.py` a second reason to change when HTML-cleaning rules evolve.

### 1.3 Recommended refactors (SRP), ordered by impact

1. **Extract `run_pipeline()` into a `PipelineRunner` use-case class** that delegates to `Scraper`, `ContentAdapter`, `QuestionGenerator`, and `GenerationPersister`. High impact; touches `pipeline/run.py` and creates new modules.
2. **Split `web/main.py` into FastAPI routers**: `pages.py`, `topics.py`, `prompts.py`, `generations.py`, `evaluations.py`, `lab.py`. High impact; preserves existing routes.
3. **Move `Generation.avg_rating`, `difficulty_dict`, and `timeline` into Pydantic response schemas** in `web/schemas/generation.py`. Medium impact.
4. **Extract prompt-versioning policy into a `PromptVersioningService`** in `web/services/`; keep `db/crud.py::create_prompt` as a thin persistence wrapper. Medium impact.
5. **Remove `strip_html` from `pipeline/run.py`** and reuse `pipeline/content_adapter.strip_html`. Low effort, high clarity.
6. **Move `Base.metadata.create_all()` to an explicit `init_db()` called by entry points**, and split `pipeline/db.py` into a legacy-shim module and a repository module. Medium impact.

---

## 2. Open/Closed Principle (OCP)

> "Software entities should be open for extension, but closed for modification." — Bertrand Meyer [^2].

### 2.1 What is healthy

- `pipeline/content_adapter.py::build_adapter_prompt()` accepts `custom_system` / `custom_user`, allowing new prompt styles without editing the adapter.
- `pipeline/question_generator.py::build_question_prompt()` accepts a `custom_prompt` for the same reason.
- `web/repositories/question_repository.py` defines an ABC; new question sources can be added without changing callers.
- `web/services/nursing_service.py` builders can be extended by adding new builder classes.

### 2.2 What violates OCP

#### A. `pipeline/llm_client.py::LLMClient` — provider selected by if-chain

```python
# pipeline/llm_client.py, lines 21-44
class LLMClient:
    def __init__(self):
        if LLM_PROVIDER == "azure":
            ...
        elif LLM_PROVIDER == "grok":
            ...
        else:
            ...
```

Adding Anthropic, Gemini, or a local Ollama backend means editing `LLMClient.__init__`. The class is not closed for modification.

#### B. `pipeline/scraper.py::search_mathisfun_topic()` — hardcoded topic map

```python
# pipeline/scraper.py, lines 46-80
mapping = {
    "integer": "positive-negative-integers.html",
    "fraction": "fractions.html",
    "percentage": "percentage.html",
    ...
}
```

Every new Class-VII topic requires editing the scraper. The topic-to-source map should be external configuration or a registry class.

#### C. `pipeline/run.py::run_pipeline()` — pipeline steps are hardcoded

The numbered steps `[1/5] ... [5/5]` are wired inline. Adding evaluation, image generation, or a human-in-the-loop review step means editing the function.

#### D. `pipeline/question_generator.py` — schema prompt is a global constant

The 40-question, 4-option, A–D JSON schema prompt is hardcoded. Adding a hint field, changing the number of options, or supporting multi-select would require editing the module.

#### E. `web/main.py` — prompt dimensions hardcoded in multiple places

```python
# web/main.py, line 60
if len(parts) >= 2 and parts[-1] in ("default", "storyteller", "visual", "zpd"):
```

This tuple is repeated in `topic_page`, `review_page`, `_list_topics`, and `status_page`. Adding a fifth dimension requires editing every occurrence.

#### F. `db/crud.py::update_generation()` — closed for modification

```python
# db/crud.py, lines 164-212
def update_generation(...):
    if status is not None:
        gen.status = status
    if output_path is not None:
        gen.output_path = output_path
    ...  # repeated for ~13 fields
```

Adding a new `Generation` column forces another `if` branch. A schema-driven mapper or small intent-specific methods would be open for extension.

### 2.3 Recommended refactors (OCP), ordered by impact

1. **Introduce an `LLMPort` protocol/ABC** with `AzureProvider`, `OpenAIProvider`, `GrokProvider`, and a factory. High impact; fixes both OCP and DIP.
2. **Externalize the MathIsFun topic map** into `data/mathisfun_topics.yaml` or a `TopicResolver` registry. Medium impact.
3. **Parameterize prompt dimensions** in `pipeline/config.py` (`PROMPT_DIMENSIONS`) and inject them into endpoints. Medium impact.
4. **Model pipeline steps as a list of `PipelineStep` strategies** so new steps can be added without editing `run_pipeline()`. Medium impact; do only if the pipeline will keep evolving.
5. **Replace `update_generation()` with a generic `apply_update(db, Generation, **kwargs)` helper** or with focused methods such as `mark_success()` and `set_output_paths()`. Medium impact.
6. **Make the question JSON schema composable** via a `QuestionSchema` value object. Low impact for current scope.

---


## 3. Liskov Substitution Principle (LSP)

> "If for each object o1 of type S there is an object o2 of type T such that for all programs P defined in terms of T, the behavior of P is unchanged when o1 is substituted for o2, then S is a subtype of T." — Barbara Liskov [^3].

### 3.1 What is healthy

- `web/repositories/question_repository.py::JsonFileQuestionRepository` correctly implements every abstract method of `QuestionRepository`. A caller depending only on the ABC can receive the JSON implementation without behavior changes.
- `web/domain/models.py::Capability` subclasses (`SubjectCapability`, `TopicCapability`, `DimensionCapability`) extend the base without overriding behavior destructively.

### 3.2 What violates or risks LSP

#### A. `JsonFileQuestionRepository` exposes a wider public interface than its base

```python
# web/repositories/question_repository.py, lines 68-120
class JsonFileQuestionRepository(QuestionRepository):
    def reload(self): ...
    def get_meta(self): ...
    def filter(self, ...): ...
    def count_by_subject(self): ...
    def list_subjects(self): ...
    def list_topics(self, ...): ...
```

`QuestionRepository` declares only `get_all`, `get_by_id`, `get_by_subject`, `get_by_topic`, and `get_diagnostic_set`. `web/routers/nursing.py` calls `service.repository.list_subjects()` and `service.repository.get_meta()` directly on the concrete singleton. A future DB-backed repository would silently break those call sites because the methods are not part of the contract.

#### B. `pipeline/db.py` legacy wrappers are not behavioral substitutes for `db.crud`

```python
# pipeline/db.py, lines 80-93
def log_generation(topic: str, prompt_id: Optional[str], output_path: str, status: str, meta: Dict[str, Any]):
    """Legacy log — creates or updates a generation record."""
    db = _session()
    try:
        slug = topic.lower().replace(" ", "_")
        topic_obj = crud.get_or_create_topic(db, slug, topic)
        crud.create_generation(
            db,
            topic_id=topic_obj.id,
            prompt_id=prompt_id,
            status=status,
        )
    finally:
        db.close()
```

The signature promises to handle `output_path`, `status`, and `meta`, but the function ignores them and always creates a `pending` generation. A caller expecting the signature contract is misled.

#### C. `NursingService` defaults to a concrete repository

```python
# web/services/nursing_service.py, lines 323-324 (class constructor)
class NursingService:
    def __init__(self, repository: Optional[QuestionRepository] = None):
        self.repository = repository or JsonFileQuestionRepository()
```

The constructor accepts the abstraction but immediately defaults to the concrete JSON implementation. Production wiring should happen in a composition root, not inside the service.

#### D. `CapabilityService` reaches into a private function

```python
# web/services/nursing_service.py (approximate)
def _compute_capability(self, attempts: List[Attempt]) -> Dict[str, float]:
    from web.services.adaptive_queue import _compute_capability
    return _compute_capability(attempts)
```

Importing `_compute_capability` (a private function by naming convention) from another module weakens substitutability. A public capability-calculator interface or function should be used instead.

### 3.3 Recommended refactors (LSP), ordered by impact

1. **Promote commonly used repository methods into `QuestionRepository`** (`filter`, `list_subjects`, `list_topics`, `get_meta`, `count_by_subject`) or split the ABC into role interfaces. High impact; prevents future DB implementation breakage.
2. **Make `log_generation()` match its signature** or remove it from the public API. Medium impact.
3. **Remove the default concrete repository from `NursingService.__init__`** and inject the repository from a composition root. Medium impact.
4. **Expose a public `compute_capability()` function** in `web/services/adaptive_queue.py` and use it from `CapabilityService`. Low impact.

---

## 4. Interface Segregation Principle (ISP)

> "Clients should not be forced to depend on interfaces they do not use." [^1]

### 4.1 What is healthy

- `web/repositories/question_repository.py::QuestionRepository` (ignoring the extra concrete methods) is a small, coherent interface for reading questions.
- `pipeline/content_adapter.py::build_adapter_prompt()` and `pipeline/question_generator.py::build_question_prompt()` have focused parameter lists.

### 4.2 What violates ISP

#### A. No `pipeline/interfaces.py` exists

`AGENTS.md` mentions `pipeline/interfaces.py` as the home for hexagonal ports, but the file does not exist. Every pipeline caller therefore depends on concrete modules.

#### B. `db/crud.py::update_generation()` — fat interface

```python
# db/crud.py, lines 164-180
def update_generation(
    db: Session,
    generation_id: int,
    status: Optional[str] = None,
    output_path: Optional[str] = None,
    total_questions: Optional[int] = None,
    difficulty_distribution: Optional[dict] = None,
    adapted_content: Optional[str] = None,
    questions_json: Optional[list] = None,
    raw_html_path: Optional[str] = None,
    antigravity_path: Optional[str] = None,
    meta: Optional[dict] = None,
    scraped_at: Optional[datetime] = None,
    adapted_at: Optional[datetime] = None,
    questions_generated_at: Optional[datetime] = None,
    saved_at: Optional[datetime] = None,
) -> Optional[Generation]:
```

A caller that only wants to mark an error (`status="error"`) must know about `antigravity_path`, `questions_json`, and every other field.

#### C. `web/main.py` depends on two incompatible prompt APIs

```python
# web/main.py, lines 14-17
from pipeline.config import OUTPUT_DIR, DATA_DIR
from pipeline.run import run_pipeline
from pipeline.db import list_prompts, get_prompt, save_prompt, delete_prompt, list_generations, _session
from db.crud import create_or_update_question_review, get_question_review, ...
```

The same module imports the legacy `pipeline.db` wrapper (`list_prompts()` with no session) and the new `db.crud` functions (`db: Session` required). Maintainers must know which abstraction to use for each call.

#### D. `db/models.py::Generation` exposes a broad interface

With ~20 columns and multiple computed properties, the model serves templates, API endpoints, the lab, and analytics. Each client only needs a subset.

### 4.3 Recommended refactors (ISP), ordered by impact

1. **Create `pipeline/interfaces.py`** with small ports: `ScraperPort`, `LLMPort`, `PromptRepository`, `GenerationRepository`, `ContentStore`, `GroundingLogRepository`. High impact.
2. **Split `update_generation()` into focused methods**: `mark_success()`, `mark_error()`, `set_output_paths()`, `set_timeline()`. Or use a `GenerationUpdate` value object. Medium impact.
3. **Consolidate prompt access on `db.crud`** and remove the legacy `pipeline.db` wrapper from `web/main.py`. Medium impact.
4. **Define Pydantic response DTOs** (`GenerationSummary`, `GenerationDetail`, `GenerationTimeline`) so endpoints depend on narrow views instead of the full ORM model. Medium impact.

---

## 5. Dependency Inversion Principle (DIP)

> "High-level modules should not depend on low-level modules. Both should depend on abstractions. Abstractions should not depend on details. Details should depend on abstractions." [^1]

### 5.1 What is healthy

- FastAPI dependency injection is used for the database session in most endpoints:
  ```python
  # web/main.py
  def topic_page(request: Request, slug: str, prompt: Optional[str] = None,
                 db: Session = Depends(get_db_session)):
  ```
- `web/services/nursing_service.py` builder constructors accept `QuestionRepository`, an abstraction.
- `pipeline/config.py` centralizes environment values so modules do not hard-code URLs or secrets.

### 5.2 What violates DIP

#### A. `pipeline/run.py` directly imports and instantiates concrete modules

```python
# pipeline/run.py, lines 9-18
from pipeline.config import OUTPUT_DIR, DATA_DIR
from pipeline.scraper import fetch_ixl_topics, search_mathisfun_topic
from pipeline.content_adapter import build_adapter_prompt
from pipeline.question_generator import build_question_prompt, parse_json_array
from pipeline.llm_client import LLMClient
from pipeline.db import get_prompt
from db.database import SessionLocal
from db import crud
```

The high-level orchestrator depends on every low-level detail. There is no abstraction to invert.

#### B. `pipeline/llm_client.py::LLMClient` depends on concrete provider classes

```python
# pipeline/llm_client.py, lines 2, 26, 36, 42
from openai import OpenAI, AzureOpenAI
...
self.client = AzureOpenAI(...)
self.client = OpenAI(api_key=GROK_API_KEY, base_url=GROK_BASE_URL)
self.client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
```

There is no `LLMPort`; the orchestrator depends on `LLMClient`, which depends on concrete OpenAI/Azure clients.

#### C. `web/main.py` directly invokes `run_pipeline()`

```python
# web/main.py, line 15
from pipeline.run import run_pipeline
```

The web layer is coupled to the pipeline's concrete runner, its side effects, and its file-path contract.

#### D. `web/routers/nursing.py` uses a module-level singleton

```python
# web/routers/nursing.py, line 19
service = NursingService()
```

Although `NursingService` accepts an optional repository, the router ignores that capability and instantiates the concrete default. FastAPI's `Depends` should supply the service.

#### E. Direct file-system I/O in routers and services

```python
# web/routers/nursing.py, lines 192-208
EVENTS_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "nursing_events.jsonl"
with EVENTS_PATH.open("a", encoding="utf-8") as f:
    f.write(...)
```

Analytics logging depends directly on a local file path. A test environment or a future cloud deployment cannot substitute a different sink.

#### F. `pipeline/db.py` creates tables at import time

```python
# pipeline/db.py, line 16
Base.metadata.create_all(bind=engine)
```

The schema-creation side effect is a detail that should be controlled by an application bootstrap, not by importing a wrapper module.

### 5.3 Recommended refactors (DIP), ordered by impact

1. **Introduce dependency injection in `run_pipeline()`** so it receives `scraper`, `llm_client`, `prompt_repo`, `generation_repo`, and `content_store` as arguments. High impact.
2. **Create `LLMPort` and provider-specific adapters**; inject the adapter into `run_pipeline()`. High impact.
3. **Wrap pipeline orchestration behind a `ContentGenerationPort`** (e.g., `generate(topic, prompt_id) -> GenerationId`) and inject it into `web/main.py`. High impact.
4. **Inject `NursingService` via FastAPI `Depends`** and wire the repository in a composition root. Medium impact.
5. **Introduce an `AnalyticsSink` interface** (file, DB, null) and inject it into the nursing router. Medium impact.
6. **Introduce a `ContentStore` port** for file-system writes so tests and alternate storage can plug in. Medium impact.
7. **Move `Base.metadata.create_all()` to an explicit bootstrap function** called by `web/main.py` and `scripts/`. Low effort, high clarity.

---

## 6. Hexagonal / Clean Architecture Assessment

### 6.1 What is already present

| Pattern | Location | Assessment |
|---|---|---|
| Adapter (infrastructure) | `pipeline/scraper.py`, `pipeline/llm_client.py`, `pipeline/content_adapter.py` | Adapts external systems to the pipeline's needs, but without ports. |
| Repository + domain models | `web/repositories/question_repository.py`, `web/domain/models.py` | The nursing module already has clean layers. |
| Config externalization | `pipeline/config.py` | Good; environment-dependent values are centralized. |

### 6.2 What is missing

| Missing element | Why it matters |
|---|---|
| `pipeline/interfaces.py` with abstract ports | Without ports, no module can depend on abstractions. |
| Dependency injection container / composition root | `run.py` and `web/main.py` construct every dependency manually. |
| Domain layer for the math pipeline | Business rules (difficulty distribution, question normalization) are mixed with I/O and DB calls. |
| Use-case / application service | `run_pipeline()` is a script, not a clean use-case object. |
| Side-effect-free imports | `pipeline/db.py` creates tables on import, making tests and imports unpredictable. |
| Empty `src/` tree | The hexagonal skeleton is dead scaffolding. |

### 6.3 Domain logic leakage

| Layer | What lives there | What leaked there |
|---|---|---|
| `pipeline/` | scraping, LLM calls, file output | DB persistence, orchestration, topic slugging |
| `db/models.py` | SQLAlchemy ORM | presentation properties (`timeline`, `avg_rating`) |
| `web/main.py` | HTTP routing/rendering | file parsing, DB queries, direct pipeline runner call |
| `web/services/nursing_service.py` | nursing business logic | direct `DATA_DIR / "nursing_topics.json"` reads |

### 6.4 Deployment-layer separation

- `Dockerfile` is clean but copies `data/`, `output/`, and `test_pipeline.py` into the production image.
- `docker-compose.yml` is simple but has no healthcheck.
- `nginx.http.conf` / `nginx.ssl.conf` mix SSL termination, ACME challenges, static files, PWA routing, APK downloads, rate limiting, and proxying. These concerns could be split into included snippet files.

---

## 7. Prioritized Remediation Roadmap

| Priority | Principle | Action | Files touched |
|---|---|---|---|
| **Critical** | SRP, DIP | Refactor `pipeline/run.py::run_pipeline()` into a `PipelineRunner` use-case class with injected ports. | `pipeline/run.py`, new `pipeline/interfaces.py`, new service modules |
| **Critical** | SRP, DIP | Split `web/main.py` into focused FastAPI routers and keep routes thin. | `web/main.py`, new `web/routers/*.py` |
| **High** | OCP, DIP | Introduce `LLMPort` and provider adapters (`OpenAI`, `Azure`, `Grok`). | `pipeline/llm_client.py`, `pipeline/interfaces.py` |
| **High** | SRP | Remove `strip_html` duplication in `pipeline/run.py`. | `pipeline/run.py` |
| **High** | ISP | Create `pipeline/interfaces.py` with `ScraperPort`, `LLMPort`, `GenerationRepository`, `ContentStore`, `GroundingLogRepository`. | new `pipeline/interfaces.py` |
| **High** | ISP, DIP | Consolidate prompt access on `db.crud`; remove legacy `pipeline.db` from `web/main.py`. | `web/main.py`, `pipeline/db.py` |
| **Medium** | SRP | Move `Generation` presentation properties into Pydantic response schemas. | `db/models.py`, new `web/schemas/generation.py` |
| **Medium** | SRP | Move `Base.metadata.create_all()` out of `pipeline/db.py` into an explicit `init_db()`. | `pipeline/db.py`, `web/main.py`, `scripts/` |
| **Medium** | OCP | Externalize MathIsFun topic map into config or `TopicResolver` registry. | `pipeline/scraper.py`, new mapper/config |
| **Medium** | OCP | Parameterize prompt dimensions instead of hardcoding tuples. | `pipeline/config.py`, `web/main.py` |
| **Medium** | ISP | Replace fat `update_generation()` with focused methods or a value object. | `db/crud.py`, callers |
| **Medium** | LSP, ISP | Align `QuestionRepository` ABC with methods actually used by callers. | `web/repositories/question_repository.py`, `web/routers/nursing.py` |
| **Medium** | DIP | Inject `NursingService` via FastAPI `Depends` from a composition root. | `web/routers/nursing.py`, `web/main.py` |
| **Medium** | DIP | Introduce `AnalyticsSink` interface for nursing events. | `web/routers/nursing.py`, new analytics modules |
| **Low** | OCP | Model pipeline steps as `PipelineStep` strategies. | `pipeline/run.py` |
| **Low** | SRP | Remove `data/`, `output/`, `test_pipeline.py` from production Docker image. | `Dockerfile`, `.dockerignore` |
| **Low** | SRP | Either populate or delete the empty `src/` tree and update `AGENTS.md`. | `src/`, `AGENTS.md` |

---

## 8. Conclusion

Dr. Math has reached the point where its research-grade pipeline and its product-grade nursing module are pulling in opposite architectural directions. The nursing module shows that the team already knows how to build SOLID code: domain models, a repository ABC, builder services, and constructor injection. The math pipeline and `web/main.py` have not yet received the same treatment.

The guiding question for the next refactor cycle should be: *Would Barbara Liskov be able to substitute a new LLM provider, a new scraper, or a new repository without changing the callers?* Today, the answer is no for the pipeline and yes for nursing. Closing that gap is the single highest-leverage architectural investment before Phase 10.9.

Start with the critical items: decouple `run_pipeline()`, split `web/main.py`, and write `pipeline/interfaces.py`. Everything else is a consequence of those three moves.

---

## References

[^1]: Martin, R. C. (2002). *Agile Software Development, Principles, Patterns, and Practices*. Prentice Hall. (Contains the canonical treatments of SRP, ISP, and DIP.)

[^2]: Meyer, B. (1988). *Object-Oriented Software Construction*. Prentice Hall. (Origin of the Open/Closed Principle.)

[^3]: Liskov, B. (1988). Data abstraction and hierarchy. *ACM SIGPLAN Notices*, 23(5), 17-34. (Origin of the Liskov Substitution Principle, presented at OOPSLA '87.)

[^4]: Feathers, M. (2004). The SOLID acronym. Coined in correspondence with Robert C. Martin to summarize the five principles; discussed in Martin, R. C. (2017). *Clean Architecture: A Craftsman's Guide to Software Structure and Design*. Prentice Hall.

[^5]: Cockburn, A. (2005). Hexagonal architecture. Alistair Cockburn's blog. https://alistair.cockburn.us/hexagonal-architecture/ (accessed 2026-06-28).

[^6]: Evans, E. (2003). *Domain-Driven Design: Tackling Complexity in the Heart of Software*. Addison-Wesley.
