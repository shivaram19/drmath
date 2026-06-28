# Nursing Flutter Module — Round 3 Introspection, Self-Interview & Retrospect

**Date:** 2026-05-14  
**Scope:** Dig deeper into the mental/blended-space unknowns observed during Phase 7 widget testing, validate them against first-principles research, and revise the plan accordingly.  
**Research covenant:** No code change was made before the unknowns were named, researched, and documented.

---

## Part 1: Introspection — Unknowns I Was Still Hiding

### Unknown 1: Why does the quiz submit widget test time out even though `/api/nursing/analyze` is mocked?
The compaction claimed the timeout was caused by an unmocked analyze endpoint. After reading the actual test file, the endpoint **is** mocked. The real cause was deeper: the quiz screen constructs `NursingResultsScreen(attempts: attempts)` without propagating the injected `api`/`storage`, so the results screen instantiates a fresh `NursingApiService()` and hits the test harness's default 400 responses.

### Unknown 2: Does `NursingResultsScreen` ever leave `_loading = true` in production?
Yes. The non-offline error branch sets `_error` but never sets `_loading = false`. If the backend returns a non-retryable 4xx/5xx after retries, the user sees an infinite loading spinner instead of an error message. This is a production bug, not just a test flake.

### Unknown 3: Is constructor injection enough, or do we need a real DI framework?
The screens currently accept optional `api`, `storage`, `logger`, and `controller` parameters. This works for widget tests but creates a recurring risk: every navigation site must remember to propagate the injected dependencies. One missing propagation silently breaks testability and offline behavior.

### Unknown 4: Is exponential backoff without jitter safe?
The current `_retry` wrapper doubles the delay (300 ms → 600 ms → 1.2 s, capped at 5 s) but has no jitter. In a production incident where many clients retry simultaneously, this can create a thundering herd against a recovering server.

### Unknown 5: Is `pumpAndSettle` the right tool after every asynchronous action?
No. `pumpAndSettle` waits until no frames are scheduled. An indeterminate `CircularProgressIndicator` schedules frames forever, so any unhandled loading state causes a timeout. This is a test-authoring bug, not a framework bug.

### Unknown 6: What should the retry policy classify as retryable?
Currently we retry on `isOffline` or any HTTP 5xx. We do not retry 429 (rate limit) or respect `Retry-After`. We also do not distinguish between 500 (transient) and 501/505 (likely permanent). This is imprecise.

---

## Part 2: Self-Interview

**Q: Why did I initially blame the unmocked analyze endpoint when the test already mocks it?**
A: I trusted a compacted context summary without re-reading the source. The lesson is to verify the primary artifact before diagnosing. Compaction is a hint, not evidence.

**Q: Is adding `maxAttempts: 1` in tests the right fix, or does it mask design problems?**
A: It is a pragmatic seam for unit tests, but it does not replace mocking every endpoint the widget touches. A better fix is to propagate injected services so the results screen uses the same `MockClient`. The real design problem is that navigation silently drops dependencies.

**Q: Should `NursingApiService` expose `maxAttempts` as a constructor parameter?**
A: Yes. Making retry behavior configurable is a valid test seam. However, it must be paired with the discipline of always injecting the same service instance through every navigation hop.

**Q: Should we add random jitter to the retry backoff?**
A: Yes, but carefully. Jitter adds value only when many clients share the same retry schedule. For a single-user mobile app, the benefit is smaller, but the cost is also small. We should add decorrelated jitter and cap the delay to follow AWS/reliability best practices.

**Q: Should we switch from constructor injection to `provider` or `get_it`?**
A: Not for v1. The Flutter team recommends `provider` for DI, and `get_it` is popular, but both add a dependency or global registry. Constructor injection keeps the dependency graph explicit and requires no new packages. The immediate problem is missing propagation, not the injection mechanism.

**Q: What happens if a screen deep in the navigation stack needs a service but was not passed one?**
A: It falls back to the default constructor, which in tests means a real network call (or test-harness 400) and in production means the production backend. This is exactly the failure mode we saw. The fix is to audit every `Navigator.push` and pass the services.

**Q: Is `pumpAndSettle` ever appropriate after a network call?**
A: Only if the resulting UI has no infinite animations and no pending timers. After a screen transition, `pumpAndSettle` is fine. While a network request is in flight and a `CircularProgressIndicator` is spinning, `pumpAndSettle` will timeout. Prefer explicit `pump()` calls or mock the network so the loading state is brief.

**Q: What does the `_loading = false` omission teach us about state machines?**
A: Every loading state must have exactly one terminal transition to either success or error. The results screen has three terminal states (success, offline, error) but only two of them cleared `_loading`. This is a state-machine completeness bug.

---

## Part 3: Research Findings

### 3.1 `pumpAndSettle` and infinite animations
Flutter's own docs state that `pumpAndSettle` "waits for all animations to have completed" and "if there is an infinite animation in progress (for example, if there is an indeterminate progress indicator spinning), this method will throw" [^1]. The recommended practice is to use `tester.pump(Duration)` when fine-grained control is needed and to avoid relying on `pumpAndSettle` for network requests [^1][^2].

### 3.2 Constructor injection vs DI frameworks
First-principles engineering and Flutter architecture guidance agree: constructor parameters make dependencies explicit and testable without a framework [^3][^4]. The Flutter team's Compass app case study uses `provider` for composition at the app root, but the underlying pattern is still constructor injection into repositories and view models [^4]. The anti-pattern to avoid is the service locator: pulling dependencies from a global registry inside classes [^5]. For nursing v1, manual constructor injection is the right balance of simplicity and testability.

### 3.3 Retry with exponential backoff
Industry best practice for resilient clients includes:
- Bounded attempts (3–5) and a capped maximum delay (30–60 s) [^6][^7].
- Random jitter to prevent thundering herd [^6][^7].
- Fail-fast on client errors (4xx) and auth errors [^6][^8].
- Respect `Retry-After` when present [^8].
- Log every retry so systemic issues are visible [^8].

Our current implementation satisfies bounded attempts and delay cap but lacks jitter and `Retry-After` handling. For v1, adding jitter is low-cost and aligns with the reliability-first persona.

### 3.4 Offline-first UX
Offline-first design transforms network availability from a blocking requirement into an optimization [^9]. For read-only content like a question bank, bundling a JSON asset is a valid offline-fallback strategy [^9]. For write operations like analysis, an outbox pattern (queue attempts when offline and sync later) is the correct pattern [^9]. Our pending-analysis queue in `NursingStorageService` follows this.

---

## Part 4: Decisions and Plan Changes

### Decision 1: Fix the two root causes of the quiz submit timeout
1. **Propagate injected services:** `NursingQuizScreen._submit()` must pass `widget.api`, `widget.storage`, and a `NursingSessionLogger` to `NursingResultsScreen`.
2. **Clear `_loading` on every error path:** In `NursingResultsScreen._load()`, set `_loading = false` in the non-offline `NursingApiException` branch and in the generic `catch` branch.

### Decision 2: Add `maxAttempts` as a configurable constructor parameter on `NursingApiService`
Expose `maxAttempts` so tests can set it to `1`. Keep the production default at `3`. This is a deliberate test seam, not a hack.

### Decision 3: Add decorrelated jitter to the retry backoff
Update `_retry` to add randomized jitter within the capped delay. This reduces thundering-herd risk during backend recovery.

### Decision 4: Audit all navigation sites for dependency propagation
Add a checklist item to the completion plan: every `Navigator.push` / `pushReplacement` / `pushAndRemoveUntil` that creates a nursing screen must propagate `api`, `storage`, `logger`, or `controller` as appropriate.

### Decision 5: Keep constructor injection; defer DI framework
No `provider`, `get_it`, or `riverpod` for v1. The cost of adding a dependency outweighs the benefit when the real problem is missing propagation, not the injection mechanism.

### Decision 6: Document the `pumpAndSettle` lesson in the project skill
Widget tests must either mock every endpoint the screen calls or inject a service with `maxAttempts: 1`. Tests that rely on `pumpAndSettle` while a network call is in flight are fragile.

---

## Part 5: Updated Immediate Tasks

1. Fix `_loading = false` in `NursingResultsScreen._load()` for non-offline errors.
2. Pass `widget.api`/`widget.storage` from `NursingQuizScreen` to `NursingResultsScreen`.
3. Add `maxAttempts` constructor parameter to `NursingApiService`.
4. Add jitter to retry backoff.
5. Re-run `flutter test test/features/nursing` and `flutter build apk --debug`.
6. Commit with a conventional message citing the research.

---

## References

[^1]: Flutter API docs. `WidgetTester.pumpAndSettle`. https://api.flutter.dev/flutter/flutter_test/WidgetTester/pumpAndSettle.html  
[^2]: DCM blog. *Navigating the Hard Parts of Testing in Flutter*. https://dcm.dev/blog/2025/07/30/navigating-hard-parts-testing-flutter-developers/  
[^3]: SoftInstigate. *Dependency Injection vs Constructor Parameters*. https://softinstigate.com/en/blog/posts/dep-injection/  
[^4]: Flutter docs. *Communicating between layers — Dependency Injection*. https://docs.flutter.dev/app-architecture/case-study/dependency-injection  
[^5]: Carrion.dev. *Dependency Injection + Dependency Inversion: More Robust and Testable Code*. https://carrion.dev/en/posts/dependency-injection-benefits/  
[^6]: GetStream blog. *The Architecture and Best Practices for Mobile App Stability*. https://getstream.io/blog/mobile-app-stability/  
[^7]: StackPractices. *Retry with Exponential Backoff*. https://stackpractices.com/recipes/retry-backoff/  
[^8]: Totoro Jam. *Pattern: Retry with Exponential Backoff*. https://totoro-jam.github.io/battle-tested-patterns/patterns/retry-backoff/  
[^9]: Stackademic. *Offline-First Architecture: Building Apps That Work When...* https://blog.stackademic.com/offline-first-architecture-5cb12314af75
