import 'dart:convert';
import 'package:flutter/services.dart';

/// Loads the English → Telugu medical glossary from bundled JSON.
class GlossaryService {
  Map<String, String> _glossary = {};

  Future<void> load() async {
    try {
      final raw = await rootBundle.loadString('assets/nursing/glossary.json');
      final data = jsonDecode(raw) as Map<String, dynamic>;
      _glossary = data.map((k, v) => MapEntry(k.toLowerCase(), v as String));
    } catch (_) {
      _glossary = {};
    }
  }

  String? lookup(String term) {
    return _glossary[term.toLowerCase()];
  }

  Map<String, String> get all => Map.unmodifiable(_glossary);
}
