import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:mathwise/features/nursing/models/attempt.dart';
import 'package:mathwise/features/nursing/screens/nursing_quiz_screen.dart';
import 'package:mathwise/features/nursing/screens/nursing_results_screen.dart';
import 'package:mathwise/features/nursing/services/nursing_api_service.dart';
import 'package:mathwise/features/nursing/services/nursing_storage_service.dart';
import 'package:shared_preferences/shared_preferences.dart';

const _attempt = Attempt(
  questionId: 1,
  selectedOption: 'A',
  isCorrect: true,
  timeSeconds: 12.0,
  confidence: 3,
  subjectId: 'nursing',
  topicId: 'vital_signs',
  cognitiveLevel: 'remember',
);

http.Response _jsonResponse(Object body, {int statusCode = 200}) {
  return http.Response.bytes(
    utf8.encode(jsonEncode(body)),
    statusCode,
    headers: {'content-type': 'application/json; charset=utf-8'},
  );
}

void main() {
  group('NursingResultsScreen', () {
    setUp(() {
      SharedPreferences.setMockInitialValues({});
    });

    testWidgets('renders score and weak areas from analysis',
        (tester) async {
      final client = MockClient((request) async {
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
          home: NursingResultsScreen(
            attempts: const [_attempt],
            api: NursingApiService(client: client),
            storage: NursingStorageService(),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('1 / 1'), findsOneWidget);
      expect(find.text('100% correct'), findsOneWidget);
      expect(find.text('vital signs'), findsOneWidget);
    });

    testWidgets('shows pending sync banner when offline', (tester) async {
      final client = MockClient((request) async {
        throw const SocketException('No internet');
      });

      await tester.pumpWidget(
        MaterialApp(
          home: NursingResultsScreen(
            attempts: const [_attempt],
            api: NursingApiService(client: client),
            storage: NursingStorageService(),
          ),
        ),
      );
      await tester.pump(const Duration(seconds: 5));

      expect(find.textContaining('offline'), findsOneWidget);
    });

    testWidgets('try again button navigates to quiz', (tester) async {
      final client = MockClient((request) async {
        if (request.url.path == '/api/nursing/analyze') {
          return _jsonResponse(<String, dynamic>{
            'subject_capabilities': <Map<String, dynamic>>[],
            'topic_capabilities': [
              {
                'topic_id': 'vital_signs',
                'accuracy': 0.5,
                'speed_score': 0.5,
                'confidence_gap': 0.2,
                'consistency_score': 0.5,
                'priority_score': 0.5,
              },
            ],
            'dimension_capabilities': <Map<String, dynamic>>[],
          });
        }
        if (request.url.path == '/api/nursing/diagnostic/start') {
          return _jsonResponse({
            'questions': [
              {
                'id': 2,
                'subject_id': 'nursing',
                'topic_id': 'vital_signs',
                'concept_tag': 'pulse',
                'difficulty': 1,
                'cognitive_level': 'remember',
                'context': 'clinical',
                'format': 'mcq',
                'question': 'Q2',
                'options': ['A) Pulse', 'B) Rate', 'C) Rhythm', 'D) Volume'],
                'correct_answer': 'A',
                'explanation': 'Exp',
                'source': 'Tabers',
                'verification_status': 'verified',
              },
            ],
          });
        }
        return http.Response.bytes(utf8.encode('Not found'), 404);
      });

      await tester.pumpWidget(
        MaterialApp(
          home: NursingResultsScreen(
            attempts: const [_attempt],
            api: NursingApiService(client: client),
            storage: NursingStorageService(),
          ),
        ),
      );
      await tester.pumpAndSettle();

      await tester.tap(find.text('Try Again'));
      await tester.pumpAndSettle();

      expect(find.byType(NursingQuizScreen), findsOneWidget);
      expect(find.byType(NursingResultsScreen), findsNothing);
    });
  });
}
