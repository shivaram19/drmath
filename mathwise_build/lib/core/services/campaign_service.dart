import 'package:referrer/referrer.dart';

/// Best-effort install-open attribution parsed from the platform referrer.
///
/// For side-loaded APKs the browser may supply [Intent.EXTRA_REFERRER] when the
/// user opens the app from the install flow, but this is not guaranteed.
class CampaignAttribution {
  const CampaignAttribution({
    required this.referrerUrl,
    this.utmSource,
    this.utmMedium,
    this.utmCampaign,
    this.utmContent,
    this.referrerName,
    this.referrerBrowser,
  });

  final String? referrerUrl;
  final String? utmSource;
  final String? utmMedium;
  final String? utmCampaign;
  final String? utmContent;
  final String? referrerName;
  final String? referrerBrowser;

  Map<String, dynamic> toMetadata() {
    return {
      'referrer_url': referrerUrl,
      'utm_source': utmSource,
      'utm_medium': utmMedium,
      'utm_campaign': utmCampaign,
      'utm_content': utmContent,
      'referrer_name': referrerName,
      'referrer_browser': referrerBrowser,
    }..removeWhere((_, value) => value == null);
  }
}

/// Reads the platform referrer and parses standard UTM campaign parameters.
class CampaignService {
  CampaignService({Referrer? referrer}) : _referrer = referrer ?? Referrer();

  final Referrer _referrer;

  Future<CampaignAttribution?> getAttribution() async {
    final info = await _referrer.getReferrer();
    if (info == null) return null;

    final uri = info.referrer;
    final referrerUrl = uri?.toString() ?? '';
    final params = uri?.queryParameters ?? {};

    return CampaignAttribution(
      referrerUrl: referrerUrl.isEmpty ? null : referrerUrl,
      utmSource: _nonEmpty(params['utm_source']),
      utmMedium: _nonEmpty(params['utm_medium']),
      utmCampaign: _nonEmpty(params['utm_campaign']),
      utmContent: _nonEmpty(params['utm_content']),
      referrerName: _nonEmpty(info.referrerName),
      referrerBrowser: _nonEmpty(info.referrerBrowswer),
    );
  }

  String? _nonEmpty(String? value) {
    if (value == null || value.trim().isEmpty) return null;
    return value.trim();
  }
}
