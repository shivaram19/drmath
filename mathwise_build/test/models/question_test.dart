import 'package:flutter_test/flutter_test.dart';
import 'package:mathwise/shared/models/question.dart';

void main() {
  group('Question', () {
    const question = Question(
      id: 'q1',
      topic: 'triangles',
      questionText: 'What is the sum of angles in a triangle?',
      options: [
        QuizOption(label: 'A', text: '90°'),
        QuizOption(label: 'B', text: '180°'),
        QuizOption(label: 'C', text: '270°'),
        QuizOption(label: 'D', text: '360°'),
      ],
      correctIndex: 1,
      hint: 'Remember: all three angles add up to a straight line.',
    );

    test('stores all fields correctly', () {
      expect(question.id, 'q1');
      expect(question.topic, 'triangles');
      expect(question.questionText, 'What is the sum of angles in a triangle?');
      expect(question.options.length, 4);
      expect(question.correctIndex, 1);
      expect(question.hint, 'Remember: all three angles add up to a straight line.');
      expect(question.diagramType, isNull);
    });

    test('correctIndex identifies the right answer', () {
      expect(question.options[question.correctIndex].text, '180°');
    });
  });

  group('QuizSession', () {
    final questions = List.generate(
      5,
      (i) => Question(
        id: 'q$i',
        topic: 'test',
        questionText: 'Question $i',
        options: const [
          QuizOption(label: 'A', text: 'Wrong'),
          QuizOption(label: 'B', text: 'Correct'),
        ],
        correctIndex: 1,
        hint: 'Hint $i',
      ),
    );

    test('initial state has zero score', () {
      final session = QuizSession(
        topic: 'test',
        questions: questions,
      );
      expect(session.score, 0.0);
      expect(session.currentIndex, 0);
      expect(session.answers, isEmpty);
    });

    test('score calculates correctly for all correct', () {
      final session = QuizSession(
        topic: 'test',
        questions: questions,
        answers: const {0: 1, 1: 1, 2: 1, 3: 1, 4: 1},
      );
      expect(session.score, 1.0);
    });

    test('score calculates correctly for half correct', () {
      final session = QuizSession(
        topic: 'test',
        questions: questions,
        answers: const {0: 1, 1: 0, 2: 1, 3: 0, 4: 1},
      );
      expect(session.score, 0.6);
    });

    test('score calculates correctly for none correct', () {
      final session = QuizSession(
        topic: 'test',
        questions: questions,
        answers: const {0: 0, 1: 0, 2: 0, 3: 0, 4: 0},
      );
      expect(session.score, 0.0);
    });

    test('copyWith updates currentIndex', () {
      const session = QuizSession(topic: 'test', questions: []);
      final updated = session.copyWith(currentIndex: 3);
      expect(updated.currentIndex, 3);
      expect(updated.topic, 'test'); // Unchanged
    });

    test('copyWith updates answers', () {
      const session = QuizSession(topic: 'test', questions: []);
      final updated = session.copyWith(answers: {0: 1});
      expect(updated.answers, {0: 1});
    });
  });
}
