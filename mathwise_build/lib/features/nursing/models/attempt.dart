/// User attempt payload sent to /api/nursing/analyze.
class Attempt {
  final int questionId;
  final String selectedOption;
  final bool isCorrect;
  final double timeSeconds;
  final int confidence;
  final String subjectId;
  final String topicId;
  final String cognitiveLevel;

  const Attempt({
    required this.questionId,
    required this.selectedOption,
    required this.isCorrect,
    required this.timeSeconds,
    required this.confidence,
    required this.subjectId,
    required this.topicId,
    required this.cognitiveLevel,
  });

  Map<String, dynamic> toJson() {
    return {
      'question_id': questionId,
      'selected_option': selectedOption,
      'is_correct': isCorrect,
      'time_seconds': timeSeconds,
      'confidence': confidence,
      'subject_id': subjectId,
      'topic_id': topicId,
      'cognitive_level': cognitiveLevel,
    };
  }

  factory Attempt.fromJson(Map<String, dynamic> json) {
    return Attempt(
      questionId: json['question_id'] as int,
      selectedOption: json['selected_option'] as String,
      isCorrect: json['is_correct'] as bool,
      timeSeconds: (json['time_seconds'] as num).toDouble(),
      confidence: json['confidence'] as int,
      subjectId: json['subject_id'] as String,
      topicId: json['topic_id'] as String,
      cognitiveLevel: json['cognitive_level'] as String,
    );
  }
}
