enum TopicStatus { locked, inProgress, completed }

class SubTopic {
  final String id;
  final String title;
  final TopicStatus status;
  final String? conceptId;

  const SubTopic({
    required this.id,
    required this.title,
    required this.status,
    this.conceptId,
  });
}

class Chapter {
  final String id;
  final String chapterNumber;
  final String title;
  final String icon;
  final List<SubTopic> subtopics;
  final TopicStatus status;
  final double progress;

  const Chapter({
    required this.id,
    required this.chapterNumber,
    required this.title,
    required this.icon,
    required this.subtopics,
    required this.status,
    required this.progress,
  });
}

class StudentClass {
  final String grade;
  final String subtitle;
  final String icon;
  final double progress;
  final String progressLabel;

  const StudentClass({
    required this.grade,
    required this.subtitle,
    required this.icon,
    required this.progress,
    required this.progressLabel,
  });
}
