import 'package:flutter_test/flutter_test.dart';
import 'package:mathwise/features/nursing/models/attempt.dart';
import 'package:mathwise/features/nursing/services/nursing_storage_service.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  group('NursingStorageService', () {
    late NursingStorageService storage;

    setUp(() {
      SharedPreferences.setMockInitialValues({});
      storage = NursingStorageService();
    });

    test('queues and loads pending analysis', () async {
      final attempts = [
        _attempt(subjectId: 'anatomy_physiology', topicId: 'ap_cardiovascular'),
      ];

      expect(await storage.hasPendingAnalysis, isFalse);

      await storage.queuePendingAnalysis(attempts);

      expect(await storage.hasPendingAnalysis, isTrue);
      final loaded = await storage.loadPendingAnalysis();
      expect(loaded.length, equals(1));
      expect(loaded.first.subjectId, equals('anatomy_physiology'));
    });

    test('clears pending analysis', () async {
      await storage.queuePendingAnalysis([_attempt()]);
      await storage.clearPendingAnalysis();

      expect(await storage.hasPendingAnalysis, isFalse);
      expect(await storage.loadPendingAnalysis(), isEmpty);
    });

    test('appends and retrieves attempts', () async {
      await storage.appendAttempts([_attempt(topicId: 'ap_respiratory')]);
      await storage.appendAttempts([_attempt(topicId: 'ap_cardiovascular')]);

      final loaded = await storage.loadAttempts();
      expect(loaded.length, equals(2));
    });

    test('caps attempts at 200', () async {
      final many = List.generate(250, (_) => _attempt());
      await storage.saveAttempts(many);

      final loaded = await storage.loadAttempts();
      expect(loaded.length, equals(200));
    });
  });
}

Attempt _attempt({
  String subjectId = 'anatomy_physiology',
  String topicId = 'ap_cardiovascular',
}) {
  return Attempt(
    questionId: 1,
    selectedOption: 'A',
    isCorrect: false,
    timeSeconds: 30,
    confidence: 3,
    subjectId: subjectId,
    topicId: topicId,
    cognitiveLevel: 'remember',
  );
}
