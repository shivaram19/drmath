# ADR-004: Web Framework Selection

**Date:** 2026-05-03  
**Scope:** Frontend and API layer  
**Research Phase:** BFS completed  
**Status:** Accepted

## Context

The system requires:
1. A human-facing web UI for topic browsing, prompt management, and generation triggering.
2. REST API endpoints for programmatic access and future mobile clients.
3. Server-side rendering for SEO and initial page load performance.

## Decision

Use **FastAPI** with **Jinja2** server-side templates and minimal vanilla CSS/JS.

## Consequences

**Positive:**
- FastAPI's async-native design supports concurrent generation requests without blocking [^1].
- Jinja2 templates require no build step; deployment is a single `docker-compose up`.
- Automatic OpenAPI docs at `/docs` for API consumers.
- Starlette background tasks support async generation without blocking HTTP responses.

**Negative:**
- No client-side reactivity; full page reloads on navigation.
- Limited component reusability vs. React/Vue.

## Alternatives Considered

| Alternative | Rejected Because |
|-------------|-----------------|
| Flask | No native async; blocking under concurrent loads |
| Django | Overhead for a 4-route API; ORM not needed |
| React + Vite | Build step adds complexity; no SSR requirement justifies the cost |
| Next.js | Excellent but requires Node runtime; adds 300MB+ to container |

## References

[^1]: FastAPI documentation. https://fastapi.tiangolo.com/ (accessed 2026-05-03).
