import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:mathwise/features/nursing/controllers/nursing_session_controller.dart';
import 'package:mathwise/features/nursing/screens/nursing_quiz_screen.dart';
import 'package:mathwise/features/nursing/screens/nursing_results_screen.dart';
import 'package:mathwise/features/nursing/services/nursing_api_service.dart';
import 'package:mathwise/features/nursing/services/nursing_storage_service.dart';
import 'package:shared_preferences/shared_preferences.dart';

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

http.Response _jsonResponse(Object body, {int statusCode = 200}) {
  return http.Response.bytes(
    utf8.encode(jsonEncode(body)),
    statusCode,
    headers: {'content-type': 'application/json; charset=utf-8'},
  );
}

void main() {
  group('NursingQuizScreen', () {
    setUp(() {
      SharedPreferences.setMockInitialValues({});
    });

    testWidgets('loads and displays a practice question', (tester) async {
      final client = MockClient((request) async {
        if (request.url.path == '/api/nursing/questions') {
          return _jsonResponse([_questionJson]);
        }
        return http.Response.bytes(utf8.encode('Not found'), 404);
      });

      await tester.pumpWidget(
        MaterialApp(
          home: NursingQuizScreen(
            mode: QuizMode.practice,
            subjectId: 'nursing',
            api: NursingApiService(client: client),
            storage: NursingStorageService(),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Practice'), findsOneWidget);
      expect(find.text('Question 1 of 1'), findsOneWidget);
      expect(find.text('What is normal body temperature?'), findsOneWidget);
    });

    testWidgets('selects an answer and submits to results', (tester) async {
      final client = MockClient((request) async {
        if (request.url.path == '/api/nursing/questions') {
          return _jsonResponse([_questionJson]);
        }
        if (request.url.path == '/api/nursing/analyze') {
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

      await tester.pumpWidget(
        MaterialApp(
          home: NursingQuizScreen(
            mode: QuizMode.practice,
            subjectId: 'nursing',
            api: NursingApiService(client: client),
            storage: NursingStorageService(),
          ),
        ),
      );
      await tester.pumpAndSettle();

      await tester.tap(find.text('A) 36-37°C'));
      await tester.pump();

      await tester.tap(find.text('Submit'));
      await tester.pumpAndSettle();

      expect(find.byType(NursingResultsScreen), findsOneWidget);
    });

    testWidgets('shows snackbar when advancing without answer',
        (tester) async {
      final client = MockClient((request) async {
        return _jsonResponse([_questionJson, _questionJson]);
      });

      await tester.pumpWidget(
        MaterialApp(
          home: NursingQuizScreen(
            mode: QuizMode.practice,
            subjectId: 'nursing',
            api: NursingApiService(client: client),
            storage: NursingStorageService(),
          ),
        ),
      );
      await tester.pumpAndSettle();

      await tester.tap(find.text('Next'));
      await tester.pump();

      expect(find.text('Please select an answer'), findsOneWidget);
    });

    testWidgets('offers to resume an in-flight session', (tester) async {
      final storage = NursingStorageService();
      await storage.saveInflightSession({
        'mode': 'practice',
        'subject_id': 'nursing',
        'topic_id': 'vital_signs',
        'questions': [_questionJson],
        'current_index': 0,
        'selected_answers': {'0': 'A'},
        'marked_for_review': <int>[],
        'remaining_seconds': 3600,
      });

      await tester.pumpWidget(
        MaterialApp(
          home: NursingQuizScreen(
            mode: QuizMode.practice,
            subjectId: 'nursing',
            api: NursingApiService(),
            storage: storage,
          ),
        ),
      );
      await tester.pump();

      expect(find.text('Resume previous session?'), findsOneWidget);
    });
  });
}
