/// Class Selection Screen
///
/// Research basis:
/// - Deci & Ryan (2000): Autonomy is a core psychological need [^23].
///   Allowing the student to choose their grade (vs. auto-assigning)
///   supports intrinsic motivation and self-regulated learning.
///
/// - Sweller (1988): Six class cards fit within working memory limits [^1][^2].
///   Each card presents exactly 3 chunks: grade number, subject description,
///   and progress bar. No secondary information (teacher name, school) is shown.
///
/// - Elliot & Maier (2014): Blue reduces anxiety; green signals growth [^12][^14].
///   Progress bars use green for in-progress, blue for active, gray for untouched.
///
/// ADR-010 Decisions: D3, D6
library;

import 'package:flutter/material.dart';
import '../../core/constants/app_colors.dart';
import '../../shared/data/demo_data.dart';
import '../../shared/widgets/top_app_bar.dart';
import '../practice/practice_question_screen.dart';
import '../topics/topics_subtopics_screen.dart';

class ClassSelectionScreen extends StatelessWidget {
  const ClassSelectionScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: const MathWiseAppBar(showBackButton: true),
      body: SingleChildScrollView(
        padding: const EdgeInsets.fromLTRB(24, 16, 24, 120),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Welcome back, Alex!', style: Theme.of(context).textTheme.displayLarge),
            const SizedBox(height: 8),
            Text(
              'Pick your current grade to continue your journey through the universe of mathematics.',
              style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                color: AppColors.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: 32),
            // Six class cards: chunking limit respected (Miller 1956) [^2].
            ...DemoData.studentClasses.asMap().entries.expand((entry) {
              final i = entry.key;
              final c = entry.value;
              return [
                _ClassCard(
                  grade: c.grade,
                  subtitle: c.subtitle,
                  icon: _iconFromString(c.icon),
                  iconBg: _iconBgForIndex(i),
                  iconColor: _iconColorForIndex(i),
                  progress: c.progress,
                  progressColor: _progressColorForIndex(i),
                  progressLabel: c.progressLabel,
                  onTap: () => Navigator.of(context).push(
                    MaterialPageRoute<void>(builder: (_) => const TopicsSubtopicsScreen()),
                  ),
                ),
                if (i < DemoData.studentClasses.length - 1)
                  const SizedBox(height: 12),
              ];
            }),
            const SizedBox(height: 32),
            // Promo banner: daily challenge cue for habit formation.
            // Rationale: Lally et al. (2010) — fixed cues build habits [^17].
            _buildPromoBanner(context),
          ],
        ),
      ),
    );
  }

  Widget _buildPromoBanner(BuildContext context) {
    return Row(
      children: [
        Expanded(
          flex: 2,
          child: Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: AppColors.primaryContainer,
              borderRadius: BorderRadius.circular(24),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'DAILY CHALLENGE',
                  style: Theme.of(context).textTheme.labelLarge?.copyWith(
                    color: AppColors.onPrimaryContainer.withValues(alpha: 0.8),
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Master Pythagoras today',
                  style: Theme.of(context).textTheme.displaySmall?.copyWith(
                    color: AppColors.onPrimaryContainer,
                  ),
                ),
                const SizedBox(height: 16),
                ElevatedButton(
                  onPressed: () => Navigator.of(context).push(
                    MaterialPageRoute<void>(builder: (_) => const PracticeQuestionScreen()),
                  ),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.surfaceContainerLowest,
                    foregroundColor: AppColors.primary,
                    padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                  ),
                  child: const Text('Start Now'),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(width: 16),
        Expanded(
          child: Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: AppColors.secondaryContainer,
              borderRadius: BorderRadius.circular(24),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Icon(Icons.emoji_events, color: AppColors.onSecondaryContainer, size: 32),
                const SizedBox(height: 12),
                Text(
                  '12',
                  style: Theme.of(context).textTheme.displayLarge?.copyWith(
                    color: AppColors.onSecondaryContainer,
                    fontSize: 36,
                  ),
                ),
                Text(
                  'Streak Days',
                  style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                    color: AppColors.onSecondaryContainer,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Keep going!',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: AppColors.onSecondaryContainer,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}

IconData _iconFromString(String name) {
  switch (name) {
    case 'functions':
      return Icons.functions;
    case 'calculate':
      return Icons.calculate;
    case 'category':
      return Icons.category;
    case 'code':
      return Icons.code;
    case 'analytics':
      return Icons.analytics;
    case 'change_history':
      return Icons.change_history;
    default:
      return Icons.school;
  }
}

Color _iconBgForIndex(int index) {
  switch (index) {
    case 0:
      return AppColors.primaryFixed;
    case 1:
      return AppColors.secondaryContainer;
    case 2:
      return AppColors.tertiaryContainer.withValues(alpha: 0.2);
    case 3:
      return AppColors.primaryFixedDim.withValues(alpha: 0.3);
    case 4:
      return AppColors.secondaryFixedDim.withValues(alpha: 0.2);
    case 5:
      return AppColors.tertiaryFixed.withValues(alpha: 0.2);
    default:
      return AppColors.surfaceContainer;
  }
}

Color _iconColorForIndex(int index) {
  switch (index) {
    case 0:
      return AppColors.primary;
    case 1:
      return AppColors.secondary;
    case 2:
      return AppColors.tertiary;
    case 3:
      return AppColors.primaryContainer;
    case 4:
      return AppColors.secondary;
    case 5:
      return AppColors.tertiary;
    default:
      return AppColors.onSurface;
  }
}

Color _progressColorForIndex(int index) {
  switch (index) {
    case 0:
      return AppColors.secondary;
    case 1:
      return AppColors.primary;
    default:
      return AppColors.outline;
  }
}

class _ClassCard extends StatelessWidget {
  final String grade;
  final String subtitle;
  final IconData icon;
  final Color iconBg;
  final Color iconColor;
  final double progress;
  final Color progressColor;
  final String progressLabel;
  final VoidCallback? onTap;

  const _ClassCard({
    required this.grade,
    required this.subtitle,
    required this.icon,
    required this.iconBg,
    required this.iconColor,
    required this.progress,
    required this.progressColor,
    required this.progressLabel,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(24),
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: AppColors.surfaceContainerLowest,
          borderRadius: BorderRadius.circular(24),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.04),
              blurRadius: 20,
              offset: const Offset(0, 4),
            ),
          ],
          border: Border.all(color: Colors.transparent),
        ),
        child: Row(
          children: [
            Container(
              width: 56,
              height: 56,
              decoration: BoxDecoration(
                color: iconBg,
                borderRadius: BorderRadius.circular(16),
              ),
              child: Icon(icon, color: iconColor, size: 28),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(grade, style: Theme.of(context).textTheme.displaySmall),
                  const SizedBox(height: 2),
                  Text(
                    subtitle,
                    style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                      color: AppColors.onSurfaceVariant,
                      fontSize: 14,
                    ),
                  ),
                ],
              ),
            ),
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  progressLabel,
                  style: Theme.of(context).textTheme.labelLarge?.copyWith(
                    color: progress > 0 ? progressColor : AppColors.onSurfaceVariant,
                  ),
                ),
                const SizedBox(height: 6),
                SizedBox(
                  width: 80,
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(4),
                    child: LinearProgressIndicator(
                      value: progress,
                      minHeight: 6,
                      backgroundColor: AppColors.surfaceContainerHigh,
                      valueColor: AlwaysStoppedAnimation(progressColor),
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(width: 8),
            const Icon(Icons.chevron_right, color: AppColors.outline),
          ],
        ),
      ),
    );
  }
}
