import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mathwise/core/constants/app_theme.dart';

/// Pumps a widget wrapped in MaterialApp with the app's theme.
/// Use this instead of bare MaterialApp to ensure theme-dependent
/// widgets render correctly in tests.
Future<void> pumpWithTheme(WidgetTester tester, Widget widget) async {
  await tester.pumpWidget(
    MaterialApp(
      theme: AppTheme.lightTheme,
      home: widget,
    ),
  );
  await tester.pumpAndSettle();
}

/// Sets a large tablet-sized viewport to prevent overflow errors
/// in widget tests for complex screens.
void setLargeViewport(WidgetTester tester) {
  tester.view.physicalSize = const Size(2400, 3200);
  tester.view.devicePixelRatio = 1.0;
  addTearDown(tester.view.reset);
}
