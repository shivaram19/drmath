import 'package:flutter/material.dart';

import '../services/nursing_api_service.dart';
import '../services/nursing_storage_service.dart';
import '../widgets/nursing_app_bar.dart';
import 'nursing_home_screen.dart';
import 'nursing_onboarding_screen.dart';

/// First-launch disclaimer for the nursing module.
class NursingDisclaimerScreen extends StatefulWidget {
  final NursingStorageService? storage;
  final NursingApiService? api;

  const NursingDisclaimerScreen({super.key, this.storage, this.api});

  @override
  State<NursingDisclaimerScreen> createState() => _NursingDisclaimerScreenState();
}

class _NursingDisclaimerScreenState extends State<NursingDisclaimerScreen> {
  late final NursingStorageService _storage = widget.storage ?? NursingStorageService();
  bool _accepted = false;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _checkExisting();
  }

  Future<void> _checkExisting() async {
    final accepted = await _storage.getDisclaimerAccepted();
    if (!mounted) return;
    if (accepted) {
      _goHome();
    } else {
      setState(() => _loading = false);
    }
  }

  Future<void> _accept() async {
    await _storage.setDisclaimerAccepted(true);
    if (!mounted) return;

    final onboardingSeen = await _storage.getOnboardingSeen();
    if (!mounted) return;
    if (onboardingSeen) {
      _goHome();
    } else {
      Navigator.of(context).pushReplacement(
        MaterialPageRoute<void>(
          builder: (_) => NursingOnboardingScreen(
            storage: widget.storage,
            api: widget.api,
          ),
        ),
      );
    }
  }

  void _goHome() {
    Navigator.of(context).pushReplacement(
      MaterialPageRoute<void>(
        builder: (_) => NursingHomeScreen(
          api: widget.api,
          storage: widget.storage,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    return Scaffold(
      appBar: const NursingAppBar(
        title: 'Important — Read Before You Begin',
        showBackButton: false,
      ),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Expanded(
              child: SingleChildScrollView(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Nursing Exam Practice',
                      style: Theme.of(context).textTheme.headlineSmall,
                    ),
                    const SizedBox(height: 16),
                    const _Bullet(
                      text:
                          'This app is for exam preparation and educational practice only.',
                    ),
                    const _Bullet(
                      text:
                          'It is not medical advice, diagnosis, or treatment.',
                    ),
                    const _Bullet(
                      text:
                          'Always verify answers with the official INC/GNM syllabus and your institution.',
                    ),
                    const _Bullet(
                      text:
                          'Content is reviewed but not guaranteed to be error-free. Report any questionable question.',
                    ),
                  ],
                ),
              ),
            ),
            const Divider(),
            CheckboxListTile(
              title: const Text('I understand and agree'),
              value: _accepted,
              onChanged: (value) => setState(() => _accepted = value ?? false),
              controlAffinity: ListTileControlAffinity.leading,
            ),
            const SizedBox(height: 12),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _accepted ? _accept : null,
                child: const Text('Continue'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _Bullet extends StatelessWidget {
  final String text;

  const _Bullet({required this.text});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('• ', style: TextStyle(fontSize: 18)),
          Expanded(child: Text(text)),
        ],
      ),
    );
  }
}
