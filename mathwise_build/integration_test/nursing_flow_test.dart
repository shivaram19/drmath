import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:integration_test/integration_test.dart';
import 'package:mathwise/features/nursing/screens/nursing_entry_screen.dart';
import 'package:mathwise/features/nursing/screens/nursing_home_screen.dart';
import 'package:mathwise/features/nursing/screens/nursing_quiz_screen.dart';
import 'package:mathwise/features/nursing/screens/nursing_results_screen.dart';
import 'package:mathwise/features/nursing/services/nursing_api_service.dart';
import 'package:mathwise/features/nursing/services/nursing_storage_service.dart';
import 'package:shared_preferences/shared_preferences.dart';

http.Response _jsonResponse(Object body, {int statusCode = 200}) {
  return http.Response.bytes(
    utf8.encode(jsonEncode(body)),
    statusCode,
    headers: {'content-type': 'application/json; charset=utf-8'},
  );
}

const _questionJson = {
  'id': 1,
  'subject_id': 'nursing',
  'topic_id': 'vital_signs',
  'concept_tag': 'temperature',
  'difficulty': 1,
  'cognitive_level': 'remember',
  'context': 'clinical',
  'format': 'mcq',
  'question': 'What is normal body temperature?',
  'options': ['A) 36-37°C', 'B) 38°C', 'C) 35°C', 'D) 39°C'],
  'correct_answer': 'A',
  'explanation': 'Around 37°C.',
  'source': 'Tabers',
  'verification_status': 'verified',
};

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('Nursing flow', () {
    late MockClient client;

    setUp(() {
      SharedPreferences.setMockInitialValues({});
      client = MockClient((request) async {
        final path = request.url.path;
        if (path == '/api/nursing/status') {
          return _jsonResponse({'questions': 130});
        }
        if (path == '/api/nursing/topics') {
          return _jsonResponse({
            'subjects': ['nursing'],
            'topics_by_subject': {
              'nursing': [
                {'id': 'vital_signs', 'name': 'Vital Signs'},
              ],
            },
            'counts': {'nursing': 130},
          });
        }
        if (path == '/api/nursing/questions') {
          return _jsonResponse([_questionJson]);
        }
        if (path == '/api/nursing/analyze') {
          return _jsonResponse(<String, dynamic>{
            'subject_capabilities': <Map<String, dynamic>>[],
            'topic_capabilities': [
              {
                'topic_id': 'vital_signs',
                'accuracy': 1.0,
                'speed_score': 0.5,
                'confidence_gap': 0.0,
                'consistency_score': 1.0,
                'priority_score': 0.0,
              },
            ],
            'dimension_capabilities': <Map<String, dynamic>>[],
          });
        }
        return http.Response.bytes(utf8.encode('Not found'), 404);
      });
    });

    testWidgets('entry → disclaimer → onboarding → home → quiz → results',
        (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: NursingEntryScreen(
            api: NursingApiService(client: client),
            storage: NursingStorageService(),
          ),
        ),
      );
      await tester.pumpAndSettle();

      // Disclaimer
      expect(find.text('Nursing Exam Practice'), findsOneWidget);
      await tester.tap(find.text('I understand and agree'));
      await tester.pump();
      await tester.tap(find.widgetWithText(ElevatedButton, 'Continue'));
      await tester.pumpAndSettle();

      // Onboarding
      expect(find.text('Practice by Subject'), findsOneWidget);
      await tester.tap(find.text('Skip'));
      await tester.pumpAndSettle();

      // Home
      expect(find.byType(NursingHomeScreen), findsOneWidget);
      expect(find.text('Nursing Practice'), findsOneWidget);

      // Start a diagnostic quiz
      await tester.tap(find.widgetWithText(ElevatedButton, 'Diagnostic'));
      await tester.pumpAndSettle();

      // Quiz
      expect(find.byType(NursingQuizScreen), findsOneWidget);
      expect(find.text('What is normal body temperature?'), findsOneWidget);

      await tester.tap(find.text('A) 36-37°C'));
      await tester.pump();
      await tester.tap(find.widgetWithText(ElevatedButton, 'Submit'));
      await tester.pumpAndSettle();

      // Results
      expect(find.byType(NursingResultsScreen), findsOneWidget);
      expect(find.text('1 / 1'), findsOneWidget);
    });
  });
}
