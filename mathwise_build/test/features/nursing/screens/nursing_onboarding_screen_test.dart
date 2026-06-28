import 'package:flutter_test/flutter_test.dart';
import 'package:mathwise/features/nursing/screens/nursing_home_screen.dart';
import 'package:mathwise/features/nursing/screens/nursing_onboarding_screen.dart';
import 'package:mathwise/features/nursing/services/nursing_storage_service.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../../../test_helpers.dart';

void main() {
  group('NursingOnboardingScreen', () {
    setUp(() {
      SharedPreferences.setMockInitialValues({});
    });

    testWidgets('shows three onboarding pages', (WidgetTester tester) async {
      await pumpWithTheme(tester, const NursingOnboardingScreen());

      expect(find.text('Practice by Subject'), findsOneWidget);
      expect(find.text('Full Mock Test'), findsNothing);

      await tester.tap(find.text('Next'));
      await tester.pumpAndSettle();

      expect(find.text('Full Mock Test'), findsOneWidget);

      await tester.tap(find.text('Next'));
      await tester.pumpAndSettle();

      expect(find.text('Review Weak Areas'), findsOneWidget);
      expect(find.text('Get Started'), findsOneWidget);

      await expectLater(tester, meetsGuideline(androidTapTargetGuideline));
      await expectLater(tester, meetsGuideline(iOSTapTargetGuideline));
    });

    testWidgets('skip navigates to home and marks onboarding seen',
        (WidgetTester tester) async {
      final storage = NursingStorageService();
      await pumpWithTheme(
        tester,
        NursingOnboardingScreen(storage: storage),
      );

      await tester.tap(find.text('Skip'));
      await tester.pumpAndSettle();

      expect(find.byType(NursingHomeScreen), findsOneWidget);
      expect(await storage.getOnboardingSeen(), isTrue);
    });

    testWidgets('get started navigates to home and marks onboarding seen',
        (WidgetTester tester) async {
      final storage = NursingStorageService();
      await pumpWithTheme(
        tester,
        NursingOnboardingScreen(storage: storage),
      );

      await tester.tap(find.text('Next'));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Next'));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Get Started'));
      await tester.pumpAndSettle();

      expect(find.byType(NursingHomeScreen), findsOneWidget);
      expect(await storage.getOnboardingSeen(), isTrue);
    });
  });
}
