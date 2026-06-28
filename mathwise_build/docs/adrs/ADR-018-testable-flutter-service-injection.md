# ADR-018: Testable Service Injection for the Nursing Flutter Module

**Date:** 2026-05-14  
**Scope:** Architecture of dependency injection and retry resilience in `mathwise_build/lib/features/nursing`.  
**Status:** Approved  
**Research Phase:** DFS (technology deep-dive) + retrospective root-cause analysis

---

## Context

The nursing module needs to be testable without network calls, resilient to transient failures, and maintainable by a small team. During Phase 7 widget testing, a quiz-submit test timed out because:

1. `NursingQuizScreen` did not propagate its injected `NursingApiService` to `NursingResultsScreen`, so the results screen instantiated a fresh service and hit the widget-test harness's default 400 responses.
2. `NursingResultsScreen._load()` left `_loading = true` on non-offline API errors, causing an infinite loading spinner and a `pumpAndSettle` timeout.

This ADR records the decisions made to prevent recurrence.

---

## Decision 1: Use constructor injection as the default DI pattern

### Choice
All services (`NursingApiService`, `NursingStorageService`, `NursingSessionLogger`) and the session controller (`NursingSessionController`) are accepted as optional constructor parameters by every screen and controller that needs them. Production code uses the default constructor when no dependency is supplied; tests inject fakes/mocks.

### Rationale
- **Explicit dependencies.** Constructor parameters make the dependency graph visible in the type signature [^1].
- **Zero new dependencies.** No DI framework (`provider`, `get_it`, `riverpod`) is added for v1. `ChangeNotifier` from `flutter:foundation` is sufficient for the controller.
- **Fast, deterministic tests.** A `MockClient` from `package:http/testing.dart` can be injected directly; no framework setup is required.
- **Migration path.** If the graph grows, we can later introduce `provider` at the composition root without changing screen constructors.

### Consequences
- Every navigation site must remember to propagate injected services. We mitigate this with the checklist in the completion plan.
- Optional parameters allow accidental fallback to real services in tests. Mitigated by adding a configurable `maxAttempts` seam and by writing tests that assert the expected mock client is used.

---

## Decision 2: Expose `maxAttempts` as a configurable constructor parameter

### Choice
`NursingApiService` accepts an optional `maxAttempts` parameter with a production default of `3`. Tests may pass `1` to disable retries.

### Rationale
- Widget tests that accidentally miss an endpoint fail fast instead of waiting through exponential backoff.
- The retry policy remains encapsulated in the service; tests do not need to mock internal timers.
- The default behavior in production is unchanged.

### Consequences
- Adds one more constructor parameter. This is acceptable because the service already accepts `baseUrl`, `timeout`, `client`, and `assetBundle`.
- Test authors must remember to use `maxAttempts: 1` when the screen under test is not fully mocked. Documented in the project skill.

---

## Decision 3: Retry with exponential backoff, capped delay, and jitter

### Choice
`NursingApiService._retry` retries up to `maxAttempts` on:
- `NursingApiException.isOffline == true` (timeout/socket).
- HTTP status code >= 500.

It does **not** retry 4xx errors. Delay is `min(baseDelay * 2^(attempt-1), maxDelay)` plus decorrelated jitter.

### Rationale
- Retrying transient network/server errors improves perceived reliability for users on poor mobile networks [^2][^3].
- A capped delay bounds worst-case latency.
- Jitter prevents synchronized retries from overwhelming a recovering backend [^3][^4].
- 4xx errors are client-side; retrying them wastes bandwidth and user time.

### Consequences
- Jitter makes retry timing non-deterministic, but the sequence of attempts and the final outcome remain deterministic for tests that use `maxAttempts: 1`.
- We do not yet respect `Retry-After` headers; deferred to a future ADR if rate-limiting becomes a concern.

---

## Decision 4: Loading/error state machines must be complete

### Choice
Every screen that shows a loading indicator must transition `_loading` to `false` in exactly one terminal branch: success, offline error, non-offline error, or generic exception.

### Rationale
- An incomplete state machine causes infinite loading spinners in production and `pumpAndSettle` timeouts in tests.
- Explicit terminal states make the UI trustworthy for adult learners who may not know how to force-quit an app.

### Consequences
- Requires careful review of every async `setState` block. Added as a code-review checklist item.

---

## Decision 5: Propagate injected services through every navigation hop

### Choice
When one nursing screen navigates to another nursing screen, it passes its injected services forward. Example: `NursingQuizScreen._submit()` passes `api` and `storage` to `NursingResultsScreen`.

### Rationale
- Prevents silent fallback to default (real) services deep in the navigation stack.
- Keeps the lifetime of `NursingStorageService` consistent across screens, which is important for in-flight session persistence and pending-analysis queues.

### Consequences
- Slightly more verbose navigation calls. Acceptable trade-off for correctness.
- Future refactor to a scoped DI framework would remove this boilerplate.

---

## References

[^1]: Flutter docs. *Communicating between layers — Dependency Injection*. https://docs.flutter.dev/app-architecture/case-study/dependency-injection  
[^2]: Stackademic. *Offline-First Architecture: Building Apps That Work When...* https://blog.stackademic.com/offline-first-architecture-5cb12314af75  
[^3]: StackPractices. *Retry with Exponential Backoff*. https://stackpractices.com/recipes/retry-backoff/  
[^4]: AWS Architecture Blog. *Exponential Backoff and Jitter*. https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/
