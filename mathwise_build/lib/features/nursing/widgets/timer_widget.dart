import 'package:flutter/material.dart';

/// Countdown or elapsed timer display for quiz modes.
class TimerWidget extends StatelessWidget {
  final int seconds;
  final bool isCountdown;

  const TimerWidget({
    super.key,
    required this.seconds,
    this.isCountdown = true,
  });

  String get _formatted {
    final effective = isCountdown ? seconds : seconds.abs();
    final m = (effective ~/ 60).toString().padLeft(2, '0');
    final s = (effective % 60).toString().padLeft(2, '0');
    return '$m:$s';
  }

  Color get _color {
    if (seconds <= 0) return Colors.red;
    if (seconds < 300) return Colors.red.shade700;
    if (seconds < 900) return Colors.orange;
    return Colors.orange.shade700;
  }

  @override
  Widget build(BuildContext context) {
    return Semantics(
      label: 'Time remaining: $_formatted',
      child: Padding(
        padding: const EdgeInsets.only(right: 16),
        child: Text(
          _formatted,
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: _color,
          ),
        ),
      ),
    );
  }
}
