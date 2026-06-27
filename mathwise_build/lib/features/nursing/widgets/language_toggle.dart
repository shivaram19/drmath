import 'package:flutter/material.dart';

import '../services/nursing_storage_service.dart';

/// Toggles UI language between English and Telugu.
class LanguageToggle extends StatefulWidget {
  final ValueChanged<String>? onChanged;

  const LanguageToggle({super.key, this.onChanged});

  @override
  State<LanguageToggle> createState() => _LanguageToggleState();
}

class _LanguageToggleState extends State<LanguageToggle> {
  final _storage = NursingStorageService();
  String _language = 'en';

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final lang = await _storage.getLanguage();
    if (mounted) setState(() => _language = lang);
  }

  Future<void> _toggle() async {
    final next = _language == 'en' ? 'te' : 'en';
    await _storage.setLanguage(next);
    if (mounted) setState(() => _language = next);
    widget.onChanged?.call(next);
  }

  @override
  Widget build(BuildContext context) {
    return TextButton(
      onPressed: _toggle,
      child: Text(
        _language == 'en' ? 'తెలుగు' : 'English',
        style: const TextStyle(fontWeight: FontWeight.w600),
      ),
    );
  }
}
