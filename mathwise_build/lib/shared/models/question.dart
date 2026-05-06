class QuizOption {
  final String label;
  final String text;

  const QuizOption({required this.label, required this.text});
}

/// Domain entity representing a single quiz question.
///
/// TODO: This is currently an anemic domain model (data bag only).
/// Per `architecture/layers.md` and Reso Coder's DDD guidance, domain
/// models should contain behavior and enforce invariants.
///
/// Next evolution (when backed by real repository):
/// - Add `isCorrect(int selectedIndex)` method
/// - Add `calculateScore({bool usedHint})` method
/// - Add assertions for `correctIndex` bounds in constructor
/// - Move scoring logic from `QuizSession` into `Question`
///
/// Blocked on: Real backend + repository pattern implementation.
/// Current demo data does not justify the abstraction overhead.
class Question {
  final String id;
  final String topic;
  final String questionText;
  final List<QuizOption> options;
  final int correctIndex;
  final String hint;
  final String? diagramType;

  const Question({
    required this.id,
    required this.topic,
    required this.questionText,
    required this.options,
    required this.correctIndex,
    required this.hint,
    this.diagramType,
  });
}

class QuizSession {
  final String topic;
  final List<Question> questions;
  final int currentIndex;
  final Map<int, int> answers;

  const QuizSession({
    required this.topic,
    required this.questions,
    this.currentIndex = 0,
    this.answers = const {},
  });

  QuizSession copyWith({
    int? currentIndex,
    Map<int, int>? answers,
  }) {
    return QuizSession(
      topic: topic,
      questions: questions,
      currentIndex: currentIndex ?? this.currentIndex,
      answers: answers ?? this.answers,
    );
  }

  double get score {
    if (answers.isEmpty) return 0;
    int correct = 0;
    answers.forEach((qIndex, selected) {
      if (selected == questions[qIndex].correctIndex) correct++;
    });
    return correct / questions.length;
  }
}
