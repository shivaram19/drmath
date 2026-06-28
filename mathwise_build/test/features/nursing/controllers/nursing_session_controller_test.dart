import 'dart:convert';

import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:mathwise/features/nursing/controllers/nursing_session_controller.dart';
import 'package:mathwise/features/nursing/models/nursing_question.dart';
import 'package:mathwise/features/nursing/services/nursing_api_service.dart';
import 'package:mathwise/features/nursing/services/nursing_storage_service.dart';
import 'package:shared_preferences/shared_preferences.dart';

const _question = NursingQuestion(
  id: 1,
  subjectId: 'nursing',
  topicId: 'vital_signs',
  conceptTag: 'temperature',
  difficulty: 1,
  cognitiveLevel: 'remember',
  context: 'clinical',
  format: 'mcq',
  question: 'Normal body temperature?',
  options: ['36-37°C', '38°C', '35°C', '39°C'],
  correctAnswer: 'A',
  explanation: 'Around 37°C.',
  source: 'Tabers',
  verificationStatus: 'verified',
);

http.Response _jsonResponse(Object body, {int statusCode = 200}) {
  return http.Response.bytes(
    utf8.encode(jsonEncode(body)),
    statusCode,
    headers: {'content-type': 'application/json; charset=utf-8'},
  );
}

class _FakeBundle extends AssetBundle {
  @override
  Future<String> loadString(String key, {bool cache = true}) async =>
      jsonEncode([_question.toJson()]);

  @override
  Future<ByteData> load(String key) async => ByteData(0);
}

void main() {
  group('NursingSessionController', () {
    setUp(() {
      SharedPreferences.setMockInitialValues({});
    });

    test('starts a diagnostic session and loads questions', () async {
      final client = MockClient((request) async {
        return _jsonResponse({
          'questions': [_question.toJson()],
        });
      });
      final controller = NursingSessionController(
        api: NursingApiService(
          client: client,
          assetBundle: _FakeBundle(),
        ),
      );

      var notified = false;
      controller.addListener(() => notified = true);

      await controller.start(mode: QuizMode.diagnostic);

      expect(controller.loading, isFalse);
      expect(controller.error, isNull);
      expect(controller.questions, hasLength(1));
      expect(controller.currentQuestion?.id, _question.id);
      expect(controller.currentQuestion?.question, _question.question);
      expect(notified, isTrue);
    });

    test('selects answers and tracks progress', () async {
      final controller = NursingSessionController();
      await controller.start(mode: QuizMode.diagnostic, questions: [_question]);

      controller.selectAnswer(0, 'A');

      expect(controller.selectedAnswers[0], 'A');
      expect(controller.answeredCount, 1);
      expect(controller.isLastQuestion, isTrue);
    });

    test('marks questions for review', () async {
      final controller = NursingSessionController();
      await controller.start(mode: QuizMode.mock, questions: [_question]);

      controller.toggleMarkForReview(0);
      expect(controller.markedForReview, contains(0));

      controller.toggleMarkForReview(0);
      expect(controller.markedForReview, isNot(contains(0)));
    });

    test('navigates to next question only when answered', () async {
      final controller = NursingSessionController();
      await controller.start(
        mode: QuizMode.diagnostic,
        questions: [_question, _question],
      );

      expect(controller.next(), isFalse);
      controller.selectAnswer(0, 'A');
      expect(controller.next(), isTrue);
      expect(controller.currentIndex, 1);
    });

    test('builds attempts from session', () async {
      final controller = NursingSessionController();
      await controller.start(mode: QuizMode.diagnostic, questions: [_question]);
      controller.selectAnswer(0, 'A');

      final attempts = controller.buildAttempts();

      expect(attempts, hasLength(1));
      expect(attempts.first.questionId, 1);
      expect(attempts.first.isCorrect, isTrue);
    });

    test('persists and restores in-flight session', () async {
      final controller = NursingSessionController();
      await controller.start(mode: QuizMode.mock, questions: [_question]);
      controller.selectAnswer(0, 'A');
      controller.toggleMarkForReview(0);
      controller.goToQuestion(0);

      final restored = NursingSessionController();
      final didRestore = await restored.restoreInflightSession();

      expect(didRestore, isTrue);
      expect(restored.mode, QuizMode.mock);
      expect(restored.questions, hasLength(1));
      expect(restored.selectedAnswers[0], 'A');
      expect(restored.markedForReview, contains(0));
    });

    test('submit clears in-flight session', () async {
      final controller = NursingSessionController();
      await controller.start(mode: QuizMode.diagnostic, questions: [_question]);
      controller.selectAnswer(0, 'A');

      await controller.submit();

      final pending = await controller.restoreInflightSession();
      expect(pending, isFalse);
    });

    test('abandon clears in-flight session', () async {
      final controller = NursingSessionController();
      await controller.start(mode: QuizMode.diagnostic, questions: [_question]);

      await controller.abandon();

      final pending = await controller.restoreInflightSession();
      expect(pending, isFalse);
      expect(controller.hasQuestions, isFalse);
    });
  });
}
