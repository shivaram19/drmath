import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:mathwise/core/services/analytics_service.dart';
import 'package:mathwise/core/services/campaign_service.dart';
import 'package:mathwise/core/services/native_consent_service.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  group('AnalyticsService', () {
    setUp(() {
      SharedPreferences.setMockInitialValues({});
    });

    test('does not send events when consent is false', () async {
      var requests = 0;
      final client = MockClient((_) async {
        requests++;
        return http.Response('{}', 200);
      });
      final consentService = NativeConsentService();
      await consentService.setConsent(false);
      final service = AnalyticsService(
        client: client,
        consentService: consentService,
        baseUrl: 'https://test.example.com',
      );
      await service.trackEvent('app_first_open', {'platform': 'android'});
      expect(requests, 0);
    });

    test('sends app_first_open with attribution when consent is true', () async {
      http.Request? captured;
      final client = MockClient((request) async {
        captured = request;
        return http.Response('{"status":"recorded"}', 200);
      });
      final consentService = NativeConsentService();
      await consentService.setConsent(true);
      const attribution = CampaignAttribution(
        referrerUrl: 'https://drmath.trelolabs.com/nursing/?utm_source=test',
        utmSource: 'test',
        utmMedium: 'result_cta',
        utmCampaign: 'nursing_full_app_install',
        utmContent: 'after_quiz',
      );
      final service = AnalyticsService(
        client: client,
        consentService: consentService,
        baseUrl: 'https://test.example.com',
      );
      await service.trackAppFirstOpen(attribution);

      expect(captured, isNotNull);
      expect(captured!.url.toString(), 'https://test.example.com/api/nursing/analytics');
      final body = jsonDecode(captured!.body) as Map<String, dynamic>;
      expect(body['event'], 'app_first_open');
      expect(body['consent_version'], NativeConsentService.version);
      final metadata = body['metadata'] as Map<String, dynamic>;
      expect(metadata['platform'], 'android');
      expect(metadata['utm_source'], 'test');
      expect(metadata['utm_campaign'], 'nursing_full_app_install');
      expect(metadata['referrer_url'], contains('utm_source=test'));
    });

    test('swallows HTTP errors without throwing', () async {
      final client = MockClient((_) async => http.Response('error', 500));
      final consentService = NativeConsentService();
      await consentService.setConsent(true);
      final service = AnalyticsService(
        client: client,
        consentService: consentService,
        baseUrl: 'https://test.example.com',
      );
      expect(
        service.trackEvent('test_event', {}),
        completes,
      );
    });
  });
}
