class UserProfile {
  final String name;
  final String grade;
  final String tagline;
  final String avatarUrl;
  final int level;
  final String rank;
  final int streakDays;
  final double totalStudyHours;
  final int topicsCompleted;
  final double accuracyRate;

  const UserProfile({
    required this.name,
    required this.grade,
    required this.tagline,
    required this.avatarUrl,
    required this.level,
    required this.rank,
    required this.streakDays,
    required this.totalStudyHours,
    required this.topicsCompleted,
    required this.accuracyRate,
  });
}

class AchievementBadge {
  final String label;
  final String iconName;
  final bool unlocked;

  const AchievementBadge({
    required this.label,
    required this.iconName,
    required this.unlocked,
  });
}

class TopicMastery {
  final String topic;
  final double score;

  const TopicMastery({required this.topic, required this.score});
}
