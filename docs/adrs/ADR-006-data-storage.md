# ADR-006: Data Storage Strategy

**Date:** 2026-05-03  
**Scope:** Persistence layer for prompts, generations, and outputs  
**Research Phase:** BFS completed  
**Status:** Accepted

## Context

The system must persist:
1. **Prompts:** Small JSON array (< 100KB), append-only, read-heavy.
2. **Generation history:** Append-only log of generation attempts.
3. **Generated outputs:** Per-topic JSON files (20–30KB each), read-heavy after write.

Total dataset size: < 10MB for hundreds of topics. No relational queries, no joins, no transactions.

## Decision

Use **JSON file storage** for all persistence needs, with runtime artifacts in `data/` and `output/` (both gitignored).

## Consequences

**Positive:**
- Zero infrastructure cost (no database server).
- Human-readable; debuggable via `cat` and `jq`.
- Git-versionable for prompts (JSON files can be tracked if desired).
- No schema migration headaches.

**Negative:**
- No concurrent write safety (mitigated: single-writer process, append-only).
- No query capabilities beyond linear scan (acceptable for < 10MB).
- No backup/replication (mitigated: filesystem snapshots).

## Alternatives Considered

| Alternative | Rejected Because |
|-------------|-----------------|
| PostgreSQL | Requires server process, connection management, schema migrations for trivial data |
| SQLite | Better than PostgreSQL for this scale, but still adds dependency and locking complexity |
| MongoDB | Document model fits, but requires separate server; TCO not justified |
| Redis | In-memory only; data loss on restart without AOF persistence |

## References

[^1]: Martin, F., Chen, Y., Moore, R. L., & Westine, C. (2020). Systematic review of adaptive learning research designs. *Educational Technology Research & Development*, 68, 1903–1929.
