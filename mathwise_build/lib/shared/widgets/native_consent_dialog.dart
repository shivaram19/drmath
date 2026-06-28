import 'package:flutter/material.dart';

/// A one-time DPDPA-aligned consent dialog shown on the native app's first open.
///
/// Returns `true` if the user agrees to anonymous first-open analytics, or
/// `false` if they decline.
Future<bool> showNativeConsentDialog(BuildContext context) async {
  final result = await showDialog<bool>(
    context: context,
    barrierDismissible: false,
    builder: (context) {
      return AlertDialog(
        title: const Text('Help us improve MathWise'),
        content: const Text(
          'Can we collect anonymous info about how you found the app? '
          'This never includes your name, phone number, or location.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Not now'),
          ),
          TextButton(
            onPressed: () => Navigator.of(context).pop(true),
            child: const Text('Yes, agree'),
          ),
        ],
      );
    },
  );
  return result ?? false;
}
