# Expert: Matej Rešetár (Reso Coder)

**GitHub:** https://github.com/resocoder  
**Key Projects:** Reso Coder platform, DDD/Clean Architecture tutorials  
**Authority:** DDD + TDD + Clean Architecture deep-dives for Flutter

## Why He Matters

Reso Coder's contribution: **making DDD accessible in Flutter.** His tutorials demonstrate that domain models should contain behavior, not just data.

## Key Patterns

### Rich Domain Models

```dart
// ANEMIC (WRONG)
class Question {
  final String id;
  final String text;
  final int correctIndex;
  // No behavior — just data bag
}

// RICH (CORRECT)
class Question {
  const Question({
    required this.id,
    required this.text,
    required this.options,
    required this.correctIndex,
  }) : assert(options.length >= 2, 'Question must have at least 2 options'),
       assert(correctIndex >= 0 && correctIndex < options.length,
              'correctIndex must be valid');

  final String id;
  final String text;
  final List<String> options;
  final int correctIndex;

  bool isCorrect(int selectedIndex) => selectedIndex == correctIndex;

  int calculateScore({bool usedHint = false}) {
    var score = 10;
    if (usedHint) score ~/= 2;
    return score;
  }

  Question copyWith({/*...*/}) => /*...*/;

  @override
  bool operator ==(Object other) => /*...*/;

  @override
  int get hashCode => /*...*/;
}
```

### TDD Workflow

```dart
// 1. Write failing test FIRST
test('calculateScore returns 5 when hint used', () {
  const question = Question(/*...*/);
  expect(question.calculateScore(usedHint: true), 5);
});

// 2. Implement minimal code to pass
int calculateScore({bool usedHint = false}) {
  var score = 10;
  if (usedHint) score ~/= 2;
  return score;
}

// 3. Refactor while tests pass
```

### Hexagonal Architecture

```
lib/
├── domain/           # Pure Dart. No Flutter. No external packages.
│   ├── entities/
│   ├── value_objects/
│   ├── repositories/  # Interfaces only
│   └── failures/
├── infrastructure/   # Implementations
│   ├── data_sources/
│   └── repositories/
└── application/      # BLoC / Riverpod / ViewModels
    └── blocs/
```

**Rule:** The `domain` directory compiles with only `dart:*` and `meta`.

## Failure Modes He Observed

1. **Anemic domain models:** All logic in controllers/services. Entities are data bags.
2. **Leaky infrastructure:** Database models leaking into UI.
3. **No failure types:** Using `Exception` everywhere instead of domain-specific failures.

## Citation

```
[^1]: Rešetár, M. "Flutter Clean Architecture / DDD."
      https://resocoder.com/category/tutorials/flutter/ddd-clean-architecture
[^2]: Rešetár, M. "Flutter TDD Clean Architecture Course."
      https://resocoder.com/category/tutorials/flutter/tdd-clean-architecture
```
