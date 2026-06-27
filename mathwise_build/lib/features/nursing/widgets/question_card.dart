import 'package:flutter/material.dart';

import '../models/nursing_question.dart';
import 'explanation_card.dart';
import 'option_button.dart';

/// Displays a single nursing MCQ stem, options, feedback, and trust metadata.
class QuestionCard extends StatelessWidget {
  final NursingQuestion question;
  final int? questionNumber;
  final int? totalQuestions;
  final String? selectedAnswer;
  final ValueChanged<String>? onSelect;
  final bool showFeedback;
  final bool readOnly;
  final VoidCallback? onReport;

  const QuestionCard({
    super.key,
    required this.question,
    this.questionNumber,
    this.totalQuestions,
    this.selectedAnswer,
    this.onSelect,
    this.showFeedback = false,
    this.readOnly = false,
    this.onReport,
  });

  String get _meta {
    final parts = <String>[
      if (questionNumber != null && totalQuestions != null)
        'Q$questionNumber/$totalQuestions',
      question.cognitiveLevel,
      question.context,
    ];
    return parts.join(' • ');
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    _meta,
                    style: Theme.of(context).textTheme.labelSmall,
                  ),
                ),
                if (onReport != null)
                  IconButton(
                    icon: const Icon(Icons.flag_outlined, size: 20),
                    tooltip: 'Report question',
                    onPressed: onReport,
                  ),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              question.question,
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 16),
            ...question.options.map((opt) {
              final value = opt.isNotEmpty ? opt[0] : '';
              return OptionButton(
                option: opt,
                isSelected: selectedAnswer == value,
                isCorrect: value == question.correctAnswer,
                showFeedback: showFeedback,
                onTap: readOnly || showFeedback
                    ? null
                    : () => onSelect?.call(value),
              );
            }),
            if (showFeedback) ...[
              const SizedBox(height: 16),
              ExplanationCard(
                explanation: question.explanation,
                correctAnswer: question.correctAnswer,
              ),
            ],
            const SizedBox(height: 12),
            _TrustRow(
              source: question.source,
              verifiedBy: question.verifiedBy,
              lastReviewed: question.lastReviewed,
            ),
          ],
        ),
      ),
    );
  }
}

class _TrustRow extends StatelessWidget {
  final String source;
  final String? verifiedBy;
  final String? lastReviewed;

  const _TrustRow({
    required this.source,
    this.verifiedBy,
    this.lastReviewed,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return ExpansionTile(
      tilePadding: EdgeInsets.zero,
      title: Text(
        'Source & verification',
        style: theme.textTheme.labelSmall?.copyWith(
              color: theme.colorScheme.primary,
            ),
      ),
      children: [
        Align(
          alignment: Alignment.centerLeft,
          child: Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Source: $source', style: theme.textTheme.bodySmall),
                if (verifiedBy != null)
                  Text('Verified by: $verifiedBy',
                      style: theme.textTheme.bodySmall),
                if (lastReviewed != null)
                  Text('Last reviewed: $lastReviewed',
                      style: theme.textTheme.bodySmall),
              ],
            ),
          ),
        ),
      ],
    );
  }
}
