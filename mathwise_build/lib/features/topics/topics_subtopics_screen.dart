/// Topics & Subtopics Screen
///
/// Research basis:
/// - Gobet et al. (2001): Chunking is fundamental to learning [^3].
///   Accordion pattern presents one active module at a time, preventing
///   information overload.
///
/// - Sweller (1988): Split-attention increases extraneous load [^1].
///   Nested sub-topics are indented with a clear left-border path,
///   reducing eye travel between parent and child.
///
/// - Bruner (1966) CPA: The expanded Geometry chapter shows
///   Lines → Angles → Triangles (concrete to abstract progression) [^5].
///
/// - Deci & Ryan (2000): Autonomy [^23]. Student chooses which chapter
///   to expand and which sub-topic to engage.
///
/// ADR-010 Decisions: D6, D2

import 'package:flutter/material.dart';
import '../../core/constants/app_colors.dart';
import '../../shared/data/demo_data.dart';
import '../../shared/models/curriculum.dart';
import '../../shared/widgets/top_app_bar.dart';
import 'topic_choice_screen.dart';

class TopicsSubtopicsScreen extends StatefulWidget {
  const TopicsSubtopicsScreen({super.key});

  @override
  State<TopicsSubtopicsScreen> createState() => _TopicsSubtopicsScreenState();
}

class _TopicsSubtopicsScreenState extends State<TopicsSubtopicsScreen> {
  String? _expandedChapterId;

  void _toggleChapter(String chapterId) {
    setState(() {
      if (_expandedChapterId == chapterId) {
        _expandedChapterId = null;
      } else {
        _expandedChapterId = chapterId;
      }
    });
  }

  void _navigateToTopicChoice(BuildContext context) {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => const TopicChoiceScreen()),
    );
  }

  @override
  Widget build(BuildContext context) {
    final curriculum = DemoData.grade7Curriculum;

    return Scaffold(
      appBar: const MathWiseAppBar(showBackButton: true),
      body: SingleChildScrollView(
        padding: const EdgeInsets.fromLTRB(24, 16, 24, 120),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildHero(context),
            const SizedBox(height: 32),
            ...curriculum.map((chapter) {
              final isExpanded = _expandedChapterId == chapter.id;
              return Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: _ChapterAccordion(
                  chapter: chapter.chapterNumber,
                  title: chapter.title,
                  icon: _getIconData(chapter.icon),
                  topics: _buildTopicsLabel(chapter),
                  isExpanded: isExpanded,
                  isActive: chapter.status == TopicStatus.inProgress,
                  isLocked: chapter.status == TopicStatus.locked,
                  subtopics: chapter.subtopics,
                  onToggle: () => _toggleChapter(chapter.id),
                  onSubtopicTap: chapter.status == TopicStatus.locked
                      ? null
                      : () => _navigateToTopicChoice(context),
                ),
              );
            }),
            const SizedBox(height: 32),
            _buildProgressOverview(context),
          ],
        ),
      ),
    );
  }

  Widget _buildHero(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Text(
              'Curriculum'.toUpperCase(),
              style: Theme.of(context).textTheme.labelLarge?.copyWith(
                color: AppColors.primary,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Container(height: 1, color: AppColors.surfaceContainerHighest),
            ),
          ],
        ),
        const SizedBox(height: 12),
        Text('Grade 7 Mathematics', style: Theme.of(context).textTheme.displayLarge),
        const SizedBox(height: 8),
        Text(
          'Master core mathematical principles through guided practice, interactive visualizations, and structured learning paths.',
          style: Theme.of(context).textTheme.headlineMedium?.copyWith(
            color: AppColors.onSurfaceVariant,
          ),
        ),
      ],
    );
  }

  String _buildTopicsLabel(Chapter chapter) {
    final count = chapter.subtopics.length;
    switch (chapter.status) {
      case TopicStatus.locked:
        return '$count Topics • Locked';
      case TopicStatus.inProgress:
        return 'Active Module • $count Topics';
      case TopicStatus.completed:
        return '$count Topics • Completed';
    }
  }

  Widget _buildProgressOverview(BuildContext context) {
    return Row(
      children: [
        Expanded(
          child: Container(
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
              children: [
                Text('Overall Progress', style: Theme.of(context).textTheme.displaySmall),
                const SizedBox(height: 12),
                Row(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    Text(
                      '64%',
                      style: Theme.of(context).textTheme.displayLarge?.copyWith(
                        color: AppColors.primary,
                        fontSize: 36,
                      ),
                    ),
                    const SizedBox(width: 8),
                    Padding(
                      padding: const EdgeInsets.only(bottom: 4),
                      child: Text(
                        'of curriculum completed',
                        style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                          color: AppColors.onSurfaceVariant,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                ClipRRect(
                  borderRadius: BorderRadius.circular(8),
                  child: LinearProgressIndicator(
                    value: 0.64,
                    minHeight: 8,
                    backgroundColor: AppColors.surfaceContainerLow,
                    valueColor: const AlwaysStoppedAnimation(AppColors.primaryContainer),
                  ),
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
              color: AppColors.surfaceContainerHigh,
              borderRadius: BorderRadius.circular(16),
            ),
            child: Row(
              children: [
                ClipRRect(
                  borderRadius: BorderRadius.circular(12),
                  child: Image.network(
                    'https://images.unsplash.com/photo-1509228468518-180dd4864904?w=200',
                    width: 80,
                    height: 80,
                    fit: BoxFit.cover,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Next Concept',
                        style: Theme.of(context).textTheme.displaySmall?.copyWith(fontSize: 16),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Mastering the Pythagorean Theorem',
                        style: Theme.of(context).textTheme.bodyMedium,
                      ),
                      const SizedBox(height: 8),
                      ElevatedButton(
                        onPressed: () => _navigateToTopicChoice(context),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: AppColors.primary,
                          foregroundColor: AppColors.onPrimary,
                          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                          minimumSize: const Size(0, 36),
                        ),
                        child: const Text('Resume Learning'),
                      ),
                    ],
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

IconData _getIconData(String name) {
  switch (name) {
    case 'pin_drop':
      return Icons.pin_drop;
    case 'category':
      return Icons.category;
    case 'pie_chart':
      return Icons.pie_chart;
    case 'functions':
      return Icons.functions;
    case 'architecture':
      return Icons.architecture;
    case 'calculate':
      return Icons.calculate;
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

class _ChapterAccordion extends StatelessWidget {
  final String chapter;
  final String title;
  final IconData icon;
  final String topics;
  final bool isExpanded;
  final bool isActive;
  final bool isLocked;
  final List<SubTopic> subtopics;
  final VoidCallback onToggle;
  final VoidCallback? onSubtopicTap;

  const _ChapterAccordion({
    required this.chapter,
    required this.title,
    required this.icon,
    required this.topics,
    required this.subtopics,
    required this.onToggle,
    this.onSubtopicTap,
    this.isExpanded = false,
    this.isActive = false,
    this.isLocked = false,
  });

  @override
  Widget build(BuildContext context) {
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
        border: isActive ? Border.all(color: AppColors.primary.withOpacity(0.1)) : null,
      ),
      child: Column(
        children: [
          InkWell(
            onTap: isLocked ? null : onToggle,
            borderRadius: BorderRadius.vertical(
              top: const Radius.circular(16),
              bottom: isExpanded ? Radius.zero : const Radius.circular(16),
            ),
            child: Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: isActive ? AppColors.primary.withOpacity(0.05) : Colors.transparent,
                borderRadius: BorderRadius.vertical(
                  top: const Radius.circular(16),
                  bottom: isExpanded ? Radius.zero : const Radius.circular(16),
                ),
              ),
              child: Row(
                children: [
                  Container(
                    width: 48,
                    height: 48,
                    decoration: BoxDecoration(
                      color: isActive
                          ? AppColors.primaryContainer
                          : AppColors.surfaceContainerLow,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Icon(
                      icon,
                      color: isActive ? Colors.white : AppColors.primary,
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          '$chapter: $title',
                          style: Theme.of(context).textTheme.displaySmall?.copyWith(
                            fontSize: 18,
                          ),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          topics,
                          style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                            color: isActive ? AppColors.primary : AppColors.onSurfaceVariant,
                            fontSize: 14,
                          ),
                        ),
                      ],
                    ),
                  ),
                  Icon(
                    isLocked
                        ? Icons.lock
                        : isExpanded
                            ? Icons.expand_more
                            : Icons.chevron_right,
                    color: isActive ? AppColors.primary : AppColors.outline,
                  ),
                ],
              ),
            ),
          ),
          if (isExpanded)
            Container(
              padding: const EdgeInsets.fromLTRB(20, 0, 20, 16),
              decoration: BoxDecoration(
                color: isActive ? AppColors.primary.withOpacity(0.05) : Colors.transparent,
                borderRadius: const BorderRadius.vertical(bottom: Radius.circular(16)),
              ),
              child: Column(
                children: subtopics.map((sub) {
                  return _SubtopicItem(
                    title: sub.title,
                    isCompleted: sub.status == TopicStatus.completed,
                    isCurrent: sub.status == TopicStatus.inProgress,
                    isLocked: sub.status == TopicStatus.locked,
                    onTap: sub.status == TopicStatus.locked ? null : onSubtopicTap,
                  );
                }).toList(),
              ),
            ),
        ],
      ),
    );
  }
}

class _SubtopicItem extends StatelessWidget {
  final String title;
  final bool isCompleted;
  final bool isCurrent;
  final bool isLocked;
  final VoidCallback? onTap;

  const _SubtopicItem({
    required this.title,
    this.isCompleted = false,
    this.isCurrent = false,
    this.isLocked = false,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        margin: const EdgeInsets.only(bottom: 4),
        decoration: BoxDecoration(
          color: isCurrent ? Colors.white : Colors.transparent,
          borderRadius: BorderRadius.circular(12),
          border: isCurrent
              ? Border.all(color: AppColors.primaryContainer.withOpacity(0.2))
              : null,
          boxShadow: isCurrent
              ? [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.04),
                    blurRadius: 8,
                    offset: const Offset(0, 2),
                  ),
                ]
              : null,
        ),
        child: Row(
          children: [
            Icon(
              isLocked
                  ? Icons.lock
                  : isCompleted
                      ? Icons.check_circle
                      : isCurrent
                          ? Icons.play_circle
                          : Icons.circle_outlined,
              color: isLocked
                  ? AppColors.outline
                  : isCompleted
                      ? AppColors.secondary
                      : isCurrent
                          ? AppColors.primary
                          : AppColors.outline,
              size: 20,
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                title,
                style: TextStyle(
                  fontWeight: isCurrent ? FontWeight.w600 : FontWeight.normal,
                  color: isCurrent ? AppColors.primary : AppColors.onSurface,
                ),
              ),
            ),
            if (isCurrent)
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: AppColors.primaryContainer.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  'In Progress',
                  style: Theme.of(context).textTheme.labelLarge?.copyWith(
                    color: AppColors.primary,
                    fontSize: 10,
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
