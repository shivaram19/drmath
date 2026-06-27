import 'dart:convert';

import 'package:shared_preferences/shared_preferences.dart';

import '../models/attempt.dart';

/// Local persistence for nursing progress, preferences, and offline queue.
class NursingStorageService {
  static const String _attemptsKey = 'nursing_attempts';
  static const String _capabilityKey = 'nursing_capability_map';
  static const String _languageKey = 'nursing_language';
  static const String _pendingAnalysisKey = 'nursing_pending_analysis';
  static const String _disclaimerKey = 'nursing_disclaimer_accepted';
  static const String _onboardingKey = 'nursing_onboarding_seen';

  Future<List<Attempt>> loadAttempts() async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getString(_attemptsKey);
    if (raw == null || raw.isEmpty) return [];
    final list = jsonDecode(raw) as List<dynamic>;
    return list.map((e) => Attempt.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<void> saveAttempts(List<Attempt> attempts) async {
    final prefs = await SharedPreferences.getInstance();
    final limited = attempts.length > 200 ? attempts.sublist(attempts.length - 200) : attempts;
    await prefs.setString(_attemptsKey, jsonEncode(limited.map((a) => a.toJson()).toList()));
  }

  Future<void> appendAttempts(List<Attempt> attempts) async {
    final existing = await loadAttempts();
    existing.addAll(attempts);
    await saveAttempts(existing);
  }

  Future<Map<String, dynamic>?> loadCapabilityMap() async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getString(_capabilityKey);
    if (raw == null) return null;
    return jsonDecode(raw) as Map<String, dynamic>;
  }

  Future<void> saveCapabilityMap(Map<String, dynamic> map) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_capabilityKey, jsonEncode(map));
  }

  Future<String> getLanguage() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_languageKey) ?? 'en';
  }

  Future<void> setLanguage(String language) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_languageKey, language);
  }

  /// Stores attempts that could not be analyzed because the device is offline.
  Future<void> queuePendingAnalysis(List<Attempt> attempts) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(
      _pendingAnalysisKey,
      jsonEncode(attempts.map((a) => a.toJson()).toList()),
    );
  }

  /// Retrieves any attempts waiting for online analysis.
  Future<List<Attempt>> loadPendingAnalysis() async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getString(_pendingAnalysisKey);
    if (raw == null || raw.isEmpty) return [];
    final list = jsonDecode(raw) as List<dynamic>;
    return list.map((e) => Attempt.fromJson(e as Map<String, dynamic>)).toList();
  }

  /// Returns true if there are attempts waiting for online analysis.
  Future<bool> get hasPendingAnalysis async {
    final pending = await loadPendingAnalysis();
    return pending.isNotEmpty;
  }

  /// Clears the offline analysis queue, typically after a successful sync.
  Future<void> clearPendingAnalysis() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_pendingAnalysisKey);
  }

  Future<bool> getDisclaimerAccepted() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getBool(_disclaimerKey) ?? false;
  }

  Future<void> setDisclaimerAccepted(bool value) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_disclaimerKey, value);
  }

  Future<bool> getOnboardingSeen() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getBool(_onboardingKey) ?? false;
  }

  Future<void> setOnboardingSeen(bool value) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_onboardingKey, value);
  }

  Future<void> clearAll() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_attemptsKey);
    await prefs.remove(_capabilityKey);
    await prefs.remove(_pendingAnalysisKey);
  }
}
