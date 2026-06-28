import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mathwise/features/home/home_screen.dart';
import 'package:mathwise/shared/widgets/bottom_nav_bar.dart';

import '../../test_helpers.dart';

void main() {
  group('HomeScreen', () {
    testWidgets('renders MathWise title', (WidgetTester tester) async {
      await pumpWithTheme(tester, const HomeScreen());

      expect(find.text('MathWise'), findsOneWidget);
    });

    testWidgets('shows greeting', (WidgetTester tester) async {
      await pumpWithTheme(tester, const HomeScreen());

      expect(find.textContaining('Hello'), findsOneWidget);
    });

    testWidgets('has Resume Lesson CTA', (WidgetTester tester) async {
      await pumpWithTheme(tester, const HomeScreen());

      expect(find.text('Resume Lesson'), findsOneWidget);
    });

    testWidgets('has Daily Practice section', (WidgetTester tester) async {
      await pumpWithTheme(tester, const HomeScreen());

      expect(find.text('Daily Practice'), findsOneWidget);
      expect(find.text('Start Now'), findsOneWidget);
    });

    testWidgets('has custom bottom navigation', (WidgetTester tester) async {
      await pumpWithTheme(tester, const HomeScreen());

      expect(find.byType(MathWiseBottomNav), findsOneWidget);
    });

    // TODO(phase10.7): Add narrow-screen overflow test once the full HomeScreen
    // responsive pass (Course Progress row, Games card, bottom nav) is complete.
  });
}
