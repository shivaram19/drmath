import 'dart:convert';

import 'package:shared_preferences/shared_preferences.dart';

/// Logs completed nursing sessions for later correlation analysis.
class NursingSessionLogger {
  static const String _key = 'nursing_sessions';
  static const int _maxEntries = 100;

  Future<void> log({
    required String mode,
    required int attemptsCount,
    required double score,
    required List<String> weakAreas,
  }) async {
    final prefs = await SharedPreferences.getInstance();
    final sessions = _load(prefs);
    sessions.add({
      'timestamp': DateTime.now().toIso8601String(),
      'mode': mode,
      'attempts_count': attemptsCount,
      'score': score,
      'weak_areas': weakAreas,
    });
    while (sessions.length > _maxEntries) {
      sessions.removeAt(0);
    }
    await prefs.setString(
      _key,
      jsonEncode(sessions),
    );
  }

  Future<List<Map<String, dynamic>>> loadAll() async {
    final prefs = await SharedPreferences.getInstance();
    return _load(prefs);
  }

  List<Map<String, dynamic>> _load(SharedPreferences prefs) {
    final raw = prefs.getString(_key);
    if (raw == null || raw.isEmpty) return [];
    final list = jsonDecode(raw) as List<dynamic>;
    return list.cast<Map<String, dynamic>>();
  }
}
