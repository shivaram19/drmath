/// Curriculum Stepper Screen
///
/// Research basis:
/// - Bruner (1966): Linear progression through concepts mirrors the
///   scaffolding principle — each step builds on the previous [^5].
///
/// - Vygotsky (1978): ZPD requires sequential challenge [^8].
///   Locked steps represent "not yet reachable" content; the current step
///   is the edge of the student's ZPD.
///
/// - Sweller (1988): The vertical path line integrates spatial progress
///   into a single visual chunk, reducing split-attention [^1].
///
/// - Dweck (2006): Completed steps are green (growth); current step is
///   blue (focus); locked steps are gray (future potential, not failure) [^13].
///
/// ADR-010 Decisions: D2, D6, D3

import 'package:flutter/material.dart';
import '../../core/constants/app_colors.dart';
import '../../shared/widgets/top_app_bar.dart';
import '../concept/concept_content_screen.dart';
import '../practice/practice_question_screen.dart';
import '../topics/topic_choice_screen.dart';

class CurriculumStepperScreen extends StatelessWidget {
  const CurriculumStepperScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: const MathWiseAppBar(showBackButton: true),
      body: SingleChildScrollView(
        padding: const EdgeInsets.fromLTRB(24, 16, 24, 120),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildHeader(context),
            const SizedBox(height: 32),
            _buildStepperCard(context),
            const SizedBox(height: 32),
            Row(
              children: [
                Expanded(
                  child: _TipCard(
                    icon: Icons.lightbulb,
                    title: 'Study Tip',
                    description: 'Geometry is visual! Try sketching each concept in your notebook to strengthen your spatial reasoning skills.',
                    color: AppColors.primaryFixed,
                    borderColor: AppColors.primaryContainer.withOpacity(0.2),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: _TipCard(
                    icon: Icons.workspace_premium,
                    title: 'Milestone Reward',
                    description: 'Finish the "Angles" module to unlock the "Protractor Pro" badge and 50 bonus wisdom points.',
                    color: AppColors.tertiaryFixed.withOpacity(0.2),
                    borderColor: AppColors.tertiaryFixed.withOpacity(0.3),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Text(
              'CONTINUE LEARNING',
              style: Theme.of(context).textTheme.labelLarge?.copyWith(
                color: AppColors.primary,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(width: 12),
            Container(
              width: 48,
              height: 4,
              decoration: BoxDecoration(
                color: AppColors.primaryContainer,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        Text('Geometry Mastery', style: Theme.of(context).textTheme.displayLarge),
        const SizedBox(height: 8),
        Text(
          'Master the fundamental properties of shapes and spaces through our guided linear path.',
          style: Theme.of(context).textTheme.headlineMedium?.copyWith(
            color: AppColors.onSurfaceVariant,
          ),
        ),
      ],
    );
  }

  Widget _buildStepperCard(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.surfaceContainerLowest,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.04),
            blurRadius: 20,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: AppColors.surfaceContainerLow,
              borderRadius: const BorderRadius.vertical(top: Radius.circular(16)),
            ),
            child: Row(
              children: [
                Container(
                  width: 56,
                  height: 56,
                  decoration: BoxDecoration(
                    color: AppColors.primary,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Icon(Icons.category, color: Colors.white, size: 28),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'CHAPTER 2',
                        style: Theme.of(context).textTheme.labelLarge?.copyWith(
                          color: AppColors.primary,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text('Geometry', style: Theme.of(context).textTheme.displaySmall),
                    ],
                  ),
                ),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    Text(
                      '25% Complete',
                      style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                        color: AppColors.secondary,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    const SizedBox(height: 6),
                    SizedBox(
                      width: 100,
                      child: ClipRRect(
                        borderRadius: BorderRadius.circular(4),
                        child: LinearProgressIndicator(
                          value: 0.25,
                          minHeight: 6,
                          backgroundColor: AppColors.outlineVariant,
                          valueColor: const AlwaysStoppedAnimation(AppColors.secondary),
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(24),
            child: Stack(
              children: [
                // Vertical path line: spatial integration of progress.
                // Rationale: Sweller (1988) — integrated visual reduces split-attention [^1].
                Positioned(
                  left: 23,
                  top: 30,
                  bottom: 30,
                  child: Container(
                    width: 2,
                    decoration: BoxDecoration(
                      border: Border(
                        left: BorderSide(
                          color: AppColors.primaryContainer.withOpacity(0.3),
                          width: 2,
                          style: BorderStyle.solid,
                        ),
                      ),
                    ),
                  ),
                ),
                Column(
                  children: [
                    _StepItem(
                      title: 'Lines',
                      description: 'Understanding parallel, perpendicular, and intersecting lines within a 2D plane.',
                      status: StepStatus.completed,
                    ),
                    _StepItem(
                      title: 'Angles',
                      description: 'Exploring acute, obtuse, and right angles. Introduction to protractor measurement techniques.',
                      status: StepStatus.current,
                    ),
                    _StepItem(
                      title: 'Triangles',
                      description: 'Types of triangles: Equilateral, Isosceles, and Scalene. The internal angle sum theorem.',
                      status: StepStatus.locked,
                    ),
                    _StepItem(
                      title: 'Circles',
                      description: 'Calculating circumference and area. Introduction to the concept of Pi and radius properties.',
                      status: StepStatus.locked,
                      isLast: true,
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

enum StepStatus { completed, current, locked }

class _StepItem extends StatelessWidget {
  final String title;
  final String description;
  final StepStatus status;
  final bool isLast;

  const _StepItem({
    required this.title,
    required this.description,
    required this.status,
    this.isLast = false,
  });

  @override
  Widget build(BuildContext context) {
    final isCompleted = status == StepStatus.completed;
    final isCurrent = status == StepStatus.current;
    final isLocked = status == StepStatus.locked;

    return Padding(
      padding: EdgeInsets.only(bottom: isLast ? 0 : 24),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Step circle: 48dp touch target + visual status.
          Container(
            width: 48,
            height: 48,
            decoration: BoxDecoration(
              color: isCompleted
                  ? AppColors.secondary
                  : isCurrent
                      ? AppColors.primary
                      : AppColors.surfaceDim,
              shape: BoxShape.circle,
              border: Border.all(color: Colors.white, width: 4),
              boxShadow: [
                if (isCurrent)
                  BoxShadow(
                    color: AppColors.primary.withOpacity(0.3),
                    blurRadius: 20,
                  ),
              ],
            ),
            child: Icon(
              isCompleted
                  ? Icons.check
                  : isCurrent
                      ? Icons.play_arrow
                      : Icons.lock,
              color: isCompleted || isCurrent ? Colors.white : AppColors.outline,
              size: 24,
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: isCurrent
                    ? Colors.white
                    : isCompleted
                        ? AppColors.surfaceContainerHigh.withOpacity(0.3)
                        : AppColors.surfaceContainerLow,
                borderRadius: BorderRadius.circular(16),
                border: isCurrent
                    ? Border.all(color: AppColors.primaryContainer.withOpacity(0.2))
                    : null,
                boxShadow: isCurrent
                    ? [
                        BoxShadow(
                          color: Colors.black.withOpacity(0.06),
                          blurRadius: 12,
                          offset: const Offset(0, 4),
                        ),
                      ]
                    : null,
              ),
              child: Opacity(
                opacity: isLocked ? 0.6 : 1.0,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          title,
                          style: Theme.of(context).textTheme.displaySmall?.copyWith(
                            fontSize: 18,
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                          decoration: BoxDecoration(
                            color: isCompleted
                                ? AppColors.secondaryContainer
                                : isCurrent
                                    ? AppColors.primaryContainer.withOpacity(0.2)
                                    : AppColors.outlineVariant,
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: Text(
                            isCompleted
                                ? 'Completed'
                                : isCurrent
                                    ? 'Current'
                                    : 'Locked',
                            style: Theme.of(context).textTheme.labelLarge?.copyWith(
                              color: isCompleted
                                  ? AppColors.onSecondaryContainer
                                  : isCurrent
                                      ? AppColors.onPrimaryContainer
                                      : AppColors.onSurfaceVariant,
                              fontSize: 10,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text(
                      description,
                      style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                        color: AppColors.onSurfaceVariant,
                        fontSize: 14,
                      ),
                    ),
                    if (isCompleted) ...[
                      const SizedBox(height: 12),
                      TextButton.icon(
                        onPressed: () {
                          Navigator.of(context).push(
                            MaterialPageRoute(builder: (_) => const ConceptContentScreen()),
                          );
                        },
                        icon: const Icon(Icons.arrow_forward, size: 16),
                        label: const Text('Review Lesson'),
                        style: TextButton.styleFrom(
                          foregroundColor: AppColors.primary,
                          padding: EdgeInsets.zero,
                          textStyle: const TextStyle(fontWeight: FontWeight.bold),
                        ),
                      ),
                    ] else if (isCurrent) ...[
                      const SizedBox(height: 12),
                      Row(
                        children: [
                          ElevatedButton(
                            onPressed: () {
                              Navigator.of(context).push(
                                MaterialPageRoute(builder: (_) => const TopicChoiceScreen()),
                              );
                            },
                            style: ElevatedButton.styleFrom(
                              backgroundColor: AppColors.primary,
                              foregroundColor: AppColors.onPrimary,
                              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                            ),
                            child: const Text('Resume Journey'),
                          ),
                          const SizedBox(width: 12),
                          OutlinedButton(
                            onPressed: () {
                              Navigator.of(context).push(
                                MaterialPageRoute(builder: (_) => const PracticeQuestionScreen()),
                              );
                            },
                            style: OutlinedButton.styleFrom(
                              foregroundColor: AppColors.onSurfaceVariant,
                              side: const BorderSide(color: AppColors.outlineVariant),
                              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                            ),
                            child: const Text('Quick Quiz'),
                          ),
                        ],
                      ),
                    ],
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _TipCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final String description;
  final Color color;
  final Color borderColor;

  const _TipCard({
    required this.icon,
    required this.title,
    required this.description,
    required this.color,
    required this.borderColor,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: color,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: borderColor),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: AppColors.primary, size: 24),
          const SizedBox(height: 8),
          Text(
            title,
            style: Theme.of(context).textTheme.displaySmall?.copyWith(fontSize: 18),
          ),
          const SizedBox(height: 4),
          Text(
            description,
            style: Theme.of(context).textTheme.bodyLarge?.copyWith(
              color: AppColors.onSurfaceVariant,
              fontSize: 14,
            ),
          ),
        ],
      ),
    );
  }
}
