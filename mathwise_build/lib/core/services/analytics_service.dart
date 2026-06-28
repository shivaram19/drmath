import 'dart:convert';

import 'package:http/http.dart' as http;

import 'campaign_service.dart';
import 'native_consent_service.dart';

/// Sends anonymous, consent-gated events to the Nursing analytics endpoint.
///
/// Events are fire-and-forget: failures are swallowed so the app never blocks
/// on telemetry.
class AnalyticsService {
  AnalyticsService({
    http.Client? client,
    NativeConsentService? consentService,
    String baseUrl = 'https://drmath.trelolabs.com',
  })  : _client = client ?? http.Client(),
        _consentService = consentService ?? NativeConsentService(),
        _baseUrl = baseUrl;

  final http.Client _client;
  final NativeConsentService _consentService;
  final String _baseUrl;

  /// Track an arbitrary event if native consent has been given.
  Future<void> trackEvent(String event, Map<String, dynamic> metadata) async {
    if (!await _consentService.hasConsent()) return;

    final payload = {
      'event': event,
      'timestamp': DateTime.now().toUtc().toIso8601String(),
      'consent_version': NativeConsentService.version,
      'metadata': metadata,
    };

    try {
      await _client.post(
        Uri.parse('$_baseUrl/api/nursing/analytics'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(payload),
      );
    } catch (_) {
      // Telemetry must not crash or block the UI.
    }
  }

  /// Convenience helper for the first-open attribution event.
  Future<void> trackAppFirstOpen(CampaignAttribution? attribution) async {
    final metadata = <String, dynamic>{
      'platform': 'android',
    };
    if (attribution != null) {
      metadata.addAll(attribution.toMetadata());
    }
    await trackEvent('app_first_open', metadata);
  }
}
