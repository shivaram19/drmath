import 'dart:async';

import 'package:flutter/foundation.dart';

import '../models/attempt.dart';
import '../models/nursing_question.dart';
import '../services/nursing_api_service.dart';
import '../services/nursing_storage_service.dart';

/// Quiz modes supported by the nursing module.
enum QuizMode { diagnostic, mock, practice }

/// Lightweight ChangeNotifier that holds cross-screen quiz state.
///
/// Persists in-flight progress to [NursingStorageService] so that a user who
/// loses the app to process death can resume a long mock or practice session.
class NursingSessionController extends ChangeNotifier {
  NursingSessionController({
    NursingApiService? api,
    NursingStorageService? storage,
  })  : _api = api ?? NursingApiService(),
        _storage = storage ?? NursingStorageService();

  final NursingApiService _api;
  final NursingStorageService _storage;

  QuizMode? mode;
  String? subjectId;
  String? topicId;
  List<NursingQuestion> questions = [];
  int currentIndex = 0;
  final Map<int, String> selectedAnswers = {};
  final Set<int> markedForReview = {};
  bool loading = false;
  String? error;
  DateTime? startTime;
  int remainingSeconds = 60 * 60;

  Timer? _mockTimer;

  bool get hasQuestions => questions.isNotEmpty;

  bool get isLastQuestion =>
      questions.isNotEmpty && currentIndex == questions.length - 1;

  NursingQuestion? get currentQuestion =>
      questions.isNotEmpty ? questions[currentIndex] : null;

  int get answeredCount => selectedAnswers.length;

  int get unansweredCount => questions.length - answeredCount;

  /// Starts a new quiz session by loading questions from the API.
  ///
  /// If [questions] are provided directly (e.g., resumed from a saved session),
  /// the API call is skipped.
  Future<void> start({
    required QuizMode mode,
    String? subjectId,
    String? topicId,
    List<NursingQuestion>? questions,
  }) async {
    this.mode = mode;
    this.subjectId = subjectId;
    this.topicId = topicId;
    loading = true;
    error = null;
    notifyListeners();

    try {
      if (questions != null && questions.isNotEmpty) {
        this.questions = questions;
      } else {
        switch (mode) {
          case QuizMode.diagnostic:
            this.questions = await _api.startDiagnostic(numQuestions: 20);
          case QuizMode.mock:
            this.questions = await _api.startMock();
            _startMockTimer();
          case QuizMode.practice:
            this.questions = await _api.fetchQuestions(
              subjectId: subjectId,
              topicId: topicId,
              limit: 20,
            );
        }
      }

      startTime = DateTime.now();
      currentIndex = 0;
      selectedAnswers.clear();
      markedForReview.clear();
      loading = false;
      await _persist();
      notifyListeners();
    } catch (e) {
      loading = false;
      error = e.toString();
      notifyListeners();
    }
  }

  /// Records an answer for the question at [index].
  void selectAnswer(int index, String answer) {
    selectedAnswers[index] = answer;
    _persist();
    notifyListeners();
  }

  /// Toggles the mark-for-review flag for the question at [index].
  void toggleMarkForReview(int index) {
    if (markedForReview.contains(index)) {
      markedForReview.remove(index);
    } else {
      markedForReview.add(index);
    }
    _persist();
    notifyListeners();
  }

  /// Jumps to a specific question [index].
  void goToQuestion(int index) {
    if (index < 0 || index >= questions.length) return;
    currentIndex = index;
    _persist();
    notifyListeners();
  }

  /// Advances to the next question if the current one has been answered.
  ///
  /// Returns `true` if navigation occurred, `false` if the current question
  /// is unanswered.
  bool next() {
    if (!selectedAnswers.containsKey(currentIndex)) return false;
    if (currentIndex < questions.length - 1) {
      currentIndex++;
      _persist();
      notifyListeners();
      return true;
    }
    return false;
  }

  /// Builds the [Attempt] list from the current session.
  List<Attempt> buildAttempts() {
    if (questions.isEmpty || startTime == null) return [];
    final elapsed = DateTime.now().difference(startTime!).inSeconds;
    final perQuestion = questions.isNotEmpty
        ? (elapsed / questions.length).clamp(1, 9999).toDouble()
        : 30.0;

    return List.generate(questions.length, (i) {
      final q = questions[i];
      final selected = selectedAnswers[i] ?? '';
      return Attempt(
        questionId: q.id,
        selectedOption: selected,
        isCorrect: selected == q.correctAnswer,
        timeSeconds: perQuestion,
        confidence: 3,
        subjectId: q.subjectId,
        topicId: q.topicId,
        cognitiveLevel: q.cognitiveLevel,
      );
    });
  }

  /// Submits the current session, persists attempts, and clears in-flight state.
  Future<void> submit() async {
    _mockTimer?.cancel();
    final attempts = buildAttempts();
    await _storage.appendAttempts(attempts);
    await _storage.clearInflightSession();
  }

  /// Clears the current session without submitting.
  Future<void> abandon() async {
    _mockTimer?.cancel();
    await _storage.clearInflightSession();
    _reset();
  }

  /// Attempts to restore a previously saved in-flight session.
  ///
  /// Returns `true` if a session was restored.
  Future<bool> restoreInflightSession() async {
    final session = await _storage.loadInflightSession();
    if (session == null) return false;

    final savedModeName = session['mode'] as String?;
    final savedQuestions = (session['questions'] as List<dynamic>?)
        ?.map((e) => NursingQuestion.fromJson(e as Map<String, dynamic>))
        .toList();

    if (savedModeName == null || savedQuestions == null || savedQuestions.isEmpty) {
      await _storage.clearInflightSession();
      return false;
    }

    mode = QuizMode.values.byName(savedModeName);
    subjectId = session['subject_id'] as String?;
    topicId = session['topic_id'] as String?;
    questions = savedQuestions;
    currentIndex = (session['current_index'] as num?)?.toInt() ?? 0;
    selectedAnswers.clear();
    final answers = session['selected_answers'] as Map<String, dynamic>?;
    if (answers != null) {
      for (final entry in answers.entries) {
        selectedAnswers[int.parse(entry.key)] = entry.value as String;
      }
    }
    markedForReview.clear();
    final marked = session['marked_for_review'] as List<dynamic>?;
    if (marked != null) {
      markedForReview.addAll(marked.map((e) => (e as num).toInt()));
    }
    remainingSeconds = (session['remaining_seconds'] as num?)?.toInt() ?? 60 * 60;
    startTime = DateTime.now();

    if (mode == QuizMode.mock) {
      _startMockTimer();
    }

    notifyListeners();
    return true;
  }

  void _startMockTimer() {
    _mockTimer?.cancel();
    _mockTimer = Timer.periodic(const Duration(seconds: 1), (timer) {
      remainingSeconds--;
      if (remainingSeconds <= 0) {
        timer.cancel();
        // Auto-submit is handled by the listening screen.
      }
      _persist();
      notifyListeners();
    });
  }

  Future<void> _persist() async {
    if (mode == null || questions.isEmpty) return;
    final session = <String, dynamic>{
      'mode': mode!.name,
      'subject_id': subjectId,
      'topic_id': topicId,
      'questions': questions.map((q) => q.toJson()).toList(),
      'current_index': currentIndex,
      'selected_answers': selectedAnswers.map(
        (key, value) => MapEntry(key.toString(), value),
      ),
      'marked_for_review': markedForReview.toList(),
      'remaining_seconds': remainingSeconds,
    };
    await _storage.saveInflightSession(session);
  }

  void _reset() {
    mode = null;
    subjectId = null;
    topicId = null;
    questions = [];
    currentIndex = 0;
    selectedAnswers.clear();
    markedForReview.clear();
    loading = false;
    error = null;
    startTime = null;
    remainingSeconds = 60 * 60;
    notifyListeners();
  }

  @override
  void dispose() {
    _mockTimer?.cancel();
    super.dispose();
  }
}
