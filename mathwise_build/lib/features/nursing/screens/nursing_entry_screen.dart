import 'package:flutter/material.dart';

import '../services/nursing_api_service.dart';
import '../services/nursing_storage_service.dart';
import '../widgets/loading_state.dart';
import 'nursing_disclaimer_screen.dart';
import 'nursing_home_screen.dart';
import 'nursing_onboarding_screen.dart';

/// Module gateway that routes first-time users through disclaimer and onboarding.
///
/// The main MathWise home screen navigates here. This screen reads persisted
/// flags and decides whether to show the disclaimer, the onboarding flow, or
/// the nursing home screen directly.
class NursingEntryScreen extends StatefulWidget {
  final NursingApiService? api;
  final NursingStorageService? storage;

  const NursingEntryScreen({super.key, this.api, this.storage});

  @override
  State<NursingEntryScreen> createState() => _NursingEntryScreenState();
}

class _NursingEntryScreenState extends State<NursingEntryScreen> {
  late final NursingStorageService _storage =
      widget.storage ?? NursingStorageService();
  String? _error;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _route());
  }

  Future<void> _route() async {
    try {
      final disclaimerAccepted = await _storage.getDisclaimerAccepted();
      final onboardingSeen = await _storage.getOnboardingSeen();

      if (!mounted) return;

      Widget destination;
      if (!disclaimerAccepted) {
        destination = NursingDisclaimerScreen(
          storage: widget.storage,
          api: widget.api,
        );
      } else if (!onboardingSeen) {
        destination = NursingOnboardingScreen(
          storage: widget.storage,
          api: widget.api,
        );
      } else {
        destination = NursingHomeScreen(
          api: widget.api,
          storage: widget.storage,
        );
      }

      await Navigator.of(context).pushReplacement(
        MaterialPageRoute<void>(builder: (_) => destination),
      );
    } catch (e) {
      if (mounted) setState(() => _error = e.toString());
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _error != null
          ? Center(child: Text('Error: $_error'))
          : const Center(child: NursingLoading()),
    );
  }
}
