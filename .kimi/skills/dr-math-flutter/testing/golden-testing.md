# Golden Testing — UI Regression Detection

**Single Responsibility:** Catch visual regressions automatically.

## Problem

A CSS change breaks padding on 12 screens. Manual QA misses it. Golden tests catch pixel-level regressions.

## How Golden Tests Work

1. Generate reference screenshot (`--update-goldens`)
2. On subsequent runs, compare current render to reference
3. Fail if pixels differ beyond tolerance

## Implementation

```dart
// test/goldens/home_screen_test.dart
testWidgets('home screen matches golden', (WidgetTester tester) async {
  await tester.pumpWidget(
    MaterialApp(
      theme: AppTheme.light(),
      home: const HomeScreen(),
    ),
  );
  await tester.pumpAndSettle();

  await expectLater(
    find.byType(HomeScreen),
    matchesGoldenFile('goldens/home_screen.png'),
  );
});
```

## Generate References

```bash
cd mathwise_build
flutter test --update-goldens
# Generates: test/goldens/*.png
# Commit these to git!
```

## Platform Considerations

Golden files are **platform-dependent** (font rendering differs macOS/Linux/Windows).

**Solution 1:** Generate on CI (Linux) and download for local comparison.

**Solution 2:** Use `flutter_test_config.dart` with Ahem font:

```dart
// test/flutter_test_config.dart
import 'dart:async';
import 'package:flutter_test/flutter_test.dart';

Future<void> testExecutable(FutureOr<void> Function() testMain) async {
  TestWidgetsFlutterBinding.ensureInitialized();
  // Use consistent font across platforms
  await loadFonts();
  await testMain();
}
```

## Golden Tests to Maintain

| Screen | Priority |
|--------|----------|
| HomeScreen | Critical |
| PracticeQuestionScreen | Critical |
| ProfileScreen | High |
| CurriculumListScreen | High |
| GamesScreen | Medium |

## Anti-Patterns

| Anti-Pattern | Fix |
|-------------|-----|
| Golden tests on CI only | Run locally before commit |
| No tolerance for anti-aliasing | Use `matchesGoldenFile` with tolerance |
| Committing goldens without review | Goldens are code — review them |
| Testing every screen | Focus on high-traffic screens |

## Expert Sources

Flutter Team. "Golden file testing." https://docs.flutter.dev/testing/overview#golden-tests
