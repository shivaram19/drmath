/// Capability score for a subject, topic, or cognitive dimension.
class Capability {
  final double accuracy;
  final double speedScore;
  final double confidenceGap;
  final double consistencyScore;
  final double priorityScore;
  final String? subjectId;
  final String? topicId;
  final String? cognitiveLevel;

  const Capability({
    required this.accuracy,
    required this.speedScore,
    required this.confidenceGap,
    required this.consistencyScore,
    required this.priorityScore,
    this.subjectId,
    this.topicId,
    this.cognitiveLevel,
  });

  factory Capability.fromJson(Map<String, dynamic> json) {
    return Capability(
      accuracy: (json['accuracy'] as num).toDouble(),
      speedScore: (json['speed_score'] as num).toDouble(),
      confidenceGap: (json['confidence_gap'] as num).toDouble(),
      consistencyScore: (json['consistency_score'] as num).toDouble(),
      priorityScore: (json['priority_score'] as num).toDouble(),
      subjectId: json['subject_id'] as String?,
      topicId: json['topic_id'] as String?,
      cognitiveLevel: json['cognitive_level'] as String?,
    );
  }
}

/// Full analysis response from /api/nursing/analyze.
class CapabilityAnalysis {
  final List<Capability> subjectCapabilities;
  final List<Capability> topicCapabilities;
  final List<Capability> dimensionCapabilities;

  const CapabilityAnalysis({
    required this.subjectCapabilities,
    required this.topicCapabilities,
    required this.dimensionCapabilities,
  });

  factory CapabilityAnalysis.fromJson(Map<String, dynamic> json) {
    return CapabilityAnalysis(
      subjectCapabilities: (json['subject_capabilities'] as List<dynamic>)
          .map((e) => Capability.fromJson(e as Map<String, dynamic>))
          .toList(),
      topicCapabilities: (json['topic_capabilities'] as List<dynamic>)
          .map((e) => Capability.fromJson(e as Map<String, dynamic>))
          .toList(),
      dimensionCapabilities: (json['dimension_capabilities'] as List<dynamic>)
          .map((e) => Capability.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }
}
