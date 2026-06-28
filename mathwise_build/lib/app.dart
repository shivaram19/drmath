import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'core/constants/app_theme.dart';
import 'core/services/analytics_service.dart';
import 'core/services/campaign_service.dart';
import 'core/services/native_consent_service.dart';
import 'features/home/home_screen.dart';
import 'shared/widgets/native_consent_dialog.dart';

class MathWiseApp extends StatefulWidget {
  const MathWiseApp({super.key});

  @override
  State<MathWiseApp> createState() => _MathWiseAppState();
}

class _MathWiseAppState extends State<MathWiseApp> {
  final GlobalKey<NavigatorState> _navigatorKey = GlobalKey<NavigatorState>();

  @override
  void initState() {
    super.initState();
    _handleFirstOpenAttribution();
  }

  Future<void> _handleFirstOpenAttribution() async {
    // Wait for the first frame so the navigator key is attached.
    await Future<void>.delayed(Duration.zero);
    if (!mounted) return;

    final prefs = await SharedPreferences.getInstance();
    const firstOpenKey = 'mw_first_open_handled';
    if (prefs.getBool(firstOpenKey) == true) return;

    await prefs.setBool(firstOpenKey, true);

    final consentService = NativeConsentService(prefs: prefs);
    if (!await consentService.hasRecordedAnswer()) {
      final context = _navigatorKey.currentContext;
      if (context == null || !context.mounted) return;
      final accepted = await showNativeConsentDialog(context);
      await consentService.setConsent(accepted);
    }

    if (await consentService.hasConsent()) {
      final attribution = await CampaignService().getAttribution();
      await AnalyticsService().trackAppFirstOpen(attribution);
    }
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      navigatorKey: _navigatorKey,
      title: 'MathWise',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      home: const HomeScreen(),
    );
  }
}
