# Testing Strategy — Pyramid for Flutter

**Single Responsibility:** Define what to test and at what level.

## Problem

"We don't have time to test" = "We don't have time to do it right the first time." Teams that skip testing spend 3x longer debugging production issues.

## Flutter Test Pyramid

```
       /\
      /  \     E2E / Integration — 5-10%
     /----\     (Full user journey, slow, device required)
    /      \
   / Widget \   Widget Tests — 20-30%
  /----------\  (Screen rendering, interactions, headless)
 /   Unit     \ Unit Tests — 60-70%
/______________\ (Pure logic, instant, no Flutter needed)
```

## Layer Testing Matrix

| Layer | Test Type | File Location | Speed |
|-------|----------|---------------|-------|
| Domain models | Unit | `test/models/*_test.dart` | <10ms |
| Repository | Unit (mocked) | `test/data/*_test.dart` | <50ms |
| ViewModel / Notifier | Unit | `test/features/*_test.dart` | <50ms |
| Screen rendering | Widget | `test/features/*_screen_test.dart` | <500ms |
| Navigation flow | Widget | `test/navigation/*_test.dart` | <1s |
| Full user journey | Integration | `integration_test/*_test.dart` | 10-60s |

## Coverage Targets

| Metric | Target | Enforcement |
|--------|--------|-------------|
| Domain layer | 100% | CI gate |
| Repository layer | 90% | CI gate |
| UI layer | 70% | CI warning |
| E2E critical paths | 100% | Manual QA + mobilerun |

## Run Commands

```bash
# Full suite
flutter test

# With coverage report
cd mathwise_build && flutter test --coverage
genhtml coverage/lcov.info -o coverage/html

# Specific test
cd mathwise_build && flutter test test/models/question_test.dart

# Integration tests (requires device/emulator)
cd mathwise_build && flutter test integration_test/

# Watch mode (during development)
cd mathwise_build && flutter test --watch
```

## Anti-Patterns

| Anti-Pattern | Symptom | Fix |
|-------------|---------|-----|
| Only widget tests | Slow suite, missed edge cases | Unit test domain logic |
| Testing Flutter framework | `test('Column renders children')` | Test YOUR code, not Flutter's |
| No golden tests | UI regressions slip through | Add golden file tests for critical screens |
| Mocking value objects | `MockQuestion()` instead of real `Question` | Use real immutable objects |
| Testing private methods | Brittle, implementation-detail tests | Test public behavior |

## Expert Sources

Angelov, F. "Testing with bloc_test." https://bloclibrary.dev/#/testing  
Flutter Team. "Testing Flutter apps." https://docs.flutter.dev/testing/overview
