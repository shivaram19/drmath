class Game {
  final String id;
  final String title;
  final String description;
  final String imageUrl;
  final int starCost;
  final bool unlocked;

  const Game({
    required this.id,
    required this.title,
    required this.description,
    required this.imageUrl,
    required this.starCost,
    required this.unlocked,
  });
}

class GameStats {
  final double studyMinutesToday;
  final double studyGoalMinutes;
  final int lifelines;
  final int maxLifelines;

  const GameStats({
    required this.studyMinutesToday,
    required this.studyGoalMinutes,
    required this.lifelines,
    required this.maxLifelines,
  });

  double get studyProgress => studyMinutesToday / studyGoalMinutes;
}

class WeeklyChallenge {
  final String title;
  final String description;
  final String timeRemaining;

  const WeeklyChallenge({
    required this.title,
    required this.description,
    required this.timeRemaining,
  });
}
