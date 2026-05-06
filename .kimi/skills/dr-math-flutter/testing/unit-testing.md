# Unit Testing — Pure Dart Logic

**Single Responsibility:** Test business logic without Flutter dependencies.

## Problem

Unit tests are fast (<10ms) and deterministic. They catch logic errors before they reach the UI layer. Skipping them means debugging through widget trees.

## Test Structure

```dart
// test/models/question_test.dart
import 'package:flutter_test/flutter_test.dart'; // Re-exports test package
import 'package:mathwise/shared/models/question.dart';

void main() {
  group('Question', () {
    const question = Question(
      id: 'q1',
      text: 'Sum of angles in triangle?',
      options: ['90°', '180°', '270°', '360°'],
      correctIndex: 1,
    );

    test('isCorrect returns true for correct index', () {
      expect(question.isCorrect(1), isTrue);
    });

    test('isCorrect returns false for incorrect index', () {
      expect(question.isCorrect(0), isFalse);
    });

    test('assertion fails for invalid correctIndex', () {
      expect(
        () => const Question(
          id: 'q2',
          text: 'Test',
          options: ['A', 'B'],
          correctIndex: 5, // Invalid
        ),
        throwsAssertionError,
      );
    });
  });

  group('Question Scoring', () {
    const question = Question(
      id: 'q1',
      text: 'Test',
      options: ['A', 'B'],
      correctIndex: 0,
    );

    test('full score without hint', () {
      expect(question.calculateScore(usedHint: false), 10);
    });

    test('half score with hint', () {
      expect(question.calculateScore(usedHint: true), 5);
    });
  });
}
```

## Mocking with mocktail

```dart
// test/data/question_repository_test.dart
import 'package:mocktail/mocktail.dart';

class MockQuestionDataSource extends Mock implements QuestionDataSource {}

void main() {
  late MockQuestionDataSource dataSource;
  late QuestionRepository repository;

  setUp(() {
    dataSource = MockQuestionDataSource();
    repository = QuestionRepository(dataSource: dataSource);
  });

  test('getByTopic returns questions from data source', () async {
    when(() => dataSource.fetchByTopic('triangles'))
        .thenAnswer((_) async => [/* raw data */]);

    final questions = await repository.getByTopic('triangles');

    expect(questions, hasLength(1));
    verify(() => dataSource.fetchByTopic('triangles')).called(1);
  });
}
```

## Coverage

```bash
flutter test --coverage
genhtml coverage/lcov.info -o coverage/html
# Open coverage/html/index.html
```

## Rules

- Test public API, not private methods
- Use real value objects, not mocks
- One assertion concept per test
- Name tests descriptively: `test('returns empty list when topic not found')`

## Anti-Patterns

| Anti-Pattern | Fix |
|-------------|-----|
| Testing getters/setters | Test behavior, not properties |
| Mocking value objects | Use real immutable objects |
| Multiple unrelated assertions | Split into separate tests |
| Testing implementation details | Test public contract |

## Expert Sources

Dart Skills. "dart-add-unit-test." https://github.com/dart-lang/skills  
Angelov, F. "Testing with bloc_test." https://bloclibrary.dev/#/testing
