import 'package:flutter_test/flutter_test.dart';
import 'package:mathwise/features/nursing/models/attempt.dart';
import 'package:mathwise/features/nursing/screens/nursing_disclaimer_screen.dart';
import 'package:mathwise/features/nursing/screens/nursing_settings_screen.dart';
import 'package:mathwise/features/nursing/services/nursing_storage_service.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../../../test_helpers.dart';

void main() {
  group('NursingSettingsScreen', () {
    setUp(() {
      SharedPreferences.setMockInitialValues({});
    });

    testWidgets('renders settings tiles', (WidgetTester tester) async {
      await pumpWithTheme(tester, const NursingSettingsScreen());

      expect(find.text('Settings'), findsOneWidget);
      expect(find.text('Language'), findsOneWidget);
      expect(find.text('Offline analysis'), findsOneWidget);
      expect(find.text('Clear progress'), findsOneWidget);
      expect(find.text('Disclaimer'), findsOneWidget);

      await expectLater(tester, meetsGuideline(androidTapTargetGuideline));
      await expectLater(tester, meetsGuideline(iOSTapTargetGuideline));
    });

    testWidgets('shows pending sync indicator when analysis is queued',
        (WidgetTester tester) async {
      final storage = NursingStorageService();
      await storage.queuePendingAnalysis([
        const Attempt(
          questionId: 1,
          selectedOption: 'A',
          isCorrect: true,
          timeSeconds: 10,
          confidence: 3,
          subjectId: 'nursing',
          topicId: 'vital_signs',
          cognitiveLevel: 'remember',
        ),
      ]);

      await pumpWithTheme(tester, NursingSettingsScreen(storage: storage));

      expect(find.text('Some results are waiting to sync.'), findsOneWidget);
    });

    testWidgets('clear progress removes stored data',
        (WidgetTester tester) async {
      final storage = NursingStorageService();
      await storage.appendAttempts([
        const Attempt(
          questionId: 1,
          selectedOption: 'A',
          isCorrect: true,
          timeSeconds: 10,
          confidence: 3,
          subjectId: 'nursing',
          topicId: 'vital_signs',
          cognitiveLevel: 'remember',
        ),
      ]);

      await pumpWithTheme(tester, NursingSettingsScreen(storage: storage));

      await tester.tap(find.text('Clear progress'));
      await tester.pumpAndSettle();

      await tester.tap(find.text('Clear'));
      await tester.pumpAndSettle();

      expect(find.text('Progress cleared'), findsOneWidget);
      expect(await storage.loadAttempts(), isEmpty);
    });

    testWidgets('disclaimer tile navigates to disclaimer screen',
        (WidgetTester tester) async {
      await pumpWithTheme(tester, const NursingSettingsScreen());

      await tester.tap(find.text('Disclaimer'));
      await tester.pumpAndSettle();

      expect(find.byType(NursingDisclaimerScreen), findsOneWidget);
    });
  });
}
