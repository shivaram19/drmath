import 'package:flutter/material.dart';

import '../services/nursing_storage_service.dart';
import '../widgets/language_toggle.dart';
import '../widgets/nursing_app_bar.dart';
import 'nursing_disclaimer_screen.dart';

/// Language and data preferences for the nursing module.
class NursingSettingsScreen extends StatefulWidget {
  const NursingSettingsScreen({super.key});

  @override
  State<NursingSettingsScreen> createState() => _NursingSettingsScreenState();
}

class _NursingSettingsScreenState extends State<NursingSettingsScreen> {
  final _storage = NursingStorageService();
  bool _hasPendingAnalysis = false;
  String _language = 'en';

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final pending = await _storage.hasPendingAnalysis;
    final language = await _storage.getLanguage();
    if (mounted) {
      setState(() {
        _hasPendingAnalysis = pending;
        _language = language;
      });
    }
  }

  Future<void> _clearProgress() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Clear all progress?'),
        content: const Text(
          'This will delete your attempts, capability map, and pending analysis. This cannot be undone.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () => Navigator.of(context).pop(true),
            child: const Text('Clear'),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      await _storage.clearAll();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Progress cleared')),
        );
        _load();
      }
    }
  }

  Future<void> _showDisclaimer() async {
    await Navigator.of(context).push(
      MaterialPageRoute<void>(
        builder: (_) => const NursingDisclaimerScreen(),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: const NursingAppBar(title: 'Settings'),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Card(
            child: Column(
              children: [
                ListTile(
                  leading: const Icon(Icons.language),
                  title: const Text('Language'),
                  subtitle: Text(_language == 'te' ? 'Telugu' : 'English'),
                  trailing: const LanguageToggle(),
                ),
                const Divider(height: 1),
                ListTile(
                  leading: Icon(
                    _hasPendingAnalysis ? Icons.cloud_off : Icons.cloud_done,
                    color: _hasPendingAnalysis ? Colors.orange : Colors.green,
                  ),
                  title: const Text('Offline analysis'),
                  subtitle: Text(
                    _hasPendingAnalysis
                        ? 'Some results are waiting to sync.'
                        : 'All results are synced.',
                  ),
                ),
                const Divider(height: 1),
                ListTile(
                  leading: const Icon(Icons.delete_outline),
                  title: const Text('Clear progress'),
                  onTap: _clearProgress,
                ),
                const Divider(height: 1),
                ListTile(
                  leading: const Icon(Icons.info_outline),
                  title: const Text('Disclaimer'),
                  onTap: _showDisclaimer,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
