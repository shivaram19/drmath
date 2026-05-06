# Architecture Skill — Layer Contracts

**Single Responsibility:** Define how code is organized into layers and how layers communicate.

## Problem

Flutter's freedom is its curse. Without enforced boundaries, `lib/` becomes a flat dumping ground: UI, business logic, API calls, and data models interleaved. The result: untestable code, circular dependencies, and 2000-line files.

## Expert Solution

Brian Egan's architecture samples demonstrate that **architecture emerges from pain, not prediction** [^1]. Reso Coder's DDD tutorials enforce that **domain is pure Dart** — no Flutter imports [^2].

## Current Architecture: Feature-First with Layer Separation

```
lib/
├── main.dart
├── app.dart                    # MaterialApp, routing, theme injection
├── shared/
│   ├── models/                 # Pure Dart. No flutter/material.dart.
│   ├── data/                   # Repository implementations (static for now)
│   ├── widgets/                # Cross-cutting UI components
│   └── theme/                  # ThemeData, extensions, tokens
└── features/
    └── [feature_name]/
        ├── screens/            # Stateful/Stateless widgets
        └── widgets/            # Private to this feature
```

## Layer Contract Rules

| Layer | May Import | Must NOT Import |
|-------|-----------|-----------------|
| `shared/models` | `dart:*` only | `package:flutter/*`, other layers |
| `shared/data` | `shared/models`, `dart:*` | `features/*`, Flutter widgets |
| `shared/widgets` | `shared/models`, `shared/theme`, Flutter | `features/*` |
| `features/X/screens` | `shared/*`, Flutter | `features/Y/*` (no cross-feature) |
| `features/X/widgets` | `shared/*`, `features/X/*`, Flutter | `features/Y/*` |

## Dependency Direction

```
features/X/screens ──→ shared/widgets
        │                    │
        └──────→ shared/data ──→ shared/models
```

**The domain arrow always points inward.** Models know nothing. Data knows models. Screens know data and widgets.

## Cross-Feature Communication

**Forbidden:** `features/curriculum/screens/curriculum_list_screen.dart` importing `features/practice/screens/practice_question_screen.dart`.

**Allowed:** Navigation via named routes with type-safe arguments:

```dart
// shared/navigation/routes.dart
class AppRoutes {
  static const home = '/';
  static const curriculum = '/curriculum';
  static const practice = '/practice';
  static const practiceArgs = 'topicId';
}

// In CurriculumScreen:
Navigator.pushNamed(context, AppRoutes.practice, arguments: topic.id);

// In PracticeScreen:
final topicId = ModalRoute.of(context)!.settings.arguments as String;
```

## Evolution Triggers

| Trigger | Current → Target | Skill |
|---------|-----------------|-------|
| >15 screens | Feature-First → Clean Architecture | `layers.md` |
| Complex async state | StatefulWidget → Riverpod | `../state-management/riverpod.md` |
| Multi-developer team | Monolith → Melos monorepo | `modularity.md` |
| Real backend | Static repos → Repository pattern + DI | `dependency-inversion.md` |

## Anti-Patterns

| Pattern | Why It Fails | Expert Source |
|---------|-------------|---------------|
| All screens in `lib/screens/` | No separation, untestable | Brian Egan [^1] |
| Business logic in `build()` | Rebuild triggers logic re-execution | Reso Coder [^2] |
| Direct `http.get` in `onPressed` | No offline, no testability, no retry | Andrea Bizzotto |
| Feature A imports Feature B | Circular dependencies, tight coupling | Felix Angelov |
| Anemic models (`class User { String name; }`) | Business logic leaks into controllers | Reso Coder [^2] |

## Agentic Invocation

When scaffolding a new feature:

```
You are generating a Flutter feature for Dr. Math.
Architecture constraints:
- Feature goes in lib/features/{feature_name}/
- Domain models go in lib/shared/models/ (pure Dart, no Flutter imports)
- Data repository goes in lib/shared/data/ (implements abstract interface)
- Screens go in lib/features/{feature_name}/screens/
- No cross-feature imports. Use named routes for navigation.
- All interactive elements >= 48dp touch target.
- Use Theme.of(context) for all colors, sizes, typography.
```

[^1]: Egan, B. Flutter Architecture Samples. https://github.com/brianegan/flutter_architecture_samples
[^2]: Rešetár, M. (Reso Coder). Clean Architecture / DDD in Flutter. https://resocoder.com/category/tutorials/flutter/ddd-clean-architecture
