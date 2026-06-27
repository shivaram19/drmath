import 'dart:convert';

import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:mathwise/features/nursing/models/attempt.dart';
import 'package:mathwise/features/nursing/models/nursing_question.dart';
import 'package:mathwise/features/nursing/services/nursing_api_exception.dart';
import 'package:mathwise/features/nursing/services/nursing_api_service.dart';

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
  'options': ['36-37°C', '38°C', '35°C', '39°C'],
  'correct_answer': 'A',
  'explanation': 'Normal body temperature is around 37°C.',
  'source': 'Tabers',
  'verification_status': 'verified',
  'verified_by': 'Nurse Educator',
  'last_reviewed': '2025-01-01',
  'telugu_hint': 'సాధారణ శరీర ఉష్ణోగ్రత 37°C చుట్టూ ఉంటుంది.',
};

const _analysisJson = {
  'subject_capabilities': [
    {
      'subject_id': 'nursing',
      'accuracy': 0.8,
      'speed_score': 0.9,
      'confidence_gap': 0.1,
      'consistency_score': 0.85,
      'priority_score': 0.2,
    },
  ],
  'topic_capabilities': [
    {
      'topic_id': 'vital_signs',
      'accuracy': 0.75,
      'speed_score': 0.8,
      'confidence_gap': 0.15,
      'consistency_score': 0.7,
      'priority_score': 0.3,
    },
  ],
  'dimension_capabilities': [
    {
      'cognitive_level': 'remember',
      'accuracy': 0.9,
      'speed_score': 0.95,
      'confidence_gap': 0.05,
      'consistency_score': 0.9,
      'priority_score': 0.1,
    },
  ],
};

http.Response _jsonResponse(Object body, {int statusCode = 200}) {
  return http.Response.bytes(
    utf8.encode(jsonEncode(body)),
    statusCode,
    headers: {'content-type': 'application/json; charset=utf-8'},
  );
}

class _FakeAssetBundle extends AssetBundle {
  final String fallback;

  _FakeAssetBundle({required this.fallback});

  @override
  Future<String> loadString(String key, {bool cache = true}) async => fallback;

  @override
  Future<ByteData> load(String key) async => ByteData(0);
}

void main() {
  group('NursingApiService contract tests', () {
    test('fetchQuestions parses a list of questions', () async {
      final client = MockClient((request) async {
        expect(request.method, 'GET');
        expect(request.url.path, '/api/nursing/questions');
        return _jsonResponse([_questionJson]);
      });

      final service = NursingApiService(client: client);
      final questions = await service.fetchQuestions();

      expect(questions, hasLength(1));
      expect(questions.first, isA<NursingQuestion>());
      expect(questions.first.id, 1);
      expect(questions.first.correctAnswer, 'A');
    });

    test('startDiagnostic parses questions from response', () async {
      final client = MockClient((request) async {
        expect(request.method, 'POST');
        expect(request.url.path, '/api/nursing/diagnostic/start');
        return _jsonResponse({'questions': [_questionJson]});
      });

      final service = NursingApiService(client: client);
      final questions = await service.startDiagnostic(numQuestions: 1);

      expect(questions, hasLength(1));
      expect(questions.first.topicId, 'vital_signs');
    });

    test('analyzeAttempts parses capability analysis', () async {
      final client = MockClient((request) async {
        expect(request.method, 'POST');
        expect(request.url.path, '/api/nursing/analyze');
        return _jsonResponse(_analysisJson);
      });

      final service = NursingApiService(client: client);
      final analysis = await service.analyzeAttempts([
        const Attempt(
          questionId: 1,
          selectedOption: 'A',
          isCorrect: true,
          timeSeconds: 12.0,
          confidence: 4,
          subjectId: 'nursing',
          topicId: 'vital_signs',
          cognitiveLevel: 'remember',
        ),
      ]);

      expect(analysis.subjectCapabilities, hasLength(1));
      expect(analysis.topicCapabilities.first.topicId, 'vital_signs');
      expect(analysis.topicCapabilities.first.accuracy, closeTo(0.75, 0.001));
    });

    test('retries on 500 and succeeds on second attempt', () async {
      var attempts = 0;
      final client = MockClient((request) async {
        attempts++;
        if (attempts == 1) {
          return http.Response.bytes(
            utf8.encode('Internal Server Error'),
            500,
          );
        }
        return _jsonResponse([_questionJson]);
      });

      final service = NursingApiService(client: client);
      final questions = await service.fetchQuestions();

      expect(attempts, 2);
      expect(questions, hasLength(1));
    });

    test('gives up after max retries and throws NursingApiException', () async {
      final client = MockClient((request) async {
        return http.Response.bytes(
          utf8.encode('Internal Server Error'),
          500,
        );
      });

      final service = NursingApiService(
        client: client,
        baseUrl: 'https://example.com',
      );

      await expectLater(
        service.fetchStatus(),
        throwsA(
          isA<NursingApiException>().having(
            (e) => e.statusCode,
            'statusCode',
            500,
          ),
        ),
      );
    });

    test('fetchQuestions falls back to bundled seed on API failure', () async {
      final client = MockClient((request) async {
        return http.Response.bytes(
          utf8.encode('Unavailable'),
          503,
        );
      });
      final bundle = _FakeAssetBundle(
        fallback: jsonEncode([_questionJson]),
      );

      final service = NursingApiService(
        client: client,
        assetBundle: bundle,
      );
      final questions = await service.fetchQuestions(subjectId: 'nursing');

      expect(questions, hasLength(1));
      expect(questions.first.subjectId, 'nursing');
    });
  });
}
