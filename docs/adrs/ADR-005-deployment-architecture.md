# ADR-005: Deployment Architecture

**Date:** 2026-05-03  
**Scope:** Production infrastructure  
**Research Phase:** BFS completed  
**Status:** Accepted

## Context

The system must be deployable by a single user (Bill) on a standard Linux VM with minimal DevOps expertise. Target domain: `drmath.trelolabs.com`.

## Decision

**Docker Compose** stack with two services:
1. `drmath` (FastAPI app) — port 8000 internal.
2. `nginx` (reverse proxy + static file server) — ports 80/443 external.

Static files mounted as read-only volumes. Runtime data (`data/`, `output/`) mounted as writable volumes.

## Consequences

**Positive:**
- Single-command deploy (`docker-compose up -d`).
- Nginx handles TLS termination, static file caching, and reverse proxying.
- Containers are stateless; data persists via volume mounts.
- Easy rollback: `docker-compose down && docker-compose up -d`.

**Negative:**
- No horizontal scaling (single container per service).
- No orchestration (Kubernetes) — but not needed for single-tenant use.
- HTTPS requires manual certbot step (documented in `DEPLOY.md`).

## Alternatives Considered

| Alternative | Rejected Because |
|-------------|-----------------|
| Kubernetes | Overkill for single-VM, single-user deployment |
| Serverless (AWS Lambda) | Cold start latency unacceptable for Obscura + LLM pipeline (30–120s) |
| PM2 + Nginx directly on host | Harder to reproduce across environments; dependency conflicts |

## References

[^1]: Docker Compose documentation. https://docs.docker.com/compose/ (accessed 2026-05-03).
