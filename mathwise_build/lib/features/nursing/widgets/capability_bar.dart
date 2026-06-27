import 'package:flutter/material.dart';

/// Visual bar for accuracy or priority score.
class CapabilityBar extends StatelessWidget {
  final String label;
  final double value; // 0.0 to 1.0
  final Color? color;

  const CapabilityBar({
    super.key,
    required this.label,
    required this.value,
    this.color,
  });

  @override
  Widget build(BuildContext context) {
    final clamped = value.clamp(0.0, 1.0);
    final barColor = color ?? Theme.of(context).colorScheme.primary;

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(child: Text(label)),
              Text('${(clamped * 100).round()}%'),
            ],
          ),
          const SizedBox(height: 6),
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: clamped,
              minHeight: 8,
              backgroundColor: barColor.withValues(alpha: 0.12),
              valueColor: AlwaysStoppedAnimation<Color>(barColor),
            ),
          ),
        ],
      ),
    );
  }
}
