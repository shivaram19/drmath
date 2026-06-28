import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mathwise/features/nursing/screens/nursing_disclaimer_screen.dart';
import 'package:mathwise/features/nursing/screens/nursing_entry_screen.dart';
import 'package:mathwise/features/nursing/screens/nursing_home_screen.dart';
import 'package:mathwise/features/nursing/screens/nursing_onboarding_screen.dart';
import 'package:mathwise/features/nursing/services/nursing_storage_service.dart';

class _FakeStorage extends NursingStorageService {
  _FakeStorage({this.disclaimerAccepted = false, this.onboardingSeen = false});

  final bool disclaimerAccepted;
  final bool onboardingSeen;

  @override
  Future<bool> getDisclaimerAccepted() async => disclaimerAccepted;

  @override
  Future<bool> getOnboardingSeen() async => onboardingSeen;
}

void main() {
  group('NursingEntryScreen', () {
    Future<void> pumpEntry(WidgetTester tester, NursingStorageService storage) async {
      await tester.pumpWidget(
        MaterialApp(
          home: NursingEntryScreen(storage: storage),
        ),
      );
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 100));
    }

    testWidgets('routes to disclaimer when not yet accepted', (tester) async {
      await pumpEntry(tester, _FakeStorage());
      expect(find.byType(NursingDisclaimerScreen), findsOneWidget);
      expect(find.byType(NursingOnboardingScreen), findsNothing);
      expect(find.byType(NursingHomeScreen), findsNothing);
    });

    testWidgets('routes to onboarding when disclaimer accepted but onboarding not seen', (tester) async {
      await pumpEntry(tester, _FakeStorage(disclaimerAccepted: true));
      expect(find.byType(NursingDisclaimerScreen), findsNothing);
      expect(find.byType(NursingOnboardingScreen), findsOneWidget);
      expect(find.byType(NursingHomeScreen), findsNothing);
    });

    testWidgets('routes to home when disclaimer and onboarding are complete', (tester) async {
      await pumpEntry(tester, _FakeStorage(disclaimerAccepted: true, onboardingSeen: true));
      expect(find.byType(NursingDisclaimerScreen), findsNothing);
      expect(find.byType(NursingOnboardingScreen), findsNothing);
      expect(find.byType(NursingHomeScreen), findsOneWidget);
    });
  });
}
