import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:mathwise/features/nursing/models/attempt.dart';
import 'package:mathwise/features/nursing/screens/nursing_pdf_screen.dart';
import 'package:mathwise/features/nursing/services/nursing_api_service.dart';

import '../../../test_helpers.dart';

http.Response _jsonResponse(Object body, {int statusCode = 200}) {
  return http.Response.bytes(
    utf8.encode(jsonEncode(body)),
    statusCode,
    headers: {'content-type': 'application/json; charset=utf-8'},
  );
}

const _attempts = [
  Attempt(
    questionId: 1,
    selectedOption: 'A',
    isCorrect: true,
    timeSeconds: 10,
    confidence: 3,
    subjectId: 'nursing',
    topicId: 'vital_signs',
    cognitiveLevel: 'remember',
  ),
];

void main() {
  group('NursingPdfScreen', () {
    testWidgets('loads weak topics and generates PDF',
        (WidgetTester tester) async {
      final client = MockClient((request) async {
        if (request.url.path == '/api/nursing/analyze') {
          return _jsonResponse(<String, dynamic>{
            'subject_capabilities': <Map<String, dynamic>>[],
            'topic_capabilities': [
              {
                'topic_id': 'vital_signs',
                'accuracy': 0.5,
                'speed_score': 0.5,
                'confidence_gap': 0.0,
                'consistency_score': 0.5,
                'priority_score': 0.5,
              },
            ],
            'dimension_capabilities': <Map<String, dynamic>>[],
          });
        }
        if (request.url.path == '/api/nursing/pdf') {
          return http.Response.bytes(
            utf8.encode('<html><body>Practice PDF</body></html>'),
            200,
            headers: {'content-type': 'text/html; charset=utf-8'},
          );
        }
        return http.Response.bytes(utf8.encode('Not found'), 404);
      });

      await pumpWithTheme(
        tester,
        NursingPdfScreen(
          attempts: _attempts,
          api: NursingApiService(client: client),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Select weak areas to include'), findsOneWidget);
      expect(find.text('vital signs'), findsOneWidget);

      await tester.tap(find.text('Generate Practice PDF'));
      await tester.pumpAndSettle();

      expect(find.text('Practice PDF'), findsOneWidget);

      final copied = <String>[];
      tester.binding.defaultBinaryMessenger.setMockMethodCallHandler(
        SystemChannels.platform,
        (call) async {
          if (call.method == 'Clipboard.setData') {
            copied.add((call.arguments as Map<String, dynamic>)['text'] as String);
          }
          return null;
        },
      );

      await tester.tap(find.text('Copy HTML'));
      await tester.pump();

      expect(copied, contains('<html><body>Practice PDF</body></html>'));
    });
  });
}
