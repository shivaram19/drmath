/// Home Screen — Dashboard & Entry Point
///
/// Research basis:
/// - Deci & Ryan (2000) Self-Determination Theory: Autonomy, competence, relatedness [^23].
///   The home screen provides three autonomy-supporting entry points:
///   (1) "Resume Lesson" — student controls pacing.
///   (2) "Daily Practice" — student chooses when to engage.
///   (3) "Enter Games" — student selects their engagement mode.
///
/// - Lally et al. (2010): Habit formation requires consistent cues [^17].
///   The Daily Practice card displays a reset countdown, creating a
///   predictable routine cue.
///
/// - Cognitive Load Theory: The bento grid limits primary actions to 3 cards.
///   No notification badges, no scrolling ads, no interruptive modals.
///
/// - Blue primary color reduces math anxiety (Elliot & Maier 2014) [^12].
///   The "Continue Learning" card uses blue to signal focus, not pressure.
///
/// ADR-010 Decisions: D9, D3
library;

import 'package:flutter/material.dart';
import '../../core/constants/app_breakpoints.dart';
import '../../core/constants/app_colors.dart';
import '../../shared/data/demo_data.dart';
import '../../shared/widgets/bottom_nav_bar.dart';
import '../../shared/widgets/top_app_bar.dart';
import '../class_selection/class_selection_screen.dart';
import '../concept/concept_content_screen.dart';
import '../curriculum/curriculum_grid_screen.dart';
import '../curriculum/curriculum_list_screen.dart';
import '../curriculum/curriculum_stepper_screen.dart';
import '../games/games_screen.dart';
import '../nursing/screens/nursing_entry_screen.dart';
import '../practice/practice_question_screen.dart';
import '../profile/profile_screen.dart';
import '../topics/topic_choice_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _currentIndex = 0;

  final _pages = [
    const _HomeTab(),
    const CurriculumListScreen(),
    const GamesScreen(),
    const ProfileScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: const MathWiseAppBar(),
      body: _pages[_currentIndex],
      bottomNavigationBar: MathWiseBottomNav(
        currentIndex: _currentIndex,
        onTap: (i) => setState(() => _currentIndex = i),
      ),
    );
  }
}

class _HomeTab extends StatelessWidget {
  const _HomeTab();

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return SingleChildScrollView(
      padding: const EdgeInsets.fromLTRB(24, 16, 24, 120),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Greeting: autonomy-supporting, not prescriptive.
          // "Ready to conquer" frames math as challenge, not threat.
          Text('Hello \u{1F44B}', style: theme.textTheme.displayLarge),
          const SizedBox(height: 8),
          Text(
            'Ready to conquer some numbers today? You\'re doing great!',
            style: theme.textTheme.headlineMedium?.copyWith(
              color: AppColors.onSurfaceVariant,
            ),
          ),
          const SizedBox(height: 16),
          _buildClassSelector(context),
          const SizedBox(height: 32),
          // Bento grid: responsive 2-column on tablet, single column on phone.
          // Research: Sweller (1988) — less scrolling reduces extraneous load.
          // Material 3 medium breakpoint (600dp) triggers two-column layout.
          LayoutBuilder(
            builder: (context, constraints) {
              final isTablet = constraints.maxWidth >= Breakpoints.medium;
              if (isTablet) {
                return Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(
                      flex: 2,
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          _buildContinueCard(context),
                          const SizedBox(height: 16),
                          _buildGamesSummaryCard(context),
                          const SizedBox(height: 32),
                          Text('Recommended for You', style: theme.textTheme.displaySmall),
                          const SizedBox(height: 16),
                          _buildRecommendedGrid(context),
                        ],
                      ),
                    ),
                    const SizedBox(width: 24),
                    Expanded(
                      flex: 1,
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          _buildDailyPracticeCard(context),
                        ],
                      ),
                    ),
                  ],
                );
              }
              // Compact: single column (mobile default).
              return Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildContinueCard(context),
                  const SizedBox(height: 16),
                  _buildDailyPracticeCard(context),
                  const SizedBox(height: 16),
                  _buildGamesSummaryCard(context),
                  const SizedBox(height: 32),
                  Text('Recommended for You', style: theme.textTheme.displaySmall),
                  const SizedBox(height: 16),
                  _buildRecommendedGrid(context),
                ],
              );
            },
          ),
          const SizedBox(height: 32),
          // Nursing practice entry point for adult learners.
          Text('Nursing Practice', style: theme.textTheme.displaySmall),
          const SizedBox(height: 16),
          _buildNursingCard(context),
          const SizedBox(height: 32),
          // Dev/demo navigation to all screens.
          Text('All Screens', style: theme.textTheme.displaySmall),
          const SizedBox(height: 16),
          _buildAllScreensGrid(context),
        ],
      ),
    );
  }

  Widget _buildContinueCard(BuildContext context) {
    // "Continue Learning" card: competence feedback + autonomy.
    // Student sees their exact progress (68%) and decides to resume.
    // Rationale: SDT — competence + autonomy = intrinsic motivation [^23].
    return LayoutBuilder(
      builder: (context, constraints) {
        final isCompact = constraints.maxWidth <= 360;
        final padding = isCompact ? 16.0 : 24.0;
        return Container(
          padding: EdgeInsets.all(padding),
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
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                decoration: BoxDecoration(
                  color: AppColors.primaryContainer.withValues(alpha: 0.2),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  'CONTINUE LEARNING',
                  style: Theme.of(context).textTheme.labelLarge?.copyWith(
                    color: AppColors.primary,
                    letterSpacing: 0.05,
                  ),
                ),
              ),
              const SizedBox(height: 16),
              Text(
                DemoData.currentTopic,
                style: Theme.of(context).textTheme.displayMedium,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 4),
              Text(
                'Mastering chords, tangents, and sectors.',
                style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                  color: AppColors.onSurfaceVariant,
                ),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 20),
              _buildCourseProgressRow(context, isCompact),
              const SizedBox(height: 8),
              ClipRRect(
                borderRadius: BorderRadius.circular(8),
                child: const LinearProgressIndicator(
                  value: DemoData.currentTopicProgress,
                  minHeight: 8,
                  backgroundColor: AppColors.surfaceContainer,
                  valueColor: AlwaysStoppedAnimation(AppColors.primary),
                ),
              ),
              const SizedBox(height: 20),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: () => _navigate(context, const TopicChoiceScreen()),
                  icon: const Icon(Icons.play_arrow, size: 20),
                  label: const Text('Resume Lesson'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.primary,
                    foregroundColor: AppColors.onPrimary,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    textStyle: const TextStyle(fontWeight: FontWeight.w600),
                  ),
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildCourseProgressRow(BuildContext context, bool isCompact) {
    final label = Text(
      'Course Progress',
      style: Theme.of(context).textTheme.bodyLarge,
      overflow: TextOverflow.ellipsis,
    );
    final value = Text(
      '${(DemoData.currentTopicProgress * 100).toInt()}%',
      style: Theme.of(context).textTheme.bodyLarge?.copyWith(
        fontWeight: FontWeight.w700,
        color: AppColors.primary,
      ),
      overflow: TextOverflow.ellipsis,
    );

    if (isCompact) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          label,
          const SizedBox(height: 2),
          value,
        ],
      );
    }

    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Expanded(child: label),
        Flexible(child: value),
      ],
    );
  }

  Widget _buildDailyPracticeCard(BuildContext context) {
    // Daily Practice: spaced repetition cue.
    // Rationale: Ebbinghaus forgetting curve — 60% loss in 24h without retrieval [^15].
    // Roediger & Karpicke (2006): retrieval practice > re-reading [^16].
    // Lally et al. (2010): fixed-time cues build habits [^17].
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: AppColors.secondaryContainer.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.secondaryContainer.withValues(alpha: 0.2)),
      ),
      child: Column(
        children: [
          Container(
            width: 64,
            height: 64,
            decoration: BoxDecoration(
              color: AppColors.secondaryContainer,
              borderRadius: BorderRadius.circular(16),
            ),
            child: const Icon(Icons.auto_awesome, color: AppColors.secondary, size: 32),
          ),
          const SizedBox(height: 16),
          Text('Daily Practice', style: Theme.of(context).textTheme.displaySmall),
          const SizedBox(height: 4),
          Text(
            '10 Questions Ready',
            style: Theme.of(context).textTheme.bodyLarge?.copyWith(
              color: AppColors.onSecondaryContainer,
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(height: 16),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: () => _navigate(context, const PracticeQuestionScreen()),
              style: ElevatedButton.styleFrom(
                backgroundColor: AppColors.secondary,
                foregroundColor: AppColors.onSecondary,
                padding: const EdgeInsets.symmetric(vertical: 16),
              ),
              child: const Text('Start Now'),
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Resets in 4h 20m',
            style: Theme.of(context).textTheme.labelLarge?.copyWith(
              color: AppColors.outline,
              fontStyle: FontStyle.italic,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildGamesSummaryCard(BuildContext context) {
    // Games summary: competence feedback without extrinsic reward language.
    // "Lifelines" = attempts remaining (competence signal), not coins.
    // Rationale: Hamari et al. (2014): competence-linked gamification works;
    // extrinsic currency crowds out intrinsic motivation [^19][^21].
    return LayoutBuilder(
      builder: (context, constraints) {
        final isCompact = constraints.maxWidth <= 360;
        final padding = isCompact ? 16.0 : 24.0;
        return Container(
          padding: EdgeInsets.all(padding),
          decoration: BoxDecoration(
            color: AppColors.surfaceContainerLow,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: AppColors.surfaceContainerHigh),
          ),
          child: isCompact
              ? _buildGamesCompactLayout(context)
              : _buildGamesWideLayout(context),
        );
      },
    );
  }

  Widget _buildGamesWideLayout(BuildContext context) {
    return Row(
      children: [
        Container(
          width: 72,
          height: 72,
          decoration: BoxDecoration(
            color: AppColors.tertiaryFixed,
            borderRadius: BorderRadius.circular(36),
          ),
          child: const Icon(Icons.sports_esports, color: AppColors.onTertiaryFixed, size: 36),
        ),
        const SizedBox(width: 16),
        Expanded(
          child: _buildGamesInfoColumn(context),
        ),
        const SizedBox(width: 12),
        Flexible(
          child: _buildGamesEnterButton(context),
        ),
      ],
    );
  }

  Widget _buildGamesCompactLayout(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        Container(
          width: 64,
          height: 64,
          decoration: BoxDecoration(
            color: AppColors.tertiaryFixed,
            borderRadius: BorderRadius.circular(32),
          ),
          child: const Icon(Icons.sports_esports, color: AppColors.onTertiaryFixed, size: 32),
        ),
        const SizedBox(height: 12),
        _buildGamesInfoColumn(context, center: true),
        const SizedBox(height: 16),
        SizedBox(
          width: double.infinity,
          child: _buildGamesEnterButton(context),
        ),
      ],
    );
  }

  Widget _buildGamesInfoColumn(BuildContext context, {bool center = false}) {
    return Column(
      crossAxisAlignment: center ? CrossAxisAlignment.center : CrossAxisAlignment.start,
      children: [
        Text(
          'Math Playground',
          style: Theme.of(context).textTheme.displaySmall,
          overflow: TextOverflow.ellipsis,
          textAlign: center ? TextAlign.center : TextAlign.start,
        ),
        const SizedBox(height: 8),
        _buildStatRow(context, Icons.schedule, AppColors.primary, '1h 30m Today'),
        const SizedBox(height: 4),
        _buildStatRow(context, Icons.star, AppColors.tertiary, '3 Lifelines Available'),
      ],
    );
  }

  Widget _buildStatRow(BuildContext context, IconData icon, Color color, String text) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, color: color, size: 18),
        const SizedBox(width: 4),
        Flexible(
          child: Text(
            text,
            style: Theme.of(context).textTheme.bodyLarge?.copyWith(
              color: AppColors.onSurfaceVariant,
            ),
            overflow: TextOverflow.ellipsis,
          ),
        ),
      ],
    );
  }

  Widget _buildGamesEnterButton(BuildContext context) {
    return ElevatedButton(
      onPressed: () => _navigate(context, const GamesScreen()),
      style: ElevatedButton.styleFrom(
        backgroundColor: AppColors.surfaceContainerHighest,
        foregroundColor: AppColors.primaryFixedDim,
        side: const BorderSide(color: AppColors.primary, width: 0.5),
        elevation: 0,
        minimumSize: const Size(0, 48),
      ),
      child: const Text('Enter Games'),
    );
  }

  Widget _buildNursingCard(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final isCompact = constraints.maxWidth <= 360;
        final padding = isCompact ? 16.0 : 24.0;
        return Container(
          padding: EdgeInsets.all(padding),
          decoration: BoxDecoration(
            color: AppColors.surfaceContainerLowest,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: AppColors.primary.withValues(alpha: 0.2)),
          ),
          child: isCompact
              ? _buildNursingCompactLayout(context)
              : _buildNursingWideLayout(context),
        );
      },
    );
  }

  Widget _buildNursingWideLayout(BuildContext context) {
    return Row(
      children: [
        Container(
          width: 56,
          height: 56,
          decoration: BoxDecoration(
            color: AppColors.primaryContainer,
            borderRadius: BorderRadius.circular(16),
          ),
          child: const Icon(Icons.local_hospital, color: AppColors.primary),
        ),
        const SizedBox(width: 16),
        Expanded(
          child: _buildNursingInfoColumn(context),
        ),
        const SizedBox(width: 12),
        Flexible(
          child: _buildNursingOpenButton(context),
        ),
      ],
    );
  }

  Widget _buildNursingCompactLayout(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: AppColors.primaryContainer,
                borderRadius: BorderRadius.circular(14),
              ),
              child: const Icon(Icons.local_hospital, color: AppColors.primary, size: 24),
            ),
            const SizedBox(width: 12),
            Expanded(child: _buildNursingInfoColumn(context)),
          ],
        ),
        const SizedBox(height: 12),
        SizedBox(
          width: double.infinity,
          child: _buildNursingOpenButton(context),
        ),
      ],
    );
  }

  Widget _buildNursingInfoColumn(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Telangana Staff Nurse',
          style: Theme.of(context).textTheme.titleLarge,
          overflow: TextOverflow.ellipsis,
          maxLines: 1,
        ),
        const SizedBox(height: 4),
        Text(
          'Topic-wise practice for ANM/GNM recruitment',
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
            color: AppColors.onSurfaceVariant,
          ),
          overflow: TextOverflow.ellipsis,
          maxLines: 2,
        ),
      ],
    );
  }

  Widget _buildNursingOpenButton(BuildContext context) {
    return ElevatedButton(
      onPressed: () => _navigate(context, const NursingEntryScreen()),
      style: ElevatedButton.styleFrom(
        backgroundColor: AppColors.primary,
        foregroundColor: AppColors.onPrimary,
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        minimumSize: const Size(0, 48),
      ),
      child: const Text('Open'),
    );
  }

  Widget _buildRecommendedGrid(BuildContext context) {
    final items = [
      (Icons.functions, 'Algebra Basics', '12 Lessons', const Color(0xFFEBF4FF)),
      (Icons.percent, 'Percentage Pro', '8 Lessons', const Color(0xFFFFF4EB)),
      (Icons.straighten, 'Measurement', '15 Lessons', const Color(0xFFEBFFF4)),
    ];
    return Column(
      children: items.map((item) {
        return GestureDetector(
          onTap: () => _navigate(context, const TopicChoiceScreen()),
          child: Container(
            margin: const EdgeInsets.only(bottom: 12),
            padding: const EdgeInsets.all(16),
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
                    color: item.$4,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Icon(item.$1, color: AppColors.primary),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        item.$2,
                        style: const TextStyle(
                          fontWeight: FontWeight.w600,
                          fontSize: 16,
                        ),
                      ),
                      Text(
                        item.$3,
                        style: const TextStyle(
                          fontSize: 12,
                          color: AppColors.outline,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        );
      }).toList(),
    );
  }

  Widget _buildAllScreensGrid(BuildContext context) {
    final screens = [
      ('Class Selection', () => _navigate(context, const ClassSelectionScreen())),
      ('Curriculum Grid', () => _navigate(context, const CurriculumGridScreen())),
      ('Curriculum Stepper', () => _navigate(context, const CurriculumStepperScreen())),
      ('Topic Choice', () => _navigate(context, const TopicChoiceScreen())),
      ('Concept Content', () => _navigate(context, const ConceptContentScreen())),
      ('Practice Question', () => _navigate(context, const PracticeQuestionScreen())),
    ];
    return Wrap(
      spacing: 12,
      runSpacing: 12,
      children: screens.map((s) {
        return ActionChip(
          label: Text(s.$1),
          onPressed: s.$2,
          backgroundColor: AppColors.primaryContainer.withValues(alpha: 0.1),
          side: BorderSide(color: AppColors.primaryContainer.withValues(alpha: 0.3)),
          labelStyle: const TextStyle(color: AppColors.primary),
        );
      }).toList(),
    );
  }

  Widget _buildClassSelector(BuildContext context) {
    // Grade selector: autonomy-supporting, visible, discoverable.
    // Rationale: Deci & Ryan (2000) — autonomy requires visible choices.
    // Nielsen (2016) — hidden navigation reduces discoverability by 50%.
    return GestureDetector(
      onTap: () => _navigate(context, const ClassSelectionScreen()),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: AppColors.primaryContainer.withValues(alpha: 0.15),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: AppColors.primaryContainer.withValues(alpha: 0.3),
          ),
        ),
        child: Row(
          children: [
            Container(
              width: 40,
              height: 40,
              decoration: BoxDecoration(
                color: AppColors.primaryContainer,
                borderRadius: BorderRadius.circular(10),
              ),
              child: const Icon(Icons.school, color: Colors.white, size: 20),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    DemoData.currentUser.grade,
                    style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                      fontWeight: FontWeight.w600,
                      color: AppColors.primary,
                    ),
                    overflow: TextOverflow.ellipsis,
                    maxLines: 1,
                  ),
                  Text(
                    'Tap to switch class',
                    style: Theme.of(context).textTheme.labelLarge?.copyWith(
                      color: AppColors.onSurfaceVariant,
                    ),
                    overflow: TextOverflow.ellipsis,
                    maxLines: 1,
                  ),
                ],
              ),
            ),
            const Icon(
              Icons.chevron_right,
              color: AppColors.primary,
            ),
          ],
        ),
      ),
    );
  }

  void _navigate(BuildContext context, Widget screen) {
    Navigator.of(context).push(MaterialPageRoute<void>(builder: (_) => screen));
  }
}
