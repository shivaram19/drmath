# Riverpod — Reactive Caching & Data-binding

**Single Responsibility:** Manage app-level state with compile-time safety.

## Problem

Provider's runtime errors (`ProviderNotFoundException`), nested widget hell, and lack of compile-time safety led Rémi Rousselet to build Riverpod [^1].

## Why Riverpod Over Provider

| Feature | Provider | Riverpod |
|---------|----------|----------|
| Compile-time safety | ❌ Runtime lookup | ✅ Generated providers |
| No BuildContext needed | ❌ Must be inside widget | ✅ Global scope |
| Auto-dispose | ❌ Manual | ✅ Automatic |
| Family (parameterized) | ❌ Complex | ✅ `family` modifier |
| Select rebuilds | ❌ Full provider rebuild | ✅ `select` for partial |
| Testing overrides | ❌ Difficult | ✅ `ProviderContainer` overrides |

## Code-Generated Setup

```yaml
# pubspec.yaml
dependencies:
  flutter_riverpod: ^2.4.0
  riverpod_annotation: ^2.2.0

dev_dependencies:
  riverpod_generator: ^2.3.0
  build_runner: ^2.4.0
```

```dart
// providers/question_provider.dart
import 'package:riverpod_annotation/riverpod_annotation.dart';
part 'question_provider.g.dart';

@riverpod
class QuestionBank extends _$QuestionBank {
  @override
  Future<List<Question>> build(String topicId) async {
    final repo = ref.watch(questionRepositoryProvider);
    return repo.getByTopic(topicId);
  }

  Future<void> refresh() async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      final repo = ref.read(questionRepositoryProvider);
      return repo.getByTopic(arg); // arg = build parameter
    });
  }
}

@riverpod
QuestionRepository questionRepository(QuestionRepositoryRef ref) {
  return DemoQuestionRepository();
}
```

## Consumption Patterns

```dart
// Full rebuild on any change
final questions = ref.watch(questionBankProvider(topicId));

// Partial rebuild: only when list length changes
final count = ref.watch(
  questionBankProvider(topicId).select((q) => q.valueOrNull?.length),
);

// One-shot read (callbacks, events)
final repo = ref.read(questionRepositoryProvider);
```

## AsyncValue Pattern

```dart
questions.when(
  data: (list) => QuestionList(questions: list),
  loading: () => const SkeletonLoader(),
  error: (err, stack) => ErrorView(
    message: err.toString(),
    onRetry: () => ref.invalidate(questionBankProvider(topicId)),
  ),
);
```

**Never** manually track `isLoading` / `hasError` booleans. `AsyncValue` handles all three states.

## Testing

```dart
test('questionBank loads questions', () async {
  final container = ProviderContainer(
    overrides: [
      questionRepositoryProvider.overrideWithValue(MockRepository()),
    ],
  );

  final provider = questionBankProvider('triangles');
  await expectLater(
    container.read(provider.future),
    completion(hasLength(8)),
  );
});
```

## Anti-Patterns

| Anti-Pattern | Why It Fails |
|-------------|-------------|
| `ref.watch` inside `onPressed` | Should use `ref.read` for one-shot reads |
| `ref.read(provider.notifier).state = x` | Bypasses reactive system |
| Not using `AsyncValue` | Manual loading/error booleans are error-prone |
| Forgetting `part` directive | Code generation fails silently |
| `ref.watch` in `initState` | Use `ref.listen` for side effects |

## Expert Sources

[^1]: Rousselet, R. Riverpod Documentation. https://riverpod.dev  
[^2]: Bizzotto, A. "Flutter Riverpod 2.0: Complete Guide." https://codewithandrea.com/articles/flutter-riverpod-2
