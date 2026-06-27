import 'package:flutter_test/flutter_test.dart';
import 'package:mathwise/features/nursing/services/nursing_session_logger.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  group('NursingSessionLogger', () {
    setUp(() {
      SharedPreferences.setMockInitialValues({});
    });

    test('logs a session and preserves it', () async {
      final logger = NursingSessionLogger();
      await logger.log(
        mode: 'mock',
        attemptsCount: 10,
        score: 0.7,
        weakAreas: ['vital_signs', 'medication'],
      );

      final sessions = await logger.loadAll();
      expect(sessions, hasLength(1));
      expect(sessions.first['mode'], 'mock');
      expect(sessions.first['attempts_count'], 10);
      expect(sessions.first['score'], 0.7);
      expect(sessions.first['weak_areas'], ['vital_signs', 'medication']);
      expect(sessions.first['timestamp'], isNotNull);
    });

    test('evicts oldest entries when max is exceeded', () async {
      final logger = NursingSessionLogger();
      for (var i = 0; i < 102; i++) {
        await logger.log(
          mode: 'mock',
          attemptsCount: i,
          score: 0.5,
          weakAreas: const [],
        );
      }

      final sessions = await logger.loadAll();
      expect(sessions.length, lessThanOrEqualTo(100));
      expect(sessions.first['attempts_count'], 2);
      expect(sessions.last['attempts_count'], 101);
    });
  });
}
