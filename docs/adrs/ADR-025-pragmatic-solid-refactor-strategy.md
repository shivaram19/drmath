# ADR-025: Pragmatic SOLID Refactor Strategy — Ports for Volatile Boundaries, Strangler Fig for the Rest

**Date:** 2026-06-28  
**Scope:** How to act on the SOLID audit findings without over-engineering the codebase or blocking product delivery.  
**Research Phase:** Bidirectional / cross-domain impact analysis, informed by `docs/research/bidirectional/bidirectional-09-introspection-solid-unknowns.md`.  
**Status:** Accepted.

---

## Context

The SOLID audit (`docs/research/bidirectional/bidirectional-08-solid-audit-2026-06-28.md`) identified two architectural realities in Dr. Math:

1. The **nursing module** (`web/domain`, `web/repositories`, `web/services`) already follows SOLID reasonably well.
2. The **math pipeline** (`pipeline/run.py`) and the **web entry point** (`web/main.py`) remain procedural, with tight coupling to concrete infrastructure.

We must decide how deeply to refactor before continuing with Phase 10.9 (WhatsApp reminders) and Phase 10.10 (seed-bank expansion). A full clean-architecture rewrite would delay product experiments. Doing nothing will make the next provider swap, schema change, or analytics sink increasingly risky.

Research in `docs/research/bidirectional/bidirectional-09-introspection-solid-unknowns.md` concluded that we should apply **pragmatic ports-and-adapters** only where boundaries are volatile, use the **Strangler Fig pattern** to migrate incrementally, and add **characterization tests** before moving code.

---

## Decision

**Adopt a pragmatic SOLID refactor strategy:**

1. Define ports only for boundaries that already have multiple implementations or a high probability of changing: LLM provider, scraper, content store, generation repository, grounding-log repository, and analytics sink.
2. Keep the internal structure simple (orchestrator → services → adapters) rather than introducing a full clean-architecture layer cake.
3. Preserve existing public APIs (`run_pipeline()`, FastAPI routes) as thin compatibility wrappers while new implementations grow behind them.
4. Refactor incrementally, route-by-route and port-by-port, not in a single big-bang PR.
5. Delete the empty `src/` tree and update `AGENTS.md` to reflect the actual layout.
6. Add characterization tests before any structural change.
7. Do not block Phase 10.9; unblock it by injecting `NursingService` and extracting an `AnalyticsSink` first.

---

## Consequences

### Positive

- Lower risk than a full rewrite; each refactor PR is small and reversible.
- Existing product features keep working because old APIs remain compatibility wrappers.
- New features (WhatsApp reminders, new LLM providers, cloud storage) can plug into defined ports instead of editing god functions.
- The nursing module's existing clean pattern is extended rather than replaced.
- Tests become possible because ports can be mocked or faked.

### Negative

- The codebase will temporarily contain two styles: old procedural paths and new port-based paths.
- Maintainers must know which code paths are "strangled" and which are still legacy.
- Some duplication may remain until the third example justifies a shared abstraction.

### Neutral

- `pipeline/interfaces.py` will be created, fulfilling the intent stated in `AGENTS.md`.
- The `src/` tree will be removed; if a true hexagonal core emerges later, it will be created explicitly under `pipeline/` or `web/`.

---

## Alternatives Considered

1. **Full clean-architecture migration.** Rejected. The project does not yet have rich enough domain logic to justify entities, use cases, and multiple mapping layers. The overhead would delay product delivery without proportional benefit [^1][^2].
2. **No refactor; keep shipping features.** Rejected. The god functions in `pipeline/run.py` and `web/main.py` already slow down provider/schema changes and will block WhatsApp analytics integration.
3. **Big-bang rewrite of `pipeline/run.py` and `web/main.py`.** Rejected. Without characterization tests, a rewrite risks silent regressions in output JSON, DB state, and route behavior [^3].
4. **Populate the empty `src/` tree.** Rejected. Empty scaffolding is worse than no scaffolding; it misleads contributors. Delete it now and recreate a core only when a real domain model exists [^4].

---

## Implementation Log

- **2026-05-05** — Phase 10.8b complete: math pipeline refactored into ports (`pipeline/interfaces.py`), adapters (`pipeline/adapters.py`), and `GenerateContentUseCase` (`pipeline/use_cases.py`). `pipeline/run.py` remains a compatibility wrapper.
- **2026-05-05** — Phase 10.8c complete (minimal scope): web composition root created in `web/dependencies.py`; `NursingService` and `AnalyticsSink` injected into `web/routers/nursing.py` via FastAPI `Depends`. `web/main.py` left intact; router decomposition deferred to a future incremental cleanup.

## Council of Ten Deliberation Summary

- **Research Scientist:** The decision is backed by first-principles analysis of change cost, not by architectural fashion.
- **First-Principles Engineer:** We isolate the boundaries that actually move (LLM, scraper, store, sink) and leave stable code alone.
- **Distributed Systems Architect:** Ports/adapters allow future adapters (queue, cloud storage, new scraper) without touching the core.
- **Infrastructure-First SRE:** Characterization tests and incremental rollout reduce blast radius.
- **Ethical Technologist:** No new dependencies; the refactor reuses FastAPI's built-in `Depends`.
- **Resource Strategist:** Avoids the TCO of a full rewrite and the ongoing cost of maintaining empty directories.
- **Diagnostic Problem-Solver:** Targets the root cause (coupling) rather than symptoms (more features tacked onto god modules).
- **Curious Explorer:** Findings recorded in `docs/research/bidirectional/bidirectional-09-introspection-solid-unknowns.md`.
- **Clarity-Driven Communicator:** This ADR makes the strategy explicit so future refactors are consistent.
- **Inner-Self Guided Builder:** The plan protects the child's learning experience by reducing regression risk.

---

## References

[^1]: Cockburn, A. (2005). Hexagonal architecture. https://alistair.cockburn.us/hexagonal-architecture/ (accessed 2026-06-28).

[^2]: Martin, R. C. (2017). *Clean Architecture: A Craftsman's Guide to Software Structure and Design*. Prentice Hall.

[^3]: Feathers, M. (2004). *Working Effectively with Legacy Code*. Prentice Hall Professional.

[^4]: Fowler, M. (2018). *Refactoring: Improving the Design of Existing Code* (2nd ed.). Addison-Wesley.
