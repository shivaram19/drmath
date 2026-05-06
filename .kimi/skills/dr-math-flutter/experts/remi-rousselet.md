# Expert: Rémi Rousselet

**GitHub:** https://github.com/rrousselGit  
**Key Projects:** Provider, Riverpod, flutter_hooks  
**Authority:** #1 Flutter StackOverflow answerer; state management paradigm architect

## Why He Matters

Rousselet identified the fundamental flaw in Provider: **runtime lookup with no compile-time safety**. A missing `Provider` in the widget tree causes `ProviderNotFoundException` at runtime — untraceable in large apps.

Riverpod solves this by:
1. **Global providers** — no widget tree dependency
2. **Code generation** — `riverpod_generator` creates type-safe provider references
3. **Auto-dispose** — providers automatically clean up when no longer watched
4. **Family + Select** — parameterized providers with partial rebuilds

## Key Patterns

### Provider is the DI Container

```dart
@riverpod
UserRepository userRepository(UserRepositoryRef ref) {
  return DemoUserRepository();
}

// Anywhere:
final repo = ref.read(userRepositoryProvider);
```

### AsyncNotifier for Async State

```dart
@riverpod
class QuizSession extends _$QuizSession {
  @override
  Future<QuizState> build(String topicId) async {
    final repo = ref.watch(questionRepositoryProvider);
    final questions = await repo.getByTopic(topicId);
    return QuizState(questions: questions, currentIndex: 0);
  }

  void answer(int selected) {
    final current = state.valueOrNull;
    if (current == null) return;
    state = AsyncData(current.copyWith(/*...*/));
  }
}
```

### Select for Partial Rebuilds

```dart
// Only rebuilds when score changes, not when hint changes
final score = ref.watch(
  quizSessionProvider(topicId).select((s) => s.valueOrNull?.score),
);
```

## Failure Modes He Observed

1. **Provider nesting hell:** Teams wrapping entire app in 5+ Provider widgets. Riverpod eliminates nesting entirely.
2. **Forgetting to dispose:** Streams, controllers leak memory. Riverpod auto-disposes.
3. **Testing without overrides:** Hard to mock with Provider. Riverpod's `ProviderContainer` makes overrides trivial.

## When to Use His Patterns

| Scenario | Pattern |
|----------|---------|
| Simple local state | `StatefulWidget` |
| Shared state, 2-3 consumers | `ValueNotifier` |
| Shared state, many consumers | Riverpod `Notifier` |
| Async data with loading/error | Riverpod `AsyncNotifier` |
| Complex event sequences | BLoC (Angelov) |

## Citation

```
[^1]: Rousselet, R. (2021-2025). Riverpod: A Reactive Caching and 
      Data-binding Framework. GitHub: rrousselGit/riverpod. 
      Motivation derived from production failures of Provider's 
      runtime lookup model in enterprise Flutter applications.
```
