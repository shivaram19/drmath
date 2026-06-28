import 'package:flutter_test/flutter_test.dart';
import 'package:mathwise/core/services/campaign_service.dart';
import 'package:referrer/referrer.dart';

class _FakeReferrer extends Referrer {
  _FakeReferrer(this._info);

  final ReferrerInfo? _info;

  @override
  Future<ReferrerInfo?> getReferrer() async => _info;
}

void main() {
  group('CampaignService', () {
    test('returns null when referrer is unavailable', () async {
      final service = CampaignService(referrer: _FakeReferrer(null));
      final attribution = await service.getAttribution();
      expect(attribution, isNull);
    });

    test('parses UTM params from referrer URI', () async {
      final info = ReferrerInfo(
        referrer: Uri.parse(
          'https://drmath.trelolabs.com/nursing/?utm_source=whatsapp_share'
          '&utm_medium=share_text&utm_campaign=nursing_full_app_install'
          '&utm_content=score_share',
        ),
        referrerName: 'com.android.chrome',
        referrerBrowswer: 'Chrome',
      );
      final service = CampaignService(referrer: _FakeReferrer(info));
      final attribution = await service.getAttribution();

      expect(attribution, isNotNull);
      expect(attribution!.utmSource, 'whatsapp_share');
      expect(attribution.utmMedium, 'share_text');
      expect(attribution.utmCampaign, 'nursing_full_app_install');
      expect(attribution.utmContent, 'score_share');
      expect(attribution.referrerName, 'com.android.chrome');
      expect(attribution.referrerBrowser, 'Chrome');
      expect(
        attribution.referrerUrl,
        contains('utm_campaign=nursing_full_app_install'),
      );
    });

    test('metadata removes empty fields', () async {
      final info = ReferrerInfo(
        referrer: Uri.parse('https://example.com/?utm_source=test'),
        referrerName: null,
        referrerBrowswer: null,
      );
      final service = CampaignService(referrer: _FakeReferrer(info));
      final attribution = (await service.getAttribution())!;
      final metadata = attribution.toMetadata();

      expect(metadata['utm_source'], 'test');
      expect(metadata.containsKey('utm_medium'), isFalse);
      expect(metadata.containsKey('referrer_name'), isFalse);
    });
  });
}
