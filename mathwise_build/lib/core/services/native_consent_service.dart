import 'dart:convert';

import 'package:shared_preferences/shared_preferences.dart';

/// Manages the native app's DPDPA-aligned analytics consent record.
///
/// This is deliberately separate from the web PWA consent (`mw_privacy_consent`)
/// because consent must be specific to the processing context.
class NativeConsentService {
  static const String _key = 'mw_native_consent';
  static const String version = '2026-05-05';

  final SharedPreferences? _prefs;

  NativeConsentService({SharedPreferences? prefs}) : _prefs = prefs;

  Future<SharedPreferences> get _preferences async {
    return _prefs ?? await SharedPreferences.getInstance();
  }

  /// Whether the user has explicitly accepted analytics for the native app.
  Future<bool> hasConsent() async {
    final record = await _getRecord();
    return record != null &&
        record['version'] == version &&
        record['accepted'] == true;
  }

  /// Whether the user has ever answered the native consent prompt.
  Future<bool> hasRecordedAnswer() async {
    final record = await _getRecord();
    return record != null && record['version'] == version;
  }

  /// Persist the user's choice. [accepted] must be `true` or `false`.
  Future<void> setConsent(bool accepted) async {
    final prefs = await _preferences;
    final record = {
      'version': version,
      'accepted': accepted,
      'timestamp': DateTime.now().toUtc().toIso8601String(),
    };
    await prefs.setString(_key, jsonEncode(record));
  }

  Future<Map<String, dynamic>?> _getRecord() async {
    final prefs = await _preferences;
    final raw = prefs.getString(_key);
    if (raw == null || raw.isEmpty) return null;
    try {
      return jsonDecode(raw) as Map<String, dynamic>;
    } catch (_) {
      return null;
    }
  }
}
