# Expert: Brian Egan

**GitHub:** https://github.com/brianegan  
**Key Projects:** flutter_architecture_samples, RxDart, flutter_redux  
**Authority:** Cross-framework architecture comparison; real-world production scaling

## Why He Matters

Egan's core insight: **"Architecture should solve problems you have, not problems you imagine."** His architecture samples compare MVC, MVVM, BLoC, Redux, and Scoped Model — demonstrating that each solves different problems at different scales.

## Key Patterns

### Start Simple, Extract When Painful

```dart
// Phase 1: Startup (3-5 screens)
// StatefulWidget is CORRECT. Don't add BLoC.

// Phase 2: Growth (10-15 screens)
// Extract repository pattern when data logic duplicates.

// Phase 3: Scale (20+ screens, multi-developer)
// Add Riverpod/BLoC when prop drilling becomes painful.
```

### Repository Pattern

```dart
// Abstract interface in domain
abstract class QuestionRepository {
  Future<List<Question>> getQuestions(String topicId);
}

// Multiple implementations, swappable at composition root
class DemoQuestionRepository implements QuestionRepository { /*...*/ }
class ApiQuestionRepository implements QuestionRepository { /*...*/ }
```

## Failure Modes He Observed

1. **Premature architecture:** Startups choosing Clean Architecture + BLoC for 5-screen MVPs. Result: 6-month rewrite cycles when requirements changed.
2. **Architecture as religion:** Teams debating BLoC vs Riverpod for weeks instead of shipping. The difference matters at scale; not at 5 screens.
3. **Missing composition root:** Dependencies instantiated deep in widget tree. No single place to swap implementations.

## Decision Heuristic

```
Screens < 10    → StatefulWidget + Repository
Screens 10-20   → Riverpod for shared state
Screens 20+     → BLoC for complex flows + Riverpod for simple state
Developers > 3  → Enforce architecture tests (custom_lint)
```

## Citation

```
[^1]: Egan, B. Flutter Architecture Samples. GitHub: brianegan/flutter_architecture_samples.
      Demonstrates 7+ architecture patterns on identical feature set, 
      enabling evidence-based selection rather than trend-based.
```
