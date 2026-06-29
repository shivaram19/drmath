# ADR-030: PWA Service Worker Cache-Busting Strategy

**Date:** 2026-05-05  
**Scope:** Deployment-time invalidation of cached nursing PWA assets.  
**Research Phase:** Implementation of ADR-026 (PWA-first default mobile strategy).  
**Status:** Accepted.  
**Tracked in:** #58

---

## Context

The nursing PWA is cached by a service worker (`sw.js`). Without a cache-busting strategy, users may continue to see stale HTML, CSS, or JavaScript after a deploy. This is especially risky now that ISSUE-001 and ISSUE-002 ship learner-facing logic (spaced-repetition selector, weak-area concept card) in `app.js`.

## Decision

### 1. Per-deploy cache name

`scripts/deploy.sh` computes a deploy version from the current git short hash and injects it into the deployed `sw.js` as the `CACHE_NAME`. Because the service worker file itself changes on every deploy, the browser installs the new service worker, which:

1. Creates a new cache keyed by the deploy version.
2. Fetches fresh shell assets during install.
3. Deletes all older caches on activation.

### 2. Source file stays stable

The source `web/static/nursing/sw.js` keeps the default cache name `mathwise-nursing-v1` so local development is unaffected. Only the deployed copy in the nginx webroot is modified.

### 3. No manual user action required

The update path relies on the browser’s service-worker lifecycle (`install` → `skipWaiting` → `activate` → `clients.claim`), not on users clearing site data.

## Consequences

### Positive

- New deploys reliably deliver updated PWA code.
- No build step or filename hashing is required.
- Old caches are cleaned up automatically.

### Negative

- The service worker file is mutated server-side; the deployed copy differs from the repo copy.
- Cache busting happens only at deploy time; multiple changes between deploys still share one cache name.
- A failed `sed` replacement would leave the default cache name and stale assets.

## Alternatives Considered

1. **Filename hashing (`app.a1b2c3.js`).** Rejected because it requires a build toolchain the project does not currently use.
2. **Runtime `version.json` fetched by SW.** Rejected because the browser only re-installs the SW when `sw.js` bytes change; a separate version file would not trigger update checks.
3. **Manual cache-name bump in source.** Rejected because it is error-prone and easy to forget.

## References

[^1]: Google Developers. (2024). *Service workers: Update via cache*. https://developer.chrome.com/docs/workbox/service-worker-lifecycle
