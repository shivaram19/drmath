# DFS-01: Flutter State Management — Riverpod vs BLoC Decision Framework

**Date:** 2026-05-06  
**Scope:** Technical comparison of Riverpod and BLoC for Dr. Math architecture  
**Research Phase:** DFS (Depth-First Technology Deep-Dive)  
**Parent BFS:** BFS-01 Flutter Architecture Landscape Mapping

---

## 1. Hypothesis

Riverpod is the optimal default state management for Dr. Math. BLoC should be reserved for complex event sequences (e.g., real-time collaborative features).

## 2. Deep Dive: Riverpod

### 2.1 Compile-Time Safety

Provider's `Provider.of<T>(context)` fails at runtime if no ancestor Provider<T> exists. Riverpod's generated providers are global references — impossible to miswire.

```dart
// Provider: Runtime failure possible
final user = Provider.of<User>(context); // ProviderNotFoundException?

// Riverpod: Compile-time guaranteed
final user = ref.watch(userProvider); // Always valid reference
```

### 2.2 Auto-Dispose

Riverpod tracks watcher count. When no widget watches a provider, it auto-disposes. Provider requires manual `Provider` wrapper or `ChangeNotifierProvider` with `dispose` override.

### 2.3 Family + Select

Parameterized providers with partial rebuilds:

```dart
@riverpod
Future<List<Question>> questions(QuestionsRef ref, String topicId) {
  return ref.watch(questionRepositoryProvider).getByTopic(topicId);
}

// Only rebuilds when score changes, not when list order changes
final score = ref.watch(
  questionsProvider(topicId).select((q) => q.valueOrNull?.length),
);
```

### 2.4 Testing

```dart
final container = ProviderContainer(
  overrides: [
    questionRepositoryProvider.overrideWithValue(MockRepository()),
  ],
);
```

Zero widget tree setup. Direct provider testing.

## 3. Deep Dive: BLoC

### 3.1 Event-Driven Unidirectional Flow

```
User taps → Event added → Bloc processes → State emitted → UI rebuilds
```

This is valuable when:
- Events have complex validation rules
- Multiple events can arrive simultaneously
- State transitions have side effects (analytics, logging)
- Timeouts and retries are business-critical

### 3.2 Cubit Simplification

For simpler cases, Cubit removes the Event layer:

```dart
class QuizCubit extends Cubit<QuizState> {
  void answer(int selected) => emit(state.copyWith(/*...*/));
}
```

### 3.3 Testing with bloc_test

```dart
blocTest<QuizCubit, QuizState>(
  'emits correct state',
  build: QuizCubit.new,
  act: (cubit) => cubit.answer(1),
  expect: () => [isA<QuizState>()],
);
```

Deterministic, time-independent testing.

## 4. Comparative Analysis

| Dimension | Riverpod | BLoC | Winner |
|-----------|----------|------|--------|
| Learning curve | Medium | Medium-High | Riverpod |
| Boilerplate | Low | Medium | Riverpod |
| Compile safety | Yes | Yes (with sealed classes) | Tie |
| Async handling | AsyncNotifier | Stream-based | Riverpod |
| Complex events | Basic | Excellent | BLoC |
| Testing ease | Very easy | Easy | Riverpod |
| Community size | Large | Very large | BLoC |
| Enterprise adoption | Growing | Established | BLoC |

## 5. Decision Framework for Dr. Math

| Feature | State Complexity | Solution |
|---------|-----------------|----------|
| Quiz scoring | Low (increment counter) | `StatefulWidget` |
| Curriculum progress | Medium (track completion) | Riverpod `Notifier` |
| User profile | Medium (load/save) | Riverpod `AsyncNotifier` |
| Real-time leaderboard | High (WebSocket, conflicts) | BLoC |
| Multi-step wizard | High (validation, branching) | BLoC |
| Theme toggle | Low | Riverpod `StateNotifier` |

## 6. Conclusion

**Default:** Riverpod for all state management.  
**Exception:** BLoC for complex event-driven flows (real-time, multi-step wizards).  
**Rationale:** Riverpod's lower boilerplate and superior async handling match Dr. Math's offline-first, demo-data architecture. BLoC adds unnecessary complexity for current scope.

## 7. ADR Reference

This deep-dive supports ADR-0XX (to be written): "State Management Selection for Dr. Math Mobile."

## 8. References

[^1]: Rousselet, R. "Riverpod vs Provider." https://riverpod.dev/docs/why_riverpod  
[^2]: Angelov, F. "BLoC Core Concepts." https://bloclibrary.dev/#/coreconcepts  
[^3]: Bizzotto, A. "Flutter Riverpod 2.0 Complete Guide." https://codewithandrea.com/articles/flutter-riverpod-2  
[^4]: Egan, B. "Flutter Architecture Samples." https://github.com/brianegan/flutter_architecture_samples
