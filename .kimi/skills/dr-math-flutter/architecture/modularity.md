# Modularity — Feature Modules & Package Boundaries

**Single Responsibility:** Decide when and how to split a monolith into packages.

## Problem

A single `lib/` directory works for 10 screens. At 30+ screens, build times increase, merge conflicts multiply, and CI slows. Package splitting enforces compile-time boundaries.

## Current: Monolith

```
mathwise_build/
├── lib/
│   ├── shared/
│   └── features/
├── test/
└── pubspec.yaml
```

**Valid for:** <20 screens, <5 developers, single product.

## Growth: Internal Packages

```
mathwise/
├── packages/
│   ├── mathwise_core/          # Domain models, pure Dart
│   │   ├── lib/
│   │   │   ├── src/models/
│   │   │   └── mathwise_core.dart
│   │   └── pubspec.yaml
│   ├── mathwise_data/          # Repositories, data sources
│   │   ├── lib/
│   │   │   └── mathwise_data.dart
│   │   └── pubspec.yaml        # Depends on mathwise_core
│   ├── mathwise_ui/            # Theme, shared widgets
│   │   ├── lib/
│   │   │   └── mathwise_ui.dart
│   │   └── pubspec.yaml        # Depends on mathwise_core
│   └── mathwise_features/      # Feature screens
│       ├── lib/
│       │   ├── home/
│       │   ├── curriculum/
│       │   └── practice/
│       └── pubspec.yaml        # Depends on mathwise_core, mathwise_ui, mathwise_data
├── apps/
│   └── mathwise_mobile/        # Thin app shell
│       ├── lib/main.dart
│       └── pubspec.yaml        # Depends on all packages
└── melos.yaml                  # Monorepo orchestration
```

## Dependency Direction

```
mathwise_features → mathwise_ui → mathwise_core
                  → mathwise_data → mathwise_core
```

**Forbidden:** `mathwise_data` importing `mathwise_features`. Features do not depend on each other.

## Tooling: Melos

```yaml
# melos.yaml
name: mathwise
packages:
  - packages/*
  - apps/*

scripts:
  analyze:
    exec: flutter analyze
  test:
    exec: flutter test
  build:
    exec: flutter build apk --release
```

```bash
dart pub global activate melos
melos bootstrap  # Links all packages
melos run analyze
melos run test
```

## Evolution Triggers

| Trigger | Action |
|---------|--------|
| >20 screens | Extract `mathwise_core` + `mathwise_ui` |
| >30 screens | Extract `mathwise_data` + feature packages |
| >5 developers | Enforce package boundaries with CI |
| Multiple products | Extract shared packages, thin app shells |

## Anti-Patterns

| Anti-Pattern | Fix |
|-------------|-----|
| Packages depending on each other | DAG only — no cycles |
| Shared everything package | `mathwise_common` becomes a dumping ground |
| Premature splitting | <15 screens = monolith is fine |
| No automated boundary enforcement | Add CI check for illegal imports |

## Expert Sources

Hajian, M. "Flutter Engineering — Monorepo." https://majidhajian.com  
Very Good Ventures. "Very Good CLI — Monorepo." https://cli.vgv.dev
