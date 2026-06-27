/// Domain model for a nursing MCQ, matching the FastAPI Pydantic schema.
class NursingQuestion {
  final int id;
  final String subjectId;
  final String topicId;
  final String conceptTag;
  final int difficulty;
  final String cognitiveLevel;
  final String context;
  final String format;
  final String question;
  final List<String> options;
  final String correctAnswer;
  final String explanation;
  final String source;
  final String verificationStatus;
  final String? verifiedBy;
  final String? lastReviewed;
  final String? teluguHint;

  const NursingQuestion({
    required this.id,
    required this.subjectId,
    required this.topicId,
    required this.conceptTag,
    required this.difficulty,
    required this.cognitiveLevel,
    required this.context,
    required this.format,
    required this.question,
    required this.options,
    required this.correctAnswer,
    required this.explanation,
    required this.source,
    required this.verificationStatus,
    this.verifiedBy,
    this.lastReviewed,
    this.teluguHint,
  });

  factory NursingQuestion.fromJson(Map<String, dynamic> json) {
    return NursingQuestion(
      id: json['id'] as int,
      subjectId: json['subject_id'] as String,
      topicId: json['topic_id'] as String,
      conceptTag: json['concept_tag'] as String,
      difficulty: json['difficulty'] as int,
      cognitiveLevel: json['cognitive_level'] as String,
      context: json['context'] as String,
      format: json['format'] as String,
      question: json['question'] as String,
      options: (json['options'] as List<dynamic>).cast<String>(),
      correctAnswer: json['correct_answer'] as String,
      explanation: json['explanation'] as String,
      source: json['source'] as String,
      verificationStatus: json['verification_status'] as String,
      verifiedBy: json['verified_by'] as String?,
      lastReviewed: json['last_reviewed'] as String?,
      teluguHint: json['telugu_hint'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'subject_id': subjectId,
      'topic_id': topicId,
      'concept_tag': conceptTag,
      'difficulty': difficulty,
      'cognitive_level': cognitiveLevel,
      'context': context,
      'format': format,
      'question': question,
      'options': options,
      'correct_answer': correctAnswer,
      'explanation': explanation,
      'source': source,
      'verification_status': verificationStatus,
      'verified_by': verifiedBy,
      'last_reviewed': lastReviewed,
      'telugu_hint': teluguHint,
    };
  }
}
