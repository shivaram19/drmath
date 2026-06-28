# Introspection / Self-Interview / Retrospect — Unknowns Surfaced by the SOLID Audit

**Date:** 2026-06-28  
**Scope:** Cross-domain reflection on the SOLID audit findings; first-principles investigation of architecture, refactoring strategy, and sequencing relative to the product roadmap.  
**Research Phase:** Bidirectional / cross-domain impact analysis  

---

## 1. The mental space after the audit

The SOLID audit surfaced a fracture: the **nursing module** already behaves like a well-factored application, while the **math pipeline** still behaves like a research script that accidentally reached production. The instinctive reaction is to impose a grand architecture — ports everywhere, domain entities, use-case layers — and "fix" the codebase in one sweep. That instinct is exactly what this document questions.

The liberators of SOLID did not write rules for rule-following. They wrote heuristics for managing change. Meyer warned that abstractions are only useful when they protect a real boundary [^1]. Liskov showed that substitutability depends on behavioral contracts, not interface count [^2]. Feathers defined legacy code as code without tests and taught that the safest path is incremental, not heroic [^3]. Fowler documented the Strangler Fig pattern precisely because big-bang rewrites usually fail [^4]. Metz reminded us that the wrong abstraction costs more than duplication [^5].

So the real question is not *"How do we become perfectly SOLID?"* but *"Where is the friction that will actually kill the next feature, and what is the smallest safe move that removes it?"*

---

## 2. Unknowns that need answers

### U1 — Architecture depth: full hexagonal/clean, or pragmatic service layer?

**Why it matters.** The empty `src/` tree promises hexagonal architecture, but the working code lives in `pipeline/` and `web/`. A full clean-architecture migration would create new abstractions before we know which boundaries actually move.

**Research.**
- Cockburn's original Ports and Adapters (2005) isolates the application core from external technology so the core can be tested and swapped independently [^6].
- Martin's Clean Architecture (2017) adds concentric layers (Entities → Use Cases → Interface Adapters → Frameworks/Drivers) and the Dependency Rule: source dependencies point inward [^7].
- These patterns pay off for long-lived systems with multiple integrations and changing infrastructure. They are overhead for short-lived or single-integration scripts [^8][^9].
- Evans notes that Ports and Adapters is "a better description of what we do than the layered architecture" for domain-driven systems [^10].

**Self-interview.**
- *Q: Does Dr. Math need multiple UI or persistence implementations?* A: Not today. One web UI, one SQLite DB, one JSON question bank.
- *Q: Which boundaries actually change?* A: LLM provider (OpenAI/Azure/Grok/exhausted), scraper (Obscura today, maybe direct HTTP tomorrow), content store (local files now, maybe S3/cloud later), analytics sink (file now, maybe DB/queue later).
- *Q: Is the math pipeline a long-lived product or a research tool?* A: It is a research-grade generator that the manager uses. It is not user-facing. Its main risk is fragility when we add providers or schema changes.

**Answer.** Adopt a **pragmatic ports-and-adapters** posture, not a full clean-architecture rewrite. Define ports only for the volatile boundaries listed above. Keep the internal structure simple: orchestrator → services → adapters. Do not create a `src/` hexagon until a real domain model (not just data shapes) emerges.

---

### U2 — Refactoring path: big rewrite or strangler fig?

**Why it matters.** `pipeline/run.py::run_pipeline()` and `web/main.py` are large. Rewriting them in one PR is risky and would block Phase 10.9.

**Research.**
- Fowler's Strangler Fig pattern: build the new system alongside the old, route traffic incrementally, and let the old system shrink until it can be removed [^4].
- Feathers' legacy-code algorithm: add characterization tests, find seams, break dependencies just enough to change behavior safely [^3].
- Fowler's definition of refactoring: "a change made to the internal structure of software to make it easier to understand and cheaper to modify without changing its observable behavior" [^11].

**Self-interview.**
- *Q: Can we afford a feature freeze?* A: No. Phase 10.9 WhatsApp reminders and the APK funnel are active.
- *Q: What is the public surface of the pipeline?* A: `run_pipeline(topic, output_path, prompt_id)` and the web `/generate` endpoint. The output JSON schema is the real contract.
- *Q: What is the public surface of `web/main.py`?* A: Many FastAPI routes. We can split routes without changing URLs.

**Answer.** Use **Strangler Fig + Branch by Abstraction**:
1. Wrap the existing `run_pipeline()` in a compatibility shell.
2. Build `PipelineRunner` behind the shell, one port at a time.
3. Switch callers only when the new path matches the old behavior.
4. Split `web/main.py` route-by-route; each split is a small, reversible PR.

---

### U3 — Test strategy: how do we avoid regressions during structural change?

**Why it matters.** The pipeline touches LLMs and subprocesses; unit tests are scarce. Refactoring without a safety net is dangerous.

**Research.**
- Feathers: legacy code is code without tests. Before refactoring, write **characterization tests** that pin current behavior, even if that behavior is ugly [^3].
- Golden-master / snapshot testing is a valid characterization technique when the output is deterministic enough to compare [^12].
- Fowler: refactoring requires a solid test suite; without it, you are not refactoring — you are just changing code [^11].

**Self-interview.**
- *Q: Is the pipeline output deterministic?* A: No — LLM content varies. But the *structure* (topic, prompt fields, question count, JSON schema, grounding logs) is deterministic given the same inputs.
- *Q: What can we snapshot?* A: The shape of the output JSON, the DB `generations` row, and the files created. We can mock the LLM and scraper to make tests deterministic.
- *Q: What about the web layer?* A: Use FastAPI `TestClient` and `app.dependency_overrides` to inject fakes.

**Answer.**
1. Add **characterization tests** for `run_pipeline()` with mocked LLM and scraper.
2. Add **HTTP contract tests** for the web routes we will split.
3. Use these tests as the guardrail for every refactor PR.
4. Do not aim for 100% coverage; aim for coverage of the behavior we are about to move.

---

### U4 — Abstraction timing: when do we extract a port vs. leave duplication?

**Why it matters.** Premature ports are just premature abstractions. Metz's warning about the wrong abstraction is particularly relevant for a small team [^5].

**Research.**
- Metz: "Duplication is far cheaper than the wrong abstraction." The wrong abstraction traps you in conditionals and parameter bloat [^5].
- Cockburn: ports are useful when you need multiple adapters or when testing the core without the real adapter [^6].
- The "Rule of Three" (variously attributed) suggests waiting for three concrete examples before extracting a shared abstraction.

**Self-interview.**
- *Q: Do we have multiple LLM providers today?* A: Yes — OpenAI, Azure, Grok are already in the code, even if only OpenAI is reliable.
- *Q: Do we have multiple scrapers?* A: No. Only Obscura. But the boundary is real because Obscura is an external subprocess.
- *Q: Do we have multiple analytics sinks?* A: Not yet. But Phase 10.9 will likely need a DB/queue sink for WhatsApp events.

**Answer.** Extract ports where:
- there is already more than one implementation or a high probability of one (LLM provider, analytics sink),
- the dependency is external and hard to test (scraper, file store),
- the boundary protects a product feature (consent-gated analytics).
Leave duplication alone everywhere else until a third example appears.

---

### U5 — The empty `src/` tree: populate, delete, or ignore?

**Why it matters.** Empty directories create confusion. AGENTS.md says scraper code belongs in `pipeline/` and web logic in `web/`, which makes `src/` a dead limb.

**Research.**
- Honesty of structure: a codebase should look like what it is. Dead scaffolding signals unfinished intent [^13].
- Fowler: remove dead code; it is a form of documentation that lies [^11].

**Self-interview.**
- *Q: Is anything imported from `src/`?* A: No. `grep` found zero references.
- *Q: Would populating `src/` improve the codebase?* A: Only if we commit to a full migration. That is not justified by current needs.
- *Q: What is the minimal honest action?* A: Delete `src/` and update AGENTS.md to describe the actual layout.

**Answer.** **Delete `src/`** and remove the implication of a hexagonal skeleton from `AGENTS.md`. If a true core emerges later, we will create it explicitly (e.g., `pipeline/core` or `web/domain`) rather than maintain a ghost directory.

---

### U6 — Sequencing: should SOLID fixes block Phase 10.9 WhatsApp reminders?

**Why it matters.** The team wants to ship user-facing value. Architecture work can become a vanity project if it delays experiments.

**Research.**
- Cockburn/Martin: architecture should support delivery, not replace it [^6][^7].
- Fowler: technical debt should be paid down when it slows you down or increases risk; not all debt must be repaid immediately [^11].
- The Strangler Fig pattern lets new features use the new structure while old features stay on the old structure [^4].

**Self-interview.**
- *Q: Does Phase 10.9 need the pipeline refactor?* A: No. WhatsApp reminders are in the nursing module.
- *Q: Does Phase 10.9 need the `web/main.py` split?* A: Partially. It needs a clean analytics sink and a composition root for `NursingService`.
- *Q: What is the smallest architecture move that unblocks Phase 10.9?* A: Extract `AnalyticsSink` and inject `NursingService` via FastAPI `Depends`. Everything else can wait.

**Answer.** Do not block Phase 10.9. Run architecture and product work in parallel:
- **Before Phase 10.9:** inject `NursingService`, extract `AnalyticsSink`, add consent/phone models.
- **During Phase 10.9:** build the WhatsApp opt-in and scheduler on the new sink.
- **After Phase 10.9:** continue strangler-fig refactoring of the pipeline and `web/main.py`.

---

### U7 — Repository interfaces: one big ABC or role-based interfaces?

**Why it matters.** `JsonFileQuestionRepository` exposes methods not in `QuestionRepository`, breaking substitutability. But over-segregating creates interface soup.

**Research.**
- Martin: Interface Segregation Principle says clients should not depend on methods they do not use [^14].
- Evans/Vernon: repositories are per-aggregate; the interface should match the aggregate's needs [^15].
- Practical FastAPI patterns: class-based dependencies with `Annotated[Service, Depends(Service)]` keep injection clean [^16].

**Self-interview.**
- *Q: Who uses `QuestionRepository`?* A: Builders in `NursingService` use reading/filtering; the router uses listing/counting/meta; diagnostic uses only `get_diagnostic_set`.
- *Q: Will we have a DB-backed repository soon?* A: Possibly, once the nursing seed bank moves from JSON to DB.
- *Q: What is the honest contract?* A: The contract is the set of methods callers actually invoke.

**Answer.** Promote the methods that are actually called (`filter`, `list_subjects`, `list_topics`, `get_meta`, `count_by_subject`) into `QuestionRepository`. If a future caller needs a narrower view, introduce a role interface then. Do not split preemptively.

---

## 3. First-principles synthesis

The foundational axiom: **software architecture exists to manage change cost.** Dr. Math is changing in two directions at once:

1. **Research-to-product:** the nursing module is becoming a real product with consent, analytics, and distribution.
2. **Script-to-system:** the math pipeline is becoming a reproducible content-generation system with multiple providers and reviewers.

The right architecture is the one that lowers the cost of the *next* change in each direction. For nursing, that means clean boundaries around consent, analytics, and question sources. For the pipeline, that means isolating the orchestrator from volatile infrastructure. We do not need a unified cathedral; we need two well-fenced gardens connected by clear paths.

---

## 4. Adjusted plan — architecture and product together

The previous plan in `docs/research/introspection-phase10_8-and-beyond-2026-06-28.md` stays valid for product phases. This section inserts **architecture tracks** that run alongside them and explicitly gates the riskiest moves.

### Track A — Immediate safety net (do before any large refactor)

1. Add characterization tests for `pipeline/run.py::run_pipeline()`:
   - Mock `fetch_ixl_topics()`, `search_mathisfun_topic()`, and `LLMClient.generate()`.
   - Assert output JSON schema, DB row fields, file existence, and grounding-log count.
2. Add `TestClient` tests for the most-used web routes (`/`, `/manager`, `/topic/{slug}`, `/lab`, `/generate`, `/api/evaluations`).
3. Capture a golden-master output file for one topic (e.g., `Integers`) to detect unintended output drift.

**Gating criterion:** `pytest` must pass with the new tests before any structural refactor is merged.

### Track B — Pragmatic decoupling of the math pipeline

1. Create `pipeline/interfaces.py` with minimal ports:
   - `ScraperPort`
   - `LLMPort`
   - `PromptRepository`
   - `GenerationRepository`
   - `ContentStore`
   - `GroundingLogRepository`
2. Implement adapters:
   - `ObscuraScraper(ScraperPort)`
   - `OpenAILLMAdapter(LLMPort)`, `AzureLLMAdapter(LLMPort)`, `GrokLLMAdapter(LLMPort)`
   - `FileSystemContentStore(ContentStore)`
   - `SQLAlchemyGenerationRepository(GenerationRepository)`
   - `SQLAlchemyGroundingLogRepository(GroundingLogRepository)`
3. Create `pipeline/use_cases/generate_content.py` with a `GenerateContentUseCase` that depends only on the ports.
4. Keep `pipeline/run.py::run_pipeline()` as a thin compatibility wrapper that wires the default adapters and calls the use case.
5. Move `Base.metadata.create_all()` from `pipeline/db.py` to an explicit `init_db()` invoked by `web/main.py` and scripts.
6. Remove duplicate `strip_html()` from `pipeline/run.py`.

**Gating criterion:** `run_pipeline()` produces identical output and DB state before and after the refactor.

### Track C — Web layer composition and route split

1. Create a composition root (`web/container.py` or `web/dependencies.py`) that wires:
   - `QuestionRepository` → `JsonFileQuestionRepository`
   - `NursingService(repository)`
   - `AnalyticsSink` → `JsonlAnalyticsSink`
2. Inject `NursingService` and `AnalyticsSink` into `web/routers/nursing.py` via FastAPI `Depends`.
3. Move analytics recording out of the nursing router into the sink.
4. Split `web/main.py` into routers incrementally:
   - `web/routers/pages.py` (home, manager, about)
   - `web/routers/topics.py` (topic page, topic list)
   - `web/routers/prompts.py` (prompt builder, CRUD)
   - `web/routers/generations.py` (generate, status, history)
   - `web/routers/evaluations.py` (lab, compare, ratings)
5. Move `Generation` presentation properties (`avg_rating`, `difficulty_dict`, `timeline`) into Pydantic schemas.

**Gating criterion:** All existing URLs respond identically; `TestClient` tests pass.

### Track D — Structural cleanup

1. Delete the empty `src/` tree.
2. Update `AGENTS.md` to describe the actual layout (`pipeline/`, `web/`, `db/`) and retire the `src/` hexagon reference.
3. Remove `data/`, `output/`, and `test_pipeline.py` from the production Docker image via `.dockerignore`.
4. Consolidate prompt access: migrate `web/main.py` from legacy `pipeline.db` to `db.crud`.

### Product phases revised

| Phase | Work | Depends on | Status |
|---|---|---|---|
| 10.8+ | Monitor APK funnel; document click→install gap. | — | Ongoing |
| **10.8a** | **Safety net:** characterization tests for pipeline and web routes. | — | New |
| **10.8b** | **Pipeline decoupling:** ports/adapters for LLM, scraper, content store; `GenerateContentUseCase`; compatibility wrapper. | 10.8a | New |
| **10.8c** | **Web composition:** inject `NursingService`, extract `AnalyticsSink`, minimal route split. | 10.8a | New |
| 10.9 | WhatsApp daily quiz reminders: opt-in, consent record, scheduler, STOP handling. | 10.8c | Revised gate |
| 10.10 | Expand nursing seed bank with source verification metadata. | — | Unchanged |
| 10.11 | Play Store release spike if side-load click→open remains low. | 10.8+ | Unchanged |

### Decision authority

- **ADR-024** (WhatsApp channel, consent, retention) must be written before Phase 10.9 code.
- **ADR-025** (pragmatic SOLID refactor strategy) must be written before Track B/C code. This research doc provides the evidence.

---

## 5. Retrospect — what I would do differently

- **Do not let an empty `src/` tree survive more than one sprint.** It is a promise that nobody keeps, and it confuses every new contributor.
- **Add characterization tests before diagnosing architecture.** Without them, an audit is just an opinion.
- **Separate "what is broken" from "what needs to be fixed now."** `web/main.py` is broken in five ways, but only one of them blocks Phase 10.9.
- **Respect the nursing module's existing pattern.** Instead of imposing a new architecture on it, extend its repository/service/sink pattern to the boundaries that are still leaking.

---

## 6. Conclusion

The SOLID audit is correct but incomplete without this introspection. The codebase does not need a cathedral; it needs **two incremental refactors** running under a **safety net of tests**. The highest-leverage moves are:

1. Add characterization tests now.
2. Delete `src/` and update `AGENTS.md`.
3. Decouple the pipeline through ports for the boundaries that actually change.
4. Inject `NursingService` and extract `AnalyticsSink` before Phase 10.9.
5. Write ADR-025 to record the pragmatic refactor strategy.

Everything else is a consequence.

---

## References

[^1]: Meyer, B. (1988). *Object-Oriented Software Construction*. Prentice Hall.

[^2]: Liskov, B. (1988). Data abstraction and hierarchy. *ACM SIGPLAN Notices*, 23(5), 17-34.

[^3]: Feathers, M. (2004). *Working Effectively with Legacy Code*. Prentice Hall Professional.

[^4]: Fowler, M. (2004). Strangler Fig application. https://martinfowler.com/bliki/StranglerFigApplication.html (accessed 2026-06-28).

[^5]: Metz, S. (2016). The wrong abstraction. https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction (accessed 2026-06-28).

[^6]: Cockburn, A. (2005). Hexagonal architecture. https://alistair.cockburn.us/hexagonal-architecture/ (accessed 2026-06-28).

[^7]: Martin, R. C. (2017). *Clean Architecture: A Craftsman's Guide to Software Structure and Design*. Prentice Hall.

[^8]: Cogent. (n.d.). Designing scalable, secure applications: choosing between clean, hexagonal, and layered architectures. https://cogentinfo.com/resources/designing-scalable-secure-applications-choosing-between-clean-hexagonal-and-layered-architectures (accessed 2026-06-28).

[^9]: HappyCoders. (2023). Hexagonal architecture — what is it? https://www.happycoders.eu/software-craftsmanship/hexagonal-architecture/ (accessed 2026-06-28).

[^10]: Evans, E. (2013). Foreword to Vernon, V. *Implementing Domain-Driven Design*. Addison-Wesley.

[^11]: Fowler, M. (2018). *Refactoring: Improving the Design of Existing Code* (2nd ed.). Addison-Wesley.

[^12]: Feathers, M. (2004). Golden master / characterization testing. Discussed in *Working Effectively with Legacy Code*, Prentice Hall Professional.

[^13]: Martin, R. C. (2002). *Agile Software Development, Principles, Patterns, and Practices*. Prentice Hall.

[^14]: Martin, R. C. (2002). The Interface Segregation Principle. In *Agile Software Development, Principles, Patterns, and Practices*. Prentice Hall.

[^15]: Evans, E. (2003). *Domain-Driven Design: Tackling Complexity in the Heart of Software*. Addison-Wesley.

[^16]: FastAPI. (n.d.). Dependencies — first steps. https://fastapi.tiangolo.com/tutorial/dependencies/ (accessed 2026-06-28).
