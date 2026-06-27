import 'package:flutter/material.dart';

/// Shows the explanation and correct answer after answering a question.
class ExplanationCard extends StatelessWidget {
  final String explanation;
  final String correctAnswer;

  const ExplanationCard({
    super.key,
    required this.explanation,
    required this.correctAnswer,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      color: Colors.teal.shade50,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.lightbulb_outline, color: Colors.teal.shade700),
                const SizedBox(width: 8),
                Text(
                  'Explanation',
                  style: Theme.of(context).textTheme.titleSmall?.copyWith(
                        color: Colors.teal.shade900,
                        fontWeight: FontWeight.bold,
                      ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              'Correct answer: $correctAnswer',
              style: TextStyle(
                fontWeight: FontWeight.w600,
                color: Colors.teal.shade900,
              ),
            ),
            const SizedBox(height: 8),
            Text(explanation),
          ],
        ),
      ),
    );
  }
}
