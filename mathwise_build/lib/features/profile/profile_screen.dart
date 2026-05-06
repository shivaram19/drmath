/// Profile Screen
///
/// Research basis:
/// - Deci & Ryan (2000): Competence feedback supports intrinsic motivation [^23].
///   The stats grid, progress bars, and badges are all competence signals.
///
/// - Dweck (2006): Growth mindset [^13]. "Strong Topics" and "Needs Focus"
///   framing (not "Bad at Fractions") encourages malleable self-concept.
///
/// - Elliot & Maier (2014): Green signals growth; red is used only for
///   informational labeling, never for shaming [^14].
///
/// - Lally et al. (2010): Streaks leverage loss aversion for habit formation [^17].
///   The "10 Day Streak" badge is a visual habit cue.
///
/// - Hamari et al. (2014): Gamification badges must be competence-linked [^19].
///   Each badge maps to a specific, achievable behavior (Perfect Week, Fast Learner).
///
/// ADR-010 Decisions: D9, D4
library;

import 'package:flutter/material.dart';
import '../../core/constants/app_colors.dart';
import '../../shared/data/demo_data.dart';
import '../topics/topic_choice_screen.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.fromLTRB(24, 16, 24, 120),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildProfileHeader(context),
          const SizedBox(height: 32),
          _buildStatsGrid(context),
          const SizedBox(height: 32),
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(child: _buildAchievements(context)),
              const SizedBox(width: 24),
              Expanded(child: _buildTopicProgress(context)),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildProfileHeader(BuildContext context) {
    const user = DemoData.currentUser;
    return Row(
      children: [
        Stack(
          children: [
            Container(
              width: 100,
              height: 100,
              decoration: BoxDecoration(
                color: AppColors.surfaceContainer,
                shape: BoxShape.circle,
                border: Border.all(color: Colors.white, width: 4),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withValues(alpha: 0.1),
                    blurRadius: 12,
                  ),
                ],
              ),
              child: ClipOval(
                child: Image.network(
                  user.avatarUrl,
                  fit: BoxFit.cover,
                  errorBuilder: (context, error, stackTrace) => const Icon(Icons.person),
                ),
              ),
            ),
            // Verified badge: competence signal, not status symbol.
            Positioned(
              bottom: 4,
              right: 4,
              child: Container(
                padding: const EdgeInsets.all(6),
                decoration: const BoxDecoration(
                  color: AppColors.secondary,
                  shape: BoxShape.circle,
                ),
                child: const Icon(Icons.verified, color: Colors.white, size: 16),
              ),
            ),
          ],
        ),
        const SizedBox(width: 20),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(user.name, style: Theme.of(context).textTheme.displayLarge),
              const SizedBox(height: 4),
              Text(
                '${user.grade} • ${user.tagline}',
                style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                  color: AppColors.onSurfaceVariant,
                ),
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  _Badge(label: 'Level ${user.level}', color: AppColors.primaryContainer.withValues(alpha: 0.1), textColor: AppColors.primary),
                  const SizedBox(width: 8),
                  _Badge(label: user.rank, color: AppColors.secondaryContainer.withValues(alpha: 0.2), textColor: AppColors.secondary),
                ],
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildStatsGrid(BuildContext context) {
    // Three competence metrics: time, volume, accuracy.
    // Rationale: Deci & Ryan (2000) — competence feedback must be specific [^23].
    return Row(
      children: [
        const Expanded(
          child: _StatBox(
            icon: Icons.schedule,
            iconBg: Color(0xFFEBF4FF),
            iconColor: AppColors.primary,
            label: 'Total Study Hours',
            value: '24h',
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _StatBox(
            icon: Icons.task_alt,
            iconBg: AppColors.secondaryContainer.withValues(alpha: 0.2),
            iconColor: AppColors.secondary,
            label: 'Topics Completed',
            value: '12',
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _StatBox(
            icon: Icons.analytics,
            iconBg: AppColors.tertiaryContainer.withValues(alpha: 0.1),
            iconColor: AppColors.tertiary,
            label: 'Accuracy Rate',
            value: '85%',
          ),
        ),
      ],
    );
  }

  Widget _buildAchievements(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text('Achievements', style: Theme.of(context).textTheme.displaySmall),
            GestureDetector(
              onTap: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('All achievements unlocked!')),
                );
              },
              child: Text(
                'View All',
                style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                  color: AppColors.primary,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
        Container(
          padding: const EdgeInsets.all(24),
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
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: AppColors.surfaceContainerLow,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Row(
                  children: [
                    Container(
                      width: 48,
                      height: 48,
                      decoration: const BoxDecoration(
                        color: AppColors.tertiaryFixed,
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(Icons.emoji_events, color: AppColors.tertiary),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Competitions Won',
                            style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                          Text(
                            '3 First Place Trophies',
                            style: Theme.of(context).textTheme.bodyMedium,
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),
              Text(
                'Unlocked Badges'.toUpperCase(),
                style: Theme.of(context).textTheme.labelLarge,
              ),
              const SizedBox(height: 12),
              // Competence-linked badges: each maps to a specific behavior.
              // Rationale: Hamari et al. (2014) [^19]; Deci (1971) anti-crowding [^21].
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: DemoData.badges.asMap().entries.map((entry) {
                  final badge = entry.value;
                  final colors = [
                    AppColors.primaryContainer,
                    AppColors.secondaryContainer.withValues(alpha: 0.3),
                    AppColors.tertiaryContainer.withValues(alpha: 0.2),
                    const Color(0xFFFFEBEE),
                  ];
                  return _BadgeItem(
                    icon: _iconFromName(badge.iconName),
                    label: badge.label,
                    color: colors[entry.key % colors.length],
                  );
                }).toList(),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildTopicProgress(BuildContext context) {
    // "Strong Topics" vs. "Needs Focus" framing.
    // Rationale: Dweck (2006) growth mindset [^13].
    // "Needs Focus" implies malleability; "Weak Topics" would imply fixed ability.
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Topic Progress', style: Theme.of(context).textTheme.displaySmall),
        const SizedBox(height: 16),
        Container(
          padding: const EdgeInsets.all(24),
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
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  const Icon(Icons.trending_up, color: AppColors.secondary, size: 18),
                  const SizedBox(width: 8),
                  Text(
                    'Strong Topics'.toUpperCase(),
                    style: Theme.of(context).textTheme.labelLarge?.copyWith(
                      color: AppColors.secondary,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              ...DemoData.strongTopics.asMap().entries.map((entry) {
                return Padding(
                  padding: EdgeInsets.only(bottom: entry.key < DemoData.strongTopics.length - 1 ? 12 : 0),
                  child: _ProgressBar(label: entry.value.topic, value: entry.value.score, color: AppColors.secondary),
                );
              }),
              const SizedBox(height: 24),
              Row(
                children: [
                  const Icon(Icons.trending_down, color: AppColors.error, size: 18),
                  const SizedBox(width: 8),
                  Text(
                    'Needs Focus'.toUpperCase(),
                    style: Theme.of(context).textTheme.labelLarge?.copyWith(
                      color: AppColors.error,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              ...DemoData.weakTopics.asMap().entries.map((entry) {
                return Padding(
                  padding: EdgeInsets.only(bottom: entry.key < DemoData.weakTopics.length - 1 ? 12 : 0),
                  child: _ProgressBar(label: entry.value.topic, value: entry.value.score, color: AppColors.error),
                );
              }),
              const SizedBox(height: 16),
              SizedBox(
                width: double.infinity,
                child: OutlinedButton.icon(
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute<void>(builder: (_) => const TopicChoiceScreen()),
                    );
                  },
                  icon: const Icon(Icons.arrow_forward, size: 18),
                  label: const Text('Practice Fractions Now'),
                  style: OutlinedButton.styleFrom(
                    foregroundColor: AppColors.primary,
                    side: const BorderSide(color: AppColors.primary, width: 0.5),
                    padding: const EdgeInsets.symmetric(vertical: 14),
                  ),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

IconData _iconFromName(String name) {
  switch (name) {
    case 'rocket_launch':
      return Icons.rocket_launch;
    case 'military_tech':
      return Icons.military_tech;
    case 'functions':
      return Icons.functions;
    case 'local_fire_department':
      return Icons.local_fire_department;
    default:
      return Icons.emoji_events;
  }
}

class _Badge extends StatelessWidget {
  final String label;
  final Color color;
  final Color textColor;

  const _Badge({required this.label, required this.color, required this.textColor});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: color,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Text(
        label,
        style: Theme.of(context).textTheme.labelLarge?.copyWith(
          color: textColor,
          fontSize: 10,
        ),
      ),
    );
  }
}

class _StatBox extends StatelessWidget {
  final IconData icon;
  final Color iconBg;
  final Color iconColor;
  final String label;
  final String value;

  const _StatBox({
    required this.icon,
    required this.iconBg,
    required this.iconColor,
    required this.label,
    required this.value,
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
            color: Colors.black.withValues(alpha: 0.04),
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
              color: iconBg,
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(icon, color: iconColor, size: 24),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  label,
                  style: Theme.of(context).textTheme.labelLarge,
                ),
                const SizedBox(height: 4),
                Text(
                  value,
                  style: Theme.of(context).textTheme.displayMedium?.copyWith(fontSize: 24),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _BadgeItem extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;

  const _BadgeItem({required this.icon, required this.label, required this.color});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Container(
          width: 56,
          height: 56,
          decoration: BoxDecoration(
            color: color,
            shape: BoxShape.circle,
          ),
          child: Icon(icon, color: AppColors.primary, size: 28),
        ),
        const SizedBox(height: 8),
        Text(
          label,
          style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w500),
          textAlign: TextAlign.center,
        ),
      ],
    );
  }
}

class _ProgressBar extends StatelessWidget {
  final String label;
  final double value;
  final Color color;

  const _ProgressBar({required this.label, required this.value, required this.color});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(label, style: Theme.of(context).textTheme.bodyLarge),
            Text(
              '${(value * 100).toInt()}%',
              style: TextStyle(
                color: color,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
        const SizedBox(height: 6),
        ClipRRect(
          borderRadius: BorderRadius.circular(4),
          child: LinearProgressIndicator(
            value: value,
            minHeight: 6,
            backgroundColor: AppColors.surfaceContainerLow,
            valueColor: AlwaysStoppedAnimation(color),
          ),
        ),
      ],
    );
  }
}
