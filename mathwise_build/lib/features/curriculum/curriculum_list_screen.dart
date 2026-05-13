/// Curriculum List Screen
///
/// Research basis:
/// - Gobet et al. (2001): Chunking is the fundamental mechanism of human learning [^3].
///   Progressive disclosure (accordion) presents one chapter chunk at a time,
///   preventing working memory overload.
///
/// - Sweller (1988): Split-attention effect [^1]. We avoid showing all sub-topics
///   simultaneously; only the active chapter expands.
///
/// - Dweck (2006): Growth mindset [^13]. Green "COMPLETE" badges signal
///   "you can grow" rather than "you are done." Locked chapters use gray,
///   not red — avoiding shame-based signaling.
///
/// - Deci & Ryan (2000): Autonomy [^23]. The student chooses which chapter
///   to expand and which sub-topic to resume.
///
/// ADR-010 Decisions: D3, D6
library;

import 'package:flutter/material.dart';
import '../../core/constants/app_colors.dart';
import '../../shared/data/demo_data.dart';
import '../../shared/models/curriculum.dart';

import '../topics/topic_choice_screen.dart';

class CurriculumListScreen extends StatefulWidget {
  const CurriculumListScreen({super.key});

  @override
  State<CurriculumListScreen> createState() => _CurriculumListScreenState();
}

class _CurriculumListScreenState extends State<CurriculumListScreen> {
  String? _expandedChapterId;

  @override
  void initState() {
    super.initState();
    // Auto-expand the first in-progress or unlocked chapter.
    // Rationale: Gobet et al. (2001) — present the active chunk first.
    // A collapsed accordion is invisible; the student cannot discover
    // sub-topics without first guessing the tap affordance.
    final firstOpen = DemoData.grade7Curriculum.firstWhere(
      (ch) => ch.status != TopicStatus.locked,
      orElse: () => DemoData.grade7Curriculum.first,
    );
    _expandedChapterId = firstOpen.id;
  }

  IconData _iconFromString(String name) {
    return switch (name) {
      'pin_drop' => Icons.pin_drop,
      'category' => Icons.category,
      'pie_chart' => Icons.pie_chart,
      'functions' => Icons.functions,
      'architecture' => Icons.architecture,
      'calculate' => Icons.calculate,
      'code' => Icons.code,
      'analytics' => Icons.analytics,
      'change_history' => Icons.change_history,
      _ => Icons.school,
    };
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.fromLTRB(24, 16, 24, 120),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Math Curriculum', style: Theme.of(context).textTheme.displayLarge),
          const SizedBox(height: 8),
          Text(
            'Master mathematical concepts at your own pace with our structured learning path.',
            style: Theme.of(context).textTheme.headlineMedium?.copyWith(
              color: AppColors.onSurfaceVariant,
            ),
          ),
          const SizedBox(height: 32),
          ...DemoData.grade7Curriculum.asMap().entries.map((entry) {
            final chapter = entry.value;
            final isExpanded = _expandedChapterId == chapter.id;
            final isLocked = chapter.status == TopicStatus.locked;
            final iconColor = isLocked
                ? AppColors.outline
                : chapter.status == TopicStatus.completed
                    ? AppColors.onSecondaryContainer
                    : AppColors.onPrimaryContainer;
            final iconBg = isLocked
                ? AppColors.surfaceContainerHighest
                : chapter.status == TopicStatus.completed
                    ? AppColors.secondaryContainer
                    : AppColors.primaryContainer;

            return Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: isExpanded
                  ? _buildExpandedChapter(context, chapter)
                  : _ChapterCard(
                      chapter: chapter.chapterNumber.toUpperCase(),
                      title: chapter.title,
                      icon: _iconFromString(chapter.icon),
                      iconBg: iconBg,
                      iconColor: iconColor,
                      isLocked: isLocked,
                      trailing: isLocked
                          ? null
                          : Icon(
                              isExpanded ? Icons.expand_less : Icons.expand_more,
                              color: isLocked ? AppColors.outline : AppColors.primary,
                            ),
                      onTap: isLocked
                          ? null
                          : () {
                              setState(() {
                                _expandedChapterId = isExpanded ? null : chapter.id;
                              });
                            },
                    ),
            );
          }),
        ],
      ),
    );
  }

  Widget _buildExpandedChapter(BuildContext context, Chapter chapter) {
    return Container(
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
          GestureDetector(
            onTap: () {
              setState(() {
                _expandedChapterId = null;
              });
            },
            child: Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                border: const Border(
                  bottom: BorderSide(color: AppColors.surfaceContainerLow),
                ),
                color: AppColors.primary.withValues(alpha: 0.05),
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
                    child: Icon(
                      _iconFromString(chapter.icon),
                      color: Colors.white,
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          chapter.chapterNumber.toUpperCase(),
                          style: Theme.of(context).textTheme.labelLarge?.copyWith(
                            color: AppColors.primary,
                          ),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          chapter.title,
                          style: Theme.of(context).textTheme.displaySmall,
                        ),
                      ],
                    ),
                  ),
                  const Icon(Icons.expand_less, color: AppColors.primary),
                ],
              ),
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(8),
            child: Column(
              children: chapter.subtopics.map((sub) {
                final isCompleted = sub.status == TopicStatus.completed;
                final isCurrent = sub.status == TopicStatus.inProgress;
                final isLocked = sub.status == TopicStatus.locked;
                return _SubTopicRow(
                  title: sub.title,
                  isCompleted: isCompleted,
                  isCurrent: isCurrent,
                  isLocked: isLocked,
                  onTap: isLocked
                      ? null
                      : () {
                          Navigator.of(context).push(
                            MaterialPageRoute<void>(builder: (_) => const TopicChoiceScreen()),
                          );
                        },
                );
              }).toList(),
            ),
          ),
        ],
      ),
    );
  }
}

class _ChapterCard extends StatelessWidget {
  final String chapter;
  final String title;
  final IconData icon;
  final Color iconBg;
  final Color iconColor;
  final Widget? trailing;
  final bool isLocked;
  final VoidCallback? onTap;

  const _ChapterCard({
    required this.chapter,
    required this.title,
    required this.icon,
    required this.iconBg,
    required this.iconColor,
    this.trailing,
    this.isLocked = false,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        decoration: BoxDecoration(
          color: isLocked ? AppColors.surfaceContainerLow : AppColors.surfaceContainerLowest,
          borderRadius: BorderRadius.circular(16),
          border: isLocked ? Border.all(color: AppColors.outlineVariant.withValues(alpha: 0.3)) : null,
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.04),
              blurRadius: 20,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Row(
            children: [
              Container(
                width: 48,
                height: 48,
                decoration: BoxDecoration(
                  color: iconBg,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(icon, color: iconColor),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      chapter,
                      style: Theme.of(context).textTheme.labelLarge?.copyWith(
                        color: isLocked ? AppColors.outline : AppColors.secondary,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      title,
                      style: Theme.of(context).textTheme.displaySmall?.copyWith(
                        color: isLocked ? AppColors.outline : AppColors.onSurface,
                      ),
                    ),
                  ],
                ),
              ),
              trailing ?? const Icon(Icons.lock, color: AppColors.outline),
            ],
          ),
        ),
      ),
    );
  }
}

class _SubTopicRow extends StatelessWidget {
  final String title;
  final bool isCompleted;
  final bool isCurrent;
  final bool isLocked;
  final VoidCallback? onTap;

  const _SubTopicRow({
    required this.title,
    this.isCompleted = false,
    this.isCurrent = false,
    this.isLocked = false,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      // 48dp touch target: padding ensures minimum hit area.
      onTap: isLocked ? null : onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        margin: const EdgeInsets.only(bottom: 4),
        decoration: BoxDecoration(
          color: isCurrent ? AppColors.primary.withValues(alpha: 0.1) : Colors.transparent,
          border: isCurrent ? Border.all(color: AppColors.primary.withValues(alpha: 0.2)) : null,
          borderRadius: BorderRadius.circular(12),
        ),
        child: Row(
          children: [
            Container(
              width: 24,
              height: 24,
              decoration: BoxDecoration(
                color: isCompleted
                    ? AppColors.secondary
                    : isCurrent
                        ? AppColors.primary
                        : AppColors.outlineVariant,
                shape: BoxShape.circle,
              ),
              child: isCompleted
                  ? const Icon(Icons.check, color: Colors.white, size: 16)
                  : isCurrent
                      ? Container(
                          margin: const EdgeInsets.all(8),
                          decoration: const BoxDecoration(
                            color: Colors.white,
                            shape: BoxShape.circle,
                          ),
                        )
                      : const Icon(Icons.lock, color: AppColors.onSurfaceVariant, size: 14),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                title,
                style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                  fontWeight: isCurrent ? FontWeight.w600 : FontWeight.normal,
                ),
              ),
            ),
            if (isCurrent)
              ElevatedButton(
                onPressed: onTap,
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.primary,
                  foregroundColor: AppColors.onPrimary,
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                  minimumSize: const Size(0, 32),
                  textStyle: const TextStyle(fontSize: 11, fontWeight: FontWeight.w700),
                ),
                child: const Text('RESUME'),
              )
            else if (isCompleted)
              Text(
                'COMPLETE',
                style: Theme.of(context).textTheme.labelLarge?.copyWith(
                  color: AppColors.secondary,
                ),
              )
            else
              Text(
                'LOCKED',
                style: Theme.of(context).textTheme.labelLarge?.copyWith(
                  color: AppColors.outline,
                ),
              ),
          ],
        ),
      ),
    );
  }
}
