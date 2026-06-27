import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mathwise/features/nursing/models/nursing_question.dart';
import 'package:mathwise/features/nursing/widgets/question_card.dart';

import '../../../test_helpers.dart';

NursingQuestion get _sampleQuestion => const NursingQuestion(
      id: 1,
      subjectId: 'anatomy_physiology',
      topicId: 'ap_cardiovascular',
      conceptTag: 'normal blood pressure',
      difficulty: 1,
      cognitiveLevel: 'remember',
      context: 'theory',
      format: 'mcq',
      question: 'What is the normal adult blood pressure?',
      options: [
        'A) 90/60 mmHg',
        'B) 120/80 mmHg',
        'C) 140/90 mmHg',
        'D) 100/70 mmHg',
      ],
      correctAnswer: 'B',
      explanation: 'Normal adult BP is approximately 120/80 mmHg.',
      source: 'INC GNM Syllabus',
      verificationStatus: 'reviewed',
      verifiedBy: 'GNM syllabus cross-check',
      lastReviewed: '2026-06-27',
    );

void main() {
  group('QuestionCard', () {
    testWidgets('renders question and options', (WidgetTester tester) async {
      await pumpWithTheme(
        tester,
        QuestionCard(question: _sampleQuestion),
      );

      expect(find.text('What is the normal adult blood pressure?'), findsOneWidget);
      expect(find.text('A) 90/60 mmHg'), findsOneWidget);
      expect(find.text('B) 120/80 mmHg'), findsOneWidget);
      expect(find.text('C) 140/90 mmHg'), findsOneWidget);
      expect(find.text('D) 100/70 mmHg'), findsOneWidget);
    });

    testWidgets('calls onSelect with option letter when tapped',
        (WidgetTester tester) async {
      String? selected;
      await pumpWithTheme(
        tester,
        QuestionCard(
          question: _sampleQuestion,
          onSelect: (value) => selected = value,
        ),
      );

      await tester.tap(find.text('B) 120/80 mmHg'));
      await tester.pump();

      expect(selected, equals('B'));
    });

    testWidgets('shows explanation in feedback mode',
        (WidgetTester tester) async {
      await pumpWithTheme(
        tester,
        SingleChildScrollView(
          child: QuestionCard(
            question: _sampleQuestion,
            showFeedback: true,
            selectedAnswer: 'A',
          ),
        ),
      );

      expect(find.text('Explanation'), findsOneWidget);
      expect(find.textContaining('Normal adult BP'), findsOneWidget);
    });

    testWidgets('shows trust metadata when expanded',
        (WidgetTester tester) async {
      await pumpWithTheme(
        tester,
        QuestionCard(question: _sampleQuestion),
      );

      await tester.tap(find.text('Source & verification'));
      await tester.pumpAndSettle();

      expect(find.text('Source: INC GNM Syllabus'), findsOneWidget);
      expect(find.text('Verified by: GNM syllabus cross-check'), findsOneWidget);
    });

    testWidgets('all option buttons meet tap target guidelines',
        (WidgetTester tester) async {
      await pumpWithTheme(
        tester,
        QuestionCard(question: _sampleQuestion),
      );

      await expectLater(tester, meetsGuideline(androidTapTargetGuideline));
      await expectLater(tester, meetsGuideline(iOSTapTargetGuideline));
    });
  });
}
