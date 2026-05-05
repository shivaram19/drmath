import '../models/concept.dart';
import '../models/curriculum.dart';
import '../models/game.dart';
import '../models/question.dart';
import '../models/user_profile.dart';

class DemoData {
  static const UserProfile currentUser = UserProfile(
    name: 'Alex Johnson',
    grade: 'Grade 8',
    tagline: 'Math Enthusiast',
    avatarUrl: 'https://i.pravatar.cc/150?img=12',
    level: 14,
    rank: 'Top 5% Learner',
    streakDays: 12,
    totalStudyHours: 24.0,
    topicsCompleted: 12,
    accuracyRate: 0.85,
  );

  static const List<AchievementBadge> badges = [
    AchievementBadge(label: 'Fast Learner', iconName: 'rocket_launch', unlocked: true),
    AchievementBadge(label: 'Perfect Week', iconName: 'military_tech', unlocked: true),
    AchievementBadge(label: 'Math Wizard', iconName: 'functions', unlocked: true),
    AchievementBadge(label: '10 Day Streak', iconName: 'local_fire_department', unlocked: true),
  ];

  static const List<TopicMastery> strongTopics = [
    TopicMastery(topic: 'Geometry', score: 0.94),
    TopicMastery(topic: 'Numbers', score: 0.88),
  ];

  static const List<TopicMastery> weakTopics = [
    TopicMastery(topic: 'Fractions', score: 0.62),
  ];

  static const List<StudentClass> studentClasses = [
    StudentClass(
      grade: 'Class 5',
      subtitle: 'Foundations of Fractions & Decimals',
      icon: 'functions',
      progress: 0.85,
      progressLabel: '85% Complete',
    ),
    StudentClass(
      grade: 'Class 6',
      subtitle: 'Ratios, Rates & Proportions',
      icon: 'calculate',
      progress: 0.40,
      progressLabel: '40% Complete',
    ),
    StudentClass(
      grade: 'Class 7',
      subtitle: 'Number Systems & Geometry',
      icon: 'category',
      progress: 0.0,
      progressLabel: '0% Complete',
    ),
    StudentClass(
      grade: 'Class 8',
      subtitle: 'Algebraic Expressions & Identities',
      icon: 'code',
      progress: 0.0,
      progressLabel: '0% Complete',
    ),
    StudentClass(
      grade: 'Class 9',
      subtitle: 'Polynomials & Quadrilaterals',
      icon: 'analytics',
      progress: 0.0,
      progressLabel: '0% Complete',
    ),
    StudentClass(
      grade: 'Class 10',
      subtitle: 'Trigonometry & Advanced Calculus',
      icon: 'change_history',
      progress: 0.0,
      progressLabel: '0% Complete',
    ),
  ];

  static const List<Chapter> grade7Curriculum = [
    Chapter(
      id: 'ch1',
      chapterNumber: 'Chapter 1',
      title: 'Numbers',
      icon: 'pin_drop',
      status: TopicStatus.completed,
      progress: 1.0,
      subtopics: [
        SubTopic(id: 'st1', title: 'Integers', status: TopicStatus.completed),
        SubTopic(id: 'st2', title: 'Fractions & Decimals', status: TopicStatus.completed),
        SubTopic(id: 'st3', title: 'Rational Numbers', status: TopicStatus.completed),
        SubTopic(id: 'st4', title: 'Exponents', status: TopicStatus.completed),
      ],
    ),
    Chapter(
      id: 'ch2',
      chapterNumber: 'Chapter 2',
      title: 'Geometry',
      icon: 'category',
      status: TopicStatus.inProgress,
      progress: 0.45,
      subtopics: [
        SubTopic(id: 'st5', title: 'Lines', status: TopicStatus.completed),
        SubTopic(id: 'st6', title: 'Angles', status: TopicStatus.completed),
        SubTopic(id: 'st7', title: 'Triangles', status: TopicStatus.inProgress, conceptId: 'triangles'),
        SubTopic(id: 'st8', title: 'Circles', status: TopicStatus.locked),
      ],
    ),
    Chapter(
      id: 'ch3',
      chapterNumber: 'Chapter 3',
      title: 'Fractions',
      icon: 'pie_chart',
      status: TopicStatus.locked,
      progress: 0.0,
      subtopics: [
        SubTopic(id: 'st9', title: 'Equivalent Fractions', status: TopicStatus.locked),
        SubTopic(id: 'st10', title: 'Operations on Fractions', status: TopicStatus.locked),
        SubTopic(id: 'st11', title: 'Decimal Operations', status: TopicStatus.locked),
      ],
    ),
  ];

  static const List<Chapter> grade8Curriculum = [
    Chapter(
      id: 'ch1-8',
      chapterNumber: 'Chapter 1',
      title: 'Algebraic Thinking',
      icon: 'functions',
      status: TopicStatus.completed,
      progress: 1.0,
      subtopics: [
        SubTopic(id: 'st1-8', title: 'Variables & Expressions', status: TopicStatus.completed),
        SubTopic(id: 'st2-8', title: 'Linear Equations', status: TopicStatus.completed),
        SubTopic(id: 'st3-8', title: 'Inequalities', status: TopicStatus.completed),
      ],
    ),
    Chapter(
      id: 'ch2-8',
      chapterNumber: 'Chapter 2',
      title: 'Geometry',
      icon: 'architecture',
      status: TopicStatus.inProgress,
      progress: 0.45,
      subtopics: [
        SubTopic(id: 'st4-8', title: 'Lines', status: TopicStatus.completed),
        SubTopic(id: 'st5-8', title: 'Angles', status: TopicStatus.completed),
        SubTopic(id: 'st6-8', title: 'Triangles', status: TopicStatus.inProgress, conceptId: 'triangles'),
        SubTopic(id: 'st7-8', title: 'Circles', status: TopicStatus.locked),
      ],
    ),
    Chapter(
      id: 'ch3-8',
      chapterNumber: 'Chapter 3',
      title: 'Statistics',
      icon: 'calculate',
      status: TopicStatus.locked,
      progress: 0.0,
      subtopics: [
        SubTopic(id: 'st8-8', title: 'Data Collection', status: TopicStatus.locked),
        SubTopic(id: 'st9-8', title: 'Mean, Median, Mode', status: TopicStatus.locked),
      ],
    ),
  ];

  static const List<Question> triangleQuestions = [
    Question(
      id: 'q1',
      topic: 'Triangles',
      questionText: 'In a right-angled triangle, if one angle measures 35°, what is the measure of the third angle?',
      options: [
        QuizOption(label: 'A', text: '45°'),
        QuizOption(label: 'B', text: '55°'),
        QuizOption(label: 'C', text: '65°'),
        QuizOption(label: 'D', text: '90°'),
      ],
      correctIndex: 1,
      hint: 'Remember: The sum of interior angles in any triangle is always 180°.',
      diagramType: 'right_triangle_35',
    ),
    Question(
      id: 'q2',
      topic: 'Triangles',
      questionText: 'A triangle has sides of 5cm, 5cm, and 8cm. What type of triangle is it?',
      options: [
        QuizOption(label: 'A', text: 'Equilateral'),
        QuizOption(label: 'B', text: 'Isosceles'),
        QuizOption(label: 'C', text: 'Scalene'),
        QuizOption(label: 'D', text: 'Right-Angled'),
      ],
      correctIndex: 1,
      hint: 'Two sides are equal — what do we call a triangle with two equal sides?',
    ),
    Question(
      id: 'q3',
      topic: 'Triangles',
      questionText: 'What is the sum of all interior angles of a triangle?',
      options: [
        QuizOption(label: 'A', text: '90°'),
        QuizOption(label: 'B', text: '180°'),
        QuizOption(label: 'C', text: '270°'),
        QuizOption(label: 'D', text: '360°'),
      ],
      correctIndex: 1,
      hint: 'This is one of the most fundamental facts about triangles.',
    ),
    Question(
      id: 'q4',
      topic: 'Triangles',
      questionText: 'In an equilateral triangle, what is the measure of each angle?',
      options: [
        QuizOption(label: 'A', text: '45°'),
        QuizOption(label: 'B', text: '60°'),
        QuizOption(label: 'C', text: '90°'),
        QuizOption(label: 'D', text: '120°'),
      ],
      correctIndex: 1,
      hint: 'All angles are equal and the sum is 180°.',
    ),
    Question(
      id: 'q5',
      topic: 'Triangles',
      questionText: 'Which side is the longest in a right-angled triangle?',
      options: [
        QuizOption(label: 'A', text: 'Adjacent'),
        QuizOption(label: 'B', text: 'Opposite'),
        QuizOption(label: 'C', text: 'Hypotenuse'),
        QuizOption(label: 'D', text: 'Base'),
      ],
      correctIndex: 2,
      hint: 'The side opposite the right angle is always the longest.',
    ),
    Question(
      id: 'q6',
      topic: 'Triangles',
      questionText: 'A triangle with all sides of different lengths is called:',
      options: [
        QuizOption(label: 'A', text: 'Equilateral'),
        QuizOption(label: 'B', text: 'Isosceles'),
        QuizOption(label: 'C', text: 'Scalene'),
        QuizOption(label: 'D', text: 'Right'),
      ],
      correctIndex: 2,
      hint: 'Think about the Greek root "skalenos" meaning unequal.',
    ),
    Question(
      id: 'q7',
      topic: 'Triangles',
      questionText: 'Using Pythagoras theorem, if a = 3 and b = 4, what is c?',
      options: [
        QuizOption(label: 'A', text: '5'),
        QuizOption(label: 'B', text: '6'),
        QuizOption(label: 'C', text: '7'),
        QuizOption(label: 'D', text: '25'),
      ],
      correctIndex: 0,
      hint: 'a² + b² = c² → 9 + 16 = 25 → c = √25',
    ),
    Question(
      id: 'q8',
      topic: 'Triangles',
      questionText: 'How many degrees are in the exterior angle of a triangle?',
      options: [
        QuizOption(label: 'A', text: 'Equal to the sum of opposite interior angles'),
        QuizOption(label: 'B', text: 'Always 90°'),
        QuizOption(label: 'C', text: 'Always 180°'),
        QuizOption(label: 'D', text: 'Equal to the adjacent interior angle'),
      ],
      correctIndex: 0,
      hint: 'The exterior angle theorem states that the exterior angle equals the sum of the two opposite interior angles.',
    ),
  ];

  static const GameStats currentGameStats = GameStats(
    studyMinutesToday: 105.0,
    studyGoalMinutes: 120.0,
    lifelines: 3,
    maxLifelines: 5,
  );

  static const List<Game> games = [
    Game(
      id: 'g1',
      title: 'Math Detective',
      description: 'Solve the numerical puzzles to find the missing variables and crack the vault.',
      imageUrl: 'https://images.unsplash.com/photo-1606326608606-aa0b62935f2b?w=600',
      starCost: 1,
      unlocked: true,
    ),
    Game(
      id: 'g2',
      title: 'Puzzle Escape',
      description: 'Use geometric logic and spatial reasoning to escape the 3D mathematical labyrinth.',
      imageUrl: 'https://images.unsplash.com/photo-1611996908543-1605677ee272?w=600',
      starCost: 2,
      unlocked: true,
    ),
  ];

  static const WeeklyChallenge weeklyChallenge = WeeklyChallenge(
    title: 'Weekly Challenge',
    description: 'Test your skills with the Weekly Geometry Battle.',
    timeRemaining: 'Next Competition starts in 5 Hours',
  );

  static const ConceptTopic trianglesConcept = ConceptTopic(
    id: 'triangles',
    breadcrumb: 'Geometry Foundations',
    title: 'Types of Triangles',
    progress: 0.65,
    sections: [
      ConceptSection(
        type: SectionType.concrete,
        title: 'Why do we care?',
        body: 'Triangles are the strongest shape in engineering. From the giant trusses of the Golden Gate Bridge to the support beams in your own roof, understanding their properties helps us build a world that stays standing.',
        imageUrl: 'https://images.unsplash.com/photo-1545558014-8692077e9b5c?w=600',
      ),
      ConceptSection(
        type: SectionType.pictorial,
        title: 'Classification Guide',
        body: 'Triangles are defined by their sides and their angles.',
      ),
      ConceptSection(
        type: SectionType.abstract,
        title: 'The Pythagorean Connection',
        body: 'When dealing with Right-Angled triangles, we unlock a special mathematical superpower called the Pythagorean Theorem. This allows us to calculate the length of any side if we know the other two.',
        formula: 'a² + b² = c²',
      ),
    ],
    quickCheck: ConceptQuestion(
      question: 'A triangle has sides of 5cm, 5cm, and 8cm. What type of triangle is it?',
      options: ['Equilateral', 'Isosceles', 'Scalene', 'Right-Angled'],
      correctIndex: 1,
    ),
  );

  static const List<String> recommendedTopics = [
    'Algebra Basics',
    'Percentage Pro',
    'Measurement',
  ];

  static const String currentTopic = 'Geometry → Circles';
  static const double currentTopicProgress = 0.68;
}
