import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:mathwise/features/nursing/screens/nursing_home_screen.dart';
import 'package:mathwise/features/nursing/screens/nursing_quiz_screen.dart';
import 'package:mathwise/features/nursing/screens/nursing_subject_screen.dart';
import 'package:mathwise/features/nursing/services/nursing_api_service.dart';
import 'package:mathwise/features/nursing/widgets/loading_state.dart';

http.Response _jsonResponse(Object body, {int statusCode = 200}) {
  return http.Response.bytes(
    utf8.encode(jsonEncode(body)),
    statusCode,
    headers: {'content-type': 'application/json; charset=utf-8'},
  );
}

void main() {
  group('NursingHomeScreen', () {
    testWidgets('renders subjects and question count after loading',
        (tester) async {
      final client = MockClient((request) async {
        if (request.url.path == '/api/nursing/status') {
          return _jsonResponse({'questions': 130});
        }
        if (request.url.path == '/api/nursing/topics') {
          return _jsonResponse({
            'subjects': ['nursing_fundamentals', 'medical_surgical'],
            'counts': {'nursing_fundamentals': 60, 'medical_surgical': 70},
          });
        }
        return http.Response.bytes(utf8.encode('Not found'), 404);
      });

      await tester.pumpWidget(
        MaterialApp(
          home: NursingHomeScreen(api: NursingApiService(client: client)),
        ),
      );
      await tester.pump();
      await tester.pump(const Duration(seconds: 1));

      expect(find.text('Nursing Practice'), findsOneWidget);
      expect(find.text('Subjects (130 questions)'), findsOneWidget);
      expect(find.text('NURSING FUNDAMENTALS'), findsOneWidget);
      expect(find.text('MEDICAL SURGICAL'), findsOneWidget);
    });

    testWidgets('shows error state when API fails', (tester) async {
      final client = MockClient((request) async {
        throw const SocketException('No internet');
      });

      await tester.pumpWidget(
        MaterialApp(
          home: NursingHomeScreen(api: NursingApiService(client: client)),
        ),
      );
      await tester.pump();
      await tester.pump(const Duration(seconds: 5));

      expect(find.byType(NursingError), findsOneWidget);
    });

    testWidgets('diagnostic button navigates to quiz screen', (tester) async {
      final client = MockClient((request) async {
        if (request.url.path == '/api/nursing/status') {
          return _jsonResponse({'questions': 130});
        }
        if (request.url.path == '/api/nursing/topics') {
          return _jsonResponse(<String, dynamic>{
            'subjects': <String>[],
            'counts': <String, dynamic>{},
          });
        }
        if (request.url.path == '/api/nursing/diagnostic/start') {
          return _jsonResponse({
            'questions': [
              {
                'id': 1,
                'subject_id': 'nursing',
                'topic_id': 'vital_signs',
                'concept_tag': 'temperature',
                'difficulty': 1,
                'cognitive_level': 'remember',
                'context': 'clinical',
                'format': 'mcq',
                'question': 'Q1',
                'options': ['A) Option A', 'B) Option B', 'C) Option C', 'D) Option D'],
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
          home: NursingHomeScreen(api: NursingApiService(client: client)),
        ),
      );
      await tester.pump();
      await tester.pump(const Duration(seconds: 1));

      await tester.tap(find.text('Diagnostic'));
      await tester.pump();
      await tester.pump(const Duration(seconds: 1));

      expect(find.byType(NursingQuizScreen), findsOneWidget);
    });

    testWidgets('subject tile navigates to subject screen', (tester) async {
      final client = MockClient((request) async {
        if (request.url.path == '/api/nursing/status') {
          return _jsonResponse({'questions': 130});
        }
        if (request.url.path == '/api/nursing/topics') {
          return _jsonResponse({
            'subjects': ['nursing_fundamentals'],
            'counts': {'nursing_fundamentals': 60},
          });
        }
        return http.Response.bytes(utf8.encode('Not found'), 404);
      });

      await tester.pumpWidget(
        MaterialApp(
          home: NursingHomeScreen(api: NursingApiService(client: client)),
        ),
      );
      await tester.pump();
      await tester.pump(const Duration(seconds: 1));

      await tester.tap(find.byKey(const Key('subject_tile_nursing_fundamentals')));
      await tester.pump();
      await tester.pump(const Duration(seconds: 1));

      expect(find.byType(NursingSubjectScreen), findsOneWidget);
    });
  });
}
