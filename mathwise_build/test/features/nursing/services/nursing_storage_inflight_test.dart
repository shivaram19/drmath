import 'package:flutter_test/flutter_test.dart';
import 'package:mathwise/features/nursing/services/nursing_storage_service.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  group('NursingStorageService in-flight session', () {
    setUp(() {
      SharedPreferences.setMockInitialValues({});
    });

    test('saves, loads, and clears an in-flight session', () async {
      final storage = NursingStorageService();
      await storage.saveInflightSession({
        'mode': 'mock',
        'subject_id': 'nursing',
        'topic_id': 'vital_signs',
        'current_index': 3,
        'selected_answers': {'0': 'A', '1': 'B'},
        'marked_for_review': [2],
        'remaining_seconds': 1800,
        'questions': <Map<String, dynamic>>[],
      });

      final session = await storage.loadInflightSession();
      expect(session, isNotNull);
      expect(session!['mode'], 'mock');
      expect(session['current_index'], 3);
      expect(session['selected_answers'], {'0': 'A', '1': 'B'});

      await storage.clearInflightSession();
      final cleared = await storage.loadInflightSession();
      expect(cleared, isNull);
    });

    test('returns null when no in-flight session exists', () async {
      final storage = NursingStorageService();
      final session = await storage.loadInflightSession();
      expect(session, isNull);
    });
  });
}
