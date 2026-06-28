import 'package:flutter_test/flutter_test.dart';
import 'package:mathwise/core/services/native_consent_service.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  group('NativeConsentService', () {
    setUp(() {
      SharedPreferences.setMockInitialValues({});
    });

    test('has no consent before an answer is recorded', () async {
      final service = NativeConsentService();
      expect(await service.hasConsent(), isFalse);
      expect(await service.hasRecordedAnswer(), isFalse);
    });

    test('records acceptance', () async {
      final service = NativeConsentService();
      await service.setConsent(true);
      expect(await service.hasConsent(), isTrue);
      expect(await service.hasRecordedAnswer(), isTrue);
    });

    test('records decline', () async {
      final service = NativeConsentService();
      await service.setConsent(false);
      expect(await service.hasConsent(), isFalse);
      expect(await service.hasRecordedAnswer(), isTrue);
    });

    test('ignores stale consent records from a different version', () async {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(
        'mw_native_consent',
        '{"version":"2026-01-01","accepted":true,"timestamp":"2026-01-01T00:00:00Z"}',
      );
      final service = NativeConsentService(prefs: prefs);
      expect(await service.hasConsent(), isFalse);
      expect(await service.hasRecordedAnswer(), isFalse);
    });
  });
}
