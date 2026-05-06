# Integration Testing — E2E & Mobilerun

**Single Responsibility:** Verify complete user journeys across the full app.

## Problem

Unit and widget tests validate components in isolation. Integration tests validate that components work together: navigation, state persistence, async data loading.

## integration_test Package

```dart
// integration_test/practice_flow_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:mathwise/main.dart' as app;

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('Practice Flow E2E', () {
    testWidgets('student completes triangle quiz', (tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Navigate to curriculum
      await tester.tap(find.text('Start Learning'));
      await tester.pumpAndSettle();

      // Select Triangles topic
      await tester.tap(find.text('Triangles'));
      await tester.pumpAndSettle();

      // Answer all questions
      for (var i = 0; i < 8; i++) {
        // Select first option
        await tester.tap(find.byType(ElevatedButton).first);
        await tester.pumpAndSettle();

        // Tap next / submit
        if (i < 7) {
          await tester.tap(find.text('Next'));
        } else {
          await tester.tap(find.text('Submit'));
        }
        await tester.pumpAndSettle();
      }

      // Verify completion screen
      expect(find.text('Quiz Complete!'), findsOneWidget);
      expect(find.textContaining('Score:'), findsOneWidget);
    });
  });
}
```

## Run E2E Tests

```bash
# Requires connected device or emulator
flutter test integration_test/practice_flow_test.dart

# With screenshots
flutter test integration_test/ --dart-define=TAKE_SCREENSHOTS=true
```

## Mobilerun Agentic Testing

Mobilerun executes tests on physical devices using AI agents:

```bash
# Requirements: Android device + Portal APK + LLM API key
source mobilerun-venv/bin/activate
cd mathwise_build
mobilerun --test-dir integration_test/ --agent gemini
```

**Limitation:** Requires physical Android device + `GOOGLE_API_KEY` environment variable.

## Critical Paths to Test

| Flow | Test File |
|------|-----------|
| Home → Curriculum → Topic → Practice → Complete | `practice_flow_test.dart` |
| Home → Profile → Edit → Save | `profile_flow_test.dart` |
| Home → Games → Select → Play | `games_flow_test.dart` |
| Curriculum → Concept → Back → Practice | `concept_flow_test.dart` |

## Anti-Patterns

| Anti-Pattern | Fix |
|-------------|-----|
| Testing at widget level (find.byType) | Use semantic labels (`find.text`) |
| No pumpAndSettle after navigation | Widget not found errors |
| Hardcoded delays (`Future.delayed`) | Flaky tests. Use `pumpAndSettle` |
| Testing non-critical paths | Focus on conversion flows |

## Expert Sources

Flutter Team. "Integration testing." https://docs.flutter.dev/testing/integration-tests  
Mobilerun Documentation. https://pub.dev/packages/mobilerun
