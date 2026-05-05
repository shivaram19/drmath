/// Curriculum Grid Screen
///
/// Research basis:
/// - Gobet et al. (2001): Grid layouts support spatial chunking [^3].
///   The 2×2 topic tile grid allows students to see all sub-topics in one glance,
///   reducing search time compared to vertical lists.
///
/// - Sweller (1988): Split-attention effect [^1]. Each tile integrates icon,
///   title, and status into a single visual unit. No separate legend required.
///
/// - Dweck (2006): Growth mindset [^13]. "Mastered" and "In Progress" labels
///   frame learning as ongoing. "Next Up" (not "Locked") frames future content
///   as achievable.
///
/// ADR-010 Decisions: D6, D3

import 'package:flutter/material.dart';
import '../../core/constants/app_colors.dart';
import '../../shared/widgets/top_app_bar.dart';
import '../practice/practice_question_screen.dart';
import '../topics/topic_choice_screen.dart';

class CurriculumGridScreen extends StatelessWidget {
  const CurriculumGridScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: const MathWiseAppBar(showBackButton: true),
      body: SingleChildScrollView(
        padding: const EdgeInsets.fromLTRB(24, 16, 24, 120),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildHero(context),
            const SizedBox(height: 32),
            _ChapterRow(
              chapter: 'Chapter 1',
              title: 'Algebraic Thinking',
              icon: Icons.functions,
              progress: 1.0,
              isCompleted: true,
            ),
            const SizedBox(height: 12),
            _ExpandedChapterGrid(),
            const SizedBox(height: 12),
            _ChapterRow(
              chapter: 'Chapter 3',
              title: 'Statistics',
              icon: Icons.calculate,
              isLocked: true,
            ),
            const SizedBox(height: 32),
            _buildCTASection(context),
          ],
        ),
      ),
    );
  }

  Widget _buildHero(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
          decoration: BoxDecoration(
            color: AppColors.primaryContainer.withOpacity(0.2),
            borderRadius: BorderRadius.circular(20),
          ),
          child: Text(
            'Grade 8 Curriculum',
            style: Theme.of(context).textTheme.labelLarge?.copyWith(
              color: AppColors.primary,
            ),
          ),
        ),
        const SizedBox(height: 12),
        Text('Geometry Journey', style: Theme.of(context).textTheme.displayLarge),
        const SizedBox(height: 8),
        Text(
          'Master the world of shapes and structures through intuitive visualizations and guided challenges.',
          style: Theme.of(context).textTheme.headlineMedium?.copyWith(
            color: AppColors.onSurfaceVariant,
          ),
        ),
      ],
    );
  }

  Widget _buildCTASection(BuildContext context) {
    return Row(
      children: [
        Expanded(
          child: Container(
            height: 200,
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: AppColors.primaryContainer,
              borderRadius: BorderRadius.circular(16),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Practice Challenge',
                      style: Theme.of(context).textTheme.displaySmall?.copyWith(
                        color: Colors.white,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Test your skills with the Weekly Geometry Battle.',
                      style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                        color: Colors.white.withOpacity(0.8),
                      ),
                    ),
                  ],
                ),
                ElevatedButton(
                  onPressed: () {
                    Navigator.of(context).push(
                      MaterialPageRoute(builder: (_) => const PracticeQuestionScreen()),
                    );
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.white,
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
            height: 200,
            padding: const EdgeInsets.all(24),
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
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Visual Glossary', style: Theme.of(context).textTheme.displaySmall),
                    const SizedBox(height: 4),
                    Text(
                      'Interactive definitions for all geometric terms.',
                      style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                        color: AppColors.onSurfaceVariant,
                      ),
                    ),
                  ],
                ),
                Row(
                  children: [
                    Container(
                      width: 40,
                      height: 40,
                      decoration: BoxDecoration(
                        color: AppColors.surfaceContainer,
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: const Icon(Icons.menu_book, color: AppColors.primary),
                    ),
                    const SizedBox(width: 8),
                    Container(
                      width: 40,
                      height: 40,
                      decoration: BoxDecoration(
                        color: AppColors.surfaceContainer,
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: const Icon(Icons.search, color: AppColors.primary),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}

class _ChapterRow extends StatelessWidget {
  final String chapter;
  final String title;
  final IconData icon;
  final double? progress;
  final bool isCompleted;
  final bool isLocked;

  const _ChapterRow({
    required this.chapter,
    required this.title,
    required this.icon,
    this.progress,
    this.isCompleted = false,
    this.isLocked = false,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
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
      child: Row(
        children: [
          Container(
            width: 48,
            height: 48,
            decoration: BoxDecoration(
              color: isCompleted
                  ? AppColors.secondaryContainer
                  : isLocked
                      ? AppColors.surfaceContainerHighest.withOpacity(0.3)
                      : AppColors.surfaceContainerLow,
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(
              icon,
              color: isCompleted
                  ? AppColors.secondary
                  : isLocked
                      ? AppColors.outline
                      : AppColors.primary,
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  chapter,
                  style: Theme.of(context).textTheme.labelLarge?.copyWith(
                    color: isCompleted ? AppColors.secondary : AppColors.outline,
                  ),
                ),
                const SizedBox(height: 2),
                Text(title, style: Theme.of(context).textTheme.displaySmall),
              ],
            ),
          ),
          if (progress != null)
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  '${(progress! * 100).toInt()}% Complete',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: AppColors.onSurfaceVariant,
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
                      backgroundColor: AppColors.outlineVariant,
                      valueColor: AlwaysStoppedAnimation(
                        isCompleted ? AppColors.secondary : AppColors.primary,
                      ),
                    ),
                  ),
                ),
              ],
            )
          else
            Icon(
              isLocked ? Icons.lock : Icons.chevron_right,
              color: AppColors.outline,
            ),
        ],
      ),
    );
  }
}

class _ExpandedChapterGrid extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.surfaceContainerLow,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.04),
            blurRadius: 20,
            offset: const Offset(0, 4),
          ),
        ],
        border: Border.all(color: AppColors.primaryContainer.withOpacity(0.3)),
      ),
      child: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: AppColors.surfaceContainerLowest,
              borderRadius: const BorderRadius.vertical(top: Radius.circular(16)),
              border: Border(
                bottom: BorderSide(color: AppColors.primaryContainer.withOpacity(0.1)),
              ),
            ),
            child: Row(
              children: [
                Container(
                  width: 48,
                  height: 48,
                  decoration: BoxDecoration(
                    color: AppColors.primaryContainer,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Icon(Icons.architecture, color: Colors.white),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Chapter 2',
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
                      '45% Complete',
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: AppColors.onSurfaceVariant,
                      ),
                    ),
                    const SizedBox(height: 6),
                    SizedBox(
                      width: 80,
                      child: ClipRRect(
                        borderRadius: BorderRadius.circular(4),
                        child: LinearProgressIndicator(
                          value: 0.45,
                          minHeight: 6,
                          backgroundColor: AppColors.outlineVariant,
                          valueColor: const AlwaysStoppedAnimation(AppColors.primary),
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(width: 8),
                const Icon(Icons.expand_less, color: AppColors.primary),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(16),
            child: GridView.count(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              crossAxisCount: 2,
              mainAxisSpacing: 12,
              crossAxisSpacing: 12,
              childAspectRatio: 1.4,
              children: [
                _TopicTile(
                  title: 'Lines',
                  icon: Icons.linear_scale,
                  isCompleted: true,
                  onTap: () {
                    Navigator.of(context).push(
                      MaterialPageRoute(builder: (_) => const TopicChoiceScreen()),
                    );
                  },
                ),
                _TopicTile(
                  title: 'Angles',
                  icon: Icons.text_rotation_angleup,
                  isCompleted: true,
                  onTap: () {
                    Navigator.of(context).push(
                      MaterialPageRoute(builder: (_) => const TopicChoiceScreen()),
                    );
                  },
                ),
                _TopicTile(
                  title: 'Triangles',
                  icon: Icons.change_history,
                  isCurrent: true,
                  onTap: () {
                    Navigator.of(context).push(
                      MaterialPageRoute(builder: (_) => const TopicChoiceScreen()),
                    );
                  },
                ),
                _TopicTile(
                  title: 'Circles',
                  icon: Icons.panorama_fish_eye,
                  isLocked: true,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _TopicTile extends StatelessWidget {
  final String title;
  final IconData icon;
  final bool isCompleted;
  final bool isCurrent;
  final bool isLocked;
  final VoidCallback? onTap;

  const _TopicTile({
    required this.title,
    required this.icon,
    this.isCompleted = false,
    this.isCurrent = false,
    this.isLocked = false,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: isLocked ? null : onTap,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: AppColors.surfaceContainerLowest,
          borderRadius: BorderRadius.circular(12),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.04),
              blurRadius: 8,
              offset: const Offset(0, 2),
            ),
          ],
          border: isCurrent
              ? Border.all(color: AppColors.primaryContainer.withOpacity(0.3))
              : null,
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Container(
                  width: 36,
                  height: 36,
                  decoration: BoxDecoration(
                    color: isCurrent
                        ? AppColors.primaryContainer
                        : AppColors.surfaceDim.withOpacity(0.3),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Icon(
                    icon,
                    color: isCurrent ? Colors.white : AppColors.onSurfaceVariant,
                    size: 20,
                  ),
                ),
                Icon(
                  isCompleted
                      ? Icons.check_circle
                      : isLocked
                          ? Icons.lock
                          : Icons.play_circle,
                  color: isCompleted
                      ? AppColors.secondary
                      : isCurrent
                          ? AppColors.primary
                          : AppColors.outline,
                  size: 18,
                ),
              ],
            ),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontWeight: FontWeight.w600,
                    fontSize: 15,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  isCompleted
                      ? 'Mastered'
                      : isCurrent
                          ? 'In Progress'
                          : 'Next Up',
                  style: TextStyle(
                    fontSize: 11,
                    color: isCurrent ? AppColors.primary : AppColors.onSurfaceVariant,
                    fontWeight: isCurrent ? FontWeight.w500 : FontWeight.normal,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
