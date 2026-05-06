# Flutter Expert Directory

Canonical sources for every architectural, performance, and design decision. Cite before committing.

## Core Framework & State Management

### Rémi Rousselet (`rrousselGit`)
- **GitHub:** https://github.com/rrousselGit
- **Creations:** Provider → Riverpod, flutter_hooks
- **Authority:** #1 StackOverflow Flutter answerer; state management paradigm shifter
- **Key Insight:** Provider's lack of compile-time safety led to Riverpod. Code-generated providers eliminate runtime `ProviderNotFoundException`.
- **When to cite:** State management decisions, dependency injection, hooks patterns
- **Failure observed:** Teams nesting 5+ Provider widgets, losing track of rebuild scope. Riverpod's `ref.watch` + `select` solves this at compile time.

### Felix Angelov (`felangel`)
- **GitHub:** https://github.com/felangel
- **Creations:** flutter_bloc, bloc, mason, very_good_cli, very_good_workflows
- **Authority:** Standardized BLoC for Flutter; enterprise-scale architecture tooling
- **Key Insight:** BLoC enforces unidirectional data flow via `Event → State` transitions. Cubit removes events for simpler cases.
- **When to cite:** Event-driven architecture, testing strategy (bloc_test), CLI scaffolding
- **Failure observed:** Developers using BLoC for trivial UI state (checkbox toggles). Cubit or `ValueNotifier` is sufficient.

### Brian Egan (`brianegan`)
- **GitHub:** https://github.com/brianegan
- **Creations:** flutter_architecture_samples, RxDart, flutter_redux
- **Authority:** Cross-framework architecture comparison; real-world production scaling
- **Key Insight:** "Architecture should solve problems you have, not problems you imagine." Start simple, extract layers when pain emerges.
- **When to cite:** Architecture selection, when to migrate from simple to complex patterns
- **Failure observed:** Startups choosing Clean Architecture day 1 for 5-screen MVPs. 6-month rewrite cycles ensue.

## Architecture & Design Patterns

### Andrea Bizzotto (`bizz84`)
- **GitHub:** https://github.com/bizz84
- **Creations:** CodingWithAndrea.com, Flutter Complete Reference
- **Authority:** Clean Architecture educator; Riverpod v2 adoption patterns
- **Key Insight:** Repository pattern isolates data sources. ViewModel (or AsyncNotifier) isolates UI state. Widgets remain "dumb."
- **When to cite:** Repository pattern, AsyncNotifier patterns, testing with Riverpod
- **Failure observed:** Mixing Firebase calls directly in `onPressed` handlers. No offline capability, no testability.

### Matej Rešetár / Reso Coder (`resocoder`)
- **GitHub:** https://github.com/resocoder
- **Creations:** Reso Coder education platform, Clean Architecture tutorials
- **Authority:** DDD + TDD + Clean Architecture deep-dives for Flutter
- **Key Insight:** Domain layer must be pure Dart (no Flutter, no dart:io). Use cases encapsulate business rules. Entities enforce invariants.
- **When to cite:** DDD in Flutter, TDD workflow, hexagonal architecture
- **Failure observed:** Anemic domain models (data classes with no behavior). Business logic scattered across controllers.

## Performance & Rendering

### Filip Hráček (`filiph`)
- **GitHub:** https://github.com/filiph
- **Authority:** Former Google Flutter/Dart team; Flutter Performance Book
- **Key Insight:** Most Flutter performance issues are rebuild scope issues, not rendering issues. `const`, `RepaintBoundary`, and `ListView.builder` solve 80% of jank.
- **When to cite:** Performance debugging, rendering pipeline, Impeller migration
- **Failure observed:** Developers profiling GPU when actual issue is `setState` rebuilding 500 list items. Use Widget rebuild profiler first.

### Pascal Welsch (`passsy`)
- **GitHub:** https://github.com/passsy
- **Creations:** Wiredash, flutter isolates advocacy
- **Authority:** Enterprise Flutter, isolate computation patterns
- **Key Insight:** Heavy computation (JSON parsing, image processing) must run in isolates. Main thread must remain < 16ms/frame.
- **When to cite:** Isolate usage, compute-heavy operations, enterprise architecture
- **Failure observed:** Parsing 5MB JSON on main thread → 300ms jank. Use `compute()` or `Isolate.run()`.

## Ecosystem & Tooling

### Robert Felker (`Solido`)
- **GitHub:** https://github.com/Solido
- **Creations:** awesome-flutter (55k+ stars)
- **Authority:** Ecosystem cartographer; package discovery
- **Key Insight:** Package selection should prioritize maintenance velocity, issue response time, and test coverage over star count.
- **When to cite:** Package selection, ecosystem evaluation
- **Failure observed:** Using abandoned packages (last commit 2+ years ago). Security and compatibility rot.

### Majid Hajian (`mhadaily`)
- **GitHub:** https://github.com/mhadaily
- **Creations:** Flutter Engineering book, Flutter Vikings
- **Authority:** Microsoft-scale Flutter, architecture at enterprise level
- **Key Insight:** Monorepo with Melos enables package isolation without repository overhead. CI enforces dependency direction.
- **When to cite:** Monorepo setup, multi-package architecture, CI/CD for Flutter

## Accessibility & Design

### Pooja Bhaumik (`poojab26`)
- **GitHub:** https://github.com/poojab26
- **Authority:** Designer-developer bridge; accessibility advocate
- **Key Insight:** Accessibility is not a feature — it's a constraint. Design for screen readers first, visual polish second.
- **When to cite:** Accessibility implementation, design-system integration

## Citation Format

When referencing an expert in code or ADRs:

```
Decision to use Riverpod over Provider [^1].

[^1]: Rousselet, R. (2021). "Riverpod: A Reactive Caching and Data-binding Framework." 
      GitHub: rrousselGit/riverpod. Derived from observed Provider failure modes 
      in production applications (compile-time safety gaps, nested provider hell).
```
