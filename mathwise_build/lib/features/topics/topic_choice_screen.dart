/// Topic Choice Screen
///
/// Research basis:
/// - Deci & Ryan (2000): Autonomy is a core psychological need [^23].
///   Presenting "Learn Concept" and "Practice Problems" as equal choices
///   supports self-regulated learning. The student decides their entry point.
///
/// - Cognitive Load Theory: Two large cards = 2 chunks. Easily processed.
///   No secondary options (quiz, flashcards, video) to avoid decision paralysis.
///
/// - Bruner (1966): Some students need more pictorial exposure before practice;
///   others are ready for abstract retrieval. Two paths respect individual differences [^5].
///
/// ADR-010 Decisions: D2, D3
library;

import 'package:flutter/material.dart';

import '../../core/constants/app_colors.dart';
import '../../shared/widgets/top_app_bar.dart';
import '../concept/concept_content_screen.dart';
import '../practice/practice_question_screen.dart';

class TopicChoiceScreen extends StatelessWidget {
  const TopicChoiceScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: const MathWiseAppBar(showBackButton: true),
      body: SingleChildScrollView(
        padding: const EdgeInsets.fromLTRB(24, 16, 24, 120),
        child: Column(
          children: [
            _buildHeader(context),
            const SizedBox(height: 40),
            Row(
              children: [
                Expanded(
                  child: _ModeCard(
                    icon: Icons.import_contacts,
                    title: '\u{1F4D8} Learn Concept',
                    description: 'Master the foundations with visual guides and step-by-step examples.',
                    buttonText: 'START LEARNING',
                    color: AppColors.primary,
                    onTap: () => Navigator.of(context).push(
                      MaterialPageRoute<void>(builder: (_) => const ConceptContentScreen()),
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: _ModeCard(
                    icon: Icons.edit_square,
                    title: '\u{270F}\u{FE0F} Practice Problems',
                    description: 'Test your skills with interactive exercises and real-time feedback.',
                    buttonText: 'START PRACTICE',
                    color: AppColors.secondary,
                    onTap: () => Navigator.of(context).push(
                      MaterialPageRoute<void>(builder: (_) => const PracticeQuestionScreen()),
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 40),
            // Decorative element: low-opacity pictorial cue.
            // Rationale: Priming effect — triangle icon activates relevant schemas.
            const Opacity(
              opacity: 0.2,
              child: Icon(
                Icons.change_history,
                size: 120,
                color: AppColors.primaryContainer,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader(BuildContext context) {
    return Column(
      children: [
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          decoration: BoxDecoration(
            color: AppColors.surfaceContainerLow,
            borderRadius: BorderRadius.circular(20),
          ),
          child: Row(
            children: [
              const Icon(Icons.arrow_back, color: AppColors.primary, size: 18),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  'Geometry Foundations'.toUpperCase(),
                  style: Theme.of(context).textTheme.labelLarge?.copyWith(
                    color: AppColors.primary,
                    letterSpacing: 0.1,
                  ),
                  overflow: TextOverflow.ellipsis,
                  maxLines: 1,
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),
        Text('Triangles', style: Theme.of(context).textTheme.displayLarge),
        const SizedBox(height: 20),
        SizedBox(
          width: 300,
          child: Column(
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'YOUR PROGRESS',
                    style: Theme.of(context).textTheme.labelLarge?.copyWith(
                      color: AppColors.onSurfaceVariant,
                    ),
                  ),
                  Text(
                    '65%',
                    style: Theme.of(context).textTheme.displaySmall?.copyWith(
                      color: AppColors.primary,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              ClipRRect(
                borderRadius: BorderRadius.circular(8),
                child: const LinearProgressIndicator(
                  value: 0.65,
                  minHeight: 10,
                  backgroundColor: AppColors.surfaceContainer,
                  valueColor: AlwaysStoppedAnimation(AppColors.primaryContainer),
                ),
              ),
              const SizedBox(height: 8),
              Text(
                "Keep going! You're almost ready for the quiz.",
                style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                  color: AppColors.onSurfaceVariant,
                ),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _ModeCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final String description;
  final String buttonText;
  final Color color;
  final VoidCallback onTap;

  const _ModeCard({
    required this.icon,
    required this.title,
    required this.description,
    required this.buttonText,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: Container(
        padding: const EdgeInsets.all(32),
        decoration: BoxDecoration(
          color: AppColors.surfaceContainerLowest,
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.04),
              blurRadius: 20,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Column(
          children: [
            Container(
              width: 80,
              height: 80,
              decoration: BoxDecoration(
                color: color.withValues(alpha: 0.1),
                shape: BoxShape.circle,
              ),
              child: Icon(icon, size: 40, color: color),
            ),
            const SizedBox(height: 24),
            Text(
              title,
              style: Theme.of(context).textTheme.displayMedium?.copyWith(fontSize: 22),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 12),
            Text(
              description,
              style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                color: AppColors.onSurfaceVariant,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 24),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
              decoration: BoxDecoration(
                color: color,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(
                buttonText,
                style: Theme.of(context).textTheme.labelLarge?.copyWith(
                  color: Colors.white,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
