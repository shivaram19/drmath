# DECISION-20260513-001: Backend Language & Framework Selection

**Date:** 2026-05-13  
**Proposal:** Select the runtime language, web framework, and ORM for the student-facing Dr. Math backend.  
**Risk Level:** Critical  
**Final Decision:** Deferred pending BFS completion and TCO analysis.  

---

## Proposal

Select among:
- **Option A:** Node.js + Express + Prisma + PostgreSQL + Redis
- **Option B:** Python + FastAPI + SQLAlchemy 2.0 + PostgreSQL + Redis
- **Option C:** Hybrid / Polyglot (Python pipeline + Node.js student API)
- **Option D:** "Agentic Backend" (LLM-orchestrated adaptation)

## Council Deliberation

| Persona | Stance | Key Point |
|---------|--------|-----------|
| Research Scientist | Endorse | No learning-science evidence favors one runtime; decision should be engineering-driven. |
| First-Principles Engineer | Concern | Derive from the state machine, not ecosystem trends. |
| Distributed Systems Architect | Concern | Hybrid option adds integration complexity and consistency risk. |
| Infrastructure-First SRE | Concern | Agentic option lacks observability and auditability for child safety. |
| Diagnostic Problem-Solver | Concern | Language decision is inseparable from database/scale assumptions. |
| Ethical Technologist | Concern | Data-model discipline matters more than language for student privacy. |
| Resource Strategist | **Block** | TCO analysis is missing for all options. |
| Curious Explorer | Endorse | Propose a spike implementing the same endpoint in Python and Node.js. |
| Clarity-Driven Communicator | Endorse | Final decision must be recorded in ADR-018. |
| Inner-Self Guided Builder | Endorse | Bias toward boring, well-understood technology. |

## Rationale

The Council agreed that insufficient evidence exists to overturn the existing FastAPI decision (ADR-004). The "agentic backend" concept is too vague to evaluate. A hybrid polyglot architecture should be rejected unless a clear service boundary justifies the operational overhead. The decision is deferred until BFS landscape research and DFS TCO/schema deep-dives are complete.

## Interim Position

1. **Default path:** Retain Python/FastAPI/SQLAlchemy to minimize context switching and avoid polyglot overhead.
2. **Explicit evaluation:** Node.js/Express/Prisma will be compared in a DFS deep-dive with TCO and team-velocity analysis.
3. **Agentic decomposition:** "Agentic backend" will be broken into bounded roles (hint generation, misconception diagnosis, content regeneration triggers) and evaluated individually.
4. **Database migration:** SQLite → PostgreSQL is required regardless of language choice.

## Dissent Recorded

None. All personas accepted the deferred decision.

## Action Items

- [ ] Complete `docs/research/bfs/bfs-03-backend-architecture-landscape.md`
- [ ] Write DFS TCO comparison: `docs/research/dfs/dfs-07-backend-stack-tco.md`
- [ ] Write DFS schema design: `docs/research/dfs/dfs-04-adaptive-database-schema.md`
- [ ] Reconvene Council and write `docs/adrs/ADR-018-backend-language-framework.md`
