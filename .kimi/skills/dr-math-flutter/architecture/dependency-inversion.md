# Dependency Inversion — DI Patterns in Flutter

**Single Responsibility:** How to inject dependencies without tight coupling.

## Problem

```dart
// TIGHT COUPLING — wrong
class ProfileScreen extends StatelessWidget {
  final _repository = DemoQuestionRepository(); // Concrete class!
  // Cannot swap to ApiQuestionRepository for testing
}
```

Direct instantiation creates untestable, unswappable code.

## Principle

**Depend on abstractions, not concretions.** The UI layer depends on `QuestionRepository` (interface). The runtime binding injects `DemoQuestionRepository` or `ApiQuestionRepository`.

## Current: Manual Constructor Injection

For our 11-screen offline app, manual injection is sufficient:

```dart
// app.dart — composition root
class MathWiseApp extends StatelessWidget {
  const MathWiseApp({super.key});

  @override
  Widget build(BuildContext context) {
    final questionRepo = DemoQuestionRepository();
    final userRepo = DemoUserRepository();

    return MaterialApp(
      home: HomeScreen(
        questionRepository: questionRepo,
        userRepository: userRepo,
      ),
      routes: {
        '/practice': (context) => PracticeQuestionScreen(
          questionRepository: questionRepo,
        ),
      },
    );
  }
}
```

**Pros:** Zero dependencies, explicit, testable.  
**Cons:** Boilerplate grows with screen count. Manual route argument handling.

## Growth: get_it + injectable

When screens exceed 15 or dependencies multiply:

```dart
// pubspec.yaml
dependencies:
  get_it: ^7.0.0
  injectable: ^2.0.0

dev_dependencies:
  injectable_generator: ^2.0.0
  build_runner: ^2.0.0

// di/injection.dart
import 'package:get_it/get_it.dart';
import 'package:injectable/injectable.dart';

final getIt = GetIt.instance;

@InjectableInit()
void configureDependencies() => getIt.init();

// shared/data/module.dart
@module
abstract class DataModule {
  @dev
  @singleton
  QuestionRepository get demoQuestionRepo => DemoQuestionRepository();

  @prod
  @singleton
  QuestionRepository get apiQuestionRepo => ApiQuestionRepository();
}

// In widget:
final repo = getIt<QuestionRepository>();
```

## Scale: Riverpod as DI Container

Riverpod's providers **are** the DI container:

```dart
// providers/repository_providers.dart
final questionRepositoryProvider = Provider<QuestionRepository>((ref) {
  return DemoQuestionRepository();
});

// In widget:
final repo = ref.watch(questionRepositoryProvider);
```

**Advantage over get_it:** Compile-time safety. Scoped disposal. Test overrides:

```dart
// In test:
final container = ProviderContainer(
  overrides: [
    questionRepositoryProvider.overrideWithValue(MockQuestionRepository()),
  ],
);
```

## Comparison

| Approach | Lines of Config | Compile Safe | Scoped Disposal | Test Override | When to Use |
|----------|----------------|-------------|-----------------|---------------|-------------|
| Manual constructor | 0 | Yes | Yes | Pass mock | <15 screens |
| get_it | ~10 | No (runtime) | No | `registerSingleton` | Medium scale |
| Riverpod | ~5 | Yes | Yes | `overrideWithValue` | Any scale, recommended |

## Testing with DI

```dart
// test/features/practice/practice_screen_test.dart
class MockQuestionRepository implements QuestionRepository {
  @override
  Future<List<Question>> getByTopic(String topicId) async => [
    const Question(id: '1', text: 'Test', options: ['A','B'], correctIndex: 0),
  ];
}

testWidgets('loads questions on init', (tester) async {
  await tester.pumpWidget(
    MaterialApp(
      home: PracticeQuestionScreen(
        questionRepository: MockQuestionRepository(),
      ),
    ),
  );
  await tester.pumpAndSettle();
  expect(find.text('Test'), findsOneWidget);
});
```

## Anti-Patterns

| Anti-Pattern | Why It Fails |
|-------------|-------------|
| `new Repository()` in widget | Untestable, unswappable |
| `GetIt.I<Repository>()` in `build()` | Hidden dependency, hard to trace |
| Service locator without abstraction | Violates DIP, still tightly coupled |
| Global mutable singletons | Race conditions, test pollution |

## Expert Sources

Rousselet, R. Riverpod Documentation — Dependency Injection. https://riverpod.dev/docs/concepts/providers  
Angelov, F. very_good_cli — Dependency Injection scaffolding. https://cli.vgv.dev
