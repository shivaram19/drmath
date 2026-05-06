# BLoC — Business Logic Component

**Single Responsibility:** Event-driven state management for complex async flows.

## Problem

When async operations have complex sequencing (load → validate → submit → handle error → retry), `setState` and even Riverpod become spaghetti. BLoC enforces unidirectional data flow: `Event → Bloc → State`.

## When to Use BLoC

Use BLoC when state transitions have **business rules**:
- Load user → if premium, load extra content → if error, show retry
- Form: validate field A → if valid, enable field B → submit → handle 409 conflict
- Real-time: WebSocket message → merge with local state → deduplicate → emit

**Do NOT use BLoC for:**
- Simple boolean toggles
- Static content display
- Single API call with loading/success/error (Riverpod `AsyncNotifier` is sufficient)

## Cubit vs BLoC

| | Cubit | BLoC |
|--|-------|------|
| Input | Methods (`emit`) | Events (`add`) |
| Use case | Simple state changes | Complex event handling, logging, analytics |
| Boilerplate | Low | Medium |

```dart
// Cubit: Simple quiz scoring
class QuizCubit extends Cubit<QuizState> {
  QuizCubit() : super(const QuizState());

  void answerQuestion(int selectedIndex) {
    final current = state;
    final isCorrect = selectedIndex == current.currentQuestion.correctIndex;
    emit(current.copyWith(
      score: isCorrect ? current.score + 1 : current.score,
      currentIndex: current.currentIndex + 1,
    ));
  }
}

// BLoC: Complex quiz with lifelines, hints, time limits
class QuizBloc extends Bloc<QuizEvent, QuizState> {
  QuizBloc() : super(const QuizState()) {
    on<QuestionAnswered>(_onQuestionAnswered);
    on<HintRequested>(_onHintRequested);
    on<TimeExpired>(_onTimeExpired);
  }

  void _onQuestionAnswered(QuestionAnswered event, Emitter<QuizState> emit) {
    // Complex business logic with multiple state transitions
  }
}
```

## Testing with bloc_test

```dart
blocTest<QuizCubit, QuizState>(
  'emits updated score when answer is correct',
  build: QuizCubit.new,
  act: (cubit) => cubit.answerQuestion(1), // correctIndex
  expect: () => [isA<QuizState>().having((s) => s.score, 'score', 1)],
);
```

## Anti-Patterns

| Anti-Pattern | Why It Fails |
|-------------|-------------|
| BLoC for a counter | 10x boilerplate for 3 lines of logic |
| Calling `emit` after `await` without `closed` check | Runtime error if bloc disposed |
| Business logic in `mapEventToState` (legacy) | Use `on<Event>` API |
| Not using `equatable` | Duplicate state emissions, unnecessary rebuilds |

## Expert Sources

Angelov, F. BLoC Library Documentation. https://bloclibrary.dev  
Angelov, F. very_good_cli — BLoC scaffolding. https://cli.vgv.dev
