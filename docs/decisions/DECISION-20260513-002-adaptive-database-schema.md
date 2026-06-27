# DECISION-20260513-002: Adaptive Database Schema v1

**Date:** 2026-05-13  
**Proposal:** Adopt the PostgreSQL schema defined in `docs/research/dfs/dfs-04-adaptive-database-schema.md` as the v1 student-facing data model for Dr. Math.  
**Risk Level:** High  
**Final Decision:** Approved in principle; blocked from code until ADR-019 is written.  

---

## Council Deliberation

| Persona | Stance | Key Point |
|---------|--------|-----------|
| Research Scientist | Endorse | Schema aligns with ASSISTments, Duolingo, and ADR-007 Mark system. |
| First-Principles Engineer | Endorse | Derived from atomic student action: see → hint → answer → update state. |
| Distributed Systems Architect | Concern | Need retention/cold-storage strategy for large `attempts` table. |
| Infrastructure-First SRE | Concern | Need latency metrics before production. |
| Diagnostic Problem-Solver | Concern | Pipeline output lacks concept/misconception tags; tagging strategy required. |
| Ethical Technologist | Endorse | Privacy-by-default design; recommend encrypting Mark JSONB at rest. |
| Resource Strategist | Concern | Need per-student cost model for Postgres + Redis + LLM. |
| Curious Explorer | Endorse | Extensible for BKT, HLR, and A/B experiments. |
| Clarity-Driven Communicator | **Block** | Major architectural decision requires ADR before any code. |
| Inner-Self Guided Builder | Endorse | Serves the child first. |

## Rationale

The schema is research-backed, privacy-respecting, and extensible to future games and spaced repetition. The blocking concern is procedural: an ADR must be written before migration code. All technical concerns will be addressed in that ADR.

## Final Proposal

1. Adopt the schema from `dfs-04-adaptive-database-schema.md`.
2. Create ADR-019 documenting the decision, retention policy, observability, and cost model.
3. Create DFS research task for question concept/misconception tagging.
4. No code or migrations until ADR-019 is accepted.

## Dissent Recorded

None.

## Action Items

- [ ] Write `docs/adrs/ADR-019-adaptive-database-schema.md`
- [ ] Write `docs/research/dfs/dfs-08-question-concept-tagging.md`
- [ ] Define cost model for student runtime
- [ ] Define data retention and cold-storage policy
- [ ] Define observability metrics for adaptive loop
