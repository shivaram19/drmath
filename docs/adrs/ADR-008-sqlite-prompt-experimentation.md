# ADR-008: SQLite for Prompt Experimentation & Evaluation

**Date:** 2026-05-03
**Scope:** Persistence layer for manager-driven prompt A/B testing and evaluation
**Research Phase:** Requirements-driven; supersedes ADR-006 for evaluation use-case
**Status:** Accepted

## Context

ADR-006 selected JSON file storage for all persistence on the grounds that:
- Dataset size is < 10MB
- No relational queries or joins needed
- Zero infrastructure cost preferred

New requirements have emerged:
1. **Manager must experiment with prompts** — create variants, generate the same topic multiple times, compare outputs.
2. **Evaluation tracking** — 1–5 star ratings per generation, with notes, to identify which prompt produces the best results.
3. **A/B comparison queries** — "Show me all generations of topic X with prompt Y, sorted by rating."
4. **Leaderboard analytics** — average rating per prompt across all topics.

JSON files cannot efficiently support cross-table joins (generations × prompts × evaluations), aggregate queries (`AVG(rating) GROUP BY prompt_id`), or referential integrity (deleting a prompt cascades to its generations).

## Decision

Introduce **SQLite** as an application-embedded database for:
- `prompts`, `topics`, `generations`, `evaluations`, `grounding_logs`

Keep JSON file output in `output/` for backward compatibility and human readability.

## Consequences

**Positive:**
- SQL enables complex queries: leaderboard, filtered history, version comparison [^1].
- Foreign key constraints maintain referential integrity.
- ACID transactions prevent corruption during concurrent web API calls.
- SQLAlchemy ORM provides typed, testable data access.
- SQLite is file-based: zero server process, trivial backups (copy `data/drmath.db`).

**Negative:**
- Adds `sqlalchemy>=2.0.0` dependency (one package, well-maintained).
- Schema migrations required when models change (mitigated: SQLAlchemy `Base.metadata.create_all()` handles creation; Alembic reserved for future if schema evolves).
- Legacy JSON `data/prompts_db.json` and `data/generations_db.json` become read-only; migration script provided.

## Alternatives Considered

| Alternative | Rejected Because |
|-------------|-----------------|
| Keep JSON, build query engine in Python | Reinventing SQLite; O(n²) joins on generation + prompt + evaluation arrays |
| PostgreSQL | Overkill for single-process, single-user manager tool; adds server management |
| DuckDB | Excellent analytical engine, but SQLAlchemy support less mature than SQLite |

## References

[^1]: SQLite Project. (2024). *Appropriate Uses For SQLite*. https://sqlite.org/whentouse.html
