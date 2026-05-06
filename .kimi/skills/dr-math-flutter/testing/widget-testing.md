# Widget Testing — UI Rendering & Interactions

**Single Responsibility:** Verify widgets render correctly and respond to user input.

## Core API

| Class | Purpose |
|-------|---------|
| `WidgetTester` | Build, interact, inspect widget tree |
| `Finder` | Locate widgets (`find.text`, `find.byType`, `find.byKey`) |
| `Matcher` | Assert presence (`findsOneWidget`, `findsNothing`, `findsNWidgets`) |

## Test Structure

```dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mathwise/features/practice/practice_question_screen.dart';
import 'package:mathwise/shared/data/demo_data.dart';

void main() {
  group('PracticeQuestionScreen', () {
    testWidgets('renders first question on load', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: PracticeQuestionScreen(topicId: 'triangles'),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text(DemoData.triangleQuestions.first.text), findsOneWidget);
      expect(find.byType(ElevatedButton), findsNWidgets(4)); // 4 options
    });

    testWidgets('selecting option updates UI', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: PracticeQuestionScreen(topicId: 'triangles'),
        ),
      );
      await tester.pumpAndSettle();

      // Tap first option
      await tester.tap(find.byType(ElevatedButton).first);
      await tester.pump(); // Single frame for setState

      // Verify selection visual (e.g., selected color)
      final button = tester.widget<ElevatedButton>(find.byType(ElevatedButton).first);
      expect(button.style?.backgroundColor?.resolve({}), isNotNull);
    });

    testWidgets('completing quiz shows completion', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: PracticeQuestionScreen(topicId: 'triangles'),
        ),
      );
      await tester.pumpAndSettle();

      // Answer all 8 questions
      for (var i = 0; i < 8; i++) {
        await tester.tap(find.byType(ElevatedButton).first);
        await tester.pumpAndSettle();
      }

      expect(find.text('Quiz Complete!'), findsOneWidget);
    });
  });
}
```

## Finder Patterns

```dart
// By text
find.text('Submit');

// By type
find.byType(ElevatedButton);
find.byType(ListView);

// By key (preferred for dynamic content)
find.byKey(const Key('submit_button'));

// By icon
find.byIcon(Icons.check);

// Descendant
find.descendant(
  of: find.byType(Card),
  matching: find.text('Hint'),
);

// Scroll until visible
await tester.scrollUntilVisible(
  find.text('Last item'),
  500.0,
  scrollable: find.byType(Scrollable),
);
```

## Pump Semantics

| Method | Use When |
|--------|----------|
| `pumpWidget()` | Initial build |
| `pump()` | After `setState`, single frame |
| `pumpAndSettle()` | After animations, navigation, async loads |
| `pump(const Duration(seconds: 1))` | After explicit delays |

## Golden File Tests

```dart
testWidgets('home screen matches golden', (WidgetTester tester) async {
  await tester.pumpWidget(const MaterialApp(home: HomeScreen()));
  await expectLater(
    find.byType(HomeScreen),
    matchesGoldenFile('goldens/home_screen.png'),
  );
});
```

**First run generates:** `flutter test --update-goldens`

## Anti-Patterns

| Anti-Pattern | Fix |
|-------------|-----|
| `pumpAndSettle()` after every tap | Slow. Use `pump()` for simple state changes. |
| `find.text()` on dynamically generated text | Use `find.byKey()` instead. |
| Testing pixel-perfect layout | Use golden files, not coordinate assertions. |
| No `MaterialApp` wrapper | Widgets needing theme/directionality crash. |

## Expert Sources

Flutter Team. "Widget testing." https://docs.flutter.dev/testing#widget-tests
