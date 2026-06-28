/// Visual Screenshot Generation Test
///
/// Generates golden file screenshots for all 11 screens at 5 viewport sizes.
/// Run with: flutter test --update-goldens test/visual_screenshots_test.dart
///
/// These screenshots feed the dual-persona visual testing pipeline:
/// - Screenshot Auditor (pixel-level token validation)
/// - UI/UX Engineer (qualitative rubric evaluation)
///
/// Note: Uses system fallback fonts to avoid GoogleFonts async network
/// requests in test environment. Layout, color, and spacing evaluation
/// remains fully accurate.
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:mathwise/core/constants/app_colors.dart';
import 'package:mathwise/features/class_selection/class_selection_screen.dart';
import 'package:mathwise/features/concept/concept_content_screen.dart';
import 'package:mathwise/features/curriculum/curriculum_grid_screen.dart';
import 'package:mathwise/features/curriculum/curriculum_list_screen.dart';
import 'package:mathwise/features/curriculum/curriculum_stepper_screen.dart';
import 'package:mathwise/features/games/games_screen.dart';
import 'package:mathwise/features/home/home_screen.dart';
import 'package:mathwise/features/practice/practice_question_screen.dart';
import 'package:mathwise/features/profile/profile_screen.dart';
import 'package:mathwise/features/topics/topic_choice_screen.dart';
import 'package:mathwise/features/topics/topics_subtopics_screen.dart';


/// Minimal theme that preserves the app's color scheme without triggering
/// GoogleFonts network requests in tests.
final _testTheme = ThemeData(
  useMaterial3: true,
  brightness: Brightness.light,
  colorScheme: const ColorScheme(
    brightness: Brightness.light,
    primary: AppColors.primary,
    onPrimary: AppColors.onPrimary,
    primaryContainer: AppColors.primaryContainer,
    onPrimaryContainer: AppColors.onPrimaryContainer,
    secondary: AppColors.secondary,
    onSecondary: AppColors.onSecondary,
    secondaryContainer: AppColors.secondaryContainer,
    onSecondaryContainer: AppColors.onSecondaryContainer,
    tertiary: AppColors.tertiary,
    onTertiary: AppColors.onTertiary,
    tertiaryContainer: AppColors.tertiaryContainer,
    onTertiaryContainer: AppColors.onTertiaryContainer,
    error: AppColors.error,
    onError: AppColors.onPrimary,
    errorContainer: AppColors.errorContainer,
    onErrorContainer: AppColors.onErrorContainer,
    surface: AppColors.surface,
    onSurface: AppColors.onSurface,
    surfaceContainerHighest: AppColors.surfaceContainerHighest,
    surfaceContainerHigh: AppColors.surfaceContainerHigh,
    surfaceContainer: AppColors.surfaceContainer,
    surfaceContainerLow: AppColors.surfaceContainerLow,
    surfaceContainerLowest: AppColors.surfaceContainerLowest,
    outline: AppColors.outline,
    outlineVariant: AppColors.outlineVariant,
    inverseSurface: AppColors.inverseSurface,
    inversePrimary: AppColors.primaryFixedDim,
    shadow: Color(0x1F000000),
    scrim: Color(0x99000000),
  ),
  scaffoldBackgroundColor: AppColors.background,
);

void main() {
  final viewports = [
    ('375x812', const Size(375, 812)),
    ('390x844', const Size(390, 844)),
    ('430x932', const Size(430, 932)),
    ('768x1024', const Size(768, 1024)),
    ('1024x768', const Size(1024, 768)),
  ];

  group('Visual Testing Screenshot Capture', () {
    final screens = <(String, Widget)>[
      ('home', const HomeScreen()),
      ('class_selection', const ClassSelectionScreen()),
      ('topic_choice', const TopicChoiceScreen()),
      ('topics_subtopics', const TopicsSubtopicsScreen()),
      ('curriculum_grid', const CurriculumGridScreen()),
      ('curriculum_list', const CurriculumListScreen()),
      ('curriculum_stepper', const CurriculumStepperScreen()),
      ('concept_content', const ConceptContentScreen()),
      ('practice_question', const PracticeQuestionScreen()),
      ('games', const GamesScreen()),
      ('profile', const ProfileScreen()),
    ];

    for (final screen in screens) {
      final screenName = screen.$1;
      final screenWidget = screen.$2;
      for (final viewport in viewports) {
        final vpName = viewport.$1;
        final vpSize = viewport.$2;
        testWidgets('$screenName @ $vpName', (tester) async {
          // physicalSize is in pixels; devicePixelRatio converts to logical dp.
          // Multiply the named viewport by the DPR so logical size equals vpSize.
          const dpr = 2.0;
          tester.view.physicalSize = Size(
            vpSize.width * dpr,
            vpSize.height * dpr,
          );
          tester.view.devicePixelRatio = dpr;
          addTearDown(tester.view.reset);

          await tester.pumpWidget(
            MaterialApp(
              theme: _testTheme,
              debugShowCheckedModeBanner: false,
              home: screenWidget,
            ),
          );
          await tester.pumpAndSettle(const Duration(seconds: 2));

          await expectLater(
            find.byType(MaterialApp),
            matchesGoldenFile('goldens/$screenName/$vpName.png'),
          );
        });
      }
    }
  });
}
