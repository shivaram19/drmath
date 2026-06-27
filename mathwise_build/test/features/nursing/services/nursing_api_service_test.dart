import 'dart:convert';

import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mathwise/features/nursing/models/nursing_question.dart';
import 'package:mathwise/features/nursing/services/nursing_api_exception.dart';
import 'package:mathwise/features/nursing/services/nursing_api_service.dart';

const _sampleQuestions = [
  {
    'id': 1,
    'subject_id': 'anatomy_physiology',
    'topic_id': 'ap_cardiovascular',
    'concept_tag': 'normal blood pressure',
    'difficulty': 1,
    'cognitive_level': 'remember',
    'context': 'theory',
    'format': 'mcq',
    'question': 'What is the normal adult blood pressure?',
    'options': [
      'A) 90/60 mmHg',
      'B) 120/80 mmHg',
      'C) 140/90 mmHg',
      'D) 100/70 mmHg',
    ],
    'correct_answer': 'B',
    'explanation': 'Normal adult BP is approximately 120/80 mmHg.',
    'source': 'INC GNM Syllabus',
    'verification_status': 'reviewed',
  },
  {
    'id': 2,
    'subject_id': 'anatomy_physiology',
    'topic_id': 'ap_respiratory',
    'concept_tag': 'normal respiratory rate',
    'difficulty': 1,
    'cognitive_level': 'remember',
    'context': 'theory',
    'format': 'mcq',
    'question': 'What is the normal adult respiratory rate?',
    'options': [
      'A) 8-10/min',
      'B) 12-20/min',
      'C) 22-28/min',
      'D) 30-40/min',
    ],
    'correct_answer': 'B',
    'explanation': 'Normal adult respiratory rate is 12-20/min.',
    'source': 'INC GNM Syllabus',
    'verification_status': 'reviewed',
  },
];

class _FakeAssetBundle extends CachingAssetBundle {
  @override
  Future<String> loadString(String key, {bool cache = true}) async {
    if (key == 'assets/nursing/nursing_seed_questions.json') {
      return jsonEncode(_sampleQuestions);
    }
    throw ArgumentError('Unexpected asset: $key');
  }

  @override
  Future<ByteData> load(String key) => throw UnimplementedError();
}

void main() {
  group('NursingApiService offline fallback', () {
    test('loads fallback questions when baseUrl is unreachable', () async {
      final service = NursingApiService(
        baseUrl: 'http://localhost:59999', // unlikely to respond
        timeout: const Duration(milliseconds: 100),
        assetBundle: _FakeAssetBundle(),
      );

      final questions = await service.fetchQuestions();

      expect(questions.length, equals(2));
      expect(questions.first, isA<NursingQuestion>());
    });

    test('filters fallback questions by subject and topic', () async {
      final service = NursingApiService(
        baseUrl: 'http://localhost:59999',
        timeout: const Duration(milliseconds: 100),
        assetBundle: _FakeAssetBundle(),
      );

      final questions = await service.fetchQuestions(
        subjectId: 'anatomy_physiology',
        topicId: 'ap_cardiovascular',
      );

      expect(questions.length, equals(1));
      expect(questions.first.topicId, equals('ap_cardiovascular'));
    });

    test('diagnostic falls back to shuffled seed questions', () async {
      final service = NursingApiService(
        baseUrl: 'http://localhost:59999',
        timeout: const Duration(milliseconds: 100),
        assetBundle: _FakeAssetBundle(),
      );

      final questions = await service.startDiagnostic(numQuestions: 1);

      expect(questions.length, equals(1));
    });

    test('throws NursingApiException with isOffline true on timeout',
        () async {
      final service = NursingApiService(
        baseUrl: 'http://localhost:59999',
        timeout: const Duration(milliseconds: 100),
        assetBundle: _FakeAssetBundle(),
      );

      // analyzeAttempts has no fallback, so it should surface the offline error.
      await expectLater(
        () => service.analyzeAttempts([]),
        throwsA(
          isA<NursingApiException>().having(
            (e) => e.isOffline,
            'isOffline',
            isTrue,
          ),
        ),
      );
    });
  });
}
