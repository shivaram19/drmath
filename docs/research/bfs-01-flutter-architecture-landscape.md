# BFS-01: Flutter Architecture Landscape Mapping

**Date:** 2026-05-06  
**Scope:** State management, architecture patterns, design systems for Flutter mobile apps  
**Research Phase:** BFS (Breadth-First Landscape Mapping)  
**Driver:** Agentic Flutter code generation requires canonical architecture patterns

---

## 1. Decomposition

Flutter architecture decomposes into:
1. State management (how data flows)
2. Layer separation (where code lives)
3. Dependency injection (how components connect)
4. Navigation (how screens transition)
5. Design system (how UI is themed)
6. Testing (how correctness is verified)
7. Performance (how speed is maintained)
8. Build pipeline (how code ships)

## 2. Landscape Scan

### State Management Solutions

| Solution | Creator | Maturity | Complexity | Use Case |
|----------|---------|----------|------------|----------|
| StatefulWidget | Flutter Team | Stable | Low | Local UI state |
| ValueNotifier | Flutter Team | Stable | Low | Simple shared state |
| Provider | Rousselet | Stable | Medium | InheritedWidget wrapper |
| Riverpod | Rousselet | Stable | Medium | Compile-safe Provider successor |
| BLoC / Cubit | Angelov | Stable | Medium-High | Complex event-driven state |
| Redux | Egan / Community | Stable | High | Predictable state container |
| MobX | Community | Stable | Medium | Reactive programming |
| GetX | Community | Controversial | Low | All-in-one (avoid) |

**Key Finding:** Rousselet's Riverpod emerged from Provider's runtime failure modes [^1]. Angelov's BLoC standardizes event-driven patterns for enterprise [^2]. Egan's Redux samples demonstrate that Redux is overkill for most Flutter apps [^3].

### Architecture Patterns

| Pattern | Source | Complexity | When to Use |
|---------|--------|------------|-------------|
| MVC | Generic | Low | Not recommended for Flutter |
| MVVM | Microsoft/Xamarin | Medium | ViewModel pattern |
| Clean Architecture | Uncle Bob | High | >20 screens, multi-dev |
| DDD | Eric Evans | High | Complex domain logic |
| Hexagonal | Cockburn | Medium | Test-driven, ports/adapters |
| Feature-First | Community | Low-Medium | Team scalability |

**Key Finding:** Reso Coder demonstrates DDD in Flutter with rich domain models [^4]. Andrea Bizzotto advocates Repository + Riverpod as the pragmatic middle ground [^5]. Brian Egan's samples prove that architecture should emerge from pain, not be imposed day one [^3].

### Design Systems

| System | Source | Status |
|--------|--------|--------|
| Material 3 | Google | Stable, default |
| Cupertino | Apple/Flutter | Stable, iOS-only |
| Fluent UI | Microsoft | Community |
| Custom Token-Based | Team-defined | Required for brand identity |

**Key Finding:** Material 3's `ColorScheme.fromSeed` + `ThemeExtension` provides sufficient customization without abandoning the design system [^6].

## 3. Expert Mapping

| Expert | Primary Contribution | GitHub | Skill File |
|--------|---------------------|--------|------------|
| Rémi Rousselet | Riverpod, Provider, flutter_hooks | rrousselGit | `experts/remi-rousselet.md` |
| Felix Angelov | BLoC, Cubit, very_good_cli | felangel | `experts/felix-angelov.md` |
| Brian Egan | Architecture Samples, RxDart | brianegan | `experts/brian-egan.md` |
| Andrea Bizzotto | Clean Architecture, Riverpod v2 | bizz84 | `experts/andrea-bizzotto.md` |
| Matej Rešetár | DDD, TDD, Clean Architecture | resocoder | `experts/reso-coder.md` |
| Filip Hráček | Performance, Impeller, rendering | filiph | `experts/filip-hracek.md` |
| Pascal Welsch | Isolates, enterprise Flutter | passsy | (referenced) |
| Robert Felker | Awesome Flutter ecosystem | Solido | (referenced) |

## 4. Failure Mode Inventory

| Failure | Expert Observation | Skill Prevention |
|---------|-------------------|------------------|
| Provider nesting hell | Rousselet [^1] | Riverpod eliminates nesting |
| BLoC for simple state | Angelov [^2] | Decision matrix in `state-management/SKILL.md` |
| Premature Clean Architecture | Egan [^3] | Evolution triggers in `architecture/SKILL.md` |
| Anemic domain models | Rešetár [^4] | Rich model pattern in `architecture/layers.md` |
| Firebase in widgets | Bizzotto [^5] | Repository pattern mandate |
| GPU profiling first | Hráček [^7] | Widget rebuild profiler first |
| `setState` rebuild storms | Hráček [^7] | `const`, `ListView.builder` |
| Hardcoded values | Bizzotto [^5] | ThemeExtension + custom lint |

## 5. References

[^1]: Rousselet, R. Riverpod. https://github.com/rrousselGit/riverpod  
[^2]: Angelov, F. BLoC Library. https://bloclibrary.dev  
[^3]: Egan, B. Flutter Architecture Samples. https://github.com/brianegan/flutter_architecture_samples  
[^4]: Rešetár, M. Reso Coder DDD. https://resocoder.com  
[^5]: Bizzotto, A. Clean Architecture. https://codewithandrea.com  
[^6]: Material Design 3. https://m3.material.io  
[^7]: Hráček, F. Flutter Performance. https://flutterperformance.com
