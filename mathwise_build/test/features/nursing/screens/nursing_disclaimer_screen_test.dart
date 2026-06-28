import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mathwise/features/nursing/screens/nursing_disclaimer_screen.dart';
import 'package:mathwise/features/nursing/screens/nursing_home_screen.dart';
import 'package:mathwise/features/nursing/screens/nursing_onboarding_screen.dart';
import 'package:mathwise/features/nursing/services/nursing_storage_service.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../../../test_helpers.dart';

void main() {
  group('NursingDisclaimerScreen', () {
    setUp(() {
      SharedPreferences.setMockInitialValues({});
    });

    testWidgets('shows disclaimer text and requires acceptance',
        (WidgetTester tester) async {
      await pumpWithTheme(tester, const NursingDisclaimerScreen());

      expect(find.text('Nursing Exam Practice'), findsOneWidget);
      expect(find.text('This app is for exam preparation and educational practice only.'), findsOneWidget);

      final continueButton = find.widgetWithText(ElevatedButton, 'Continue');
      expect(tester.widget<ElevatedButton>(continueButton).enabled, isFalse);

      await tester.tap(find.text('I understand and agree'));
      await tester.pump();

      expect(tester.widget<ElevatedButton>(continueButton).enabled, isTrue);

      await expectLater(tester, meetsGuideline(androidTapTargetGuideline));
      await expectLater(tester, meetsGuideline(iOSTapTargetGuideline));
    });

    testWidgets('continue button enables after acceptance',
        (WidgetTester tester) async {
      await pumpWithTheme(tester, const NursingDisclaimerScreen());

      await tester.tap(find.text('I understand and agree'));
      await tester.pump();

      final continueButton = find.widgetWithText(ElevatedButton, 'Continue');
      expect(tester.widget<ElevatedButton>(continueButton).enabled, isTrue);
    });

    testWidgets('accepting navigates to onboarding when not seen',
        (WidgetTester tester) async {
      await pumpWithTheme(tester, const NursingDisclaimerScreen());

      await tester.tap(find.text('I understand and agree'));
      await tester.pump();
      await tester.tap(find.widgetWithText(ElevatedButton, 'Continue'));
      await tester.pumpAndSettle();

      expect(find.byType(NursingOnboardingScreen), findsOneWidget);
    });

    testWidgets('navigates to home when already accepted',
        (WidgetTester tester) async {
      final storage = NursingStorageService();
      await storage.setDisclaimerAccepted(true);

      await pumpWithTheme(tester, NursingDisclaimerScreen(storage: storage));

      expect(find.byType(NursingHomeScreen), findsOneWidget);
    });
  });
}
