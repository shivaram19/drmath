# State Management — Decision Matrix

**Single Responsibility:** Choose the right state management for the problem.

## Problem

"Which state management should I use?" is the wrong question. The right question: "What is the lifetime and scope of this state?"

## Expert Framework

Rémi Rousselet's hierarchy [^1]:
1. **Ephemeral state** (checkbox, animation progress) → `StatefulWidget`
2. **App state shared by few widgets** → `ValueNotifier` + `ListenableBuilder`
3. **App state shared by many widgets** → Riverpod
4. **Complex async sequences with side effects** → BLoC

## Decision Matrix

| State Type | Lifetime | Scope | Solution | Code Complexity |
|-----------|----------|-------|----------|----------------|
| Checkbox toggle | Widget | Local | `StatefulWidget` | 3 lines |
| Form input | Screen | Local | `TextEditingController` | 5 lines |
| Tab index | Screen | Screen | `StatefulWidget` + `setState` | 5 lines |
| Quiz progress | Session | 2-3 screens | `ValueNotifier` | 10 lines |
| User profile | App | Global | Riverpod `AsyncNotifier` | 20 lines |
| Shopping cart | App | Global + persistence | Riverpod + Repository | 30 lines |
| Real-time chat | App | Global + WebSocket | BLoC | 50 lines |

## Dr. Math Current State

| Feature | State Type | Current | Correct |
|---------|-----------|---------|---------|
| Quiz scoring | Session | `StatefulWidget` | ✅ Correct |
| Curriculum progress | App | Static in `DemoData` | `ValueNotifier` or Riverpod |
| User profile | App | Static in `DemoData` | Riverpod `AsyncNotifier` |
| Theme toggle | App | Not implemented | Riverpod `StateNotifier` |

## Migration Trigger

Upgrade state management when **any** of these occur:
1. Same state accessed from 3+ different screens
2. Deep prop drilling (>2 levels of widget tree)
3. State needs to survive navigation (not tied to single route)
4. Complex loading/error/success async states
5. Need for caching, deduplication, or optimistic updates

## Anti-Patterns

| Anti-Pattern | Symptom | Fix |
|-------------|---------|-----|
| BLoC for checkbox | 50 lines of boilerplate for a boolean | `StatefulWidget` |
| Riverpod for ephemeral UI | `ref.watch` on every frame for animation | `AnimationController` |
| `setState` on ancestor | Rebuilds entire app for a button color change | Localize state or extract `ValueNotifier` |
| Global mutable variables | `static int currentScore = 0` | Proper state management |
| Nested Provider hell | 5+ `Provider` widgets deep in tree | Riverpod eliminates nesting |

## Expert Sources

[^1]: Rousselet, R. Riverpod Documentation — State Management. https://riverpod.dev/docs/concepts/reading  
[^2]: Angelov, F. "When to use BLoC." https://bloclibrary.dev/#/coreconcepts
