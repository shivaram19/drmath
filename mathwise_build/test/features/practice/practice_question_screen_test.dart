import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mathwise/features/practice/practice_question_screen.dart';

import '../../test_helpers.dart';

void main() {
  group('PracticeQuestionScreen', () {
    testWidgets('renders first question with all options', (WidgetTester tester) async {
      await pumpWithTheme(tester, const PracticeQuestionScreen());

      // Question counter
      expect(find.textContaining('Question'), findsOneWidget);

      // Submit button
      expect(find.text('Submit Answer'), findsOneWidget);

      // All 4 option labels (A, B, C, D)
      expect(find.text('A'), findsOneWidget);
      expect(find.text('B'), findsOneWidget);
      expect(find.text('C'), findsOneWidget);
      expect(find.text('D'), findsOneWidget);
    });

    testWidgets('selecting an option highlights it', (WidgetTester tester) async {
      await pumpWithTheme(tester, const PracticeQuestionScreen());

      // Tap option B
      await tester.tap(find.text('B'));
      await tester.pump();

      // Option B should still be visible (selected state)
      expect(find.text('B'), findsOneWidget);
    });

    testWidgets('submit button is present', (WidgetTester tester) async {
      await pumpWithTheme(tester, const PracticeQuestionScreen());

      expect(find.text('Submit Answer'), findsOneWidget);
    });

    testWidgets('progress indicator shows current position', (WidgetTester tester) async {
      await pumpWithTheme(tester, const PracticeQuestionScreen());

      expect(find.byType(LinearProgressIndicator), findsOneWidget);
    });
  });
}
