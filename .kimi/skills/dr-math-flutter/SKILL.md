# Dr. Math Flutter — Master Skill Index

**Scope:** `mathwise_build/` and all future Flutter modules.  
**Method:** Research-First Covenant (BFS → DFS → ADR → Code).  
**Principle:** No skill file exceeds one responsibility. Cross-cutting concerns reference, do not duplicate.

## Skill Map

```
dr-math-flutter/
├── SKILL.md                          ← You are here
├── architecture/
│   ├── SKILL.md                      # Layer contracts, dependency rules
│   ├── layers.md                     # UI / Domain / Data separation
│   ├── dependency-inversion.md       # DI: get_it, injectable, Riverpod
│   └── modularity.md                 # Feature modules, package boundaries
├── state-management/
│   ├── SKILL.md                      # Decision matrix: when to use what
│   ├── setstate-patterns.md          # StatefulWidget done right
│   ├── riverpod.md                   # AsyncNotifier, code-generation, testing
│   └── bloc.md                       # Event-driven, Cubit simplification
├── design-system/
│   ├── SKILL.md                      # Token architecture
│   ├── theming.md                    # ColorScheme, ThemeExtension, M3
│   ├── accessibility.md              # WCAG 2.1 AA, screen readers, touch targets
│   └── animation.md                  # Pedagogical motion, implicit/explicit
├── testing/
│   ├── SKILL.md                      # Pyramid, coverage strategy
│   ├── unit-testing.md               # Pure Dart, mocktail
│   ├── widget-testing.md             # Finder patterns, pump semantics
│   ├── integration-testing.md        # integration_test, mobilerun
│   └── golden-testing.md             # matchesGoldenFile, tolerance
├── performance/
│   ├── SKILL.md                      # Profiling strategy
│   ├── build-size.md                 # APK/AAB shrink, treeshaking
│   ├── runtime-jank.md               # Rebuild scope, const, RepaintBoundary
│   └── startup-time.md               # TTI, shader warmup, deferred loading
├── tooling/
│   ├── SKILL.md                      # CLI reference, DevTools
│   ├── static-analysis.md            # analysis_options.yaml, custom_lint
│   └── ci-cd.md                      # GitHub Actions, artifact gates
├── agentic/
│   ├── SKILL.md                      # AI-assisted Flutter workflow
│   ├── code-generation.md            # Fine-tuning, prompt engineering
│   ├── rules.md                      # .kimi/rules for project context
│   └── mcp-integration.md            # Dart/Flutter MCP server usage
└── experts/
    ├── index.md                      # Canonical expert directory
    ├── remi-rousselet.md             # Riverpod, Provider, Hooks
    ├── brian-egan.md                 # Architecture Samples, RxDart
    ├── felix-angelov.md              # BLoC, testing, very_good_cli
    ├── andrea-bizzotto.md            # Clean Architecture, Riverpod v2
    ├── reso-coder.md                 # DDD, TDD, Clean Architecture in Flutter
    └── filip-hracek.md               # Performance, Impeller, rendering pipeline
```

## Invocation Rules

1. **Before any Flutter code change:** Read the relevant sub-skill(s).
2. **Architecture change:** Must read `architecture/SKILL.md` + write/update ADR.
3. **New dependency:** Must read `architecture/dependency-inversion.md` + run TCO check.
4. **State management change:** Must read `state-management/SKILL.md` decision matrix.
5. **UI change:** Must read `design-system/SKILL.md` + `design-system/accessibility.md`.
6. **Test addition:** Must read `testing/SKILL.md` + relevant test-type skill.

## Expert Chain of Custody

Every skill cites primary sources. Expert GitHub profiles are canonical:
- rrousselGit (Riverpod)
- brianegan (Architecture)
- felangel (BLoC)
- bizz84 (Clean Architecture)
- resocoder (DDD/TDD)
- filiph (Performance)
- passsy (Isolates, enterprise)
- Solido (Awesome Flutter — ecosystem map)

## Failure Taxonomy

Each skill documents expert-observed failure modes. Do not repeat these:
- **Over-engineering:** Using BLoC for 3-screen apps (Brian Egan)
- **Provider hell:** Nesting 5+ Providers (Remi Rousselet — why he built Riverpod)
- **Business logic in widgets:** Untestable, tightly coupled (Reso Coder)
- **setState everywhere:** Rebuild storms, jank (Filip Hracek)
- **Ignoring const:** Unnecessary rebuilds across entire tree (Flutter Team)
- **Hardcoded values:** No theming, no localization (Andrea Bizzotto)

## Quick Reference

| Task | Skill |
|------|-------|
| Add a new screen | `architecture/layers.md` + `design-system/theming.md` |
| Add state management | `state-management/SKILL.md` decision matrix |
| Add a test | `testing/SKILL.md` pyramid position → specific test skill |
| Optimize build size | `performance/build-size.md` |
| Fix analysis warnings | `tooling/static-analysis.md` |
| Use AI to generate code | `agentic/SKILL.md` + `agentic/rules.md` |
| Debug performance | `performance/SKILL.md` + `experts/filip-hracek.md` |
