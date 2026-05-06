# Expert: Felix Angelov

**GitHub:** https://github.com/felangel  
**Key Projects:** flutter_bloc, bloc, mason, very_good_cli, very_good_workflows  
**Authority:** Standardized BLoC for Flutter; enterprise CLI tooling

## Why He Matters

Angelov transformed BLoC from a pattern into a **framework** with strict contracts:
- `Event` → `Bloc` → `State` — unidirectional, immutable, testable
- `bloc_test` — deterministic state machine testing
- `mason` — code generation templates
- `very_good_cli` — production-ready project scaffolding

## Key Patterns

### Cubit for Simple State

```dart
class QuizCubit extends Cubit<QuizState> {
  QuizCubit() : super(const QuizState());

  void answerQuestion(int selected) {
    final isCorrect = selected == state.currentQuestion.correctIndex;
    emit(state.copyWith(
      score: isCorrect ? state.score + 1 : state.score,
      currentIndex: state.currentIndex + 1,
    ));
  }
}
```

### BLoC for Complex Flows

```dart
class QuizBloc extends Bloc<QuizEvent, QuizState> {
  QuizBloc() : super(const QuizState()) {
    on<QuestionAnswered>(_onAnswered);
    on<HintRequested>(_onHintRequested);
    on<LifelineUsed>(_onLifelineUsed);
    on<TimeExpired>(_onTimeExpired);
  }

  Future<void> _onAnswered(QuestionAnswered event, Emitter<QuizState> emit) async {
    emit(state.copyWith(status: QuizStatus.validating));
    await Future.delayed(const Duration(milliseconds: 500)); // UX delay
    // ... validation logic
    emit(state.copyWith(status: QuizStatus.answered));
  }
}
```

### Testing with bloc_test

```dart
blocTest<QuizCubit, QuizState>(
  'awards point for correct answer',
  build: QuizCubit.new,
  seed: () => QuizState(
    currentQuestion: const Question(id: '1', text: '2+2=?', options: ['3','4'], correctIndex: 1),
  ),
  act: (cubit) => cubit.answerQuestion(1),
  expect: () => [
    isA<QuizState>().having((s) => s.score, 'score', 1),
  ],
);
```

## Failure Modes He Observed

1. **BLoC for everything:** Using BLoC for a checkbox toggle. 50 lines of boilerplate for 3 lines of logic.
2. **Not using equatable:** Duplicate state emissions cause unnecessary rebuilds.
3. **Calling emit after async without closed check:** Runtime crash if bloc disposed during await.

## When to Use His Patterns

| Scenario | Pattern |
|----------|---------|
| Boolean toggle | `StatefulWidget` |
| Simple counter/list | `ValueNotifier` |
| Async data with retry | Riverpod `AsyncNotifier` |
| Multi-step wizard with validation | BLoC |
| Real-time with complex event ordering | BLoC |

## Citation

```
[^1]: Angelov, F. BLoC Library. GitHub: felangel/bloc. 
      Standardized event-driven state management with 
      unidirectional data flow, immutable states, and 
      deterministic testing via bloc_test.
```
