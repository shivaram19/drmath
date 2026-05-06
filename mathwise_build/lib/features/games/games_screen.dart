/// Games Screen
///
/// Research basis:
/// - Hamari et al. (2014): Gamification improves learning only when tied to
///   competence feedback, not extrinsic rewards [^19].
///   "Star lifelines" = attempts remaining (competence signal), not currency.
///
/// - Deci (1971): Extrinsic rewards (coins, gems) crowd out intrinsic motivation [^21].
///   This screen contains NO purchasable items, NO coin economy.
///
/// - Ashcraft (2002): Time pressure in formative assessment increases anxiety [^9].
///   The "Weekly Challenge" is event-based ("starts in 5 hours"), not a personal
///   countdown timer. Competition is against self, not social leaderboard.
///
/// - Valkenburg & Peter (2013): Social comparison leaderboards harm self-esteem
///   in children under 14 [^20]. We avoid leaderboards entirely.
///
/// ADR-010 Decisions: D9, D8
library;

import 'package:flutter/material.dart';
import '../../core/constants/app_colors.dart';
import '../../shared/data/demo_data.dart';
import '../practice/practice_question_screen.dart';

class GamesScreen extends StatelessWidget {
  const GamesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.fromLTRB(24, 16, 24, 120),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildStatsRow(context),
          const SizedBox(height: 32),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Play & Learn', style: Theme.of(context).textTheme.displayMedium),
              Text(
                'Unlocked by your effort',
                style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                  color: AppColors.primary,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          ...DemoData.games.asMap().entries.map((entry) {
            final game = entry.value;
            return Padding(
              padding: EdgeInsets.only(bottom: entry.key < DemoData.games.length - 1 ? 16 : 0),
              child: _GameCard(
                title: game.title,
                description: game.description,
                imageUrl: game.imageUrl,
                stars: game.starCost,
                onPlay: () {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Game starting...')),
                  );
                },
              ),
            );
          }),
          const SizedBox(height: 32),
          _buildCompetitionCard(context),
        ],
      ),
    );
  }

  Widget _buildStatsRow(BuildContext context) {
    const stats = DemoData.currentGameStats;
    final studyHours = stats.studyMinutesToday ~/ 60;
    final studyMins = (stats.studyMinutesToday % 60).toInt();
    return Row(
      children: [
        Expanded(
          child: _StatCard(
            icon: Icons.schedule,
            iconBg: AppColors.primaryContainer.withValues(alpha: 0.1),
            iconColor: AppColors.primary,
            label: 'Study Time Today',
            value: '${studyHours}h ${studyMins}m',
            progress: stats.studyProgress,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _StatCard(
            icon: Icons.stars,
            iconBg: AppColors.tertiaryFixed.withValues(alpha: 0.2),
            iconColor: AppColors.tertiary,
            label: 'Lifelines',
            value: '${stats.lifelines} Stars',
            showStars: true,
            starCount: stats.lifelines,
          ),
        ),
      ],
    );
  }

  Widget _buildCompetitionCard(BuildContext context) {
    // Weekly Challenge: self-competition, not social leaderboard.
    // Rationale: Valkenburg & Peter (2013) — social comparison harms children [^20].
    // Event-based timing avoids personal performance pressure (Ashcraft 2002) [^9].
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: AppColors.secondaryContainer.withValues(alpha: 0.3),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white),
      ),
      child: Row(
        children: [
          Container(
            width: 72,
            height: 72,
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
            ),
            child: const Icon(Icons.emoji_events, color: AppColors.secondary, size: 40),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Weekly Challenge', style: Theme.of(context).textTheme.displayMedium),
                const SizedBox(height: 4),
                Row(
                  children: [
                    const Icon(Icons.timer, color: AppColors.secondary, size: 16),
                    const SizedBox(width: 4),
                    Text(
                      'Next Competition starts in 5 Hours',
                      style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                        color: AppColors.secondary,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute<void>(builder: (_) => const PracticeQuestionScreen()),
              );
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.secondary,
              foregroundColor: AppColors.onSecondary,
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
            ),
            child: const Text('Join Competition'),
          ),
        ],
      ),
    );
  }
}

class _StatCard extends StatelessWidget {
  final IconData icon;
  final Color iconBg;
  final Color iconColor;
  final String label;
  final String value;
  final double? progress;
  final bool showStars;
  final int starCount;

  const _StatCard({
    required this.icon,
    required this.iconBg,
    required this.iconColor,
    required this.label,
    required this.value,
    this.progress,
    this.showStars = false,
    this.starCount = 3,
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
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
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
              const Spacer(),
              if (showStars)
                Row(
                  children: List.generate(
                    starCount,
                    (i) => const Icon(Icons.star, color: AppColors.tertiary, size: 18),
                  ),
                )
              else if (progress != null)
                SizedBox(
                  width: 64,
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(4),
                    child: LinearProgressIndicator(
                      value: progress,
                      minHeight: 6,
                      backgroundColor: AppColors.surfaceContainerLow,
                      valueColor: const AlwaysStoppedAnimation(AppColors.primary),
                    ),
                  ),
                ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            label,
            style: Theme.of(context).textTheme.labelLarge,
          ),
          const SizedBox(height: 4),
          Text(value, style: Theme.of(context).textTheme.displaySmall),
        ],
      ),
    );
  }
}

class _GameCard extends StatelessWidget {
  final String title;
  final String description;
  final String imageUrl;
  final int stars;
  final VoidCallback? onPlay;

  const _GameCard({
    required this.title,
    required this.description,
    required this.imageUrl,
    required this.stars,
    this.onPlay,
  });

  @override
  Widget build(BuildContext context) {
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
      clipBehavior: Clip.antiAlias,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Stack(
            children: [
              Image.network(
                imageUrl,
                height: 180,
                width: double.infinity,
                fit: BoxFit.cover,
                errorBuilder: (context, error, stackTrace) => const Icon(Icons.broken_image),
              ),
              // Star cost badge: competence signal ("you have earned 2 stars"),
              // not currency ("this costs 2 coins").
              Positioned(
                top: 12,
                right: 12,
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: 0.9),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(Icons.stars, color: AppColors.tertiary, size: 16),
                      const SizedBox(width: 4),
                      Text(
                        '$stars Star${stars > 1 ? 's' : ''}',
                        style: Theme.of(context).textTheme.labelLarge,
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
          Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: Theme.of(context).textTheme.displaySmall),
                const SizedBox(height: 8),
                Text(
                  description,
                  style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                    color: AppColors.onSurfaceVariant,
                  ),
                ),
                const SizedBox(height: 16),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    onPressed: onPlay,
                    icon: const Icon(Icons.play_arrow, size: 20),
                    label: const Text('Play Now'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppColors.primary,
                      foregroundColor: AppColors.onPrimary,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
