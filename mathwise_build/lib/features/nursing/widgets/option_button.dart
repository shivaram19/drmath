import 'package:flutter/material.dart';

/// A single A/B/C/D answer option with accessibility-friendly touch target.
class OptionButton extends StatelessWidget {
  final String option;
  final bool isSelected;
  final bool isCorrect;
  final bool showFeedback;
  final VoidCallback? onTap;

  const OptionButton({
    super.key,
    required this.option,
    this.isSelected = false,
    this.isCorrect = false,
    this.showFeedback = false,
    this.onTap,
  });

  String get _letter {
    if (option.isEmpty) return '';
    return option[0].toUpperCase();
  }

  Color? get _backgroundColor {
    if (showFeedback && isCorrect) return Colors.green.shade50;
    if (showFeedback && isSelected && !isCorrect) return Colors.red.shade50;
    if (isSelected) return Colors.blue.shade50;
    return null;
  }

  Color? get _foregroundColor {
    if (showFeedback && isCorrect) return Colors.green.shade800;
    if (showFeedback && isSelected && !isCorrect) return Colors.red.shade800;
    if (isSelected) return Colors.blue.shade800;
    return null;
  }

  @override
  Widget build(BuildContext context) {
    return Semantics(
      button: true,
      label: 'Option $_letter',
      selected: isSelected,
      child: Padding(
        padding: const EdgeInsets.only(bottom: 12),
        child: Material(
          color: _backgroundColor ?? Theme.of(context).cardColor,
          borderRadius: BorderRadius.circular(12),
          child: InkWell(
            onTap: showFeedback ? null : onTap,
            borderRadius: BorderRadius.circular(12),
            child: Container(
              constraints: const BoxConstraints(minHeight: 56),
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
              child: Row(
                children: [
                  Container(
                    width: 32,
                    height: 32,
                    alignment: Alignment.center,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: _foregroundColor?.withValues(alpha: 0.12) ??
                          Colors.grey.shade200,
                    ),
                    child: Text(
                      _letter,
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        color: _foregroundColor ?? Colors.grey.shade800,
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      option,
                      style: TextStyle(
                        color: _foregroundColor,
                        fontWeight:
                            isSelected ? FontWeight.w600 : FontWeight.normal,
                      ),
                    ),
                  ),
                  if (showFeedback && isCorrect)
                    const Icon(Icons.check_circle, color: Colors.green)
                  else if (showFeedback && isSelected && !isCorrect)
                    const Icon(Icons.cancel, color: Colors.red),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
